"""⭐ The Complete Learning Loop — the single most important integration test.

One authoritative test of the product's spine: a learner starts a session,
submits every activity, completes it, and the deterministic scoring engine
pushes points into their running totals — exercising
`sessions + progress + streaks + scoring` together with `Stub*` agents (offline).

This consolidates the patterns spread across `test_session_lifecycle.py` and
`test_session_replay_and_scoring.py` into one end-to-end assertion of:
attempt persistence → evaluation+feedback rows → SkillPoints/SkillPointsLog
written → streak (DailyActivity) recorded → replay re-submit earns nothing.

Uses the shared whole-schema `db_session` fixture (every table exists, so the
streak write actually fires — the replay test's minimal fixture no-ops it
because its user has no UserProfile).
"""

from __future__ import annotations

import pytest
import pytest_asyncio  # noqa: F401 — ensures the asyncio plugin is loaded

from app.modules.curriculum.models import (
    CurriculumDay,
    CurriculumWeek,
    ThemeType,
)
from app.modules.progress.models import SkillPoints, SkillPointsLog
from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.feedback_generator import StubFeedbackGenerator
from app.modules.sessions.models import (
    ActivityEvaluation,
    ActivityFeedback,
    AttemptStatus,
    SessionStatus,
)
from app.modules.sessions.service import SessionService
from app.modules.streaks.models import DailyActivity
from app.scoring import CourseLength
from scripts.seed_curriculum import seed_archetypes
from tests.factories.progress import seed_skills
from tests.factories.users import make_user

DAY_ID = "day_24_05_03"


def _build_world(db):
    """Seed a learner (with profile, so streaks fire), the 7 sub-skills,
    archetypes, and one curriculum week+day. Returns the persisted user.

    Also seeds diagnosis-style starting SkillPoints (3000 each) so the
    session's earned points show up as growth above a real baseline — the
    state a learner is actually in by the time they reach a daily session.
    """
    user = make_user(db, name="Loop Learner")
    skills = seed_skills(db)
    for skill in skills.values():
        db.add(SkillPoints(
            user_id=user.id, skill_id=skill.id, points=3000, display_score=3.0,
        ))
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
    db.add(CurriculumDay(
        day_id=DAY_ID,
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
    ))
    db.commit()
    return user


def _service(db, *, score: float = 8.0) -> SessionService:
    return SessionService(
        db,
        evaluator=StubEvaluator(default_score=score),
        feedback_generator=StubFeedbackGenerator(),
    )


async def _run_full_session(db, service: SessionService, user_id: int):
    """start → submit EVERY activity → complete.

    The day is file-authored, so the activity set (and count) is fixed by the
    curriculum, not by tasks_per_day — we submit each attempt by its real
    sequence. Returns (session, scorecard, report, activity_count).
    """
    session = await service.start_session(
        user_id=user_id,
        day_id=DAY_ID,
        course_length=CourseLength.WEEKS_24,
        tasks_per_day=4,
        allowed_activities={"read", "write", "listen", "speak"},
    )
    sequences = [a.sequence for a in session.attempts]
    for seq in sequences:
        await service.submit_activity(
            session_id=session.session_id,
            user_id=user_id,
            sequence=seq,
            user_response={"answer": "x"},
        )
    scorecard, report = await service.complete_session(
        session_id=session.session_id, user_id=user_id,
    )
    return session, scorecard, report, len(sequences)


class TestCompleteLearningLoop:
    @pytest.mark.asyncio
    async def test_full_loop_persists_and_scores(self, db_session):
        user = _build_world(db_session)
        service = _service(db_session)

        session, scorecard, report, activity_count = await _run_full_session(
            db_session, service, user.id,
        )
        assert activity_count >= 2  # file-authored day has several activities

        # ── session + attempts ─────────────────────────────────────
        assert session.is_first_attempt is True
        refreshed = service.get_session(session_id=session.session_id, user_id=user.id)
        assert refreshed.status is SessionStatus.COMPLETED
        attempts = refreshed.attempts
        assert len(attempts) == activity_count
        assert all(a.status is AttemptStatus.EVALUATED for a in attempts)

        # ── one evaluation + one feedback row per attempt ───────────
        assert db_session.query(ActivityEvaluation).count() == activity_count
        assert db_session.query(ActivityFeedback).count() == activity_count

        # ── scorecard applied on first attempt ──────────────────────
        assert report.applied is True
        assert scorecard.points_applied is True
        assert sum(scorecard.points_earned.values()) > 0

        # ── points landed in SkillPoints + audit log ────────────────
        skill_points = db_session.query(SkillPoints).all()
        assert skill_points, "expected SkillPoints rows written by scoring_writer"
        assert any(int(sp.points) > 3000 for sp in skill_points), (
            "at least one sub-skill should have earned points above the 3000 baseline"
        )
        logs = db_session.query(SkillPointsLog).all()
        assert logs
        assert all(log.session_id is not None for log in logs)
        assert all(log.reason.startswith("session:") for log in logs)

        # ── streak recorded once for the day ────────────────────────
        activities = db_session.query(DailyActivity).filter_by(user_id=user.id).all()
        assert len(activities) == 1
        assert activities[0].activity_count == activity_count

    @pytest.mark.asyncio
    async def test_replay_same_day_earns_no_extra_points(self, db_session):
        user = _build_world(db_session)

        # First (scoring) attempt.
        await _run_full_session(db_session, _service(db_session), user.id)
        first_totals = {
            sp.skill_id: int(sp.points) for sp in db_session.query(SkillPoints).all()
        }
        first_log_count = db_session.query(SkillPointsLog).count()
        assert first_totals

        # Replay the same day → scorecard computes points but does NOT apply them.
        replay = _service(db_session)
        session2, scorecard2, report2, _ = await _run_full_session(
            db_session, replay, user.id,
        )

        assert session2.is_first_attempt is False
        assert sum(scorecard2.points_earned.values()) > 0  # still computed
        assert report2.applied is False                     # but not applied
        assert scorecard2.points_applied is False

        second_totals = {
            sp.skill_id: int(sp.points) for sp in db_session.query(SkillPoints).all()
        }
        assert second_totals == first_totals
        # No new audit-log rows from the replay.
        assert db_session.query(SkillPointsLog).count() == first_log_count
