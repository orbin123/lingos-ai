"""drop orphaned `activity` column from activity_attempts

The column was added by an older migration that no longer exists in the
codebase. The current ActivityAttempt model has no such column and
_materialise_attempt never sets it, so every INSERT into activity_attempts
fails with a NotNullViolation.

Revision ID: b1c2d3e4f5a6
Revises: 4cbeac0620cd
Create Date: 2026-05-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "b1c2d3e4f5a6"
down_revision = "4cbeac0620cd"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    if _has_column("activity_attempts", "activity"):
        op.drop_column("activity_attempts", "activity")


def downgrade() -> None:
    if not _has_column("activity_attempts", "activity"):
        op.add_column(
            "activity_attempts",
            sa.Column("activity", sa.Text(), nullable=True),
        )
