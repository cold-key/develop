"""Stage 0 -> 打新 -> Stage 1 -> Stage 2 -> 落盘 主管线（带板块级故障隔离与离线演练夹具）。"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Sequence, Tuple

from wealth_radar.app.audit_store import append_audit_records, load_state, save_state_atomic
from wealth_radar.config.loader import AppConfig, load_portfolio
from wealth_radar.core.cb_screener import filter_cb_ipos, screen_cb_candidates
from wealth_radar.core.evidence_packer import (
    compute_evidence_sha256,
    pack_cb_evidence,
    pack_index_evidence,
)
from wealth_radar.core.index_screener import screen_index_targets
from wealth_radar.core.position_monitor import evaluate_positions
from wealth_radar.data_feed.protocols import CBProvider, MarketProvider, NewsProvider
from wealth_radar.domain.models import (
    AuditRecord,
    AuditVerdict,
    CBCandidate,
    CBIpoItem,
    CBMarketRow,
    EvidenceBundle,
    IndexCandidate,
    IndexQuoteSeries,
    MarketTimezone,
    NoticeItem,
    PipelineReport,
    PortfolioSnapshot,
    PositionAlert,
    PriceBar,
)
from wealth_radar.llm.base import BaseAuditLLM


class RadarPipeline:
    """三阶段投研风控主管线（严格依赖协议接口，支持 100% 离线测试）。"""

    def __init__(
        self,
        app_cfg: AppConfig,
        market_provider: MarketProvider,
        news_provider: NewsProvider,
        cb_provider: CBProvider,
        audit_llm: Optional[BaseAuditLLM] = None,
    ) -> None:
        self.app_cfg = app_cfg
        self.market_provider = market_provider
        self.news_provider = news_provider
        self.cb_provider = cb_provider
        self.audit_llm = audit_llm

    def run(
        self,
        trade_date: Optional[date] = None,
        *,
        dry_run: bool = False,
        no_llm: bool = False,
        force_audit: bool = False,
        positions_only: bool = False,
        portfolio_override: Optional[PortfolioSnapshot] = None,
    ) -> PipelineReport:
        today = trade_date or date.today()
        run_ts = datetime.now(timezone.utc)
        radar_cfg = self.app_cfg.radar

        portfolio = (
            portfolio_override
            if portfolio_override is not None
            else load_portfolio(self.app_cfg.portfolio_path, default_date=today)
        )
        state = load_state(self.app_cfg.state_path)
        updated_state = state.model_copy(deep=True)

        section_errors: Dict[str, str] = {}
        position_alerts: List[PositionAlert] = []
        cb_ipos: List[CBIpoItem] = []
        ipo_cash_warning: Optional[str] = None
        index_candidates: List[IndexCandidate] = []
        cb_candidates: List[CBCandidate] = []
        audit_records: List[AuditRecord] = []

        # 共享抓取缓存（避免 Stage 0 和 Stage 1 重复拉取同一份行情）
        cb_market_rows: Optional[List[CBMarketRow]] = None
        index_quotes_by_symbol: Dict[str, IndexQuoteSeries] = {}

        # =====================================================================
        # Stage 0: 持仓存续期守卫与卖出预警（最高优先级、不依赖 LLM、故障隔离）
        # =====================================================================
        cb_quotes_map: Dict[str, CBMarketRow] = {}
        cb_holding_notices: Dict[str, List[NoticeItem]] = {}
        index_latest_prices: Dict[str, float] = {}

        if portfolio.cb_holdings:
            try:
                cb_market_rows = self.cb_provider.fetch_cb_market_rows()
                cb_quotes_map = {row.bond_code: row for row in cb_market_rows}
            except Exception as exc:
                section_errors["stage0_cb_quotes"] = f"持仓可转债行情抓取失败: {exc}"

            for holding in portfolio.cb_holdings:
                try:
                    cb_holding_notices[holding.stock_code] = self.cb_provider.fetch_stock_notices(
                        stock_code=holding.stock_code,
                        lookback_days=14,
                        fetch_detail_keywords=radar_cfg.cb_screener.fetch_detail_keywords,
                        max_detail_chars=radar_cfg.evidence_budget.max_detail_chars_per_notice,
                        as_of_date=today,
                    )
                except Exception as exc:
                    section_errors[f"stage0_cb_notice_{holding.stock_code}"] = str(exc)

        if portfolio.index_holdings:
            source_by_symbol = {t.symbol: (t.source, t.market_timezone) for t in radar_cfg.index_monitor.targets}
            for idx_holding in portfolio.index_holdings:
                src, tz = source_by_symbol.get(
                    idx_holding.symbol,
                    ("yfinance" if idx_holding.symbol.isalpha() else "akshare", "CN"),
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
                    section_errors[f"stage0_index_{idx_holding.symbol}"] = (
                        f"持仓指数 {idx_holding.symbol} 行情失败: {exc}"
                    )

        position_alerts = evaluate_positions(
            portfolio=portfolio,
            cb_quotes=cb_quotes_map,
            cb_recent_notices=cb_holding_notices,
            index_latest_prices=index_latest_prices,
            cfg=radar_cfg.position_monitor,
            as_of_date=today,
        )

        if positions_only:
            return PipelineReport(
                trade_date=today,
                run_timestamp=run_ts,
                dry_run=dry_run,
                positions_only=True,
                position_alerts=position_alerts,
                section_errors=section_errors,
            )

        # =====================================================================
        # 今日可转债打新（独立隔离，直接置顶推送）
        # =====================================================================
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
        # Stage 1 & Stage 2: 指数回撤主线舱（单标的隔离）
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
                section_errors[f"index_quote_{target.symbol}"] = f"指数 {target.symbol} 行情抓取失败: {exc}"

        index_candidates, updated_state = screen_index_targets(
            cfg=radar_cfg.index_monitor,
            quotes_by_symbol=index_quotes_by_symbol,
            portfolio=portfolio,
            state=updated_state,
            trade_date=today,
        )

        target_source_map = {t.symbol: t.source for t in radar_cfg.index_monitor.targets}
        if not no_llm and self.audit_llm is not None:
            for cand in index_candidates:
                if not cand.budget_allowed:
                    # 预算耗尽不调用 LLM 消耗 Token
                    continue
                news_items: List[NoticeItem] = []
                try:
                    news_items = self.news_provider.fetch_index_news(
                        symbol=cand.symbol,
                        source=target_source_map.get(cand.symbol, "yfinance"),
                        max_items=radar_cfg.evidence_budget.max_news_per_target,
                    )
                except Exception as exc:
                    section_errors[f"index_news_{cand.symbol}"] = f"指数 {cand.symbol} 新闻抓取失败(按空证据降级): {exc}"

                bundle = pack_index_evidence(
                    candidate=cand,
                    news_items=news_items,
                    trade_date=today,
                    budget=radar_cfg.evidence_budget,
                )
                record, _ = self.audit_llm.audit(
                    bundle=bundle,
                    price_at_audit=cand.latest_close,
                    cache=updated_state.daily_audit_cache,
                    force_audit=force_audit,
                )
                audit_records.append(record)

        # =====================================================================
        # Stage 1 & Stage 2: 可转债低价下修博弈舱（故障隔离）
        # =====================================================================
        if cb_market_rows is None:
            try:
                cb_market_rows = self.cb_provider.fetch_cb_market_rows()
            except Exception as exc:
                section_errors["cb_market"] = f"可转债全市场行情抓取失败: {exc}"

        if cb_market_rows is not None:
            cb_candidates = screen_cb_candidates(
                rows=cb_market_rows,
                portfolio=portfolio,
                cfg=radar_cfg.cb_screener,
            )
            if not no_llm and self.audit_llm is not None:
                for cb_cand in cb_candidates:
                    if not cb_cand.budget_allowed:
                        continue
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
                            f"正股 {cb_cand.row.stock_code} 公告抓取失败(按空证据 Fail-Closed): {exc}"
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
                    record, _ = self.audit_llm.audit(
                        bundle=bundle,
                        price_at_audit=cb_cand.row.price,
                        cache=updated_state.daily_audit_cache,
                        force_audit=force_audit,
                    )
                    audit_records.append(record)

        # =====================================================================
        # 原子持久化状态与审计归档（--dry-run 严禁改写磁盘状态）
        # =====================================================================
        if not dry_run:
            save_state_atomic(self.app_cfg.state_path, updated_state, current_date=today)
            append_audit_records(self.app_cfg.audits_dir, audit_records)

        return PipelineReport(
            trade_date=today,
            run_timestamp=run_ts,
            dry_run=dry_run,
            positions_only=False,
            position_alerts=position_alerts,
            cb_ipos=cb_ipos,
            ipo_cash_warning=ipo_cash_warning,
            index_candidates=index_candidates,
            cb_candidates=cb_candidates,
            audit_records=audit_records,
            section_errors=section_errors,
        )


# =============================================================================
# 内置离线演练提供器（供 --dry-run）与 test-llm 双模式测试夹具
# =============================================================================


class DryRunDataProvider:
    """零网络内置离线夹具提供器，用于 `wealth-radar run --dry-run` 演练整套管线。"""

    def __init__(self, trade_date: date) -> None:
        self._trade_date = trade_date

    def fetch_index_history(
        self,
        symbol: str,
        source: str,
        market_timezone: MarketTimezone,
        lookback_days: int,
    ) -> IndexQuoteSeries:
        start = self._trade_date - timedelta(days=30)
        if symbol == "QQQ":
            closes = [520.0, 515.0, 500.0, 485.0, 462.8]  # -11.0% 回撤，触发 -10% 档位
        else:
            closes = [5.80, 5.85, 5.82, 5.79, 5.78]       # -1.2% 回撤，未触发
        bars = [
            PriceBar(trade_date=start + timedelta(days=idx * 5), close=val)
            for idx, val in enumerate(closes)
        ]
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
        return 462.8 if symbol == "QQQ" else 5.78

    def fetch_index_news(self, symbol: str, source: str, max_items: int) -> List[NoticeItem]:
        return [
            NoticeItem(
                pub_date=self._trade_date - timedelta(days=1),
                title="美债收益率反弹叠加科技股季报前获利回吐，纳指100承压回调",
                snippet="市场重新定价降息节奏导致成长股估值阶段性消化，但龙头资本开支指引保持稳健。",
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
                credit_rating="AA",
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
                    snippet="公司董事会决定本次不向下修正转股价格，且自公告日起未来6个月内（至2027-05-14）均不提出向下修正方案。",
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


class DryRunAuditLLM(BaseAuditLLM):
    """供 --dry-run 离线演练使用的确定性本地模拟 LLM。"""

    provider_name = "dry_run_mock"

    def _call_provider(
        self,
        system_prompt: str,
        user_prompt: str,
        bundle: EvidenceBundle,
    ) -> AuditVerdict:
        if bundle.audit_mode == "INDEX_BRIEFING":
            return AuditVerdict(
                target_id=bundle.target_id,
                target_name=bundle.target_name,
                asset_type=bundle.asset_type,
                audit_mode="INDEX_BRIEFING",
                hard_veto=False,
                drawdown_attribution="美债收益率反弹引发科技估值阶段性消化，属常规周期回调而非基本面结构破坏。",
                credit_or_structural_risk="MEDIUM",
                thesis_status="INTACT",
                bear_case_arguments=["若美债利率持续走高，科技板块估值仍存在进一步下探风险。"],
                bull_case_catalysts=["龙头资本开支指引保持稳健，回撤已击穿预设左侧分批档位。"],
                evidence_citations=[f"{n.pub_date.isoformat()} {n.title}" for n in bundle.news_items[:2]],
                missing_info_warnings=[],
                final_action="APPROVE_BUY",
                confidence_score=78,
            )

        has_non_revision = any("不向下修正" in n.title or "不下修" in n.title for n in bundle.notices)
        if has_non_revision:
            return AuditVerdict(
                target_id=bundle.target_id,
                target_name=bundle.target_name,
                asset_type=bundle.asset_type,
                audit_mode="CRO_VETO",
                hard_veto=True,
                veto_reason="正股近期已公告未来6个月不向下修正转股价格（锁定期至2027-05-14），下修博弈逻辑失效。",
                lockup_expiry_date="2027-05-14",
                credit_or_structural_risk="HIGH",
                thesis_status="BROKEN",
                bear_case_arguments=["明确承诺6个月内不下修，直接封杀短期条款博弈空间。"],
                bull_case_catalysts=[],
                evidence_citations=[f"{n.pub_date.isoformat()} {n.title}" for n in bundle.notices[:2]],
                missing_info_warnings=[],
                final_action="REJECT",
                confidence_score=95,
            )

        return AuditVerdict(
            target_id=bundle.target_id,
            target_name=bundle.target_name,
            asset_type=bundle.asset_type,
            audit_mode="CRO_VETO",
            hard_veto=False,
            credit_or_structural_risk="LOW",
            thesis_status="INTACT",
            bear_case_arguments=["当前溢价率约24.5%，若正股走弱短期仍面临债性回撤。"],
            bull_case_catalysts=["正股三季报业绩预增且现金流改善，债底与下修赔率结构完好。"],
            evidence_citations=[f"{n.pub_date.isoformat()} {n.title}" for n in bundle.notices[:2]],
            missing_info_warnings=[],
            final_action="APPROVE_BUY",
            confidence_score=80,
        )


def build_test_llm_bundles(trade_date: Optional[date] = None) -> Tuple[EvidenceBundle, EvidenceBundle]:
    """构造 `wealth-radar test-llm` 使用的双模式测试夹具（转债不下修陷阱 + 指数常规回调归因）。"""
    today = trade_date or date.today()

    cb_trap = EvidenceBundle(
        trade_date=today,
        asset_type="CB_CONVEX",
        audit_mode="CRO_VETO",
        target_id="123888",
        target_name="测试陷阱转债",
        data_as_of=f"{today.isoformat()} 14:30 CST",
        quantitative_metrics={
            "bond_price": 103.2,
            "premium_rate_pct": 26.5,
            "double_low": 129.7,
            "ytm_pct": 1.85,
            "remaining_years": 1.9,
            "stock_price": 9.2,
            "credit_rating": "AA-",
        },
        trigger_summary="合规双低排名第1(双低129.7 | 现价103.2 | 溢价26.5% | YTM+1.85%)",
        budget_check={"allowed": True, "cb_available_cny": 3000.0, "reason": "OK"},
        notices=[
            NoticeItem(
                pub_date=today - timedelta(days=7),
                title="关于董事会提议不向下修正“测试陷阱转债”转股价格的公告",
                snippet="公司董事会审议通过：本次不向下修正转股价格，且自2026年11月17日起未来6个月内（至2027-05-17）如再次触发下修条款亦不提出向下修正方案。",
                detail_fetched=True,
                matched_keywords=["不向下修正"],
            )
        ],
        news_items=[],
        user_holding_context={"cb_invested_cny": 0.0, "already_holds_target": "NO"},
    )
    cb_trap.evidence_sha256 = compute_evidence_sha256(cb_trap)

    index_panic = EvidenceBundle(
        trade_date=today,
        asset_type="INDEX_BATCH",
        audit_mode="INDEX_BRIEFING",
        target_id="QQQ",
        target_name="纳指100 (对应场外C类)",
        data_as_of=f"{(today - timedelta(days=1)).isoformat()} US Close (T-1 美股收盘滞后，申购按今晚净值)",
        quantitative_metrics={
            "latest_close": 468.0,
            "peak_120d": 520.0,
            "drawdown_pct": -10.0,
            "triggered_tier_pct": -10.0,
            "requested_amount_cny": 1200.0,
            "approved_amount_cny": 1200.0,
        },
        trigger_summary="首次触发 -10.0% 回撤档位（拟投 1200 元）",
        budget_check={"allowed": True, "approved_amount_cny": 1200.0, "reason": "OK"},
        notices=[],
        news_items=[
            NoticeItem(
                pub_date=today - timedelta(days=1),
                title="通胀数据略超预期引发降息推迟担忧，纳斯达克100遭遇短期恐慌抛售",
                snippet="多位策略师警告短期波动加剧，但头部科技企业云业务营收与现金流仍保持两位数增长。",
                detail_fetched=True,
            )
        ],
        user_holding_context={"symbol_invested_cny": 800.0, "index_total_invested_cny": 800.0},
    )
    index_panic.evidence_sha256 = compute_evidence_sha256(index_panic)

    return cb_trap, index_panic
