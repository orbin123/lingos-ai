"""Pass-mark gating: gate helpers + points-once-after-retry invariant.

The gate itself lives in the chat ``LearningSessionService`` (it decides
whether to advance or offer a retry). These tests cover the deterministic
decision helpers and the underlying reset → re-submit → complete path the gate
relies on, with the offline Stub* agents so the suite stays LLM-free.
"""

from __future__ import annotations

import pytest
import pytest_asyncio  # noqa: F401
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.curriculum.models import (
    CurriculumDay,
    CurriculumWeek,
    TaskArchetype,
    ThemeType,
)
from app.modules.learning_session.service import LearningSessionService
from app.modules.preferences.models import UserCoursePreference
from app.modules.preferences.service import PreferenceService
from app.modules.progress.models import SkillPoints, SkillPointsLog
from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.feedback_generator import StubFeedbackGenerator
from app.modules.sessions.models import (
    ActivityAttempt,
    ActivityEvaluation,
    ActivityFeedback,
    AttemptStatus,
    DailySession,
    SessionScorecard,
)
from app.modules.sessions.service import SessionService
from app.modules.skills.models import Skill
from app.scoring import CourseLength, SUB_SKILLS
from scripts.seed_curriculum import seed_archetypes


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            UserCoursePreference.__table__,
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
        _seed(db)
        yield db
    finally:
        db.close()
        engine.dispose()


def _seed(db):
    db.add(User(email="u@example.com", password_hash="x", name="L"))
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
    db.add(
        CurriculumDay(
            day_id="day_24_05_03",
            week_id=week.id,
            day_number=3,
            topic="Past negative and questions",
            explanation_brief="didn't + base verb",
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


def _user_id(db) -> int:
    return db.query(User).first().id


async def _start_and_submit(db, *, score: float, tasks_per_day: int = 2):
    """Start a day and submit every activity at `score` (no completion)."""
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
    for seq in range(1, tasks_per_day + 1):
        await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=seq,
            user_response={"answer": "x"},
        )
    return service, session.session_id


# ── Gate decision helpers ──────────────────────────────────────────


class TestGateHelpers:
    @pytest.mark.asyncio
    async def test_low_score_fails_threshold_high_score_passes(self, db_session):
        # StubEvaluator default 5.0 → raw_score 5.0 → 50% on the 0–100 gate.
        _, session_id = await _start_and_submit(db_session, score=5.0)
        gate = LearningSessionService(db_session)
        daily = db_session.query(DailySession).filter_by(session_id=session_id).one()
        attempt = next(
            a
            for a in gate.attempts_repo.list_for_session(daily.id)
            if a.status is AttemptStatus.EVALUATED
        )
        assert gate._attempt_passes_gate(attempt, 65) is False  # 50 < 65
        assert gate._attempt_passes_gate(attempt, 40) is True  # 50 >= 40

    @pytest.mark.asyncio
    async def test_error_fallback_note_bypasses_gate(self, db_session):
        _, session_id = await _start_and_submit(db_session, score=3.0)
        gate = LearningSessionService(db_session)
        daily = db_session.query(DailySession).filter_by(session_id=session_id).one()
        attempt = next(
            a
            for a in gate.attempts_repo.list_for_session(daily.id)
            if a.status is AttemptStatus.EVALUATED
        )
        # A genuine 30% is gated...
        assert gate._attempt_passes_gate(attempt, 65) is False
        # ...but an infra/error fallback (note marker) bypasses the gate.
        attempt.evaluation.evaluator_notes = "Evaluator unavailable: boom"
        db_session.flush()
        assert gate._attempt_passes_gate(attempt, 65) is True

    @pytest.mark.asyncio
    async def test_has_unpassed_gated_attempt(self, db_session):
        _, session_id = await _start_and_submit(db_session, score=5.0)
        gate = LearningSessionService(db_session)
        daily = db_session.query(DailySession).filter_by(session_id=session_id).one()
        assert gate._has_unpassed_gated_attempt(daily, 65) is True
        assert gate._has_unpassed_gated_attempt(daily, 40) is False

    def test_gate_settings_default_off(self, db_session):
        gate = LearningSessionService(db_session)
        require, threshold = gate._gate_settings(_user_id(db_session))
        assert require is False
        assert threshold == 65

    def test_gate_settings_reads_preference(self, db_session):
        PreferenceService(db_session).update_settings(
            _user_id(db_session),
            require_pass_to_advance=True,
            pass_threshold_pct=70,
        )
        gate = LearningSessionService(db_session)
        require, threshold = gate._gate_settings(_user_id(db_session))
        assert require is True
        assert threshold == 70


# ── Points are awarded once across a fail → retry → pass → complete ──


class TestPointsOnceAfterRetry:
    @pytest.mark.asyncio
    async def test_reset_then_pass_awards_passing_attempt_once(self, db_session):
        # Fail both activities (no completion — the gate would block it).
        fail_service, session_id = await _start_and_submit(db_session, score=5.0)

        # Retry: reset both, then re-submit at a passing score.
        for seq in (1, 2):
            await fail_service.reset_activity(
                session_id=session_id,
                user_id=_user_id(db_session),
                sequence=seq,
            )
        pass_service = SessionService(
            db_session,
            evaluator=StubEvaluator(default_score=8.0),
            feedback_generator=StubFeedbackGenerator(),
        )
        for seq in (1, 2):
            await pass_service.submit_activity(
                session_id=session_id,
                user_id=_user_id(db_session),
                sequence=seq,
                user_response={"answer": "x"},
            )
        scorecard, report = await pass_service.complete_session(
            session_id=session_id,
            user_id=_user_id(db_session),
        )

        # Points applied exactly once, reflecting the passing attempt only.
        assert report.applied is True
        scorecard_total = sum(int(p) for p in scorecard.points_earned.values())
        assert scorecard_total > 0
        earned_skills = {s for s, p in scorecard.points_earned.items() if p > 0}

        # One log row per earned skill — no double-count from the failed tries.
        log_rows = db_session.query(SkillPointsLog).all()
        assert len(log_rows) == len(earned_skills)
        assert sum(int(r.points_earned) for r in log_rows) == scorecard_total

        # Running SkillPoints totals equal exactly the single passing scorecard.
        points_total = sum(int(r.points) for r in db_session.query(SkillPoints).all())
        assert points_total == scorecard_total
