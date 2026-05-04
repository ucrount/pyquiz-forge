"""
Lightweight in-process migrations for SQLite.

We don't use Alembic for this MVP — instead, this module checks whether the
schema has columns the current ORM expects, and ALTERs missing columns on
startup. This is idempotent and safe to call repeatedly.

Only ADD COLUMN is supported (SQLite limitation). Drops or renames require
a real migration tool — switch to Alembic if the schema starts changing
in non-additive ways.
"""
from __future__ import annotations

from typing import Iterable

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.core.logger import get_logger

logger = get_logger(__name__)


# Each tuple: (table, column, SQL type clause, default literal or None)
EXPECTED_COLUMNS: list[tuple[str, str, str, str | None]] = [
    # Quality scoring (added 2026-05)
    ("exercises", "score_overall",       "REAL",                          None),
    ("exercises", "score_detail",        "TEXT NOT NULL",                 "'{}'"),
    ("exercises", "score_comment",       "TEXT NOT NULL",                 "''"),
    ("exercises", "scored_at",           "DATETIME",                      None),
    ("exercises", "score_llm_config_id", "INTEGER",                       None),
    # Multi-language (added 2026-05)
    ("chapters",         "language", "VARCHAR(20) NOT NULL", "'python'"),
    ("knowledge_points", "language", "VARCHAR(20) NOT NULL", "'python'"),
    ("exercises",        "language", "VARCHAR(20) NOT NULL", "'python'"),
    # Learning content + mastery (v0.3, added 2026-05)
    ("knowledge_points", "content",            "TEXT NOT NULL",        "''"),
    ("knowledge_points", "mastery",            "VARCHAR(20) NOT NULL", "'not_started'"),
    ("knowledge_points", "mastery_note",       "TEXT NOT NULL",        "''"),
    ("knowledge_points", "mastery_updated_at", "DATETIME",             None),
]


def _existing_columns(engine: Engine, table: str) -> set[str]:
    insp = inspect(engine)
    if table not in insp.get_table_names():
        return set()
    return {c["name"] for c in insp.get_columns(table)}


def ensure_columns(engine: Engine) -> None:
    """Add any missing columns from EXPECTED_COLUMNS via ALTER TABLE."""
    by_table: dict[str, list[tuple[str, str, str | None]]] = {}
    for table, col, type_clause, default in EXPECTED_COLUMNS:
        by_table.setdefault(table, []).append((col, type_clause, default))

    for table, cols in by_table.items():
        existing = _existing_columns(engine, table)
        if not existing:
            # Table doesn't exist yet — Base.metadata.create_all will build it.
            continue

        missing = [(c, t, d) for c, t, d in cols if c not in existing]
        if not missing:
            continue

        logger.info(
            "Schema migration: adding %d missing column(s) on '%s': %s",
            len(missing), table, [c for c, _, _ in missing],
        )
        with engine.begin() as conn:
            for col, type_clause, default in missing:
                sql = f"ALTER TABLE {table} ADD COLUMN {col} {type_clause}"
                if default is not None:
                    sql += f" DEFAULT {default}"
                conn.execute(text(sql))


def list_missing(engine: Engine) -> Iterable[tuple[str, str]]:
    """Diagnostic helper: yield (table, column) for any missing columns."""
    for table, col, _, _ in EXPECTED_COLUMNS:
        if col not in _existing_columns(engine, table):
            yield table, col
