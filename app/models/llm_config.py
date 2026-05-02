"""LLMConfig ORM model."""
from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class LLMConfig(Base, TimestampMixin):
    __tablename__ = "llm_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    api_key: Mapped[str] = mapped_column(Text, nullable=False)
    api_base: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=2048)
    extra: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # JSON
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return f"<LLMConfig {self.name} provider={self.provider} model={self.model}>"
