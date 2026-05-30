"""ORM models for streak tracking.

`DailyActivity` is the source of truth for "did the user complete at least
one lesson on this local date?" — the activity grid renders directly off
this table. `StreakFreezeUsage` is an append-only log of automatic freeze
spends, used to render the ice-tinted cells in the grid.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import CreatedAtMixin, IDMixin, TimestampMixin


class DailyActivity(Base, IDMixin, TimestampMixin):
    """One row per (user, local_date) the user completed any activity.

    `local_date` is the date in the user's profile timezone at completion
    time — comparing across rows is safe because the timezone is fixed
    per user. The unique constraint on (user_id, local_date) is what
    makes `record_daily_activity` idempotent under concurrent fires.
    """

    __tablename__ = "daily_activities"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    local_date: Mapped[date] = mapped_column(Date, nullable=False)
    activity_count: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", nullable=False,
    )
    # Diagnostic FK — last session that bumped this row. Nullable so the
    # streak logic still works if the caller doesn't pass a session id.
    last_session_id: Mapped[int | None] = mapped_column(
        ForeignKey("daily_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    streak_awarded: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "local_date", name="uq_daily_activities_user_date"),
        Index("ix_daily_activities_user_date", "user_id", "local_date"),
    )

    def __repr__(self) -> str:
        return (
            f"<DailyActivity(user_id={self.user_id}, "
            f"local_date={self.local_date}, count={self.activity_count})>"
        )


class StreakFreezeUsage(Base, IDMixin, CreatedAtMixin):
    """Append-only record of automatic freeze spends.

    One row per protected date. Lets the activity grid render protected
    days with the frozen tint and lets us audit/refund freezes later if
    product rules change.
    """

    __tablename__ = "streak_freeze_usages"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    protected_date: Mapped[date] = mapped_column(Date, nullable=False)
    used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    reason: Mapped[str] = mapped_column(
        String(64),
        default="auto_missed_day_protection",
        server_default="auto_missed_day_protection",
        nullable=False,
    )

    __table_args__ = (
        Index("ix_streak_freeze_usages_user_date", "user_id", "protected_date"),
    )

    def __repr__(self) -> str:
        return (
            f"<StreakFreezeUsage(user_id={self.user_id}, "
            f"protected_date={self.protected_date})>"
        )
