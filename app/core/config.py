"""Application settings loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic settings, populated from .env and environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "pyquiz-forge"
    app_env: str = "production"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"

    # DB
    database_url: str = "sqlite:///./data/pyquiz.db"

    # CORS
    cors_origins: str = "*"

    # Default LLM (used by seed_service if no config exists yet)
    default_llm_provider: str = "deepseek"
    default_llm_api_key: str = ""
    default_llm_api_base: str = "https://api.deepseek.com/v1"
    default_llm_model: str = "deepseek-chat"
    default_llm_temperature: float = 0.7
    default_llm_max_tokens: int = 2048

    # Code sandbox (Piston)
    piston_api_base: str = "https://emkc.org/api/v2/piston"
    piston_run_timeout_ms: int = 5000  # max runtime per test case
    piston_compile_timeout_ms: int = 10000

    @property
    def cors_origin_list(self) -> List[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @field_validator("default_llm_temperature")
    @classmethod
    def _validate_temp(cls, v: float) -> float:
        if not 0.0 <= v <= 2.0:
            raise ValueError("temperature must be between 0 and 2")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
