"""KnowledgePoint ORM model."""
from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chapter_id: Mapped[int] = mapped_column(
        ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    language: Mapped[str] = mapped_column(
        String(20), nullable=False, default="python", index=True
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    keywords: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON array as text
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # ── Learning content + mastery (added in v0.3) ──
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    mastery: Mapped[str] = mapped_column(
        String(20), nullable=False, default="not_started", index=True
    )
    mastery_note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    mastery_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    chapter: Mapped["Chapter"] = relationship(back_populates="knowledge_points")  # noqa: F821
    exercises: Mapped[List["Exercise"]] = relationship(  # noqa: F821
        back_populates="knowledge_point",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<KnowledgePoint {self.language}/{self.code} {self.title}>"
