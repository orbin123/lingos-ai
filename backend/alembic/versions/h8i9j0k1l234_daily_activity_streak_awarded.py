"""daily_activities: streak_awarded; widen last_animation_type

Revision ID: h8i9j0k1l234
Revises: 217aeaf4205d
Create Date: 2026-05-30 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "h8i9j0k1l234"
down_revision: Union[str, Sequence[str], None] = "217aeaf4205d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "daily_activities",
        sa.Column(
            "streak_awarded",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
    )
    op.alter_column(
        "user_profiles",
        "last_animation_type",
        existing_type=sa.String(length=16),
        type_=sa.String(length=20),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "user_profiles",
        "last_animation_type",
        existing_type=sa.String(length=20),
        type_=sa.String(length=16),
        existing_nullable=True,
    )
    op.drop_column("daily_activities", "streak_awarded")
