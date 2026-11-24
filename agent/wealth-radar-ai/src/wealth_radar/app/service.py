"""应用服务层（v2.0）：编排 sentinel / scan / qdii-check / record-audit / portfolio 与离线夹具。"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Sequence, Tuple

from wealth_radar.app.audit_store import (
    append_audit_records,
    load_last_scan,
    load_state,
    save_last_scan_atomic,
    save_portfolio_atomic,
    save_state_atomic,
)
from wealth_radar.config.loader import AppConfig, load_portfolio
from wealth_radar.core.audit_gate import enforce_audit_gate
from wealth_radar.core.cb_screener import filter_cb_ipos, screen_cb_candidates
from wealth_radar.core.evidence_packer import pack_cb_evidence, pack_index_evidence
from wealth_radar.core.index_screener import screen_index_targets
from wealth_radar.core.position_monitor import evaluate_positions
from wealth_radar.core.qdii_router import build_qdii_route_plan
from wealth_radar.data_feed.protocols import (
    CBProvider,
    MarketProvider,
    NewsProvider,
    QDIIProvider,
)
from wealth_radar.domain.errors import AuditGateError
from wealth_radar.domain.models import (
    AssetType,
    AuditRecord,
    AuditVerdict,
    CBHolding,
    CBIpoItem,
    CBMarketRow,
    EvidenceBundle,
    IndexHolding,
    IndexQuoteSeries,
    MarketTimezone,
    NoticeItem,
    PortfolioSnapshot,
    PriceBar,
    QDIIHoldingItem,
    QDIIPurchaseInfo,
    QDIIRoutePlan,
    ScanPacket,
    SymbolTierState,
)


class RadarService:
    """确定性投研基础设施服务（零 LLM 依赖，全协议注入，板块级故障隔离）。"""

    def __init__(
        self,
        app_cfg: AppConfig,
        market_provider: MarketProvider,
        news_provider: NewsProvider,
        cb_provider: CBProvider,
        qdii_provider: QDIIProvider,
    ) -> None:
        self.app_cfg = app_cfg
        self.market_provider = market_provider
        self.news_provider = news_provider
        self.cb_provider = cb_provider
        self.qdii_provider = qdii_provider

    def run_qdii_check(
        self,
        requested_amount_cny: float,
        trade_date: Optional[date] = None,
        benchmark_bars: Optional[Sequence[PriceBar]] = None,
    ) -> Tuple[QDIIRoutePlan, Dict[str, str]]:
        """独立体检 QDII 平替池（申购开关/日限额/美股纯度/相关性）与场内纳指 ETF 溢价。"""
        today = trade_date or date.today()
        qdii_cfg = self.app_cfg.radar.qdii_router
        errors: Dict[str, str] = {}

        # 1. 基准（QQQ）历史走势，用于计算 120 日真实相关性
        bench_bars: Sequence[PriceBar] = benchmark_bars or []
        if not bench_bars:
            bench_target = next(
                (t for t in self.app_cfg.radar.index_monitor.targets if t.symbol == qdii_cfg.benchmark_symbol),
                None,
            )
            src = bench_target.source if bench_target else "akshare_us"
            tz: MarketTimezone = bench_target.market_timezone if bench_target else "US"
            try:
                series = self.market_provider.fetch_index_history(
                    symbol=qdii_cfg.benchmark_symbol,
                    source=src,
                    market_timezone=tz,
                    lookback_days=self.app_cfg.radar.index_monitor.lookback_days,
                )
                bench_bars = series.bars
            except Exception as exc:
                errors["qdii_benchmark"] = f"拉取基准 {qdii_cfg.benchmark_symbol} 走势失败: {exc}"

        # 2. 实时申购状态与单日限额
        fund_codes = [item.fund_code for item in qdii_cfg.proxy_pool]
        purchase_map: Dict[str, QDIIPurchaseInfo] = {}
        try:
            purchase_map = self.qdii_provider.fetch_purchase_info_map(fund_codes)
        except Exception as exc:
            errors["qdii_purchase_limits"] = f"拉取 QDII 申购限额失败: {exc}"

        # 3. 季报前十大持仓（主动 QDII 必须核验防漂移与物理防老鼠仓）+ 120 日净值走势
        holdings_by_code: Dict[str, List[QDIIHoldingItem]] = {}
        nav_by_code: Dict[str, List[PriceBar]] = {}
        for item in qdii_cfg.proxy_pool:
            if not item.is_passive and item.holdings_code not in holdings_by_code:
                try:
                    holdings_by_code[item.holdings_code] = self.qdii_provider.fetch_quarterly_holdings(
                        holdings_code=item.holdings_code,
                        year=today.year,
                    )
                except Exception as exc:
                    errors[f"qdii_holdings_{item.fund_code}"] = str(exc)

            try:
                nav_by_code[item.fund_code] = self.qdii_provider.fetch_fund_nav_series(
                    fund_code=item.fund_code,
                    lookback_days=self.app_cfg.radar.index_monitor.lookback_days,
                )
            except Exception as exc:
                errors[f"qdii_nav_{item.fund_code}"] = str(exc)

        # 4. 场内纳指 ETF 现价 vs 净值 -> 实时溢价守卫
        etf_codes = [e.code for e in qdii_cfg.on_exchange_etfs]
        etf_nav_map: Dict[str, float] = {}
        etf_spot_prices: Dict[str, float] = {}
        if etf_codes:
            try:
                etf_nav_map = self.qdii_provider.fetch_etf_latest_nav_map(etf_codes)
            except Exception as exc:
                errors["etf_nav"] = f"拉取场内 ETF 净值失败: {exc}"

            for code in etf_codes:
                try:
                    spot = self.market_provider.fetch_latest_index_price(code, "akshare")
                    if spot is not None and spot > 0:
                        etf_spot_prices[code] = spot
                except Exception as exc:
                    errors[f"etf_spot_{code}"] = str(exc)

        plan = build_qdii_route_plan(
            cfg=qdii_cfg,
            requested_amount_cny=requested_amount_cny,
            benchmark_bars=bench_bars,
            purchase_info_map=purchase_map,
            holdings_by_code=holdings_by_code,
            nav_series_by_code=nav_by_code,
            etf_spot_prices=etf_spot_prices,
            etf_nav_map=etf_nav_map,
        )
        return plan, errors

    def scan(
        self,
        trade_date: Optional[date] = None,
        *,
        dry_run: bool = False,
        include_news_and_notices: bool = True,
        save_snapshot: bool = True,
        portfolio_override: Optional[PortfolioSnapshot] = None,
    ) -> ScanPacket:
        """执行全市场确定性扫描（Stage 0 + 打新 + 指数回撤 + QDII 平替路由 + 合规转债证据打包）。"""
        today = trade_date or date.today()
        run_ts = datetime.now(timezone.utc)
        radar_cfg = self.app_cfg.radar

        portfolio = (
            portfolio_override
            if portfolio_override is not None
            else load_portfolio(self.app_cfg.portfolio_path, default_date=today)
        )
        state = load_state(self.app_cfg.state_path)

        section_errors: Dict[str, str] = {}
        cb_market_rows: Optional[List[CBMarketRow]] = None
        index_quotes_by_symbol: Dict[str, IndexQuoteSeries] = {}

        # =====================================================================
        # Stage 0: 持仓存续期守卫（强赎、信用、止盈、C 类费率 + 持仓 QDII 风格漂移）
        # =====================================================================
        cb_quotes_map: Dict[str, CBMarketRow] = {}
        cb_holding_notices: Dict[str, List[NoticeItem]] = {}
        index_latest_prices: Dict[str, float] = {}
        held_qdii_holdings: Dict[str, Sequence[QDIIHoldingItem]] = {}

        if portfolio.cb_holdings:
            try:
                cb_market_rows = self.cb_provider.fetch_cb_market_rows()
                cb_quotes_map = {row.bond_code: row for row in cb_market_rows}
            except Exception as exc:
                section_errors["stage0_cb_quotes"] = f"持仓可转债行情抓取失败: {exc}"

            for cb_holding in portfolio.cb_holdings:
                try:
                    cb_holding_notices[cb_holding.stock_code] = self.cb_provider.fetch_stock_notices(
                        stock_code=cb_holding.stock_code,
                        lookback_days=14,
                        fetch_detail_keywords=radar_cfg.cb_screener.fetch_detail_keywords,
                        max_detail_chars=radar_cfg.evidence_budget.max_detail_chars_per_notice,
                        as_of_date=today,
                    )
                except Exception as exc:
                    section_errors[f"stage0_cb_notice_{cb_holding.stock_code}"] = str(exc)

        if portfolio.index_holdings:
            source_by_symbol = {t.symbol: (t.source, t.market_timezone) for t in radar_cfg.index_monitor.targets}
            for idx_holding in portfolio.index_holdings:
                src, tz = source_by_symbol.get(
                    idx_holding.symbol,
                    ("akshare_us" if idx_holding.symbol.isalpha() else "akshare", "CN"),
                )
                try:
                    series = self.market_provider.fetch_index_history(
                        symbol=idx_holding.symbol,
                        source=src,
                        market_timezone=tz,
                        lookback_days=radar_cfg.index_monitor.lookback_days,
                    )
                    index_quotes_by_symbol[idx_holding.symbol] = series
                    if series.bars:
                        index_latest_prices[idx_holding.symbol] = series.bars[-1].close
                except Exception as exc:
                    section_errors[f"stage0_index_{idx_holding.symbol}"] = str(exc)

                lookup_code = idx_holding.qdii_holdings_code or idx_holding.qdii_fund_code
                if lookup_code:
                    try:
                        held_qdii_holdings[lookup_code] = self.qdii_provider.fetch_quarterly_holdings(
                            holdings_code=lookup_code,
                            year=today.year,
                        )
                    except Exception as exc:
                        section_errors[f"stage0_qdii_drift_{lookup_code}"] = str(exc)

        position_alerts = evaluate_positions(
            portfolio=portfolio,
            cb_quotes=cb_quotes_map,
            cb_recent_notices=cb_holding_notices,
            index_latest_prices=index_latest_prices,
            cfg=radar_cfg.position_monitor,
            as_of_date=today,
            qdii_holdings_by_code=held_qdii_holdings,
            qdii_cfg=radar_cfg.qdii_router,
        )

        # =====================================================================
        # 今日可转债打新（独立故障隔离）
        # =====================================================================
        cb_ipos: List[CBIpoItem] = []
        ipo_cash_warning: Optional[str] = None
        try:
            raw_ipos = self.cb_provider.fetch_cb_ipos(today)
            cb_ipos, ipo_cash_warning = filter_cb_ipos(
                ipos=raw_ipos,
                trade_date=today,
                portfolio=portfolio,
                cfg=radar_cfg.cb_screener,
            )
        except Exception as exc:
            section_errors["cb_ipo"] = f"可转债打新列表抓取失败: {exc}"

        # =====================================================================
        # Stage 1: 指数回撤阶梯 + QDII 平替智能路由
        # =====================================================================
        for target in radar_cfg.index_monitor.targets:
            if target.symbol in index_quotes_by_symbol:
                continue
            try:
                index_quotes_by_symbol[target.symbol] = self.market_provider.fetch_index_history(
                    symbol=target.symbol,
                    source=target.source,
                    market_timezone=target.market_timezone,
                    lookback_days=radar_cfg.index_monitor.lookback_days,
                )
            except Exception as exc:
                section_errors[f"index_quote_{target.symbol}"] = f"指数 {target.symbol} 行情失败: {exc}"

        index_candidates, _ = screen_index_targets(
            cfg=radar_cfg.index_monitor,
            quotes_by_symbol=index_quotes_by_symbol,
            portfolio=portfolio,
            state=state,
            trade_date=today,
        )

        qdii_route_plan: Optional[QDIIRoutePlan] = None
        qdii_target_cand = next(
            (c for c in index_candidates if c.qdii_router_enabled and c.budget_allowed),
            None,
        )
        if qdii_target_cand is not None:
            bench_series = index_quotes_by_symbol.get(radar_cfg.qdii_router.benchmark_symbol)
            qdii_route_plan, qdii_errs = self.run_qdii_check(
                requested_amount_cny=qdii_target_cand.approved_amount_cny,
                trade_date=today,
                benchmark_bars=bench_series.bars if bench_series else None,
            )
            section_errors.update(qdii_errs)

        index_bundles: List[EvidenceBundle] = []
        target_source_map = {t.symbol: t.source for t in radar_cfg.index_monitor.targets}
        if include_news_and_notices:
            for cand in index_candidates:
                news_items: List[NoticeItem] = []
                if cand.budget_allowed:
                    try:
                        news_items = self.news_provider.fetch_index_news(
                            symbol=cand.symbol,
                            source=target_source_map.get(cand.symbol, "akshare_us"),
                            max_items=radar_cfg.evidence_budget.max_news_per_target,
                        )
                    except Exception as exc:
                        section_errors[f"index_news_{cand.symbol}"] = f"指数 {cand.symbol} 新闻失败: {exc}"

                bundle = pack_index_evidence(
                    candidate=cand,
                    news_items=news_items,
                    trade_date=today,
                    budget=radar_cfg.evidence_budget,
                    qdii_route_plan=qdii_route_plan if cand.qdii_router_enabled else None,
                )
                index_bundles.append(bundle)

        # =====================================================================
        # Stage 1: 可转债信用底线初筛 + 公告证据打包
        # =====================================================================
        if cb_market_rows is None:
            try:
                cb_market_rows = self.cb_provider.fetch_cb_market_rows()
            except Exception as exc:
                section_errors["cb_market"] = f"可转债全市场行情抓取失败: {exc}"

        cb_candidates = (
            screen_cb_candidates(rows=cb_market_rows, portfolio=portfolio, cfg=radar_cfg.cb_screener)
            if cb_market_rows is not None
            else []
        )

        cb_bundles: List[EvidenceBundle] = []
        if include_news_and_notices:
            for cb_cand in cb_candidates:
                stock_notices: List[NoticeItem] = []
                try:
                    stock_notices = self.cb_provider.fetch_stock_notices(
                        stock_code=cb_cand.row.stock_code,
                        lookback_days=radar_cfg.cb_screener.notice_lookback_days,
                        fetch_detail_keywords=radar_cfg.cb_screener.fetch_detail_keywords,
                        max_detail_chars=radar_cfg.evidence_budget.max_detail_chars_per_notice,
                        as_of_date=today,
                    )
                except Exception as exc:
                    section_errors[f"cb_notice_{cb_cand.row.bond_code}"] = (
                        f"正股 {cb_cand.row.stock_code} 公告抓取失败: {exc}"
                    )

                bundle = pack_cb_evidence(
                    candidate=cb_cand,
                    notices=stock_notices,
                    news_items=[],
                    trade_date=today,
                    notice_keywords=radar_cfg.cb_screener.notice_keywords,
                    fetch_detail_keywords=radar_cfg.cb_screener.fetch_detail_keywords,
                    budget=radar_cfg.evidence_budget,
                )
                cb_bundles.append(bundle)

        packet = ScanPacket(
            trade_date=today,
            run_timestamp=run_ts,
            dry_run=dry_run,
            position_alerts=position_alerts,
            cb_ipos=cb_ipos,
            ipo_cash_warning=ipo_cash_warning,
            index_candidates=index_candidates,
            index_bundles=index_bundles,
            qdii_route_plan=qdii_route_plan,
            cb_candidates=cb_candidates,
            cb_bundles=cb_bundles,
            section_errors=section_errors,
        )

        if save_snapshot and not dry_run and include_news_and_notices:
            save_last_scan_atomic(self.app_cfg.last_scan_path, packet)

        return packet

    def record_audit(
        self,
        verdict: AuditVerdict,
        *,
        bundle: Optional[EvidenceBundle] = None,
        auditor: str = "agent_harness",
        commit_tier: bool = False,
    ) -> AuditRecord:
        """经由 Python 五重硬门禁校验 Agent 审计结论并落盘 JSONL（可选同步锁定已触发指数档位）。"""
        resolved_bundle = bundle
        if resolved_bundle is None:
            last_scan = load_last_scan(self.app_cfg.last_scan_path)
            if last_scan is None:
                raise AuditGateError(
                    f"未找到最近扫描快照 {self.app_cfg.last_scan_path}，请先运行 `wealth-radar scan --json` 或通过 --bundle-file 提供证据包。"
                )
            all_bundles = last_scan.index_bundles + last_scan.cb_bundles
            resolved_bundle = next(
                (b for b in all_bundles if b.target_id == verdict.target_id),
                None,
            )
            if resolved_bundle is None:
                raise AuditGateError(
                    f"在最近扫描快照中未找到 target_id='{verdict.target_id}' 的证据包，拒绝无证据归档。"
                )

        enforced_verdict, overrides = enforce_audit_gate(
            verdict=verdict,
            bundle=resolved_bundle,
            max_etf_premium_pct=self.app_cfg.radar.qdii_router.max_etf_premium_pct,
        )

        price_at_audit = float(
            resolved_bundle.quantitative_metrics.get("latest_close")
            or resolved_bundle.quantitative_metrics.get("bond_price")
            or 0.0
        )

        record = AuditRecord(
            run_timestamp=datetime.now(timezone.utc),
            skill_version="wealth_radar_v2.0",
            auditor=auditor,
            price_at_audit=price_at_audit,
            bundle=resolved_bundle,
            verdict=enforced_verdict,
            gate_overrides=overrides,
        )
        append_audit_records(self.app_cfg.audits_dir, [record])

        # 仅当明确指定 --commit-tier 且为指数主线触发时，将本次击穿档位写入 state.json 防后续刷屏
        if commit_tier and resolved_bundle.asset_type == "INDEX_BATCH":
            tier_val = resolved_bundle.quantitative_metrics.get("triggered_tier_pct")
            if isinstance(tier_val, (int, float)):
                state = load_state(self.app_cfg.state_path)
                sym_state = state.index_tiers.get(resolved_bundle.target_id, SymbolTierState())
                target_cfg = next(
                    (t for t in self.app_cfg.radar.index_monitor.targets if t.symbol == resolved_bundle.target_id),
                    None,
                )
                tiers_to_mark = (
                    [t.drawdown_pct for t in target_cfg.tiers if t.drawdown_pct >= float(tier_val)]
                    if target_cfg
                    else [float(tier_val)]
                )
                for tv in tiers_to_mark:
                    if tv not in sym_state.triggered_tiers:
                        sym_state.triggered_tiers.append(tv)
                sym_state.triggered_tiers.sort(reverse=True)
                state.index_tiers[resolved_bundle.target_id] = sym_state
                save_state_atomic(self.app_cfg.state_path, state)

        return record

    def add_index_holding(
        self,
        holding: IndexHolding,
        as_of_date: Optional[date] = None,
    ) -> PortfolioSnapshot:
        """原子新增或合并指数/QDII 持仓（按加权平均成本合并同 symbol+qdii_fund_code 记录）。"""
        today = as_of_date or date.today()
        portfolio = load_portfolio(self.app_cfg.portfolio_path, default_date=today)
        existing = next(
            (
                h
                for h in portfolio.index_holdings
                if h.symbol == holding.symbol and h.qdii_fund_code == holding.qdii_fund_code
            ),
            None,
        )
        if existing is not None:
            total_amt = existing.invested_cny + holding.invested_cny
            if total_amt > 0:
                existing.avg_entry_price = round(
                    (
                        existing.invested_cny * existing.avg_entry_price
                        + holding.invested_cny * holding.avg_entry_price
                    )
                    / total_amt,
                    4,
                )
            existing.invested_cny = round(total_amt, 2)
            existing.first_buy_date = min(existing.first_buy_date, holding.first_buy_date)
            if holding.qdii_holdings_code:
                existing.qdii_holdings_code = holding.qdii_holdings_code
        else:
            portfolio.index_holdings.append(holding)
        portfolio.updated_at = today
        save_portfolio_atomic(self.app_cfg.portfolio_path, portfolio)
        return portfolio

    def add_cb_holding(
        self,
        holding: CBHolding,
        as_of_date: Optional[date] = None,
    ) -> PortfolioSnapshot:
        """原子新增或合并可转债持仓。"""
        today = as_of_date or date.today()
        portfolio = load_portfolio(self.app_cfg.portfolio_path, default_date=today)
        existing = next(
            (h for h in portfolio.cb_holdings if h.bond_code == holding.bond_code),
            None,
        )
        if existing is not None:
            total_qty = existing.quantity + holding.quantity
            existing.avg_cost_price = round(
                (existing.quantity * existing.avg_cost_price + holding.quantity * holding.avg_cost_price)
                / total_qty,
                3,
            )
            existing.quantity = total_qty
            existing.buy_date = min(existing.buy_date, holding.buy_date)
        else:
            portfolio.cb_holdings.append(holding)
        portfolio.updated_at = today
        save_portfolio_atomic(self.app_cfg.portfolio_path, portfolio)
        return portfolio

    def remove_holding(
        self,
        asset_type: AssetType,
        target_id: str,
        as_of_date: Optional[date] = None,
    ) -> Tuple[PortfolioSnapshot, bool]:
        """原子移除指定持仓（支持按 symbol / qdii_fund_code / bond_code 匹配）。"""
        today = as_of_date or date.today()
        portfolio = load_portfolio(self.app_cfg.portfolio_path, default_date=today)
        removed = False
        if asset_type == "INDEX_BATCH":
            before = len(portfolio.index_holdings)
            portfolio.index_holdings = [
                h
                for h in portfolio.index_holdings
                if h.symbol != target_id and h.qdii_fund_code != target_id
            ]
            removed = len(portfolio.index_holdings) < before
        else:
            before = len(portfolio.cb_holdings)
            portfolio.cb_holdings = [h for h in portfolio.cb_holdings if h.bond_code != target_id]
            removed = len(portfolio.cb_holdings) < before
        if removed:
            portfolio.updated_at = today
            save_portfolio_atomic(self.app_cfg.portfolio_path, portfolio)
        return portfolio, removed


# =============================================================================
# 零网络内置离线演练提供器（供 --dry-run）
# =============================================================================


class DryRunDataProvider:
    """零网络内置离线夹具提供器（实现全部 4 个数据源协议），用于 --dry-run 演练。"""

    def __init__(self, trade_date: date) -> None:
        self._trade_date = trade_date

    def fetch_index_history(
        self,
        symbol: str,
        source: str,
        market_timezone: MarketTimezone,
        lookback_days: int,
    ) -> IndexQuoteSeries:
        # 构造 25 个交易日序列，便于演示 120 日回撤与 QDII 相关性计算
        bars: List[PriceBar] = []
        base = 520.0 if symbol == "QQQ" else 5.80
        start = self._trade_date - timedelta(days=35)
        for i in range(25):
            dt = start + timedelta(days=i)
            wave = 0.012 * ((i % 4) - 1.5)
            if symbol == "QQQ":
                val = base * (1.0 - 0.0046 * i + (wave if i < 24 else 0.0))  # 末尾约 -11.0% 回撤
            else:
                val = base * (1.0 - 0.0005 * (i % 4))
            bars.append(PriceBar(trade_date=dt, close=round(val, 4)))
        as_of = (
            f"{(self._trade_date - timedelta(days=1)).isoformat()} US Close"
            if market_timezone == "US"
            else f"{self._trade_date.isoformat()} 14:30 CST"
        )
        return IndexQuoteSeries(
            symbol=symbol,
            source=source,
            market_timezone=market_timezone,
            bars=bars,
            data_as_of=as_of,
        )

    def fetch_latest_index_price(self, symbol: str, source: str) -> Optional[float]:
        etf_spots = {"513100": 2.05, "159941": 1.52, "159659": 2.19, "159501": 1.94, "513300": 2.49}
        if symbol in etf_spots:
            return etf_spots[symbol]
        return 462.5 if symbol == "QQQ" else 5.79

    def fetch_index_news(self, symbol: str, source: str, max_items: int) -> List[NoticeItem]:
        return [
            NoticeItem(
                pub_date=self._trade_date - timedelta(days=1),
                title="美债收益率反弹引发科技成长股回调，龙头资本开支指引保持稳健",
                snippet="市场重新定价降息节奏导致成长股阶段性估值消化，但 AI 算力需求依然强劲。",
                detail_fetched=True,
            )
        ]

    def fetch_cb_ipos(self, trade_date: date) -> List[CBIpoItem]:
        return [
            CBIpoItem(
                bond_code="123999",
                bond_name="演练新债",
                subscribe_date=trade_date,
                credit_rating="AA",
                issue_scale_billion=8.5,
            )
        ]

    def fetch_cb_market_rows(self) -> List[CBMarketRow]:
        return [
            CBMarketRow(
                bond_code="123001",
                bond_name="陷阱转债",
                stock_code="300001",
                stock_name="陷阱股份",
                price=102.5,
                premium_rate_pct=22.0,
                ytm_pct=2.1,
                remaining_years=1.8,
                stock_price=8.5,
                credit_rating="AA-",
            ),
            CBMarketRow(
                bond_code="123002",
                bond_name="稳健转债",
                stock_code="300002",
                stock_name="稳健科技",
                price=104.2,
                premium_rate_pct=24.5,
                ytm_pct=1.6,
                remaining_years=1.6,
                stock_price=12.4,
                credit_rating="AA+sti",
            ),
            CBMarketRow(
                bond_code="123003",
                bond_name="违约垃圾债",
                stock_code="300003",
                stock_name="危局股份",
                price=82.0,
                premium_rate_pct=35.0,
                ytm_pct=14.0,
                remaining_years=1.2,
                stock_price=1.45,
                credit_rating="BBB+",
            ),
        ]

    def fetch_stock_notices(
        self,
        stock_code: str,
        lookback_days: int,
        fetch_detail_keywords: Sequence[str],
        max_detail_chars: int,
        as_of_date: date,
    ) -> List[NoticeItem]:
        if stock_code == "300001":
            return [
                NoticeItem(
                    pub_date=as_of_date - timedelta(days=10),
                    title="关于不向下修正“陷阱转债”转股价格的公告",
                    snippet="公司董事会决定本次不向下修正转股价格，未来6个月内（至2027-05-14）不提出向下修正方案。",
                    detail_fetched=True,
                )
            ]
        return [
            NoticeItem(
                pub_date=as_of_date - timedelta(days=12),
                title="2026年第三季度业绩预告：净利润同比预增18%",
                snippet="主营订单稳健增长，经营性现金流同比改善，无逾期及立案事项。",
                detail_fetched=True,
            )
        ]

    def fetch_latest_cb_price(self, bond_code: str) -> Optional[float]:
        for row in self.fetch_cb_market_rows():
            if row.bond_code == bond_code:
                return row.price
        return None

    def fetch_purchase_info_map(self, fund_codes: Sequence[str]) -> Dict[str, QDIIPurchaseInfo]:
        sample = {
            "021277": QDIIPurchaseInfo(
                fund_code="021277",
                fund_name="广发全球精选股票(QDII)人民币C",
                purchase_status="限大额",
                daily_limit_cny=2000.0,
                fee_rate_pct=0.0,
            ),
            "022184": QDIIPurchaseInfo(
                fund_code="022184",
                fund_name="富国全球科技互联网股票(QDII)C",
                purchase_status="限大额",
                daily_limit_cny=100000.0,
                fee_rate_pct=0.0,
            ),
            "008971": QDIIPurchaseInfo(
                fund_code="008971",
                fund_name="大成纳斯达克100ETF联接(QDII)C",
                purchase_status="限大额",
                daily_limit_cny=10.0,
                fee_rate_pct=0.0,
            ),
        }
        return {code: sample[code] for code in fund_codes if code in sample}

    def fetch_quarterly_holdings(self, holdings_code: str, year: int) -> List[QDIIHoldingItem]:
        q_label = f"{year}年1季度股票投资明细"
        if holdings_code == "270023":
            return [
                QDIIHoldingItem(stock_code="NVDA", stock_name="英伟达", weight_pct=8.5, quarter=q_label),
                QDIIHoldingItem(stock_code="AAPL", stock_name="苹果", weight_pct=7.8, quarter=q_label),
                QDIIHoldingItem(stock_code="GOOG", stock_name="谷歌-C", weight_pct=7.2, quarter=q_label),
                QDIIHoldingItem(stock_code="AMZN", stock_name="亚马逊", weight_pct=6.9, quarter=q_label),
                QDIIHoldingItem(stock_code="ASML", stock_name="阿斯麦", weight_pct=6.2, quarter=q_label),
                QDIIHoldingItem(stock_code="AVGO", stock_name="博通", weight_pct=5.4, quarter=q_label),
                QDIIHoldingItem(stock_code="02513", stock_name="智谱", weight_pct=4.0, quarter=q_label),
            ]
        return [
            QDIIHoldingItem(stock_code="TSM", stock_name="台积电", weight_pct=9.5, quarter=q_label),
            QDIIHoldingItem(stock_code="NVDA", stock_name="英伟达", weight_pct=9.0, quarter=q_label),
            QDIIHoldingItem(stock_code="GOOGL", stock_name="谷歌-A", weight_pct=8.0, quarter=q_label),
            QDIIHoldingItem(stock_code="AMD", stock_name="超威半导体", weight_pct=7.2, quarter=q_label),
            QDIIHoldingItem(stock_code="09899", stock_name="网易云音乐", weight_pct=5.0, quarter=q_label),
        ]

    def fetch_fund_nav_series(self, fund_code: str, lookback_days: int) -> List[PriceBar]:
        start = self._trade_date - timedelta(days=35)
        factor = 1.0 if fund_code == "021277" else 0.92
        return [
            PriceBar(
                trade_date=start + timedelta(days=i),
                close=round(
                    2.0 * (1.0 - 0.0046 * factor * i + (0.0115 * factor * ((i % 4) - 1.5) if i < 24 else 0.0)),
                    4,
                ),
            )
            for i in range(25)
        ]

    def fetch_etf_latest_nav_map(self, etf_codes: Sequence[str]) -> Dict[str, float]:
        navs = {"513100": 1.6742, "159941": 1.2516, "159659": 1.8102, "159501": 1.5723, "513300": 2.0785}
        return {code: navs[code] for code in etf_codes if code in navs}
