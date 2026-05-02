"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.core.logger import get_logger, setup_logging
from app.models import Base
from app.services.seed_service import run_all_seeds

setup_logging()
logger = get_logger(__name__)

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_FILE = STATIC_DIR / "index.html"
ASSETS_DIR = STATIC_DIR / "assets"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s ...", settings.app_name, __version__)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        run_all_seeds(db)
    finally:
        db.close()
    if INDEX_FILE.exists():
        logger.info("Frontend bundle detected at %s — serving SPA at /", STATIC_DIR)
    else:
        logger.info(
            "No frontend bundle at %s — backend will respond JSON at /. "
            "Run `npm run build` in frontend/ or build via Docker.",
            STATIC_DIR,
        )
    logger.info("Startup complete. Swagger UI: /docs")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="pyquiz-forge",
    description="Python 练习题自动生成系统 — MVP",
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

# API routes — must be registered before SPA catch-all so they win on /api/*.
app.include_router(api_router, prefix=settings.api_prefix)


# --- Frontend serving ------------------------------------------------------
# When the SPA build is present (app/static/index.html), mount its assets and
# fall back to index.html for any non-API path. Reserved prefixes below are
# always handled by FastAPI itself and never proxied to the SPA.
RESERVED_PREFIXES = ("api", "docs", "redoc", "openapi.json")


if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


# Some files commonly live at SPA root (favicon etc) — serve them directly.
@app.get("/favicon.svg", include_in_schema=False)
def favicon_svg():
    f = STATIC_DIR / "favicon.svg"
    if f.exists():
        return FileResponse(f)
    return JSONResponse({"detail": "not found"}, status_code=404)


@app.get("/favicon.ico", include_in_schema=False)
def favicon_ico():
    f = STATIC_DIR / "favicon.svg"
    if f.exists():
        return FileResponse(f, media_type="image/svg+xml")
    return JSONResponse({"detail": "not found"}, status_code=404)


@app.get("/{full_path:path}", include_in_schema=False)
def spa_catch_all(full_path: str):
    """
    SPA fallback: any GET that wasn't matched by /api, /docs, /redoc,
    /openapi.json or /assets returns index.html so client-side routing
    (e.g. /exercises, /generate) works on hard refresh.
    """
    # If a reserved prefix slipped through, return JSON 404 (don't pretend
    # to serve the SPA for genuinely missing API routes).
    first_seg = full_path.split("/", 1)[0]
    if first_seg in RESERVED_PREFIXES:
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)

    # No frontend bundle — show backend metadata so /docs is discoverable.
    return JSONResponse(
        {
            "name": settings.app_name,
            "version": __version__,
            "docs": "/docs",
            "api": settings.api_prefix,
            "note": "frontend not built. visit /docs for Swagger.",
        }
    )
