"""Integration tests for `POST /api/sessions/start-today`.

Exercises the find-or-create logic by stubbing `_make_session_service` so
the route runs offline (no LLM, no network). Seeds curriculum_v2 data
mirroring `test_session_lifecycle.py`.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401 — populate Base.metadata
from app.core.database import Base, get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.curriculum.v2_models import (
    CurriculumDay,
    CurriculumWeek,
    TaskArchetype,
    ThemeType,
)
from app.modules.preferences.models import UserCoursePreference
from app.modules.progress.models import SkillPoints, SkillPointsLog
from app.modules.sessions import routes as sessions_routes
from app.modules.sessions.models import (
    ActivityAttempt,
    ActivityEvaluation,
    ActivityFeedback,
    DailySession,
    SessionScorecard,
)
from app.modules.sessions.routes import router as sessions_router
from app.modules.sessions.service import SessionService
from app.modules.skills.models import Skill
from app.scoring import SUB_SKILLS
from scripts.seed_curriculum_v2 import seed_archetypes


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            Skill.__table__,
            SkillPoints.__table__,
            SkillPointsLog.__table__,
            CurriculumWeek.__table__,
            CurriculumDay.__table__,
            TaskArchetype.__table__,
            DailySession.__table__,
            ActivityAttempt.__table__,
            ActivityEvaluation.__table__,
            ActivityFeedback.__table__,
            SessionScorecard.__table__,
            UserCoursePreference.__table__,
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        _seed_world(db)
        yield db
    finally:
        db.close()
        engine.dispose()


def _seed_world(db):
    user = User(email="learner@example.com", password_hash="x", name="L")
    db.add(user)
    for sub_skill in SUB_SKILLS:
        db.add(Skill(name=sub_skill, description=sub_skill))
    db.flush()
    seed_archetypes(db)
    week = CurriculumWeek(
        week_id="wk_24_05",
        course_length="24w",
        week_number=5,
        theme_type=ThemeType.GRAMMAR,
        title="What I Did and What I'll Do",
        cefr_level="A2",
        sub_level_min=3,
        sub_level_max=3,
        learning_goal="Past simple + future with will/going to.",
    )
    db.add(week)
    db.flush()
    day = CurriculumDay(
        day_id="day_24_05_03",
        week_id=week.id,
        day_number=3,
        topic="Past negative and questions",
        explanation_brief="didn't + base; did you/she …",
        default_activities=["read", "write", "listen", "speak"],
        mandatory_activities=["read", "write"],
        suggested_archetypes={
            "read":   ["READ_CLOZE", "READ_COMP_MCQ"],
            "write":  ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"],
            "listen": ["LISTEN_CLOZE"],
            "speak":  ["SPEAK_TIMED"],
        },
    )
    db.add(day)
    db.commit()
    return user, day


@pytest.fixture()
def user(db_session):
    return db_session.query(User).first()


@pytest.fixture()
def client(db_session, user, monkeypatch):
    # Patch the LLM-wired service factory so the test runs offline.
    monkeypatch.setattr(
        sessions_routes,
        "_make_session_service",
        lambda db: SessionService(db),
    )

    app = FastAPI()
    app.include_router(sessions_router, prefix="/api")

    def _override_db():
        yield db_session

    def _override_user():
        return user

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _override_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _set_pref(db, user, *, week=5, day=3, course_length="24w", tasks_per_day=2):
    pref = UserCoursePreference(
        user_id=user.id,
        course_length=course_length,
        tasks_per_day=tasks_per_day,
        current_week=week,
        current_day_in_week=day,
    )
    db.add(pref)
    db.commit()
    return pref


class TestStartToday:
    def test_starts_fresh_session_when_none_exists(self, client, db_session, user):
        _set_pref(db_session, user)

        resp = client.post("/api/sessions/start-today")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["day_id"] == "day_24_05_03"
        assert body["course_length"] == "24w"
        assert body["status"] == "in_progress"
        assert body["is_first_attempt"] is True
        assert len(body["attempts"]) >= 1
        # The mandatory activities for this day are read + write.
        archetype_ids = {a["archetype_id"] for a in body["attempts"]}
        # Mandatory slots must be present.
        assert any(a.startswith("READ_") for a in archetype_ids)
        assert any(a.startswith("WRITE_") for a in archetype_ids)

    def test_resumes_in_progress_session_idempotently(self, client, db_session, user):
        _set_pref(db_session, user)

        first = client.post("/api/sessions/start-today").json()
        second = client.post("/api/sessions/start-today").json()
        assert first["session_id"] == second["session_id"]
        assert second["status"] == "in_progress"

    def test_returns_404_when_day_not_in_curriculum(self, client, db_session, user):
        # Lazy-create path: user has no preference row, so the service
        # creates one with defaults (24w, week=1, day=1) — and our seed
        # only has week=5 day=3, so the day lookup misses.
        resp = client.post("/api/sessions/start-today")
        assert resp.status_code == 404
        assert "curriculum" in resp.json()["detail"].lower()

    def test_404_when_preference_week_out_of_range(self, client, db_session, user):
        _set_pref(db_session, user, week=99)

        resp = client.post("/api/sessions/start-today")
        assert resp.status_code == 404
        assert "course_length='24w'" in resp.json()["detail"]
        assert "week=99" in resp.json()["detail"]

    def test_404_when_flag_off(self, client, monkeypatch):
        from app.core.config import settings
        monkeypatch.setattr(settings, "use_new_session_flow", False)
        resp = client.post("/api/sessions/start-today")
        assert resp.status_code == 404
