"""Phase 8 — verify that LearningSessionService._state_from_row rehydrates
the DailyPlan on every read, so agents see it on every WebSocket message
(not just the first turn)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.curriculum.models import DailyPlan
from app.modules.curriculum.repository import DailyPlanRepository
from app.modules.learning_session.service import LearningSessionService


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine, tables=[User.__table__, DailyPlan.__table__],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _service(db, *, enrollment) -> LearningSessionService:
    """Build a service without invoking __init__ (which wires many repos)."""
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = db

    class _FakeEnrollmentRepo:
        def get_by_id(self, eid):
            return enrollment if eid == enrollment.id else None

    service.enrollment_repo = _FakeEnrollmentRepo()
    service.daily_plan_repo = DailyPlanRepository(db)

    # session_repo is needed by _apply_update; stub a no-op save.
    class _FakeSessionRepo:
        def save(self, session):
            return None
    service.session_repo = _FakeSessionRepo()
    return service


def _fake_row(*, user_id: int, enrollment_id: int, current_activity_order: int = 1):
    return SimpleNamespace(
        session_id="sess-abc",
        user_id=user_id,
        enrollment_id=enrollment_id,
        user_task_id=None,
        task_queue=[],
        current_task_index=0,
        phase="teaching",
        messages=[],
        topic="Everyday Words — Family & Home",
        skill_name="vocabulary",
        activity_type="read",
        user_level=1,
        pre_generated_tasks={},
        task_type="mcq",
        user_submission=None,
        evaluation=None,
        feedback=None,
        understanding_confirmed=False,
        current_activity_order=current_activity_order,
    )


def test_state_from_row_rehydrates_daily_plan_from_db(db_session) -> None:
    user = User(email="learner@example.com", password_hash="x", name="L")
    db_session.add(user)
    db_session.flush()

    enrollment = SimpleNamespace(
        id=7, user_id=user.id,
        current_week=1, current_day_in_week=2,
        course=SimpleNamespace(slug="beginner-24w", duration_weeks=24),
    )
    service = _service(db_session, enrollment=enrollment)

    # Seed a plan in the DB.
    plan_json = {
        "topic_name": "Everyday Words — Family & Home",
        "sub_skill": "vocabulary",
        "sub_level": 1,
        "teacher_instructions": {"learning_goal": "Teach family/home words"},
        "activities": [{"order": i + 1} for i in range(4)],
    }
    service.daily_plan_repo.upsert(
        user_id=user.id, course_slug="beginner-24w", week=1, day=2,
        topic_id="1:2", plan_json=plan_json,
    )

    row = _fake_row(user_id=user.id, enrollment_id=enrollment.id,
                    current_activity_order=3)
    state = service._state_from_row(row)

    assert state["daily_plan"] is not None
    assert state["daily_plan"]["teacher_instructions"]["learning_goal"] == "Teach family/home words"
    assert state["course_slug"] == "beginner-24w"
    assert state["week"] == 1
    assert state["day"] == 2
    assert state["current_activity_order"] == 3


def test_state_from_row_handles_missing_plan_gracefully(db_session) -> None:
    user = User(email="learner@example.com", password_hash="x", name="L")
    db_session.add(user)
    db_session.flush()

    enrollment = SimpleNamespace(
        id=9, user_id=user.id,
        current_week=2, current_day_in_week=4,
        course=SimpleNamespace(slug="beginner-24w", duration_weeks=24),
    )
    service = _service(db_session, enrollment=enrollment)

    row = _fake_row(user_id=user.id, enrollment_id=enrollment.id)
    state = service._state_from_row(row)

    # No plan persisted for (week=2, day=4) → state has no daily_plan.
    assert state.get("daily_plan") is None
    # current_activity_order still defaults to 1.
    assert state["current_activity_order"] == 1


def test_apply_update_persists_current_activity_order(db_session) -> None:
    enrollment = SimpleNamespace(
        id=11, user_id=1,
        current_week=1, current_day_in_week=2,
        course=SimpleNamespace(slug="beginner-24w", duration_weeks=24),
    )
    service = _service(db_session, enrollment=enrollment)

    row = _fake_row(user_id=1, enrollment_id=enrollment.id, current_activity_order=1)
    service._apply_update(row, {"current_activity_order": 3})
    assert row.current_activity_order == 3

    # None values should not zero out the column.
    service._apply_update(row, {"current_activity_order": None})
    assert row.current_activity_order == 3
