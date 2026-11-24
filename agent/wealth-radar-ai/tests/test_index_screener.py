"""Stage 1 指数回撤阶梯器单元测试：金字塔档位、去重、冷却期、三层预算与美股 T-1 提示。"""

from __future__ import annotations

from datetime import date, timedelta

from wealth_radar.config.loader import IndexMonitorConfig, IndexTargetConfig, IndexTierConfig
from wealth_radar.core.index_screener import screen_index_targets
from wealth_radar.domain.models import (
    IndexHolding,
    IndexQuoteSeries,
    PortfolioSnapshot,
    PriceBar,
    RadarState,
)


def _make_series(
    symbol: str,
    closes: list[float],
    end_date: date,
    market_timezone: str = "US",
) -> IndexQuoteSeries:
    start = end_date - timedelta(days=len(closes) - 1)
    bars = [
        PriceBar(trade_date=start + timedelta(days=i), close=c)
        for i, c in enumerate(closes)
    ]
    return IndexQuoteSeries(
        symbol=symbol,
        source="yfinance" if market_timezone == "US" else "akshare",
        market_timezone=market_timezone,  # type: ignore[arg-type]
        bars=bars,
        data_as_of=f"{(end_date - timedelta(days=1)).isoformat()} US Close"
        if market_timezone == "US"
        else f"{end_date.isoformat()} 14:30 CST",
    )


def _base_cfg() -> IndexMonitorConfig:
    return IndexMonitorConfig(
        total_budget_cny=5000.0,
        lookback_days=120,
        reset_drawdown_pct=-2.0,
        cooldown_trading_days=5,
        correlation_groups={"us_tech": 3500.0, "defensive_hedge": 1500.0},
        targets=[
            IndexTargetConfig(
                symbol="QQQ",
                source="yfinance",
                market_timezone="US",
                correlation_group="us_tech",
                name="纳指100 (对应场外C类)",
                budget_cny=3500.0,
                tiers=[
                    IndexTierConfig(drawdown_pct=-5.0, amount_cny=800.0),
                    IndexTierConfig(drawdown_pct=-10.0, amount_cny=1200.0),
                    IndexTierConfig(drawdown_pct=-15.0, amount_cny=1500.0),
                ],
            ),
            IndexTargetConfig(
                symbol="518880",
                source="akshare",
                market_timezone="CN",
                correlation_group="defensive_hedge",
                name="黄金ETF (对应场外C类联接)",
                budget_cny=1500.0,
                tiers=[
                    IndexTierConfig(drawdown_pct=-4.0, amount_cny=600.0),
                    IndexTierConfig(drawdown_pct=-8.0, amount_cny=900.0),
                ],
            ),
        ],
    )


def test_tier_progression_dedup_reset_and_cooldown() -> None:
    cfg = _base_cfg()
    portfolio = PortfolioSnapshot(updated_at=date(2026, 11, 2))
    state = RadarState()

    # Day 1: 首次击穿 -5% (从 500 跌到 472, -5.6%) -> 触发 800 元，且包含 US T-1 / QDII 提示
    d1 = date(2026, 11, 2)
    cands, state = screen_index_targets(
        cfg, {"QQQ": _make_series("QQQ", [500.0, 490.0, 472.0], d1)}, portfolio, state, d1
    )
    assert len(cands) == 1
    assert cands[0].triggered_tier_pct == -5.0
    assert cands[0].approved_amount_cny == 800.0
    assert "T-1" in cands[0].data_as_of and "QDII" in cands[0].data_as_of

    # Day 2: 首次击穿 -10% (跌到 445, -11.0%) -> 触发 1200 元
    d2 = date(2026, 11, 3)
    cands, state = screen_index_targets(
        cfg, {"QQQ": _make_series("QQQ", [500.0, 472.0, 445.0], d2)}, portfolio, state, d2
    )
    assert len(cands) == 1
    assert cands[0].triggered_tier_pct == -10.0
    assert cands[0].approved_amount_cny == 1200.0

    # Day 3: 停留在 -11.2% (444) -> 不重复刷屏
    d3 = date(2026, 11, 4)
    cands, state = screen_index_targets(
        cfg, {"QQQ": _make_series("QQQ", [500.0, 445.0, 444.0], d3)}, portfolio, state, d3
    )
    assert cands == []

    # Day 4: 反弹回 -1.5% (492.5) -> 自动重置档位并启动 5 个交易日冷却期 (2026-11-05 -> 2026-11-12)
    d4 = date(2026, 11, 5)
    cands, state = screen_index_targets(
        cfg, {"QQQ": _make_series("QQQ", [500.0, 444.0, 492.5], d4)}, portfolio, state, d4
    )
    assert cands == []
    assert state.index_tiers["QQQ"].triggered_tiers == []
    assert state.index_tiers["QQQ"].cooldown_until == date(2026, 11, 12)

    # Day 5 (冷却期内 2026-11-09): 再次回撤 -6% -> 冷却期拦截，不重复触发
    d5 = date(2026, 11, 9)
    cands, state = screen_index_targets(
        cfg, {"QQQ": _make_series("QQQ", [500.0, 492.5, 470.0], d5)}, portfolio, state, d5
    )
    assert cands == []

    # Day 6 (冷却期结束后 2026-11-13): 回撤 -6% -> 恢复正常触发 -5% 档位
    d6 = date(2026, 11, 13)
    cands, state = screen_index_targets(
        cfg, {"QQQ": _make_series("QQQ", [500.0, 492.5, 470.0], d6)}, portfolio, state, d6
    )
    assert len(cands) == 1
    assert cands[0].triggered_tier_pct == -5.0
    assert cands[0].approved_amount_cny == 800.0


def test_budget_truncation_and_correlation_group_hard_cap() -> None:
    # QQQ 与 SOXX 共享 us_tech=3500 合并预算
    cfg = IndexMonitorConfig(
        total_budget_cny=5000.0,
        lookback_days=120,
        reset_drawdown_pct=-2.0,
        cooldown_trading_days=5,
        correlation_groups={"us_tech": 3500.0, "defensive_hedge": 1500.0},
        targets=[
            IndexTargetConfig(
                symbol="QQQ",
                source="yfinance",
                market_timezone="US",
                correlation_group="us_tech",
                name="纳指100",
                budget_cny=3500.0,
                tiers=[IndexTierConfig(drawdown_pct=-5.0, amount_cny=1000.0)],
            ),
            IndexTargetConfig(
                symbol="SOXX",
                source="yfinance",
                market_timezone="US",
                correlation_group="us_tech",
                name="费城半导体",
                budget_cny=3500.0,
                tiers=[IndexTierConfig(drawdown_pct=-5.0, amount_cny=1000.0)],
            ),
        ],
    )
    trade_d = date(2026, 11, 24)
    # 已有 3,000 元在 us_tech 组内，组剩余仅 500 元
    portfolio = PortfolioSnapshot(
        updated_at=trade_d,
        index_holdings=[
            IndexHolding(
                symbol="QQQ",
                name="纳指100",
                fund_class="C",
                correlation_group="us_tech",
                invested_cny=3000.0,
                avg_entry_price=480.0,
                first_buy_date=date(2026, 9, 1),
            )
        ],
    )
    quotes = {
        "QQQ": _make_series("QQQ", [500.0, 470.0], trade_d),
        "SOXX": _make_series("SOXX", [250.0, 230.0], trade_d),
    }

    cands, _ = screen_index_targets(cfg, quotes, portfolio, RadarState(), trade_d)
    by_sym = {c.symbol: c for c in cands}

    # QQQ 拿走剩余 500 元（被截断）
    assert by_sym["QQQ"].budget_allowed is True
    assert by_sym["QQQ"].approved_amount_cny == 500.0
    assert "TRUNCATED_BY_BUDGET" in by_sym["QQQ"].budget_reason

    # 同组 SOXX 剩余预算为 0，被硬拦截
    assert by_sym["SOXX"].budget_allowed is False
    assert by_sym["SOXX"].approved_amount_cny == 0.0
    assert "BUDGET_EXHAUSTED" in by_sym["SOXX"].budget_reason
