"""Gemini 原生结构化输出适配器（google-genai response_schema）。"""

from __future__ import annotations

from typing import Any, Optional

from wealth_radar.config.loader import LLMConfig
from wealth_radar.domain.errors import MissingDependencyError
from wealth_radar.domain.models import AuditVerdict, EvidenceBundle
from wealth_radar.llm.base import BaseAuditLLM


class GeminiAuditClient(BaseAuditLLM):
    """基于 google-genai 原生 response_schema 的结构化审计客户端。"""

    provider_name = "gemini"

    def __init__(
        self,
        cfg: LLMConfig,
        api_key: str = "",
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(cfg)
        self._api_key = api_key
        self._client = client

    def _get_client_and_types(self) -> tuple[Any, Any]:
        if self._client is not None:
            try:
                from google.genai import types
            except ImportError:
                types = None
            return self._client, types

        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise MissingDependencyError(
                "未安装 google-genai，请执行 `uv sync` 或 `pip install google-genai`"
            ) from exc

        http_options = types.HttpOptions(timeout=self.cfg.timeout_sec * 1000)
        self._client = genai.Client(api_key=self._api_key, http_options=http_options)
        return self._client, types

    def _call_provider(
        self,
        system_prompt: str,
        user_prompt: str,
        bundle: EvidenceBundle,
    ) -> AuditVerdict | str:
        client, types = self._get_client_and_types()
        if types is not None:
            gen_config: Any = types.GenerateContentConfig(
                temperature=self.cfg.temperature,
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=AuditVerdict,
            )
        else:
            # 离线注入 mock client 且本地未安装 google-genai 时的纯字典配置回退
            gen_config = {
                "temperature": self.cfg.temperature,
                "system_instruction": system_prompt,
                "response_mime_type": "application/json",
                "response_schema": AuditVerdict,
            }

        response = client.models.generate_content(
            model=self.cfg.model,
            contents=user_prompt,
            config=gen_config,
        )

        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, AuditVerdict):
            return parsed
        text = getattr(response, "text", None)
        if not text:
            raise ValueError("Gemini 返回空响应文本")
        return str(text)
