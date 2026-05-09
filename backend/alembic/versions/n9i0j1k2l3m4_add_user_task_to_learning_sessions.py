"""add user_task link to learning_sessions

Revision ID: n9i0j1k2l3m4
Revises: m8h9i0j1k2l3
Create Date: 2026-05-09 14:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "n9i0j1k2l3m4"
down_revision: Union[str, Sequence[str], None] = "m8h9i0j1k2l3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "learning_sessions",
        sa.Column("user_task_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_learning_sessions_user_task_id"),
        "learning_sessions",
        ["user_task_id"],
        unique=False,
    )
    op.create_foreign_key(
        op.f("fk_learning_sessions_user_task_id_user_tasks"),
        "learning_sessions",
        "user_tasks",
        ["user_task_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_learning_sessions_user_task_id_user_tasks"),
        "learning_sessions",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_learning_sessions_user_task_id"),
        table_name="learning_sessions",
    )
    op.drop_column("learning_sessions", "user_task_id")
