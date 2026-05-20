from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401
from app.core.config import settings
from app.core.database import Base, get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.curriculum.models import (
    Course,
    CourseLevel,
    CourseStatus,
    EnrollmentStatus,
    UserEnrollment,
)
from app.modules.curriculum.v2_models import (
    CurriculumDay,
    CurriculumWeek,
    TaskArchetype,
    ThemeType,
)
from app.modules.sessions import routes as sessions_routes
from app.modules.sessions.models import (
    ActivityAttempt,
    AttemptStatus,
    DailySession,
    SessionScorecard,
    SessionStatus,
)
from app.modules.sessions.service import SessionService
from scripts.seed_curriculum_v2 import seed_archetypes


@pytest.fixture()
def dashboard_client(monkeypatch):
    monkeypatch.setattr(settings, "use_new_session_flow", True)

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            Course.__table__,
            UserEnrollment.__table__,
            CurriculumWeek.__table__,
            CurriculumDay.__table__,
            TaskArchetype.__table__,
            DailySession.__table__,
            ActivityAttempt.__table__,
            SessionScorecard.__table__,
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    user = _seed_world(db)

    app = FastAPI()
    app.include_router(sessions_routes.router, prefix="/api")

    def override_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: user
    monkeypatch.setattr(
        sessions_routes,
        "_make_session_service",
        lambda route_db: SessionService(route_db),
    )

    try:
        yield TestClient(app), db, user
    finally:
        db.close()
        engine.dispose()


def _seed_world(db):
    user = User(email="learner@example.com", password_hash="x", name="Learner")
    course = Course(
        slug="beginner-24w",
        title="Beginner English",
        description="",
        duration_weeks=24,
        target_level=CourseLevel.BEGINNER,
        status=CourseStatus.ACTIVE,
    )
    db.add_all([user, course])
    db.flush()
    db.add(
        UserEnrollment(
            user_id=user.id,
            course_id=course.id,
            current_week=5,
            current_day_in_week=3,
            tasks_per_day=3,
            allow_reading=True,
            allow_writing=True,
            allow_listening=True,
            allow_speaking=True,
            current_day_started_at=datetime.now(timezone.utc),
            status=EnrollmentStatus.ACTIVE,
            started_at=datetime.now(timezone.utc),
        )
    )
    seed_archetypes(db)
    week = CurriculumWeek(
        week_id="wk_24_05",
        course_length="24w",
        week_number=5,
        theme_type=ThemeType.GRAMMAR,
        title="Past and future",
        cefr_level="A2",
        sub_level_min=3,
        sub_level_max=3,
        learning_goal="Use past negatives and questions.",
    )
    db.add(week)
    db.flush()
    db.add(
        CurriculumDay(
            day_id="day_24_05_03",
            week_id=week.id,
            day_number=3,
            topic="Past negative and questions",
            explanation_brief="didn't + base; did you/she ...",
            default_activities=["read", "write", "listen", "speak"],
            mandatory_activities=["read", "write"],
            suggested_archetypes={
                "read": ["READ_CLOZE"],
                "write": ["WRITE_SENT_TRANS"],
                "listen": ["LISTEN_CLOZE"],
                "speak": ["SPEAK_TIMED"],
            },
        )
    )
    db.commit()
    return user


def test_today_plan_previews_without_creating_session(dashboard_client):
    client, db, _user = dashboard_client

    resp = client.get("/api/sessions/today-plan")

    assert resp.status_code == 200
    body = resp.json()
    assert body["day_id"] == "day_24_05_03"
    assert body["session_id"] is None
    assert body["is_preview"] is True
    assert [a["archetype_id"] for a in body["activities"]] == [
        "READ_CLOZE",
        "WRITE_SENT_TRANS",
        "LISTEN_CLOZE",
    ]
    assert db.query(DailySession).count() == 0


def test_today_plan_returns_existing_in_progress_session(dashboard_client):
    client, db, user = dashboard_client
    session = _create_session(db, user.id, SessionStatus.IN_PROGRESS)

    resp = client.get("/api/sessions/today-plan")

    assert resp.status_code == 200
    body = resp.json()
    assert body["session_id"] == session.session_id
    assert body["status"] == "in_progress"
    assert body["is_preview"] is False
    assert body["activities"][0]["status"] == "evaluated"
    assert body["activities"][1]["status"] == "pending"


def test_start_or_continue_creates_once_then_continues(dashboard_client):
    client, db, _user = dashboard_client

    first = client.post("/api/sessions/today/start-or-continue")
    second = client.post("/api/sessions/today/start-or-continue")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["mode"] == "start"
    assert second.json()["mode"] == "continue"
    assert first.json()["session_id"] == second.json()["session_id"]
    assert db.query(DailySession).count() == 1


def test_start_or_continue_does_not_create_after_completed(dashboard_client):
    client, db, user = dashboard_client
    session = _create_session(db, user.id, SessionStatus.COMPLETED)

    resp = client.post("/api/sessions/today/start-or-continue")

    assert resp.status_code == 200
    body = resp.json()
    assert body["mode"] == "completed"
    assert body["session_id"] == session.session_id
    assert db.query(DailySession).count() == 1


def _create_session(db, user_id: int, status: SessionStatus) -> DailySession:
    session = DailySession(
        session_id=f"session-{status.value}",
        user_id=user_id,
        day_id="day_24_05_03",
        course_length="24w",
        status=status,
        is_first_attempt=True,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc)
        if status is SessionStatus.COMPLETED
        else None,
    )
    db.add(session)
    db.flush()
    db.add_all(
        [
            ActivityAttempt(
                session_id=session.id,
                sequence=1,
                archetype_id="READ_CLOZE",
                is_mandatory=True,
                status=AttemptStatus.EVALUATED,
                task_content={},
            ),
            ActivityAttempt(
                session_id=session.id,
                sequence=2,
                archetype_id="WRITE_SENT_TRANS",
                is_mandatory=True,
                status=AttemptStatus.PENDING,
                task_content={},
            ),
        ]
    )
    db.commit()
    db.refresh(session)
    return session
