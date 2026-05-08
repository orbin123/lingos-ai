"""add daily practice settings

Revision ID: k6f7g8h9i0j1
Revises: j5e6f7g8h9i0
Create Date: 2026-05-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "k6f7g8h9i0j1"
down_revision: Union[str, Sequence[str], None] = "j5e6f7g8h9i0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user_enrollments",
        sa.Column(
            "allow_reading",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "user_enrollments",
        sa.Column(
            "allow_writing",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "user_enrollments",
        sa.Column(
            "allow_listening",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "user_enrollments",
        sa.Column(
            "allow_speaking",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "user_enrollments",
        sa.Column(
            "current_day_started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.add_column(
        "user_enrollments",
        sa.Column("last_completed_on", sa.Date(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("user_enrollments", "last_completed_on")
    op.drop_column("user_enrollments", "current_day_started_at")
    op.drop_column("user_enrollments", "allow_speaking")
    op.drop_column("user_enrollments", "allow_listening")
    op.drop_column("user_enrollments", "allow_writing")
    op.drop_column("user_enrollments", "allow_reading")
