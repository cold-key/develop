"""BaseAuditLLM 抽象基类：双模式分派、当日缓存幂等、校验重试与代码层硬门禁。"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

from pydantic import ValidationError

from wealth_radar.config.loader import LLMConfig
from wealth_radar.domain.models import AuditRecord, AuditVerdict, EvidenceBundle
from wealth_radar.llm.prompts import build_user_prompt, get_prompt_for_mode

NON_REVISION_KEYWORDS = ("不向下修正", "不下修")


def make_cache_key(
    target_id: str,
    trade_date_iso: str,
    evidence_sha256: str,
    prompt_version: str,
) -> str:
    """计算四元组幂等缓存键：(target_id, trade_date, evidence_sha256, prompt_version)。"""
    return f"{target_id}|{trade_date_iso}|{evidence_sha256}|{prompt_version}"


def strip_json_fences(raw_text: str) -> str:
    """清理部分兼容接口偶尔包裹的 ```json ... ``` 围栏。"""
    text = raw_text.strip()
    match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def build_fail_closed_verdict(bundle: EvidenceBundle, reason: str) -> AuditVerdict:
    """构造 Fail-Closed 兜底结论（绝不放行 APPROVE_BUY）。"""
    return AuditVerdict(
        target_id=bundle.target_id,
        target_name=bundle.target_name,
        asset_type=bundle.asset_type,
        audit_mode=bundle.audit_mode,
        hard_veto=True,
        veto_reason=f"LLM_AUDIT_FAILED: {reason}",
        credit_or_structural_risk="HIGH",
        thesis_status="UNKNOWN",
        bear_case_arguments=["LLM 审计网关超时、异常或结构化输出校验失败，按 Fail-Closed 原则自动拦截买入。"],
        bull_case_catalysts=[],
        evidence_citations=[],
        missing_info_warnings=[f"自动审计降级原因: {reason}"],
        final_action="WATCHLIST",
        confidence_score=0,
    )


def enforce_post_processing_rules(
    verdict: AuditVerdict,
    bundle: EvidenceBundle,
) -> AuditVerdict:
    """代码层二次强校验（不轻信模型自觉）：执行预算、证据空缺、不下修正文缺失与一致性四重硬门禁。"""
    enforced = verdict.model_copy(deep=True)

    # 0. 强制对齐基础身份字段，防止模型篡改 target_id / asset_type / audit_mode
    enforced.target_id = bundle.target_id
    enforced.target_name = bundle.target_name
    enforced.asset_type = bundle.asset_type
    enforced.audit_mode = bundle.audit_mode

    # 1. 预算硬门禁：预算超限时无条件 REJECT
    if bundle.budget_check.get("allowed") is False:
        enforced.hard_veto = True
        enforced.final_action = "REJECT"
        reason = str(bundle.budget_check.get("reason", "BUDGET_EXHAUSTED"))
        enforced.veto_reason = f"BUDGET_GATE_BLOCKED: {reason}"
        if not any("预算" in w for w in enforced.missing_info_warnings):
            enforced.missing_info_warnings.append(f"代码层预算门禁已拦截：{reason}")

    # 2. 证据空缺门禁：notices 与 news_items 均为空时严禁 APPROVE_BUY
    if not bundle.notices and not bundle.news_items:
        enforced.hard_veto = True
        if enforced.final_action == "APPROVE_BUY":
            enforced.final_action = "WATCHLIST"
        if not enforced.veto_reason:
            enforced.veto_reason = "EVIDENCE_EMPTY: 公告与新闻证据均为空，按 Fail-Closed 拦截买入"
        warning = "输入证据包中 notices 与 news_items 均为空，已由代码层强制降级拦截 APPROVE_BUY"
        if warning not in enforced.missing_info_warnings:
            enforced.missing_info_warnings.append(warning)

    # 3. 可转债“不下修”公告未抓到正文门禁
    if bundle.asset_type == "CB_CONVEX":
        unverified_non_rev = [
            n
            for n in bundle.notices
            if any(kw in n.title for kw in NON_REVISION_KEYWORDS) and not n.detail_fetched
        ]
        if unverified_non_rev and enforced.final_action != "REJECT":
            enforced.hard_veto = True
            if enforced.final_action == "APPROVE_BUY":
                enforced.final_action = "WATCHLIST"
            if not enforced.lockup_expiry_date:
                enforced.lockup_expiry_date = "UNSPECIFIED_IN_TITLE"
            if not enforced.veto_reason:
                enforced.veto_reason = (
                    "NON_REVISION_DETAIL_MISSING: 命中不下修公告但未抓到正文，无法确认锁定期截止日"
                )
            warning = "命中“不向下修正”公告但未抓取正文，已由代码层强制拦截 APPROVE_BUY，请人工查阅原文确认锁定期。"
            if warning not in enforced.missing_info_warnings:
                enforced.missing_info_warnings.append(warning)

    # 4. 一致性门禁：只要 hard_veto 为 True，严禁输出 APPROVE_BUY
    if enforced.hard_veto and enforced.final_action == "APPROVE_BUY":
        enforced.final_action = "REJECT"
        if not enforced.veto_reason:
            enforced.veto_reason = "HARD_VETO_CONSISTENCY_OVERRIDE: hard_veto=True 不允许放行 APPROVE_BUY"

    return enforced


class BaseAuditLLM(ABC):
    """所有 LLM Provider 适配器的公共基类。"""

    provider_name: str = "base"

    def __init__(self, cfg: LLMConfig) -> None:
        self.cfg = cfg

    @abstractmethod
    def _call_provider(
        self,
        system_prompt: str,
        user_prompt: str,
        bundle: EvidenceBundle,
    ) -> AuditVerdict | str:
        """向底层 Provider 发起单次推理请求，返回已解析的 AuditVerdict 或原始 JSON 字符串。"""

    def audit(
        self,
        bundle: EvidenceBundle,
        price_at_audit: float,
        cache: Optional[Dict[str, AuditVerdict]] = None,
        force_audit: bool = False,
    ) -> Tuple[AuditRecord, bool]:
        """执行完整审计流程：缓存检查 -> 调用/解析/重试 -> Fail-Closed 兜底 -> 代码层强校验。"""
        prompt_version, system_prompt = get_prompt_for_mode(bundle.audit_mode)
        cache_key = make_cache_key(
            target_id=bundle.target_id,
            trade_date_iso=bundle.trade_date.isoformat(),
            evidence_sha256=bundle.evidence_sha256,
            prompt_version=prompt_version,
        )

        # 1. 当日幂等缓存命中检查
        if (
            self.cfg.enable_daily_cache
            and not force_audit
            and cache is not None
            and cache_key in cache
        ):
            cached_verdict = enforce_post_processing_rules(cache[cache_key], bundle)
            record = AuditRecord(
                run_timestamp=datetime.now(timezone.utc),
                prompt_version=prompt_version,
                provider=self.provider_name,
                model=self.cfg.model,
                price_at_audit=price_at_audit,
                bundle=bundle,
                verdict=cached_verdict,
                from_cache=True,
            )
            return record, True

        # 2. 调起底层模型并执行最多 max_parse_retries 次带报错反馈的重试
        base_user_prompt = build_user_prompt(bundle, include_json_schema=False)
        current_user_prompt = base_user_prompt
        verdict: Optional[AuditVerdict] = None
        last_error_msg = ""

        max_attempts = 1 + self.cfg.max_parse_retries
        for attempt in range(max_attempts):
            try:
                raw_result = self._call_provider(system_prompt, current_user_prompt, bundle)
                if isinstance(raw_result, AuditVerdict):
                    verdict = raw_result
                else:
                    cleaned = strip_json_fences(raw_result)
                    verdict = AuditVerdict.model_validate_json(cleaned)
                break
            except (ValidationError, json.JSONDecodeError, ValueError) as exc:
                last_error_msg = f"JSON/Schema 校验失败 (attempt {attempt + 1}/{max_attempts}): {exc}"
                if attempt + 1 < max_attempts:
                    current_user_prompt = (
                        f"{base_user_prompt}\n\n"
                        f"【上次输出格式校验失败，请修正并仅输出合法 JSON】\n错误信息：{exc}"
                    )
                    continue
            except Exception as exc:
                # 网络超时 / HTTP 异常等不可重试解析错误直接触发 Fail-Closed
                last_error_msg = f"Provider 调用异常: {exc}"
                break

        audit_succeeded = verdict is not None
        if verdict is None:
            verdict = build_fail_closed_verdict(bundle, last_error_msg or "未知错误")

        # 3. 执行代码层四重硬门禁
        final_verdict = enforce_post_processing_rules(verdict, bundle)

        # 仅对正常完成的审计结果写入当日缓存（Fail-Closed 瞬时网络故障不写入缓存，允许稍后重跑恢复）
        if audit_succeeded and self.cfg.enable_daily_cache and cache is not None:
            cache[cache_key] = final_verdict

        record = AuditRecord(
            run_timestamp=datetime.now(timezone.utc),
            prompt_version=prompt_version,
            provider=self.provider_name,
            model=self.cfg.model,
            price_at_audit=price_at_audit,
            bundle=bundle,
            verdict=final_verdict,
            from_cache=False,
        )
        return record, False
