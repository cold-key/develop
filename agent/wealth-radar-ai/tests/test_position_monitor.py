"""Stage 0 持仓存续期守卫与卖出预警单元测试（100% 离线）。"""

from __future__ import annotations

from datetime import date

from wealth_radar.config.loader import PositionMonitorConfig
from wealth_radar.core.position_monitor import evaluate_positions
from wealth_radar.domain.models import (
    CBHolding,
    CBMarketRow,
    IndexHolding,
    NoticeItem,
    PortfolioSnapshot,
)


def test_cb_redeem_announced_and_countdown_trigger_critical() -> None:
    cfg = PositionMonitorConfig()
    as_of = date(2026, 11, 24)
    portfolio = PortfolioSnapshot(
        updated_at=as_of,
        cb_holdings=[
            CBHolding(
                bond_code="123101",
                bond_name="已强赎转债",
                stock_code="300101",
                quantity=10,
                avg_cost_price=105.0,
                buy_date=date(2026, 8, 1),
            ),
            CBHolding(
                bond_code="123102",
                bond_name="临近强赎转债",
                stock_code="300102",
                quantity=10,
                avg_cost_price=104.0,
                buy_date=date(2026, 8, 15),
            ),
        ],
    )
    quotes = {
        "123101": CBMarketRow(
            bond_code="123101",
            bond_name="已强赎转债",
            stock_code="300101",
            price=135.0,
            premium_rate_pct=15.0,
            ytm_pct=-5.0,
            remaining_years=1.5,
            stock_price=14.0,
            credit_rating="AA",
            redeem_announced=True,
        ),
        "123102": CBMarketRow(
            bond_code="123102",
            bond_name="临近强赎转债",
            stock_code="300102",
            price=125.0,
            premium_rate_pct=8.0,
            ytm_pct=-3.0,
            remaining_years=1.5,
            stock_price=13.5,
            credit_rating="AA",
            redeem_announced=False,
            redeem_days_remaining=3,
        ),
    }

    alerts = evaluate_positions(portfolio, quotes, {}, {}, cfg, as_of)
    redeem_alerts = [a for a in alerts if a.alert_type == "REDEEM_URGENT"]
    assert len(redeem_alerts) == 2
    assert all(a.severity == "CRITICAL" for a in redeem_alerts)
    assert {a.target_id for a in redeem_alerts} == {"123101", "123102"}


def test_cb_stop_review_price_and_recent_investigation_notice() -> None:
    cfg = PositionMonitorConfig(cb_stop_review_price=92.0)
    as_of = date(2026, 11, 24)
    portfolio = PortfolioSnapshot(
        updated_at=as_of,
        cb_holdings=[
            CBHolding(
                bond_code="123201",
                bond_name="承压转债",
                stock_code="300201",
                quantity=20,
                avg_cost_price=101.0,
                buy_date=date(2026, 9, 1),
            )
        ],
    )
    quotes = {
        "123201": CBMarketRow(
            bond_code="123201",
            bond_name="承压转债",
            stock_code="300201",
            price=90.5,
            premium_rate_pct=42.0,
            ytm_pct=9.5,
            remaining_years=1.2,
            stock_price=2.4,
            credit_rating="A+",
            putback_triggered=True,
        )
    }
    notices = {
        "300201": [
            NoticeItem(
                pub_date=date(2026, 11, 21),
                title="关于收到中国证监会立案告知书的公告",
                snippet="因涉嫌信息披露违法违规被立案调查。",
                detail_fetched=True,
            )
        ]
    }

    alerts = evaluate_positions(portfolio, quotes, notices, {}, cfg, as_of)
    credit_alerts = [a for a in alerts if a.alert_type == "CREDIT_DETERIORATION"]
    putback_alerts = [a for a in alerts if a.alert_type == "PUTBACK_WINDOW"]
    assert len(credit_alerts) == 2
    assert all(a.severity == "CRITICAL" for a in credit_alerts)
    assert len(putback_alerts) == 1
    assert putback_alerts[0].severity == "WARNING"
    # CRITICAL 必须排在 WARNING 之前
    assert alerts[0].severity == "CRITICAL"
    assert alerts[-1].severity == "WARNING"


def test_cb_take_profit_index_take_profit_and_c_class_fee_drag() -> None:
    cfg = PositionMonitorConfig(
        cb_take_profit_price=128.0,
        index_take_profit_pct=25.0,
        index_c_class_max_days=330,
    )
    as_of = date(2026, 11, 24)
    portfolio = PortfolioSnapshot(
        updated_at=as_of,
        index_holdings=[
            IndexHolding(
                symbol="QQQ",
                name="纳指100场外C类",
                fund_class="C",
                correlation_group="us_tech",
                invested_cny=1500.0,
                avg_entry_price=400.0,
                first_buy_date=date(2025, 12, 1),  # 持有 358 天 >= 330 天
            )
        ],
        cb_holdings=[
            CBHolding(
                bond_code="123301",
                bond_name="下修大涨转债",
                stock_code="300301",
                quantity=20,
                avg_cost_price=103.0,
                buy_date=date(2026, 7, 10),
            )
        ],
    )
    quotes = {
        "123301": CBMarketRow(
            bond_code="123301",
            bond_name="下修大涨转债",
            stock_code="300301",
            price=130.5,
            premium_rate_pct=15.0,
            ytm_pct=-8.0,
            remaining_years=1.6,
            stock_price=18.0,
            credit_rating="AA",
        )
    }

    alerts = evaluate_positions(portfolio, quotes, {}, {"QQQ": 510.0}, cfg, as_of)
    alert_map = {(a.target_id, a.alert_type): a for a in alerts}
    assert ("123301", "TAKE_PROFIT") in alert_map
    assert ("QQQ", "TAKE_PROFIT") in alert_map
    assert ("QQQ", "C_CLASS_FEE_DRAG") in alert_map
    assert alert_map[("QQQ", "C_CLASS_FEE_DRAG")].severity == "INFO"


def test_stage0_held_qdii_style_drift_triggers_critical_alert() -> None:
    from wealth_radar.config.loader import QDIIRouterConfig
    from wealth_radar.domain.models import QDIIHoldingItem

    cfg = PositionMonitorConfig()
    qdii_cfg = QDIIRouterConfig(min_us_developed_top10_pct=65.0, max_cn_hk_top10_pct=20.0)
    as_of = date(2026, 11, 24)
    portfolio = PortfolioSnapshot(
        updated_at=as_of,
        index_holdings=[
            IndexHolding(
                symbol="QQQ",
                name="某风格漂移全球基C",
                fund_class="C",
                correlation_group="us_tech",
                invested_cny=1200.0,
                avg_entry_price=500.0,
                first_buy_date=date(2026, 10, 1),
                qdii_fund_code="017431",
                qdii_holdings_code="017431",
            )
        ],
    )
    drifted_holdings = {
        "017431": [
            QDIIHoldingItem(stock_code="300750", stock_name="宁德时代", weight_pct=9.4, quarter="2026年1季度"),
            QDIIHoldingItem(stock_code="00700", stock_name="腾讯控股", weight_pct=6.1, quarter="2026年1季度"),
            QDIIHoldingItem(stock_code="TSLA", stock_name="特斯拉", weight_pct=5.0, quarter="2026年1季度"),
        ]
    }
    alerts = evaluate_positions(
        portfolio,
        {},
        {},
        {"QQQ": 510.0},
        cfg,
        as_of,
        qdii_holdings_by_code=drifted_holdings,
        qdii_cfg=qdii_cfg,
    )
    drift_alerts = [a for a in alerts if a.alert_type == "STYLE_DRIFT"]
    assert len(drift_alerts) == 1
    assert drift_alerts[0].severity == "CRITICAL"
    assert "风格漂移" in drift_alerts[0].message
