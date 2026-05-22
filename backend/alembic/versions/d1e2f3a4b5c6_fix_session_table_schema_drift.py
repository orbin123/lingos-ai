"""fix session table schema drift

Three tables diverged from the current ORM models:
- activity_evaluations: missing updated_at
- activity_feedback: table never created (model references it)
- session_scorecards: missing points_applied column

Revision ID: d1e2f3a4b5c6
Revises: c2d3e4f5a6b7
Create Date: 2026-05-22

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, Sequence[str], None] = "c2d3e4f5a6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_JSON = sa.JSON().with_variant(sa.dialects.postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    # activity_evaluations — add missing updated_at
    op.add_column(
        "activity_evaluations",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # activity_feedback — create missing table
    op.create_table(
        "activity_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("attempt_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("did_well", _JSON, nullable=False),
        sa.Column("mistakes", _JSON, nullable=False),
        sa.Column("next_tip", sa.Text(), nullable=True),
        sa.Column("sub_skill_breakdown", _JSON, nullable=False),
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
            ["attempt_id"], ["activity_attempts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("attempt_id", name="uq_activity_feedback_attempt"),
    )
    op.create_index(
        op.f("ix_activity_feedback_attempt_id"),
        "activity_feedback",
        ["attempt_id"],
        unique=True,
    )

    # session_scorecards — add missing points_applied
    op.add_column(
        "session_scorecards",
        sa.Column(
            "points_applied",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    op.drop_column("session_scorecards", "points_applied")
    op.drop_index(
        op.f("ix_activity_feedback_attempt_id"), table_name="activity_feedback"
    )
    op.drop_table("activity_feedback")
    op.drop_column("activity_evaluations", "updated_at")
