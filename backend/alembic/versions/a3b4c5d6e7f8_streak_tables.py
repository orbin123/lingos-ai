"""streaks: daily_activities, streak_freeze_usages + user_profiles columns

Revision ID: a3b4c5d6e7f8
Revises: c2d3e4f5a678
Create Date: 2026-05-19 10:00:00.000000

Adds the streak / activity-grid feature:
  - daily_activities       — one row per (user, local_date) completed
  - streak_freeze_usages   — append-only log of automatic freeze spends
  - user_profiles          — seven new columns for streak state

Default timezone is Asia/Kolkata; default freeze count is 0 (strict mode).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a3b4c5d6e7f8"
down_revision: Union[str, Sequence[str], None] = "c2d3e4f5a678"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── user_profiles: seven new columns ─────────────────────────────
    op.add_column(
        "user_profiles",
        sa.Column(
            "timezone",
            sa.String(length=64),
            nullable=False,
            server_default="Asia/Kolkata",
        ),
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "current_streak",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "longest_streak",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "user_profiles",
        sa.Column("last_activity_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "streak_freezes",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "user_profiles",
        sa.Column("last_seen_streak_animation_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("last_animation_type", sa.String(length=16), nullable=True),
    )

    # ── daily_activities ─────────────────────────────────────────────
    op.create_table(
        "daily_activities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column(
            "activity_count",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column("last_session_id", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["last_session_id"],
            ["daily_sessions.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "local_date",
            name="uq_daily_activities_user_date",
        ),
    )
    op.create_index(
        "ix_daily_activities_user_id",
        "daily_activities",
        ["user_id"],
    )
    op.create_index(
        "ix_daily_activities_user_date",
        "daily_activities",
        ["user_id", "local_date"],
    )

    # ── streak_freeze_usages ─────────────────────────────────────────
    op.create_table(
        "streak_freeze_usages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("protected_date", sa.Date(), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "reason",
            sa.String(length=64),
            nullable=False,
            server_default="auto_missed_day_protection",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_streak_freeze_usages_user_id",
        "streak_freeze_usages",
        ["user_id"],
    )
    op.create_index(
        "ix_streak_freeze_usages_user_date",
        "streak_freeze_usages",
        ["user_id", "protected_date"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_streak_freeze_usages_user_date", table_name="streak_freeze_usages"
    )
    op.drop_index("ix_streak_freeze_usages_user_id", table_name="streak_freeze_usages")
    op.drop_table("streak_freeze_usages")

    op.drop_index("ix_daily_activities_user_date", table_name="daily_activities")
    op.drop_index("ix_daily_activities_user_id", table_name="daily_activities")
    op.drop_table("daily_activities")

    op.drop_column("user_profiles", "last_animation_type")
    op.drop_column("user_profiles", "last_seen_streak_animation_date")
    op.drop_column("user_profiles", "streak_freezes")
    op.drop_column("user_profiles", "last_activity_date")
    op.drop_column("user_profiles", "longest_streak")
    op.drop_column("user_profiles", "current_streak")
    op.drop_column("user_profiles", "timezone")
