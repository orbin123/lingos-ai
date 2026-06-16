"""Tests for the curriculum-aware stats dashboard.

Covers the rework: curriculum-period task goals (28/week, 112/month at 4
tasks/day — not the old constant 7), range-aware KPIs and history buckets,
curriculum-week filtering by ``day_id`` (not the wall-clock Monday), all-time
sub-skill overview, RAG-backed number-free insights, and time practiced.

Runs offline against in-memory SQLite with the stats endpoint called as a
plain function (FastAPI deps are just defaults).
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401 — register every model on Base.metadata
from app.core.database import Base
from app.modules.auth.models import User, UserProfile
from app.modules.curriculum.models import (
    CurriculumDay,
    CurriculumWeek,
    TaskArchetype,
    ThemeType,
)
from app.modules.feedback_memory.models import FeedbackMemoryLog
from app.modules.preferences.models import UserCoursePreference
from app.modules.progress import routes as stats_routes
from app.modules.progress.curriculum_periods import build_period
from app.modules.progress.models import SkillPoints, SkillPointsLog
from app.modules.progress.stats_insights import build_insights
from app.modules.sessions.models import (
    ActivityAttempt,
    ActivityEvaluation,
    ActivityFeedback,
    AttemptStatus,
    DailySession,
    SessionScorecard,
    SessionStatus,
)
from app.modules.skills.models import Skill
from app.scoring import SUB_SKILLS
from scripts.seed_curriculum import seed_archetypes


# ── fixtures / builders ────────────────────────────────────────────


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            UserProfile.__table__,
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
            FeedbackMemoryLog.__table__,
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _seed_user(db, *, tasks_per_day=4, current_week=1, current_day=4) -> User:
    user = User(email="learner@example.com", password_hash="x", name="L")
    db.add(user)
    db.flush()
    for sub_skill in SUB_SKILLS:
        db.add(Skill(name=sub_skill, description=sub_skill))
    db.flush()
    for skill in db.query(Skill).all():
        db.add(
            SkillPoints(
                user_id=user.id, skill_id=skill.id, points=3000, display_score=3.0
            )
        )
    seed_archetypes(db)
    db.add(
        UserCoursePreference(
            user_id=user.id,
            course_length="24w",
            tasks_per_day=tasks_per_day,
            current_week=current_week,
            current_day_in_week=current_day,
        )
    )
    db.commit()
    return user


def _archetype_id(db) -> str:
    return db.query(TaskArchetype).first().archetype_id


def _add_week(db, week_number: int, *, cefr: str = "A1") -> CurriculumWeek:
    week = CurriculumWeek(
        week_id=f"wk_24_{week_number:02d}",
        course_length="24w",
        week_number=week_number,
        theme_type=ThemeType.GRAMMAR,
        title=f"Week {week_number}",
        cefr_level=cefr,
        sub_level_min=1,
        sub_level_max=2,
        learning_goal="Goal.",
    )
    db.add(week)
    db.flush()
    return week


def _add_day(db, week: CurriculumWeek, day_number: int) -> CurriculumDay:
    day = CurriculumDay(
        day_id=f"day_24_{week.week_number:02d}_{day_number:02d}",
        week_id=week.id,
        day_number=day_number,
        topic=f"Day {day_number}",
        explanation_brief="Brief.",
        default_activities=["read"],
        mandatory_activities=["read"],
        suggested_archetypes={"read": ["READ_CLOZE"]},
    )
    db.add(day)
    db.flush()
    return day


def _complete_session(
    db,
    *,
    user_id: int,
    day_id: str,
    n_attempts: int,
    score: float = 7.0,
    started: datetime | None = None,
    completed: datetime | None = None,
) -> DailySession:
    """One completed session with ``n_attempts`` evaluated attempts."""
    started = started or datetime.now(timezone.utc)
    completed = completed or (started + timedelta(minutes=10))
    session = DailySession(
        session_id=f"sess-{day_id}",
        user_id=user_id,
        day_id=day_id,
        course_length="24w",
        status=SessionStatus.COMPLETED,
        is_first_attempt=True,
        started_at=started,
        completed_at=completed,
    )
    db.add(session)
    db.flush()
    arch = _archetype_id(db)
    for seq in range(n_attempts):
        attempt = ActivityAttempt(
            session_id=session.id,
            archetype_id=arch,
            sequence=seq,
            status=AttemptStatus.EVALUATED,
            task_content={},
            submitted_at=completed,
        )
        db.add(attempt)
        db.flush()
        db.add(
            ActivityEvaluation(
                attempt_id=attempt.id,
                raw_score=score,
                rubric_scores={},
                base_reward=0,
                weighted_points={},
            )
        )
    db.commit()
    return session


def _add_feedback_log(db, *, user_id, session_id, attempt_id, mistakes, did_well):
    db.add(
        FeedbackMemoryLog(
            user_id=user_id,
            session_id=session_id,
            attempt_id=attempt_id,
            memory_type="activity_feedback",
            vector_id=f"act_{user_id}_{attempt_id}",
            document_text="doc",
            metadata_json={"mistakes": mistakes, "did_well": did_well},
        )
    )
    db.commit()


def _stats(db, user: User, range_: str = "week"):
    return stats_routes.get_stats_dashboard(range_=range_, current_user=user, db=db)


# ── build_period (pure) ────────────────────────────────────────────


class TestBuildPeriod:
    def test_week_goal_is_tasks_per_day_times_seven(self):
        period = build_period(
            "week", course_length="24w", tasks_per_day=4,
            current_week=1, current_day=4,
        )
        assert period.expected_tasks == 28  # not the old constant 7
        assert period.day_ids == [f"day_24_01_{d:02d}" for d in range(1, 8)]
        assert period.bucket_labels == [f"D{d}" for d in range(1, 8)]
        assert period.comparison_day_ids is None  # no week 0

    def test_month_goal_is_tasks_per_day_times_28(self):
        period = build_period(
            "month", course_length="24w", tasks_per_day=4,
            current_week=6, current_day=2,
        )
        assert period.expected_tasks == 112
        # Week 6 sits in the 4-week block weeks 5..8.
        assert period.start_week == 5 and period.end_week == 8
        assert period.bucket_labels == ["W5", "W6", "W7", "W8"]
        # Previous block weeks 1..4 is the comparison window.
        assert period.comparison_day_ids is not None
        assert period.comparison_day_ids[0] == "day_24_01_01"

    def test_all_goal_prorates_to_weeks_reached(self):
        period = build_period(
            "all", course_length="24w", tasks_per_day=4,
            current_week=3, current_day=1,
        )
        assert period.start_week == 1 and period.end_week == 3
        assert period.expected_tasks == 4 * 7 * 3
        assert period.bucket_labels == ["W1", "W2", "W3"]

    def test_all_aggregates_into_blocks_when_long(self):
        period = build_period(
            "all", course_length="48w", tasks_per_day=2,
            current_week=24, current_day=7,
        )
        # 24 week-buckets would be too dense → 4-week blocks.
        assert period.bucket_labels[0] == "W1-4"
        assert len(period.bucket_labels) == 6


# ── endpoint: task goals & completion ──────────────────────────────


class TestTaskGoals:
    def test_day_four_four_per_day_is_sixteen_of_twentyeight(self, db_session):
        user = _seed_user(
            db_session, tasks_per_day=4, current_week=1, current_day=4
        )
        week = _add_week(db_session, 1)
        for d in range(1, 5):  # days 1..4 done, 4 attempts each = 16
            day = _add_day(db_session, week, d)
            _complete_session(
                db_session, user_id=user.id, day_id=day.day_id, n_attempts=4
            )

        stats = _stats(db_session, user, "week")
        assert stats.period_snapshot.tasks_completed == 16
        assert stats.period_snapshot.tasks_goal == 28  # full week, not prorated
        assert stats.period_snapshot.completion_pct == pytest.approx(57.1, abs=0.2)
        # Legacy card mirrors the period goal — no more hardcoded 7.
        assert stats.weekly_snapshot.weekly_task_goal == 28

    def test_month_goal_is_112(self, db_session):
        user = _seed_user(
            db_session, tasks_per_day=4, current_week=2, current_day=1
        )
        _add_week(db_session, 1)
        stats = _stats(db_session, user, "month")
        assert stats.period_snapshot.tasks_goal == 112


# ── endpoint: curriculum-week filtering (not calendar) ─────────────


class TestCurriculumFiltering:
    def test_only_current_week_days_count_for_week_range(self, db_session):
        user = _seed_user(
            db_session, tasks_per_day=4, current_week=2, current_day=7
        )
        wk1 = _add_week(db_session, 1)
        wk2 = _add_week(db_session, 2)
        # Both weeks completed *today* (same wall-clock) — only week 2 should
        # count for the week range, proving day_id (not Monday) drives it.
        now = datetime.now(timezone.utc)
        d1 = _add_day(db_session, wk1, 1)
        _complete_session(
            db_session, user_id=user.id, day_id=d1.day_id,
            n_attempts=4, started=now,
        )
        d2 = _add_day(db_session, wk2, 1)
        _complete_session(
            db_session, user_id=user.id, day_id=d2.day_id,
            n_attempts=4, started=now,
        )

        week_stats = _stats(db_session, user, "week")
        assert week_stats.period_snapshot.tasks_completed == 4  # week 2 only

        all_stats = _stats(db_session, user, "all")
        assert all_stats.period_snapshot.tasks_completed == 8  # both weeks


# ── endpoint: range-dependence vs all-time pinning ─────────────────


class TestRangeBehaviour:
    def test_range_changes_history_labels_and_keeps_subskills(self, db_session):
        user = _seed_user(
            db_session, tasks_per_day=4, current_week=2, current_day=3
        )
        for wn in (1, 2):
            week = _add_week(db_session, wn)
            day = _add_day(db_session, week, 1)
            _complete_session(
                db_session, user_id=user.id, day_id=day.day_id, n_attempts=2
            )

        week_stats = _stats(db_session, user, "week")
        all_stats = _stats(db_session, user, "all")

        assert week_stats.skill_history_labels == [f"D{d}" for d in range(1, 8)]
        assert all_stats.skill_history_labels == ["W1", "W2"]

        # Sub-skill overview is all-time → identical across ranges.
        wk_scores = {s.skill_id: s.score for s in week_stats.skill_scores}
        all_scores = {s.skill_id: s.score for s in all_stats.skill_scores}
        assert wk_scores == all_scores
        assert len(week_stats.skill_scores) == len(SUB_SKILLS)

    def test_overall_score_is_period_eval_average(self, db_session):
        user = _seed_user(
            db_session, tasks_per_day=2, current_week=2, current_day=1
        )
        wk1 = _add_week(db_session, 1)
        wk2 = _add_week(db_session, 2)
        d1 = _add_day(db_session, wk1, 1)
        _complete_session(
            db_session, user_id=user.id, day_id=d1.day_id, n_attempts=2, score=4.0
        )
        d2 = _add_day(db_session, wk2, 1)
        _complete_session(
            db_session, user_id=user.id, day_id=d2.day_id, n_attempts=2, score=8.0
        )

        week_stats = _stats(db_session, user, "week")
        # Week 2 only → avg of the 8.0 evals.
        assert week_stats.period_snapshot.overall_score == pytest.approx(8.0)
        # Change vs previous week (4.0) → +4.0.
        assert week_stats.period_snapshot.overall_score_change == pytest.approx(4.0)


# ── endpoint: time practiced ───────────────────────────────────────


class TestTimePracticed:
    def test_sums_session_durations_in_period(self, db_session):
        user = _seed_user(
            db_session, tasks_per_day=4, current_week=1, current_day=2
        )
        week = _add_week(db_session, 1)
        start = datetime.now(timezone.utc)
        d1 = _add_day(db_session, week, 1)
        _complete_session(
            db_session, user_id=user.id, day_id=d1.day_id, n_attempts=2,
            started=start, completed=start + timedelta(minutes=10),
        )
        d2 = _add_day(db_session, week, 2)
        _complete_session(
            db_session, user_id=user.id, day_id=d2.day_id, n_attempts=2,
            started=start, completed=start + timedelta(minutes=5),
        )

        stats = _stats(db_session, user, "week")
        assert stats.period_snapshot.time_practiced_seconds == 15 * 60
        assert stats.practice_patterns.sessions_count == 2
        assert stats.practice_patterns.avg_session_seconds == int(15 * 60 / 2)


# ── endpoint: RAG insights are qualitative & number-free ───────────


class TestInsights:
    def test_insights_carry_no_digits(self, db_session):
        user = _seed_user(db_session)
        week = _add_week(db_session, 1)
        day = _add_day(db_session, week, 1)
        session = _complete_session(
            db_session, user_id=user.id, day_id=day.day_id, n_attempts=1
        )
        attempt = db_session.query(ActivityAttempt).first()
        _add_feedback_log(
            db_session,
            user_id=user.id,
            session_id=session.id,
            attempt_id=attempt.id,
            mistakes=[{"issue": "Article usage in 3 sentences", "rule": "a/an/the"}],
            did_well=["Strong past-tense control"],
        )

        stats = _stats(db_session, user, "week")
        joined = " ".join(stats.feedback.strengths + stats.feedback.focus_areas)
        assert not re.search(r"\d", joined), joined
        assert stats.feedback.strengths and stats.feedback.focus_areas

    def test_build_insights_falls_back_without_history(self):
        strengths, focus = build_insights({"strengths": [], "focus": []})
        assert len(strengths) == 3 and len(focus) == 3
        assert not re.search(r"\d", " ".join(strengths + focus))

    def test_build_insights_scrubs_digits_from_themes(self):
        strengths, focus = build_insights(
            {"strengths": ["Used 5 connectors"], "focus": ["Spelling of 2 words"]}
        )
        assert not re.search(r"\d", " ".join(strengths + focus))


# ── endpoint: milestone card ───────────────────────────────────────


class TestMilestone:
    def test_milestone_from_preference(self, db_session):
        user = _seed_user(
            db_session, tasks_per_day=3, current_week=5, current_day=2
        )
        stats = _stats(db_session, user, "week")
        assert stats.curriculum_milestone.current_week == 5
        assert stats.curriculum_milestone.current_day == 2
        assert stats.curriculum_milestone.total_weeks == 24
        assert stats.curriculum_milestone.course_length == "24w"
