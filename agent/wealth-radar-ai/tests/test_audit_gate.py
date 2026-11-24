"""代码层五重 Fail-Closed 硬门禁单元测试（100% 离线，零 LLM 依赖）。"""

from __future__ import annotations

from datetime import date

from wealth_radar.core.audit_gate import enforce_audit_gate
from wealth_radar.core.evidence_packer import compute_evidence_sha256
from wealth_radar.domain.models import (
    AuditVerdict,
    ETFSpotPremium,
    EvidenceBundle,
    NoticeItem,
    QDIIRoutePlan,
)


def _cb_bundle(*, notices: list[NoticeItem], budget_allowed: bool = True) -> EvidenceBundle:
    b = EvidenceBundle(
        trade_date=date(2026, 11, 24),
        asset_type="CB_CONVEX",
        audit_mode="CRO_VETO",
        target_id="123001",
        target_name="陷阱转债",
        data_as_of="2026-11-24 14:30 CST",
        quantitative_metrics={"bond_price": 102.0},
        trigger_summary="双低第1",
        budget_check={"allowed": budget_allowed, "reason": "OK" if budget_allowed else "BUDGET_EXHAUSTED"},
        notices=notices,
        news_items=[],
    )
    b.evidence_sha256 = compute_evidence_sha256(b)
    return b


def _approve_verdict(
    *,
    target_id: str = "123001",
    asset_type: str = "CB_CONVEX",
    audit_mode: str = "CRO_VETO",
    hard_veto: bool = False,
    web_notes: list[str] | None = None,
    selected_etf_code: str | None = None,
) -> AuditVerdict:
    return AuditVerdict(
        target_id=target_id,
        target_name="测试标的",
        asset_type=asset_type,  # type: ignore[arg-type]
        audit_mode=audit_mode,  # type: ignore[arg-type]
        hard_veto=hard_veto,
        selected_etf_code=selected_etf_code,
        credit_or_structural_risk="LOW",
        thesis_status="INTACT",
        bear_case_arguments=["存在常规波动风险"],
        web_research_notes=web_notes or [],
        final_action="APPROVE_BUY",
        confidence_score=80,
    )


def test_budget_gate_and_hard_veto_consistency_override() -> None:
    bundle = _cb_bundle(
        notices=[NoticeItem(pub_date=date(2026, 11, 20), title="业绩预告", snippet="预增20%", detail_fetched=True)],
        budget_allowed=False,
    )
    enforced, overrides = enforce_audit_gate(_approve_verdict(), bundle)
    assert enforced.hard_veto is True
    assert enforced.final_action == "REJECT"
    assert any("BUDGET_GATE" in o for o in overrides)

    # hard_veto=True 与 APPROVE_BUY 矛盾时强制覆写 REJECT
    ok_bundle = _cb_bundle(
        notices=[NoticeItem(pub_date=date(2026, 11, 20), title="业绩预告", snippet="预增20%", detail_fetched=True)],
        budget_allowed=True,
    )
    enforced2, overrides2 = enforce_audit_gate(_approve_verdict(hard_veto=True), ok_bundle)
    assert enforced2.final_action == "REJECT"
    assert any("HARD_VETO_CONSISTENCY_GATE" in o for o in overrides2)


def test_empty_evidence_and_unverified_non_revision_cleared_only_with_web_notes() -> None:
    # 1. 本地证据为空且无联网补证 -> 拦截 APPROVE_BUY
    empty_b = _cb_bundle(notices=[])
    enforced, overrides = enforce_audit_gate(_approve_verdict(), empty_b)
    assert enforced.hard_veto is True
    assert enforced.final_action == "WATCHLIST"
    assert any("EMPTY_EVIDENCE_GATE" in o for o in overrides)

    # 2. 若 Agent 已通过 Harness 联网核验并写入 web_research_notes -> 允许正常放行
    enforced_web, overrides_web = enforce_audit_gate(
        _approve_verdict(web_notes=["2026-11-24 [巨潮资讯] 已核验三季报及近90日无不下修公告"]),
        empty_b,
    )
    assert enforced_web.final_action == "APPROVE_BUY"
    assert overrides_web == []

    # 3. 命中不下修且未抓正文 + 无联网补证 -> 强制拦截
    non_rev_b = _cb_bundle(
        notices=[NoticeItem(pub_date=date(2026, 11, 10), title="关于不向下修正转股价格的公告", detail_fetched=False)]
    )
    enforced_nr, overrides_nr = enforce_audit_gate(_approve_verdict(), non_rev_b)
    assert enforced_nr.hard_veto is True
    assert enforced_nr.final_action == "WATCHLIST"
    assert enforced_nr.lockup_expiry_date == "UNSPECIFIED_IN_TITLE"
    assert any("NON_REVISION_DETAIL_GATE" in o for o in overrides_nr)


def test_high_premium_on_exchange_etf_gate_blocks_approve_buy() -> None:
    idx_bundle = EvidenceBundle(
        trade_date=date(2026, 11, 24),
        asset_type="INDEX_BATCH",
        audit_mode="INDEX_BRIEFING",
        target_id="QQQ",
        target_name="纳指100",
        data_as_of="2026-11-23 US Close",
        quantitative_metrics={"latest_close": 651.0},
        trigger_summary="触发 -10% 档位",
        budget_check={"allowed": True},
        news_items=[NoticeItem(pub_date=date(2026, 11, 23), title="美股回调", snippet="利率重定价", detail_fetched=True)],
        qdii_route_plan=QDIIRoutePlan(
            benchmark_symbol="QQQ",
            requested_amount_cny=1200.0,
            total_allocated_cny=1200.0,
            shortfall_cny=0.0,
            etf_premiums=[
                ETFSpotPremium(
                    code="513100",
                    name="国泰纳指ETF",
                    spot_price=2.05,
                    latest_nav=1.6742,
                    premium_pct=22.45,
                    executable=False,
                    warning="高溢价严禁接盘",
                )
            ],
        ),
    )
    verdict = _approve_verdict(
        target_id="QQQ",
        asset_type="INDEX_BATCH",
        audit_mode="INDEX_BRIEFING",
        selected_etf_code="513100",
    )
    enforced, overrides = enforce_audit_gate(verdict, idx_bundle, max_etf_premium_pct=2.0)
    assert enforced.hard_veto is True
    assert enforced.final_action == "REJECT"
    assert any("HIGH_PREMIUM_ETF_GATE" in o for o in overrides)
