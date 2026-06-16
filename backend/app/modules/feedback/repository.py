"""Data access for the feedback-prompt system.

Two concerns live here:
  1. Reading the prompt-log table (cooldown lookups + analytics counts).
  2. Eligibility counters computed from existing learning tables
     (daily_sessions, activity_feedback) — read-only.

Time-on-task is summed in Python from each session's started_at/completed_at
so the query stays dialect-safe (SQLite has no EXTRACT(epoch ...)).
"""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.feedback.models import FeedbackPromptLog
from app.modules.sessions.models import (
    ActivityAttempt,
    ActivityFeedback,
    DailySession,
    SessionStatus,
)


class FeedbackPromptRepository:
    """All DB access for feedback prompts + eligibility counters."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Prompt log: cooldown lookups ──────────────────────────────────

    def last_submitted_at(self, user_id: int) -> datetime | None:
        stmt = (
            select(FeedbackPromptLog.prompted_at)
            .where(
                FeedbackPromptLog.user_id == user_id,
                FeedbackPromptLog.submitted.is_(True),
            )
            .order_by(FeedbackPromptLog.prompted_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def last_dismissed_at(self, user_id: int) -> datetime | None:
        stmt = (
            select(FeedbackPromptLog.prompted_at)
            .where(
                FeedbackPromptLog.user_id == user_id,
                FeedbackPromptLog.dismissed.is_(True),
            )
            .order_by(FeedbackPromptLog.prompted_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def latest_open_prompt(self, user_id: int) -> FeedbackPromptLog | None:
        """Most recent prompt the user hasn't yet acted on."""
        stmt = (
            select(FeedbackPromptLog)
            .where(
                FeedbackPromptLog.user_id == user_id,
                FeedbackPromptLog.submitted.is_(False),
                FeedbackPromptLog.dismissed.is_(False),
            )
            .order_by(FeedbackPromptLog.prompted_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    # ── Prompt log: writes ────────────────────────────────────────────

    def create_log(
        self, *, user_id: int, prompted_at: datetime, trigger_type: str
    ) -> FeedbackPromptLog:
        log = FeedbackPromptLog(
            user_id=user_id,
            prompted_at=prompted_at,
            trigger_type=trigger_type,
        )
        self.db.add(log)
        self.db.flush()
        return log

    # ── Eligibility counters (read-only) ──────────────────────────────

    def completed_task_count(self, user_id: int) -> int:
        stmt = select(func.count(DailySession.id)).where(
            DailySession.user_id == user_id,
            DailySession.status == SessionStatus.COMPLETED,
        )
        return self.db.execute(stmt).scalar_one() or 0

    def feedback_report_count(self, user_id: int) -> int:
        """Number of AI feedback reports the user has received."""
        stmt = (
            select(func.count(ActivityFeedback.id))
            .select_from(ActivityFeedback)
            .join(ActivityAttempt, ActivityFeedback.attempt_id == ActivityAttempt.id)
            .join(DailySession, ActivityAttempt.session_id == DailySession.id)
            .where(DailySession.user_id == user_id)
        )
        return self.db.execute(stmt).scalar_one() or 0

    def active_minutes(self, user_id: int) -> float:
        """Total learning minutes across completed sessions.

        Summed in Python from started_at/completed_at to stay dialect-safe.
        """
        stmt = select(DailySession.started_at, DailySession.completed_at).where(
            DailySession.user_id == user_id,
            DailySession.completed_at.is_not(None),
        )
        total_seconds = 0.0
        for started_at, completed_at in self.db.execute(stmt).all():
            if started_at is None or completed_at is None:
                continue
            delta = (completed_at - started_at).total_seconds()
            if delta > 0:
                total_seconds += delta
        return total_seconds / 60.0

    # ── Analytics: prompt-log aggregates ──────────────────────────────

    def prompt_totals(self) -> tuple[int, int]:
        """(total prompts shown, prompts that led to a submission)."""
        total = (
            self.db.execute(select(func.count(FeedbackPromptLog.id))).scalar_one() or 0
        )
        submitted = (
            self.db.execute(
                select(func.count(FeedbackPromptLog.id)).where(
                    FeedbackPromptLog.submitted.is_(True)
                )
            ).scalar_one()
            or 0
        )
        return total, submitted
