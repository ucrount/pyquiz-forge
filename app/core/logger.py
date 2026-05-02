"""Logging setup: stdout + rotating file."""
from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

from app.core.config import settings

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def setup_logging() -> None:
    """Configure root logger. Idempotent."""
    root = logging.getLogger()
    if root.handlers:
        return

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # stdout
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(fmt)
    root.addHandler(stream)

    # rotating file
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    # quiet down noisy libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
