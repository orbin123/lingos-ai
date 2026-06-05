"""Session lifecycle tables — Phase 3 of the restructure.

Five tables back the new flow:

  daily_sessions
    └── activity_attempts
          ├── activity_evaluations  (one-to-one)
          └── activity_feedback     (one-to-one)
  session_scorecards                (one-to-one with daily_sessions)

The legacy `learning_sessions` table remains in place — Phase 7 retires it.

Replay rule: a session has `is_first_attempt=True` only when no prior
COMPLETED session exists for the same `(user_id, day_id)`. Only first-attempt
sessions write points to `SkillPoints` at completion time.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import CreatedAtMixin, IDMixin, TimestampMixin


# Allowed `course_length` values (mirror of the enum used by curriculum_v2).
_COURSE_LENGTH_VALUES = ("24w", "48w")


# ── Enums ──────────────────────────────────────────────────────────


class SessionStatus(str, Enum):
    """Lifecycle of a daily session."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class AttemptStatus(str, Enum):
    """Lifecycle of one activity inside a session."""

    PENDING = "pending"       # task delivered, user hasn't submitted yet
    SUBMITTED = "submitted"   # response stored, evaluator hasn't run
    EVALUATED = "evaluated"   # scored + feedback written


# ── DailySession ───────────────────────────────────────────────────


class DailySession(Base, IDMixin, TimestampMixin):
    """One day's session for one user.

    Identified to the outside world by `session_id` (UUID string). The
    integer `id` is internal only — keeps FK joins fast.
    """

    __tablename__ = "daily_sessions"

    session_id: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day_id: Mapped[str] = mapped_column(
        String(24),
        ForeignKey("curriculum_days.day_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    course_length: Mapped[str] = mapped_column(
        SQLAlchemyEnum(
            *_COURSE_LENGTH_VALUES,
            name="course_length_enum",
            create_type=False,  # already created by curriculum_v2 migration
        ),
        nullable=False,
    )
    status: Mapped[SessionStatus] = mapped_column(
        SQLAlchemyEnum(
            SessionStatus,
            name="session_status_enum",
            values_callable=lambda e: [m.value for m in e],
            create_type=False,
        ),
        nullable=False,
        default=SessionStatus.IN_PROGRESS,
        index=True,
    )
    is_first_attempt: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    attempts: Mapped[list["ActivityAttempt"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ActivityAttempt.sequence",
    )
    scorecard: Mapped["SessionScorecard | None"] = relationship(
        back_populates="session", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<DailySession(session_id={self.session_id!r}, user_id={self.user_id}, "
            f"day_id={self.day_id!r}, status={self.status.value})>"
        )


# ── ActivityAttempt ────────────────────────────────────────────────


class ActivityAttempt(Base, IDMixin, TimestampMixin):
    """One activity (one archetype) inside a session.

    `task_content` is the generated task body the frontend renders. For
    Phase 3 with stub agents, this is a minimal placeholder; Phase 4 fills
    it with real Task-Generator output.
    """

    __tablename__ = "activity_attempts"
    __table_args__ = (
        UniqueConstraint("session_id", "sequence", name="uq_activity_attempt_sequence"),
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey("daily_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    archetype_id: Mapped[str] = mapped_column(
        String(40),
        ForeignKey("task_archetypes.archetype_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    status: Mapped[AttemptStatus] = mapped_column(
        SQLAlchemyEnum(
            AttemptStatus,
            name="attempt_status_enum",
            values_callable=lambda e: [m.value for m in e],
            create_type=False,
        ),
        nullable=False,
        default=AttemptStatus.PENDING,
    )
    task_content: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    user_response: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    session: Mapped[DailySession] = relationship(back_populates="attempts")
    evaluation: Mapped["ActivityEvaluation | None"] = relationship(
        back_populates="attempt", uselist=False, cascade="all, delete-orphan"
    )
    feedback: Mapped["ActivityFeedback | None"] = relationship(
        back_populates="attempt", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<ActivityAttempt(session_id={self.session_id}, seq={self.sequence}, "
            f"archetype={self.archetype_id!r}, status={self.status.value})>"
        )


# ── ActivityEvaluation ─────────────────────────────────────────────


class ActivityEvaluation(Base, IDMixin, TimestampMixin):
    """Scoring output for one attempt — deterministic + structured.

    `weighted_points` is `{sub_skill: float}` (unrounded — rounding happens
    once at session aggregation per the scoring engine's contract).
    """

    __tablename__ = "activity_evaluations"

    attempt_id: Mapped[int] = mapped_column(
        ForeignKey("activity_attempts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    raw_score: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False)
    rubric_scores: Mapped[dict[str, float]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    base_reward: Mapped[int] = mapped_column(Integer, nullable=False)
    weighted_points: Mapped[dict[str, float]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    evaluator_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    attempt: Mapped[ActivityAttempt] = relationship(back_populates="evaluation")

    def __repr__(self) -> str:
        return (
            f"<ActivityEvaluation(attempt_id={self.attempt_id}, "
            f"raw={float(self.raw_score)}, base_reward={self.base_reward})>"
        )


# ── ActivityFeedback ───────────────────────────────────────────────


class ActivityFeedback(Base, IDMixin, TimestampMixin):
    """Structured feedback for one attempt — replaces the legacy Feedback table.

    Shape matches the restructure spec §14 exactly:
      summary, did_well[], mistakes[], next_tip, sub_skill_breakdown.
    """

    __tablename__ = "activity_feedback"

    attempt_id: Mapped[int] = mapped_column(
        ForeignKey("activity_attempts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    did_well: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    mistakes: Mapped[list[dict]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    next_tip: Mapped[str | None] = mapped_column(Text, nullable=True)
    sub_skill_breakdown: Mapped[dict[str, int]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )

    attempt: Mapped[ActivityAttempt] = relationship(back_populates="feedback")

    def __repr__(self) -> str:
        return f"<ActivityFeedback(attempt_id={self.attempt_id}, score={self.score})>"


# ── SessionScorecard ───────────────────────────────────────────────


class SessionScorecard(Base, IDMixin, CreatedAtMixin):
    """One-to-one with `daily_sessions`. Append-only.

    Produced exactly once by the scoring engine at session completion.
    Contains the aggregated per-sub-skill earnings plus the post-write
    totals and dashboard snapshot for fast frontend rendering.
    """

    __tablename__ = "session_scorecards"

    session_id: Mapped[int] = mapped_column(
        ForeignKey("daily_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    points_earned: Mapped[dict[str, int]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    subskill_totals_after: Mapped[dict[str, int]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    dashboard_after: Mapped[dict[str, float]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    activities: Mapped[list[dict] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    points_applied: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    mentor_note: Mapped[str | None] = mapped_column(
        Text, nullable=True,
    )

    session: Mapped[DailySession] = relationship(back_populates="scorecard")

    def __repr__(self) -> str:
        return (
            f"<SessionScorecard(session_id={self.session_id}, "
            f"earned_skills={len(self.points_earned)}, applied={self.points_applied})>"
        )


# ── FeedbackRating ─────────────────────────────────────────────────


class FeedbackRating(Base, IDMixin, TimestampMixin):
    """Learner thumbs up/down on a session's RAG feedback (Coach's Note).

    Keyed on the scorecard because the mentor note physically lives there.
    One rating per user per scorecard — toggling like↔dislike upserts in place.
    Liked notes surface as positive in admin Feedback Review; disliked as flagged.
    """

    __tablename__ = "feedback_ratings"
    __table_args__ = (
        UniqueConstraint("scorecard_id", "user_id", name="uq_feedback_rating_user"),
    )

    scorecard_id: Mapped[int] = mapped_column(
        ForeignKey("session_scorecards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # "like" | "dislike"
    value: Mapped[str] = mapped_column(String(10), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<FeedbackRating(scorecard_id={self.scorecard_id}, "
            f"user_id={self.user_id}, value={self.value!r})>"
        )
