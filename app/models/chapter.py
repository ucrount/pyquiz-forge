"""Chapter ORM model."""
from typing import List

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    language: Mapped[str] = mapped_column(
        String(20), nullable=False, default="python", index=True
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    knowledge_points: Mapped[List["KnowledgePoint"]] = relationship(  # noqa: F821
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="KnowledgePoint.order_index",
    )

    def __repr__(self) -> str:
        return f"<Chapter {self.language}/{self.code} {self.title}>"
