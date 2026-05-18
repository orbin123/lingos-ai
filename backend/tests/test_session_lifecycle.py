"""End-to-end SessionService lifecycle tests against in-memory SQLite.

Async after Phase 4 — the LLM-driven agents are async, so the whole
SessionService start/submit/complete path is async. Tests inject the
deterministic Stub* agents to keep the suite offline.
"""

from __future__ import annotations

import pytest
import pytest_asyncio  # noqa: F401  — ensures the asyncio plugin is loaded
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Register all models on Base.metadata.
from app import models  # noqa: F401
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.curriculum.v2_models import (
    CurriculumDay,
    CurriculumWeek,
    TaskArchetype,
    ThemeType,
)
from app.modules.progress.models import SkillPoints, SkillPointsLog
from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.exceptions import (
    AttemptAlreadySubmitted,
    SessionAlreadyOpen,
    SessionNotFound,
)
from app.modules.sessions.feedback_generator import StubFeedbackGenerator
from app.modules.sessions.models import (
    ActivityAttempt,
    ActivityEvaluation,
    ActivityFeedback,
    AttemptStatus,
    DailySession,
    SessionScorecard,
    SessionStatus,
)
from app.modules.sessions.service import SessionService
from app.modules.skills.models import Skill
from app.scoring import ARCHETYPE_REGISTRY, CourseLength, SUB_SKILLS
from scripts.seed_curriculum_v2 import seed_archetypes


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
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
    """Seed users, the 7 skills, archetypes, and one curriculum week+day."""
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


def _user_id(db) -> int:
    return db.query(User).first().id


# ── start ──────────────────────────────────────────────────────────


class TestStartSession:
    @pytest.mark.asyncio
    async def test_creates_session_with_mandatory_attempts(self, db_session):
        service = SessionService(db_session, evaluator=StubEvaluator(default_score=7.0))
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_05_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        assert session.status is SessionStatus.IN_PROGRESS
        assert session.is_first_attempt is True
        assert len(session.attempts) == 4
        assert [a.archetype_id for a in session.attempts] == [
            "READ_CLOZE",
            "WRITE_SENT_TRANS",
            "LISTEN_CLOZE",
            "SPEAK_TIMED",
        ]
        assert [a.is_mandatory for a in session.attempts] == [True, True, False, False]

    @pytest.mark.asyncio
    async def test_blocks_second_in_progress_session(self, db_session):
        service = SessionService(db_session)
        await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_05_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write"},
        )
        with pytest.raises(SessionAlreadyOpen):
            await service.start_session(
                user_id=_user_id(db_session),
                day_id="day_24_05_03",
                course_length=CourseLength.WEEKS_24,
                tasks_per_day=2,
                allowed_activities={"read", "write"},
            )

    @pytest.mark.asyncio
    async def test_attempts_carry_stub_task_content(self, db_session):
        service = SessionService(db_session)
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_05_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write"},
        )
        content = session.attempts[0].task_content
        assert content["archetype_id"] == "READ_CLOZE"
        assert content["topic"] == "Past negative and questions"
        assert content["ui_widget"] == ARCHETYPE_REGISTRY["READ_CLOZE"].ui_widget


# ── lifecycle ──────────────────────────────────────────────────────


class TestSessionLifecycle:
    async def _start(self, db, tasks_per_day=4, score=7.0):
        service = SessionService(
            db,
            evaluator=StubEvaluator(default_score=score),
            feedback_generator=StubFeedbackGenerator(),
        )
        session = await service.start_session(
            user_id=_user_id(db),
            day_id="day_24_05_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=tasks_per_day,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        return service, session

    @pytest.mark.asyncio
    async def test_full_happy_path(self, db_session):
        service, session = await self._start(db_session, tasks_per_day=4, score=8.0)

        # Walk through all 4 activities.
        for expected_seq in range(1, 5):
            attempt = service.next_activity(
                session_id=session.session_id, user_id=session.user_id,
            )
            assert attempt.sequence == expected_seq
            attempt, evaluation, feedback = await service.submit_activity(
                session_id=session.session_id,
                user_id=session.user_id,
                sequence=attempt.sequence,
                user_response={"answer": "hello"},
            )
            assert attempt.status is AttemptStatus.EVALUATED
            assert float(evaluation.raw_score) == 8.0
            assert evaluation.base_reward == 55  # 24w Excellent
            assert sum(evaluation.weighted_points.values()) == pytest.approx(55.0)
            assert feedback.score == 8

        # Complete the session.
        scorecard, report = await service.complete_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert report.applied is True
        assert scorecard.points_applied is True
        assert sum(scorecard.points_earned.values()) > 0

        # Session must now be COMPLETED.
        refreshed = service.get_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert refreshed.status is SessionStatus.COMPLETED
        assert refreshed.completed_at is not None

    @pytest.mark.asyncio
    async def test_submit_blocks_resubmit(self, db_session):
        service, session = await self._start(db_session, tasks_per_day=2)
        await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"a": "b"},
        )
        with pytest.raises(AttemptAlreadySubmitted):
            await service.submit_activity(
                session_id=session.session_id,
                user_id=session.user_id,
                sequence=1,
                user_response={"a": "b"},
            )

    @pytest.mark.asyncio
    async def test_complete_is_idempotent(self, db_session):
        service, session = await self._start(db_session, tasks_per_day=2, score=8.0)
        for seq in (1, 2):
            await service.submit_activity(
                session_id=session.session_id,
                user_id=session.user_id,
                sequence=seq,
                user_response={"a": "b"},
            )
        first, report1 = await service.complete_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        second, report2 = await service.complete_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert first.id == second.id
        assert report1.applied is True
        assert report2.applied is False
        assert report2.reason == "session already completed"

    @pytest.mark.asyncio
    async def test_submitted_response_persists_on_attempt(self, db_session):
        service, session = await self._start(db_session, tasks_per_day=2)
        await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"answer": "yes"},
        )
        refreshed = service.get_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert refreshed.attempts[0].user_response == {"answer": "yes"}
        assert refreshed.attempts[0].submitted_at is not None


# ── ownership / not found ──────────────────────────────────────────


class TestOwnership:
    def test_unknown_session_raises_not_found(self, db_session):
        # next_activity is sync (no LLM); a plain sync test is fine.
        service = SessionService(db_session)
        with pytest.raises(SessionNotFound):
            service.next_activity(session_id="does-not-exist", user_id=_user_id(db_session))

    @pytest.mark.asyncio
    async def test_other_users_session_is_invisible(self, db_session):
        service = SessionService(db_session)
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_05_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write"},
        )
        with pytest.raises(SessionNotFound):
            service.next_activity(session_id=session.session_id, user_id=99999)
