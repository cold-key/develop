"""Stage 1: 指数 120 日回撤阶梯触发器（带冷却期、三层预算硬约束与状态去重）。"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List, Tuple

from wealth_radar.config.loader import IndexMonitorConfig
from wealth_radar.domain.models import (
    IndexCandidate,
    IndexQuoteSeries,
    PortfolioSnapshot,
    RadarState,
    SymbolTierState,
)


def add_trading_days(start_date: date, trading_days: int) -> date:
    """按工作日（跳过周六/周日）推进指定交易日数，纯确定性计算。"""
    current = start_date
    remaining = trading_days
    while remaining > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current


def screen_index_targets(
    cfg: IndexMonitorConfig,
    quotes_by_symbol: Dict[str, IndexQuoteSeries],
    portfolio: PortfolioSnapshot,
    state: RadarState,
    trade_date: date,
) -> Tuple[List[IndexCandidate], RadarState]:
    """计算指数回撤档位与三层预算约束，返回候选列表与更新后的新状态（不原地修改入参 state）。"""
    updated_state = state.model_copy(deep=True)
    candidates: List[IndexCandidate] = []

    # 统计当前已投入金额（按单标的、相关性组、总指数舱三层汇总）
    invested_by_symbol: Dict[str, float] = {}
    invested_by_group: Dict[str, float] = {}
    total_invested = 0.0

    for holding in portfolio.index_holdings:
        invested_by_symbol[holding.symbol] = (
            invested_by_symbol.get(holding.symbol, 0.0) + holding.invested_cny
        )
        invested_by_group[holding.correlation_group] = (
            invested_by_group.get(holding.correlation_group, 0.0) + holding.invested_cny
        )
        total_invested += holding.invested_cny

    # 追踪本轮已预留金额，防止同日多标的重复占用同一组或总预算
    planned_by_symbol: Dict[str, float] = {}
    planned_by_group: Dict[str, float] = {}
    planned_total = 0.0

    for target in cfg.targets:
        quote_series = quotes_by_symbol.get(target.symbol)
        if quote_series is None or not quote_series.bars:
            continue

        sorted_bars = sorted(quote_series.bars, key=lambda b: b.trade_date)
        window = sorted_bars[-cfg.lookback_days :]
        peak_120d = max(bar.close for bar in window)
        latest_bar = window[-1]
        latest_close = latest_bar.close
        drawdown_pct = round((latest_close - peak_120d) / peak_120d * 100.0, 2)

        sym_state = updated_state.index_tiers.get(target.symbol, SymbolTierState())

        # 1. 反弹收敛重置档位 + 开启冷却期
        if drawdown_pct >= cfg.reset_drawdown_pct:
            if sym_state.triggered_tiers:
                sym_state.triggered_tiers = []
                sym_state.last_reset_date = trade_date
                sym_state.cooldown_until = (
                    add_trading_days(trade_date, cfg.cooldown_trading_days)
                    if cfg.cooldown_trading_days > 0
                    else None
                )
            updated_state.index_tiers[target.symbol] = sym_state
            continue

        # 2. 冷却期内跳过触发，避免震荡市浅回调反复消耗子弹
        if sym_state.cooldown_until is not None and trade_date <= sym_state.cooldown_until:
            updated_state.index_tiers[target.symbol] = sym_state
            continue

        # 3. 寻找所有已击穿且尚未触发的回撤档位（tiers 已按由浅到深排序）
        breached = [
            tier
            for tier in target.tiers
            if drawdown_pct <= tier.drawdown_pct
            and tier.drawdown_pct not in sym_state.triggered_tiers
        ]
        if not breached:
            updated_state.index_tiers[target.symbol] = sym_state
            continue

        # 选取本次击穿的最深档位作为拟执行档位，并记录所有已越过档位防止重复刷屏
        active_tier = breached[-1]

        # 4. 三层预算硬约束校验
        used_symbol = invested_by_symbol.get(target.symbol, 0.0) + planned_by_symbol.get(
            target.symbol, 0.0
        )
        used_group = invested_by_group.get(target.correlation_group, 0.0) + planned_by_group.get(
            target.correlation_group, 0.0
        )
        used_total = total_invested + planned_total

        target_remaining = round(max(0.0, target.budget_cny - used_symbol), 2)
        group_limit = cfg.correlation_groups[target.correlation_group]
        group_remaining = round(max(0.0, group_limit - used_group), 2)
        total_remaining = round(max(0.0, cfg.total_budget_cny - used_total), 2)

        max_available = min(target_remaining, group_remaining, total_remaining)
        approved_amount = round(min(active_tier.amount_cny, max_available), 2)
        budget_allowed = approved_amount > 0.0

        if not budget_allowed:
            budget_reason = (
                f"BUDGET_EXHAUSTED (单标的余 {target_remaining:.0f} / "
                f"组[{target.correlation_group}]余 {group_remaining:.0f} / "
                f"指数舱总余 {total_remaining:.0f})"
            )
        elif approved_amount < active_tier.amount_cny:
            budget_reason = (
                f"TRUNCATED_BY_BUDGET (原档位 {active_tier.amount_cny:.0f} 元，"
                f"受预算上限截断为 {approved_amount:.0f} 元)"
            )
        else:
            budget_reason = "OK"

        # 标记已触发档位（仅在允许投入时扣减本轮预留预算）
        for tier in breached:
            if tier.drawdown_pct not in sym_state.triggered_tiers:
                sym_state.triggered_tiers.append(tier.drawdown_pct)
        sym_state.triggered_tiers.sort(reverse=True)
        updated_state.index_tiers[target.symbol] = sym_state

        if budget_allowed:
            planned_by_symbol[target.symbol] = (
                planned_by_symbol.get(target.symbol, 0.0) + approved_amount
            )
            planned_by_group[target.correlation_group] = (
                planned_by_group.get(target.correlation_group, 0.0) + approved_amount
            )
            planned_total += approved_amount

        # 5. 美股 T-1 时区与 QDII 限购提示标准化
        data_as_of = quote_series.data_as_of
        if target.market_timezone == "US" and "QDII" not in data_as_of:
            data_as_of = (
                f"{data_as_of} | T-1 美股收盘滞后提示：15:00前申购场外QDII按今晚净值成交，请核对基金限购"
            )

        budget_check: Dict[str, float | str | bool] = {
            "allowed": budget_allowed,
            "requested_amount_cny": active_tier.amount_cny,
            "approved_amount_cny": approved_amount,
            "target_remaining_cny": target_remaining,
            "group_remaining_cny": group_remaining,
            "total_remaining_cny": total_remaining,
            "correlation_group": target.correlation_group,
            "reason": budget_reason,
        }

        user_holding_context: Dict[str, float | str] = {
            "symbol_invested_cny": round(invested_by_symbol.get(target.symbol, 0.0), 2),
            "group_invested_cny": round(invested_by_group.get(target.correlation_group, 0.0), 2),
            "index_total_invested_cny": round(total_invested, 2),
            "triggered_tiers_history": ",".join(f"{t:.1f}%" for t in sym_state.triggered_tiers),
        }

        trigger_summary = (
            f"首次触发 {active_tier.drawdown_pct:.1f}% 回撤档位"
            f"（当前回撤 {drawdown_pct:.2f}%，拟投 {approved_amount:.0f} 元 / 原档位 {active_tier.amount_cny:.0f} 元）"
        )
        if not budget_allowed:
            trigger_summary = f"触发 {active_tier.drawdown_pct:.1f}% 档位但已超预算拦截（{budget_reason}）"

        candidates.append(
            IndexCandidate(
                symbol=target.symbol,
                name=target.name,
                correlation_group=target.correlation_group,
                market_timezone=target.market_timezone,
                data_as_of=data_as_of,
                latest_close=latest_close,
                peak_120d=peak_120d,
                drawdown_pct=drawdown_pct,
                triggered_tier_pct=active_tier.drawdown_pct,
                requested_amount_cny=active_tier.amount_cny,
                approved_amount_cny=approved_amount,
                budget_allowed=budget_allowed,
                budget_reason=budget_reason,
                budget_check=budget_check,
                user_holding_context=user_holding_context,
                trigger_summary=trigger_summary,
            )
        )

    return candidates, updated_state
