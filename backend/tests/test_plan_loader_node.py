"""Tests for plan_loader_node — generates on first run, loads from DB after."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401  (ensure all models register on Base)
from app.ai.graphs import nodes as nodes_module
from app.ai.graphs.nodes import plan_loader_node
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.curriculum.models import DailyPlan
from app.modules.curriculum.topics import CourseTopic


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
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


def _make_user(db) -> User:
    user = User(email="learner@example.com", password_hash="x", name="Learner")
    db.add(user)
    db.flush()
    return user


def _patch_enrollment(monkeypatch, *, user_id: int) -> SimpleNamespace:
    """Stub UserEnrollmentRepository.get_by_id to return a fake enrollment.

    Avoids needing to create user_enrollments + courses tables in SQLite.
    """
    fake_enrollment = SimpleNamespace(
        id=7,
        user_id=user_id,
        current_week=1,
        current_day_in_week=2,
        course=SimpleNamespace(slug="beginner-24w", duration_weeks=24),
    )

    class FakeEnrollmentRepo:
        def __init__(self, db):
            self.db = db

        def get_by_id(self, enrollment_id):
            assert enrollment_id == fake_enrollment.id
            return fake_enrollment

    monkeypatch.setattr(nodes_module, "UserEnrollmentRepository", FakeEnrollmentRepo)
    return fake_enrollment


def _patch_topic(monkeypatch) -> CourseTopic:
    topic = CourseTopic(
        week=1, day=2, topic_id="1:2", sub_skill="vocabulary",
        sub_level=1,
        communication_goal="talk about the people around you",
        language_focus="everyday vocabulary: people and places",
    )
    monkeypatch.setattr(
        nodes_module, "get_course_topic",
        lambda *, duration_weeks, week, day: topic,
    )
    return topic


def test_plan_loader_generates_persists_and_then_loads_from_db(
    db_session, monkeypatch
) -> None:
    user = _make_user(db_session)
    enrollment = _patch_enrollment(monkeypatch, user_id=user.id)
    _patch_topic(monkeypatch)

    call_count = {"n": 0}

    async def fake_generate(*, user_id, course_slug, topic_entry, learner_profile):
        call_count["n"] += 1
        return {
            "user_id": user_id,
            "course_slug": course_slug,
            "week": topic_entry.week,
            "day": topic_entry.day,
            "topic_id": topic_entry.topic_id,
            "topic_name": topic_entry.display_label,
            "sub_skill": topic_entry.sub_skill,
            "sub_level": topic_entry.sub_level,
            "generated_at": "2026-05-13T00:00:00+00:00",
            "teacher_instructions": {"learning_goal": "teach family words"},
            "activities": [{"order": i + 1} for i in range(4)],
        }

    monkeypatch.setattr(nodes_module, "generate_daily_plan", fake_generate)

    state = {
        "user_id": user.id,
        "enrollment_id": enrollment.id,
        "learner_profile": {},
    }

    # 1st run: no plan in DB → generate + persist
    update_1 = asyncio.run(plan_loader_node(state, db=db_session))
    assert call_count["n"] == 1
    assert update_1["daily_plan"]["teacher_instructions"]["learning_goal"] == "teach family words"
    assert update_1["current_activity_order"] == 1
    assert update_1["course_slug"] == "beginner-24w"
    assert update_1["week"] == 1
    assert update_1["day"] == 2

    rows = db_session.query(DailyPlan).all()
    assert len(rows) == 1
    assert rows[0].plan_json["teacher_instructions"]["learning_goal"] == "teach family words"

    # 2nd run: plan exists → load from DB, do NOT call the Planner again
    update_2 = asyncio.run(plan_loader_node(state, db=db_session))
    assert call_count["n"] == 1
    assert update_2["daily_plan"]["teacher_instructions"]["learning_goal"] == "teach family words"
    assert update_2["current_activity_order"] == 1


def test_plan_loader_requires_user_and_enrollment(db_session) -> None:
    with pytest.raises(ValueError):
        asyncio.run(plan_loader_node({"user_id": 1}, db=db_session))
    with pytest.raises(ValueError):
        asyncio.run(plan_loader_node({"enrollment_id": 1}, db=db_session))


def test_plan_loader_raises_when_topic_missing(db_session, monkeypatch) -> None:
    user = _make_user(db_session)
    enrollment = _patch_enrollment(monkeypatch, user_id=user.id)
    monkeypatch.setattr(
        nodes_module, "get_course_topic",
        lambda *, duration_weeks, week, day: None,
    )

    async def _should_not_be_called(**kwargs):
        raise AssertionError("generate_daily_plan should not run without a topic")

    monkeypatch.setattr(nodes_module, "generate_daily_plan", _should_not_be_called)

    with pytest.raises(LookupError):
        asyncio.run(plan_loader_node(
            {"user_id": user.id, "enrollment_id": enrollment.id},
            db=db_session,
        ))
