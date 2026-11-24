"""Rich 终端渲染（ScanPacket / QDII 路由 / 持仓 / 复盘）与 Sentinel Webhook 推送（v2.0）。"""

from __future__ import annotations

from typing import List, Optional

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from wealth_radar.app.audit_store import AssetReviewReport
from wealth_radar.domain.models import (
    AssetType,
    AuditRecord,
    FinalAction,
    PortfolioSnapshot,
    QDIIRoutePlan,
    ScanPacket,
)

SEVERITY_STYLE = {
    "CRITICAL": "bold red",
    "WARNING": "bold yellow",
    "INFO": "cyan",
}

ACTION_STYLE = {
    "REJECT": "bold red",
    "WATCHLIST": "bold yellow",
    "APPROVE_BUY": "bold green",
}


def format_sentinel_webhook(packet: ScanPacket) -> str:
    """生成零 LLM 自动哨兵的分级推送摘要（强赎与打新置顶，有信号提醒唤起 Skill 深度研判）。"""
    mode_tag = "DRY-RUN" if packet.dry_run else "SENTINEL"
    lines: List[str] = [
        f"【wealth-radar-ai 自动哨兵 | {packet.trade_date.isoformat()} | {mode_tag}】",
    ]

    if packet.position_alerts:
        lines.append("\n## 🚨 Stage 0 持仓存续期预警（最高优先级）")
        for alert in packet.position_alerts:
            lines.append(
                f"- [{alert.severity}][{alert.alert_type}] {alert.target_name}({alert.target_id}): "
                f"{alert.message} | 建议：{alert.recommended_action}"
            )
    else:
        lines.append("\n## ✅ Stage 0 持仓存续期守卫：暂无异常")

    if packet.cb_ipos:
        lines.append("\n## 🎯 今日可转债打新（顶格申购）")
        for ipo in packet.cb_ipos:
            rating_txt = f" | 评级 {ipo.credit_rating}" if ipo.credit_rating else ""
            lines.append(f"- {ipo.bond_name}({ipo.bond_code}){rating_txt}")
    else:
        lines.append("\n## 🎯 今日可转债打新：无新债申购")
    if packet.ipo_cash_warning:
        lines.append(f"- ⚠️ 缴款提示：{packet.ipo_cash_warning}")

    if packet.index_candidates:
        lines.append("\n## 📈 指数回撤主线命中（建议唤起 Antigravity / Codex Skill 深度研判）")
        for cand in packet.index_candidates:
            tag = "OK" if cand.budget_allowed else "BUDGET_BLOCKED"
            lines.append(f"- [{tag}] {cand.name}({cand.symbol}): {cand.trigger_summary}")
        if packet.qdii_route_plan is not None:
            lines.append(f"- 🔀 QDII平替路由：{packet.qdii_route_plan.summary}")

    if packet.cb_candidates:
        lines.append(f"\n## 🛡️ 合规双低可转债候选（{len(packet.cb_candidates)} 只，待 Skill CRO 排雷）")
        for cb_cand in packet.cb_candidates:
            warn = f" | ⚠️ {cb_cand.commission_warning}" if cb_cand.commission_warning else ""
            lines.append(
                f"- {cb_cand.row.bond_name}({cb_cand.row.bond_code}): {cb_cand.trigger_summary}{warn}"
            )

    if packet.section_errors:
        lines.append("\n## ⚠️ 局部数据源降级告警（已故障隔离）")
        for section, err in packet.section_errors.items():
            lines.append(f"- {section}: {err}")

    if packet.has_actionable_signal:
        lines.append("\n💡 检测到有效投研/风控信号，建议在 Antigravity 或 Codex 中触发 `wealth-radar` Skill 执行深度联网排雷与归档。")

    return "\n".join(lines)


def render_scan_packet(packet: ScanPacket, console: Optional[Console] = None) -> None:
    """在终端以 Rich 表格渲染扫描结果（含 Stage 0、打新、指数回撤、QDII 平替路由与合规转债）。"""
    out = console or Console()
    mode_tag = "DRY-RUN" if packet.dry_run else "LIVE"
    out.print(
        Panel.fit(
            f"[bold cyan]wealth-radar-ai 确定性投研哨兵 & 扫描器 (v2.0)[/bold cyan]  |  日期: {packet.trade_date.isoformat()}  |  模式: [bold]{mode_tag}[/bold]",
            border_style="cyan",
        )
    )

    # Stage 0
    if packet.position_alerts:
        alert_table = Table(title="Stage 0 持仓存续期预警（置顶）", show_lines=True)
        alert_table.add_column("级别", width=10)
        alert_table.add_column("类型", width=22)
        alert_table.add_column("标的", width=18)
        alert_table.add_column("详情与行动建议")
        for alert in packet.position_alerts:
            style = SEVERITY_STYLE.get(alert.severity, "white")
            alert_table.add_row(
                f"[{style}]{alert.severity}[/{style}]",
                alert.alert_type,
                f"{alert.target_name}\n({alert.target_id})",
                f"{alert.message}\n[dim]建议: {alert.recommended_action}[/dim]",
            )
        out.print(alert_table)
    else:
        out.print("[green]Stage 0 持仓存续期守卫：暂无强赎、止盈、风格漂移或信用恶化告警。[/green]")

    # 打新
    if packet.cb_ipos:
        ipo_table = Table(title="今日可转债打新（顶格申购）")
        ipo_table.add_column("代码")
        ipo_table.add_column("名称")
        ipo_table.add_column("评级")
        ipo_table.add_column("规模(亿)")
        for ipo in packet.cb_ipos:
            scale = f"{ipo.issue_scale_billion:.2f}" if ipo.issue_scale_billion is not None else "-"
            ipo_table.add_row(ipo.bond_code, ipo.bond_name, ipo.credit_rating or "-", scale)
        out.print(ipo_table)
    else:
        out.print("[dim]今日可转债打新：无新债可申购。[/dim]")
    if packet.ipo_cash_warning:
        out.print(f"[yellow]⚠️ 打新资金提示: {packet.ipo_cash_warning}[/yellow]")

    # 指数回撤候选
    if packet.index_candidates:
        idx_table = Table(title="Stage 1 指数回撤主线触发", show_lines=True)
        idx_table.add_column("标的")
        idx_table.add_column("当前回撤", justify="right")
        idx_table.add_column("拟投/核准金额", justify="right")
        idx_table.add_column("状态与时区说明")
        for cand in packet.index_candidates:
            status_style = "green" if cand.budget_allowed else "red"
            idx_table.add_row(
                f"{cand.name}\n({cand.symbol})",
                f"{cand.drawdown_pct:.2f}%",
                f"[{status_style}]{cand.approved_amount_cny:.0f} / {cand.requested_amount_cny:.0f} 元[/{status_style}]",
                f"{cand.trigger_summary}\n[dim]{cand.data_as_of}[/dim]",
            )
        out.print(idx_table)
    else:
        out.print("[dim]指数回撤主线：今日无新触发档位。[/dim]")

    # QDII 平替路由表
    if packet.qdii_route_plan is not None:
        render_qdii_route_plan(packet.qdii_route_plan, console=out)

    # 合规双低可转债候选
    if packet.cb_candidates:
        cb_table = Table(title="Stage 1 合规双低可转债候选（待 Agent Skill CRO 排雷）", show_lines=True)
        cb_table.add_column("排名", justify="right")
        cb_table.add_column("转债")
        cb_table.add_column("现价/溢价/双低", justify="right")
        cb_table.add_column("YTM / 剩余 / 评级", justify="right")
        cb_table.add_column("正股 / 提示")
        for cb_cand in packet.cb_candidates:
            r = cb_cand.row
            extra = f"\n[yellow]⚠️ {cb_cand.commission_warning}[/yellow]" if cb_cand.commission_warning else ""
            cb_table.add_row(
                str(cb_cand.rank),
                f"{r.bond_name}\n({r.bond_code})",
                f"{r.price:.2f} / {r.premium_rate_pct:.1f}% / [bold]{cb_cand.double_low:.2f}[/bold]",
                f"{r.ytm_pct:+.2f}% / {r.remaining_years:.2f}y / {r.credit_rating}",
                f"{r.stock_name}({r.stock_code}) {r.stock_price:.2f}元{extra}",
            )
        out.print(cb_table)
    else:
        out.print("[dim]可转债初筛：今日无满足价格+信用双底线的候选转债。[/dim]")

    if packet.section_errors:
        err_lines = "\n".join(f"- {k}: {v}" for k, v in packet.section_errors.items())
        out.print(Panel(err_lines, title="局部数据源降级告警（已隔离）", border_style="yellow"))


def render_qdii_route_plan(plan: QDIIRoutePlan, console: Optional[Console] = None) -> None:
    """渲染 QDII 平替白名单体检表、拆单路线与场内 ETF 溢价守卫表。"""
    out = console or Console()
    out.print(Panel(plan.summary, title=f"QDII 平替智能路由 ({plan.benchmark_symbol})", border_style="magenta"))

    table = Table(title="QDII 平替池体检（防老鼠仓 / 防风格漂移 / 实时限额）", show_lines=True)
    table.add_column("基金代码/名称")
    table.add_column("申购状态/日限额")
    table.add_column("美股纯度 / A港占比", justify="right")
    table.add_column("120日相关性", justify="right")
    table.add_column("纯度分", justify="right")
    table.add_column("门禁结果")

    for ev in plan.proxy_evaluations:
        limit_str = "不限额" if ev.daily_limit_cny is None else f"{ev.daily_limit_cny:,.0f} 元"
        us_str = f"{ev.us_developed_top10_pct:.1f}%" if ev.us_developed_top10_pct is not None else ("被动" if ev.is_passive else "-")
        cn_str = f"{ev.cn_hk_top10_pct:.1f}%" if ev.cn_hk_top10_pct is not None else "-"
        corr_str = f"{ev.corr_with_benchmark:.2f}" if ev.corr_with_benchmark is not None else "-"
        result_str = (
            "[bold green]PASS[/bold green]"
            if ev.passed
            else "[bold red]BLOCK[/bold red]\n" + "；".join(ev.reject_reasons)
        )
        table.add_row(
            f"{ev.name}\n({ev.fund_code} | {ev.company})",
            f"{ev.purchase_status}\n{limit_str}",
            f"{us_str} / {cn_str}",
            corr_str,
            f"{ev.purity_score:.1f}",
            result_str,
        )
    out.print(table)

    if plan.etf_premiums:
        etf_table = Table(title="场内纳指 ETF 实时溢价守卫")
        etf_table.add_column("代码")
        etf_table.add_column("名称")
        etf_table.add_column("现价", justify="right")
        etf_table.add_column("最新净值", justify="right")
        etf_table.add_column("实时溢价率", justify="right")
        etf_table.add_column("可执行")
        for etf in plan.etf_premiums:
            prem_style = "green" if etf.executable else "bold red"
            status_txt = "[green]可考虑[/green]" if etf.executable else "[bold red]严禁追高[/bold red]"
            etf_table.add_row(
                etf.code,
                etf.name,
                f"{etf.spot_price:.4f}",
                f"{etf.latest_nav:.4f}",
                f"[{prem_style}]{etf.premium_pct:+.2f}%[/{prem_style}]",
                status_txt,
            )
        out.print(etf_table)


def render_audit_record(record: AuditRecord, console: Optional[Console] = None) -> None:
    """渲染经代码层硬门禁校验后的归档审计记录。"""
    out = console or Console()
    v = record.verdict
    style = ACTION_STYLE.get(v.final_action, "white")
    body = [
        f"标的：{v.target_name} ({v.target_id}) | 模式：{v.audit_mode} | 审计价：{record.price_at_audit}",
        f"最终结论：[{style}]{v.final_action}[/{style}] (hard_veto={v.hard_veto}, confidence={v.confidence_score})",
    ]
    if v.veto_reason:
        body.append(f"[red]否决事实：{v.veto_reason}[/red]")
    if v.execution_plan:
        body.append(f"执行方案：{v.execution_plan}")
    if v.drawdown_attribution:
        body.append(f"下跌归因：{v.drawdown_attribution}")
    if record.gate_overrides:
        body.append("[bold yellow]代码硬门禁覆写：" + "；".join(record.gate_overrides) + "[/bold yellow]")
    out.print(Panel("\n".join(body), title="审计记录已通过硬门禁并落盘", border_style="green" if not record.gate_overrides else "yellow"))


def render_portfolio(portfolio: PortfolioSnapshot, console: Optional[Console] = None) -> None:
    out = console or Console()
    out.print(Panel.fit(f"[bold cyan]当前持仓快照[/bold cyan]  |  更新日期: {portfolio.updated_at.isoformat()}"))

    if portfolio.index_holdings:
        t1 = Table(title="指数 / QDII 持仓")
        t1.add_column("信号锚")
        t1.add_column("名称 / QDII代码")
        t1.add_column("相关性组")
        t1.add_column("已投(元)", justify="right")
        t1.add_column("参考均价", justify="right")
        t1.add_column("首次买入")
        for h in portfolio.index_holdings:
            qdii_txt = f"\nQDII: {h.qdii_fund_code}" if h.qdii_fund_code else ""
            t1.add_row(
                h.symbol,
                f"{h.name} ({h.fund_class}类){qdii_txt}",
                h.correlation_group,
                f"{h.invested_cny:,.2f}",
                f"{h.avg_entry_price:.4f}",
                h.first_buy_date.isoformat(),
            )
        out.print(t1)
    else:
        out.print("[dim]指数 / QDII 持仓：空仓[/dim]")

    if portfolio.cb_holdings:
        t2 = Table(title="可转债持仓")
        t2.add_column("转债代码/名称")
        t2.add_column("正股代码")
        t2.add_column("张数", justify="right")
        t2.add_column("成本价", justify="right")
        t2.add_column("成本合计(元)", justify="right")
        t2.add_column("买入日期")
        for cb_h in portfolio.cb_holdings:
            t2.add_row(
                f"{cb_h.bond_name} ({cb_h.bond_code})",
                cb_h.stock_code,
                str(cb_h.quantity),
                f"{cb_h.avg_cost_price:.3f}",
                f"{cb_h.quantity * cb_h.avg_cost_price:,.2f}",
                cb_h.buy_date.isoformat(),
            )
        out.print(t2)
    else:
        out.print("[dim]可转债持仓：空仓[/dim]")


def render_review_report(
    reports: dict[AssetType, AssetReviewReport],
    days: int,
    console: Optional[Console] = None,
) -> None:
    """渲染多周期分资产胜率复盘表。"""
    out = console or Console()
    out.print(
        Panel.fit(
            f"[bold cyan]wealth-radar-ai 事后胜率复盘（过去 {days} 天）[/bold cyan]",
            border_style="cyan",
        )
    )
    asset_types: tuple[AssetType, ...] = ("CB_CONVEX", "INDEX_BATCH")
    actions: tuple[FinalAction, ...] = ("REJECT", "WATCHLIST", "APPROVE_BUY")
    for asset_type in asset_types:
        asset_report = reports[asset_type]
        table = Table(title=f"资产类别：{asset_type}（共 {len(asset_report.items)} 条审计记录）")
        table.add_column("AI 结论")
        table.add_column("记录数", justify="right")
        table.add_column("已取价数", justify="right")
        table.add_column("平均涨跌幅", justify="right")
        table.add_column("中位涨跌幅", justify="right")
        table.add_column("胜率(>0)", justify="right")
        table.add_column("区间 [最差, 最佳]", justify="right")

        for action in actions:
            bucket = asset_report.buckets[action]
            avg_s = f"{bucket.avg_return_pct:+.2f}%" if bucket.avg_return_pct is not None else "-"
            med_s = f"{bucket.median_return_pct:+.2f}%" if bucket.median_return_pct is not None else "-"
            win_s = f"{bucket.win_rate_pct:.1f}%" if bucket.win_rate_pct is not None else "-"
            rng_s = (
                f"[{bucket.min_return_pct:+.2f}%, {bucket.max_return_pct:+.2f}%]"
                if bucket.min_return_pct is not None and bucket.max_return_pct is not None
                else "-"
            )
            style = ACTION_STYLE.get(action, "white")
            table.add_row(
                f"[{style}]{action}[/{style}]",
                str(bucket.total_count),
                str(bucket.priced_count),
                avg_s,
                med_s,
                win_s,
                rng_s,
            )
        out.print(table)


def send_webhook(
    webhook_url: str,
    packet: ScanPacket,
    timeout_sec: float = 10.0,
    http_client: Optional[httpx.Client] = None,
) -> bool:
    """将自动哨兵分级摘要推送至飞书 / 企微 / Telegram 或通用 Webhook。"""
    if not webhook_url.strip():
        return False

    summary = format_sentinel_webhook(packet)
    lower_url = webhook_url.lower()
    if "feishu" in lower_url or "larksuite" in lower_url:
        payload: dict[str, object] = {"msg_type": "text", "content": {"text": summary}}
    elif "weixin.qq.com" in lower_url:
        payload = {"msgtype": "markdown", "markdown": {"content": summary}}
    elif "api.telegram.org" in lower_url:
        payload = {"text": summary}
    else:
        payload = {"text": summary, "markdown": summary}

    if http_client is not None:
        resp = http_client.post(webhook_url, json=payload)
        resp.raise_for_status()
        return True

    with httpx.Client(timeout=timeout_sec) as client:
        resp = client.post(webhook_url, json=payload)
        resp.raise_for_status()
    return True
