"""drop_daily_sessions_curriculum_day_id

The e4f5a6b7c890 migration backfilled day_id from curriculum_day_id but never
dropped the now-redundant integer FK. The ORM model only knows about day_id,
so new inserts fail with a NOT NULL violation on curriculum_day_id.

Revision ID: 4cbeac0620cd
Revises: a1b2c3d4e5f6
Create Date: 2026-05-21 09:14:50.385577
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "4cbeac0620cd"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(c["name"] == column for c in inspector.get_columns(table))


def _has_constraint(table: str, constraint: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(fk["name"] == constraint for fk in inspector.get_foreign_keys(table))


def upgrade() -> None:
    if _has_constraint("daily_sessions", "daily_sessions_curriculum_day_id_fkey"):
        op.drop_constraint(
            "daily_sessions_curriculum_day_id_fkey",
            "daily_sessions",
            type_="foreignkey",
        )
    if _has_column("daily_sessions", "curriculum_day_id"):
        op.drop_column("daily_sessions", "curriculum_day_id")


def downgrade() -> None:
    # Restore the column as nullable — data cannot be recovered.
    if not _has_column("daily_sessions", "curriculum_day_id"):
        op.add_column(
            "daily_sessions",
            sa.Column("curriculum_day_id", sa.Integer(), nullable=True),
        )
