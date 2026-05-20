"""v2 session schema compatibility

Revision ID: e4f5a6b7c890
Revises: a3b4c5d6e7f8
Create Date: 2026-05-20 00:00:00.000000

Some databases were stamped past the v2 session migrations while still
carrying the earlier physical schema. This migration adds the natural day/session
columns that the current ORM expects and backfills them from the existing
curriculum week/day rows.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "e4f5a6b7c890"
down_revision: Union[str, Sequence[str], None] = "a3b4c5d6e7f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
    if not _has_column("curriculum_days", "day_id"):
        op.add_column("curriculum_days", sa.Column("day_id", sa.String(length=24)))

    op.execute(
        """
        UPDATE curriculum_days cd
        SET day_id = 'day_' || replace(cw.course_length::text, 'w', '') || '_' ||
            lpad(cw.week_number::text, 2, '0') || '_' ||
            lpad(cd.day_number::text, 2, '0')
        FROM curriculum_weeks cw
        WHERE cd.week_id = cw.id
          AND cd.day_id IS NULL
        """
    )
    op.alter_column("curriculum_days", "day_id", nullable=False)
    op.create_index(
        op.f("ix_curriculum_days_day_id"),
        "curriculum_days",
        ["day_id"],
        unique=True,
        if_not_exists=True,
    )

    if not _has_column("daily_sessions", "session_id"):
        op.add_column("daily_sessions", sa.Column("session_id", sa.String(length=36)))
    op.execute(
        """
        UPDATE daily_sessions
        SET session_id = 'legacy-' || id::text
        WHERE session_id IS NULL
        """
    )
    op.alter_column("daily_sessions", "session_id", nullable=False)
    op.create_index(
        op.f("ix_daily_sessions_session_id"),
        "daily_sessions",
        ["session_id"],
        unique=True,
        if_not_exists=True,
    )

    if not _has_column("daily_sessions", "day_id"):
        op.add_column("daily_sessions", sa.Column("day_id", sa.String(length=24)))
    if _has_column("daily_sessions", "curriculum_day_id"):
        op.execute(
            """
            UPDATE daily_sessions ds
            SET day_id = cd.day_id
            FROM curriculum_days cd
            WHERE ds.curriculum_day_id = cd.id
              AND ds.day_id IS NULL
            """
        )
    op.alter_column("daily_sessions", "day_id", nullable=False)
    op.create_index(
        op.f("ix_daily_sessions_day_id"),
        "daily_sessions",
        ["day_id"],
        unique=False,
        if_not_exists=True,
    )

    if not _has_column("daily_sessions", "is_first_attempt"):
        op.add_column(
            "daily_sessions",
            sa.Column(
                "is_first_attempt",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
        )
    op.alter_column("daily_sessions", "is_first_attempt", server_default=None)

    if not _has_column("activity_attempts", "is_mandatory"):
        op.add_column(
            "activity_attempts",
            sa.Column(
                "is_mandatory",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
        )
    op.alter_column("activity_attempts", "is_mandatory", server_default=None)


def downgrade() -> None:
    if _has_column("activity_attempts", "is_mandatory"):
        op.drop_column("activity_attempts", "is_mandatory")
    if _has_column("daily_sessions", "is_first_attempt"):
        op.drop_column("daily_sessions", "is_first_attempt")
    if _has_column("daily_sessions", "day_id"):
        op.drop_index(op.f("ix_daily_sessions_day_id"), table_name="daily_sessions")
        op.drop_column("daily_sessions", "day_id")
    if _has_column("daily_sessions", "session_id"):
        op.drop_index(op.f("ix_daily_sessions_session_id"), table_name="daily_sessions")
        op.drop_column("daily_sessions", "session_id")
    if _has_column("curriculum_days", "day_id"):
        op.drop_index(op.f("ix_curriculum_days_day_id"), table_name="curriculum_days")
        op.drop_column("curriculum_days", "day_id")
