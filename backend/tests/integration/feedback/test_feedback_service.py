"""Feedback-prompt system tests against in-memory SQLite.

Covers eligibility (each condition + priority), cooldown gates, randomized
display, submit/dismiss recording, and admin analytics aggregation.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401 — populate Base.metadata
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.feedback import constants as C
from app.modules.feedback.models import FeedbackPromptLog
from app.modules.feedback.schemas import FeedbackSubmit
from app.modules.feedback.service import (
    FeedbackAnalyticsService,
    FeedbackEligibilityService,
    FeedbackPromptService,
)
from app.modules.reviews.models import AppReview
from app.modules.sessions.models import (
    ActivityAttempt,
    ActivityFeedback,
    AttemptStatus,
    DailySession,
    SessionStatus,
)

NOW = datetime(2026, 6, 13, 12, 0, tzinfo=timezone.utc)


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            DailySession.__table__,
            ActivityAttempt.__table__,
            ActivityFeedback.__table__,
            AppReview.__table__,
            FeedbackPromptLog.__table__,
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


class _FixedRandom:
    """Stub RNG returning a preset value from .random()."""

    def __init__(self, value: float) -> None:
        self._value = value

    def random(self) -> float:
        return self._value


# ── factories ──────────────────────────────────────────────────────


_user_seq = 0


def _make_user(db, *, created_days_ago: int = 0) -> User:
    global _user_seq
    _user_seq += 1
    user = User(
        email=f"u{_user_seq}@example.com",
        password_hash="x",
        name="L",
    )
    user.created_at = NOW - timedelta(days=created_days_ago)
    db.add(user)
    db.commit()
    return user


def _add_session(
    db,
    *,
    user_id: int,
    status: SessionStatus,
    minutes: float = 5.0,
    completed: bool = True,
    seq: int = 0,
) -> DailySession:
    started = NOW - timedelta(days=1)
    session = DailySession(
        session_id=f"sess-{user_id}-{status.value}-{seq}",
        user_id=user_id,
        day_id="day_24_01_01",
        course_length="24w",
        status=status,
        is_first_attempt=True,
        started_at=started,
        completed_at=started + timedelta(minutes=minutes) if completed else None,
    )
    db.add(session)
    db.commit()
    return session


def _add_feedback_reports(db, *, user_id: int, n: int) -> None:
    session = _add_session(
        db, user_id=user_id, status=SessionStatus.IN_PROGRESS, completed=False
    )
    for i in range(n):
        attempt = ActivityAttempt(
            session_id=session.id,
            archetype_id="READ_CLOZE",
            sequence=i + 1,
            status=AttemptStatus.EVALUATED,
            task_content={"prompt": "x"},
        )
        db.add(attempt)
        db.flush()
        db.add(
            ActivityFeedback(
                attempt_id=attempt.id,
                score=80,
                summary="Nice work",
                did_well=["clarity"],
                mistakes=[],
                sub_skill_breakdown={"grammar": 8},
            )
        )
    db.commit()


def _log(
    db,
    *,
    user_id: int,
    prompted_days_ago: int,
    submitted: bool = False,
    dismissed: bool = False,
) -> FeedbackPromptLog:
    log = FeedbackPromptLog(
        user_id=user_id,
        prompted_at=NOW - timedelta(days=prompted_days_ago),
        trigger_type=C.TRIGGER_TASK_MILESTONE,
        submitted=submitted,
        dismissed=dismissed,
    )
    db.add(log)
    db.commit()
    return log


# ── Eligibility ────────────────────────────────────────────────────


class TestEligibility:
    def test_fresh_user_not_eligible(self, db_session):
        user = _make_user(db_session, created_days_ago=0)
        result = FeedbackEligibilityService(db_session).evaluate(user, now=NOW)
        assert result.eligible is False
        assert result.trigger_type is None

    def test_completed_tasks_triggers(self, db_session):
        user = _make_user(db_session, created_days_ago=0)
        for i in range(C.ELIGIBLE_COMPLETED_TASKS):
            _add_session(
                db_session, user_id=user.id, status=SessionStatus.COMPLETED, seq=i
            )
        result = FeedbackEligibilityService(db_session).evaluate(user, now=NOW)
        assert result.eligible is True
        assert result.trigger_type == C.TRIGGER_TASK_MILESTONE

    def test_day3_triggers(self, db_session):
        user = _make_user(db_session, created_days_ago=3)
        result = FeedbackEligibilityService(db_session).evaluate(user, now=NOW)
        assert result.eligible is True
        assert result.trigger_type == C.TRIGGER_DAY_3

    def test_feedback_reports_triggers(self, db_session):
        # In-progress session → no completed tasks; user is new → not Day 3.
        user = _make_user(db_session, created_days_ago=0)
        _add_feedback_reports(
            db_session, user_id=user.id, n=C.ELIGIBLE_FEEDBACK_REPORTS
        )
        result = FeedbackEligibilityService(db_session).evaluate(user, now=NOW)
        assert result.eligible is True
        assert result.trigger_type == C.TRIGGER_FEEDBACK_REPORTS

    def test_time_spent_triggers(self, db_session):
        # Abandoned (not completed-status) but long session → minutes only.
        user = _make_user(db_session, created_days_ago=0)
        _add_session(
            db_session,
            user_id=user.id,
            status=SessionStatus.ABANDONED,
            minutes=C.ELIGIBLE_ACTIVE_MINUTES + 1,
        )
        result = FeedbackEligibilityService(db_session).evaluate(user, now=NOW)
        assert result.eligible is True
        assert result.trigger_type == C.TRIGGER_TIME_SPENT

    def test_priority_completed_tasks_wins(self, db_session):
        # Both Day-3 and completed-tasks satisfied → task milestone wins.
        user = _make_user(db_session, created_days_ago=5)
        for i in range(C.ELIGIBLE_COMPLETED_TASKS):
            _add_session(
                db_session, user_id=user.id, status=SessionStatus.COMPLETED, seq=i
            )
        result = FeedbackEligibilityService(db_session).evaluate(user, now=NOW)
        assert result.trigger_type == C.TRIGGER_TASK_MILESTONE


# ── should_show: cooldown + randomization ──────────────────────────


class TestShouldShow:
    def _eligible_user(self, db):
        user = _make_user(db, created_days_ago=4)  # Day-3 eligible
        return user

    def test_shows_when_eligible_and_random_passes(self, db_session):
        user = self._eligible_user(db_session)
        svc = FeedbackPromptService(db_session, rng=_FixedRandom(0.1))
        res = svc.should_show(user, now=NOW)
        assert res.show is True
        assert res.trigger_type == C.TRIGGER_DAY_3
        # A prompt log was recorded.
        assert db_session.query(FeedbackPromptLog).count() == 1

    def test_random_fail_does_not_show_or_log(self, db_session):
        user = self._eligible_user(db_session)
        svc = FeedbackPromptService(db_session, rng=_FixedRandom(0.9))
        res = svc.should_show(user, now=NOW)
        assert res.show is False
        assert db_session.query(FeedbackPromptLog).count() == 0

    def test_not_eligible_does_not_show(self, db_session):
        user = _make_user(db_session, created_days_ago=0)
        svc = FeedbackPromptService(db_session, rng=_FixedRandom(0.0))
        res = svc.should_show(user, now=NOW)
        assert res.show is False

    def test_submit_cooldown_blocks(self, db_session):
        user = self._eligible_user(db_session)
        _log(db_session, user_id=user.id, prompted_days_ago=5, submitted=True)
        svc = FeedbackPromptService(db_session, rng=_FixedRandom(0.0))
        assert svc.should_show(user, now=NOW).show is False

    def test_submit_cooldown_expired_allows(self, db_session):
        user = self._eligible_user(db_session)
        _log(db_session, user_id=user.id, prompted_days_ago=31, submitted=True)
        svc = FeedbackPromptService(db_session, rng=_FixedRandom(0.0))
        assert svc.should_show(user, now=NOW).show is True

    def test_dismiss_cooldown_blocks(self, db_session):
        user = self._eligible_user(db_session)
        _log(db_session, user_id=user.id, prompted_days_ago=2, dismissed=True)
        svc = FeedbackPromptService(db_session, rng=_FixedRandom(0.0))
        assert svc.should_show(user, now=NOW).show is False

    def test_dismiss_cooldown_expired_allows(self, db_session):
        user = self._eligible_user(db_session)
        _log(db_session, user_id=user.id, prompted_days_ago=8, dismissed=True)
        svc = FeedbackPromptService(db_session, rng=_FixedRandom(0.0))
        assert svc.should_show(user, now=NOW).show is True


# ── submit / dismiss ───────────────────────────────────────────────


class TestRecord:
    def test_submit_writes_review_and_marks_log(self, db_session):
        user = _make_user(db_session, created_days_ago=4)
        open_log = _log(db_session, user_id=user.id, prompted_days_ago=0)
        for i in range(2):
            _add_session(
                db_session, user_id=user.id, status=SessionStatus.COMPLETED, seq=i
            )

        svc = FeedbackPromptService(db_session)
        payload = FeedbackSubmit(
            rating=5,
            positive_feedback="Love the lessons",
            improvement_feedback="More speaking",
            bug_report="audio glitch",
            app_version="web-1.2",
        )
        review = svc.record_submit(user, payload, now=NOW)

        assert review.id is not None
        assert review.rating == 5
        assert review.positive_feedback == "Love the lessons"
        assert review.improvement_feedback == "More speaking"
        assert review.bug_report == "audio glitch"
        assert review.task_count_when_submitted == 2
        assert review.days_since_signup == 4
        assert review.app_version == "web-1.2"
        assert review.body  # synthesized

        db_session.refresh(open_log)
        assert open_log.submitted is True
        # Submit cooldown now active.
        assert (
            FeedbackPromptService(db_session, rng=_FixedRandom(0.0))
            .should_show(user, now=NOW)
            .show
            is False
        )

    def test_submit_without_open_prompt_still_records_cooldown(self, db_session):
        user = _make_user(db_session, created_days_ago=4)
        svc = FeedbackPromptService(db_session)
        svc.record_submit(user, FeedbackSubmit(rating=4), now=NOW)
        logs = db_session.query(FeedbackPromptLog).all()
        assert len(logs) == 1 and logs[0].submitted is True

    def test_dismiss_marks_open_log(self, db_session):
        user = _make_user(db_session, created_days_ago=4)
        open_log = _log(db_session, user_id=user.id, prompted_days_ago=0)
        FeedbackPromptService(db_session).record_dismiss(user, now=NOW)
        db_session.refresh(open_log)
        assert open_log.dismissed is True


# ── analytics ──────────────────────────────────────────────────────


class TestAnalytics:
    def test_stats_aggregate(self, db_session):
        user = _make_user(db_session, created_days_ago=10)
        # Two prompts shown, one submitted → 50% submission rate.
        _log(db_session, user_id=user.id, prompted_days_ago=3, submitted=True)
        _log(db_session, user_id=user.id, prompted_days_ago=2, dismissed=True)

        reviews_repo_rows = [
            (5, "great audio", "need more speaking practice"),
            (4, None, "speaking audio broken"),
            (2, "audio crash", None),
        ]
        for rating, bug, improvement in reviews_repo_rows:
            db_session.add(
                AppReview(
                    user_id=user.id,
                    rating=rating,
                    title="t",
                    body="b",
                    improvement_feedback=improvement,
                    bug_report=bug,
                    created_at=NOW - timedelta(days=1),
                )
            )
        db_session.commit()

        stats = FeedbackAnalyticsService(db_session).stats(now=NOW)
        assert stats.total_reviews == 3
        assert stats.average_rating == pytest.approx((5 + 4 + 2) / 3, abs=0.01)
        assert stats.rating_distribution[5] == 1
        assert stats.rating_distribution[4] == 1
        assert stats.rating_distribution[2] == 1
        assert stats.rating_distribution[1] == 0
        assert stats.prompts_shown == 2
        assert stats.prompts_submitted == 1
        assert stats.submission_rate == pytest.approx(0.5, abs=0.001)
        # "speaking" appears twice in improvement text → top theme.
        top_improvement_words = {t.text for t in stats.top_improvements}
        assert "speaking" in top_improvement_words
        # "audio" appears twice in bug text.
        top_bug_words = {t.text for t in stats.top_bugs}
        assert "audio" in top_bug_words
        # One day bucket of reviews.
        assert len(stats.trend) == 1
        assert stats.trend[0].count == 3
