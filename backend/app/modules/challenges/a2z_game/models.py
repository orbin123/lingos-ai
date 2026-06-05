"""ORM model for A2Z per-user progress."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import IDMixin, TimestampMixin


class A2ZUserProgress(Base, IDMixin, TimestampMixin):
    """Tracks which letters a user has cleared per level in the A2Z game.

    One row per (user, challenge). ``cleared_letters`` is the authoritative
    alphabet map that powers the home screen; individual round history lives
    in ``challenge_attempts``.
    """

    __tablename__ = "a2z_user_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "challenge_id", name="uq_a2z_user_progress_user_challenge"),
        Index("ix_a2z_user_progress_user_id", "user_id"),
        Index("ix_a2z_user_progress_challenge_id", "challenge_id"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False
    )
    cleared_letters: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=lambda: {"1": [], "2": [], "3": []},
    )
    game_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_restarted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<A2ZUserProgress(user_id={self.user_id}, "
            f"challenge_id={self.challenge_id})>"
        )
