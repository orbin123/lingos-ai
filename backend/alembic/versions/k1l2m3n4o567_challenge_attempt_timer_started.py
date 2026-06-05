"""challenge attempt timer_started_at

Revision ID: k1l2m3n4o567
Revises: j0k1l2m3n456
Create Date: 2026-06-05 16:00:00.000000

Adds timer_started_at and makes expires_at nullable so the sprint timer
starts only after the learner explicitly begins the attempt.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "k1l2m3n4o567"
down_revision: Union[str, Sequence[str], None] = "j0k1l2m3n456"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "challenge_attempts",
        sa.Column("timer_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.alter_column(
        "challenge_attempts",
        "expires_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "challenge_attempts",
        "expires_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
    op.drop_column("challenge_attempts", "timer_started_at")
