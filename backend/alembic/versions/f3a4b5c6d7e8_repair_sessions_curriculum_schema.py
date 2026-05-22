"""repair sessions/curriculum schema drift

Revision ID: f3a4b5c6d7e8
Revises: e7f8a0b1c2d3
Create Date: 2026-05-20 09:45:00.000000

Some local databases were stamped to the latest Alembic head while still
holding an earlier draft shape of the curriculum/session tables. This
migration is intentionally defensive: it adds or renames only the columns
the current ORM requires, and is a no-op on databases already created from
the canonical migrations.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "f3a4b5c6d7e8"
down_revision: Union[str, Sequence[str], None] = "e7f8a0b1c2d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_JSON = sa.JSON().with_variant(
    postgresql.JSONB(astext_type=sa.Text()), "postgresql"
)


def _columns(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def _indexes(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {index["name"] for index in inspector.get_indexes(table_name)}


def _foreign_keys(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {
        constraint["name"]
        for constraint in inspector.get_foreign_keys(table_name)
        if constraint["name"]
    }


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    return sa.inspect(bind).has_table(table_name)


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if column.name not in _columns(table_name):
        op.add_column(table_name, column)


def _create_index_if_missing(
    name: str,
    table_name: str,
    columns: list[str],
    *,
    unique: bool = False,
) -> None:
    if name not in _indexes(table_name):
        op.create_index(name, table_name, columns, unique=unique)


def upgrade() -> None:
    bind = op.get_bind()

    if _has_table("curriculum_weeks"):
        if "week_id" not in _columns("curriculum_weeks"):
            op.add_column(
                "curriculum_weeks",
                sa.Column("week_id", sa.String(length=16), nullable=True),
            )
            bind.execute(sa.text(
                """
                UPDATE curriculum_weeks
                SET week_id = 'wk_' ||
                    CASE course_length::text
                        WHEN '24w' THEN '24'
                        WHEN '48w' THEN '48'
                        ELSE regexp_replace(course_length::text, '\\D', '', 'g')
                    END ||
                    '_' || lpad(week_number::text, 2, '0')
                WHERE week_id IS NULL
                """
            ))
            op.alter_column("curriculum_weeks", "week_id", nullable=False)
        _create_index_if_missing(
            "ix_curriculum_weeks_week_id",
            "curriculum_weeks",
            ["week_id"],
            unique=True,
        )

    if _has_table("curriculum_days"):
        if "day_id" not in _columns("curriculum_days"):
            op.add_column(
                "curriculum_days",
                sa.Column("day_id", sa.String(length=24), nullable=True),
            )
            bind.execute(sa.text(
                """
                UPDATE curriculum_days d
                SET day_id = 'day_' ||
                    CASE w.course_length::text
                        WHEN '24w' THEN '24'
                        WHEN '48w' THEN '48'
                        ELSE regexp_replace(w.course_length::text, '\\D', '', 'g')
                    END ||
                    '_' || lpad(w.week_number::text, 2, '0') ||
                    '_' || lpad(d.day_number::text, 2, '0')
                FROM curriculum_weeks w
                WHERE d.week_id = w.id
                  AND d.day_id IS NULL
                """
            ))
            op.alter_column("curriculum_days", "day_id", nullable=False)
        _create_index_if_missing(
            "ix_curriculum_days_day_id",
            "curriculum_days",
            ["day_id"],
            unique=True,
        )

    if _has_table("task_archetypes"):
        cols = _columns("task_archetypes")
        if "archetype_id" not in cols and "id" in cols:
            op.alter_column(
                "task_archetypes",
                "id",
                new_column_name="archetype_id",
                existing_type=sa.String(length=40),
                existing_nullable=False,
            )

    if _has_table("daily_sessions"):
        _add_column_if_missing(
            "daily_sessions",
            sa.Column("session_id", sa.String(length=36), nullable=True),
        )
        _add_column_if_missing(
            "daily_sessions",
            sa.Column("day_id", sa.String(length=24), nullable=True),
        )
        _add_column_if_missing(
            "daily_sessions",
            sa.Column(
                "is_first_attempt",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
        )

        cols = _columns("daily_sessions")
        if "curriculum_day_id" in cols:
            op.alter_column(
                "daily_sessions",
                "curriculum_day_id",
                existing_type=sa.Integer(),
                nullable=True,
            )
            bind.execute(sa.text(
                """
                UPDATE daily_sessions s
                SET day_id = d.day_id
                FROM curriculum_days d
                WHERE s.curriculum_day_id = d.id
                  AND s.day_id IS NULL
                """
            ))

        bind.execute(sa.text(
            """
            UPDATE daily_sessions
            SET session_id = 'legacy-' || id::text
            WHERE session_id IS NULL
            """
        ))

        if not bind.execute(sa.text(
            "SELECT EXISTS (SELECT 1 FROM daily_sessions WHERE session_id IS NULL)"
        )).scalar():
            op.alter_column("daily_sessions", "session_id", nullable=False)
        if not bind.execute(sa.text(
            "SELECT EXISTS (SELECT 1 FROM daily_sessions WHERE day_id IS NULL)"
        )).scalar():
            op.alter_column("daily_sessions", "day_id", nullable=False)

        _create_index_if_missing(
            "ix_daily_sessions_session_id",
            "daily_sessions",
            ["session_id"],
            unique=True,
        )
        _create_index_if_missing(
            "ix_daily_sessions_day_id",
            "daily_sessions",
            ["day_id"],
        )

    if _has_table("activity_attempts"):
        _add_column_if_missing(
            "activity_attempts",
            sa.Column(
                "is_mandatory",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
        )
        if "activity" in _columns("activity_attempts"):
            op.alter_column(
                "activity_attempts",
                "activity",
                existing_type=sa.String(length=20),
                nullable=True,
            )
        _create_index_if_missing(
            "ix_activity_attempts_archetype_id",
            "activity_attempts",
            ["archetype_id"],
        )

    if _has_table("activity_evaluations"):
        _add_column_if_missing(
            "activity_evaluations",
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        )

    if _has_table("session_scorecards"):
        _add_column_if_missing(
            "session_scorecards",
            sa.Column(
                "points_applied",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )
        _add_column_if_missing(
            "session_scorecards",
            sa.Column("activities", _JSON, nullable=True),
        )

    if _has_table("skill_points_logs"):
        _add_column_if_missing(
            "skill_points_logs",
            sa.Column("session_id", sa.Integer(), nullable=True),
        )
        if (
            _has_table("daily_sessions")
            and "fk_skill_points_logs_session_id_daily_sessions"
            not in _foreign_keys("skill_points_logs")
        ):
            op.create_foreign_key(
                "fk_skill_points_logs_session_id_daily_sessions",
                "skill_points_logs",
                "daily_sessions",
                ["session_id"],
                ["id"],
                ondelete="SET NULL",
            )
        _create_index_if_missing(
            "ix_skill_points_logs_session_id",
            "skill_points_logs",
            ["session_id"],
        )


def downgrade() -> None:
    # This migration repairs drift in local/dev schemas. Downgrade is kept
    # intentionally empty so we do not remove data-bearing compatibility
    # columns from affected databases.
    pass
