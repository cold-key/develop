"""Typer CLI 入口（v2.0）：sentinel / scan / qdii-check / record-audit / portfolio / review / reset-tier。"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, Literal, Optional

import typer
from rich.console import Console

from wealth_radar.app.audit_store import (
    compute_review_report,
    load_audit_records,
    reset_symbol_tier_state,
)
from wealth_radar.app.notifier import (
    render_audit_record,
    render_portfolio,
    render_qdii_route_plan,
    render_review_report,
    render_scan_packet,
    send_webhook,
)
from wealth_radar.app.service import DryRunDataProvider, RadarService
from wealth_radar.config.loader import AppConfig, load_config, load_portfolio
from wealth_radar.data_feed.cb_feed import LiveCBFeed
from wealth_radar.data_feed.index_feed import LiveIndexFeed
from wealth_radar.data_feed.qdii_feed import LiveQDIIFeed
from wealth_radar.domain.errors import AuditGateError, WealthRadarError
from wealth_radar.domain.models import (
    AssetType,
    AuditVerdict,
    CBHolding,
    EvidenceBundle,
    IndexHolding,
)

app = typer.Typer(
    name="wealth-radar",
    help="wealth-radar-ai (v2.0): 确定性投研基础设施 + 跨平台 Agent Skill CLI（零 LLM API 依赖）",
    no_args_is_help=True,
)
portfolio_app = typer.Typer(help="原子管理本地持仓快照 (data/portfolio.json)", no_args_is_help=True)
app.add_typer(portfolio_app, name="portfolio")

console = Console()


def _build_service(app_cfg: AppConfig, dry_run: bool, today: date) -> RadarService:
    if dry_run:
        dry_provider = DryRunDataProvider(trade_date=today)
        return RadarService(
            app_cfg=app_cfg,
            market_provider=dry_provider,
            news_provider=dry_provider,
            cb_provider=dry_provider,
            qdii_provider=dry_provider,
        )
    index_feed = LiveIndexFeed()
    cb_feed = LiveCBFeed(jisilu_cookie=app_cfg.secrets.jisilu_cookie)
    qdii_feed = LiveQDIIFeed()
    return RadarService(
        app_cfg=app_cfg,
        market_provider=index_feed,
        news_provider=index_feed,
        cb_provider=cb_feed,
        qdii_provider=qdii_feed,
    )


def _print_json(data: object) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


@app.command("sentinel")
def sentinel_command(
    dry_run: bool = typer.Option(False, "--dry-run", help="使用离线夹具演练哨兵，不修改本地文件"),
    push: bool = typer.Option(True, "--push/--no-push", help="若配置 WEBHOOK_URL 且有信号则自动推送"),
    json_output: bool = typer.Option(False, "--json", help="以 JSON 格式输出扫描结果"),
    config: Path = typer.Option(Path("config/radar.yaml"), "--config", "-c", help="配置文件路径"),
    env_file: Path = typer.Option(Path(".env"), "--env-file", help="环境变量文件路径"),
) -> None:
    """无人值守 14:30 自动哨兵（零 LLM 依赖）：强赎/信用/漂移告警 + 打新 + 指数回撤与 QDII 限额。"""
    try:
        app_cfg = load_config(config_path=config, env_path=env_file)
        today = date.today()
        service = _build_service(app_cfg, dry_run=dry_run, today=today)
        packet = service.scan(
            trade_date=today,
            dry_run=dry_run,
            include_news_and_notices=False,
            save_snapshot=False,
        )

        if json_output:
            _print_json(packet.model_dump(mode="json"))
        else:
            render_scan_packet(packet, console=console)

        if push and not dry_run and packet.has_actionable_signal and app_cfg.secrets.webhook_url:
            try:
                send_webhook(app_cfg.secrets.webhook_url, packet)
                if not json_output:
                    console.print("[green]哨兵已将有效信号推送至 Webhook。[/green]")
            except Exception as exc:
                if not json_output:
                    console.print(f"[yellow]Webhook 推送失败: {exc}[/yellow]")
    except WealthRadarError as exc:
        console.print(f"[bold red]错误: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


@app.command("scan")
def scan_command(
    json_output: bool = typer.Option(False, "--json", help="输出完整 ScanPacket JSON（推荐供 Agent Skill 消费）"),
    dry_run: bool = typer.Option(False, "--dry-run", help="使用离线夹具运行，不覆盖 last_scan.json"),
    config: Path = typer.Option(Path("config/radar.yaml"), "--config", "-c", help="配置文件路径"),
    env_file: Path = typer.Option(Path(".env"), "--env-file", help="环境变量文件路径"),
) -> None:
    """全市场确定性扫描与证据打包（Stage 0 + 打新 + 指数回撤 + QDII 平替路由 + 合规转债证据包）。"""
    try:
        app_cfg = load_config(config_path=config, env_path=env_file)
        today = date.today()
        service = _build_service(app_cfg, dry_run=dry_run, today=today)
        packet = service.scan(
            trade_date=today,
            dry_run=dry_run,
            include_news_and_notices=True,
            save_snapshot=not dry_run,
        )
        if json_output:
            _print_json(packet.model_dump(mode="json"))
        else:
            render_scan_packet(packet, console=console)
            if not dry_run:
                console.print(f"[dim]确定性证据快照已保存至 {app_cfg.last_scan_path}，可供 record-audit 校验引用。[/dim]")
    except WealthRadarError as exc:
        console.print(f"[bold red]错误: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


@app.command("qdii-check")
def qdii_check_command(
    amount: float = typer.Option(1200.0, "--amount", "-a", min=1.0, help="本次拟投入金额（人民币元）"),
    json_output: bool = typer.Option(False, "--json", help="以 JSON 格式输出 QDII 平替路由结果"),
    dry_run: bool = typer.Option(False, "--dry-run", help="使用离线夹具演练"),
    config: Path = typer.Option(Path("config/radar.yaml"), "--config", "-c", help="配置文件路径"),
    env_file: Path = typer.Option(Path(".env"), "--env-file", help="环境变量文件路径"),
) -> None:
    """独立体检 QDII 平替白名单池（实时限额/美股大盘纯度/相关性）与场内纳指 ETF 实时溢价。"""
    try:
        app_cfg = load_config(config_path=config, env_path=env_file)
        today = date.today()
        service = _build_service(app_cfg, dry_run=dry_run, today=today)
        plan, errs = service.run_qdii_check(requested_amount_cny=amount, trade_date=today)
        if json_output:
            _print_json({"plan": plan.model_dump(mode="json"), "errors": errs})
        else:
            render_qdii_route_plan(plan, console=console)
            if errs:
                console.print(f"[yellow]局部数据提示: {errs}[/yellow]")
    except WealthRadarError as exc:
        console.print(f"[bold red]错误: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


@app.command("record-audit")
def record_audit_command(
    verdict_file: Optional[Path] = typer.Option(None, "--verdict-file", "-f", help="Agent 输出的 AuditVerdict JSON 文件路径"),
    verdict_json: Optional[str] = typer.Option(None, "--verdict-json", help="直接传入 AuditVerdict JSON 字符串"),
    bundle_file: Optional[Path] = typer.Option(None, "--bundle-file", help="可选：显式指定 EvidenceBundle JSON 文件（默认从 data/last_scan.json 匹配）"),
    auditor: str = typer.Option("agent_harness", "--auditor", help="审计执行方标识（如 antigravity / codex）"),
    commit_tier: bool = typer.Option(False, "--commit-tier", help="若为指数主线，同步将本次击穿档位写入 state.json 防重复提醒"),
    json_output: bool = typer.Option(False, "--json", help="以 JSON 格式输出落盘后的 AuditRecord"),
    config: Path = typer.Option(Path("config/radar.yaml"), "--config", "-c", help="配置文件路径"),
    env_file: Path = typer.Option(Path(".env"), "--env-file", help="环境变量文件路径"),
) -> None:
    """执行五重代码层 Fail-Closed 硬门禁校验并将 Agent 审计结论归档至 data/audits/。"""
    try:
        if not verdict_file and not verdict_json:
            raise AuditGateError("必须提供 --verdict-file 或 --verdict-json 其中之一。")

        raw_verdict_text = (
            verdict_file.read_text(encoding="utf-8") if verdict_file else str(verdict_json)
        )
        try:
            verdict = AuditVerdict.model_validate_json(raw_verdict_text)
        except Exception as exc:
            raise AuditGateError(f"AuditVerdict JSON 校验失败:\n{exc}") from exc

        bundle: Optional[EvidenceBundle] = None
        if bundle_file is not None:
            try:
                bundle = EvidenceBundle.model_validate_json(bundle_file.read_text(encoding="utf-8"))
            except Exception as exc:
                raise AuditGateError(f"EvidenceBundle JSON 校验失败:\n{exc}") from exc

        app_cfg = load_config(config_path=config, env_path=env_file)
        service = _build_service(app_cfg, dry_run=True, today=date.today())
        record = service.record_audit(
            verdict=verdict,
            bundle=bundle,
            auditor=auditor,
            commit_tier=commit_tier,
        )
        if json_output:
            _print_json(record.model_dump(mode="json"))
        else:
            render_audit_record(record, console=console)
    except WealthRadarError as exc:
        console.print(f"[bold red]门禁/错误: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


@portfolio_app.command("show")
def portfolio_show_command(
    json_output: bool = typer.Option(False, "--json", help="以 JSON 格式输出持仓"),
    config: Path = typer.Option(Path("config/radar.yaml"), "--config", "-c", help="配置文件路径"),
    env_file: Path = typer.Option(Path(".env"), "--env-file", help="环境变量文件路径"),
) -> None:
    """查看当前持仓快照。"""
    try:
        app_cfg = load_config(config_path=config, env_path=env_file)
        portfolio = load_portfolio(app_cfg.portfolio_path)
        if json_output:
            _print_json(portfolio.model_dump(mode="json"))
        else:
            render_portfolio(portfolio, console=console)
    except WealthRadarError as exc:
        console.print(f"[bold red]错误: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


@portfolio_app.command("add-index")
def portfolio_add_index_command(
    symbol: str = typer.Option(..., "--symbol", help="主线信号锚代码（如 QQQ 或 518880）"),
    name: str = typer.Option(..., "--name", help="基金/持仓名称"),
    group: str = typer.Option(..., "--group", help="相关性组名（须与 radar.yaml 一致，如 us_tech / defensive_hedge）"),
    amount: float = typer.Option(..., "--amount", min=0.01, help="本次投入金额（人民币元）"),
    price: float = typer.Option(..., "--price", min=0.0001, help="参考买入价格或单位净值"),
    fund_class: Literal["A", "C", "ETF"] = typer.Option("C", "--fund-class", help="份额类型：A / C / ETF"),
    qdii_code: Optional[str] = typer.Option(None, "--qdii-code", help="可选：实际申购的 QDII 代码（如 021277）"),
    qdii_holdings_code: Optional[str] = typer.Option(None, "--qdii-holdings-code", help="可选：季报持仓主代码（如 270023，用于漂移监测）"),
    buy_date: Optional[str] = typer.Option(None, "--date", help="买入日期 YYYY-MM-DD（默认今日）"),
    config: Path = typer.Option(Path("config/radar.yaml"), "--config", "-c", help="配置文件路径"),
    env_file: Path = typer.Option(Path(".env"), "--env-file", help="环境变量文件路径"),
) -> None:
    """原子新增或加仓指数 / QDII 持仓。"""
    try:
        app_cfg = load_config(config_path=config, env_path=env_file)
        dt = date.fromisoformat(buy_date) if buy_date else date.today()
        service = _build_service(app_cfg, dry_run=True, today=dt)
        updated = service.add_index_holding(
            IndexHolding(
                symbol=symbol,
                name=name,
                fund_class=fund_class,
                correlation_group=group,
                invested_cny=amount,
                avg_entry_price=price,
                first_buy_date=dt,
                qdii_fund_code=qdii_code,
                qdii_holdings_code=qdii_holdings_code,
            ),
            as_of_date=dt,
        )
        render_portfolio(updated, console=console)
    except (WealthRadarError, ValueError) as exc:
        console.print(f"[bold red]错误: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


@portfolio_app.command("add-cb")
def portfolio_add_cb_command(
    code: str = typer.Option(..., "--code", help="可转债代码（如 118034）"),
    name: str = typer.Option(..., "--name", help="可转债简称"),
    stock_code: str = typer.Option(..., "--stock-code", help="正股代码（如 688223）"),
    qty: int = typer.Option(..., "--qty", min=1, help="张数（10张=1手）"),
    price: float = typer.Option(..., "--price", min=0.001, help="买入成交均价（元/张）"),
    buy_date: Optional[str] = typer.Option(None, "--date", help="买入日期 YYYY-MM-DD（默认今日）"),
    config: Path = typer.Option(Path("config/radar.yaml"), "--config", "-c", help="配置文件路径"),
    env_file: Path = typer.Option(Path(".env"), "--env-file", help="环境变量文件路径"),
) -> None:
    """原子新增或加仓可转债持仓。"""
    try:
        app_cfg = load_config(config_path=config, env_path=env_file)
        dt = date.fromisoformat(buy_date) if buy_date else date.today()
        service = _build_service(app_cfg, dry_run=True, today=dt)
        updated = service.add_cb_holding(
            CBHolding(
                bond_code=code,
                bond_name=name,
                stock_code=stock_code,
                quantity=qty,
                avg_cost_price=price,
                buy_date=dt,
            ),
            as_of_date=dt,
        )
        render_portfolio(updated, console=console)
    except (WealthRadarError, ValueError) as exc:
        console.print(f"[bold red]错误: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


@portfolio_app.command("remove")
def portfolio_remove_command(
    asset_type: AssetType = typer.Option(..., "--asset-type", help="INDEX_BATCH 或 CB_CONVEX"),
    target_id: str = typer.Option(..., "--id", help="标的代码（symbol / qdii_code / bond_code）"),
    config: Path = typer.Option(Path("config/radar.yaml"), "--config", "-c", help="配置文件路径"),
    env_file: Path = typer.Option(Path(".env"), "--env-file", help="环境变量文件路径"),
) -> None:
    """清仓移除指定持仓记录。"""
    try:
        app_cfg = load_config(config_path=config, env_path=env_file)
        service = _build_service(app_cfg, dry_run=True, today=date.today())
        updated, removed = service.remove_holding(asset_type=asset_type, target_id=target_id)
        if removed:
            console.print(f"[green]已移除持仓 {target_id}。[/green]")
            render_portfolio(updated, console=console)
        else:
            console.print(f"[yellow]未在持仓中找到 {target_id}。[/yellow]")
    except WealthRadarError as exc:
        console.print(f"[bold red]错误: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


@app.command("review")
def review_command(
    days: int = typer.Option(30, "--days", "-d", min=1, max=365, help="复盘回溯天数（建议 30 / 90 / 180）"),
    json_output: bool = typer.Option(False, "--json", help="以 JSON 格式输出复盘统计"),
    config: Path = typer.Option(Path("config/radar.yaml"), "--config", "-c", help="配置文件路径"),
    env_file: Path = typer.Option(Path(".env"), "--env-file", help="环境变量文件路径"),
) -> None:
    """读取历史审计账本并对比最新现价，分资产统计 AI 排雷与放行胜率。"""
    try:
        app_cfg = load_config(config_path=config, env_path=env_file)
        records = load_audit_records(app_cfg.audits_dir, days=days)
        if not records:
            console.print(f"[yellow]过去 {days} 天内在 {app_cfg.audits_dir} 未找到任何审计记录。[/yellow]")
            return

        index_feed = LiveIndexFeed()
        cb_feed = LiveCBFeed(jisilu_cookie=app_cfg.secrets.jisilu_cookie)
        source_by_symbol = {t.symbol: t.source for t in app_cfg.radar.index_monitor.targets}

        latest_prices: Dict[str, float] = {}
        seen_targets = {(r.bundle.asset_type, r.bundle.target_id) for r in records}
        for asset_type, target_id in seen_targets:
            price: Optional[float] = None
            if asset_type == "CB_CONVEX":
                price = cb_feed.fetch_latest_cb_price(target_id)
            else:
                src = source_by_symbol.get(target_id, "akshare_us" if target_id.isalpha() else "akshare")
                price = index_feed.fetch_latest_index_price(target_id, src)
            if price is not None:
                latest_prices[target_id] = price

        review_reports = compute_review_report(records, latest_prices)
        if json_output:
            _print_json({k: v.model_dump(mode="json") for k, v in review_reports.items()})
        else:
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


if __name__ == "__main__":
    app()
