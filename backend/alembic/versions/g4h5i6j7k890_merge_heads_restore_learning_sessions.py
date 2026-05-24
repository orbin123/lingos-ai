"""merge heads and restore learning_sessions after phase8 drop

The e2 and f3 Alembic branches diverged after a3b4c5d6e7f8. Branch e2
recreates `learning_sessions` (a1b2c3d4e5f6); branch f3 drops it again in
phase 8 (e7f8a0b1c2d3). Databases that applied both heads end up without
the table even though the ORM still expects it.

This merge revision unifies the heads and idempotently recreates
`learning_sessions` when it is missing.

Revision ID: g4h5i6j7k890
Revises: e2f3a4b5c6d7, f3a4b5c6d7e8
Create Date: 2026-05-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "g4h5i6j7k890"
down_revision: Union[str, Sequence[str], None] = ("e2f3a4b5c6d7", "f3a4b5c6d7e8")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _learning_sessions_exists(bind) -> bool:
    row = bind.execute(
        sa.text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = 'learning_sessions'"
        )
    ).first()
    return row is not None


def upgrade() -> None:
    bind = op.get_bind()
    if _learning_sessions_exists(bind):
        return

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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
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
    bind = op.get_bind()
    if not _learning_sessions_exists(bind):
        return

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
