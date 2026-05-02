"""Base LLM client interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.models import LLMConfig


@dataclass
class LLMResponse:
    """Unified LLM response across providers."""
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int = 0
    raw: Dict[str, Any] = field(default_factory=dict)


class BaseLLMClient(ABC):
    """Strategy interface for all LLM providers."""

    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Send a chat completion request and return unified response."""

    def ping(self) -> LLMResponse:
        """Send a tiny request to verify connectivity. Default impl: 'ping'."""
        return self.chat(
            [{"role": "user", "content": "ping"}],
            max_tokens=8,
        )
