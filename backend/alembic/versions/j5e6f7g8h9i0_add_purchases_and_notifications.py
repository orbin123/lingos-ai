"""add_purchases_and_notifications

Revision ID: j5e6f7g8h9i0
Revises: i4d5e6f7g8h9
Create Date: 2026-05-07 13:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "j5e6f7g8h9i0"
down_revision: Union[str, Sequence[str], None] = "i4d5e6f7g8h9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user_profiles",
        sa.Column("daily_practice_reminder", sa.Boolean(), server_default="true", nullable=False),
    )
    op.add_column(
        "user_profiles",
        sa.Column("streak_reminder", sa.Boolean(), server_default="true", nullable=False),
    )
    op.add_column(
        "user_profiles",
        sa.Column("weekly_progress_email", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "user_profiles",
        sa.Column("feature_announcements", sa.Boolean(), server_default="false", nullable=False),
    )
    op.create_table(
        "purchases",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.String(length=50), nullable=False),
        sa.Column("plan_name", sa.String(length=120), nullable=False),
        sa.Column("amount_paid", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="INR", nullable=False),
        sa.Column("status", sa.String(length=30), server_default="paid", nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_purchases_plan_id"), "purchases", ["plan_id"], unique=False)
    op.create_index(op.f("ix_purchases_status"), "purchases", ["status"], unique=False)
    op.create_index(op.f("ix_purchases_user_id"), "purchases", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_purchases_user_id"), table_name="purchases")
    op.drop_index(op.f("ix_purchases_status"), table_name="purchases")
    op.drop_index(op.f("ix_purchases_plan_id"), table_name="purchases")
    op.drop_table("purchases")
    op.drop_column("user_profiles", "feature_announcements")
    op.drop_column("user_profiles", "weekly_progress_email")
    op.drop_column("user_profiles", "streak_reminder")
    op.drop_column("user_profiles", "daily_practice_reminder")
