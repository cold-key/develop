"""场外 QDII 申购限额、季报前十大持仓、120日净值与场内 ETF 实时净值数据源（akshare）。"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Sequence

from wealth_radar.core.qdii_router import classify_stock_holding
from wealth_radar.domain.errors import DataFeedError, MissingDependencyError
from wealth_radar.domain.models import PriceBar, QDIIHoldingItem, QDIIPurchaseInfo


def _import_akshare() -> Any:
    try:
        import akshare as ak
    except ImportError as exc:
        raise MissingDependencyError(
            "未安装 akshare，请执行 `uv sync` 或 `pip install akshare`"
        ) from exc
    return ak


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if value != value:
            return None
        return float(value)
    text = str(value).strip().replace("%", "").replace(",", "")
    if not text or text in {"-", "--", "nan", "None", "NaT"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _parse_date_safe(value: Any) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    text = str(value).strip()[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


class LiveQDIIFeed:
    """基于天天基金与同花顺免费接口（不触碰东财 push2）的 QDII 实时体检数据源。"""

    def __init__(self) -> None:
        self._purchase_df_cache: Optional[Any] = None
        self._etf_nav_cache: Optional[Dict[str, float]] = None

    def fetch_purchase_info_map(self, fund_codes: Sequence[str]) -> Dict[str, QDIIPurchaseInfo]:
        ak = _import_akshare()
        wanted = {c.strip() for c in fund_codes if c.strip()}
        if not wanted:
            return {}

        if self._purchase_df_cache is None:
            try:
                self._purchase_df_cache = ak.fund_purchase_em()
            except Exception as exc:
                raise DataFeedError(f"拉取天天基金申购状态表(fund_purchase_em)失败: {exc}") from exc

        df = self._purchase_df_cache
        if df is None or getattr(df, "empty", True):
            return {}

        result: Dict[str, QDIIPurchaseInfo] = {}
        matched = df[df["基金代码"].astype(str).isin(wanted)]
        for _, row in matched.iterrows():
            code = str(row.get("基金代码", "")).strip()
            raw_limit = _to_float(row.get("日累计限定金额"))
            # 天天基金将“不限额”表示为 1e11（1000亿）
            daily_limit = None if (raw_limit is not None and raw_limit >= 1e9) else raw_limit
            result[code] = QDIIPurchaseInfo(
                fund_code=code,
                fund_name=str(row.get("基金简称", "")).strip(),
                purchase_status=str(row.get("申购状态", "")).strip() or "UNKNOWN",
                daily_limit_cny=daily_limit,
                fee_rate_pct=_to_float(row.get("手续费")),
                nav=_to_float(row.get("最新净值/万份收益")),
                nav_date=str(row.get("最新净值/万份收益-报告时间", "")).strip(),
            )
        return result

    def fetch_quarterly_holdings(
        self, holdings_code: str, year: int
    ) -> List[QDIIHoldingItem]:
        ak = _import_akshare()
        df = None
        for query_year in (year, year - 1):
            try:
                candidate = ak.fund_portfolio_hold_em(symbol=holdings_code, date=str(query_year))
                if candidate is not None and not getattr(candidate, "empty", True):
                    df = candidate
                    break
            except Exception:
                continue

        if df is None or getattr(df, "empty", True):
            return []

        items: List[QDIIHoldingItem] = []
        for _, row in df.iterrows():
            stock_code = str(row.get("股票代码", "")).strip()
            stock_name = str(row.get("股票名称", "")).strip()
            weight = _to_float(row.get("占净值比例"))
            quarter = str(row.get("季度", "")).strip()
            if not stock_code or weight is None or weight < 0:
                continue
            region, is_mega = classify_stock_holding(stock_code, stock_name)
            items.append(
                QDIIHoldingItem(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    weight_pct=round(weight, 2),
                    quarter=quarter,
                    region=region,
                    is_mega_cap_tech=is_mega,
                )
            )
        return items

    def fetch_fund_nav_series(self, fund_code: str, lookback_days: int) -> List[PriceBar]:
        ak = _import_akshare()
        try:
            df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        except Exception as exc:
            raise DataFeedError(f"拉取基金 {fund_code} 单位净值走势失败: {exc}") from exc

        if df is None or getattr(df, "empty", True):
            return []

        bars: List[PriceBar] = []
        for _, row in df.tail(lookback_days + 20).iterrows():
            dt = _parse_date_safe(row.get("净值日期"))
            nav = _to_float(row.get("单位净值"))
            if dt is None or nav is None or nav <= 0:
                continue
            bars.append(PriceBar(trade_date=dt, close=round(nav, 4)))

        bars.sort(key=lambda b: b.trade_date)
        return bars[-lookback_days:]

    def fetch_etf_latest_nav_map(self, etf_codes: Sequence[str]) -> Dict[str, float]:
        ak = _import_akshare()
        wanted = {c.strip() for c in etf_codes if c.strip()}
        if not wanted:
            return {}

        if self._etf_nav_cache is None:
            try:
                df = ak.fund_etf_spot_ths()
            except Exception as exc:
                raise DataFeedError(f"拉取同花顺 ETF 净值表(fund_etf_spot_ths)失败: {exc}") from exc

            cache: Dict[str, float] = {}
            if df is not None and not getattr(df, "empty", True):
                for _, row in df.iterrows():
                    code = str(row.get("基金代码", "")).strip()
                    nav = _to_float(row.get("最新-单位净值")) or _to_float(row.get("当前-单位净值"))
                    if code and nav is not None and nav > 0:
                        cache[code] = round(nav, 4)
            self._etf_nav_cache = cache

        return {code: self._etf_nav_cache[code] for code in wanted if code in self._etf_nav_cache}
