"""核心 Pydantic v2 数据契约（v2.0 — Skill 基础设施 + QDII 平替路由 + 硬门禁账本）。"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

AssetType = Literal["INDEX_BATCH", "CB_CONVEX"]
AuditMode = Literal["CRO_VETO", "INDEX_BRIEFING"]
AlertSeverity = Literal["INFO", "WARNING", "CRITICAL"]
PositionAlertType = Literal[
    "REDEEM_URGENT",          # 已公告强赎或临近触发强赎
    "CREDIT_DETERIORATION",   # 持仓跌破警戒线或出现立案/退市/评级下调公告
    "PUTBACK_WINDOW",         # 进入回售触发或回售登记期
    "TAKE_PROFIT",            # 达到预设止盈/再平衡阈值
    "C_CLASS_FEE_DRAG",       # 场外 C 类持仓临近 1 年费率磨损提示
    "STYLE_DRIFT",            # 持仓主动 QDII 出现风格漂移（美股纯度跌破底线或塞入过多 A/港股）
]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
ThesisStatus = Literal["INTACT", "STRENGTHENED", "WEAKENED", "BROKEN", "UNKNOWN"]
FinalAction = Literal["REJECT", "WATCHLIST", "APPROVE_BUY"]
MarketTimezone = Literal["US", "CN"]
HoldingRegion = Literal["US_DEVELOPED", "CN_A", "HK", "OTHER"]

# 国内信用评级序值（越大越安全）
CREDIT_RATING_RANK: Dict[str, int] = {
    "AAA": 12,
    "AA+": 11,
    "AA": 10,
    "AA-": 9,
    "A+": 8,
    "A": 7,
    "A-": 6,
    "BBB+": 5,
    "BBB": 4,
    "BBB-": 3,
    "BB+": 2,
    "BB": 1,
    "B": 0,
    "CCC": -1,
    "CC": -2,
    "C": -3,
    "D": -4,
}

_CREDIT_RATING_PREFIX = re.compile(
    r"^(AAA|AA\+|AA-|AA|A\+|A-|A|BBB\+|BBB-|BBB|BB\+|BB-|BB|B\+|B-|B|CCC|CC|C|D)"
)


def normalize_credit_rating(rating: str) -> Optional[str]:
    """提取标准国内信用评级前缀（兼容 AA+sti / AApi 等评级机构后缀）。"""
    cleaned = rating.strip().upper()
    if not cleaned:
        return None
    match = _CREDIT_RATING_PREFIX.match(cleaned)
    return match.group(1) if match else None


def credit_rating_meets_min(rating: str, min_rating: str) -> bool:
    """判断给定信用评级是否达到最低评级门槛（未知评级按不达标处理，Fail-Closed）。"""
    normalized = normalize_credit_rating(rating)
    threshold = normalize_credit_rating(min_rating)
    if normalized is None or threshold is None:
        return False
    if normalized not in CREDIT_RATING_RANK or threshold not in CREDIT_RATING_RANK:
        return False
    return CREDIT_RATING_RANK[normalized] >= CREDIT_RATING_RANK[threshold]


class IndexHolding(BaseModel):
    symbol: str
    name: str
    fund_class: Literal["A", "C", "ETF"] = "C"
    correlation_group: str
    invested_cny: float = Field(ge=0)
    avg_entry_price: float = Field(gt=0)
    first_buy_date: date
    qdii_fund_code: Optional[str] = None       # 若通过 QDII 平替持有，填写实际申购代码（如 021277）
    qdii_holdings_code: Optional[str] = None   # 季报持仓主代码（如 270023），用于 Stage 0 风格漂移监测


class CBHolding(BaseModel):
    bond_code: str
    bond_name: str
    stock_code: str
    quantity: int = Field(gt=0)         # 张数（10 张 = 1 手）
    avg_cost_price: float = Field(gt=0)
    buy_date: date


class PortfolioSnapshot(BaseModel):
    updated_at: date
    index_holdings: List[IndexHolding] = Field(default_factory=list)
    cb_holdings: List[CBHolding] = Field(default_factory=list)


class PositionAlert(BaseModel):
    target_id: str
    target_name: str
    asset_type: AssetType
    alert_type: PositionAlertType
    severity: AlertSeverity
    message: str
    recommended_action: str


class PriceBar(BaseModel):
    trade_date: date
    close: float = Field(gt=0)


class IndexQuoteSeries(BaseModel):
    symbol: str
    source: str
    market_timezone: MarketTimezone
    bars: List[PriceBar]
    data_as_of: str


class CBMarketRow(BaseModel):
    bond_code: str
    bond_name: str
    stock_code: str
    stock_name: str = ""
    price: float = Field(gt=0)
    premium_rate_pct: float
    ytm_pct: float
    remaining_years: float = Field(ge=0)
    stock_price: float = Field(gt=0)
    credit_rating: str
    is_st: bool = False
    redeem_announced: bool = False
    redeem_days_remaining: Optional[int] = None
    putback_triggered: bool = False
    putback_register_active: bool = False


class CBIpoItem(BaseModel):
    bond_code: str
    bond_name: str
    subscribe_date: date
    credit_rating: str = ""
    issue_scale_billion: Optional[float] = None


class NoticeItem(BaseModel):
    pub_date: date
    title: str
    snippet: str = ""
    detail_fetched: bool = False
    matched_keywords: List[str] = Field(default_factory=list)


# =============================================================================
# QDII 平替智能路由与场内 ETF 溢价守卫模型 (v2.0)
# =============================================================================


class QDIIHoldingItem(BaseModel):
    stock_code: str
    stock_name: str
    weight_pct: float = Field(ge=0)
    quarter: str = ""
    region: HoldingRegion = "OTHER"
    is_mega_cap_tech: bool = False


class QDIIPurchaseInfo(BaseModel):
    fund_code: str
    fund_name: str
    purchase_status: str                 # 如 "开放申购" / "限大额" / "暂停申购"
    daily_limit_cny: Optional[float] = None
    fee_rate_pct: Optional[float] = None
    nav: Optional[float] = None
    nav_date: str = ""


class ETFSpotPremium(BaseModel):
    code: str
    name: str
    spot_price: float = Field(gt=0)
    latest_nav: float = Field(gt=0)
    premium_pct: float
    executable: bool
    warning: str = ""


class QDIIProxyEvaluation(BaseModel):
    fund_code: str
    holdings_code: str
    name: str
    company: str
    is_passive: bool
    purchase_status: str
    daily_limit_cny: Optional[float] = None
    fee_rate_pct: Optional[float] = None
    us_developed_top10_pct: Optional[float] = None
    cn_hk_top10_pct: Optional[float] = None
    mega_cap_overlap_count: int = 0
    corr_with_benchmark: Optional[float] = None
    latest_quarter: str = ""
    top_holdings: List[QDIIHoldingItem] = Field(default_factory=list)
    passed: bool = False
    reject_reasons: List[str] = Field(default_factory=list)
    purity_score: float = 0.0


class QDIISplitAllocation(BaseModel):
    fund_code: str
    name: str
    company: str
    allocated_cny: float = Field(gt=0)
    daily_limit_cny: Optional[float] = None
    is_passive: bool
    us_developed_top10_pct: Optional[float] = None
    corr_with_benchmark: Optional[float] = None


class QDIIRoutePlan(BaseModel):
    benchmark_symbol: str
    requested_amount_cny: float = Field(ge=0)
    total_allocated_cny: float = Field(ge=0)
    shortfall_cny: float = Field(ge=0)
    allocations: List[QDIISplitAllocation] = Field(default_factory=list)
    proxy_evaluations: List[QDIIProxyEvaluation] = Field(default_factory=list)
    etf_premiums: List[ETFSpotPremium] = Field(default_factory=list)
    summary: str = ""


# =============================================================================
# 筛选候选、证据包、审计结论与扫描数据包
# =============================================================================


class IndexCandidate(BaseModel):
    symbol: str
    name: str
    correlation_group: str
    market_timezone: MarketTimezone
    data_as_of: str
    latest_close: float
    peak_120d: float
    drawdown_pct: float
    triggered_tier_pct: float
    requested_amount_cny: float
    approved_amount_cny: float
    budget_allowed: bool
    budget_reason: str = ""
    qdii_router_enabled: bool = False
    budget_check: Dict[str, float | str | bool] = Field(default_factory=dict)
    user_holding_context: Dict[str, float | str] = Field(default_factory=dict)
    trigger_summary: str


class CBCandidate(BaseModel):
    row: CBMarketRow
    double_low: float
    rank: int
    available_budget_cny: float
    budget_allowed: bool
    commission_warning: Optional[str] = None
    budget_check: Dict[str, float | str | bool] = Field(default_factory=dict)
    user_holding_context: Dict[str, float | str] = Field(default_factory=dict)
    trigger_summary: str


class EvidenceBundle(BaseModel):
    trade_date: date
    asset_type: AssetType
    audit_mode: AuditMode
    target_id: str
    target_name: str
    data_as_of: str
    quantitative_metrics: Dict[str, float | str]
    trigger_summary: str
    budget_check: Dict[str, float | str | bool] = Field(default_factory=dict)
    notices: List[NoticeItem] = Field(default_factory=list)
    news_items: List[NoticeItem] = Field(default_factory=list)
    user_holding_context: Dict[str, float | str] = Field(default_factory=dict)
    qdii_route_plan: Optional[QDIIRoutePlan] = None
    evidence_sha256: str = ""


class AuditVerdict(BaseModel):
    target_id: str
    target_name: str
    asset_type: AssetType
    audit_mode: AuditMode
    hard_veto: bool = Field(
        description=(
            "CRO_VETO 模式下存在明确否决项（不下修锁定期、立案、违约、退市、评级下调、关键证据缺失）时必须为 true；"
            "INDEX_BRIEFING 模式下仅当不可逆结构性破坏(BROKEN)、预算超限或试图追高高溢价 ETF 时为 true"
        )
    )
    veto_reason: Optional[str] = None
    lockup_expiry_date: Optional[str] = None
    drawdown_attribution: Optional[str] = None
    execution_plan: Optional[str] = Field(
        default=None,
        description="可执行落地方案（如 QDII 拆单代码与金额，或可转债单笔拟投金额）",
    )
    selected_etf_code: Optional[str] = Field(
        default=None,
        description="若建议场内 ETF 执行，必须填入 ETF 代码供代码层溢价红线核查",
    )
    credit_or_structural_risk: RiskLevel
    thesis_status: ThesisStatus
    bear_case_arguments: List[str] = Field(min_length=1, max_length=5)
    bull_case_catalysts: List[str] = Field(default_factory=list, max_length=4)
    evidence_citations: List[str] = Field(default_factory=list)
    web_research_notes: List[str] = Field(
        default_factory=list,
        description="Agent 使用 Harness 联网工具补查公告原文/财报/基金经理近况的关键核验结论（必须附来源与日期）",
    )
    missing_info_warnings: List[str] = Field(default_factory=list)
    final_action: FinalAction
    confidence_score: int = Field(ge=0, le=100)


class AuditRecord(BaseModel):
    run_timestamp: datetime
    skill_version: str = "wealth_radar_v2.0"
    auditor: str = "agent_harness"
    price_at_audit: float
    bundle: EvidenceBundle
    verdict: AuditVerdict
    gate_overrides: List[str] = Field(default_factory=list)


class SymbolTierState(BaseModel):
    triggered_tiers: List[float] = Field(default_factory=list)
    cooldown_until: Optional[date] = None
    last_reset_date: Optional[date] = None


class RadarState(BaseModel):
    index_tiers: Dict[str, SymbolTierState] = Field(default_factory=dict)


class ScanPacket(BaseModel):
    """确定性基础设施扫描数据包（供 Sentinel 推送与 Agent Skill 消费）。"""

    trade_date: date
    run_timestamp: datetime
    dry_run: bool = False
    position_alerts: List[PositionAlert] = Field(default_factory=list)
    cb_ipos: List[CBIpoItem] = Field(default_factory=list)
    ipo_cash_warning: Optional[str] = None
    index_candidates: List[IndexCandidate] = Field(default_factory=list)
    index_bundles: List[EvidenceBundle] = Field(default_factory=list)
    qdii_route_plan: Optional[QDIIRoutePlan] = None
    cb_candidates: List[CBCandidate] = Field(default_factory=list)
    cb_bundles: List[EvidenceBundle] = Field(default_factory=list)
    section_errors: Dict[str, str] = Field(default_factory=dict)

    @property
    def has_actionable_signal(self) -> bool:
        return bool(
            self.position_alerts
            or self.cb_ipos
            or any(c.budget_allowed for c in self.index_candidates)
            or any(c.budget_allowed for c in self.cb_candidates)
        )
