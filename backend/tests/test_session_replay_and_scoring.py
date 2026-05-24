"""Replay rule + end-to-end scoring writer integration.

Async after Phase 4 (the SessionService start/submit/complete path went
async to support the LLM agents). Tests inject the deterministic Stub*
agents to keep the suite offline.
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
from app.modules.progress.models import SkillPoints, SkillPointsLog
from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.feedback_generator import StubFeedbackGenerator
from app.modules.sessions.models import (
    ActivityAttempt,
    ActivityEvaluation,
    ActivityFeedback,
    DailySession,
    SessionScorecard,
)
from app.modules.sessions.service import SessionService
from app.modules.skills.models import Skill
from app.scoring import (
    CourseLength,
    MAX_POINTS_PER_SUBSKILL,
    SUB_SKILLS,
)
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
    db.add(CurriculumDay(
        day_id="day_24_05_03",
        week_id=week.id,
        day_number=3,
        topic="Past negative and questions",
        explanation_brief="didn't + base verb",
        default_activities=["read", "write", "listen", "speak"],
        mandatory_activities=["read", "write"],
        suggested_archetypes={
            "read":   ["READ_CLOZE"],
            "write":  ["WRITE_SENT_TRANS"],
            "listen": ["LISTEN_CLOZE"],
            "speak":  ["SPEAK_TIMED"],
        },
    ))
    db.commit()


def _user_id(db) -> int:
    return db.query(User).first().id


async def _run_complete_session(
    db, *, score: float = 8.0, tasks_per_day: int = 2,
) -> tuple[SessionService, str]:
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
    await service.complete_session(
        session_id=session.session_id, user_id=session.user_id,
    )
    return service, session.session_id


# ── Replay rule ────────────────────────────────────────────────────


class TestReplayRule:
    @pytest.mark.asyncio
    async def test_first_session_awards_points(self, db_session):
        _, session_id = await _run_complete_session(db_session, score=8.0, tasks_per_day=2)
        rows = db_session.query(SkillPoints).all()
        assert rows, "expected at least one SkillPoints row written"
        log_rows = db_session.query(SkillPointsLog).all()
        assert log_rows
        for log in log_rows:
            assert log.session_id is not None
            assert log.reason.startswith("session:")

    @pytest.mark.asyncio
    async def test_second_session_for_same_day_awards_nothing(self, db_session):
        service1, _ = await _run_complete_session(db_session, score=8.0, tasks_per_day=2)
        first_totals = {
            row.skill_id: int(row.points)
            for row in db_session.query(SkillPoints).all()
        }
        assert first_totals, "first session should have written points"

        service2 = SessionService(
            db_session,
            evaluator=StubEvaluator(default_score=8.0),
            feedback_generator=StubFeedbackGenerator(),
        )
        session2 = await service2.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_05_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write"},
        )
        assert session2.is_first_attempt is False
        for seq in (1, 2):
            await service2.submit_activity(
                session_id=session2.session_id,
                user_id=session2.user_id,
                sequence=seq,
                user_response={"answer": "x"},
            )
        scorecard2, report2 = await service2.complete_session(
            session_id=session2.session_id, user_id=session2.user_id,
        )

        assert sum(scorecard2.points_earned.values()) > 0
        assert report2.applied is False
        assert scorecard2.points_applied is False
        second_totals = {
            row.skill_id: int(row.points)
            for row in db_session.query(SkillPoints).all()
        }
        assert second_totals == first_totals

    @pytest.mark.asyncio
    async def test_replay_writes_no_audit_log_rows(self, db_session):
        await _run_complete_session(db_session, score=8.0, tasks_per_day=2)
        first_log_count = db_session.query(SkillPointsLog).count()

        service2 = SessionService(
            db_session,
            evaluator=StubEvaluator(default_score=8.0),
            feedback_generator=StubFeedbackGenerator(),
        )
        session2 = await service2.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_05_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write"},
        )
        for seq in (1, 2):
            await service2.submit_activity(
                session_id=session2.session_id,
                user_id=session2.user_id,
                sequence=seq,
                user_response={"answer": "x"},
            )
        await service2.complete_session(
            session_id=session2.session_id, user_id=session2.user_id,
        )

        assert db_session.query(SkillPointsLog).count() == first_log_count


# ── Scoring math integration ───────────────────────────────────────


class TestScoringIntegration:
    @pytest.mark.asyncio
    async def test_scorecard_matches_engine_math(self, db_session):
        """Two READ_CLOZE + one WRITE_SENT_TRANS at Excellent should produce
        deterministic points matching what the engine would compute directly."""
        # READ_CLOZE weights: grammar 0.50, vocabulary 0.35, expression 0.15
        # WRITE_SENT_TRANS weights: grammar 0.70, vocabulary 0.20, expression 0.10
        # At score 8.0 (Excellent → 55 pts 24w):
        #   READ_CLOZE  → grammar 27.5,  vocabulary 19.25, expression 8.25
        #   WRITE_SENT  → grammar 38.5,  vocabulary 11.0,  expression 5.5
        # Aggregated then rounded:
        #   grammar:     66.0 → 66
        #   vocabulary:  30.25 → 30
        #   expression:  13.75 → 14
        await _run_complete_session(db_session, score=8.0, tasks_per_day=2)
        scorecard = db_session.query(SessionScorecard).one()
        assert scorecard.points_earned == {
            "grammar": 66,
            "vocabulary": 30,
            "expression": 14,
        }

    @pytest.mark.asyncio
    async def test_subskill_totals_after_reflects_starting_points(self, db_session):
        skill_ids = {row.name: row.id for row in db_session.query(Skill).all()}
        for name in ("grammar", "vocabulary"):
            db_session.add(SkillPoints(
                user_id=_user_id(db_session),
                skill_id=skill_ids[name],
                points=3000,
                display_score=3.0,
            ))
        db_session.commit()

        await _run_complete_session(db_session, score=8.0, tasks_per_day=2)
        scorecard = db_session.query(SessionScorecard).one()
        assert scorecard.subskill_totals_after["grammar"] == 3000 + 66
        assert scorecard.subskill_totals_after["vocabulary"] == 3000 + 30
        assert scorecard.subskill_totals_after["expression"] == 14

    @pytest.mark.asyncio
    async def test_cap_does_not_block_earned_log(self, db_session):
        skill_ids = {row.name: row.id for row in db_session.query(Skill).all()}
        db_session.add(SkillPoints(
            user_id=_user_id(db_session),
            skill_id=skill_ids["grammar"],
            points=MAX_POINTS_PER_SUBSKILL,
            display_score=10.0,
        ))
        db_session.commit()
        await _run_complete_session(db_session, score=8.0, tasks_per_day=2)
        scorecard = db_session.query(SessionScorecard).one()
        assert scorecard.points_earned["grammar"] > 0
        assert scorecard.subskill_totals_after["grammar"] == MAX_POINTS_PER_SUBSKILL
        assert scorecard.dashboard_after["grammar"] == 10.0
        row = db_session.query(SkillPoints).filter_by(
            skill_id=skill_ids["grammar"],
        ).one()
        assert row.points == MAX_POINTS_PER_SUBSKILL
