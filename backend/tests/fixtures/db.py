"""Shared in-memory SQLite engine + session fixtures.

One `db_session` for the whole suite, replacing the ~37 hand-rolled
`create_engine(...)` + curated `tables=[...]` copies. Phase 0's JSONB→variant
fix made the *whole-schema* `Base.metadata.create_all()` render on SQLite, so
no test needs to curate a table subset anymore.

`StaticPool` + `check_same_thread=False` keep the single in-memory DB alive
across connections — required so a FastAPI `TestClient` request thread sees the
same schema/data the test set up (see `tests.fixtures.client`).
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import the model registry so EVERY table registers on Base.metadata before
# create_all runs. Without this, cross-module tables are missing on SQLite.
from app import models  # noqa: F401
from app.core.database import Base


@pytest.fixture
def db_engine():
    """A fresh in-memory SQLite engine with the entire schema created."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """A SQLAlchemy session bound to the fresh in-memory schema.

    `expire_on_commit=False` so objects stay usable after `commit()` (tests
    routinely assert on a row right after committing it). `autoflush=False`
    mirrors the app's `SessionLocal`.
    """
    SessionLocal = sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
