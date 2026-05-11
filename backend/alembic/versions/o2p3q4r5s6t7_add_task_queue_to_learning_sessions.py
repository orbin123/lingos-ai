"""add task queue to learning sessions

Revision ID: o2p3q4r5s6t7
Revises: n9i0j1k2l3m4, d361e3b599b2
Create Date: 2026-05-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "o2p3q4r5s6t7"
down_revision: Union[str, Sequence[str], None] = ("n9i0j1k2l3m4", "d361e3b599b2")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE user_enrollments SET tasks_per_day = 2 WHERE tasks_per_day < 2")
    op.execute("UPDATE user_enrollments SET tasks_per_day = 4 WHERE tasks_per_day > 4")
    op.create_check_constraint(
        "ck_user_enrollments_tasks_per_day_2_4",
        "user_enrollments",
        "tasks_per_day BETWEEN 2 AND 4",
    )
    op.add_column(
        "learning_sessions",
        sa.Column(
            "task_queue",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.alter_column("learning_sessions", "task_queue", server_default=None)


def downgrade() -> None:
    op.drop_column("learning_sessions", "task_queue")
    op.drop_constraint(
        "ck_user_enrollments_tasks_per_day_2_4",
        "user_enrollments",
        type_="check",
    )
