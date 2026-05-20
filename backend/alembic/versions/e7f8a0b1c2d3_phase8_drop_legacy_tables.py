"""phase8: drop 12 legacy tables + their enums

Revision ID: e7f8a0b1c2d3
Revises: d6e7f8a0b1c2
Create Date: 2026-05-20 10:30:00.000000

Destructive cutover migration. Drops every table the old skill-as-spine
flow used. After this runs, the schema contains only the new
day-as-spine tables (daily_sessions / activity_attempts /
activity_evaluations / activity_feedback / session_scorecards) plus
shared infrastructure (users, skills, user_profiles, etc.).

Tables dropped (FK-child-first order):
  1. feedbacks               (children of evaluations + users)
  2. evaluations             (children of user_responses)
  3. user_responses          (children of user_tasks)
  4. learning_sessions       (children of user_tasks, user_enrollments, users)
  5. user_skill_scores       (children of users, skills — WMA cache)
  6. enrollment_skill_history (children of user_enrollments, skills)
  7. daily_plans             (children of users)
  8. task_skills             (children of tasks, skills)
  9. user_tasks              (children of tasks, users, user_enrollments)
  10. tasks
  11. user_enrollments       (children of courses, users)
  12. courses

Indexes and FK constraints attached to a dropped table go away with
the table — Postgres cascades them automatically — so this migration
doesn't list them explicitly. That also makes the upgrade tolerant
of dev databases that have drifted (a few indexes are missing on the
current dev box for reasons that pre-date Phase 8).

Enums dropped (after their owning tables):
  task_type_enum, task_status_enum, user_task_status_enum,
  course_level_enum, course_status_enum, enrollment_status_enum

Each enum drop is gated by a `pg_type × pg_attribute` probe so we
skip any that a new-flow table still references.

Downgrade recreates the full legacy surface — empty tables — to the
shape it had at down_revision (d6e7f8a0b1c2). That includes the
admin-monitoring additions to `feedbacks` (review_status,
reviewed_by, reviewed_at, admin_note + indexes + FK to users). The
rollback contract is schema-reversible, data-lost.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "e7f8a0b1c2d3"
down_revision: Union[str, Sequence[str], None] = "d6e7f8a0b1c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Reused by `tasks.task_type` and
# `enrollment_skill_history.last_activity_type` in the legacy schema.
_TASK_TYPE_VALUES: tuple[str, ...] = (
    "reading", "writing", "speaking", "listening",
    "fill_in_blanks", "error_spotting", "sentence_transformation",
    "voice_conversion", "error_correction", "speak_with_tense",
    "curriculum_grammar_fill_blanks", "curriculum_grammar_open_text",
    "curriculum_grammar_listen_mcq", "curriculum_grammar_speak",
    "curriculum_vocab_mcq", "curriculum_vocab_open_text",
    "curriculum_vocab_listen_mcq", "curriculum_vocab_speak",
    "curriculum_pron_read_aloud", "curriculum_pron_phonetic_mcq",
    "curriculum_pron_listen_discriminate", "curriculum_pron_speak_drill",
    "curriculum_fluency_speed_read", "curriculum_fluency_timed_write",
    "curriculum_fluency_shadow", "curriculum_fluency_speak",
    "curriculum_expression_summarize", "curriculum_expression_essay",
    "curriculum_expression_listen_structure",
    "curriculum_expression_storyboard",
    "curriculum_comprehension_read_mcq",
    "curriculum_comprehension_write_answers",
    "curriculum_comprehension_listen_mcq",
    "curriculum_comprehension_retell",
    "curriculum_tone_read_mcq", "curriculum_tone_rewrite",
    "curriculum_tone_listen_mcq", "curriculum_tone_roleplay",
)

_LEGACY_TABLES_DROP_ORDER: tuple[str, ...] = (
    "feedbacks",
    "evaluations",
    "user_responses",
    "learning_sessions",
    "user_skill_scores",
    "enrollment_skill_history",
    "daily_plans",
    "task_skills",
    "user_tasks",
    "tasks",
    "user_enrollments",
    "courses",
)

_LEGACY_ENUMS: tuple[str, ...] = (
    "task_type_enum",
    "task_status_enum",
    "user_task_status_enum",
    "course_level_enum",
    "course_status_enum",
    "enrollment_status_enum",
)


def _enum_in_use(bind, enum_name: str) -> bool:
    """True if any remaining column still references this enum type."""
    row = bind.execute(
        sa.text(
            "SELECT 1 FROM pg_type t "
            "JOIN pg_attribute a ON a.atttypid = t.oid "
            "WHERE t.typname = :name LIMIT 1"
        ),
        {"name": enum_name},
    ).first()
    return row is not None


def upgrade() -> None:
    bind = op.get_bind()

    for table_name in _LEGACY_TABLES_DROP_ORDER:
        op.drop_table(table_name)

    for enum_name in _LEGACY_ENUMS:
        if _enum_in_use(bind, enum_name):
            continue
        op.execute(sa.text(f'DROP TYPE IF EXISTS "{enum_name}"'))


def downgrade() -> None:
    # Defensive: drop any lingering legacy enum types so the
    # CREATE TABLE statements below can emit fresh ones cleanly.
    # On a healthy DB this is a no-op.
    for enum_name in _LEGACY_ENUMS:
        op.execute(sa.text(f'DROP TYPE IF EXISTS "{enum_name}" CASCADE'))

    # courses — first use of course_level_enum + course_status_enum
    # so let sa.Enum emit the CREATE TYPE (default create_type=True).
    op.create_table(
        "courses",
        sa.Column("slug", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("duration_weeks", sa.Integer(), nullable=False),
        sa.Column(
            "target_level",
            sa.Enum(
                "beginner", "intermediate", "advanced",
                name="course_level_enum",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "draft", "active", "archived",
                name="course_status_enum",
            ),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_courses_slug"), "courses", ["slug"], unique=True)
    op.create_index(
        op.f("ix_courses_status"), "courses", ["status"], unique=False
    )

    # user_enrollments
    op.create_table(
        "user_enrollments",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("current_week", sa.Integer(), nullable=False),
        sa.Column("current_day_in_week", sa.Integer(), nullable=False),
        sa.Column("tasks_per_day", sa.Integer(), nullable=False),
        sa.Column("allow_reading", sa.Boolean(), nullable=False),
        sa.Column("allow_writing", sa.Boolean(), nullable=False),
        sa.Column("allow_listening", sa.Boolean(), nullable=False),
        sa.Column("allow_speaking", sa.Boolean(), nullable=False),
        sa.Column(
            "current_day_started_at",
            sa.DateTime(timezone=True), nullable=False,
        ),
        sa.Column("last_completed_on", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "active", "paused", "completed", "abandoned",
                name="enrollment_status_enum",
            ),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.CheckConstraint(
            "tasks_per_day BETWEEN 2 AND 4",
            name="ck_user_enrollments_tasks_per_day_2_4",
        ),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_enrollments_course_id"),
        "user_enrollments", ["course_id"], unique=False,
    )
    op.create_index(
        op.f("ix_user_enrollments_status"),
        "user_enrollments", ["status"], unique=False,
    )
    op.create_index(
        op.f("ix_user_enrollments_user_id"),
        "user_enrollments", ["user_id"], unique=True,
    )

    # tasks
    op.create_table(
        "tasks",
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column(
            "task_type",
            sa.Enum(
                *_TASK_TYPE_VALUES,
                name="task_type_enum",
            ),
            nullable=False,
        ),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "draft", "active", "archived",
                name="task_status_enum",
            ),
            nullable=False,
        ),
        sa.Column(
            "content", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_tasks_status"), "tasks", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_tasks_task_type"), "tasks", ["task_type"], unique=False
    )

    # task_skills
    op.create_table(
        "task_skills",
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column(
            "weight", sa.Numeric(precision=3, scale=2), nullable=False
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["task_id"], ["tasks.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_task_skills_skill_id"),
        "task_skills", ["skill_id"], unique=False,
    )
    op.create_index(
        op.f("ix_task_skills_task_id"),
        "task_skills", ["task_id"], unique=False,
    )

    # user_tasks
    op.create_table(
        "user_tasks",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("enrollment_id", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "in_progress", "completed", "skipped",
                name="user_task_status_enum",
            ),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["enrollment_id"], ["user_enrollments.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["task_id"], ["tasks.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_tasks_enrollment_id"),
        "user_tasks", ["enrollment_id"], unique=False,
    )
    op.create_index(
        op.f("ix_user_tasks_status"), "user_tasks", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_user_tasks_task_id"),
        "user_tasks", ["task_id"], unique=False,
    )
    op.create_index(
        op.f("ix_user_tasks_user_id"),
        "user_tasks", ["user_id"], unique=False,
    )

    # learning_sessions
    op.create_table(
        "learning_sessions",
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("enrollment_id", sa.Integer(), nullable=False),
        sa.Column("user_task_id", sa.Integer(), nullable=True),
        sa.Column("phase", sa.String(length=32), nullable=False),
        sa.Column("topic", sa.String(length=200), nullable=False),
        sa.Column("skill_name", sa.String(length=50), nullable=False),
        sa.Column("activity_type", sa.String(length=50), nullable=False),
        sa.Column("task_type", sa.String(length=50), nullable=False),
        sa.Column("user_level", sa.Integer(), nullable=False),
        sa.Column(
            "pre_generated_tasks",
            postgresql.JSONB(astext_type=sa.Text()), nullable=False,
        ),
        sa.Column(
            "task_queue",
            postgresql.JSONB(astext_type=sa.Text()), nullable=False,
        ),
        sa.Column("current_task_index", sa.Integer(), nullable=False),
        sa.Column(
            "messages",
            postgresql.JSONB(astext_type=sa.Text()), nullable=False,
        ),
        sa.Column(
            "user_submission",
            postgresql.JSONB(astext_type=sa.Text()), nullable=True,
        ),
        sa.Column(
            "evaluation",
            postgresql.JSONB(astext_type=sa.Text()), nullable=True,
        ),
        sa.Column(
            "feedback",
            postgresql.JSONB(astext_type=sa.Text()), nullable=True,
        ),
        sa.Column(
            "understanding_confirmed", sa.Boolean(), nullable=False
        ),
        sa.Column("current_activity_order", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["enrollment_id"], ["user_enrollments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_task_id"], ["user_tasks.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_learning_sessions_enrollment_id"),
        "learning_sessions", ["enrollment_id"], unique=False,
    )
    op.create_index(
        op.f("ix_learning_sessions_session_id"),
        "learning_sessions", ["session_id"], unique=True,
    )
    op.create_index(
        op.f("ix_learning_sessions_user_id"),
        "learning_sessions", ["user_id"], unique=False,
    )
    op.create_index(
        op.f("ix_learning_sessions_user_task_id"),
        "learning_sessions", ["user_task_id"], unique=False,
    )

    # user_responses
    op.create_table(
        "user_responses",
        sa.Column("user_task_id", sa.Integer(), nullable=False),
        sa.Column(
            "content",
            postgresql.JSONB(astext_type=sa.Text()), nullable=False,
        ),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column(
            "embedding_status",
            sa.Text(), server_default="pending", nullable=False,
        ),
        sa.Column("pinecone_vector_id", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_task_id"], ["user_tasks.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_responses_embedding_status"),
        "user_responses", ["embedding_status"], unique=False,
    )
    op.create_index(
        op.f("ix_user_responses_user_task_id"),
        "user_responses", ["user_task_id"], unique=True,
    )

    # evaluations
    op.create_table(
        "evaluations",
        sa.Column("response_id", sa.Integer(), nullable=False),
        sa.Column(
            "overall_score",
            sa.Numeric(precision=4, scale=2), nullable=False,
        ),
        sa.Column(
            "percentage",
            sa.Numeric(precision=5, scale=2), nullable=False,
        ),
        sa.Column(
            "report",
            postgresql.JSONB(astext_type=sa.Text()), nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["response_id"], ["user_responses.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_evaluations_response_id"),
        "evaluations", ["response_id"], unique=True,
    )

    # feedbacks — includes admin-monitoring columns (review_status,
    # reviewed_by, reviewed_at, admin_note) since the down_revision
    # schema had them applied via 9a2b3c4d5e6f.
    op.create_table(
        "feedbacks",
        sa.Column("evaluation_id", sa.Integer(), nullable=False),
        sa.Column(
            "body",
            postgresql.JSONB(astext_type=sa.Text()), nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "review_status",
            sa.String(length=30),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by"], ["users.id"],
            name="fk_feedbacks_reviewed_by_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_feedbacks_evaluation_id"),
        "feedbacks", ["evaluation_id"], unique=True,
    )
    op.create_index(
        op.f("ix_feedbacks_review_status"),
        "feedbacks", ["review_status"], unique=False,
    )
    op.create_index(
        op.f("ix_feedbacks_reviewed_by"),
        "feedbacks", ["reviewed_by"], unique=False,
    )

    # user_skill_scores
    op.create_table(
        "user_skill_scores",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column(
            "score", sa.Numeric(precision=3, scale=1), nullable=False
        ),
        sa.Column(
            "is_estimated", sa.Boolean(),
            server_default="false", nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),
    )
    op.create_index(
        op.f("ix_user_skill_scores_skill_id"),
        "user_skill_scores", ["skill_id"], unique=False,
    )
    op.create_index(
        op.f("ix_user_skill_scores_user_id"),
        "user_skill_scores", ["user_id"], unique=False,
    )

    # enrollment_skill_history
    op.create_table(
        "enrollment_skill_history",
        sa.Column("enrollment_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column(
            "last_activity_type",
            sa.Enum(
                *_TASK_TYPE_VALUES,
                name="task_type_enum", create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("times_practiced", sa.Integer(), nullable=False),
        sa.Column(
            "last_practiced_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["enrollment_id"], ["user_enrollments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "enrollment_id", "skill_id", name="uq_enrollment_skill"
        ),
    )
    op.create_index(
        op.f("ix_enrollment_skill_history_enrollment_id"),
        "enrollment_skill_history", ["enrollment_id"], unique=False,
    )
    op.create_index(
        op.f("ix_enrollment_skill_history_skill_id"),
        "enrollment_skill_history", ["skill_id"], unique=False,
    )

    # daily_plans
    op.create_table(
        "daily_plans",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_slug", sa.String(length=50), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.String(length=16), nullable=False),
        sa.Column(
            "plan_json",
            sa.JSON().with_variant(
                postgresql.JSONB(astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column(
            "generated_at", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "course_slug", "week", "day",
            name="uq_daily_plan_user_day",
        ),
    )
    op.create_index(
        "ix_daily_plan_lookup",
        "daily_plans", ["user_id", "course_slug", "week", "day"],
        unique=False,
    )
    op.create_index(
        op.f("ix_daily_plans_course_slug"),
        "daily_plans", ["course_slug"], unique=False,
    )
    op.create_index(
        op.f("ix_daily_plans_user_id"),
        "daily_plans", ["user_id"], unique=False,
    )
