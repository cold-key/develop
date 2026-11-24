"""Rich 终端报告渲染与 Webhook 分级摘要推送（飞书 / 企微 / Telegram）。"""

from __future__ import annotations

from typing import List, Optional

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from wealth_radar.app.audit_store import AssetReviewReport
from wealth_radar.domain.models import AssetType, AuditRecord, FinalAction, PipelineReport

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


def format_webhook_summary(report: PipelineReport) -> str:
    """生成高信噪比的 Markdown/纯文本分级推送摘要（强赎与打新强制置顶）。"""
    mode_tag = "DRY-RUN" if report.dry_run else ("POSITIONS-ONLY" if report.positions_only else "LIVE")
    lines: List[str] = [
        f"【wealth-radar-ai 投研风控日报 | {report.trade_date.isoformat()} | {mode_tag}】",
    ]

    # 1. Stage 0 置顶持仓风控告警
    if report.position_alerts:
        lines.append("\n## 🚨 Stage 0 持仓存续期预警（最高优先级）")
        for alert in report.position_alerts:
            lines.append(
                f"- [{alert.severity}][{alert.alert_type}] {alert.target_name}({alert.target_id}): "
                f"{alert.message} | 建议：{alert.recommended_action}"
            )
    else:
        lines.append("\n## ✅ Stage 0 持仓存续期预警：暂无异常")

    # 2. 今日可转债打新置顶
    if not report.positions_only:
        if report.cb_ipos:
            lines.append("\n## 🎯 今日可转债打新（顶格申购）")
            for ipo in report.cb_ipos:
                rating_txt = f" | 评级 {ipo.credit_rating}" if ipo.credit_rating else ""
                lines.append(f"- {ipo.bond_name}({ipo.bond_code}){rating_txt}")
        else:
            lines.append("\n## 🎯 今日可转债打新：无新债申购")
        if report.ipo_cash_warning:
            lines.append(f"- ⚠️ 缴款提示：{report.ipo_cash_warning}")

    # 3. Stage 1 & 2 指数主线
    if not report.positions_only:
        index_records = [r for r in report.audit_records if r.bundle.asset_type == "INDEX_BATCH"]
        blocked_index = [c for c in report.index_candidates if not c.budget_allowed]
        lines.append("\n## 📈 指数回撤主线（INDEX_BRIEFING）")
        if not index_records and not blocked_index and not report.index_candidates:
            lines.append("- 今日无新触发回撤档位。")
        for cand in blocked_index:
            lines.append(f"- [BUDGET_BLOCKED] {cand.name}({cand.symbol}): {cand.trigger_summary}")
        if not index_records:
            for cand in [c for c in report.index_candidates if c.budget_allowed]:
                lines.append(
                    f"- [NO-LLM] {cand.name}({cand.symbol}): {cand.trigger_summary} | {cand.data_as_of}"
                )
        for rec in index_records:
            v = rec.verdict
            cache_tag = " [CACHE]" if rec.from_cache else ""
            attr = f" | 归因：{v.drawdown_attribution}" if v.drawdown_attribution else ""
            lines.append(
                f"- [{v.final_action}]{cache_tag} {v.target_name}({v.target_id}): "
                f"{rec.bundle.trigger_summary}{attr} | 风险：{v.bear_case_arguments[0]}"
            )

    # 4. Stage 1 & 2 可转债低价下修
    if not report.positions_only:
        cb_records = [r for r in report.audit_records if r.bundle.asset_type == "CB_CONVEX"]
        lines.append("\n## 🛡️ 可转债低价下修审计（CRO_VETO）")
        if not report.cb_candidates:
            lines.append("- 今日无满足信用+价格双底线的候选转债。")
        elif not cb_records:
            for cb_cand in report.cb_candidates:
                warn = f" | ⚠️ {cb_cand.commission_warning}" if cb_cand.commission_warning else ""
                lines.append(
                    f"- [NO-LLM] {cb_cand.row.bond_name}({cb_cand.row.bond_code}): {cb_cand.trigger_summary}{warn}"
                )
        for rec in cb_records:
            v = rec.verdict
            cache_tag = " [CACHE]" if rec.from_cache else ""
            veto_txt = f" | 否决：{v.veto_reason}" if v.hard_veto and v.veto_reason else ""
            lockup_txt = f" | 锁定期：{v.lockup_expiry_date}" if v.lockup_expiry_date else ""
            lines.append(
                f"- [{v.final_action}]{cache_tag} {v.target_name}({v.target_id}) "
                f"(置信度 {v.confidence_score}): {rec.bundle.trigger_summary}{veto_txt}{lockup_txt}"
            )

    # 5. 局部数据源异常隔离提示
    if report.section_errors:
        lines.append("\n## ⚠️ 局部数据源降级告警（已故障隔离）")
        for section, err in report.section_errors.items():
            lines.append(f"- {section}: {err}")

    return "\n".join(lines)


def render_terminal_report(report: PipelineReport, console: Optional[Console] = None) -> None:
    """使用 Rich 在终端渲染结构化彩色报告。"""
    out = console or Console()
    mode_tag = "DRY-RUN" if report.dry_run else ("POSITIONS-ONLY" if report.positions_only else "LIVE")
    out.print(
        Panel.fit(
            f"[bold cyan]wealth-radar-ai 投研风控雷达[/bold cyan]  |  日期: {report.trade_date.isoformat()}  |  模式: [bold]{mode_tag}[/bold]",
            border_style="cyan",
        )
    )

    # Stage 0
    if report.position_alerts:
        alert_table = Table(title="Stage 0 持仓存续期预警（置顶）", show_lines=True)
        alert_table.add_column("级别", width=10)
        alert_table.add_column("类型", width=22)
        alert_table.add_column("标的", width=18)
        alert_table.add_column("详情与行动建议")
        for alert in report.position_alerts:
            style = SEVERITY_STYLE.get(alert.severity, "white")
            alert_table.add_row(
                f"[{style}]{alert.severity}[/{style}]",
                alert.alert_type,
                f"{alert.target_name}\n({alert.target_id})",
                f"{alert.message}\n[dim]建议: {alert.recommended_action}[/dim]",
            )
        out.print(alert_table)
    else:
        out.print("[green]Stage 0 持仓存续期守卫：暂无强赎、止盈或信用恶化告警。[/green]")

    if not report.positions_only:
        # 打新
        if report.cb_ipos:
            ipo_table = Table(title="今日可转债打新（顶格申购）")
            ipo_table.add_column("代码")
            ipo_table.add_column("名称")
            ipo_table.add_column("评级")
            ipo_table.add_column("规模(亿)")
            for ipo in report.cb_ipos:
                scale = f"{ipo.issue_scale_billion:.2f}" if ipo.issue_scale_billion is not None else "-"
                ipo_table.add_row(ipo.bond_code, ipo.bond_name, ipo.credit_rating or "-", scale)
            out.print(ipo_table)
        else:
            out.print("[dim]今日可转债打新：无新债可申购。[/dim]")
        if report.ipo_cash_warning:
            out.print(f"[yellow]⚠️ 打新资金提示: {report.ipo_cash_warning}[/yellow]")

        # 审计结果表
        if report.audit_records:
            audit_table = Table(title="Stage 2 双模式 LLM 审计结论", show_lines=True)
            audit_table.add_column("模式", width=15)
            audit_table.add_column("标的", width=18)
            audit_table.add_column("结论", width=14)
            audit_table.add_column("关键证据 / 归因 / 空头论据")
            for rec in report.audit_records:
                _add_audit_row(audit_table, rec)
            out.print(audit_table)
        else:
            if report.index_candidates or report.cb_candidates:
                out.print("[yellow]Stage 1 命中候选但未执行 LLM 审计（--no-llm 或预算拦截）。[/yellow]")
                for cand in report.index_candidates:
                    out.print(f"  - [INDEX] {cand.name}({cand.symbol}): {cand.trigger_summary}")
                for cb_cand in report.cb_candidates:
                    out.print(f"  - [CB] {cb_cand.row.bond_name}({cb_cand.row.bond_code}): {cb_cand.trigger_summary}")
            else:
                out.print("[dim]今日 Stage 1 未命中新的开仓候选。[/dim]")

    if report.section_errors:
        err_lines = "\n".join(f"- {k}: {v}" for k, v in report.section_errors.items())
        out.print(Panel(err_lines, title="局部数据源降级告警（已隔离）", border_style="yellow"))


def _add_audit_row(table: Table, rec: AuditRecord) -> None:
    v = rec.verdict
    style = ACTION_STYLE.get(v.final_action, "white")
    action_cell = f"[{style}]{v.final_action}[/{style}]\nveto={v.hard_veto}\nscore={v.confidence_score}"
    if rec.from_cache:
        action_cell += "\n[dim](cache)[/dim]"

    details: List[str] = [f"[bold]{rec.bundle.trigger_summary}[/bold]"]
    if v.veto_reason:
        details.append(f"[red]否决事实: {v.veto_reason}[/red]")
    if v.lockup_expiry_date:
        details.append(f"不下修锁定期: {v.lockup_expiry_date}")
    if v.drawdown_attribution:
        details.append(f"下跌归因: {v.drawdown_attribution}")
    details.append("空头/风险: " + "；".join(v.bear_case_arguments))
    if v.evidence_citations:
        details.append("[dim]引用: " + "；".join(v.evidence_citations[:3]) + "[/dim]")
    if v.missing_info_warnings:
        details.append("[yellow]缺失警告: " + "；".join(v.missing_info_warnings) + "[/yellow]")

    table.add_row(
        f"{v.audit_mode}\n[dim]{rec.prompt_version}[/dim]",
        f"{v.target_name}\n({v.target_id})",
        action_cell,
        "\n".join(details),
    )


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
    report: PipelineReport,
    timeout_sec: float = 10.0,
    http_client: Optional[httpx.Client] = None,
) -> bool:
    """将分级摘要推送至飞书 / 企微 / Telegram 或通用 Webhook。"""
    if not webhook_url.strip():
        return False

    summary = format_webhook_summary(report)
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
