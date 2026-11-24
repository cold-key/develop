"""端到端离线服务测试：sentinel / scan / qdii-check / record-audit / portfolio / review 与故障隔离。"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import pytest

from wealth_radar.app.audit_store import (
    compute_review_report,
    load_audit_records,
    load_state,
)
from wealth_radar.app.notifier import format_sentinel_webhook
from wealth_radar.app.service import DryRunDataProvider, RadarService
from wealth_radar.config.loader import (
    AppConfig,
    IndexMonitorConfig,
    IndexTargetConfig,
    IndexTierConfig,
    load_config,
    load_portfolio,
)
from wealth_radar.domain.errors import AuditGateError, ConfigValidationError
from wealth_radar.domain.models import (
    AuditVerdict,
    CBHolding,
    CBIpoItem,
    CBMarketRow,
    IndexHolding,
    IndexQuoteSeries,
    MarketTimezone,
    NoticeItem,
    PortfolioSnapshot,
    PriceBar,
    QDIIHoldingItem,
    QDIIPurchaseInfo,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "radar.yaml"


def _make_temp_app_config(tmp_path: Path) -> AppConfig:
    return load_config(config_path=CONFIG_PATH, env_path=None, data_dir=tmp_path / "data")


def test_real_v2_radar_yaml_loads_and_invalid_budget_rejected() -> None:
    app_cfg = load_config(config_path=CONFIG_PATH, env_path=None)
    assert app_cfg.radar.index_monitor.total_budget_cny == 5000.0
    assert len(app_cfg.radar.qdii_router.proxy_pool) >= 5
    assert app_cfg.radar.qdii_router.max_etf_premium_pct == 2.0

    with pytest.raises(ValueError, match="超过单标的预算上限"):
        IndexTargetConfig(
            symbol="QQQ",
            source="akshare_us",
            correlation_group="us_tech",
            name="QQQ",
            budget_cny=1000.0,
            tiers=[
                IndexTierConfig(drawdown_pct=-5.0, amount_cny=600.0),
                IndexTierConfig(drawdown_pct=-10.0, amount_cny=600.0),
            ],
        )

    with pytest.raises(ValueError, match="超过指数舱总预算"):
        IndexMonitorConfig(
            total_budget_cny=3000.0,
            correlation_groups={"us_tech": 2500.0, "defensive_hedge": 1000.0},
            targets=[],
        )


def test_end_to_end_scan_record_audit_portfolio_and_review(tmp_path: Path) -> None:
    app_cfg = _make_temp_app_config(tmp_path)
    today = date(2026, 11, 24)
    provider = DryRunDataProvider(trade_date=today)
    service = RadarService(
        app_cfg=app_cfg,
        market_provider=provider,
        news_provider=provider,
        cb_provider=provider,
        qdii_provider=provider,
    )

    # 1. dry-run scan 不写任何磁盘文件
    dry_packet = service.scan(trade_date=today, dry_run=True)
    assert not app_cfg.last_scan_path.exists()
    assert not app_cfg.state_path.exists()
    assert dry_packet.qdii_route_plan is not None
    assert dry_packet.qdii_route_plan.total_allocated_cny == 1200.0
    assert len(dry_packet.cb_bundles) == 2

    # 2. 正式 scan 落盘 last_scan.json（不提前修改 state.json）
    live_packet = service.scan(trade_date=today, dry_run=False)
    assert app_cfg.last_scan_path.exists()
    assert not app_cfg.state_path.exists()

    # 3. Sentinel Webhook 摘要格式包含 QDII 路由与打新置顶
    summary = format_sentinel_webhook(live_packet)
    assert "演练新债(123999)" in summary
    assert "QDII平替路由" in summary

    # 4. Agent 提交结构化 AuditVerdict 经过 record-audit 硬门禁归档 + --commit-tier 锁定档位
    qqq_verdict = AuditVerdict(
        target_id="QQQ",
        target_name="纳指100",
        asset_type="INDEX_BATCH",
        audit_mode="INDEX_BRIEFING",
        hard_veto=False,
        drawdown_attribution="利率预期重定价引发估值消化",
        execution_plan="申购 021277(广发全球精选C) 1200元",
        credit_or_structural_risk="MEDIUM",
        thesis_status="INTACT",
        bear_case_arguments=["若利率继续上行存在二次回调压力"],
        final_action="APPROVE_BUY",
        confidence_score=78,
    )
    rec_qqq = service.record_audit(qqq_verdict, auditor="antigravity", commit_tier=True)
    assert rec_qqq.gate_overrides == []
    assert -10.0 in load_state(app_cfg.state_path).index_tiers["QQQ"].triggered_tiers

    cb_verdict = AuditVerdict(
        target_id="123001",
        target_name="陷阱转债",
        asset_type="CB_CONVEX",
        audit_mode="CRO_VETO",
        hard_veto=True,
        veto_reason="6个月内承诺不下修",
        lockup_expiry_date="2027-05-14",
        credit_or_structural_risk="HIGH",
        thesis_status="BROKEN",
        bear_case_arguments=["短期封杀下修博弈空间"],
        final_action="REJECT",
        confidence_score=95,
    )
    service.record_audit(cb_verdict, auditor="codex", commit_tier=False)

    # 5. 多周期复盘读取归档并计算涨跌幅
    records = load_audit_records(app_cfg.audits_dir, days=30, as_of_date=today)
    assert len(records) == 2
    review = compute_review_report(records, latest_prices={"QQQ": rec_qqq.price_at_audit * 1.1, "123001": 98.4})
    assert review["INDEX_BATCH"].buckets["APPROVE_BUY"].avg_return_pct == 10.0
    assert review["CB_CONVEX"].buckets["REJECT"].avg_return_pct == -4.0

    # 6. 安全持仓记账（新增、合并加仓、移除）
    service.add_index_holding(
        IndexHolding(
            symbol="QQQ",
            name="广发全球精选C",
            fund_class="C",
            correlation_group="us_tech",
            invested_cny=1200.0,
            avg_entry_price=462.5,
            first_buy_date=today,
            qdii_fund_code="021277",
            qdii_holdings_code="270023",
        ),
        as_of_date=today,
    )
    service.add_cb_holding(
        CBHolding(
            bond_code="123002",
            bond_name="稳健转债",
            stock_code="300002",
            quantity=20,
            avg_cost_price=104.2,
            buy_date=today,
        ),
        as_of_date=today,
    )
    loaded_pf = load_portfolio(app_cfg.portfolio_path)
    assert len(loaded_pf.index_holdings) == 1
    assert loaded_pf.index_holdings[0].qdii_fund_code == "021277"
    assert len(loaded_pf.cb_holdings) == 1

    _, removed = service.remove_holding("CB_CONVEX", "123002", as_of_date=today)
    assert removed is True
    assert load_portfolio(app_cfg.portfolio_path).cb_holdings == []


def test_record_audit_rejects_unknown_target_without_bundle(tmp_path: Path) -> None:
    app_cfg = _make_temp_app_config(tmp_path)
    provider = DryRunDataProvider(trade_date=date(2026, 11, 24))
    service = RadarService(app_cfg, provider, provider, provider, provider)
    verdict = AuditVerdict(
        target_id="UNKNOWN",
        target_name="不存在标的",
        asset_type="CB_CONVEX",
        audit_mode="CRO_VETO",
        hard_veto=True,
        credit_or_structural_risk="HIGH",
        thesis_status="UNKNOWN",
        bear_case_arguments=["无证据"],
        final_action="REJECT",
        confidence_score=50,
    )
    with pytest.raises(AuditGateError):
        service.record_audit(verdict)


def test_fault_isolation_preserves_stage0_redeem_and_cb_ipo_on_market_failure(tmp_path: Path) -> None:
    app_cfg = _make_temp_app_config(tmp_path)
    today = date(2026, 11, 24)

    class _FailingMarket:
        def fetch_index_history(self, symbol: str, source: str, market_timezone: MarketTimezone, lookback_days: int) -> IndexQuoteSeries:
            raise TimeoutError(f"network timeout for {symbol}")

        def fetch_latest_index_price(self, symbol: str, source: str) -> Optional[float]:
            raise TimeoutError("timeout")

        def fetch_index_news(self, symbol: str, source: str, max_items: int) -> List[NoticeItem]:
            return []

    class _EmptyQDII:
        def fetch_purchase_info_map(self, fund_codes: Sequence[str]) -> Dict[str, QDIIPurchaseInfo]:
            return {}

        def fetch_quarterly_holdings(self, holdings_code: str, year: int) -> List[QDIIHoldingItem]:
            return []

        def fetch_fund_nav_series(self, fund_code: str, lookback_days: int) -> List[PriceBar]:
            return []

        def fetch_etf_latest_nav_map(self, etf_codes: Sequence[str]) -> Dict[str, float]:
            return {}

    class _HealthyCB:
        def fetch_cb_ipos(self, trade_date: date) -> List[CBIpoItem]:
            return [CBIpoItem(bond_code="123777", bond_name="保底新债", subscribe_date=trade_date)]

        def fetch_cb_market_rows(self) -> List[CBMarketRow]:
            return [
                CBMarketRow(
                    bond_code="123555",
                    bond_name="持仓强赎债",
                    stock_code="300555",
                    stock_name="强赎股份",
                    price=132.0,
                    premium_rate_pct=12.0,
                    ytm_pct=-6.0,
                    remaining_years=1.5,
                    stock_price=15.0,
                    credit_rating="AA",
                    redeem_announced=True,
                )
            ]

        def fetch_stock_notices(self, stock_code: str, lookback_days: int, fetch_detail_keywords: Sequence[str], max_detail_chars: int, as_of_date: date) -> List[NoticeItem]:
            return []

        def fetch_latest_cb_price(self, bond_code: str) -> Optional[float]:
            return 132.0

    portfolio = PortfolioSnapshot(
        updated_at=today,
        cb_holdings=[
            CBHolding(
                bond_code="123555",
                bond_name="持仓强赎债",
                stock_code="300555",
                quantity=10,
                avg_cost_price=105.0,
                buy_date=today - timedelta(days=30),
            )
        ],
    )
    failing = _FailingMarket()
    service = RadarService(app_cfg, failing, failing, _HealthyCB(), _EmptyQDII())
    packet = service.scan(trade_date=today, dry_run=True, portfolio_override=portfolio)

    assert any(a.alert_type == "REDEEM_URGENT" and a.severity == "CRITICAL" for a in packet.position_alerts)
    assert [i.bond_code for i in packet.cb_ipos] == ["123777"]
    assert "index_quote_QQQ" in packet.section_errors


def test_load_config_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigValidationError):
        load_config(config_path=tmp_path / "nonexistent.yaml", env_path=None)
