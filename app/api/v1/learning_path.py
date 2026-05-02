"""Learning path endpoints: chapters, knowledge points."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import chapter as crud_chapter
from app.crud import knowledge_point as crud_kp
from app.schemas.chapter import ChapterRead, ChapterWithKnowledgePoints
from app.schemas.knowledge_point import KnowledgePointRead

router = APIRouter(tags=["learning-path"])


@router.get("/learning-path", response_model=List[ChapterWithKnowledgePoints])
def get_learning_path(db: Session = Depends(get_db)):
    """Full learning path tree: chapters + knowledge points."""
    return crud_chapter.list_chapters_with_kps(db)


@router.get("/chapters", response_model=List[ChapterRead])
def list_chapters(db: Session = Depends(get_db)):
    return crud_chapter.list_chapters(db)


@router.get(
    "/chapters/{chapter_id}/knowledge-points",
    response_model=List[KnowledgePointRead],
)
def list_chapter_kps(chapter_id: int, db: Session = Depends(get_db)):
    chapter = crud_chapter.get_chapter(db, chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return crud_kp.list_kps(db, chapter_id=chapter_id)


@router.get("/knowledge-points", response_model=List[KnowledgePointRead])
def list_kps(
    chapter_id: int | None = None,
    db: Session = Depends(get_db),
):
    return crud_kp.list_kps(db, chapter_id=chapter_id)


@router.get("/knowledge-points/{kp_id}", response_model=KnowledgePointRead)
def get_kp(kp_id: int, db: Session = Depends(get_db)):
    kp = crud_kp.get_kp(db, kp_id)
    if kp is None:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    return kp
