"""Models for the generic challenge framework."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Index,
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


class ChallengeAttemptStatus(str, Enum):
    """Lifecycle of one user challenge attempt."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    TIMED_OUT = "timed_out"


class Challenge(Base, IDMixin, TimestampMixin):
    """A challenge catalog entry, such as IELTS Sprint."""

    __tablename__ = "challenges"
    __table_args__ = (
        Index("ix_challenges_active_sort", "is_active", "sort_order"),
    )

    slug: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_description: Mapped[str] = mapped_column(String(255), nullable=False)
    rules_md: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    levels: Mapped[list["ChallengeLevel"]] = relationship(
        back_populates="challenge",
        cascade="all, delete-orphan",
        order_by="ChallengeLevel.level_number",
    )

    def __repr__(self) -> str:
        return f"<Challenge(slug={self.slug!r}, name={self.name!r})>"


class ChallengeLevel(Base, IDMixin, TimestampMixin):
    """One sequential level inside a challenge catalog entry."""

    __tablename__ = "challenge_levels"
    __table_args__ = (
        UniqueConstraint(
            "challenge_id",
            "level_number",
            name="uq_challenge_levels_challenge_level",
        ),
        Index("ix_challenge_levels_challenge_id", "challenge_id"),
    )

    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False
    )
    level_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    time_limit_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    pass_threshold: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)
    config: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )

    challenge: Mapped[Challenge] = relationship(back_populates="levels")
    attempts: Mapped[list["ChallengeAttempt"]] = relationship(
        back_populates="level",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ChallengeLevel(challenge_id={self.challenge_id}, "
            f"level={self.level_number}, name={self.name!r})>"
        )


class ChallengeAttempt(Base, IDMixin, CreatedAtMixin):
    """A user's attempt at a challenge level."""

    __tablename__ = "challenge_attempts"
    __table_args__ = (
        Index(
            "ix_challenge_attempts_user_level_status",
            "user_id",
            "challenge_level_id",
            "status",
        ),
        Index("ix_challenge_attempts_user_created_at", "user_id", "created_at"),
        Index("ix_challenge_attempts_expires_at", "expires_at"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    challenge_level_id: Mapped[int] = mapped_column(
        ForeignKey("challenge_levels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ChallengeAttemptStatus] = mapped_column(
        SQLAlchemyEnum(
            ChallengeAttemptStatus,
            name="challenge_attempt_status_enum",
            values_callable=lambda e: [m.value for m in e],
            create_type=False,
        ),
        nullable=False,
        default=ChallengeAttemptStatus.IN_PROGRESS,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    task_payload: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    response_payload: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    overall_score: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    section_scores: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    evaluation_report: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    feedback_report: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )

    level: Mapped[ChallengeLevel] = relationship(back_populates="attempts")

    def __repr__(self) -> str:
        return (
            f"<ChallengeAttempt(id={self.id}, user_id={self.user_id}, "
            f"level_id={self.challenge_level_id}, status={self.status.value})>"
        )

