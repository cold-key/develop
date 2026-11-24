"""Typer CLI 入口：run / review / reset-tier / test-llm。"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Dict, Optional

import typer
from rich.console import Console

from wealth_radar.app.audit_store import (
    compute_review_report,
    load_audit_records,
    reset_symbol_tier_state,
)
from wealth_radar.app.notifier import (
    render_review_report,
    render_terminal_report,
    send_webhook,
)
from wealth_radar.app.pipeline import (
    DryRunAuditLLM,
    DryRunDataProvider,
    RadarPipeline,
    build_test_llm_bundles,
)
from wealth_radar.config.loader import load_config
from wealth_radar.data_feed.cb_feed import LiveCBFeed
from wealth_radar.data_feed.index_feed import LiveIndexFeed
from wealth_radar.domain.errors import WealthRadarError
from wealth_radar.llm.base import BaseAuditLLM
from wealth_radar.llm.factory import create_audit_llm

app = typer.Typer(
    name="wealth-radar",
    help="wealth-radar-ai: 三阶段混合投研与风控雷达 CLI",
    no_args_is_help=True,
)
console = Console()


@app.command("run")
def run_command(
    dry_run: bool = typer.Option(False, "--dry-run", help="使用离线夹具跑通整套流程，不改写 state.json"),
    no_llm: bool = typer.Option(False, "--no-llm", help="仅跑 Stage 0 & Stage 1，跳过 LLM 审计"),
    force_audit: bool = typer.Option(False, "--force-audit", help="忽略当日缓存强制重调 LLM"),
    positions_only: bool = typer.Option(False, "--positions-only", help="仅执行 Stage 0 持仓存续期风控"),
    config: Path = typer.Option(Path("config/radar.yaml"), "--config", "-c", help="配置文件路径"),
    env_file: Path = typer.Option(Path(".env"), "--env-file", help="环境变量文件路径"),
) -> None:
    """执行完整投研风控管线（Stage 0 -> 打新 -> Stage 1 -> Stage 2 -> 推送）。"""
    try:
        app_cfg = load_config(config_path=config, env_path=env_file)
        today = date.today()

        audit_llm: Optional[BaseAuditLLM]
        if dry_run:
            dry_provider = DryRunDataProvider(trade_date=today)
            audit_llm = None if (no_llm or positions_only) else DryRunAuditLLM(app_cfg.radar.llm)
            pipeline = RadarPipeline(
                app_cfg=app_cfg,
                market_provider=dry_provider,
                news_provider=dry_provider,
                cb_provider=dry_provider,
                audit_llm=audit_llm,
            )
        else:
            index_feed = LiveIndexFeed()
            cb_feed = LiveCBFeed()
            audit_llm = None if (no_llm or positions_only) else create_audit_llm(app_cfg)
            pipeline = RadarPipeline(
                app_cfg=app_cfg,
                market_provider=index_feed,
                news_provider=index_feed,
                cb_provider=cb_feed,
                audit_llm=audit_llm,
            )

        report = pipeline.run(
            trade_date=today,
            dry_run=dry_run,
            no_llm=no_llm,
            force_audit=force_audit,
            positions_only=positions_only,
        )
        render_terminal_report(report, console=console)

        if not dry_run and app_cfg.secrets.webhook_url:
            try:
                send_webhook(app_cfg.secrets.webhook_url, report)
                console.print("[green]已推送报告摘要至 Webhook。[/green]")
            except Exception as exc:
                console.print(f"[yellow]Webhook 推送失败（不影响主流程落盘）: {exc}[/yellow]")
    except WealthRadarError as exc:
        console.print(f"[bold red]错误: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


@app.command("review")
def review_command(
    days: int = typer.Option(30, "--days", "-d", min=1, max=365, help="复盘回溯天数（建议 30 / 90 / 180）"),
    config: Path = typer.Option(Path("config/radar.yaml"), "--config", "-c", help="配置文件路径"),
    env_file: Path = typer.Option(Path(".env"), "--env-file", help="环境变量文件路径"),
) -> None:
    """读取历史审计记录并对比最新现价，分资产统计 AI 排雷与放行胜率。"""
    try:
        app_cfg = load_config(config_path=config, env_path=env_file)
        records = load_audit_records(app_cfg.audits_dir, days=days)
        if not records:
            console.print(f"[yellow]过去 {days} 天内在 {app_cfg.audits_dir} 未找到任何审计记录。[/yellow]")
            return

        index_feed = LiveIndexFeed()
        cb_feed = LiveCBFeed()
        source_by_symbol = {t.symbol: t.source for t in app_cfg.radar.index_monitor.targets}

        latest_prices: Dict[str, float] = {}
        seen_targets = {(r.bundle.asset_type, r.bundle.target_id) for r in records}
        for asset_type, target_id in seen_targets:
            price: Optional[float] = None
            if asset_type == "CB_CONVEX":
                price = cb_feed.fetch_latest_cb_price(target_id)
            else:
                src = source_by_symbol.get(target_id, "yfinance" if target_id.isalpha() else "akshare")
                price = index_feed.fetch_latest_index_price(target_id, src)
            if price is not None:
                latest_prices[target_id] = price

        review_reports = compute_review_report(records, latest_prices)
        render_review_report(review_reports, days=days, console=console)
    except WealthRadarError as exc:
        console.print(f"[bold red]错误: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


@app.command("reset-tier")
def reset_tier_command(
    symbol: str = typer.Argument(..., help="需要重置回撤档位的主线标的代码，例如 QQQ 或 518880"),
    config: Path = typer.Option(Path("config/radar.yaml"), "--config", "-c", help="配置文件路径"),
    env_file: Path = typer.Option(Path(".env"), "--env-file", help="环境变量文件路径"),
) -> None:
    """手动重置某条主线指数已触发的回撤档位与冷却期状态。"""
    try:
        app_cfg = load_config(config_path=config, env_path=env_file)
        existed = reset_symbol_tier_state(app_cfg.state_path, symbol)
        if existed:
            console.print(f"[green]已重置标的 {symbol} 的已触发回撤档位与冷却期状态。[/green]")
        else:
            console.print(f"[yellow]状态文件中未找到标的 {symbol} 的历史触发记录（无需重置）。[/yellow]")
    except WealthRadarError as exc:
        console.print(f"[bold red]错误: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


@app.command("test-llm")
def test_llm_command(
    config: Path = typer.Option(Path("config/radar.yaml"), "--config", "-c", help="配置文件路径"),
    env_file: Path = typer.Option(Path(".env"), "--env-file", help="环境变量文件路径"),
) -> None:
    """使用双模式离线夹具直连当前配置的 LLM API，验证连通性、结构化输出与双模式红线。"""
    try:
        app_cfg = load_config(config_path=config, env_path=env_file)
        audit_llm = create_audit_llm(app_cfg)
        cb_trap, index_panic = build_test_llm_bundles()

        console.print(
            f"[cyan]正在测试 LLM Provider={app_cfg.radar.llm.provider} Model={app_cfg.radar.llm.model} ...[/cyan]"
        )

        cb_rec, _ = audit_llm.audit(cb_trap, price_at_audit=103.2, cache=None, force_audit=True)
        idx_rec, _ = audit_llm.audit(index_panic, price_at_audit=468.0, cache=None, force_audit=True)

        cb_ok = cb_rec.verdict.hard_veto and cb_rec.verdict.final_action == "REJECT"
        idx_ok = (not idx_rec.verdict.hard_veto) and bool(idx_rec.verdict.drawdown_attribution)

        console.print(
            f"1) [bold]CRO_VETO (不下修陷阱转债)[/bold]: action={cb_rec.verdict.final_action}, "
            f"hard_veto={cb_rec.verdict.hard_veto}, lockup={cb_rec.verdict.lockup_expiry_date} "
            f"-> {'[green]PASS[/green]' if cb_ok else '[red]CHECK[/red]'}"
        )
        console.print(
            f"2) [bold]INDEX_BRIEFING (常规回调恐慌新闻)[/bold]: action={idx_rec.verdict.final_action}, "
            f"hard_veto={idx_rec.verdict.hard_veto}, attribution={idx_rec.verdict.drawdown_attribution} "
            f"-> {'[green]PASS[/green]' if idx_ok else '[red]CHECK[/red]'}"
        )
        if not (cb_ok and idx_ok):
            raise typer.Exit(code=2)
    except WealthRadarError as exc:
        console.print(f"[bold red]错误: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
