"""Stage 2 双模式 LLM 网关单元测试：路由、四重硬门禁、重试、Fail-Closed、400 回退与缓存幂等。"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any, List

from wealth_radar.config.loader import LLMConfig
from wealth_radar.core.evidence_packer import compute_evidence_sha256
from wealth_radar.domain.models import AuditVerdict, EvidenceBundle, NoticeItem
from wealth_radar.llm.base import BaseAuditLLM
from wealth_radar.llm.gemini_client import GeminiAuditClient
from wealth_radar.llm.openai_client import OpenAICompatibleAuditClient
from wealth_radar.llm.prompts import CB_PROMPT_VERSION, INDEX_PROMPT_VERSION

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_RESPONSES = json.loads((FIXTURES_DIR / "sample_llm_responses.json").read_text(encoding="utf-8"))


class _StubAuditLLM(BaseAuditLLM):
    provider_name = "stub"

    def __init__(self, cfg: LLMConfig, outputs: List[Any]) -> None:
        super().__init__(cfg)
        self._outputs = list(outputs)
        self.calls: List[tuple[str, str]] = []

    def _call_provider(
        self,
        system_prompt: str,
        user_prompt: str,
        bundle: EvidenceBundle,
    ) -> AuditVerdict | str:
        self.calls.append((system_prompt, user_prompt))
        item = self._outputs.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def _make_cb_bundle(
    *,
    notices: List[NoticeItem],
    budget_allowed: bool = True,
) -> EvidenceBundle:
    bundle = EvidenceBundle(
        trade_date=date(2026, 11, 24),
        asset_type="CB_CONVEX",
        audit_mode="CRO_VETO",
        target_id="123001",
        target_name="陷阱转债",
        data_as_of="2026-11-24 14:30 CST",
        quantitative_metrics={"bond_price": 102.0, "double_low": 123.0},
        trigger_summary="合规双低排名第1",
        budget_check={
            "allowed": budget_allowed,
            "reason": "OK" if budget_allowed else "BUDGET_EXHAUSTED",
        },
        notices=notices,
        news_items=[],
        user_holding_context={},
    )
    bundle.evidence_sha256 = compute_evidence_sha256(bundle)
    return bundle


def _make_index_bundle(budget_allowed: bool = True) -> EvidenceBundle:
    bundle = EvidenceBundle(
        trade_date=date(2026, 11, 24),
        asset_type="INDEX_BATCH",
        audit_mode="INDEX_BRIEFING",
        target_id="QQQ",
        target_name="纳指100 (对应场外C类)",
        data_as_of="2026-11-23 US Close",
        quantitative_metrics={"latest_close": 468.0, "drawdown_pct": -10.0},
        trigger_summary="首次触发 -10% 档位",
        budget_check={
            "allowed": budget_allowed,
            "reason": "OK" if budget_allowed else "BUDGET_EXHAUSTED",
        },
        notices=[],
        news_items=[
            NoticeItem(
                pub_date=date(2026, 11, 23),
                title="通胀预期扰动引发科技股回调",
                snippet="市场重新定价降息节奏",
                detail_fetched=True,
            )
        ],
        user_holding_context={},
    )
    bundle.evidence_sha256 = compute_evidence_sha256(bundle)
    return bundle


def test_dual_mode_prompt_routing_and_gemini_adapter() -> None:
    captured_configs: List[Any] = []

    class _FakeGeminiModels:
        def __init__(self, responses: List[str]) -> None:
            self._responses = list(responses)

        def generate_content(self, *, model: str, contents: str, config: Any) -> Any:
            captured_configs.append(config)
            return SimpleNamespace(parsed=None, text=self._responses.pop(0))

    fake_client = SimpleNamespace(
        models=_FakeGeminiModels(
            [
                json.dumps(SAMPLE_RESPONSES["cb_non_revision_reject"], ensure_ascii=False),
                json.dumps(SAMPLE_RESPONSES["index_panic_approve"], ensure_ascii=False),
            ]
        )
    )
    gateway = GeminiAuditClient(cfg=LLMConfig(provider="gemini"), client=fake_client)

    cb_bundle = _make_cb_bundle(
        notices=[
            NoticeItem(
                pub_date=date(2026, 11, 10),
                title="关于不向下修正“陷阱转债”转股价格的公告",
                snippet="未来6个月至2027-05-10不下修",
                detail_fetched=True,
            )
        ]
    )
    idx_bundle = _make_index_bundle()

    cb_rec, _ = gateway.audit(cb_bundle, price_at_audit=102.0)
    idx_rec, _ = gateway.audit(idx_bundle, price_at_audit=468.0)

    assert cb_rec.prompt_version == CB_PROMPT_VERSION
    assert cb_rec.verdict.hard_veto is True
    assert cb_rec.verdict.final_action == "REJECT"
    assert cb_rec.verdict.lockup_expiry_date == "2027-05-10"

    assert idx_rec.prompt_version == INDEX_PROMPT_VERSION
    assert idx_rec.verdict.hard_veto is False
    assert idx_rec.verdict.final_action == "APPROVE_BUY"
    assert idx_rec.verdict.drawdown_attribution is not None

    # 验证两个模式分别注入了不同 System Prompt
    sys0 = (
        captured_configs[0]["system_instruction"]
        if isinstance(captured_configs[0], dict)
        else captured_configs[0].system_instruction
    )
    sys1 = (
        captured_configs[1]["system_instruction"]
        if isinstance(captured_configs[1], dict)
        else captured_configs[1].system_instruction
    )
    assert "首席风控官" in sys0
    assert "对抗情绪误杀" in sys1


def test_code_level_gates_empty_evidence_unverified_non_revision_and_budget() -> None:
    approve_json = json.dumps(SAMPLE_RESPONSES["cb_clean_approve"], ensure_ascii=False)

    # 1. 空证据包：即使模型误输出 APPROVE_BUY，代码层强制拦截为 WATCHLIST + hard_veto=True
    empty_bundle = _make_cb_bundle(notices=[])
    gw1 = _StubAuditLLM(LLMConfig(), [approve_json])
    rec1, _ = gw1.audit(empty_bundle, price_at_audit=102.0)
    assert rec1.verdict.hard_veto is True
    assert rec1.verdict.final_action == "WATCHLIST"

    # 2. 不下修公告但 detail_fetched=False：即使模型误放行 APPROVE_BUY，代码层强制降级拦截
    title_only_bundle = _make_cb_bundle(
        notices=[
            NoticeItem(
                pub_date=date(2026, 11, 10),
                title="关于不向下修正转股价格的公告",
                snippet="",
                detail_fetched=False,
            )
        ]
    )
    gw2 = _StubAuditLLM(LLMConfig(), [approve_json])
    rec2, _ = gw2.audit(title_only_bundle, price_at_audit=102.0)
    assert rec2.verdict.hard_veto is True
    assert rec2.verdict.final_action == "WATCHLIST"
    assert rec2.verdict.lockup_expiry_date == "UNSPECIFIED_IN_TITLE"

    # 3. 预算超限：即使模型放行 APPROVE_BUY，代码层强制覆写为 REJECT + hard_veto=True
    over_budget_bundle = _make_index_bundle(budget_allowed=False)
    gw3 = _StubAuditLLM(
        LLMConfig(), [json.dumps(SAMPLE_RESPONSES["index_panic_approve"], ensure_ascii=False)]
    )
    rec3, _ = gw3.audit(over_budget_bundle, price_at_audit=468.0)
    assert rec3.verdict.hard_veto is True
    assert rec3.verdict.final_action == "REJECT"
    assert rec3.verdict.veto_reason and "BUDGET_GATE_BLOCKED" in rec3.verdict.veto_reason


def test_json_retry_success_and_fail_closed_after_double_failure() -> None:
    bundle = _make_cb_bundle(
        notices=[
            NoticeItem(
                pub_date=date(2026, 11, 5),
                title="2026年三季度业绩预告",
                snippet="净利润预增18%",
                detail_fetched=True,
            )
        ]
    )
    valid_json = json.dumps(SAMPLE_RESPONSES["cb_clean_approve"], ensure_ascii=False)

    # 第 1 次非法 JSON，第 2 次重试成功
    gw_retry = _StubAuditLLM(LLMConfig(max_parse_retries=1), ["{invalid json", valid_json])
    rec_ok, _ = gw_retry.audit(bundle, price_at_audit=104.5)
    assert len(gw_retry.calls) == 2
    assert "上次输出格式校验失败" in gw_retry.calls[1][1]
    assert rec_ok.verdict.final_action == "APPROVE_BUY"

    # 2 次均非法 JSON -> 触发 Fail-Closed（绝不返回 APPROVE_BUY）
    gw_fail = _StubAuditLLM(LLMConfig(max_parse_retries=1), ["not-json", '{"bad": true}'])
    rec_fail, _ = gw_fail.audit(bundle, price_at_audit=104.5)
    assert len(gw_fail.calls) == 2
    assert rec_fail.verdict.hard_veto is True
    assert rec_fail.verdict.final_action == "WATCHLIST"
    assert rec_fail.verdict.veto_reason and "LLM_AUDIT_FAILED" in rec_fail.verdict.veto_reason


def test_openai_400_fallback_to_json_object_and_daily_cache_hit() -> None:
    class _Http400Error(Exception):
        status_code = 400

    fallback_calls: List[dict[str, Any]] = []

    class _FakeBetaCompletions:
        def parse(self, **kwargs: Any) -> Any:
            raise _Http400Error("400 response_format json_schema is not supported")

    class _FakeChatCompletions:
        def create(self, **kwargs: Any) -> Any:
            fallback_calls.append(kwargs)
            content = json.dumps(SAMPLE_RESPONSES["cb_non_revision_reject"], ensure_ascii=False)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

    fake_openai = SimpleNamespace(
        beta=SimpleNamespace(chat=SimpleNamespace(completions=_FakeBetaCompletions())),
        chat=SimpleNamespace(completions=_FakeChatCompletions()),
    )

    client = OpenAICompatibleAuditClient(
        cfg=LLMConfig(
            provider="openai_compatible",
            model="deepseek-chat",
            strict_json_schema=True,
            enable_daily_cache=True,
        ),
        client=fake_openai,
    )
    bundle = _make_cb_bundle(
        notices=[
            NoticeItem(
                pub_date=date(2026, 11, 10),
                title="关于不向下修正“陷阱转债”转股价格的公告",
                snippet="未来6个月至2027-05-10不下修",
                detail_fetched=True,
            )
        ]
    )
    cache: dict[str, AuditVerdict] = {}

    # 第一次调用：beta.parse 报 400 -> 自动回退 chat.completions.create(json_object)
    rec1, from_cache1 = client.audit(bundle, price_at_audit=102.0, cache=cache)
    assert from_cache1 is False
    assert len(fallback_calls) == 1
    assert fallback_calls[0]["response_format"] == {"type": "json_object"}
    assert rec1.verdict.final_action == "REJECT"

    # 同日同 sha256 第二次运行：命中本地缓存，不再调 API
    rec2, from_cache2 = client.audit(bundle, price_at_audit=102.0, cache=cache)
    assert from_cache2 is True
    assert len(fallback_calls) == 1
    assert rec2.verdict.final_action == "REJECT"

    # force_audit=True 时穿透缓存重新调 API
    rec3, from_cache3 = client.audit(bundle, price_at_audit=102.0, cache=cache, force_audit=True)
    assert from_cache3 is False
    assert len(fallback_calls) == 2
