"""preferences: user_course_preferences (+ backfill from user_enrollments)

Revision ID: b4c5d6e7f9a0
Revises: a3b4c5d6e7f8
Create Date: 2026-05-19 14:00:00.000000

Creates `user_course_preferences` — the single-row-per-user state that
replaces what `UserEnrollment` carried into the daily-sessions flow:

  - course_length (24w | 48w)        — derived from `courses.duration_weeks`
  - tasks_per_day (2..4)              — copied 1:1
  - allow_read/write/listen/speak     — renamed from allow_reading/writing/…
  - current_week, current_day_in_week — copied 1:1
  - current_day_started_at            — copied 1:1
  - last_completed_on                 — copied 1:1

The backfill is one INSERT … SELECT keyed on `user_id`, using
`ON CONFLICT (user_id) DO NOTHING` so the migration is safe to re-run on
a partially-migrated DB. Only runs on Postgres — SQLite test envs use
`Base.metadata.create_all` and never see this migration.

`course_length_enum` was created by the curriculum_v2 migration; we
reuse it with `create_type=False`.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "b4c5d6e7f9a0"
down_revision: Union[str, Sequence[str], None] = "a3b4c5d6e7f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # `course_length_enum` already exists (curriculum_v2 migration). The
    # idempotent `.create(..., checkfirst=True)` is a no-op on Postgres and
    # is skipped entirely on SQLite (tests).
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        postgresql.ENUM(
            "24w", "48w", name="course_length_enum",
        ).create(bind, checkfirst=True)

    op.create_table(
        "user_course_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "course_length",
            postgresql.ENUM(
                "24w", "48w", name="course_length_enum", create_type=False,
            ),
            nullable=False,
            server_default="24w",
        ),
        sa.Column(
            "tasks_per_day",
            sa.Integer(),
            nullable=False,
            server_default="2",
        ),
        sa.Column(
            "allow_read", sa.Boolean(), nullable=False, server_default=sa.text("true"),
        ),
        sa.Column(
            "allow_write", sa.Boolean(), nullable=False, server_default=sa.text("true"),
        ),
        sa.Column(
            "allow_listen", sa.Boolean(), nullable=False, server_default=sa.text("true"),
        ),
        sa.Column(
            "allow_speak", sa.Boolean(), nullable=False, server_default=sa.text("true"),
        ),
        sa.Column(
            "current_week", sa.Integer(), nullable=False, server_default="1",
        ),
        sa.Column(
            "current_day_in_week", sa.Integer(), nullable=False, server_default="1",
        ),
        sa.Column(
            "current_day_started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("last_completed_on", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE",
        ),
        sa.UniqueConstraint("user_id", name="uq_user_course_preferences_user"),
        sa.CheckConstraint(
            "tasks_per_day BETWEEN 2 AND 4",
            name="ck_user_course_preferences_tasks_per_day_2_4",
        ),
    )
    op.create_index(
        "ix_user_course_preferences_user_id",
        "user_course_preferences",
        ["user_id"],
    )

    # Backfill from `user_enrollments`. Postgres-only — the SQLite path
    # used by tests creates tables directly via `Base.metadata.create_all`
    # and never runs migrations, so there's no enrollment data to copy.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(sa.text(
            """
            INSERT INTO user_course_preferences (
                user_id,
                course_length,
                tasks_per_day,
                allow_read,
                allow_write,
                allow_listen,
                allow_speak,
                current_week,
                current_day_in_week,
                current_day_started_at,
                last_completed_on,
                created_at,
                updated_at
            )
            SELECT
                e.user_id,
                CASE
                    WHEN c.duration_weeks = 48 THEN '48w'
                    ELSE '24w'
                END::course_length_enum,
                e.tasks_per_day,
                e.allow_reading,
                e.allow_writing,
                e.allow_listening,
                e.allow_speaking,
                e.current_week,
                e.current_day_in_week,
                e.current_day_started_at,
                e.last_completed_on,
                NOW(),
                NOW()
            FROM user_enrollments e
            JOIN courses c ON c.id = e.course_id
            ON CONFLICT (user_id) DO NOTHING
            """
        ))


def downgrade() -> None:
    op.drop_index(
        "ix_user_course_preferences_user_id",
        table_name="user_course_preferences",
    )
    op.drop_table("user_course_preferences")
