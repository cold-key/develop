"""OpenAI 兼容接口适配器（支持 json_schema 与 400 自动回退 json_object）。"""

from __future__ import annotations

import json
from typing import Any, Optional

from wealth_radar.config.loader import LLMConfig
from wealth_radar.domain.errors import MissingDependencyError
from wealth_radar.domain.models import AuditVerdict, EvidenceBundle
from wealth_radar.llm.base import BaseAuditLLM


def _is_json_schema_unsupported_400(exc: Exception) -> bool:
    """判断异常是否为第三方 OpenAI 兼容接口（如 DeepSeek）不支持 json_schema 的 400 响应。"""
    status_code = getattr(exc, "status_code", None)
    if status_code == 400:
        return True
    response = getattr(exc, "response", None)
    if response is not None and getattr(response, "status_code", None) == 400:
        return True
    text = str(exc).lower()
    return "400" in text and ("json_schema" in text or "response_format" in text or "invalid" in text)


class OpenAICompatibleAuditClient(BaseAuditLLM):
    """覆盖 OpenAI / DeepSeek / OpenRouter / 本地 vLLM 的兼容审计客户端。"""

    provider_name = "openai_compatible"

    def __init__(
        self,
        cfg: LLMConfig,
        api_key: str = "",
        base_url: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(cfg)
        self._api_key = api_key
        self._base_url = base_url
        self._client = client

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise MissingDependencyError(
                "未安装 openai，请执行 `uv sync` 或 `pip install openai`"
            ) from exc

        kwargs: dict[str, Any] = {
            "api_key": self._api_key,
            "timeout": float(self.cfg.timeout_sec),
        }
        if self._base_url:
            kwargs["base_url"] = self._base_url
        self._client = OpenAI(**kwargs)
        return self._client

    def _call_provider(
        self,
        system_prompt: str,
        user_prompt: str,
        bundle: EvidenceBundle,
    ) -> AuditVerdict | str:
        client = self._get_client()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if self.cfg.strict_json_schema:
            try:
                completion = client.beta.chat.completions.parse(
                    model=self.cfg.model,
                    messages=messages,
                    temperature=self.cfg.temperature,
                    response_format=AuditVerdict,
                )
                msg = completion.choices[0].message
                parsed = getattr(msg, "parsed", None)
                if isinstance(parsed, AuditVerdict):
                    return parsed
                content = getattr(msg, "content", None)
                if content:
                    return str(content)
                raise ValueError("OpenAI structured parse 返回空内容")
            except Exception as exc:
                if not _is_json_schema_unsupported_400(exc):
                    raise
                # 目标接口报 400 不支持 json_schema，优雅回退至 json_object 模式

        schema_json = json.dumps(AuditVerdict.model_json_schema(), ensure_ascii=False, indent=2)
        fallback_user_prompt = (
            f"{user_prompt}\n\n"
            "你必须严格输出符合以下 JSON Schema 的单个 JSON 对象（不要输出任何 Markdown 解释文字）：\n"
            f"{schema_json}"
        )
        completion = client.chat.completions.create(
            model=self.cfg.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": fallback_user_prompt},
            ],
            temperature=self.cfg.temperature,
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("OpenAI json_object 返回空内容")
        return str(content)
