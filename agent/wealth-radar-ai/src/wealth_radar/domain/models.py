"""核心 Pydantic v2 数据契约（v1.1）。"""

from __future__ import annotations

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
]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
ThesisStatus = Literal["INTACT", "STRENGTHENED", "WEAKENED", "BROKEN", "UNKNOWN"]
FinalAction = Literal["REJECT", "WATCHLIST", "APPROVE_BUY"]
MarketTimezone = Literal["US", "CN"]

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


def credit_rating_meets_min(rating: str, min_rating: str) -> bool:
    """判断给定信用评级是否达到最低评级门槛（未知评级按不达标处理，Fail-Closed）。"""
    normalized = rating.strip().upper()
    threshold = min_rating.strip().upper()
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
    detail_fetched: bool = False        # 标注是否成功抓取公告正文片段（避免仅凭标题误判锁定期）
    matched_keywords: List[str] = Field(default_factory=list)


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
    target_id: str                      # 如 "123xxx" 或 "QQQ"
    target_name: str
    data_as_of: str                     # 如 "2026-11-23 US Close (T-1 滞后，申购按今晚净值)"
    quantitative_metrics: Dict[str, float | str]
    trigger_summary: str                # 如 "首次触发 -10% 档位(拟投1200元)" 或 "合规双低第2(103.5/溢价24%/YTM+1.8%)"
    budget_check: Dict[str, float | str | bool] = Field(default_factory=dict)
    notices: List[NoticeItem] = Field(default_factory=list)
    news_items: List[NoticeItem] = Field(default_factory=list)
    user_holding_context: Dict[str, float | str] = Field(default_factory=dict)
    evidence_sha256: str = ""


class AuditVerdict(BaseModel):
    target_id: str
    target_name: str
    asset_type: AssetType
    audit_mode: AuditMode
    hard_veto: bool = Field(
        description=(
            "CRO_VETO 模式下存在明确否决项（不下修锁定期、立案、违约、退市、评级大幅下调、关键证据缺失）时必须为 true；"
            "INDEX_BRIEFING 模式下仅当出现不可逆结构性崩坏(BROKEN)或预算/证据硬失败时才为 true"
        )
    )
    veto_reason: Optional[str] = Field(
        default=None,
        description="当 hard_veto 为 true 时，用一句话给出最硬核的否决事实",
    )
    lockup_expiry_date: Optional[str] = Field(
        default=None,
        description="仅 CB_CONVEX：若证据含不下修公告，提取锁定期截止日(YYYY-MM-DD)，未披露则填 UNSPECIFIED_IN_TITLE",
    )
    drawdown_attribution: Optional[str] = Field(
        default=None,
        description="仅 INDEX_BRIEFING：用 1~2 句话提炼本次回撤的核心客观归因（宏观利率/盈利/政策/情绪）",
    )
    credit_or_structural_risk: RiskLevel
    thesis_status: ThesisStatus
    bear_case_arguments: List[str] = Field(
        min_length=1,
        max_length=4,
        description="必须列出至少 1 条反对买入或需警惕的空头/风险论据",
    )
    bull_case_catalysts: List[str] = Field(
        default_factory=list,
        max_length=3,
        description="仅基于提供证据中存在的潜在催化或支撑因素",
    )
    evidence_citations: List[str] = Field(
        default_factory=list,
        description="引用的公告或新闻日期与标题，严禁编造输入中不存在的日期或公告",
    )
    missing_info_warnings: List[str] = Field(
        default_factory=list,
        description="指出缺失的关键信息（例如：不下修公告未抓到正文无法确认截止日、未提供财务数据）",
    )
    final_action: FinalAction
    confidence_score: int = Field(ge=0, le=100)


class AuditRecord(BaseModel):
    run_timestamp: datetime
    prompt_version: str
    provider: str
    model: str
    price_at_audit: float
    bundle: EvidenceBundle
    verdict: AuditVerdict
    from_cache: bool = False


class SymbolTierState(BaseModel):
    triggered_tiers: List[float] = Field(default_factory=list)
    cooldown_until: Optional[date] = None
    last_reset_date: Optional[date] = None


class RadarState(BaseModel):
    index_tiers: Dict[str, SymbolTierState] = Field(default_factory=dict)
    daily_audit_cache: Dict[str, AuditVerdict] = Field(default_factory=dict)


class PipelineReport(BaseModel):
    trade_date: date
    run_timestamp: datetime
    dry_run: bool = False
    positions_only: bool = False
    position_alerts: List[PositionAlert] = Field(default_factory=list)
    cb_ipos: List[CBIpoItem] = Field(default_factory=list)
    ipo_cash_warning: Optional[str] = None
    index_candidates: List[IndexCandidate] = Field(default_factory=list)
    cb_candidates: List[CBCandidate] = Field(default_factory=list)
    audit_records: List[AuditRecord] = Field(default_factory=list)
    section_errors: Dict[str, str] = Field(default_factory=dict)
