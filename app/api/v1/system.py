"""System endpoints: health, version."""
from fastapi import APIRouter

from app import __version__

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/version")
def version() -> dict:
    return {"name": "pyquiz-forge", "version": __version__}
