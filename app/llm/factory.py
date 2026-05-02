"""LLM client factory."""
from __future__ import annotations

from app.llm.base import BaseLLMClient
from app.llm.claude import ClaudeClient
from app.llm.openai_compatible import OpenAICompatibleClient
from app.models import LLMConfig

# Provider name -> client class. Most are OpenAI-compatible; only Claude differs.
PROVIDER_MAP: dict[str, type[BaseLLMClient]] = {
    "openai": OpenAICompatibleClient,
    "deepseek": OpenAICompatibleClient,
    "qwen": OpenAICompatibleClient,
    "moonshot": OpenAICompatibleClient,
    "claude": ClaudeClient,
}


def build_llm_client(config: LLMConfig) -> BaseLLMClient:
    """Construct an LLM client according to provider field."""
    provider = (config.provider or "").lower()
    cls = PROVIDER_MAP.get(provider)
    if cls is None:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported: {sorted(PROVIDER_MAP.keys())}"
        )
    return cls(config)
