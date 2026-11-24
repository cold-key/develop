"""Stage 1 可转债打新与带信用底线的双低筛选器单元测试（100% 离线）。"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from wealth_radar.config.loader import CBScreenerConfig
from wealth_radar.core.cb_screener import filter_cb_ipos, screen_cb_candidates
from wealth_radar.domain.models import CBHolding, CBIpoItem, CBMarketRow, PortfolioSnapshot

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_cb_screener_credit_floor_filters_and_double_low_ranking() -> None:
    raw_rows = json.loads((FIXTURES_DIR / "sample_cb_market.json").read_text(encoding="utf-8"))
    rows = [CBMarketRow.model_validate(r) for r in raw_rows]
    cfg = CBScreenerConfig(
        min_price=96.0,
        max_price=108.0,
        max_premium_rate_pct=45.0,
        min_ytm_pct=0.0,
        min_remaining_years=0.8,
        max_remaining_years=2.5,
        min_stock_price_cny=2.0,
        min_credit_rating="A+",
        exclude_st=True,
        exclude_redeem_announced=True,
        top_k=5,
    )
    portfolio = PortfolioSnapshot(updated_at=date(2026, 11, 24))

    candidates = screen_cb_candidates(rows, portfolio, cfg)
    # 10 条样本中只有 123001 (双低 123.0) 和 123002 (双低 127.5) 全部达标；
    # 80.5 元违约债 / 负YTM / 1.45元面值高危 / A级低评级 / ST / 已强赎 / 超价 / 超期限均被过滤
    assert [c.row.bond_code for c in candidates] == ["123001", "123002"]
    assert candidates[0].double_low == 123.0
    assert candidates[0].rank == 1
    assert candidates[1].double_low == 127.5
    assert candidates[1].rank == 2
    assert candidates[0].commission_warning is None


def test_cb_screener_top_k_and_commission_warning() -> None:
    cfg = CBScreenerConfig(total_budget_cny=3000.0, min_order_amount_cny=2000.0, top_k=1)
    # 已持仓 2,000 元，剩余仅 1,000 元 < min_order_amount_cny (2,000) -> 触发不免五磨损警告
    portfolio = PortfolioSnapshot(
        updated_at=date(2026, 11, 24),
        cb_holdings=[
            CBHolding(
                bond_code="123900",
                bond_name="已持仓债",
                stock_code="300900",
                quantity=20,
                avg_cost_price=100.0,
                buy_date=date(2026, 10, 1),
            )
        ],
    )
    raw_rows = json.loads((FIXTURES_DIR / "sample_cb_market.json").read_text(encoding="utf-8"))
    rows = [CBMarketRow.model_validate(r) for r in raw_rows]

    candidates = screen_cb_candidates(rows, portfolio, cfg)
    assert len(candidates) == 1
    assert candidates[0].row.bond_code == "123001"
    assert candidates[0].available_budget_cny == 1000.0
    assert candidates[0].commission_warning is not None
    assert "不免五" in candidates[0].commission_warning


def test_cb_ipo_filtering_and_reserved_cash_warning() -> None:
    cfg = CBScreenerConfig(total_budget_cny=3000.0, reserved_ipo_cash_cny=1000.0)
    today = date(2026, 11, 24)
    ipos = [
        CBIpoItem(bond_code="123991", bond_name="今日新债", subscribe_date=today, credit_rating="AA"),
        CBIpoItem(
            bond_code="123992",
            bond_name="明日新债",
            subscribe_date=date(2026, 11, 25),
            credit_rating="AA-",
        ),
    ]
    # 已投入 2,500 元，剩余 500 元 < 1,000 元打新预留
    portfolio = PortfolioSnapshot(
        updated_at=today,
        cb_holdings=[
            CBHolding(
                bond_code="123900",
                bond_name="已持仓债",
                stock_code="300900",
                quantity=25,
                avg_cost_price=100.0,
                buy_date=date(2026, 10, 1),
            )
        ],
    )

    today_ipos, warning = filter_cb_ipos(ipos, today, portfolio, cfg)
    assert [i.bond_code for i in today_ipos] == ["123991"]
    assert warning is not None
    assert "打新预留额" in warning
