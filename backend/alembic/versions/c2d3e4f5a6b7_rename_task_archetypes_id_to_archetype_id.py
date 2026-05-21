"""rename task_archetypes.id to archetype_id

The DB was populated with the column named `id` but the SQLAlchemy model
(curriculum/models.py) maps it as `archetype_id`. Every SELECT on the ORM
fails with UndefinedColumn. Rename the column to match the model.

The FK from activity_attempts.archetype_id → task_archetypes.id is updated
automatically by PostgreSQL when the referenced column is renamed.

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-05-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "c2d3e4f5a6b7"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def _column_name_is(table: str, old: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(c["name"] == old for c in inspector.get_columns(table))


def upgrade() -> None:
    if _column_name_is("task_archetypes", "id"):
        op.alter_column("task_archetypes", "id", new_column_name="archetype_id")


def downgrade() -> None:
    if _column_name_is("task_archetypes", "archetype_id"):
        op.alter_column("task_archetypes", "archetype_id", new_column_name="id")
