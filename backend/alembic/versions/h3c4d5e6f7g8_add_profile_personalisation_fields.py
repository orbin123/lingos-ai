"""add_profile_personalisation_fields

Revision ID: h3c4d5e6f7g8
Revises: g2b3c4d5e6f7
Create Date: 2026-05-07 11:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "h3c4d5e6f7g8"
down_revision: Union[str, Sequence[str], None] = "g2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("user_profiles", sa.Column("phone_number", sa.String(length=40), nullable=True))
    op.add_column("user_profiles", sa.Column("country", sa.String(length=80), nullable=True))
    op.add_column("user_profiles", sa.Column("native_language", sa.String(length=80), nullable=True))
    op.add_column(
        "user_profiles",
        sa.Column("primary_goals", sa.String(length=500), server_default="", nullable=False),
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "personalisation_context",
            sa.String(length=500),
            server_default="",
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("user_profiles", "personalisation_context")
    op.drop_column("user_profiles", "primary_goals")
    op.drop_column("user_profiles", "native_language")
    op.drop_column("user_profiles", "country")
    op.drop_column("user_profiles", "phone_number")
