"""Anthropic Claude client.

Differences from the OpenAI Chat Completions API that this adapter handles:
  - `system` is a top-level parameter, not a message role
  - `messages` only contains user/assistant turns
  - Response content is a list of content blocks (`response.content[0].text`)
  - Token fields are `usage.input_tokens` / `usage.output_tokens`
  - `max_tokens` is required (the OpenAI SDK lets it default; Claude doesn't)

Conversion strategy:
  Take the OpenAI-style messages list, split out any `role: system` messages
  and concatenate them into a single `system` string, leaving the rest as a
  user/assistant conversation.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List

import anthropic
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.logger import get_logger
from app.llm.base import BaseLLMClient, LLMResponse

logger = get_logger(__name__)


def _convert_messages(messages: List[Dict[str, str]]) -> tuple[str, List[Dict[str, str]]]:
    """
    Split OpenAI-style messages into (system_text, anthropic_messages).

    Multiple system messages are concatenated with newlines.
    Empty system text is returned as "" (anthropic SDK accepts that).
    Non-system messages keep their role/content shape.
    """
    system_parts: List[str] = []
    convo: List[Dict[str, str]] = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "system":
            if content:
                system_parts.append(str(content))
        elif role in ("user", "assistant"):
            convo.append({"role": role, "content": str(content)})
        else:
            # Fall back: treat unknown roles as user input.
            convo.append({"role": "user", "content": str(content)})

    # Anthropic requires at least one user message — guarantee that.
    if not convo:
        convo = [{"role": "user", "content": ""}]

    return "\n\n".join(system_parts), convo


class ClaudeClient(BaseLLMClient):
    """Anthropic-style provider, used when LLMConfig.provider == 'claude'."""

    def _client(self) -> anthropic.Anthropic:
        kwargs: Dict[str, Any] = {"api_key": self.config.api_key}
        if self.config.api_base:
            # Strip a trailing /v1 if the user copied it from the OpenAI side —
            # the SDK adds the version itself.
            base = self.config.api_base.rstrip("/")
            if base.endswith("/v1"):
                base = base[:-3]
            kwargs["base_url"] = base
        return anthropic.Anthropic(**kwargs, timeout=60.0)

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
        system_text, convo = _convert_messages(messages)

        # Build kwargs — system is omitted entirely if empty (cleaner API call).
        create_kwargs: Dict[str, Any] = {
            "model": self.config.model,
            "messages": convo,
            "max_tokens": max_tokens if max_tokens is not None else self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
        }
        if system_text:
            create_kwargs["system"] = system_text

        t0 = time.perf_counter()
        try:
            resp = client.messages.create(**create_kwargs)
        except Exception as e:
            logger.error("Claude call failed: %s", e)
            raise

        latency_ms = int((time.perf_counter() - t0) * 1000)

        # Extract text from content blocks. Tool-use blocks are skipped — we
        # only ask for text JSON output, but be defensive about future shapes.
        text_parts: List[str] = []
        for block in (resp.content or []):
            block_type = getattr(block, "type", None)
            if block_type == "text":
                text_parts.append(getattr(block, "text", "") or "")
        content = "".join(text_parts)

        usage = getattr(resp, "usage", None)
        prompt_tokens = getattr(usage, "input_tokens", 0) if usage else 0
        completion_tokens = getattr(usage, "output_tokens", 0) if usage else 0

        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            raw=resp.model_dump() if hasattr(resp, "model_dump") else {},
        )
