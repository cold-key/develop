"""指数/ETF 历史行情与近期新闻数据源（yfinance + akshare，懒加载可选依赖）。"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any, List, Optional

from wealth_radar.domain.errors import DataFeedError, MissingDependencyError
from wealth_radar.domain.models import IndexQuoteSeries, MarketTimezone, NoticeItem, PriceBar


def _import_yfinance() -> Any:
    try:
        import yfinance as yf
    except ImportError as exc:
        raise MissingDependencyError(
            "未安装 yfinance，请执行 `uv sync` 或 `pip install yfinance`"
        ) from exc
    return yf


def _import_akshare() -> Any:
    try:
        import akshare as ak
    except ImportError as exc:
        raise MissingDependencyError(
            "未安装 akshare，请执行 `uv sync` 或 `pip install akshare`"
        ) from exc
    return ak


class LiveIndexFeed:
    """结合 yfinance（美股 ETF/指数）与 akshare（国内场内 ETF）的行情与新闻提供器。"""

    def fetch_index_history(
        self,
        symbol: str,
        source: str,
        market_timezone: MarketTimezone,
        lookback_days: int,
    ) -> IndexQuoteSeries:
        if source == "yfinance":
            return self._fetch_yfinance_history(symbol, market_timezone, lookback_days)
        if source == "akshare":
            return self._fetch_akshare_etf_history(symbol, market_timezone, lookback_days)
        raise DataFeedError(f"不支持的指数数据源: {source}")

    def fetch_latest_index_price(self, symbol: str, source: str) -> Optional[float]:
        try:
            series = self.fetch_index_history(
                symbol=symbol,
                source=source,
                market_timezone="US" if source == "yfinance" else "CN",
                lookback_days=20,
            )
            return series.bars[-1].close if series.bars else None
        except Exception:
            return None

    def fetch_index_news(
        self,
        symbol: str,
        source: str,
        max_items: int,
    ) -> List[NoticeItem]:
        if source == "yfinance":
            return self._fetch_yfinance_news(symbol, max_items)
        if source == "akshare":
            return self._fetch_akshare_news(symbol, max_items)
        return []

    def _fetch_yfinance_history(
        self,
        symbol: str,
        market_timezone: MarketTimezone,
        lookback_days: int,
    ) -> IndexQuoteSeries:
        yf = _import_yfinance()
        calendar_days = int(lookback_days * 1.6) + 15
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=f"{calendar_days}d", auto_adjust=False)
        except Exception as exc:
            raise DataFeedError(f"yfinance 拉取 {symbol} 历史行情失败: {exc}") from exc

        if df is None or getattr(df, "empty", True):
            raise DataFeedError(f"yfinance 返回 {symbol} 历史行情为空")

        bars: List[PriceBar] = []
        for idx, row in df.iterrows():
            close_val = row.get("Close")
            if close_val is None or close_val != close_val or float(close_val) <= 0:
                continue
            bar_date = idx.date() if hasattr(idx, "date") else date.fromisoformat(str(idx)[:10])
            bars.append(PriceBar(trade_date=bar_date, close=round(float(close_val), 4)))

        if not bars:
            raise DataFeedError(f"yfinance {symbol} 无有效收盘价数据")

        bars.sort(key=lambda b: b.trade_date)
        latest_day = bars[-1].trade_date.isoformat()
        as_of = (
            f"{latest_day} US Close (T-1 美股收盘滞后，15:00前申购场外QDII按今晚净值成交，请核对基金限购)"
            if market_timezone == "US"
            else f"{latest_day} Close"
        )
        return IndexQuoteSeries(
            symbol=symbol,
            source="yfinance",
            market_timezone=market_timezone,
            bars=bars[-lookback_days:],
            data_as_of=as_of,
        )

    def _fetch_akshare_etf_history(
        self,
        symbol: str,
        market_timezone: MarketTimezone,
        lookback_days: int,
    ) -> IndexQuoteSeries:
        ak = _import_akshare()
        end_dt = date.today()
        start_dt = end_dt - timedelta(days=int(lookback_days * 1.7) + 20)
        try:
            df = ak.fund_etf_hist_em(
                symbol=symbol,
                period="daily",
                start_date=start_dt.strftime("%Y%m%d"),
                end_date=end_dt.strftime("%Y%m%d"),
                adjust="qfq",
            )
        except Exception as exc:
            raise DataFeedError(f"akshare 拉取 ETF {symbol} 历史行情失败: {exc}") from exc

        if df is None or getattr(df, "empty", True):
            raise DataFeedError(f"akshare 返回 ETF {symbol} 历史行情为空")

        bars: List[PriceBar] = []
        for _, row in df.iterrows():
            raw_date = str(row.get("日期", ""))[:10]
            raw_close = row.get("收盘")
            if not raw_date or raw_close is None or raw_close != raw_close:
                continue
            close_f = float(raw_close)
            if close_f <= 0:
                continue
            bars.append(PriceBar(trade_date=date.fromisoformat(raw_date), close=round(close_f, 4)))

        if not bars:
            raise DataFeedError(f"akshare ETF {symbol} 无有效收盘价数据")

        bars.sort(key=lambda b: b.trade_date)
        latest_day = bars[-1].trade_date.isoformat()
        return IndexQuoteSeries(
            symbol=symbol,
            source="akshare",
            market_timezone=market_timezone,
            bars=bars[-lookback_days:],
            data_as_of=f"{latest_day} 14:30 CST",
        )

    def _fetch_yfinance_news(self, symbol: str, max_items: int) -> List[NoticeItem]:
        yf = _import_yfinance()
        try:
            raw_news = yf.Ticker(symbol).news or []
        except Exception as exc:
            raise DataFeedError(f"yfinance 拉取 {symbol} 新闻失败: {exc}") from exc

        items: List[NoticeItem] = []
        for entry in raw_news[: max_items * 2]:
            content = entry.get("content", entry) if isinstance(entry, dict) else {}
            title = str(content.get("title") or "").strip()
            if not title:
                continue
            snippet = str(content.get("summary") or content.get("description") or "").strip()
            pub_date = _parse_news_date(
                content.get("pubDate") or entry.get("providerPublishTime")
            )
            items.append(
                NoticeItem(
                    pub_date=pub_date,
                    title=title,
                    snippet=snippet,
                    detail_fetched=bool(snippet),
                )
            )
            if len(items) >= max_items:
                break
        return items

    def _fetch_akshare_news(self, symbol: str, max_items: int) -> List[NoticeItem]:
        ak = _import_akshare()
        try:
            df = ak.stock_news_em(symbol=symbol)
        except Exception as exc:
            raise DataFeedError(f"akshare 拉取 {symbol} 新闻失败: {exc}") from exc

        if df is None or getattr(df, "empty", True):
            return []

        items: List[NoticeItem] = []
        for _, row in df.head(max_items).iterrows():
            title = str(row.get("新闻标题", "")).strip()
            if not title:
                continue
            snippet = str(row.get("新闻内容", "")).strip()
            pub_date = _parse_news_date(row.get("发布时间"))
            items.append(
                NoticeItem(
                    pub_date=pub_date,
                    title=title,
                    snippet=snippet,
                    detail_fetched=bool(snippet),
                )
            )
        return items


def _parse_news_date(raw: Any) -> date:
    if raw is None:
        return date.today()
    if isinstance(raw, (int, float)):
        return datetime.fromtimestamp(float(raw), tz=timezone.utc).date()
    text = str(raw).strip()
    if len(text) >= 10:
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            pass
    return date.today()
