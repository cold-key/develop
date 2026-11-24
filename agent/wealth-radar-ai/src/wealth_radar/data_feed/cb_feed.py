"""可转债打新、全市场行情融合（集思录强赎表 + 东财全量列表 + 集思录补充）与正股近90天公告数据源。"""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Sequence

import httpx

from wealth_radar.domain.errors import DataFeedError, MissingDependencyError
from wealth_radar.domain.models import CBIpoItem, CBMarketRow, NoticeItem

# A 股公告开头标准免责声明正则，用于提取更有信息量的正文片段
_BOILERPLATE_PATTERN = re.compile(
    r"本公司董事会及全体董事保证本公告内容不存在任何虚假记载[、，,]?误导性陈述或者重大遗漏[^。]*。",
)


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
    if not text or text in {"-", "--", "nan", "None", "NaT"}:
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
    text = str(value).strip()
    if not text or text in {"-", "--", "nan", "None", "NaT"}:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _parse_redeem_status(status_text: str, countdown_text: str) -> tuple[bool, Optional[int]]:
    """解析集思录强赎状态与强赎天计数。"""
    status = status_text.strip()
    countdown = re.sub(r"<[^>]+>", " ", countdown_text).strip()

    if "已公告强赎" in status:
        return True, 0
    if "公告不强赎" in status or "暂不行使" in status:
        return False, None
    if "已满足强赎" in status:
        return False, 0

    # 匹配 "12/15" 或 "至少还需3天"
    ratio = re.search(r"(\d+)\s*/\s*(\d+)", countdown)
    if ratio:
        done = int(ratio.group(1))
        total = int(ratio.group(2))
        return False, max(0, total - done)

    need_days = re.search(r"还需\s*(\d+)\s*天", countdown)
    if need_days:
        return False, int(need_days.group(1))

    return False, None


def _estimate_conservative_ytm_pct(price: float, remaining_years: float, redeem_floor: float = 108.0) -> float:
    """在缺少集思录精确 YTM 时，按保守到期赎回价下限（108元）估算税前到期收益率。"""
    if price <= 0 or remaining_years <= 0:
        return -99.0
    years = max(remaining_years, 0.05)
    try:
        ytm = ((redeem_floor / price) ** (1.0 / years) - 1.0) * 100.0
        return round(ytm, 2)
    except (OverflowError, ZeroDivisionError, ValueError):
        return -99.0


class LiveCBFeed:
    """基于 akshare（免 Cookie 全市场融合）与东方财富公告接口的可转债数据提供器。"""

    def __init__(self, http_timeout_sec: float = 8.0, jisilu_cookie: str = "") -> None:
        self._http_timeout_sec = http_timeout_sec
        self._jisilu_cookie = jisilu_cookie.strip()
        self._list_em_df: Optional[Any] = None
        self._market_cache: Optional[Dict[str, CBMarketRow]] = None

    def _get_cb_list_em_df(self) -> Any:
        if self._list_em_df is not None:
            return self._list_em_df
        ak = _import_akshare()
        try:
            if hasattr(ak, "bond_cb_list_em"):
                self._list_em_df = ak.bond_cb_list_em()
            else:
                self._list_em_df = ak.bond_zh_cov()
        except Exception as exc:
            raise DataFeedError(f"akshare 拉取可转债列表(bond_cb_list_em)失败: {exc}") from exc
        return self._list_em_df

    def fetch_cb_ipos(self, trade_date: date) -> List[CBIpoItem]:
        df = self._get_cb_list_em_df()
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
        """融合全市场在市可转债（bond_cb_redeem_jsl + bond_cb_list_em + bond_cb_jsl），免 Cookie 覆盖全市场。"""
        ak = _import_akshare()
        today = date.today()

        # 1. 东方财富全量基础表（提供信用评级、债现价、转股溢价率、正股价）
        em_by_code: Dict[str, Dict[str, Any]] = {}
        try:
            em_df = self._get_cb_list_em_df()
            if em_df is not None and not getattr(em_df, "empty", True):
                for _, rec in em_df.iterrows():
                    code = str(rec.get("债券代码", "")).strip()
                    if code:
                        em_by_code[code] = rec.to_dict()
        except Exception:
            em_by_code = {}

        # 2. 集思录精确指标表（有 Cookie 时覆盖全市场；无 Cookie 时补充前 30 条精确 YTM / 回售触发价）
        jsl_by_code: Dict[str, Dict[str, Any]] = {}
        try:
            jsl_df = ak.bond_cb_jsl(cookie=self._jisilu_cookie) if self._jisilu_cookie else ak.bond_cb_jsl()
            if jsl_df is not None and not getattr(jsl_df, "empty", True):
                for _, rec in jsl_df.iterrows():
                    code = str(rec.get("代码", "")).strip()
                    if code:
                        jsl_by_code[code] = rec.to_dict()
        except Exception:
            jsl_by_code = {}

        # 3. 集思录强赎全量表（免 Cookie 返回全部 300+ 只在市转债，含到期日、现价、正股价、转股价、强赎状态与计数）
        redeem_df = None
        try:
            redeem_df = ak.bond_cb_redeem_jsl()
        except Exception as exc:
            if not jsl_by_code:
                raise DataFeedError(f"akshare 拉取可转债全市场行情失败: {exc}") from exc

        rows: List[CBMarketRow] = []
        seen_codes: set[str] = set()

        if redeem_df is not None and not getattr(redeem_df, "empty", True):
            for _, rec in redeem_df.iterrows():
                bond_code = str(rec.get("代码", "")).strip()
                bond_name = str(rec.get("名称", "")).strip()
                if not bond_code or not bond_name:
                    continue

                em_rec = em_by_code.get(bond_code, {})
                jsl_rec = jsl_by_code.get(bond_code, {})

                stock_code = str(rec.get("正股代码") or em_rec.get("正股代码") or "").strip()
                stock_name = str(rec.get("正股名称") or em_rec.get("正股简称") or "").strip()
                price = _to_float(jsl_rec.get("现价")) or _to_float(rec.get("现价")) or _to_float(em_rec.get("债现价"))
                stock_price = (
                    _to_float(jsl_rec.get("正股价"))
                    or _to_float(rec.get("正股价"))
                    or _to_float(em_rec.get("正股价"))
                )
                convert_price = _to_float(rec.get("转股价")) or _to_float(em_rec.get("转股价"))

                # 优先取集思录/东财转股溢价率，缺失时用现价与转股价值精确反算
                premium = _to_float(jsl_rec.get("转股溢价率"))
                if premium is None:
                    premium = _to_float(em_rec.get("转股溢价率"))
                if premium is None and price and stock_price and convert_price and convert_price > 0:
                    convert_value = (100.0 / convert_price) * stock_price
                    if convert_value > 0:
                        premium = (price / convert_value - 1.0) * 100.0

                # 剩余年限：优先用集思录，缺失则按到期日计算
                rem_years = _to_float(jsl_rec.get("剩余年限"))
                if rem_years is None:
                    maturity_dt = _parse_date_safe(rec.get("到期日"))
                    if maturity_dt is not None:
                        rem_years = max(0.0, (maturity_dt - today).days / 365.25)

                if (
                    price is None
                    or price <= 0
                    or stock_price is None
                    or stock_price <= 0
                    or premium is None
                    or rem_years is None
                ):
                    continue

                # 信用评级：兼容集思录 "债券评级" 与东财 "信用评级"
                rating = str(
                    jsl_rec.get("债券评级")
                    or jsl_rec.get("评级")
                    or em_rec.get("信用评级")
                    or ""
                ).strip()

                # YTM：优先集思录精确值，缺失时按保守到期赎回下限（108元）估算
                ytm = _to_float(jsl_rec.get("到期税前收益"))
                if ytm is None:
                    ytm = _estimate_conservative_ytm_pct(price, rem_years)

                redeem_announced, redeem_days_rem = _parse_redeem_status(
                    str(rec.get("强赎状态") or ""),
                    str(rec.get("强赎天计数") or ""),
                )

                putback_trigger_price = _to_float(jsl_rec.get("回售触发价"))
                putback_triggered = (
                    putback_trigger_price is not None
                    and putback_trigger_price > 0
                    and stock_price <= putback_trigger_price
                    and rem_years <= 2.0
                )

                rows.append(
                    CBMarketRow(
                        bond_code=bond_code,
                        bond_name=bond_name,
                        stock_code=stock_code,
                        stock_name=stock_name,
                        price=round(price, 3),
                        premium_rate_pct=round(premium, 2),
                        ytm_pct=round(ytm, 2),
                        remaining_years=round(rem_years, 2),
                        stock_price=round(stock_price, 2),
                        credit_rating=rating,
                        is_st=("ST" in stock_name.upper() or "ST" in bond_name.upper()),
                        redeem_announced=redeem_announced,
                        redeem_days_remaining=redeem_days_rem,
                        putback_triggered=putback_triggered,
                        putback_register_active=False,
                    )
                )
                seen_codes.add(bond_code)

        # 若 redeem_df 失败或漏掉个别集思录条目，补充 jsl_by_code
        for bond_code, jsl_rec in jsl_by_code.items():
            if bond_code in seen_codes:
                continue
            bond_name = str(jsl_rec.get("转债名称", "")).strip()
            stock_code = str(jsl_rec.get("正股代码", "")).strip()
            stock_name = str(jsl_rec.get("正股名称", "")).strip()
            price = _to_float(jsl_rec.get("现价"))
            premium = _to_float(jsl_rec.get("转股溢价率"))
            ytm = _to_float(jsl_rec.get("到期税前收益"))
            rem_years = _to_float(jsl_rec.get("剩余年限"))
            stock_price = _to_float(jsl_rec.get("正股价"))
            rating = str(jsl_rec.get("债券评级") or jsl_rec.get("评级") or "").strip()

            if (
                not bond_name
                or price is None
                or price <= 0
                or premium is None
                or rem_years is None
                or stock_price is None
                or stock_price <= 0
            ):
                continue

            rows.append(
                CBMarketRow(
                    bond_code=bond_code,
                    bond_name=bond_name,
                    stock_code=stock_code,
                    stock_name=stock_name,
                    price=round(price, 3),
                    premium_rate_pct=round(premium, 2),
                    ytm_pct=round(
                        ytm if ytm is not None else _estimate_conservative_ytm_pct(price, rem_years),
                        2,
                    ),
                    remaining_years=round(rem_years, 2),
                    stock_price=round(stock_price, 2),
                    credit_rating=rating,
                    is_st=("ST" in stock_name.upper() or "ST" in bond_name.upper()),
                )
            )

        if not rows:
            raise DataFeedError("融合后的可转债全市场行情为空")

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
        cutoff_date = as_of_date - timedelta(days=lookback_days)
        pure_code = re.sub(r"\D", "", stock_code)
        if not pure_code:
            return []

        raw_items = self._fetch_eastmoney_stock_notices(pure_code, cutoff_date, as_of_date)

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
        """抓取单条高危公告正文摘要（自动跳过标准免责声明），失败时静默回退。"""
        url = "https://np-cnotice-stock.eastmoney.com/api/content/ann"
        params = {"art_code": art_code, "client_source": "web", "page_index": "1"}
        try:
            with httpx.Client(timeout=self._http_timeout_sec) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                payload = resp.json()
            content = str((payload.get("data") or {}).get("notice_content") or "").strip()
            cleaned = " ".join(content.split())
            cleaned = _BOILERPLATE_PATTERN.sub("", cleaned).strip()
            return cleaned[:max_chars]
        except Exception:
            return ""
