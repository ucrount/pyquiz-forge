"""GenerationLog ORM model."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class GenerationLog(Base):
    __tablename__ = "generation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    llm_config_id: Mapped[int | None] = mapped_column(
        ForeignKey("llm_configs.id", ondelete="SET NULL"), nullable=True
    )
    knowledge_point_id: Mapped[int | None] = mapped_column(
        ForeignKey("knowledge_points.id", ondelete="SET NULL"), nullable=True
    )
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    question_type: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    prompt: Mapped[str] = mapped_column(Text, nullable=False, default="")
    raw_response: Mapped[str] = mapped_column(Text, nullable=False, default="")
    parsed_ok: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
