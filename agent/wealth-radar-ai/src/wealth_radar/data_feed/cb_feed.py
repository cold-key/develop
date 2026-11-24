"""可转债打新、全市场行情（含强赎/评级/YTM）与正股近90天公告数据源（akshare + httpx）。"""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Sequence

import httpx

from wealth_radar.domain.errors import DataFeedError, MissingDependencyError
from wealth_radar.domain.models import CBIpoItem, CBMarketRow, NoticeItem


def _import_akshare() -> Any:
    try:
        import akshare as ak
    except ImportError as exc:
        raise MissingDependencyError(
            "未安装 akshare，请执行 `uv sync` 或 `pip install akshare`"
        ) from exc
    return ak


def _to_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        if value != value:  # NaN
            return default
        return float(value)
    text = str(value).strip().replace("%", "").replace(",", "")
    if not text or text in {"-", "--", "nan", "None"}:
        return default
    try:
        return float(text)
    except ValueError:
        return default


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


def _parse_redeem_days(redeem_text: str) -> tuple[bool, Optional[int]]:
    """解析强赎状态文本（例如 '已公告强赎' 或 '12/15'）。"""
    text = redeem_text.strip()
    if not text or text in {"-", "--"}:
        return False, None
    if "已公告强赎" in text or "强赎" in text and "不强赎" not in text and "/" not in text:
        return True, 0
    match = re.search(r"(\d+)\s*/\s*(\d+)", text)
    if match:
        done = int(match.group(1))
        total = int(match.group(2))
        return False, max(0, total - done)
    return False, None


class LiveCBFeed:
    """基于 akshare 的可转债全市场数据与正股公告提供器（支持高危公告正文片段抓取）。"""

    def __init__(self, http_timeout_sec: float = 8.0) -> None:
        self._http_timeout_sec = http_timeout_sec
        self._market_cache: Optional[Dict[str, CBMarketRow]] = None

    def fetch_cb_ipos(self, trade_date: date) -> List[CBIpoItem]:
        ak = _import_akshare()
        try:
            df = ak.bond_zh_cov()
        except Exception as exc:
            raise DataFeedError(f"akshare 拉取可转债打新列表失败: {exc}") from exc

        if df is None or getattr(df, "empty", True):
            return []

        items: List[CBIpoItem] = []
        for _, row in df.iterrows():
            sub_date = _parse_date_safe(row.get("申购日期"))
            if sub_date != trade_date:
                continue
            bond_code = str(row.get("债券代码", "")).strip()
            bond_name = str(row.get("债券简称", "")).strip()
            if not bond_code or not bond_name:
                continue
            items.append(
                CBIpoItem(
                    bond_code=bond_code,
                    bond_name=bond_name,
                    subscribe_date=sub_date,
                    credit_rating=str(row.get("信用评级", "")).strip(),
                    issue_scale_billion=_to_float(row.get("发行规模")),
                )
            )
        return items

    def fetch_cb_market_rows(self) -> List[CBMarketRow]:
        ak = _import_akshare()
        try:
            df = ak.bond_cb_jsl()
        except Exception as exc:
            raise DataFeedError(f"akshare 拉取可转债全市场行情(bond_cb_jsl)失败: {exc}") from exc

        if df is None or getattr(df, "empty", True):
            raise DataFeedError("akshare 返回可转债全市场行情为空")

        rows: List[CBMarketRow] = []
        for _, rec in df.iterrows():
            bond_code = str(rec.get("代码", "")).strip()
            bond_name = str(rec.get("转债名称", "")).strip()
            stock_code = str(rec.get("正股代码", "")).strip()
            stock_name = str(rec.get("正股名称", "")).strip()
            price = _to_float(rec.get("现价"))
            premium = _to_float(rec.get("转股溢价率"))
            ytm = _to_float(rec.get("到期税前收益"), default=-99.0)
            rem_years = _to_float(rec.get("剩余年限"))
            stock_price = _to_float(rec.get("正股价"))
            rating = str(rec.get("评级", "")).strip()

            if (
                not bond_code
                or not bond_name
                or price is None
                or price <= 0
                or premium is None
                or rem_years is None
                or stock_price is None
                or stock_price <= 0
            ):
                continue

            redeem_status = str(rec.get("强赎状态", "") or rec.get("强赎", "")).strip()
            redeem_announced, redeem_days_rem = _parse_redeem_days(redeem_status)
            putback_text = str(rec.get("回售状态", "") or "").strip()

            rows.append(
                CBMarketRow(
                    bond_code=bond_code,
                    bond_name=bond_name,
                    stock_code=stock_code,
                    stock_name=stock_name,
                    price=round(price, 3),
                    premium_rate_pct=round(premium, 2),
                    ytm_pct=round(ytm if ytm is not None else -99.0, 2),
                    remaining_years=round(rem_years, 2),
                    stock_price=round(stock_price, 2),
                    credit_rating=rating,
                    is_st=("ST" in stock_name.upper() or "ST" in bond_name.upper()),
                    redeem_announced=redeem_announced,
                    redeem_days_remaining=redeem_days_rem,
                    putback_triggered=("回售" in putback_text and "未" not in putback_text),
                    putback_register_active=("登记" in putback_text),
                )
            )

        self._market_cache = {row.bond_code: row for row in rows}
        return rows

    def fetch_stock_notices(
        self,
        stock_code: str,
        lookback_days: int,
        fetch_detail_keywords: Sequence[str],
        max_detail_chars: int,
        as_of_date: date,
    ) -> List[NoticeItem]:
        """抓取正股近 lookback_days 天公告；命中高危关键词时尝试获取正文摘要。"""
        ak = _import_akshare()
        cutoff_date = as_of_date - timedelta(days=lookback_days)
        pure_code = re.sub(r"\D", "", stock_code)
        if not pure_code:
            return []

        try:
            df = ak.stock_notice_report(symbol="全部", date=as_of_date.strftime("%Y%m%d"))
        except Exception:
            df = None

        # 优先使用东方财富个股公告接口（支持完整回溯 90 天）
        raw_items = self._fetch_eastmoney_stock_notices(pure_code, cutoff_date, as_of_date)
        if not raw_items and df is not None and not getattr(df, "empty", True):
            for _, row in df.iterrows():
                if str(row.get("代码", "")).strip() != pure_code:
                    continue
                pub_d = _parse_date_safe(row.get("公告日期"))
                title = str(row.get("公告标题", "")).strip()
                if pub_d is None or pub_d < cutoff_date or not title:
                    continue
                raw_items.append({"pub_date": pub_d, "title": title, "art_code": ""})

        notices: List[NoticeItem] = []
        for entry in raw_items:
            title = str(entry["title"])
            entry_date: date = entry["pub_date"]
            art_code = str(entry.get("art_code", ""))
            snippet = ""
            detail_fetched = False

            if art_code and any(kw in title for kw in fetch_detail_keywords):
                fetched_text = self._fetch_notice_detail_snippet(art_code, max_detail_chars)
                if fetched_text:
                    snippet = fetched_text
                    detail_fetched = True

            notices.append(
                NoticeItem(
                    pub_date=entry_date,
                    title=title,
                    snippet=snippet,
                    detail_fetched=detail_fetched,
                )
            )
        return notices

    def fetch_latest_cb_price(self, bond_code: str) -> Optional[float]:
        if self._market_cache is None:
            try:
                self.fetch_cb_market_rows()
            except Exception:
                return None
        if self._market_cache and bond_code in self._market_cache:
            return self._market_cache[bond_code].price
        return None

    def _fetch_eastmoney_stock_notices(
        self,
        stock_code: str,
        cutoff_date: date,
        as_of_date: date,
    ) -> List[Dict[str, Any]]:
        url = "https://np-anotice-stock.eastmoney.com/api/security/ann"
        params = {
            "sr": "-1",
            "page_size": "50",
            "page_index": "1",
            "ann_type": "A",
            "stock_list": stock_code,
            "f_node": "0",
            "s_node": "0",
        }
        try:
            with httpx.Client(timeout=self._http_timeout_sec) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                payload = resp.json()
        except Exception as exc:
            raise DataFeedError(f"抓取正股 {stock_code} 公告列表失败: {exc}") from exc

        rows = (payload.get("data") or {}).get("list") or []
        results: List[Dict[str, Any]] = []
        for row in rows:
            pub_d = _parse_date_safe(row.get("notice_date"))
            title = str(row.get("title") or "").strip()
            if pub_d is None or not title:
                continue
            if pub_d < cutoff_date or pub_d > as_of_date:
                continue
            results.append(
                {
                    "pub_date": pub_d,
                    "title": title,
                    "art_code": str(row.get("art_code") or "").strip(),
                }
            )
        return results

    def _fetch_notice_detail_snippet(self, art_code: str, max_chars: int) -> str:
        """尝试抓取单条高危公告正文前 max_chars 字；失败时静默返回空串并由调用方标记 detail_fetched=False。"""
        url = "https://np-cnotice-stock.eastmoney.com/api/content/ann"
        params = {"art_code": art_code, "client_source": "web", "page_index": "1"}
        try:
            with httpx.Client(timeout=self._http_timeout_sec) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                payload = resp.json()
            content = str((payload.get("data") or {}).get("notice_content") or "").strip()
            cleaned = " ".join(content.split())
            return cleaned[:max_chars]
        except Exception:
            return ""
