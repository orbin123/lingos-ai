"""End-to-end SessionService lifecycle tests against in-memory SQLite.

Async after Phase 4 — the LLM-driven agents are async, so the whole
SessionService start/submit/complete path is async. Tests inject the
deterministic Stub* agents to keep the suite offline.
"""

from __future__ import annotations

from datetime import datetime, timezone

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
        assert content["activity_contract"]["task_widget"] == "fill_in_blanks"
        assert content["activity_contract"]["evaluation_widget"] == "activity_score"
        assert content["activity_contract"]["feedback_widget"] == "feedback_card"


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
        self._set_preference(db_session, user_id=user_id, week=5, day=3)
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_24_05_03",
        )

        service = SessionService(db_session)
        week, day = service.advance_day(user_id=user_id)

        assert (week, day) == (5, 4)
        pref = db_session.query(UserCoursePreference).filter_by(user_id=user_id).one()
        assert pref.current_week == 5
        assert pref.current_day_in_week == 4
        assert pref.last_completed_on is not None

    def test_advance_day_blocks_when_current_day_is_not_completed(self, db_session):
        user_id = _user_id(db_session)
        self._set_preference(db_session, user_id=user_id, week=5, day=3)
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_24_05_03",
            status=SessionStatus.IN_PROGRESS,
        )

        service = SessionService(db_session)
        with pytest.raises(SessionAdvanceBlocked):
            service.advance_day(user_id=user_id)

    def test_advance_day_rolls_day_7_into_next_week(self, db_session):
        user_id = _user_id(db_session)
        week5 = db_session.query(CurriculumWeek).filter_by(week_number=5).one()
        _add_curriculum_day(db_session, week=week5, day_number=7)
        week6 = CurriculumWeek(
            week_id="wk_24_06",
            course_length="24w",
            week_number=6,
            theme_type=ThemeType.VOCABULARY,
            title="Next week",
            cefr_level="A2",
            sub_level_min=3,
            sub_level_max=3,
            learning_goal="More practice.",
        )
        db_session.add(week6)
        db_session.commit()
        self._set_preference(db_session, user_id=user_id, week=5, day=7)
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_24_05_07",
        )

        service = SessionService(db_session)
        assert service.advance_day(user_id=user_id) == (6, 1)

    def test_advance_day_blocks_at_course_end(self, db_session):
        user_id = _user_id(db_session)
        week5 = db_session.query(CurriculumWeek).filter_by(week_number=5).one()
        _add_curriculum_day(db_session, week=week5, day_number=7)
        self._set_preference(db_session, user_id=user_id, week=5, day=7)
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_24_05_07",
        )

        service = SessionService(db_session)
        with pytest.raises(SessionAdvanceBlocked):
            service.advance_day(user_id=user_id)


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
            day_id="day_24_05_03",
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
            day_id="day_24_05_03",
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
