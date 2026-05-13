"""Curriculum module models — Course, UserEnrollment, EnrollmentSkillHistory.

The curriculum is structure-only. It does NOT store daily tasks (those live
in the tasks module). What a user does on Day N is decided at runtime by
the rotation engine, based on:
  - day_of_week → fixed skill (from WEEK_SCHEDULE constant)
  - last activity for that skill → next activity (round-robin)
  - week number → difficulty target
"""

from datetime import date, datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Index,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import IDMixin, TimestampMixin
from app.modules.tasks.models import TaskType


# Enums

class CourseLevel(str, Enum):
    """Target proficiency for a course (helps users pick)."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseStatus(str, Enum):
    """Lifecycle of a course definition."""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class EnrollmentStatus(str, Enum):
    """Lifecycle of a user's enrollment."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


# Course — static catalog row

class Course(Base, IDMixin, TimestampMixin):
    """A curriculum the user can enroll in.

    Holds only metadata. No daily plan stored here — the rotation engine
    generates the daily plan from constants at runtime.
    """

    __tablename__ = "courses"

    slug: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    duration_weeks: Mapped[int] = mapped_column(nullable=False)  # 24 or 48
    target_level: Mapped[CourseLevel] = mapped_column(
        SQLAlchemyEnum(
            CourseLevel,
            name="course_level_enum",
            values_callable=lambda e: [m.value for m in e],
            create_type=False,
        ),
        nullable=False,
    )
    status: Mapped[CourseStatus] = mapped_column(
        SQLAlchemyEnum(
            CourseStatus,
            name="course_status_enum",
            values_callable=lambda e: [m.value for m in e],
            create_type=False,
        ),
        nullable=False,
        default=CourseStatus.ACTIVE,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, slug={self.slug!r}, weeks={self.duration_weeks})>"


# UserEnrollment — user's position in a course

class UserEnrollment(Base, IDMixin, TimestampMixin):
    """A user's active path through a course.

    MVP rule: one ACTIVE enrollment per user (enforced by unique partial
    index — but we use a simple unique on user_id for MVP since we don't
    yet support multiple historical enrollments).

    `current_week` and `current_day_in_week` are advanced when the user
    completes a task (handled in a later sprint, not S7).
    """

    __tablename__ = "user_enrollments"
    __table_args__ = (
        CheckConstraint(
            "tasks_per_day BETWEEN 2 AND 4",
            name="ck_user_enrollments_tasks_per_day_2_4",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,        # MVP: one enrollment per user
        index=True,
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    current_week: Mapped[int] = mapped_column(nullable=False, default=1)
    current_day_in_week: Mapped[int] = mapped_column(nullable=False, default=1)
    tasks_per_day: Mapped[int] = mapped_column(nullable=False, default=2)
    allow_reading: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_writing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_listening: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_speaking: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    current_day_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    last_completed_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[EnrollmentStatus] = mapped_column(
        SQLAlchemyEnum(
            EnrollmentStatus,
            name="enrollment_status_enum",
            values_callable=lambda e: [m.value for m in e],
            create_type=False,
        ),
        nullable=False,
        default=EnrollmentStatus.ACTIVE,
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    course: Mapped["Course"] = relationship()
    skill_history: Mapped[list["EnrollmentSkillHistory"]] = relationship(
        back_populates="enrollment", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<UserEnrollment(id={self.id}, user_id={self.user_id}, "
            f"week={self.current_week}, day={self.current_day_in_week})>"
        )


# EnrollmentSkillHistory — rotation memory

class EnrollmentSkillHistory(Base, IDMixin, TimestampMixin):
    """Per-(enrollment, skill) record of the most recent activity used.

    The rotation engine reads this to decide the NEXT activity (round-robin).
    Example: if last_activity_type for grammar = READING, next will be WRITING.
    """

    __tablename__ = "enrollment_skill_history"

    enrollment_id: Mapped[int] = mapped_column(
        ForeignKey("user_enrollments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    last_activity_type: Mapped[TaskType | None] = mapped_column(
        SQLAlchemyEnum(
            TaskType,
            name="task_type_enum",
            values_callable=lambda e: [m.value for m in e],
            create_type=False,
        ),
        nullable=True,
    )
    times_practiced: Mapped[int] = mapped_column(nullable=False, default=0)
    last_practiced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    enrollment: Mapped["UserEnrollment"] = relationship(back_populates="skill_history")

    __table_args__ = (
        UniqueConstraint("enrollment_id", "skill_id", name="uq_enrollment_skill"),
    )

    def __repr__(self) -> str:
        return (
            f"<EnrollmentSkillHistory(enrollment_id={self.enrollment_id}, "
            f"skill_id={self.skill_id}, last={self.last_activity_type})>"
        )


# DailyPlan — Planner Agent contract per (user, course, week, day)

class DailyPlan(Base, IDMixin, TimestampMixin):
    """Per-(user, course, week, day) plan produced by the Planner Agent.

    Generated lazily on the first session open for a given day. Read by
    downstream agents (Teacher, Task Generator, Evaluator) so they share a
    consistent, level-aware view of the day's lesson.

    `course_slug` is denormalised (not an FK) so a saved plan remains
    interpretable even if the underlying course definition changes.
    """

    __tablename__ = "daily_plans"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "course_slug", "week", "day",
            name="uq_daily_plan_user_day",
        ),
        Index(
            "ix_daily_plan_lookup",
            "user_id", "course_slug", "week", "day",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_slug: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    week: Mapped[int] = mapped_column(nullable=False)
    day: Mapped[int] = mapped_column(nullable=False)
    topic_id: Mapped[str] = mapped_column(String(16), nullable=False)
    plan_json: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<DailyPlan(user_id={self.user_id}, course={self.course_slug!r}, "
            f"week={self.week}, day={self.day})>"
        )
