"""OpenAI-compatible client. Covers OpenAI, DeepSeek, Qwen, Moonshot, etc."""
from __future__ import annotations

import time
from typing import Dict, List

from openai import OpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.logger import get_logger
from app.llm.base import BaseLLMClient, LLMResponse

logger = get_logger(__name__)


class OpenAICompatibleClient(BaseLLMClient):
    """Works with any provider that exposes the OpenAI Chat Completions API."""

    def _client(self) -> OpenAI:
        kwargs = {"api_key": self.config.api_key}
        if self.config.api_base:
            kwargs["base_url"] = self.config.api_base
        return OpenAI(**kwargs, timeout=60.0)

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
    )
    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        client = self._client()
        t0 = time.perf_counter()
        try:
            resp = client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=(
                    self.config.temperature if temperature is None else temperature
                ),
                max_tokens=(
                    self.config.max_tokens if max_tokens is None else max_tokens
                ),
            )
        except Exception as e:
            logger.error("LLM call failed: %s", e)
            raise

        latency_ms = int((time.perf_counter() - t0) * 1000)

        content = ""
        if resp.choices and resp.choices[0].message:
            content = resp.choices[0].message.content or ""

        prompt_tokens = getattr(resp.usage, "prompt_tokens", 0) if resp.usage else 0
        completion_tokens = (
            getattr(resp.usage, "completion_tokens", 0) if resp.usage else 0
        )

        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            raw=resp.model_dump() if hasattr(resp, "model_dump") else {},
        )
