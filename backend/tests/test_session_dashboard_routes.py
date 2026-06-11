from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401
from app.core.database import Base, get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import Role, User, UserProfile, UserRole
from app.modules.curriculum.models import (
    Course,
    CourseLevel,
    CourseStatus,
    EnrollmentStatus,
    UserEnrollment,
)
from app.modules.curriculum.models import (
    CurriculumDay,
    CurriculumWeek,
    TaskArchetype,
    ThemeType,
)
from app.modules.preferences.models import UserCoursePreference
from app.modules.sessions import routes as sessions_routes
from app.modules.sessions.models import (
    ActivityAttempt,
    AttemptStatus,
    DailySession,
    SessionScorecard,
    SessionStatus,
)
from app.modules.sessions.repository import DailySessionRepository
from app.modules.sessions.service import SessionService
from app.modules.subscriptions.dependencies import require_active_access
from scripts.seed_curriculum import seed_archetypes


@pytest.fixture()
def dashboard_client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            Role.__table__,
            UserRole.__table__,
            UserProfile.__table__,
            Course.__table__,
            UserEnrollment.__table__,
            CurriculumWeek.__table__,
            CurriculumDay.__table__,
            TaskArchetype.__table__,
            UserCoursePreference.__table__,
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
    # Entitlement is covered by test_premium_guard; stub it out here.
    app.dependency_overrides[require_active_access] = lambda: user
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
    db.add(
        UserCoursePreference(
            user_id=user.id,
            course_length="24w",
            tasks_per_day=3,
            allow_read=True,
            allow_write=True,
            allow_listen=True,
            allow_speak=True,
            current_week=5,
            current_day_in_week=3,
            current_day_started_at=datetime.now(timezone.utc),
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
    # day_24_05_03 is file-authored: the preview uses the file archetype order
    # (read → listen → write → speak), not the DB suggested_archetypes.
    assert [a["archetype_id"] for a in body["activities"]] == [
        "READ_COMP_MCQ",
        "LISTEN_DICTATION",
        "WRITE_SENT_TRANS",
        "SPEAK_TIMED",
    ]
    assert body["topic"] == "Future Forms - Will and Going To"
    assert db.query(DailySession).count() == 0


def test_today_plan_uses_file_source_archetypes_when_day_is_authored(dashboard_client):
    client, db, user = dashboard_client
    pref = db.query(UserCoursePreference).filter(UserCoursePreference.user_id == user.id).one()
    pref.current_week = 1
    pref.current_day_in_week = 2
    week = CurriculumWeek(
        week_id="wk_24_01",
        course_length="24w",
        week_number=1,
        theme_type=ThemeType.GRAMMAR,
        title="Foundation grammar",
        cefr_level="A1",
        sub_level_min=1,
        sub_level_max=2,
        learning_goal="Use basic tense patterns.",
    )
    db.add(week)
    db.flush()
    db.add(
        CurriculumDay(
            day_id="day_24_01_02",
            week_id=week.id,
            day_number=2,
            topic="DB fallback topic",
            explanation_brief="DB fallback brief",
            default_activities=["read", "write", "listen", "speak"],
            mandatory_activities=["read", "write"],
            suggested_archetypes={
                "read": ["READ_CLOZE"],
                "write": ["WRITE_OPEN_SENT"],
                "listen": ["LISTEN_MCQ"],
                "speak": ["SPEAK_TIMED"],
            },
        )
    )
    db.commit()

    resp = client.get("/api/sessions/today-plan")

    assert resp.status_code == 200
    body = resp.json()
    assert [a["archetype_id"] for a in body["activities"]] == [
        "READ_ERROR_SPOT",
        "LISTEN_CLOZE",
        "WRITE_ERROR_CORR",
        "SPEAK_READ_ALOUD",
    ]
    assert [a["archetype_name"] for a in body["activities"]] == [
        "Error Spotting",
        "Cloze Listening",
        "Error Correction",
        "Read Aloud",
    ]
    # Topic/CEFR come from the file source, not the stale DB row.
    assert body["topic"] == "Simple Past Tense — Regular and Irregular Verbs"
    assert body["topic"] != "DB fallback topic"
    assert body["cefr_level"] == "A1"
    assert body["course_length"] == "24w"
    assert body["is_depth_day"] is False
    assert db.query(DailySession).count() == 0


def test_today_plan_uses_file_source_depth_topic_for_48w_even_pass(dashboard_client):
    client, db, user = dashboard_client
    pref = db.query(UserCoursePreference).filter(UserCoursePreference.user_id == user.id).one()
    pref.course_length = "48w"
    pref.current_week = 1
    pref.current_day_in_week = 2
    week = CurriculumWeek(
        week_id="wk_48_01",
        course_length="48w",
        week_number=1,
        theme_type=ThemeType.GRAMMAR,
        title="Foundation grammar",
        cefr_level="A1",
        sub_level_min=1,
        sub_level_max=2,
        learning_goal="Use basic tense patterns.",
    )
    db.add(week)
    db.flush()
    db.add(
        CurriculumDay(
            day_id="day_48_01_02",
            week_id=week.id,
            day_number=2,
            topic="DB fallback topic",
            explanation_brief="DB fallback brief",
            default_activities=["read", "write", "listen", "speak"],
            mandatory_activities=["read", "write"],
            suggested_archetypes={
                "read": ["READ_CLOZE"],
                "write": ["WRITE_OPEN_SENT"],
                "listen": ["LISTEN_MCQ"],
                "speak": ["SPEAK_TIMED"],
            },
        )
    )
    db.commit()

    resp = client.get("/api/sessions/today-plan")

    assert resp.status_code == 200
    body = resp.json()
    # 48w even pass (day 2) resolves to the depth day: distinct topic + A2 CEFR.
    assert body["topic"] == "Simple Present — Questions, Negatives & Short Answers"
    assert body["topic"] != "DB fallback topic"
    assert body["cefr_level"] == "A2"
    assert body["course_length"] == "48w"
    assert body["is_depth_day"] is True
    assert db.query(DailySession).count() == 0


def test_today_plan_repairs_stale_unstarted_file_session(dashboard_client):
    client, db, user = dashboard_client
    pref = db.query(UserCoursePreference).filter(UserCoursePreference.user_id == user.id).one()
    pref.current_week = 1
    pref.current_day_in_week = 2
    week = CurriculumWeek(
        week_id="wk_24_01",
        course_length="24w",
        week_number=1,
        theme_type=ThemeType.GRAMMAR,
        title="Foundation grammar",
        cefr_level="A1",
        sub_level_min=1,
        sub_level_max=2,
        learning_goal="Use basic tense patterns.",
    )
    db.add(week)
    db.flush()
    db.add(
        CurriculumDay(
            day_id="day_24_01_02",
            week_id=week.id,
            day_number=2,
            topic="DB fallback topic",
            explanation_brief="DB fallback brief",
            default_activities=["read", "write", "listen", "speak"],
            mandatory_activities=["read", "write"],
            suggested_archetypes={
                "read": ["READ_CLOZE"],
                "write": ["WRITE_OPEN_SENT"],
                "listen": ["LISTEN_MCQ"],
                "speak": ["SPEAK_TIMED"],
            },
        )
    )
    stale = DailySession(
        session_id="stale-day-1-2",
        user_id=user.id,
        day_id="day_24_01_02",
        course_length="24w",
        status=SessionStatus.IN_PROGRESS,
        is_first_attempt=True,
        started_at=datetime.now(timezone.utc),
    )
    db.add(stale)
    db.flush()
    db.add_all(
        [
            ActivityAttempt(
                session_id=stale.id,
                sequence=1,
                archetype_id="READ_CLOZE",
                is_mandatory=True,
                status=AttemptStatus.PENDING,
                task_content={},
            ),
            ActivityAttempt(
                session_id=stale.id,
                sequence=2,
                archetype_id="WRITE_OPEN_SENT",
                is_mandatory=True,
                status=AttemptStatus.PENDING,
                task_content={},
            ),
            ActivityAttempt(
                session_id=stale.id,
                sequence=3,
                archetype_id="LISTEN_MCQ",
                is_mandatory=True,
                status=AttemptStatus.PENDING,
                task_content={},
            ),
            ActivityAttempt(
                session_id=stale.id,
                sequence=4,
                archetype_id="SPEAK_READ_ALOUD",
                is_mandatory=True,
                status=AttemptStatus.PENDING,
                task_content={},
            ),
        ]
    )
    db.commit()

    resp = client.get("/api/sessions/today-plan")

    assert resp.status_code == 200
    body = resp.json()
    assert body["session_id"] is None
    assert body["is_preview"] is True
    assert [a["archetype_name"] for a in body["activities"]] == [
        "Error Spotting",
        "Cloze Listening",
        "Error Correction",
        "Read Aloud",
    ]
    db.refresh(stale)
    assert stale.status is SessionStatus.ABANDONED


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


def test_get_in_progress_dedupes_duplicate_rows(dashboard_client):
    """Duplicate in-progress rows must not break scalar_one_or_none callers."""
    _client, db, user = dashboard_client
    now = datetime.now(timezone.utc)
    older = DailySession(
        session_id="dup-older",
        user_id=user.id,
        day_id="day_24_05_03",
        course_length="24w",
        status=SessionStatus.IN_PROGRESS,
        is_first_attempt=True,
        started_at=now,
    )
    newer = DailySession(
        session_id="dup-newer",
        user_id=user.id,
        day_id="day_24_05_03",
        course_length="24w",
        status=SessionStatus.IN_PROGRESS,
        is_first_attempt=True,
        started_at=now,
    )
    db.add_all([older, newer])
    db.commit()

    repo = DailySessionRepository(db)
    resolved = repo.get_in_progress(user_id=user.id, day_id="day_24_05_03")
    db.commit()

    assert resolved is not None
    assert resolved.session_id == "dup-newer"
    db.refresh(older)
    assert older.status is SessionStatus.ABANDONED
