"""Gate: 独立于任何大模型的 Python 代码层 Fail-Closed 硬门禁（防迎合、防超预算、防追高溢价 ETF）。"""

from __future__ import annotations

from typing import List, Tuple

from wealth_radar.domain.models import AuditVerdict, EvidenceBundle

NON_REVISION_KEYWORDS = ("不向下修正", "不下修")


def enforce_audit_gate(
    verdict: AuditVerdict,
    bundle: EvidenceBundle,
    max_etf_premium_pct: float = 2.0,
) -> Tuple[AuditVerdict, List[str]]:
    """对 Agent 提交的 AuditVerdict 执行五重确定性代码门禁，返回 (校验后结论, 触发覆写列表)。"""
    enforced = verdict.model_copy(deep=True)
    overrides: List[str] = []

    # 0. 强制对齐基础身份字段，防止手工/模型填错 target_id 或 audit_mode
    enforced.target_id = bundle.target_id
    enforced.target_name = bundle.target_name
    enforced.asset_type = bundle.asset_type
    enforced.audit_mode = bundle.audit_mode

    # 1. 预算硬门禁：三层预算已耗尽时无条件 REJECT
    if bundle.budget_check.get("allowed") is False:
        reason = str(bundle.budget_check.get("reason", "BUDGET_EXHAUSTED"))
        if not enforced.hard_veto or enforced.final_action != "REJECT":
            overrides.append(f"BUDGET_GATE: 预算超限 ({reason})，强制覆写为 REJECT + hard_veto=True")
        enforced.hard_veto = True
        enforced.final_action = "REJECT"
        enforced.veto_reason = f"BUDGET_GATE_BLOCKED: {reason}"
        if not any("预算" in w for w in enforced.missing_info_warnings):
            enforced.missing_info_warnings.append(f"代码层预算门禁已拦截：{reason}")

    # 2. 空证据门禁：本地 notices/news 与 Agent 联网补证 web_research_notes 全部为空时，严禁 APPROVE_BUY
    if not bundle.notices and not bundle.news_items and not enforced.web_research_notes:
        if enforced.final_action == "APPROVE_BUY" or not enforced.hard_veto:
            overrides.append("EMPTY_EVIDENCE_GATE: 本地证据与联网补证均为空，强制拦截 APPROVE_BUY")
        enforced.hard_veto = True
        if enforced.final_action == "APPROVE_BUY":
            enforced.final_action = "WATCHLIST"
        if not enforced.veto_reason:
            enforced.veto_reason = "EVIDENCE_EMPTY: 本地证据与联网核验均为空，按 Fail-Closed 拦截买入"
        warn = "本地 notices/news 与 web_research_notes 均为空，代码门禁已拦截 APPROVE_BUY"
        if warn not in enforced.missing_info_warnings:
            enforced.missing_info_warnings.append(warn)

    # 3. 可转债“不下修”未抓正文且未联网补证门禁
    if bundle.asset_type == "CB_CONVEX":
        unverified_non_rev = [
            n
            for n in bundle.notices
            if any(kw in n.title for kw in NON_REVISION_KEYWORDS) and not n.detail_fetched
        ]
        if unverified_non_rev and not enforced.web_research_notes and enforced.final_action != "REJECT":
            overrides.append(
                "NON_REVISION_DETAIL_GATE: 命中不下修公告但未抓到正文且无联网核验记录，强制拦截 APPROVE_BUY"
            )
            enforced.hard_veto = True
            if enforced.final_action == "APPROVE_BUY":
                enforced.final_action = "WATCHLIST"
            if not enforced.lockup_expiry_date:
                enforced.lockup_expiry_date = "UNSPECIFIED_IN_TITLE"
            if not enforced.veto_reason:
                enforced.veto_reason = (
                    "NON_REVISION_DETAIL_MISSING: 命中不下修公告但正文未核验，无法确认锁定期截止日"
                )
            warn = "命中“不向下修正”公告但正文未核验且无 web_research_notes，已由代码门禁拦截 APPROVE_BUY"
            if warn not in enforced.missing_info_warnings:
                enforced.missing_info_warnings.append(warn)

    # 4. 场内高溢价 ETF 追高硬门禁（v2.0 新增）
    if enforced.selected_etf_code and bundle.qdii_route_plan is not None:
        selected = enforced.selected_etf_code.strip()
        for etf in bundle.qdii_route_plan.etf_premiums:
            if etf.code == selected and (not etf.executable or etf.premium_pct > max_etf_premium_pct):
                overrides.append(
                    f"HIGH_PREMIUM_ETF_GATE: 所选场内 ETF {etf.code} 溢价 {etf.premium_pct:+.2f}% 超过红线 +{max_etf_premium_pct:.1f}%，强制覆写为 REJECT"
                )
                enforced.hard_veto = True
                enforced.final_action = "REJECT"
                enforced.veto_reason = (
                    f"HIGH_PREMIUM_ETF_BLOCKED: {etf.name}({etf.code}) 溢价 {etf.premium_pct:+.2f}% 超过红线"
                )
                break

    # 5. 一致性门禁：只要 hard_veto 为 True，绝不允许输出 APPROVE_BUY
    if enforced.hard_veto and enforced.final_action == "APPROVE_BUY":
        overrides.append("HARD_VETO_CONSISTENCY_GATE: hard_veto=True 与 APPROVE_BUY 冲突，强制覆写为 REJECT")
        enforced.final_action = "REJECT"
        if not enforced.veto_reason:
            enforced.veto_reason = "HARD_VETO_CONSISTENCY_OVERRIDE: hard_veto=True 严禁放行 APPROVE_BUY"

    return enforced, overrides
