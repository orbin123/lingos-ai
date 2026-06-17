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


def _columns(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def _indexes(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {index["name"] for index in inspector.get_indexes(table_name)}


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    return sa.inspect(bind).has_table(table_name)


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if column.name not in _columns(table_name):
        op.add_column(table_name, column)


def upgrade() -> None:
    # This migration was hand-written against one developer's drifted database
    # and originally assumed all three changes were absent. On a fresh linear
    # replay the column/table already exist (created by e0f1a2b3c456, repaired
    # on the sibling branch by f3a4b5c6d7e8 / d6e7f8a0b1c2), so every op is now
    # guarded with the inspector. Idempotent on both fresh and migrated DBs.

    # activity_evaluations — add missing updated_at
    _add_column_if_missing(
        "activity_evaluations",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # activity_feedback — create missing table
    if not _has_table("activity_feedback"):
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
    if "ix_activity_feedback_attempt_id" not in _indexes("activity_feedback"):
        op.create_index(
            op.f("ix_activity_feedback_attempt_id"),
            "activity_feedback",
            ["attempt_id"],
            unique=True,
        )

    # session_scorecards — add missing points_applied
    _add_column_if_missing(
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
