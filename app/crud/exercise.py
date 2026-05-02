"""Exercise CRUD."""
import json
from typing import List, Optional, Tuple

from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session

from app.models import Exercise
from app.schemas.exercise import ExerciseUpdate


def create_exercise(
    db: Session,
    *,
    title: str,
    knowledge_point_id: int,
    difficulty: str,
    question_type: str,
    language: str = "python",
    description: str = "",
    example_input: str = "",
    example_output: str = "",
    hint: str = "",
    standard_answer: str = "",
    reference_code: str = "",
    test_cases: list | None = None,
    explanation: str = "",
    common_mistakes: str = "",
    extra: dict | None = None,
    llm_config_id: int | None = None,
    generation_log_id: int | None = None,
    status: str = "published",
) -> Exercise:
    obj = Exercise(
        title=title,
        knowledge_point_id=knowledge_point_id,
        language=language,
        difficulty=difficulty,
        question_type=question_type,
        description=description,
        example_input=example_input,
        example_output=example_output,
        hint=hint,
        standard_answer=standard_answer,
        reference_code=reference_code,
        test_cases=json.dumps(test_cases or [], ensure_ascii=False),
        explanation=explanation,
        common_mistakes=common_mistakes,
        extra=json.dumps(extra or {}, ensure_ascii=False),
        llm_config_id=llm_config_id,
        generation_log_id=generation_log_id,
        status=status,
    )
    db.add(obj)
    db.flush()
    return obj


def get_exercise(db: Session, exercise_id: int) -> Optional[Exercise]:
    return db.get(Exercise, exercise_id)


def list_exercises(
    db: Session,
    *,
    knowledge_point_id: Optional[int] = None,
    language: Optional[str] = None,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    page: int = 1,
    size: int = 20,
) -> Tuple[List[Exercise], int]:
    stmt = select(Exercise)
    count_stmt = select(func.count(Exercise.id))

    filters = []
    if knowledge_point_id is not None:
        filters.append(Exercise.knowledge_point_id == knowledge_point_id)
    if language:
        filters.append(Exercise.language == language)
    if difficulty:
        filters.append(Exercise.difficulty == difficulty)
    if question_type:
        filters.append(Exercise.question_type == question_type)
    if status:
        filters.append(Exercise.status == status)
    if min_score is not None:
        filters.append(Exercise.score_overall >= min_score)

    for f in filters:
        stmt = stmt.where(f)
        count_stmt = count_stmt.where(f)

    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Exercise.id.desc()).offset((page - 1) * size).limit(size)
    items = list(db.execute(stmt).scalars().all())
    return items, total


def list_exercises_for_export(
    db: Session,
    *,
    knowledge_point_id: Optional[int] = None,
    language: Optional[str] = None,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    status: Optional[str] = None,
    min_score: Optional[float] = None,
) -> List[Exercise]:
    stmt = select(Exercise)
    if knowledge_point_id is not None:
        stmt = stmt.where(Exercise.knowledge_point_id == knowledge_point_id)
    if language:
        stmt = stmt.where(Exercise.language == language)
    if difficulty:
        stmt = stmt.where(Exercise.difficulty == difficulty)
    if question_type:
        stmt = stmt.where(Exercise.question_type == question_type)
    if status:
        stmt = stmt.where(Exercise.status == status)
    if min_score is not None:
        stmt = stmt.where(Exercise.score_overall >= min_score)
    stmt = stmt.order_by(Exercise.knowledge_point_id, Exercise.difficulty, Exercise.id)
    return list(db.execute(stmt).scalars().all())


def update_exercise(db: Session, obj: Exercise, data: ExerciseUpdate) -> Exercise:
    payload = data.model_dump(exclude_unset=True)
    if "test_cases" in payload and payload["test_cases"] is not None:
        payload["test_cases"] = json.dumps(
            [tc if isinstance(tc, dict) else tc.model_dump() for tc in payload["test_cases"]],
            ensure_ascii=False,
        )
    if "extra" in payload and payload["extra"] is not None:
        payload["extra"] = json.dumps(payload["extra"], ensure_ascii=False)
    if "status" in payload and payload["status"] is not None:
        payload["status"] = payload["status"].value
    for k, v in payload.items():
        setattr(obj, k, v)
    db.flush()
    return obj


def delete_exercise(db: Session, obj: Exercise) -> None:
    db.delete(obj)
    db.flush()


def bulk_delete_exercises(db: Session, ids: List[int]) -> int:
    if not ids:
        return 0
    result = db.execute(delete(Exercise).where(Exercise.id.in_(ids)))
    db.flush()
    return result.rowcount or 0
