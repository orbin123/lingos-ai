"""a2z_user_progress table

Revision ID: j0k1l2m3n456
Revises: i9j0k1l2m345
Create Date: 2026-06-05 14:00:00.000000

Adds the ``a2z_user_progress`` table for tracking per-user alphabet
progress in the A2Z Challenge game.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "j0k1l2m3n456"
down_revision: Union[str, Sequence[str], None] = "i9j0k1l2m345"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "a2z_user_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("cleared_letters", _JSON, nullable=False),
        sa.Column("game_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_restarted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "challenge_id", name="uq_a2z_user_progress_user_challenge"
        ),
    )
    op.create_index(
        "ix_a2z_user_progress_user_id",
        "a2z_user_progress",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_a2z_user_progress_challenge_id",
        "a2z_user_progress",
        ["challenge_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_a2z_user_progress_challenge_id", table_name="a2z_user_progress")
    op.drop_index("ix_a2z_user_progress_user_id", table_name="a2z_user_progress")
    op.drop_table("a2z_user_progress")
