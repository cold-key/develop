"""行情、新闻、可转债与 QDII 平替数据源协议（支持 100% 离线 Mock 注入）。"""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional, Protocol, Sequence

from wealth_radar.domain.models import (
    CBIpoItem,
    CBMarketRow,
    IndexQuoteSeries,
    MarketTimezone,
    NoticeItem,
    PriceBar,
    QDIIHoldingItem,
    QDIIPurchaseInfo,
)


class MarketProvider(Protocol):
    """指数/ETF 历史行情与最新价格提供协议。"""

    def fetch_index_history(
        self,
        symbol: str,
        source: str,
        market_timezone: MarketTimezone,
        lookback_days: int,
    ) -> IndexQuoteSeries: ...

    def fetch_latest_index_price(self, symbol: str, source: str) -> Optional[float]: ...


class NewsProvider(Protocol):
    """指数/标的近期新闻提供协议。"""

    def fetch_index_news(
        self,
        symbol: str,
        source: str,
        max_items: int,
    ) -> List[NoticeItem]: ...


class CBProvider(Protocol):
    """可转债打新、全市场行情与正股公告提供协议。"""

    def fetch_cb_ipos(self, trade_date: date) -> List[CBIpoItem]: ...

    def fetch_cb_market_rows(self) -> List[CBMarketRow]: ...

    def fetch_stock_notices(
        self,
        stock_code: str,
        lookback_days: int,
        fetch_detail_keywords: Sequence[str],
        max_detail_chars: int,
        as_of_date: date,
    ) -> List[NoticeItem]: ...

    def fetch_latest_cb_price(self, bond_code: str) -> Optional[float]: ...


class QDIIProvider(Protocol):
    """场外 QDII 申购限额、季报持仓、历史净值与场内 ETF 净值提供协议。"""

    def fetch_purchase_info_map(self, fund_codes: Sequence[str]) -> Dict[str, QDIIPurchaseInfo]: ...

    def fetch_quarterly_holdings(
        self, holdings_code: str, year: int
    ) -> List[QDIIHoldingItem]: ...

    def fetch_fund_nav_series(self, fund_code: str, lookback_days: int) -> List[PriceBar]: ...

    def fetch_etf_latest_nav_map(self, etf_codes: Sequence[str]) -> Dict[str, float]: ...
