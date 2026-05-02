"""Claude (Anthropic) client. Reserved — to be implemented in V2."""
from __future__ import annotations

from typing import Dict, List

from app.llm.base import BaseLLMClient, LLMResponse


class ClaudeClient(BaseLLMClient):
    """
    Placeholder for Anthropic Claude API.

    The Claude API differs from OpenAI in several ways:
      - `system` is a top-level field, not a message role
      - messages contain only user/assistant turns
      - response shape differs (`content[0].text`, `usage.input_tokens`, etc.)

    To implement: install `anthropic`, instantiate with api_key + base_url,
    map messages, then translate the response to LLMResponse.
    """

    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        raise NotImplementedError(
            "Claude provider is reserved but not yet implemented. "
            "Use an OpenAI-compatible provider for now."
        )
