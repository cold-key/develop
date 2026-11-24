"""Stage 1 证据打包器单元测试：高危关键词置顶、正文截断、硬字符上限与 SHA256 稳定性。"""

from __future__ import annotations

from datetime import date

from wealth_radar.config.loader import EvidenceBudgetConfig
from wealth_radar.core.evidence_packer import (
    build_evidence_bundle,
    serialize_bundle_for_hash,
)
from wealth_radar.domain.models import NoticeItem


def test_high_risk_notice_priority_snippet_truncation_and_hash_stability() -> None:
    budget = EvidenceBudgetConfig(
        max_notices_per_target=4,
        max_detail_chars_per_notice=120,
        max_news_per_target=3,
        max_chars_per_bundle=1600,
    )
    long_snippet = "公司董事会决定本次不向下修正转股价格，并承诺未来6个月不提出向下修正方案。" * 20

    notices = [
        NoticeItem(
            pub_date=date(2026, 11, 23),
            title="关于召开2026年第三次临时股东大会的通知",
            snippet="例行会议通知内容" * 40,
            detail_fetched=False,
        ),
        NoticeItem(
            pub_date=date(2026, 11, 10),
            title="关于不向下修正转股价格的公告",
            snippet=long_snippet,
            detail_fetched=True,
        ),
        NoticeItem(
            pub_date=date(2026, 11, 20),
            title="关于收到证监会立案告知书的公告",
            snippet="立案调查正文详情" * 30,
            detail_fetched=True,
        ),
        NoticeItem(
            pub_date=date(2026, 11, 18),
            title="关于业绩预告的补充说明",
            snippet="预计净利润小幅下滑" * 30,
            detail_fetched=False,
        ),
        # 重复标题去重测试
        NoticeItem(
            pub_date=date(2026, 11, 10),
            title="关于不向下修正转股价格的公告",
            snippet="",
            detail_fetched=False,
        ),
    ]

    bundle1 = build_evidence_bundle(
        trade_date=date(2026, 11, 24),
        asset_type="CB_CONVEX",
        audit_mode="CRO_VETO",
        target_id="123001",
        target_name="陷阱转债",
        data_as_of="2026-11-24 14:30 CST",
        quantitative_metrics={"bond_price": 102.0, "double_low": 123.0},
        trigger_summary="合规双低排名第1",
        budget_check={"allowed": True, "cb_available_cny": 3000.0},
        notices=notices,
        news_items=[
            NoticeItem(
                pub_date=date(2026, 11, 22),
                title="市场热点新闻",
                snippet="超长新闻正文" * 200,
            )
        ],
        user_holding_context={"already_holds_target": "NO"},
        notice_keywords=["不向下修正", "立案", "业绩预告"],
        high_priority_keywords=["不向下修正", "立案", "强赎"],
        budget=budget,
    )

    # 1. 高危关键词公告排在最前（按日期倒序：11-20 立案，11-10 不向下修正）
    assert len(bundle1.notices) >= 2
    assert "立案" in bundle1.notices[0].title
    assert "不向下修正" in bundle1.notices[1].title
    assert bundle1.notices[1].detail_fetched is True
    assert len(bundle1.notices[1].snippet) <= budget.max_detail_chars_per_notice

    # 2. 总体字符数严格满足硬上限
    serialized = serialize_bundle_for_hash(bundle1)
    assert len(serialized) <= budget.max_chars_per_bundle

    # 3. 乱序输入相同数据，evidence_sha256 必须完全一致
    bundle2 = build_evidence_bundle(
        trade_date=date(2026, 11, 24),
        asset_type="CB_CONVEX",
        audit_mode="CRO_VETO",
        target_id="123001",
        target_name="陷阱转债",
        data_as_of="2026-11-24 14:30 CST",
        quantitative_metrics={"double_low": 123.0, "bond_price": 102.0},
        trigger_summary="合规双低排名第1",
        budget_check={"cb_available_cny": 3000.0, "allowed": True},
        notices=list(reversed(notices)),
        news_items=[
            NoticeItem(
                pub_date=date(2026, 11, 22),
                title="市场热点新闻",
                snippet="超长新闻正文" * 200,
            )
        ],
        user_holding_context={"already_holds_target": "NO"},
        notice_keywords=["不向下修正", "立案", "业绩预告"],
        high_priority_keywords=["不向下修正", "立案", "强赎"],
        budget=budget,
    )
    assert bundle1.evidence_sha256 == bundle2.evidence_sha256
    assert len(bundle1.evidence_sha256) == 64
