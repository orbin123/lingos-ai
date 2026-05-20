"""ORM model for per-user course preferences."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import IDMixin, TimestampMixin


# Mirror of `app.scoring.CourseLength`. Kept as plain strings so the ORM
# stays decoupled from the scoring module at import time. The enum type
# `course_length_enum` is created by the curriculum_v2 migration; we
# reuse it here with `create_type=False`.
_COURSE_LENGTH_VALUES = ("24w", "48w")


class UserCoursePreference(Base, IDMixin, TimestampMixin):
    """One row per user — carries everything the sessions flow needs to
    resolve "today" without consulting the legacy enrollment tables.

    The unique constraint on `user_id` enforces one row per user. Creation
    is lazy: `PreferenceService.get` upserts a default row on first access.
    """

    __tablename__ = "user_course_preferences"
    __table_args__ = (
        CheckConstraint(
            "tasks_per_day BETWEEN 2 AND 4",
            name="ck_user_course_preferences_tasks_per_day_2_4",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    course_length: Mapped[str] = mapped_column(
        SQLAlchemyEnum(
            *_COURSE_LENGTH_VALUES,
            name="course_length_enum",
            create_type=False,
        ),
        nullable=False,
        server_default="24w",
    )
    tasks_per_day: Mapped[int] = mapped_column(
        Integer, nullable=False, default=2, server_default="2",
    )
    allow_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true",
    )
    allow_write: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true",
    )
    allow_listen: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true",
    )
    allow_speak: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true",
    )
    current_week: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1",
    )
    current_day_in_week: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1",
    )
    current_day_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    last_completed_on: Mapped[date | None] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<UserCoursePreference(user_id={self.user_id}, "
            f"course_length={self.course_length!r}, "
            f"week={self.current_week}, day={self.current_day_in_week})>"
        )
