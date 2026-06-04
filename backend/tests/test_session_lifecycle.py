"""End-to-end SessionService lifecycle tests against in-memory SQLite.

Async after Phase 4 — the LLM-driven agents are async, so the whole
SessionService start/submit/complete path is async. Tests inject the
deterministic Stub* agents to keep the suite offline.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio  # noqa: F401  — ensures the asyncio plugin is loaded
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Register all models on Base.metadata.
from app import models  # noqa: F401
from app.core.database import Base
from app.modules.auth.models import User, UserProfile
from app.modules.curriculum import file_source
from app.modules.curriculum.models import (
    CurriculumDay,
    CurriculumWeek,
    TaskArchetype,
    ThemeType,
)
from app.modules.progress.models import SkillPoints, SkillPointsLog
from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.exceptions import (
    AttemptAlreadySubmitted,
    SessionAdvanceBlocked,
    SessionAlreadyOpen,
    SessionNotFound,
)
from app.modules.preferences.models import UserCoursePreference
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
from app.modules.streaks.models import DailyActivity, StreakFreezeUsage
from app.modules.streaks.service import StreakService
from app.modules.sessions.service import SessionService
from app.modules.sessions.task_generator import GeneratedTask
from app.modules.sessions.widget_mapping import normalize_widget_key
from app.modules.skills.models import Skill
from app.scoring import ARCHETYPE_REGISTRY, CourseLength, SUB_SKILLS
from scripts.seed_curriculum import seed_archetypes


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
            UserCoursePreference.__table__,
            UserProfile.__table__,
            DailyActivity.__table__,
            StreakFreezeUsage.__table__,
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
    db.flush()
    db.add(UserProfile(user_id=user.id, timezone="Asia/Kolkata"))
    for sub_skill in SUB_SKILLS:
        db.add(Skill(name=sub_skill, description=sub_skill))
    db.flush()
    seed_archetypes(db)
    week = CurriculumWeek(
        week_id="wk_24_09",
        course_length="24w",
        week_number=9,
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
        day_id="day_24_09_03",
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


def _add_curriculum_day(
    db,
    *,
    week: CurriculumWeek,
    day_number: int,
) -> CurriculumDay:
    day = CurriculumDay(
        day_id=f"day_24_{week.week_number:02d}_{day_number:02d}",
        week_id=week.id,
        day_number=day_number,
        topic=f"Day {day_number}",
        explanation_brief="Practice brief.",
        default_activities=["read", "write"],
        mandatory_activities=["read"],
        suggested_archetypes={
            "read": ["READ_CLOZE"],
            "write": ["WRITE_SENT_TRANS"],
        },
    )
    db.add(day)
    db.flush()
    return day


def _add_completed_daily_session(
    db,
    *,
    user_id: int,
    day_id: str,
    status: SessionStatus = SessionStatus.COMPLETED,
) -> DailySession:
    session = DailySession(
        session_id=f"session-{day_id}-{status.value}",
        user_id=user_id,
        day_id=day_id,
        course_length="24w",
        status=status,
        is_first_attempt=True,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc)
        if status is SessionStatus.COMPLETED
        else None,
    )
    db.add(session)
    db.commit()
    return session


# ── start ──────────────────────────────────────────────────────────


class TestStartSession:
    @pytest.mark.asyncio
    async def test_creates_session_with_mandatory_attempts(self, db_session):
        service = SessionService(db_session, evaluator=StubEvaluator(default_score=7.0))
        source_day = file_source.get_day(9, 2)
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        assert session.status is SessionStatus.IN_PROGRESS
        assert session.is_first_attempt is True
        assert len(session.attempts) == 4
        assert [a.archetype_id for a in session.attempts] == list(
            source_day.task_archetypes_used
        )
        assert [a.is_mandatory for a in session.attempts] == [
            c["mandatory"] for c in source_day.activity_contracts
        ]

    @pytest.mark.asyncio
    async def test_authored_w1d1_uses_source_file_content_in_db_mode(
        self, db_session,
    ):
        week = CurriculumWeek(
            week_id="wk_24_01",
            course_length="24w",
            week_number=1,
            theme_type=ThemeType.GRAMMAR,
            title="Old DB Week",
            cefr_level="A1",
            sub_level_min=1,
            sub_level_max=2,
            learning_goal="Old DB goal.",
        )
        db_session.add(week)
        db_session.flush()
        db_session.add(
            CurriculumDay(
                day_id="day_24_01_01",
                week_id=week.id,
                day_number=1,
                topic="Old DB family possessives",
                explanation_brief="Old DB brief about family members.",
                default_activities=["read", "write"],
                mandatory_activities=["read"],
                suggested_archetypes={
                    "read": ["READ_COMP_MCQ"],
                    "write": ["WRITE_ERROR_CORR"],
                },
            )
        )
        db_session.commit()

        service = SessionService(db_session)
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_01_01",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write", "listen", "speak"},
        )

        source_day = file_source.get_day_by_id("day_24_01_01")
        assert [a.archetype_id for a in session.attempts] == list(
            source_day.task_archetypes_used
        )
        assert [a.is_mandatory for a in session.attempts] == [True, True, True, True]
        first_content = session.attempts[0].task_content
        assert first_content["topic"] == source_day.task_specs[0]["topic_override"]
        assert first_content["explanation_brief"] == source_day.explanation_brief
        assert "family" not in first_content["instructions"].lower()
        assert first_content["activity_contract"] == {
            "activity_id": "read_cloze_simple_present",
            "sequence": 1,
            "archetype_id": "READ_CLOZE",
            "activity": "read",
            "task_widget": "fill_blanks",
            "evaluator_type": "rule_plus_llm",
            "evaluation_widget": "read_listen_evaluation",
            "feedback_type": "default",
            "feedback_widget": "read_listen_feedback",
            "mandatory": True,
        }
        assert first_content["task_widget"] == "fill_blanks"
        assert first_content["evaluation_widget"] == "read_listen_evaluation"
        assert first_content["feedback_widget"] == "read_listen_feedback"

    @pytest.mark.asyncio
    async def test_blocks_second_in_progress_session(self, db_session):
        service = SessionService(db_session)
        await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write"},
        )
        with pytest.raises(SessionAlreadyOpen):
            await service.start_session(
                user_id=_user_id(db_session),
                day_id="day_24_09_03",
                course_length=CourseLength.WEEKS_24,
                tasks_per_day=2,
                allowed_activities={"read", "write"},
            )

    @pytest.mark.asyncio
    async def test_attempts_carry_stub_task_content(self, db_session):
        service = SessionService(db_session)
        source_day = file_source.get_day(9, 2)
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write"},
        )
        content = session.attempts[0].task_content
        archetype_id = source_day.task_archetypes_used[0]
        contract = source_day.activity_contracts[0]
        assert content["archetype_id"] == archetype_id
        assert content["topic"] == source_day.task_specs[0]["topic_override"]
        assert content["ui_widget"] == ARCHETYPE_REGISTRY[archetype_id].ui_widget
        assert content["activity_contract"]["task_widget"] == contract["task_widget"]
        assert (
            content["activity_contract"]["evaluation_widget"]
            == contract["evaluation_widget"]
        )
        assert content["activity_contract"]["feedback_widget"] == contract["feedback_widget"]


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
            day_id="day_24_09_03",
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

        # Per-activity breakdown: one entry per submitted attempt, in plan order,
        # each with the fields the end-of-session UI consumes.
        assert scorecard.activities is not None
        assert len(scorecard.activities) == 4
        sequences = [a["sequence"] for a in scorecard.activities]
        assert sequences == [1, 2, 3, 4]
        for entry in scorecard.activities:
            assert entry["raw_score"] == pytest.approx(8.0)
            assert entry["tier"] == "excellent"
            assert entry["base_reward"] == 55
            assert entry["archetype_id"]
            assert entry["archetype_label"]
            assert sum(entry["weighted_points"].values()) == pytest.approx(55.0)

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

    @pytest.mark.asyncio
    async def test_streak_on_first_submit_not_on_complete(self, db_session):
        """Streak is awarded on activity submit; complete does not double-award."""
        service, session = await self._start(db_session, tasks_per_day=2, score=8.0)
        await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"a": "b"},
        )
        uid = session.user_id
        profile = db_session.query(UserProfile).filter_by(user_id=uid).one()
        assert profile.current_streak == 1
        assert profile.last_animation_type == "rekindle"
        rows = db_session.query(DailyActivity).filter_by(user_id=uid).all()
        assert len(rows) == 1
        assert rows[0].streak_awarded is True
        assert rows[0].activity_count == 1

        await service.complete_session(
            session_id=session.session_id,
            user_id=session.user_id,
        )
        db_session.refresh(profile)
        assert profile.current_streak == 1
        rows_after = db_session.query(DailyActivity).filter_by(user_id=uid).all()
        assert len(rows_after) == 1
        assert rows_after[0].activity_count == 1

        streak_data = StreakService(db_session).get_streak_data(user_id=uid)
        assert streak_data.today_streak_awarded is True


class TestResetActivity:
    """Per-activity reset: clear eval/feedback, reopen day, drop scorecard."""

    async def _start(self, db, tasks_per_day=2, score=8.0):
        service = SessionService(
            db,
            evaluator=StubEvaluator(default_score=score),
            feedback_generator=StubFeedbackGenerator(),
        )
        session = await service.start_session(
            user_id=_user_id(db),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=tasks_per_day,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        return service, session

    @pytest.mark.asyncio
    async def test_reset_clears_attempt_payload(self, db_session):
        service, session = await self._start(db_session)
        await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"answer": "first try"},
        )

        attempt = await service.reset_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
        )

        assert attempt.status is AttemptStatus.PENDING
        assert attempt.user_response is None
        assert attempt.submitted_at is None
        # No evaluation/feedback rows remain for the reset attempt.
        assert (
            db_session.query(ActivityEvaluation)
            .filter_by(attempt_id=attempt.id)
            .count()
            == 0
        )
        assert (
            db_session.query(ActivityFeedback)
            .filter_by(attempt_id=attempt.id)
            .count()
            == 0
        )

    @pytest.mark.asyncio
    async def test_reset_allows_resubmit_without_error(self, db_session):
        service, session = await self._start(db_session)
        await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"answer": "first"},
        )
        await service.reset_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
        )

        # Re-submitting the reset activity must not raise AttemptAlreadySubmitted.
        attempt, evaluation, feedback = await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"answer": "retry"},
        )
        assert attempt.status is AttemptStatus.EVALUATED
        assert attempt.user_response == {"answer": "retry"}
        assert evaluation is not None
        assert feedback is not None

    @pytest.mark.asyncio
    async def test_reset_reopens_completed_day_and_clears_scorecard(self, db_session):
        service, session = await self._start(db_session, tasks_per_day=2, score=8.0)
        for seq in (1, 2):
            await service.submit_activity(
                session_id=session.session_id,
                user_id=session.user_id,
                sequence=seq,
                user_response={"a": "b"},
            )
        scorecard, _ = await service.complete_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert scorecard is not None
        completed = service.get_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert completed.status is SessionStatus.COMPLETED

        await service.reset_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
        )

        reopened = service.get_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert reopened.status is SessionStatus.IN_PROGRESS
        assert reopened.completed_at is None
        # The stale scorecard is gone (rebuilt on the next complete).
        assert (
            db_session.query(SessionScorecard)
            .filter_by(session_id=reopened.id)
            .count()
            == 0
        )
        assert reopened.attempts[0].status is AttemptStatus.PENDING
        assert reopened.attempts[1].status is AttemptStatus.EVALUATED

    @pytest.mark.asyncio
    async def test_get_scorecard_returns_none_after_reset_reopens_day(
        self, db_session,
    ):
        """After a reset reopens a completed day, the scorecard is gone, so
        the day-level read returns None until the day is completed again."""
        service, session = await self._start(db_session, tasks_per_day=2, score=8.0)
        for seq in (1, 2):
            await service.submit_activity(
                session_id=session.session_id,
                user_id=session.user_id,
                sequence=seq,
                user_response={"a": "b"},
            )
        await service.complete_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert service.get_scorecard(
            session_id=session.session_id, user_id=session.user_id,
        ) is not None

        await service.reset_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
        )

        assert service.get_scorecard(
            session_id=session.session_id, user_id=session.user_id,
        ) is None


class TestRestartRescoring:
    """Re-completing a day after a per-activity retry must reflect the new
    score WITHOUT awarding points a second time."""

    async def _start(self, db, score=8.0):
        service = SessionService(
            db,
            evaluator=StubEvaluator(default_score=score),
            feedback_generator=StubFeedbackGenerator(),
        )
        session = await service.start_session(
            user_id=_user_id(db),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        return service, session

    @staticmethod
    def _total_points(db, user_id: int) -> int:
        return sum(
            int(row.points)
            for row in db.query(SkillPoints).filter_by(user_id=user_id).all()
        )

    @pytest.mark.asyncio
    async def test_retry_speaking_rescore_does_not_double_apply_points(
        self, db_session,
    ):
        service, session = await self._start(db_session, score=8.0)
        uid = session.user_id

        # Complete the day with all activities scored 8.0.
        for seq in (1, 2, 3, 4):
            await service.submit_activity(
                session_id=session.session_id,
                user_id=uid,
                sequence=seq,
                user_response={"a": "b"},
            )
        scorecard1, report1 = await service.complete_session(
            session_id=session.session_id, user_id=uid,
        )
        assert report1.applied is True
        assert scorecard1.points_applied is True
        points_after_first = self._total_points(db_session, uid)
        assert points_after_first > 0

        # Speaking is the 4th activity (SPEAK_TIMED). Retry it with a new,
        # lower score via a second service wired with a different evaluator.
        speaking = next(
            a for a in service.get_session(
                session_id=session.session_id, user_id=uid,
            ).attempts
            if ARCHETYPE_REGISTRY[a.archetype_id].core_activity == "speak"
        )
        await service.reset_activity(
            session_id=session.session_id, user_id=uid, sequence=speaking.sequence,
        )

        service2 = SessionService(
            db_session,
            evaluator=StubEvaluator(default_score=3.0),
            feedback_generator=StubFeedbackGenerator(),
        )
        await service2.submit_activity(
            session_id=session.session_id,
            user_id=uid,
            sequence=speaking.sequence,
            user_response={"a": "redo"},
        )
        scorecard2, report2 = await service2.complete_session(
            session_id=session.session_id, user_id=uid,
        )

        # The rebuilt scorecard reflects the NEW speaking score.
        speaking_entry = next(
            a for a in scorecard2.activities
            if a["sequence"] == speaking.sequence
        )
        assert speaking_entry["raw_score"] == pytest.approx(3.0)

        # Points were applied exactly once — the retry/re-complete must not
        # award a second batch.
        assert report2.applied is False
        assert scorecard2.points_applied is True
        assert self._total_points(db_session, uid) == points_after_first


class TestAdvanceDay:
    def _set_preference(self, db, *, user_id: int, week: int, day: int):
        pref = UserCoursePreference(
            user_id=user_id,
            course_length="24w",
            tasks_per_day=4,
            allow_read=True,
            allow_write=True,
            allow_listen=True,
            allow_speak=True,
            current_week=week,
            current_day_in_week=day,
            current_day_started_at=datetime.now(timezone.utc),
        )
        db.add(pref)
        db.commit()
        return pref

    def test_advance_day_after_completed_current_day(self, db_session):
        user_id = _user_id(db_session)
        self._set_preference(db_session, user_id=user_id, week=9, day=3)
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_24_09_03",
        )

        service = SessionService(db_session)
        week, day = service.advance_day(user_id=user_id)

        assert (week, day) == (9, 4)
        pref = db_session.query(UserCoursePreference).filter_by(user_id=user_id).one()
        assert pref.current_week == 9
        assert pref.current_day_in_week == 4
        assert pref.last_completed_on is not None

    def test_advance_day_blocks_when_current_day_is_not_completed(self, db_session):
        user_id = _user_id(db_session)
        self._set_preference(db_session, user_id=user_id, week=9, day=3)
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_24_09_03",
            status=SessionStatus.IN_PROGRESS,
        )

        service = SessionService(db_session)
        with pytest.raises(SessionAdvanceBlocked):
            service.advance_day(user_id=user_id)

    def test_advance_day_rolls_day_7_into_next_week(self, db_session):
        user_id = _user_id(db_session)
        week9 = db_session.query(CurriculumWeek).filter_by(week_number=9).one()
        _add_curriculum_day(db_session, week=week9, day_number=7)
        week10 = CurriculumWeek(
            week_id="wk_24_10",
            course_length="24w",
            week_number=10,
            theme_type=ThemeType.VOCABULARY,
            title="Next week",
            cefr_level="A2",
            sub_level_min=3,
            sub_level_max=3,
            learning_goal="More practice.",
        )
        db_session.add(week10)
        db_session.flush()
        _add_curriculum_day(db_session, week=week10, day_number=1)
        db_session.commit()
        self._set_preference(db_session, user_id=user_id, week=9, day=7)
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_24_09_07",
        )

        service = SessionService(db_session)
        assert service.advance_day(user_id=user_id) == (10, 1)

    def test_advance_day_blocks_at_course_end(self, db_session):
        user_id = _user_id(db_session)
        week5 = db_session.query(CurriculumWeek).filter_by(week_number=9).one()
        _add_curriculum_day(db_session, week=week5, day_number=7)
        self._set_preference(db_session, user_id=user_id, week=9, day=7)
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_24_09_07",
        )

        service = SessionService(db_session)
        with pytest.raises(SessionAdvanceBlocked):
            service.advance_day(user_id=user_id)

    def test_advance_day_moves_48w_learner_to_depth_day(self, db_session):
        """A 48w learner who finishes week-1 day-1 (`day_48_01_01`) must land on
        the even-pass depth day `day_48_01_02`, not skip it."""
        user_id = _user_id(db_session)
        week1_48 = CurriculumWeek(
            week_id="wk_48_01",
            course_length="48w",
            week_number=1,
            theme_type=ThemeType.GRAMMAR,
            title="Simple Present (base)",
            cefr_level="A1",
            sub_level_min=1,
            sub_level_max=2,
            learning_goal="Simple present subject-verb agreement.",
        )
        db_session.add(week1_48)
        db_session.flush()
        for day_number, day_id in ((1, "day_48_01_01"), (2, "day_48_01_02")):
            db_session.add(
                CurriculumDay(
                    day_id=day_id,
                    week_id=week1_48.id,
                    day_number=day_number,
                    topic=f"48w day {day_number}",
                    explanation_brief="brief",
                    default_activities=["read", "write"],
                    mandatory_activities=["read"],
                    suggested_archetypes={"read": ["READ_CLOZE"]},
                )
            )
        db_session.commit()

        pref = UserCoursePreference(
            user_id=user_id,
            course_length="48w",
            tasks_per_day=4,
            allow_read=True,
            allow_write=True,
            allow_listen=True,
            allow_speak=True,
            current_week=1,
            current_day_in_week=1,
            current_day_started_at=datetime.now(timezone.utc),
        )
        db_session.add(pref)
        db_session.commit()
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_48_01_01",
        )

        service = SessionService(db_session)
        assert service.advance_day(user_id=user_id) == (1, 2)
        pref = db_session.query(UserCoursePreference).filter_by(user_id=user_id).one()
        assert pref.course_length == "48w"
        assert (pref.current_week, pref.current_day_in_week) == (1, 2)


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
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write"},
        )
        with pytest.raises(SessionNotFound):
            service.next_activity(session_id=session.session_id, user_id=99999)


# ── self-healing repair for stale listening payloads ───────────────


class TestAttemptDeliveryRepair:
    """Older code paths could persist listening attempts with no
    `audio_script` / `items` / `inner_widget`, which renders as the
    "Audio could not be prepared" dead-end in the widget. The repair
    method must rebuild a renderable payload before the route returns.
    """

    class CapturingTaskGenerator:
        def __init__(self) -> None:
            self.calls = []

        async def generate(
            self,
            *,
            archetype,
            day_topic,
            explanation_brief,
            cefr_level,
            sub_level,
            user_interests=None,
            task_spec=None,
        ):
            self.calls.append({
                "archetype_id": archetype.archetype_id,
                "task_spec": dict(task_spec or {}),
            })
            content = {
                "phase": "test",
                "archetype_id": archetype.archetype_id,
                "archetype_name": archetype.name,
                "ui_widget": archetype.ui_widget,
                "widget": normalize_widget_key(archetype.ui_widget),
                "core_activity": archetype.core_activity,
                "topic": (task_spec or {}).get("topic_override") or day_topic,
                "explanation_brief": explanation_brief,
                "instructions": (task_spec or {}).get("instructions_override")
                or "Complete the activity.",
                "cefr_level": cefr_level,
                "sub_level": sub_level,
            }
            if archetype.archetype_id == "SPEAK_TIMED":
                content.update({
                    "task_intro": "Record your routine sentences.",
                    "speaking_duration_seconds": 45,
                    "speaking_prompts": [
                        "Say one routine sentence with I and a frequency adverb.",
                        "Say one routine sentence with he and a frequency adverb.",
                        "Say one routine sentence with she and a frequency adverb.",
                    ],
                    "sample_responses": [
                        "I usually drink water in the morning.",
                        "He often walks to school.",
                        "She always eats breakfast at seven.",
                    ],
                })
            return GeneratedTask(content=content)

    @pytest.mark.asyncio
    async def test_listening_attempt_with_empty_audio_is_repaired(
        self, db_session,
    ):
        service = SessionService(
            db_session,
            evaluator=StubEvaluator(),
            feedback_generator=StubFeedbackGenerator(),
        )
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )

        listening = next(
            a for a in session.attempts
            if ARCHETYPE_REGISTRY[a.archetype_id].core_activity == "listen"
        )
        # Simulate a stale row written by an older code path.
        listening.task_content = {
            "phase": "stub",
            "archetype_id": listening.archetype_id,
            "topic": "Listening for daily routines",
            "instructions": "Use short A1 routine sentences.",
            "cefr_level": "A2",
            "sub_level": 3,
        }
        db_session.commit()

        repaired = await service.prepare_attempt_for_delivery(listening)
        content = repaired.task_content
        expected_inner = (
            "fill_in_blanks"
            if listening.archetype_id == "LISTEN_CLOZE"
            else "mcq"
        )
        assert content["inner_widget"] == expected_inner
        assert isinstance(content.get("items"), list)
        assert len(content["items"]) >= 1
        assert str(content.get("audio_script") or "").strip() != ""

    @pytest.mark.asyncio
    async def test_valid_attempt_content_is_returned_unchanged(self, db_session):
        service = SessionService(
            db_session,
            evaluator=StubEvaluator(),
            feedback_generator=StubFeedbackGenerator(),
        )
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        listening = next(
            a for a in session.attempts
            if ARCHETYPE_REGISTRY[a.archetype_id].core_activity == "listen"
        )
        original = dict(listening.task_content)
        repaired = await service.prepare_attempt_for_delivery(listening)
        assert repaired.task_content == original

    @pytest.mark.asyncio
    async def test_speaking_attempt_without_prompt_is_repaired_from_source_spec(
        self, db_session,
    ):
        week = CurriculumWeek(
            week_id="wk_24_01",
            course_length="24w",
            week_number=1,
            theme_type=ThemeType.GRAMMAR,
            title="Simple Present",
            cefr_level="A1",
            sub_level_min=1,
            sub_level_max=2,
            learning_goal="Simple present routines.",
        )
        db_session.add(week)
        db_session.flush()
        db_session.add(
            CurriculumDay(
                day_id="day_24_01_01",
                week_id=week.id,
                day_number=1,
                topic="Old DB topic",
                explanation_brief="Old DB brief.",
                default_activities=["read", "write", "listen", "speak"],
                mandatory_activities=["read"],
                suggested_archetypes={"speak": ["SPEAK_TIMED"]},
            )
        )
        db_session.commit()

        task_generator = self.CapturingTaskGenerator()
        service = SessionService(
            db_session,
            evaluator=StubEvaluator(),
            feedback_generator=StubFeedbackGenerator(),
            task_generator=task_generator,
        )
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_01_01",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        speaking = next(a for a in session.attempts if a.archetype_id == "SPEAK_TIMED")
        speaking.task_content = {
            "phase": "stale",
            "archetype_id": "SPEAK_TIMED",
            "ui_widget": "SpeakAndRecord",
            "widget": "speak_and_record",
            "core_activity": "speak",
            "topic": "Old DB topic",
            "instructions": "Prompt the learner to speak.",
            "task_intro": "Record your response",
            "cefr_level": "A1",
            "sub_level": 1,
        }
        db_session.commit()

        repaired = await service.prepare_attempt_for_delivery(speaking)
        content = repaired.task_content
        assert content["widget"] == "speak_and_record"
        assert len(content["speaking_prompts"]) == 3
        assert all(prompt.strip() for prompt in content["speaking_prompts"])

        repair_call = task_generator.calls[-1]
        assert repair_call["archetype_id"] == "SPEAK_TIMED"
        assert repair_call["task_spec"]["topic_override"] == "Say simple present routines"
        assert "3 speaking prompts" in repair_call["task_spec"]["widget_requirements"]


class TestRagResilience:
    """RAG is best-effort and must never block or break the chat flow.

    - ``submit_activity`` never touches the vector store synchronously.
    - ``complete_session`` is fully decoupled from the Coach's Note: it commits
      the scorecard with ``mentor_note=None`` and never awaits the generator, so
      a slow/hanging note can never stall completion.
    - ``ensure_mentor_note`` is the single, idempotent owner of note generation
      (retrieve context → generate → store the session-summary vector). It is
      awaited in-band by the chat WS / REST completion paths.
    - The background worker only re-indexes per-activity vectors.
    """

    async def _start(self, db, tasks_per_day=2, score=8.0):
        service = SessionService(
            db,
            evaluator=StubEvaluator(default_score=score),
            feedback_generator=StubFeedbackGenerator(),
        )
        session = await service.start_session(
            user_id=_user_id(db),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=tasks_per_day,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        return service, session

    async def _submit_all(self, service, session, count):
        for seq in range(1, count + 1):
            await service.submit_activity(
                session_id=session.session_id,
                user_id=session.user_id,
                sequence=seq,
                user_response={"a": "b"},
            )

    @staticmethod
    def _mock_rag(order):
        async def rec_activity(**_kw):
            order.append("activity")
            return "act_x"

        async def rec_retrieve(**_kw):
            order.append("retrieve")
            return {}

        async def rec_session(**_kw):
            order.append("session")
            return "sess_x"

        async def rec_mentor(**_kw):
            order.append("mentor")
            return "Watch your tenses next time."

        rag = MagicMock()
        rag.store_activity_feedback = AsyncMock(side_effect=rec_activity)
        rag.retrieve_context_for_feedback = AsyncMock(side_effect=rec_retrieve)
        rag.store_session_summary = AsyncMock(side_effect=rec_session)
        mentor = MagicMock()
        mentor.generate = AsyncMock(side_effect=rec_mentor)
        return rag, mentor

    @pytest.mark.asyncio
    async def test_submit_does_not_touch_rag_synchronously(self, db_session):
        """The submit path must never call the vector store (it would race the
        shared WebSocket DB session)."""
        service, session = await self._start(db_session, tasks_per_day=2)
        rag = MagicMock()
        rag.store_activity_feedback = AsyncMock()
        rag.retrieve_context_for_activity = AsyncMock()
        service._rag_service = rag

        await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"a": "b"},
        )

        assert rag.store_activity_feedback.await_count == 0
        assert rag.retrieve_context_for_activity.await_count == 0

    @pytest.mark.asyncio
    async def test_complete_session_does_not_generate_note(self, db_session):
        """Completion is decoupled from the note: even with RAG wired, the
        scorecard commits with mentor_note=None and the generator is untouched.
        Note generation is owned by the awaited ensure_mentor_note step."""
        service, session = await self._start(db_session, tasks_per_day=2)
        await self._submit_all(service, session, 2)

        order: list[str] = []
        rag, mentor = self._mock_rag(order)
        service._rag_service = rag
        service._mentor_generator = mentor
        service._schedule_post_completion_rag = lambda **kwargs: None  # isolate

        scorecard, _report = await service.complete_session(
            session_id=session.session_id,
            user_id=session.user_id,
        )

        assert scorecard.mentor_note is None
        assert order == []  # no retrieve / mentor / session on the completion path
        assert mentor.generate.await_count == 0

    @pytest.mark.asyncio
    async def test_complete_session_never_awaits_a_hanging_note(self, db_session):
        """A hanging generator cannot stall completion, because completion no
        longer awaits the note at all."""
        service, session = await self._start(db_session, tasks_per_day=2)
        await self._submit_all(service, session, 2)

        async def hang(**_kw):
            await asyncio.sleep(60)

        rag = MagicMock()
        rag.retrieve_context_for_feedback = AsyncMock(side_effect=hang)
        mentor = MagicMock()
        mentor.generate = AsyncMock(side_effect=hang)
        service._rag_service = rag
        service._mentor_generator = mentor
        service._schedule_post_completion_rag = lambda **kwargs: None

        scorecard, _report = await asyncio.wait_for(
            service.complete_session(
                session_id=session.session_id,
                user_id=session.user_id,
            ),
            timeout=2.0,
        )

        assert scorecard.mentor_note is None
        assert rag.retrieve_context_for_feedback.await_count == 0
        assert mentor.generate.await_count == 0
        refreshed = service.get_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert refreshed.status is SessionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_ensure_mentor_note_generates_persists_and_stores_summary(
        self, db_session
    ):
        """ensure_mentor_note retrieves context, generates the note, persists it
        on the scorecard, and stores the day-level summary vector — in order."""
        service, session = await self._start(db_session, tasks_per_day=2)
        await self._submit_all(service, session, 2)
        scorecard, _report = await service.complete_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert scorecard.mentor_note is None

        order: list[str] = []
        rag, mentor = self._mock_rag(order)
        service._rag_service = rag
        service._mentor_generator = mentor

        note = await service.ensure_mentor_note(
            session_id=session.session_id, user_id=session.user_id,
        )

        assert note == "Watch your tenses next time."
        assert order == ["retrieve", "mentor", "session"]
        db_session.refresh(scorecard)
        assert scorecard.mentor_note == "Watch your tenses next time."

    @pytest.mark.asyncio
    async def test_ensure_mentor_note_is_idempotent(self, db_session):
        """A second ensure_mentor_note returns the persisted note without
        re-invoking the LLM or re-storing the summary."""
        service, session = await self._start(db_session, tasks_per_day=2)
        await self._submit_all(service, session, 2)
        await service.complete_session(
            session_id=session.session_id, user_id=session.user_id,
        )

        order: list[str] = []
        rag, mentor = self._mock_rag(order)
        service._rag_service = rag
        service._mentor_generator = mentor

        first = await service.ensure_mentor_note(
            session_id=session.session_id, user_id=session.user_id,
        )
        second = await service.ensure_mentor_note(
            session_id=session.session_id, user_id=session.user_id,
        )

        assert first == second == "Watch your tenses next time."
        assert mentor.generate.await_count == 1  # not regenerated
        assert rag.store_session_summary.await_count == 1  # not re-stored

    @pytest.mark.asyncio
    async def test_ensure_mentor_note_generates_from_empty_context(self, db_session):
        """When RAG retrieval degrades to an empty context (slow/failed vectors),
        the note is still generated from the activity data alone."""
        service, session = await self._start(db_session, tasks_per_day=2)
        await self._submit_all(service, session, 2)
        await service.complete_session(
            session_id=session.session_id, user_id=session.user_id,
        )

        rag = MagicMock()
        rag.retrieve_context_for_feedback = AsyncMock(return_value={})  # degraded
        rag.store_session_summary = AsyncMock()
        mentor = MagicMock()
        mentor.generate = AsyncMock(return_value="Keep practising your tenses.")
        service._rag_service = rag
        service._mentor_generator = mentor

        note = await service.ensure_mentor_note(
            session_id=session.session_id, user_id=session.user_id,
        )

        assert note == "Keep practising your tenses."
        assert mentor.generate.await_count == 1

    @pytest.mark.asyncio
    async def test_worker_indexes_activities_only(self, db_session):
        """The background worker only re-indexes per-activity vectors; it does
        NOT retrieve context, generate the note, or store the summary."""
        service, session = await self._start(db_session, tasks_per_day=2)
        await self._submit_all(service, session, 2)
        scorecard, _report = await service.complete_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert scorecard.mentor_note is None

        order: list[str] = []
        rag, mentor = self._mock_rag(order)
        service._rag_service = rag
        service._mentor_generator = mentor

        await service.run_post_completion_rag(
            session_id=session.session_id, user_id=session.user_id,
        )

        assert order == ["activity", "activity"]
        assert mentor.generate.await_count == 0
        assert rag.store_session_summary.await_count == 0
        db_session.refresh(scorecard)
        assert scorecard.mentor_note is None

    @pytest.mark.asyncio
    async def test_reset_activity_returns_without_awaiting_rag_delete(
        self, db_session
    ):
        """Per-activity retry commits the V2 reset immediately and only
        *schedules* the (potentially slow) vector cleanup — it never awaits
        Pinecone, so a hanging delete cannot stall the retry."""
        service, session = await self._start(db_session, tasks_per_day=2)
        await self._submit_all(service, session, 2)
        await service.complete_session(
            session_id=session.session_id, user_id=session.user_id,
        )

        async def hang(*_a, **_kw):
            await asyncio.sleep(60)

        rag = MagicMock()
        rag.delete_for_attempt = AsyncMock(side_effect=hang)
        rag.delete_session_summary = AsyncMock(side_effect=hang)
        service._rag_service = rag
        scheduled: list[dict] = []
        service._schedule_rag_delete = lambda **kw: scheduled.append(kw)

        attempt = await asyncio.wait_for(
            service.reset_activity(
                session_id=session.session_id,
                user_id=session.user_id,
                sequence=1,
            ),
            timeout=2.0,
        )

        # V2 reset committed; the hanging delete was NOT awaited on the path.
        assert attempt.status is AttemptStatus.PENDING
        assert rag.delete_for_attempt.await_count == 0
        # Cleanup was scheduled fire-and-forget with the right scope.
        assert scheduled and scheduled[0]["delete_summary"] is True
        assert scheduled[0]["attempt_ids"] == [attempt.id]
        # The day was reopened and its now-stale scorecard dropped.
        refreshed = service.get_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert refreshed.status is SessionStatus.IN_PROGRESS
        assert service.get_scorecard(
            session_id=session.session_id, user_id=session.user_id,
        ) is None

    @pytest.mark.asyncio
    async def test_reset_session_full_resets_all_and_schedules_delete(
        self, db_session
    ):
        """Full restart resets every attempt to PENDING, drops the scorecard,
        reopens the day, commits immediately, and schedules background vector
        cleanup — without awaiting Pinecone."""
        service, session = await self._start(db_session, tasks_per_day=2)
        await self._submit_all(service, session, 2)
        await service.complete_session(
            session_id=session.session_id, user_id=session.user_id,
        )

        async def hang(*_a, **_kw):
            await asyncio.sleep(60)

        rag = MagicMock()
        rag.delete_for_attempt = AsyncMock(side_effect=hang)
        rag.delete_session_summary = AsyncMock(side_effect=hang)
        service._rag_service = rag
        scheduled: list[dict] = []
        service._schedule_rag_delete = lambda **kw: scheduled.append(kw)

        reopened = await asyncio.wait_for(
            service.reset_session_full(
                session_id=session.session_id, user_id=session.user_id,
            ),
            timeout=2.0,
        )

        assert reopened.status is SessionStatus.IN_PROGRESS
        assert reopened.completed_at is None
        attempts = service.attempts_repo.list_for_session(reopened.id)
        assert attempts
        assert all(a.status is AttemptStatus.PENDING for a in attempts)
        assert service.get_scorecard(
            session_id=session.session_id, user_id=session.user_id,
        ) is None
        # Background cleanup scheduled for all attempts incl. session summary;
        # the hanging delete was never awaited on the request path.
        assert rag.delete_for_attempt.await_count == 0
        assert scheduled and scheduled[0]["delete_summary"] is True
        assert sorted(scheduled[0]["attempt_ids"]) == sorted(a.id for a in attempts)
