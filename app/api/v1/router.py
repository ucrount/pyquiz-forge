"""Aggregate v1 routers."""
from fastapi import APIRouter

from app.api.v1 import (
    exercise,
    export,
    generation,
    learning_path,
    llm_config,
    practice,
    sandbox,
    scoring,
    system,
)

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(learning_path.router)
api_router.include_router(llm_config.router)
api_router.include_router(generation.router)
api_router.include_router(scoring.router)
api_router.include_router(exercise.router)
api_router.include_router(practice.router)
api_router.include_router(export.router)
api_router.include_router(sandbox.router)
