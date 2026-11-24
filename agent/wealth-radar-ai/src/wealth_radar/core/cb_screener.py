"""Stage 1: 可转债打新筛选与带信用底线的低价下修筛选器（纯确定性计算）。"""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional, Tuple

from wealth_radar.config.loader import CBScreenerConfig
from wealth_radar.domain.models import (
    CBCandidate,
    CBIpoItem,
    CBMarketRow,
    PortfolioSnapshot,
    credit_rating_meets_min,
)


def compute_cb_invested_cny(portfolio: PortfolioSnapshot) -> float:
    """计算当前可转债舱已投入成本（1 张面值 100 元，按持仓张数 × 成本价核算）。"""
    return round(sum(h.quantity * h.avg_cost_price for h in portfolio.cb_holdings), 2)


def filter_cb_ipos(
    ipos: List[CBIpoItem],
    trade_date: date,
    portfolio: PortfolioSnapshot,
    cfg: CBScreenerConfig,
) -> Tuple[List[CBIpoItem], Optional[str]]:
    """筛选当日可申购新债，并检查可转债舱可用余额是否满足打新缴款预留。"""
    today_ipos = [item for item in ipos if item.subscribe_date == trade_date]
    today_ipos.sort(key=lambda item: item.bond_code)

    cb_invested = compute_cb_invested_cny(portfolio)
    cb_available = round(max(0.0, cfg.total_budget_cny - cb_invested), 2)

    cash_warning: Optional[str] = None
    if cb_available < cfg.reserved_ipo_cash_cny:
        cash_warning = (
            f"可转债舱剩余可用资金 {cb_available:.0f} 元低于建议打新预留额 "
            f"{cfg.reserved_ipo_cash_cny:.0f} 元，中签缴款日需提前备足资金。"
        )
    return today_ipos, cash_warning


def screen_cb_candidates(
    rows: List[CBMarketRow],
    portfolio: PortfolioSnapshot,
    cfg: CBScreenerConfig,
) -> List[CBCandidate]:
    """按 v1.1 价格+信用双底线过滤全市场转债，按双低升序取 top_k。"""
    cb_invested = compute_cb_invested_cny(portfolio)
    cb_available = round(max(0.0, cfg.total_budget_cny - cb_invested), 2)
    budget_allowed = cb_available > 0.0

    commission_warning: Optional[str] = None
    if 0.0 < cb_available < cfg.min_order_amount_cny:
        commission_warning = (
            f"可转债舱可用余额 {cb_available:.0f} 元低于不免五防磨损下限 {cfg.min_order_amount_cny:.0f} 元，"
            "单笔双边最低 10 元佣金将显著侵蚀收益（建议确认券商转债是否免五或减少轮动）。"
        )

    held_codes = {h.bond_code: h for h in portfolio.cb_holdings}

    eligible: List[Tuple[float, CBMarketRow]] = []
    for row in rows:
        if cfg.exclude_st and (
            row.is_st
            or "ST" in row.stock_name.upper()
            or "ST" in row.bond_name.upper()
        ):
            continue
        if cfg.exclude_redeem_announced and row.redeem_announced:
            continue
        if not (cfg.min_price <= row.price <= cfg.max_price):
            continue
        if row.premium_rate_pct > cfg.max_premium_rate_pct:
            continue
        if row.ytm_pct < cfg.min_ytm_pct:
            continue
        if not (cfg.min_remaining_years <= row.remaining_years <= cfg.max_remaining_years):
            continue
        if row.stock_price < cfg.min_stock_price_cny:
            continue
        if not credit_rating_meets_min(row.credit_rating, cfg.min_credit_rating):
            continue

        double_low = round(row.price + row.premium_rate_pct, 2)
        eligible.append((double_low, row))

    # 确定性升序排序：双低值 -> 转债现价 -> 代码
    eligible.sort(key=lambda pair: (pair[0], pair[1].price, pair[1].bond_code))
    top_items = eligible[: cfg.top_k]

    candidates: List[CBCandidate] = []
    for rank, (double_low, row) in enumerate(top_items, start=1):
        budget_reason = "OK" if budget_allowed else "BUDGET_EXHAUSTED"
        if commission_warning:
            budget_reason = "LOW_ORDER_COMMISSION_WARNING"

        budget_check: Dict[str, float | str | bool] = {
            "allowed": budget_allowed,
            "cb_total_budget_cny": cfg.total_budget_cny,
            "cb_invested_cny": cb_invested,
            "cb_available_cny": cb_available,
            "min_order_amount_cny": cfg.min_order_amount_cny,
            "reserved_ipo_cash_cny": cfg.reserved_ipo_cash_cny,
            "reason": budget_reason,
        }

        holding = held_codes.get(row.bond_code)
        user_holding_context: Dict[str, float | str] = {
            "cb_invested_cny": cb_invested,
            "cb_holding_count": float(len(portfolio.cb_holdings)),
            "already_holds_target": "YES" if holding is not None else "NO",
        }
        if holding is not None:
            user_holding_context["holding_quantity"] = float(holding.quantity)
            user_holding_context["holding_avg_cost"] = holding.avg_cost_price

        trigger_summary = (
            f"合规双低排名第{rank}"
            f"(双低{double_low:.2f} | 现价{row.price:.2f} | 溢价{row.premium_rate_pct:.1f}% | "
            f"YTM{row.ytm_pct:+.2f}% | 评级{row.credit_rating})"
        )

        candidates.append(
            CBCandidate(
                row=row,
                double_low=double_low,
                rank=rank,
                available_budget_cny=cb_available,
                budget_allowed=budget_allowed,
                commission_warning=commission_warning,
                budget_check=budget_check,
                user_holding_context=user_holding_context,
                trigger_summary=trigger_summary,
            )
        )

    return candidates
