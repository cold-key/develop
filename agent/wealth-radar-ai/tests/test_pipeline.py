"""端到端离线主管线测试：三阶段流转、原子落盘、Webhook 摘要、故障隔离、配置校验与多周期复盘。"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional, Sequence

import pytest

from wealth_radar.app.audit_store import (
    compute_review_report,
    load_audit_records,
    load_state,
)
from wealth_radar.app.notifier import format_webhook_summary
from wealth_radar.app.pipeline import DryRunAuditLLM, DryRunDataProvider, RadarPipeline
from wealth_radar.config.loader import (
    AppConfig,
    IndexMonitorConfig,
    IndexTargetConfig,
    IndexTierConfig,
    load_config,
)
from wealth_radar.domain.errors import ConfigValidationError
from wealth_radar.domain.models import (
    CBHolding,
    CBIpoItem,
    CBMarketRow,
    IndexQuoteSeries,
    MarketTimezone,
    NoticeItem,
    PortfolioSnapshot,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "radar.yaml"


def _make_temp_app_config(tmp_path: Path) -> AppConfig:
    return load_config(config_path=CONFIG_PATH, env_path=None, data_dir=tmp_path / "data")


def test_real_radar_yaml_loads_and_invalid_budget_rejected() -> None:
    app_cfg = load_config(config_path=CONFIG_PATH, env_path=None)
    assert app_cfg.radar.index_monitor.total_budget_cny == 5000.0
    assert app_cfg.radar.cb_screener.min_price == 96.0

    # 验证单标的档位之和超过预算会被配置校验拦截
    with pytest.raises(ValueError, match="超过单标的预算上限"):
        IndexTargetConfig(
            symbol="QQQ",
            source="yfinance",
            correlation_group="us_tech",
            name="QQQ",
            budget_cny=1000.0,
            tiers=[
                IndexTierConfig(drawdown_pct=-5.0, amount_cny=600.0),
                IndexTierConfig(drawdown_pct=-10.0, amount_cny=600.0),
            ],
        )

    # 验证相关性组之和超过指数总预算会被拦截
    with pytest.raises(ValueError, match="超过指数舱总预算"):
        IndexMonitorConfig(
            total_budget_cny=3000.0,
            correlation_groups={"us_tech": 2500.0, "defensive_hedge": 1000.0},
            targets=[],
        )


def test_end_to_end_pipeline_persistence_webhook_and_review(tmp_path: Path) -> None:
    app_cfg = _make_temp_app_config(tmp_path)
    today = date(2026, 11, 24)

    # 准备包含强赎风险持仓的 portfolio.json
    portfolio = PortfolioSnapshot(
        updated_at=today,
        cb_holdings=[
            CBHolding(
                bond_code="123001",
                bond_name="陷阱转债",
                stock_code="300001",
                quantity=10,
                avg_cost_price=101.0,
                buy_date=date(2026, 9, 1),
            )
        ],
    )
    app_cfg.data_dir.mkdir(parents=True, exist_ok=True)
    app_cfg.portfolio_path.write_text(
        json.dumps(portfolio.model_dump(mode="json"), ensure_ascii=False), encoding="utf-8"
    )

    provider = DryRunDataProvider(trade_date=today)
    llm = DryRunAuditLLM(app_cfg.radar.llm)
    pipeline = RadarPipeline(
        app_cfg=app_cfg,
        market_provider=provider,
        news_provider=provider,
        cb_provider=provider,
        audit_llm=llm,
    )

    # 1. --dry-run 不落盘 state.json 与 audits/
    dry_report = pipeline.run(trade_date=today, dry_run=True)
    assert not app_cfg.state_path.exists()
    assert not app_cfg.audits_dir.exists()
    assert len(dry_report.cb_ipos) == 1
    assert len(dry_report.audit_records) == 3  # QQQ + 123001(REJECT) + 123002(APPROVE)

    # 2. 正式运行落盘 state.json + JSONL 审计归档
    live_report = pipeline.run(trade_date=today, dry_run=False)
    assert app_cfg.state_path.exists()
    saved_state = load_state(app_cfg.state_path)
    assert -10.0 in saved_state.index_tiers["QQQ"].triggered_tiers
    assert len(saved_state.daily_audit_cache) == 3

    loaded_records = load_audit_records(app_cfg.audits_dir, days=30, as_of_date=today)
    assert len(loaded_records) == 3

    # 3. Webhook 摘要格式校验
    summary = format_webhook_summary(live_report)
    assert "Stage 0 持仓存续期预警" in summary
    assert "今日可转债打新" in summary
    assert "演练新债(123999)" in summary
    assert "[REJECT]" in summary
    assert "[APPROVE_BUY]" in summary

    # 4. 多周期分资产复盘统计校验
    review = compute_review_report(
        loaded_records,
        latest_prices={"QQQ": 509.08, "123001": 98.4, "123002": 114.62},
    )
    assert review["INDEX_BATCH"].buckets["APPROVE_BUY"].avg_return_pct == 10.0
    assert review["CB_CONVEX"].buckets["REJECT"].avg_return_pct == -4.0
    assert review["CB_CONVEX"].buckets["APPROVE_BUY"].avg_return_pct == 10.0


def test_fault_isolation_when_yfinance_times_out(tmp_path: Path) -> None:
    app_cfg = _make_temp_app_config(tmp_path)
    today = date(2026, 11, 24)

    class _FailingMarketProvider:
        def fetch_index_history(
            self,
            symbol: str,
            source: str,
            market_timezone: MarketTimezone,
            lookback_days: int,
        ) -> IndexQuoteSeries:
            raise TimeoutError(f"yfinance timeout for {symbol}")

        def fetch_latest_index_price(self, symbol: str, source: str) -> Optional[float]:
            raise TimeoutError("yfinance timeout")

        def fetch_index_news(self, symbol: str, source: str, max_items: int) -> List[NoticeItem]:
            return []

    class _HealthyCBProvider:
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

        def fetch_stock_notices(
            self,
            stock_code: str,
            lookback_days: int,
            fetch_detail_keywords: Sequence[str],
            max_detail_chars: int,
            as_of_date: date,
        ) -> List[NoticeItem]:
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
                buy_date=today - timedelta(days=40),
            )
        ],
    )
    failing_market = _FailingMarketProvider()
    pipeline = RadarPipeline(
        app_cfg=app_cfg,
        market_provider=failing_market,
        news_provider=failing_market,
        cb_provider=_HealthyCBProvider(),
        audit_llm=DryRunAuditLLM(app_cfg.radar.llm),
    )

    report = pipeline.run(trade_date=today, dry_run=True, portfolio_override=portfolio)

    # 尽管 yfinance 超时，Stage 0 持仓强赎告警与当日可转债打新必须正常送达
    assert any(a.alert_type == "REDEEM_URGENT" and a.severity == "CRITICAL" for a in report.position_alerts)
    assert [i.bond_code for i in report.cb_ipos] == ["123777"]
    assert "index_quote_QQQ" in report.section_errors


def test_positions_only_skips_llm_and_stage1(tmp_path: Path) -> None:
    app_cfg = _make_temp_app_config(tmp_path)
    today = date(2026, 11, 24)
    provider = DryRunDataProvider(trade_date=today)

    class _ExplodingLLM(DryRunAuditLLM):
        def _call_provider(self, system_prompt: str, user_prompt: str, bundle):  # type: ignore[override]
            raise AssertionError("--positions-only 模式绝不允许调用 LLM")

    pipeline = RadarPipeline(
        app_cfg=app_cfg,
        market_provider=provider,
        news_provider=provider,
        cb_provider=provider,
        audit_llm=_ExplodingLLM(app_cfg.radar.llm),
    )
    report = pipeline.run(trade_date=today, positions_only=True)
    assert report.positions_only is True
    assert report.audit_records == []
    assert report.cb_candidates == []


def test_load_config_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigValidationError):
        load_config(config_path=tmp_path / "nonexistent.yaml", env_path=None)
