"""Curriculum tables — legacy enrollment models + v2 week/day/archetype.

Legacy tables (`courses`, `user_enrollments`) back the enrollment-based
session flow.  The v2 tables (`curriculum_weeks`, `curriculum_days`,
`task_archetypes`) back the restructured daily-session planner.
"""

from __future__ import annotations

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
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import IDMixin, TimestampMixin


# ── Legacy enrollment models ────────────────────────────────────────


class CourseLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Course(Base, IDMixin, TimestampMixin):
    __tablename__ = "courses"

    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    duration_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
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
    )

    enrollments: Mapped[list["UserEnrollment"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Course({self.slug!r}: {self.title!r})>"


class UserEnrollment(Base, IDMixin, TimestampMixin):
    __tablename__ = "user_enrollments"
    __table_args__ = (
        CheckConstraint("tasks_per_day BETWEEN 2 AND 4", name="ck_user_enrollments_tasks_per_day_2_4"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    current_week: Mapped[int] = mapped_column(Integer, nullable=False)
    current_day_in_week: Mapped[int] = mapped_column(Integer, nullable=False)
    tasks_per_day: Mapped[int] = mapped_column(Integer, nullable=False)
    allow_reading: Mapped[bool] = mapped_column(Boolean, nullable=False)
    allow_writing: Mapped[bool] = mapped_column(Boolean, nullable=False)
    allow_listening: Mapped[bool] = mapped_column(Boolean, nullable=False)
    allow_speaking: Mapped[bool] = mapped_column(Boolean, nullable=False)
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
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    course: Mapped["Course"] = relationship(back_populates="enrollments")

    def __repr__(self) -> str:
        return f"<UserEnrollment(user={self.user_id}, course={self.course_id}, status={self.status})>"


# Allowed `course_length` values. Kept as plain strings rather than importing
# `app.scoring.CourseLength` to avoid coupling the ORM to the scoring module
# at import time. Tests and migrations assert these match.
_COURSE_LENGTH_VALUES = ("24w", "48w")


class ThemeType(str, Enum):
    """The four weekly theme types from the restructure spec §5."""

    GRAMMAR = "grammar"
    COMMUNICATION = "communication"
    VOCABULARY = "vocabulary"
    CONFIDENCE = "confidence"


class CoreActivity(str, Enum):
    """Core activity type for an archetype — one of read / write / listen / speak."""

    READ = "read"
    WRITE = "write"
    LISTEN = "listen"
    SPEAK = "speak"


# ── CurriculumWeek ─────────────────────────────────────────────────


class CurriculumWeek(Base, IDMixin, TimestampMixin):
    """One week of the new curriculum: theme, title, CEFR level, learning goal.

    The week table holds no content beyond the brief. Day topics live in
    `curriculum_days`; archetype suggestions live there too.
    """

    __tablename__ = "curriculum_weeks"
    __table_args__ = (
        UniqueConstraint("course_length", "week_number", name="uq_curriculum_week"),
        Index("ix_curriculum_week_lookup", "course_length", "week_number"),
    )

    week_id: Mapped[str] = mapped_column(
        String(16), unique=True, index=True, nullable=False
    )
    course_length: Mapped[str] = mapped_column(
        SQLAlchemyEnum(
            *_COURSE_LENGTH_VALUES,
            name="course_length_enum",
            create_type=False,  # migration owns CREATE TYPE on Postgres
        ),
        nullable=False,
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    theme_type: Mapped[ThemeType] = mapped_column(
        SQLAlchemyEnum(
            ThemeType,
            name="theme_type_enum",
            values_callable=lambda e: [m.value for m in e],
            create_type=False,
        ),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    cefr_level: Mapped[str] = mapped_column(String(8), nullable=False)
    sub_level_min: Mapped[int] = mapped_column(Integer, nullable=False)
    sub_level_max: Mapped[int] = mapped_column(Integer, nullable=False)
    learning_goal: Mapped[str] = mapped_column(Text, nullable=False)

    days: Mapped[list["CurriculumDay"]] = relationship(
        back_populates="week",
        cascade="all, delete-orphan",
        order_by="CurriculumDay.day_number",
    )

    def __repr__(self) -> str:
        return (
            f"<CurriculumWeek({self.week_id}: {self.theme_type.value} — {self.title!r})>"
        )


# ── CurriculumDay ──────────────────────────────────────────────────


class CurriculumDay(Base, IDMixin, TimestampMixin):
    """One day inside a week: topic + brief + activity recommendations.

    `suggested_archetypes` is a JSON dict `{activity: [archetype_id, ...]}`.
    Archetype IDs are filtered against the parent week's CEFR level at seed
    time, so the planner can pick any of them without further checks.
    """

    __tablename__ = "curriculum_days"
    __table_args__ = (
        UniqueConstraint("week_id", "day_number", name="uq_curriculum_day"),
    )

    day_id: Mapped[str] = mapped_column(
        String(24), unique=True, index=True, nullable=False
    )
    week_id: Mapped[int] = mapped_column(
        ForeignKey("curriculum_weeks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    explanation_brief: Mapped[str] = mapped_column(Text, nullable=False)
    default_activities: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    mandatory_activities: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    suggested_archetypes: Mapped[dict[str, list[str]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )

    week: Mapped["CurriculumWeek"] = relationship(back_populates="days")

    def __repr__(self) -> str:
        return f"<CurriculumDay({self.day_id}: {self.topic!r})>"


# ── TaskArchetype ──────────────────────────────────────────────────


class TaskArchetype(Base, TimestampMixin):
    """Static archetype definition mirrored from `app.scoring.ARCHETYPE_REGISTRY`.

    Lives in the DB so admin tools and downstream services can read it via
    standard queries. The Python registry stays the source of truth; the
    seeder enforces parity.

    `archetype_id` is the natural primary key — no surrogate int — so logs
    and references read naturally (`WRITE_EMAIL` not `42`).
    """

    __tablename__ = "task_archetypes"
    __table_args__ = (Index("ix_task_archetype_core_activity", "core_activity"),)

    archetype_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    core_activity: Mapped[CoreActivity] = mapped_column(
        SQLAlchemyEnum(
            CoreActivity,
            name="core_activity_enum",
            values_callable=lambda e: [m.value for m in e],
            create_type=False,
        ),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    ui_widget: Mapped[str] = mapped_column(String(60), nullable=False)
    themes_supported: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    cefr_min: Mapped[str] = mapped_column(String(8), nullable=False)
    cefr_max: Mapped[str] = mapped_column(String(8), nullable=False)
    weight_map: Mapped[dict[str, float]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    rubric: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    mvp: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    def __repr__(self) -> str:
        return f"<TaskArchetype({self.archetype_id}: {self.name!r})>"
