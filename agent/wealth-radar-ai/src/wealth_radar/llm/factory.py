"""按 config/radar.yaml 实例化对应的 LLM 审计客户端。"""

from __future__ import annotations

from wealth_radar.config.loader import AppConfig
from wealth_radar.domain.errors import ConfigValidationError
from wealth_radar.llm.base import BaseAuditLLM
from wealth_radar.llm.gemini_client import GeminiAuditClient
from wealth_radar.llm.openai_client import OpenAICompatibleAuditClient


def create_audit_llm(app_cfg: AppConfig) -> BaseAuditLLM:
    """根据配置路由返回 Gemini 或 OpenAI 兼容审计客户端。"""
    llm_cfg = app_cfg.radar.llm
    if llm_cfg.provider == "gemini":
        if not app_cfg.secrets.gemini_api_key:
            raise ConfigValidationError(
                "已选择 llm.provider='gemini'，但环境变量 GEMINI_API_KEY 为空，请在 .env 中配置。"
            )
        return GeminiAuditClient(cfg=llm_cfg, api_key=app_cfg.secrets.gemini_api_key)

    if llm_cfg.provider == "openai_compatible":
        if not app_cfg.secrets.openai_api_key:
            raise ConfigValidationError(
                "已选择 llm.provider='openai_compatible'，但环境变量 OPENAI_API_KEY 为空，请在 .env 中配置。"
            )
        return OpenAICompatibleAuditClient(
            cfg=llm_cfg,
            api_key=app_cfg.secrets.openai_api_key,
            base_url=app_cfg.effective_openai_base_url,
        )

    raise ConfigValidationError(f"不支持的 LLM provider: {llm_cfg.provider}")
