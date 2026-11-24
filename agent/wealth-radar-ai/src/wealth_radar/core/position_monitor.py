"""Stage 0: 持仓存续期守卫与卖出预警（纯确定性规则，零网络 IO）。"""

from __future__ import annotations

from datetime import date
from typing import Dict, List

from wealth_radar.config.loader import PositionMonitorConfig
from wealth_radar.domain.models import (
    CBMarketRow,
    NoticeItem,
    PortfolioSnapshot,
    PositionAlert,
)

SEVERE_CREDIT_NOTICE_KEYWORDS = (
    "立案",
    "退市",
    "违约",
    "逾期",
    "评级下调",
    "下调评级",
    "下调主体",
    "ST",
    "面值",
)

SEVERITY_ORDER = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}


def evaluate_positions(
    portfolio: PortfolioSnapshot,
    cb_quotes: Dict[str, CBMarketRow],
    cb_recent_notices: Dict[str, List[NoticeItem]],
    index_latest_prices: Dict[str, float],
    cfg: PositionMonitorConfig,
    as_of_date: date,
) -> List[PositionAlert]:
    """扫描已持仓可转债与指数标的，输出按严重程度排序的存续期告警列表。"""
    alerts: List[PositionAlert] = []

    # 1. 可转债持仓扫描
    for holding in portfolio.cb_holdings:
        row = cb_quotes.get(holding.bond_code)
        if row is not None:
            # 1a. 强赎紧急告警（最高优先级）
            if row.redeem_announced:
                alerts.append(
                    PositionAlert(
                        target_id=holding.bond_code,
                        target_name=holding.bond_name,
                        asset_type="CB_CONVEX",
                        alert_type="REDEEM_URGENT",
                        severity="CRITICAL",
                        message=(
                            f"已发布提前强赎公告（现价 {row.price:.2f} 元，溢价率 {row.premium_rate_pct:.2f}%），"
                            "若逾期未卖出或转股将按面值+利息强制赎回。"
                        ),
                        recommended_action="立即核对公告中的最后交易日与最后转股日，提前完成卖出或转股。",
                    )
                )
            elif (
                row.redeem_days_remaining is not None
                and row.redeem_days_remaining <= cfg.cb_redeem_alert_days_remaining
            ):
                alerts.append(
                    PositionAlert(
                        target_id=holding.bond_code,
                        target_name=holding.bond_name,
                        asset_type="CB_CONVEX",
                        alert_type="REDEEM_URGENT",
                        severity="CRITICAL",
                        message=(
                            f"强赎触发计数仅剩 {row.redeem_days_remaining} 个交易日"
                            f"（现价 {row.price:.2f} 元，溢价率 {row.premium_rate_pct:.2f}%）。"
                        ),
                        recommended_action="密切跟踪公司是否公告不强赎，做好随时止盈或转股预案。",
                    )
                )

            # 1b. 信用警戒线跌破
            if row.price <= cfg.cb_stop_review_price:
                alerts.append(
                    PositionAlert(
                        target_id=holding.bond_code,
                        target_name=holding.bond_name,
                        asset_type="CB_CONVEX",
                        alert_type="CREDIT_DETERIORATION",
                        severity="CRITICAL",
                        message=(
                            f"持仓转债现价 {row.price:.2f} 元跌破信用警戒线 {cfg.cb_stop_review_price:.2f} 元"
                            f"（持仓成本 {holding.avg_cost_price:.2f} 元，正股 {row.stock_price:.2f} 元）。"
                        ),
                        recommended_action="立即人工复核最新财报、现金流与偿债能力，评估是否止损离场。",
                    )
                )

            # 1c. 回售窗口提醒
            if cfg.cb_putback_window_alert and (
                row.putback_triggered or row.putback_register_active
            ):
                status_text = "已进入回售登记期" if row.putback_register_active else "已触发回售条款窗口"
                alerts.append(
                    PositionAlert(
                        target_id=holding.bond_code,
                        target_name=holding.bond_name,
                        asset_type="CB_CONVEX",
                        alert_type="PUTBACK_WINDOW",
                        severity="WARNING",
                        message=f"{status_text}（现价 {row.price:.2f} 元，剩余期限 {row.remaining_years:.2f} 年）。",
                        recommended_action="核对回售价格、下修博弈进度与市价差，决定是否申报回售或继续博弈下修。",
                    )
                )

            # 1d. 目标止盈提醒
            if row.price >= cfg.cb_take_profit_price:
                gain_pct = (row.price - holding.avg_cost_price) / holding.avg_cost_price * 100.0
                alerts.append(
                    PositionAlert(
                        target_id=holding.bond_code,
                        target_name=holding.bond_name,
                        asset_type="CB_CONVEX",
                        alert_type="TAKE_PROFIT",
                        severity="WARNING",
                        message=(
                            f"现价 {row.price:.2f} 元达到目标止盈位 {cfg.cb_take_profit_price:.2f} 元"
                            f"（浮盈 {gain_pct:+.2f}%）。"
                        ),
                        recommended_action="建议分批或全部止盈，兑现低价下修博弈脉冲收益。",
                    )
                )

        # 1e. 持仓正股近 7 日重大信用风险公告扫描
        recent_notices = cb_recent_notices.get(holding.stock_code, [])
        severe_hits = [
            notice
            for notice in recent_notices
            if 0 <= (as_of_date - notice.pub_date).days <= 7
            and any(kw in f"{notice.title} {notice.snippet}" for kw in SEVERE_CREDIT_NOTICE_KEYWORDS)
        ]
        if severe_hits:
            latest_hit = sorted(severe_hits, key=lambda n: n.pub_date, reverse=True)[0]
            alerts.append(
                PositionAlert(
                    target_id=holding.bond_code,
                    target_name=holding.bond_name,
                    asset_type="CB_CONVEX",
                    alert_type="CREDIT_DETERIORATION",
                    severity="CRITICAL",
                    message=(
                        f"正股近 7 日出现高危信用公告：[{latest_hit.pub_date.isoformat()}] {latest_hit.title}"
                    ),
                    recommended_action="立刻查阅公告原文评估违约或退市风险，必要时果断止损。",
                )
            )

    # 2. 指数持仓扫描
    for idx_holding in portfolio.index_holdings:
        latest_price = index_latest_prices.get(idx_holding.symbol)
        if latest_price is not None:
            gain_pct = (
                (latest_price - idx_holding.avg_entry_price) / idx_holding.avg_entry_price * 100.0
            )
            if gain_pct >= cfg.index_take_profit_pct:
                alerts.append(
                    PositionAlert(
                        target_id=idx_holding.symbol,
                        target_name=idx_holding.name,
                        asset_type="INDEX_BATCH",
                        alert_type="TAKE_PROFIT",
                        severity="WARNING",
                        message=(
                            f"持仓参考浮盈 {gain_pct:+.2f}%（参考价 {latest_price:.2f} / 均价 {idx_holding.avg_entry_price:.2f}），"
                            f"已达止盈阈值 +{cfg.index_take_profit_pct:.1f}%。"
                        ),
                        recommended_action="建议部分止盈并将超额收益再平衡至低相关资产或现金安全垫。",
                    )
                )

        if idx_holding.fund_class == "C":
            held_days = (as_of_date - idx_holding.first_buy_date).days
            if held_days >= cfg.index_c_class_max_days:
                alerts.append(
                    PositionAlert(
                        target_id=idx_holding.symbol,
                        target_name=idx_holding.name,
                        asset_type="INDEX_BATCH",
                        alert_type="C_CLASS_FEE_DRAG",
                        severity="INFO",
                        message=(
                            f"场外 C 类基金已持有 {held_days} 天（阈值 {cfg.index_c_class_max_days} 天），"
                            "按日计提的销售服务费累计损耗开始高于 A 类或场内 ETF。"
                        ),
                        recommended_action="若计划继续长期持有，评估逢高止盈或置换为 A 类基金/场内 ETF。",
                    )
                )

    alerts.sort(key=lambda a: (SEVERITY_ORDER[a.severity], a.asset_type, a.target_id, a.alert_type))
    return alerts
