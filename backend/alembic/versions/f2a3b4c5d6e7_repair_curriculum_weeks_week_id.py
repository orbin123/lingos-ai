"""repair curriculum_weeks.week_id

Revision ID: f2a3b4c5d6e7
Revises: e4f5a6b7c890
Create Date: 2026-05-20 09:00:00.000000

Some databases were stamped past d9e0f1a2b345 while the `curriculum_weeks`
table still carried the earlier physical schema (which had `extra_metadata`
instead of `week_id`).  This migration adds and backfills the `week_id`
string column using the same safe `_has_column` guard pattern as e4f5a6b7c890.

Backfill formula: 'wk_' + numeric part of course_length + '_' + zero-padded
week_number.  Examples:
  course_length='24w', week_number=5  →  'wk_24_05'
  course_length='48w', week_number=12 →  'wk_48_12'
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, Sequence[str], None] = "e4f5a6b7c890"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def _has_constraint(table_name: str, constraint_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    constraints = inspector.get_unique_constraints(table_name)
    return any(c["name"] == constraint_name for c in constraints)


def upgrade() -> None:
    if not _has_column("curriculum_weeks", "week_id"):
        op.add_column("curriculum_weeks", sa.Column("week_id", sa.String(length=16)))

    op.execute(
        """
        UPDATE curriculum_weeks
        SET week_id = 'wk_' || replace(course_length::text, 'w', '') || '_' ||
                      lpad(week_number::text, 2, '0')
        WHERE week_id IS NULL
        """
    )

    op.alter_column("curriculum_weeks", "week_id", nullable=False)

    if not _has_constraint("curriculum_weeks", "uq_curriculum_weeks_week_id"):
        op.create_unique_constraint(
            "uq_curriculum_weeks_week_id", "curriculum_weeks", ["week_id"]
        )

    op.create_index(
        op.f("ix_curriculum_weeks_week_id"),
        "curriculum_weeks",
        ["week_id"],
        unique=True,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_curriculum_weeks_week_id"), table_name="curriculum_weeks")
    if _has_constraint("curriculum_weeks", "uq_curriculum_weeks_week_id"):
        op.drop_constraint(
            "uq_curriculum_weeks_week_id", "curriculum_weeks", type_="unique"
        )
    if _has_column("curriculum_weeks", "week_id"):
        op.drop_column("curriculum_weeks", "week_id")
