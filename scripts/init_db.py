"""Standalone DB initialization + seed script. Used by Docker CMD and dev setup."""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running as `python scripts/init_db.py` from project root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal, engine  # noqa: E402
from app.core.logger import get_logger, setup_logging  # noqa: E402
from app.models import Base  # noqa: E402
from app.services.seed_service import run_all_seeds  # noqa: E402


def main() -> None:
    setup_logging()
    logger = get_logger("init_db")
    logger.info("Creating tables ...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        run_all_seeds(db)
    finally:
        db.close()
    logger.info("Init done.")


if __name__ == "__main__":
    main()
