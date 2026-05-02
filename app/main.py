"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.core.logger import get_logger, setup_logging
from app.models import Base
from app.services.seed_service import run_all_seeds

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting %s v%s ...", settings.app_name, __version__)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        run_all_seeds(db)
    finally:
        db.close()
    logger.info("Startup complete. Swagger UI: %s/docs", settings.api_prefix)
    yield
    # Shutdown
    logger.info("Shutting down.")


app = FastAPI(
    title="pyquiz-forge",
    description="Python 练习题自动生成系统 — MVP 后端",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": __version__,
        "docs": "/docs",
        "api": settings.api_prefix,
    }
