"""KnowledgePoint ORM model."""
from typing import List

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chapter_id: Mapped[int] = mapped_column(
        ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    keywords: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON array as text
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    chapter: Mapped["Chapter"] = relationship(back_populates="knowledge_points")  # noqa: F821
    exercises: Mapped[List["Exercise"]] = relationship(  # noqa: F821
        back_populates="knowledge_point",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<KnowledgePoint {self.code} {self.title}>"
