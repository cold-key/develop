"""Stage 1: 公告关键词优先过滤、高危正文截断、字符硬上限与 SHA256 哈希打包器。"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from typing import Dict, List, Sequence

from wealth_radar.config.loader import EvidenceBudgetConfig
from wealth_radar.domain.models import (
    AssetType,
    AuditMode,
    CBCandidate,
    EvidenceBundle,
    IndexCandidate,
    NoticeItem,
)

DEFAULT_HIGH_PRIORITY_KEYWORDS: tuple[str, ...] = (
    "不向下修正",
    "不下修",
    "立案",
    "退市",
    "违约",
    "逾期",
    "强赎",
    "提前赎回",
    "回售",
    "业绩预告",
    "评级",
)


def _truncate_text(text: str, max_chars: int) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_chars:
        return cleaned
    if max_chars <= 3:
        return cleaned[:max_chars]
    return cleaned[: max_chars - 3] + "..."


def _find_matched_keywords(text: str, keywords: Sequence[str]) -> List[str]:
    return [kw for kw in keywords if kw and kw in text]


def prioritize_and_pack_notices(
    notices: List[NoticeItem],
    notice_keywords: Sequence[str],
    high_priority_keywords: Sequence[str],
    budget: EvidenceBudgetConfig,
) -> List[NoticeItem]:
    """去重、关键词匹配、高危置顶排序、单条正文截断与数量裁剪。"""
    deduped: Dict[tuple[date, str], NoticeItem] = {}
    for item in notices:
        key = (item.pub_date, item.title.strip())
        existing = deduped.get(key)
        if existing is None or (item.detail_fetched and not existing.detail_fetched) or (
            len(item.snippet) > len(existing.snippet)
        ):
            deduped[key] = item

    high_kw = tuple(high_priority_keywords) if high_priority_keywords else DEFAULT_HIGH_PRIORITY_KEYWORDS

    enriched: List[tuple[int, int, int, str, NoticeItem]] = []
    for item in deduped.values():
        combined_text = f"{item.title} {item.snippet}"
        matched = list(item.matched_keywords)
        for kw in _find_matched_keywords(combined_text, notice_keywords):
            if kw not in matched:
                matched.append(kw)

        has_high_priority = 0 if any(kw in combined_text for kw in high_kw) else 1
        has_any_keyword = 0 if matched else 1

        packed_item = NoticeItem(
            pub_date=item.pub_date,
            title=item.title.strip(),
            snippet=_truncate_text(item.snippet, budget.max_detail_chars_per_notice),
            detail_fetched=item.detail_fetched,
            matched_keywords=matched,
        )
        enriched.append(
            (
                has_high_priority,
                has_any_keyword,
                -packed_item.pub_date.toordinal(),
                packed_item.title,
                packed_item,
            )
        )

    enriched.sort(key=lambda entry: (entry[0], entry[1], entry[2], entry[3]))
    return [entry[4] for entry in enriched[: budget.max_notices_per_target]]


def pack_news_items(
    news_items: List[NoticeItem],
    budget: EvidenceBudgetConfig,
) -> List[NoticeItem]:
    """去重、按日期倒序排序并截断新闻条目。"""
    deduped: Dict[tuple[date, str], NoticeItem] = {}
    for item in news_items:
        key = (item.pub_date, item.title.strip())
        if key not in deduped or len(item.snippet) > len(deduped[key].snippet):
            deduped[key] = item

    ordered = sorted(
        deduped.values(),
        key=lambda n: (-n.pub_date.toordinal(), n.title.strip()),
    )
    return [
        NoticeItem(
            pub_date=item.pub_date,
            title=item.title.strip(),
            snippet=_truncate_text(item.snippet, budget.max_detail_chars_per_notice),
            detail_fetched=item.detail_fetched,
            matched_keywords=list(item.matched_keywords),
        )
        for item in ordered[: budget.max_news_per_target]
    ]


def serialize_bundle_for_hash(bundle: EvidenceBundle) -> str:
    """生成规范化 JSON 字符串（不含 evidence_sha256 字段），用于字符数计量与 SHA256 计算。"""
    payload = bundle.model_dump(mode="json", exclude={"evidence_sha256"})
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compute_evidence_sha256(bundle: EvidenceBundle) -> str:
    """基于规范化 JSON 内容计算稳定的 SHA256 哈希。"""
    canonical = serialize_bundle_for_hash(bundle)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _enforce_char_budget(bundle: EvidenceBundle, max_chars: int) -> EvidenceBundle:
    """按优先级逐步裁剪非关键新闻与正文片段，严格保证序列化文本 <= max_chars。"""
    working = bundle.model_copy(deep=True)

    # 1. 若超限，先从尾部裁剪 news_items 的正文，再移除尾部 news_items
    while len(serialize_bundle_for_hash(working)) > max_chars and working.news_items:
        trimmed_snippet = False
        for item in reversed(working.news_items):
            if item.snippet:
                item.snippet = ""
                trimmed_snippet = True
                break
        if not trimmed_snippet:
            working.news_items.pop()

    # 2. 若仍超限，先从低优先级（尾部）缩减 notices 的正文片段
    while len(serialize_bundle_for_hash(working)) > max_chars and working.notices:
        shrunk = False
        for item in reversed(working.notices):
            if len(item.snippet) > 40:
                item.snippet = _truncate_text(item.snippet, len(item.snippet) // 2)
                shrunk = True
                break
            if item.snippet:
                item.snippet = ""
                shrunk = True
                break
        if shrunk:
            continue
        # 至少保留最高优先级的 1 条公告标题（除非单条本身仍超限）
        if len(working.notices) > 1:
            working.notices.pop()
        else:
            working.notices[0].title = _truncate_text(working.notices[0].title, 80)
            if len(serialize_bundle_for_hash(working)) > max_chars:
                working.notices.pop()
            break

    # 3. 极端情况：若连元数据都超限，裁剪 trigger_summary 与 data_as_of
    if len(serialize_bundle_for_hash(working)) > max_chars:
        working.trigger_summary = _truncate_text(working.trigger_summary, 120)
        working.data_as_of = _truncate_text(working.data_as_of, 120)

    working.evidence_sha256 = compute_evidence_sha256(working)
    return working


def build_evidence_bundle(
    *,
    trade_date: date,
    asset_type: AssetType,
    audit_mode: AuditMode,
    target_id: str,
    target_name: str,
    data_as_of: str,
    quantitative_metrics: Dict[str, float | str],
    trigger_summary: str,
    budget_check: Dict[str, float | str | bool],
    notices: List[NoticeItem],
    news_items: List[NoticeItem],
    user_holding_context: Dict[str, float | str],
    notice_keywords: Sequence[str],
    high_priority_keywords: Sequence[str],
    budget: EvidenceBudgetConfig,
) -> EvidenceBundle:
    """构建符合硬字符上限并带稳定 SHA256 哈希的 EvidenceBundle。"""
    packed_notices = prioritize_and_pack_notices(
        notices=notices,
        notice_keywords=notice_keywords,
        high_priority_keywords=high_priority_keywords,
        budget=budget,
    )
    packed_news = pack_news_items(news_items=news_items, budget=budget)

    raw_bundle = EvidenceBundle(
        trade_date=trade_date,
        asset_type=asset_type,
        audit_mode=audit_mode,
        target_id=target_id,
        target_name=target_name,
        data_as_of=data_as_of,
        quantitative_metrics=quantitative_metrics,
        trigger_summary=trigger_summary,
        budget_check=budget_check,
        notices=packed_notices,
        news_items=packed_news,
        user_holding_context=user_holding_context,
    )
    return _enforce_char_budget(raw_bundle, budget.max_chars_per_bundle)


def pack_index_evidence(
    candidate: IndexCandidate,
    news_items: List[NoticeItem],
    trade_date: date,
    budget: EvidenceBudgetConfig,
) -> EvidenceBundle:
    """为命中的指数回撤候选组装 INDEX_BRIEFING 证据包。"""
    metrics: Dict[str, float | str] = {
        "latest_close": candidate.latest_close,
        "peak_120d": candidate.peak_120d,
        "drawdown_pct": candidate.drawdown_pct,
        "triggered_tier_pct": candidate.triggered_tier_pct,
        "requested_amount_cny": candidate.requested_amount_cny,
        "approved_amount_cny": candidate.approved_amount_cny,
        "market_timezone": candidate.market_timezone,
        "correlation_group": candidate.correlation_group,
    }
    return build_evidence_bundle(
        trade_date=trade_date,
        asset_type="INDEX_BATCH",
        audit_mode="INDEX_BRIEFING",
        target_id=candidate.symbol,
        target_name=candidate.name,
        data_as_of=candidate.data_as_of,
        quantitative_metrics=metrics,
        trigger_summary=candidate.trigger_summary,
        budget_check=candidate.budget_check,
        notices=[],
        news_items=news_items,
        user_holding_context=candidate.user_holding_context,
        notice_keywords=(),
        high_priority_keywords=(),
        budget=budget,
    )


def pack_cb_evidence(
    candidate: CBCandidate,
    notices: List[NoticeItem],
    news_items: List[NoticeItem],
    trade_date: date,
    notice_keywords: Sequence[str],
    fetch_detail_keywords: Sequence[str],
    budget: EvidenceBudgetConfig,
) -> EvidenceBundle:
    """为命中的低价可转债候选组装 CRO_VETO 证据包。"""
    row = candidate.row
    metrics: Dict[str, float | str] = {
        "bond_price": row.price,
        "premium_rate_pct": row.premium_rate_pct,
        "double_low": candidate.double_low,
        "ytm_pct": row.ytm_pct,
        "remaining_years": row.remaining_years,
        "stock_code": row.stock_code,
        "stock_name": row.stock_name,
        "stock_price": row.stock_price,
        "credit_rating": row.credit_rating,
        "redeem_announced": "YES" if row.redeem_announced else "NO",
        "putback_triggered": "YES" if row.putback_triggered else "NO",
    }
    return build_evidence_bundle(
        trade_date=trade_date,
        asset_type="CB_CONVEX",
        audit_mode="CRO_VETO",
        target_id=row.bond_code,
        target_name=row.bond_name,
        data_as_of=f"{trade_date.isoformat()} 14:30 CST",
        quantitative_metrics=metrics,
        trigger_summary=candidate.trigger_summary,
        budget_check=candidate.budget_check,
        notices=notices,
        news_items=news_items,
        user_holding_context=candidate.user_holding_context,
        notice_keywords=notice_keywords,
        high_priority_keywords=fetch_detail_keywords,
        budget=budget,
    )
