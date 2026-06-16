"""progress: drop user_task_id FKs from progress_logs and skill_points_logs

Revision ID: c5d6e7f8a0b1
Revises: b4c5d6e7f9a0
Create Date: 2026-05-19 16:00:00.000000

Phase 8 cutover: the legacy `user_tasks` table is being dropped in a
later migration. Both `progress_logs` and `skill_points_logs` carried an
optional FK back to it; this migration removes those columns + the
indexes that backed them so the downstream table drop can succeed.

Forward-only data-loss: existing `user_task_id` values are discarded.
The points/skill history retains its `session_id` link for new-flow
entries.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "c5d6e7f8a0b1"
down_revision: Union[str, Sequence[str], None] = "b4c5d6e7f9a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # progress_logs
    try:
        op.drop_index("ix_progress_logs_user_task_id", table_name="progress_logs")
    except Exception:
        # Index may not exist on minimal/test schemas.
        pass
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TABLE progress_logs "
            "DROP CONSTRAINT IF EXISTS progress_logs_user_task_id_fkey"
        )
    op.drop_column("progress_logs", "user_task_id")

    # skill_points_logs
    try:
        op.drop_index(
            "ix_skill_points_logs_user_task_id", table_name="skill_points_logs"
        )
    except Exception:
        pass
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TABLE skill_points_logs "
            "DROP CONSTRAINT IF EXISTS skill_points_logs_user_task_id_fkey"
        )
    op.drop_column("skill_points_logs", "user_task_id")


def downgrade() -> None:
    op.add_column(
        "progress_logs",
        sa.Column("user_task_id", sa.Integer(), nullable=True),
    )
    op.create_index("ix_progress_logs_user_task_id", "progress_logs", ["user_task_id"])
    op.create_foreign_key(
        "progress_logs_user_task_id_fkey",
        "progress_logs",
        "user_tasks",
        ["user_task_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "skill_points_logs",
        sa.Column("user_task_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_skill_points_logs_user_task_id",
        "skill_points_logs",
        ["user_task_id"],
    )
    op.create_foreign_key(
        "skill_points_logs_user_task_id_fkey",
        "skill_points_logs",
        "user_tasks",
        ["user_task_id"],
        ["id"],
        ondelete="SET NULL",
    )
