"""Exercise ORM model."""
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Exercise(Base, TimestampMixin):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    knowledge_point_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_points.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    question_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)

    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    example_input: Mapped[str] = mapped_column(Text, nullable=False, default="")
    example_output: Mapped[str] = mapped_column(Text, nullable=False, default="")
    hint: Mapped[str] = mapped_column(Text, nullable=False, default="")
    standard_answer: Mapped[str] = mapped_column(Text, nullable=False, default="")
    reference_code: Mapped[str] = mapped_column(Text, nullable=False, default="")
    test_cases: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON array
    explanation: Mapped[str] = mapped_column(Text, nullable=False, default="")
    common_mistakes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    extra: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # JSON

    llm_config_id: Mapped[int | None] = mapped_column(
        ForeignKey("llm_configs.id", ondelete="SET NULL"), nullable=True
    )
    generation_log_id: Mapped[int | None] = mapped_column(
        ForeignKey("generation_logs.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="published", index=True)

    # === Quality scoring (populated by POST /exercises/{id}/score) ===
    score_overall: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    score_detail: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # JSON map
    score_comment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    scored_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    score_llm_config_id: Mapped[int | None] = mapped_column(
        ForeignKey("llm_configs.id", ondelete="SET NULL"), nullable=True
    )

    knowledge_point: Mapped["KnowledgePoint"] = relationship(  # noqa: F821
        back_populates="exercises"
    )

    def __repr__(self) -> str:
        return f"<Exercise id={self.id} {self.title}>"

