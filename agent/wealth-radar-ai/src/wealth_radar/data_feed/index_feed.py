"""指数/ETF 历史行情与近期新闻数据源（yfinance + akshare/新浪自动降级，防国内直连与 push2 限流）。"""

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


def _to_sina_etf_symbol(symbol: str) -> str:
    """将纯数字 ETF 代码转换为新浪接口所需的前缀代码（如 518880 -> sh518880, 159941 -> sz159941）。"""
    clean = symbol.strip().lower()
    if clean.startswith(("sh", "sz")):
        return clean
    if clean.startswith(("5", "6")):
        return f"sh{clean}"
    return f"sz{clean}"


class LiveIndexFeed:
    """结合新浪/akshare 与 yfinance 的高可用指数/ETF 行情与新闻提供器。"""

    def fetch_index_history(
        self,
        symbol: str,
        source: str,
        market_timezone: MarketTimezone,
        lookback_days: int,
    ) -> IndexQuoteSeries:
        if source == "yfinance":
            try:
                return self._fetch_yfinance_history(symbol, market_timezone, lookback_days)
            except Exception as yf_exc:
                # 国内网络直连 Yahoo Finance 经常 SSL 断开或被限流，自动降级到新浪美股日线
                try:
                    return self._fetch_sina_us_history(
                        symbol=symbol,
                        market_timezone=market_timezone,
                        lookback_days=lookback_days,
                        fallback_note="Sina US fallback",
                    )
                except Exception as sina_exc:
                    raise DataFeedError(
                        f"yfinance 拉取 {symbol} 失败 ({yf_exc})，且新浪美股降级源亦失败 ({sina_exc})"
                    ) from sina_exc

        if source == "akshare_us":
            return self._fetch_sina_us_history(
                symbol=symbol,
                market_timezone=market_timezone,
                lookback_days=lookback_days,
            )

        if source == "akshare":
            # 优先使用新浪 ETF 历史日线（规避东方财富 push2 高频封 IP），失败再回退东财
            try:
                return self._fetch_sina_etf_history(symbol, market_timezone, lookback_days)
            except Exception as sina_exc:
                try:
                    return self._fetch_akshare_em_etf_history(symbol, market_timezone, lookback_days)
                except Exception as em_exc:
                    raise DataFeedError(
                        f"拉取 ETF {symbol} 历史行情失败（新浪: {sina_exc}；东财: {em_exc}）"
                    ) from em_exc

        raise DataFeedError(f"不支持的指数数据源: {source}")

    def fetch_latest_index_price(self, symbol: str, source: str) -> Optional[float]:
        try:
            tz: MarketTimezone = "US" if source in {"yfinance", "akshare_us"} else "CN"
            series = self.fetch_index_history(
                symbol=symbol,
                source=source,
                market_timezone=tz,
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
            try:
                items = self._fetch_yfinance_news(symbol, max_items)
                if items:
                    return items
            except Exception:
                pass
            return self._fetch_cls_global_news(symbol, max_items)

        if source == "akshare_us":
            return self._fetch_cls_global_news(symbol, max_items)

        if source == "akshare":
            try:
                items = self._fetch_akshare_news(symbol, max_items)
                if items:
                    return items
            except Exception:
                pass
            return self._fetch_cls_global_news(symbol, max_items)

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

    def _fetch_sina_us_history(
        self,
        symbol: str,
        market_timezone: MarketTimezone,
        lookback_days: int,
        fallback_note: str = "",
    ) -> IndexQuoteSeries:
        ak = _import_akshare()
        try:
            if symbol.startswith("."):
                df = ak.index_us_daily_sina(symbol=symbol)
            else:
                try:
                    df = ak.stock_us_hist_sina(symbol=symbol, adjust="qfq")
                except Exception:
                    df = ak.stock_us_hist_sina(symbol=symbol, adjust="")
        except Exception as exc:
            raise DataFeedError(f"新浪美股拉取 {symbol} 历史行情失败: {exc}") from exc

        if df is None or getattr(df, "empty", True):
            raise DataFeedError(f"新浪美股返回 {symbol} 历史行情为空")

        bars: List[PriceBar] = []
        for _, row in df.tail(lookback_days + 20).iterrows():
            raw_date = row.get("date")
            raw_close = row.get("close")
            if raw_date is None or raw_close is None or raw_close != raw_close:
                continue
            close_f = float(raw_close)
            if close_f <= 0:
                continue
            bar_date = (
                raw_date.date()
                if hasattr(raw_date, "date")
                else date.fromisoformat(str(raw_date)[:10])
            )
            bars.append(PriceBar(trade_date=bar_date, close=round(close_f, 4)))

        if not bars:
            raise DataFeedError(f"新浪美股 {symbol} 无有效收盘价数据")

        bars.sort(key=lambda b: b.trade_date)
        latest_day = bars[-1].trade_date.isoformat()
        note_prefix = f"[{fallback_note}] " if fallback_note else ""
        as_of = (
            f"{note_prefix}{latest_day} US Close (T-1 美股收盘滞后，15:00前申购场外QDII按今晚净值成交，请核对基金限购)"
            if market_timezone == "US"
            else f"{note_prefix}{latest_day} Close"
        )
        return IndexQuoteSeries(
            symbol=symbol,
            source="akshare_us",
            market_timezone=market_timezone,
            bars=bars[-lookback_days:],
            data_as_of=as_of,
        )

    def _fetch_sina_etf_history(
        self,
        symbol: str,
        market_timezone: MarketTimezone,
        lookback_days: int,
    ) -> IndexQuoteSeries:
        ak = _import_akshare()
        sina_symbol = _to_sina_etf_symbol(symbol)
        try:
            df = ak.fund_etf_hist_sina(symbol=sina_symbol)
        except Exception as exc:
            raise DataFeedError(f"新浪拉取 ETF {sina_symbol} 历史行情失败: {exc}") from exc

        if df is None or getattr(df, "empty", True):
            raise DataFeedError(f"新浪返回 ETF {sina_symbol} 历史行情为空")

        bars: List[PriceBar] = []
        for _, row in df.tail(lookback_days + 20).iterrows():
            raw_date = row.get("date")
            raw_close = row.get("close")
            if raw_date is None or raw_close is None or raw_close != raw_close:
                continue
            close_f = float(raw_close)
            if close_f <= 0:
                continue
            bar_date = (
                raw_date.date()
                if hasattr(raw_date, "date")
                else date.fromisoformat(str(raw_date)[:10])
            )
            bars.append(PriceBar(trade_date=bar_date, close=round(close_f, 4)))

        if not bars:
            raise DataFeedError(f"新浪 ETF {sina_symbol} 无有效收盘价数据")

        bars.sort(key=lambda b: b.trade_date)
        latest_day = bars[-1].trade_date.isoformat()
        return IndexQuoteSeries(
            symbol=symbol,
            source="akshare",
            market_timezone=market_timezone,
            bars=bars[-lookback_days:],
            data_as_of=f"{latest_day} Close (Sina ETF)",
        )

    def _fetch_akshare_em_etf_history(
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

    def _fetch_cls_global_news(self, symbol: str, max_items: int) -> List[NoticeItem]:
        """财联社全球财经电报降级源（国内直连稳定，按标的主题关键词优先筛选）。"""
        ak = _import_akshare()
        try:
            df = ak.stock_news_global_cls(symbol="全部")
        except Exception as exc:
            raise DataFeedError(f"财联社电报拉取失败: {exc}") from exc

        if df is None or getattr(df, "empty", True):
            return []

        topic_keywords = _topic_keywords_for_symbol(symbol)
        matched_items: List[NoticeItem] = []
        general_items: List[NoticeItem] = []

        for _, row in df.iterrows():
            title = str(row.get("标题") or "").strip()
            content = str(row.get("内容") or "").strip()
            if not title and content:
                title = content[:48]
            if not title:
                continue
            pub_date = _parse_news_date(row.get("发布日期"))
            item = NoticeItem(
                pub_date=pub_date,
                title=title,
                snippet=content,
                detail_fetched=bool(content),
            )
            combined = f"{title} {content}"
            if topic_keywords and any(kw in combined for kw in topic_keywords):
                matched_items.append(item)
            else:
                general_items.append(item)

        ordered = matched_items + general_items
        return ordered[:max_items]


def _topic_keywords_for_symbol(symbol: str) -> tuple[str, ...]:
    upper = symbol.upper()
    if upper in {"QQQ", ".NDX", ".IXIC", "513100", "159941"}:
        return ("纳指", "纳斯达克", "美股", "美联储", "美债", "科技", "AI", "英伟达", "苹果", "微软")
    if upper in {"SOXX", "SMH"}:
        return ("半导体", "芯片", "英伟达", "台积电", "费城", "美股")
    if upper in {"518880", "518800", "159934", "GLD"}:
        return ("黄金", "金价", "贵金属", "避险", "美元", "美联储", "央行购金", "通胀")
    return ()


def _parse_news_date(raw: Any) -> date:
    if raw is None:
        return date.today()
    if isinstance(raw, date) and not isinstance(raw, datetime):
        return raw
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, (int, float)):
        return datetime.fromtimestamp(float(raw), tz=timezone.utc).date()
    text = str(raw).strip()
    if len(text) >= 10:
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            pass
    return date.today()
