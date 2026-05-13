"""Tests for DailyPlanRepository — verify get + upsert behavior and unique constraint."""

from __future__ import annotations

import time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

# Ensure all models are imported so Base.metadata sees them.
from app import models  # noqa: F401
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.curriculum.models import DailyPlan
from app.modules.curriculum.repository import DailyPlanRepository


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    # Only create the tables we touch — Base.metadata.create_all on the full
    # registry fails on SQLite because some unrelated tables use raw JSONB.
    Base.metadata.create_all(
        engine,
        tables=[User.__table__, DailyPlan.__table__],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _make_user(db, *, email: str = "learner@example.com") -> User:
    user = User(email=email, password_hash="x", name="Learner")
    db.add(user)
    db.flush()
    return user


def test_upsert_inserts_when_missing_and_get_returns_it(db_session) -> None:
    user = _make_user(db_session)
    repo = DailyPlanRepository(db_session)

    plan = repo.upsert(
        user_id=user.id,
        course_slug="beginner-24w",
        week=1,
        day=2,
        topic_id="1:2",
        plan_json={"sub_skill": "vocabulary", "activities": []},
    )

    assert plan.id is not None
    assert plan.generated_at is not None

    fetched = repo.get_for_day(
        user_id=user.id, course_slug="beginner-24w", week=1, day=2,
    )
    assert fetched is not None
    assert fetched.id == plan.id
    assert fetched.plan_json == {"sub_skill": "vocabulary", "activities": []}


def test_upsert_replaces_existing_row_without_duplicating(db_session) -> None:
    user = _make_user(db_session)
    repo = DailyPlanRepository(db_session)

    first = repo.upsert(
        user_id=user.id, course_slug="beginner-24w", week=1, day=2,
        topic_id="1:2", plan_json={"version": 1},
    )
    first_generated_at = first.generated_at
    time.sleep(0.01)

    second = repo.upsert(
        user_id=user.id, course_slug="beginner-24w", week=1, day=2,
        topic_id="1:2", plan_json={"version": 2},
    )

    assert second.id == first.id
    assert second.plan_json == {"version": 2}
    assert second.generated_at > first_generated_at

    all_rows = db_session.query(DailyPlan).all()
    assert len(all_rows) == 1


def test_unique_constraint_blocks_raw_duplicate_insert(db_session) -> None:
    user = _make_user(db_session)
    repo = DailyPlanRepository(db_session)

    repo.upsert(
        user_id=user.id, course_slug="beginner-24w", week=1, day=2,
        topic_id="1:2", plan_json={},
    )

    duplicate = DailyPlan(
        user_id=user.id,
        course_slug="beginner-24w",
        week=1,
        day=2,
        topic_id="1:2",
        plan_json={},
        generated_at=__import__("datetime").datetime.utcnow(),
    )
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_get_returns_none_when_no_plan_for_day(db_session) -> None:
    user = _make_user(db_session)
    repo = DailyPlanRepository(db_session)

    assert repo.get_for_day(
        user_id=user.id, course_slug="beginner-24w", week=5, day=3,
    ) is None
