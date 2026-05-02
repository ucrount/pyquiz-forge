"""Learning path endpoints: chapters, knowledge points (CRUD)."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import chapter as crud_chapter
from app.crud import knowledge_point as crud_kp
from app.schemas.chapter import (
    ChapterCreate,
    ChapterRead,
    ChapterUpdate,
    ChapterWithKnowledgePoints,
)
from app.schemas.knowledge_point import (
    KnowledgePointCreate,
    KnowledgePointRead,
    KnowledgePointUpdate,
)

router = APIRouter(tags=["learning-path"])


# ========================================================================
# Read endpoints
# ========================================================================


@router.get("/learning-path", response_model=List[ChapterWithKnowledgePoints])
def get_learning_path(
    language: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Full learning path tree: chapters + knowledge points (filterable by language)."""
    return crud_chapter.list_chapters_with_kps(db, language=language)


@router.get("/chapters", response_model=List[ChapterRead])
def list_chapters(
    language: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud_chapter.list_chapters(db, language=language)


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
    chapter_id: Optional[int] = None,
    language: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud_kp.list_kps(db, chapter_id=chapter_id, language=language)


@router.get("/knowledge-points/{kp_id}", response_model=KnowledgePointRead)
def get_kp(kp_id: int, db: Session = Depends(get_db)):
    kp = crud_kp.get_kp(db, kp_id)
    if kp is None:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    return kp


# ========================================================================
# Chapter mutations
# ========================================================================


@router.post("/chapters", response_model=ChapterRead, status_code=201)
def create_chapter(data: ChapterCreate, db: Session = Depends(get_db)):
    if crud_chapter.get_chapter_by_code(db, data.code):
        raise HTTPException(
            status_code=400, detail=f"Chapter code '{data.code}' already exists"
        )
    chapter = crud_chapter.create_from_schema(db, data)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.put("/chapters/{chapter_id}", response_model=ChapterRead)
def update_chapter(
    chapter_id: int, data: ChapterUpdate, db: Session = Depends(get_db)
):
    chapter = crud_chapter.get_chapter(db, chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    if data.code and data.code != chapter.code:
        if crud_chapter.get_chapter_by_code(db, data.code):
            raise HTTPException(
                status_code=400, detail=f"Chapter code '{data.code}' already exists"
            )
    chapter = crud_chapter.update_chapter(db, chapter, data)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.get("/chapters/{chapter_id}/cascade-info")
def chapter_cascade_info(chapter_id: int, db: Session = Depends(get_db)):
    """Counts of dependent rows that would be deleted along with this chapter."""
    chapter = crud_chapter.get_chapter(db, chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    kp_count = crud_chapter.count_kps_in_chapter(db, chapter_id)
    # Sum exercises across all KPs of this chapter
    kps = crud_kp.list_kps(db, chapter_id=chapter_id)
    exercise_count = sum(
        crud_kp.count_exercises_for_kp(db, kp.id) for kp in kps
    )
    return {
        "chapter_id": chapter_id,
        "knowledge_points": kp_count,
        "exercises": exercise_count,
    }


@router.delete("/chapters/{chapter_id}", status_code=204)
def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = crud_chapter.get_chapter(db, chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    crud_chapter.delete_chapter(db, chapter)
    db.commit()
    return None


# ========================================================================
# KnowledgePoint mutations
# ========================================================================


@router.post("/knowledge-points", response_model=KnowledgePointRead, status_code=201)
def create_kp_endpoint(
    data: KnowledgePointCreate, db: Session = Depends(get_db)
):
    chapter = crud_chapter.get_chapter(db, data.chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    if crud_kp.get_kp_by_code(db, data.code):
        raise HTTPException(
            status_code=400, detail=f"Knowledge point code '{data.code}' already exists"
        )
    kp = crud_kp.create_from_schema(db, data)
    db.commit()
    db.refresh(kp)
    return kp


@router.put("/knowledge-points/{kp_id}", response_model=KnowledgePointRead)
def update_kp(
    kp_id: int, data: KnowledgePointUpdate, db: Session = Depends(get_db)
):
    kp = crud_kp.get_kp(db, kp_id)
    if kp is None:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    if data.code and data.code != kp.code:
        if crud_kp.get_kp_by_code(db, data.code):
            raise HTTPException(
                status_code=400,
                detail=f"Knowledge point code '{data.code}' already exists",
            )
    if data.chapter_id and data.chapter_id != kp.chapter_id:
        if crud_chapter.get_chapter(db, data.chapter_id) is None:
            raise HTTPException(
                status_code=400, detail=f"Chapter {data.chapter_id} not found"
            )
    kp = crud_kp.update_kp(db, kp, data)
    db.commit()
    db.refresh(kp)
    return kp


@router.get("/knowledge-points/{kp_id}/cascade-info")
def kp_cascade_info(kp_id: int, db: Session = Depends(get_db)):
    """Count of exercises that would be deleted along with this KP."""
    kp = crud_kp.get_kp(db, kp_id)
    if kp is None:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    return {
        "knowledge_point_id": kp_id,
        "exercises": crud_kp.count_exercises_for_kp(db, kp_id),
    }


@router.delete("/knowledge-points/{kp_id}", status_code=204)
def delete_kp_endpoint(kp_id: int, db: Session = Depends(get_db)):
    kp = crud_kp.get_kp(db, kp_id)
    if kp is None:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    crud_kp.delete_kp(db, kp)
    db.commit()
    return None


# ========================================================================
# Helpers used by frontend dialogs
# ========================================================================


@router.get("/learning-path/next-order")
def next_order_index(
    language: str,
    chapter_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Suggest the next order_index for a new chapter (chapter_id=None) or a new
    knowledge point under a chapter (chapter_id given).
    """
    if chapter_id is None:
        return {
            "next": crud_chapter.max_order_index_for_language(db, language) + 1
        }
    chapter = crud_chapter.get_chapter(db, chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return {
        "next": crud_kp.max_order_index_in_chapter(db, chapter_id) + 1
    }
