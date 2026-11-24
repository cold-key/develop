"""YAML 配置、可选环境变量与持仓快照加载器（v2.0 — 零 LLM Key，含 QDII 路由配置与预算一致性校验）。"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Dict, List, Literal, Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError, model_validator

from wealth_radar.domain.errors import ConfigValidationError
from wealth_radar.domain.models import CREDIT_RATING_RANK, MarketTimezone, PortfolioSnapshot


class IndexTierConfig(BaseModel):
    drawdown_pct: float = Field(lt=0)
    amount_cny: float = Field(gt=0)


class IndexTargetConfig(BaseModel):
    symbol: str
    source: Literal["yfinance", "akshare", "akshare_us"]
    market_timezone: MarketTimezone = "CN"
    correlation_group: str
    name: str
    budget_cny: float = Field(gt=0)
    qdii_router_enabled: bool = False
    tiers: List[IndexTierConfig] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_tiers_and_budget(self) -> IndexTargetConfig:
        tier_sum = sum(t.amount_cny for t in self.tiers)
        if tier_sum > self.budget_cny + 1e-6:
            raise ValueError(
                f"标的 {self.symbol} 各档位金额合计 {tier_sum} 超过单标的预算上限 {self.budget_cny}"
            )
        drawdowns = [t.drawdown_pct for t in self.tiers]
        if len(set(drawdowns)) != len(drawdowns):
            raise ValueError(f"标的 {self.symbol} 存在重复的回撤档位: {drawdowns}")
        self.tiers = sorted(self.tiers, key=lambda t: t.drawdown_pct, reverse=True)
        return self


class IndexMonitorConfig(BaseModel):
    total_budget_cny: float = Field(gt=0)
    lookback_days: int = Field(ge=20, default=120)
    reset_drawdown_pct: float = Field(le=0, default=-2.0)
    cooldown_trading_days: int = Field(ge=0, default=5)
    correlation_groups: Dict[str, float] = Field(default_factory=dict)
    targets: List[IndexTargetConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_budget_hierarchy(self) -> IndexMonitorConfig:
        group_sum = sum(self.correlation_groups.values())
        if group_sum > self.total_budget_cny + 1e-6:
            raise ValueError(
                f"相关性组预算合计 {group_sum} 超过指数舱总预算 {self.total_budget_cny}"
            )
        for target in self.targets:
            if target.correlation_group not in self.correlation_groups:
                raise ValueError(
                    f"标的 {target.symbol} 的相关性组 '{target.correlation_group}' 未在 correlation_groups 中定义"
                )
            group_limit = self.correlation_groups[target.correlation_group]
            if target.budget_cny > group_limit + 1e-6:
                raise ValueError(
                    f"标的 {target.symbol} 预算 {target.budget_cny} 超过所属组 '{target.correlation_group}' 上限 {group_limit}"
                )
        return self


class OnExchangeETFConfig(BaseModel):
    code: str
    name: str


class QDIIProxyItemConfig(BaseModel):
    fund_code: str
    holdings_code: str
    name: str
    company: str
    is_passive: bool = False


class QDIIRouterConfig(BaseModel):
    benchmark_symbol: str = "QQQ"
    min_us_developed_top10_pct: float = Field(ge=0, le=100, default=65.0)
    max_cn_hk_top10_pct: float = Field(ge=0, le=100, default=20.0)
    min_corr_with_benchmark: float = Field(ge=-1.0, le=1.0, default=0.65)
    max_etf_premium_pct: float = Field(ge=0, default=2.0)
    forbidden_name_keywords: List[str] = Field(
        default_factory=lambda: ["持有期", "定开", "封闭", "美元", "港元"]
    )
    on_exchange_etfs: List[OnExchangeETFConfig] = Field(default_factory=list)
    proxy_pool: List[QDIIProxyItemConfig] = Field(default_factory=list)


class CBScreenerConfig(BaseModel):
    total_budget_cny: float = Field(gt=0, default=3000.0)
    reserved_ipo_cash_cny: float = Field(ge=0, default=1000.0)
    min_order_amount_cny: float = Field(ge=0, default=2000.0)
    min_price: float = Field(gt=0, default=96.0)
    max_price: float = Field(gt=0, default=108.0)
    max_premium_rate_pct: float = Field(default=45.0)
    min_ytm_pct: float = Field(default=0.0)
    min_remaining_years: float = Field(ge=0, default=0.8)
    max_remaining_years: float = Field(gt=0, default=2.5)
    min_stock_price_cny: float = Field(gt=0, default=2.0)
    min_credit_rating: str = Field(default="A+")
    exclude_st: bool = True
    exclude_redeem_announced: bool = True
    top_k: int = Field(ge=1, le=20, default=5)
    notice_lookback_days: int = Field(ge=7, default=90)
    fetch_detail_keywords: List[str] = Field(default_factory=list)
    notice_keywords: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_bounds(self) -> CBScreenerConfig:
        if self.min_price >= self.max_price:
            raise ValueError(f"min_price ({self.min_price}) 必须小于 max_price ({self.max_price})")
        if self.min_remaining_years >= self.max_remaining_years:
            raise ValueError(
                f"min_remaining_years ({self.min_remaining_years}) 必须小于 max_remaining_years ({self.max_remaining_years})"
            )
        if self.min_credit_rating.strip().upper() not in CREDIT_RATING_RANK:
            raise ValueError(f"不支持的最低信用评级: {self.min_credit_rating}")
        return self


class PositionMonitorConfig(BaseModel):
    cb_take_profit_price: float = Field(gt=100.0, default=128.0)
    cb_stop_review_price: float = Field(gt=0, default=92.0)
    cb_redeem_alert_days_remaining: int = Field(ge=1, default=5)
    cb_putback_window_alert: bool = True
    index_take_profit_pct: float = Field(gt=0, default=25.0)
    index_c_class_max_days: int = Field(ge=30, default=330)


class EvidenceBudgetConfig(BaseModel):
    max_notices_per_target: int = Field(ge=1, default=8)
    max_detail_chars_per_notice: int = Field(ge=50, default=400)
    max_news_per_target: int = Field(ge=1, default=6)
    max_chars_per_bundle: int = Field(ge=500, default=3200)


class RadarConfig(BaseModel):
    index_monitor: IndexMonitorConfig
    qdii_router: QDIIRouterConfig = Field(default_factory=QDIIRouterConfig)
    cb_screener: CBScreenerConfig
    position_monitor: PositionMonitorConfig = Field(default_factory=PositionMonitorConfig)
    evidence_budget: EvidenceBudgetConfig = Field(default_factory=EvidenceBudgetConfig)


class EnvSecrets(BaseModel):
    webhook_url: str = ""
    jisilu_cookie: str = ""


class AppConfig(BaseModel):
    radar: RadarConfig
    secrets: EnvSecrets
    project_root: Path
    data_dir: Path

    @property
    def state_path(self) -> Path:
        return self.data_dir / "state.json"

    @property
    def portfolio_path(self) -> Path:
        return self.data_dir / "portfolio.json"

    @property
    def audits_dir(self) -> Path:
        return self.data_dir / "audits"

    @property
    def last_scan_path(self) -> Path:
        return self.data_dir / "last_scan.json"


def load_config(
    config_path: Path | str = Path("config/radar.yaml"),
    env_path: Optional[Path | str] = Path(".env"),
    data_dir: Optional[Path | str] = None,
) -> AppConfig:
    """加载并严格校验 YAML 配置与可选 .env 环境变量（零 LLM API Key）。"""
    cfg_file = Path(config_path).resolve()
    if not cfg_file.exists():
        raise ConfigValidationError(f"配置文件不存在: {cfg_file}")

    try:
        raw = yaml.safe_load(cfg_file.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ConfigValidationError(f"解析 YAML 配置文件失败: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigValidationError("配置文件根节点必须是 YAML 映射对象")

    try:
        radar = RadarConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigValidationError(f"配置文件校验失败:\n{exc}") from exc

    if env_path is not None:
        env_file = Path(env_path)
        if env_file.exists():
            load_dotenv(env_file, override=False)

    secrets = EnvSecrets(
        webhook_url=os.getenv("WEBHOOK_URL", "").strip(),
        jisilu_cookie=os.getenv("JISILU_COOKIE", "").strip(),
    )

    project_root = cfg_file.parent.parent if cfg_file.parent.name == "config" else cfg_file.parent
    resolved_data_dir = Path(data_dir).resolve() if data_dir is not None else (project_root / "data")

    return AppConfig(
        radar=radar,
        secrets=secrets,
        project_root=project_root,
        data_dir=resolved_data_dir,
    )


def load_portfolio(
    portfolio_path: Path | str,
    default_date: Optional[date] = None,
) -> PortfolioSnapshot:
    """加载并校验持仓快照；若文件不存在，返回空仓快照。"""
    path = Path(portfolio_path)
    if not path.exists():
        return PortfolioSnapshot(updated_at=default_date or date.today())

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return PortfolioSnapshot.model_validate(raw)
    except Exception as exc:
        raise ConfigValidationError(f"持仓快照 {path} 解析或校验失败: {exc}") from exc
