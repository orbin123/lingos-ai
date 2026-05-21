"""restore learning_sessions table for chat layer (V2-linked)

Recreates the `learning_sessions` table dropped in phase 8, this time
referencing `daily_sessions.id` instead of the now-deleted
`user_enrollments` and `user_tasks` tables. Adds a `teacher_instructions`
JSONB column for the per-session teacher persona.

Revision ID: a1b2c3d4e5f6
Revises: f2a3b4c5d6e7
Create Date: 2026-05-20
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "a1b2c3d4e5f6"
down_revision = "f2a3b4c5d6e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The old learning_sessions table (with enrollment_id + user_task_id
    # FKs) is incompatible with the V2-linked chat layer. Drop and rebuild.
    # Any prior chat conversations cannot be migrated because their parent
    # rows (UserEnrollment, UserTask) have been removed by the broader
    # curriculum restructure.
    op.execute("DROP TABLE IF EXISTS learning_sessions CASCADE")

    op.create_table(
        "learning_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("daily_session_id", sa.Integer(), nullable=False),
        sa.Column("phase", sa.String(length=32), nullable=False, server_default="teaching"),
        sa.Column("topic", sa.String(length=200), nullable=False, server_default=""),
        sa.Column("skill_name", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("activity_type", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("task_type", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("user_level", sa.Integer(), nullable=False, server_default="5"),
        sa.Column(
            "pre_generated_tasks",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "task_queue",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("current_task_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "messages",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "user_submission",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "evaluation",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "feedback",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "understanding_confirmed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "current_activity_order",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "teacher_instructions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["daily_session_id"], ["daily_sessions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_learning_sessions_session_id"),
        "learning_sessions",
        ["session_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_learning_sessions_user_id"),
        "learning_sessions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_learning_sessions_daily_session_id"),
        "learning_sessions",
        ["daily_session_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_learning_sessions_daily_session_id"),
        table_name="learning_sessions",
    )
    op.drop_index(
        op.f("ix_learning_sessions_user_id"),
        table_name="learning_sessions",
    )
    op.drop_index(
        op.f("ix_learning_sessions_session_id"),
        table_name="learning_sessions",
    )
    op.drop_table("learning_sessions")
