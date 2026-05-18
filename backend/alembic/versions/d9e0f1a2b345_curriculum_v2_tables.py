"""curriculum v2: weeks, days, archetypes

Revision ID: d9e0f1a2b345
Revises: c8d9e0f1a234
Create Date: 2026-05-17 22:00:00.000000

Adds the three Phase 2 tables for the restructured flow:
  - curriculum_weeks
  - curriculum_days
  - task_archetypes

These run alongside the legacy `courses`, `user_enrollments`, `daily_plans`
tables. Phase 7 retires the legacy set; until then both schemas coexist.

The downgrade path drops the new tables and the three new Postgres enum
types (course_length_enum, theme_type_enum, core_activity_enum). Existing
enum types are untouched.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "d9e0f1a2b345"
down_revision: Union[str, Sequence[str], None] = "c8d9e0f1a234"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# JSON on SQLite, JSONB on Postgres — same column type pattern as existing migrations.
_JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "curriculum_weeks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("week_id", sa.String(length=16), nullable=False),
        sa.Column(
            "course_length",
            sa.Enum("24w", "48w", name="course_length_enum"),
            nullable=False,
        ),
        sa.Column("week_number", sa.Integer(), nullable=False),
        sa.Column(
            "theme_type",
            sa.Enum(
                "grammar", "communication", "vocabulary", "confidence",
                name="theme_type_enum",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("cefr_level", sa.String(length=8), nullable=False),
        sa.Column("sub_level_min", sa.Integer(), nullable=False),
        sa.Column("sub_level_max", sa.Integer(), nullable=False),
        sa.Column("learning_goal", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "course_length", "week_number", name="uq_curriculum_week"
        ),
    )
    op.create_index(
        op.f("ix_curriculum_weeks_week_id"),
        "curriculum_weeks", ["week_id"], unique=True,
    )
    op.create_index(
        "ix_curriculum_week_lookup",
        "curriculum_weeks", ["course_length", "week_number"], unique=False,
    )

    op.create_table(
        "curriculum_days",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("day_id", sa.String(length=24), nullable=False),
        sa.Column("week_id", sa.Integer(), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(length=200), nullable=False),
        sa.Column("explanation_brief", sa.Text(), nullable=False),
        sa.Column("default_activities", _JSON, nullable=False),
        sa.Column("mandatory_activities", _JSON, nullable=False),
        sa.Column("suggested_archetypes", _JSON, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["week_id"], ["curriculum_weeks.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("week_id", "day_number", name="uq_curriculum_day"),
    )
    op.create_index(
        op.f("ix_curriculum_days_day_id"),
        "curriculum_days", ["day_id"], unique=True,
    )
    op.create_index(
        op.f("ix_curriculum_days_week_id"),
        "curriculum_days", ["week_id"], unique=False,
    )

    op.create_table(
        "task_archetypes",
        sa.Column("archetype_id", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "core_activity",
            sa.Enum(
                "read", "write", "listen", "speak",
                name="core_activity_enum",
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("ui_widget", sa.String(length=60), nullable=False),
        sa.Column("themes_supported", _JSON, nullable=False),
        sa.Column("cefr_min", sa.String(length=8), nullable=False),
        sa.Column("cefr_max", sa.String(length=8), nullable=False),
        sa.Column("weight_map", _JSON, nullable=False),
        sa.Column("rubric", _JSON, nullable=False),
        sa.Column(
            "mvp",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("archetype_id"),
    )
    op.create_index(
        "ix_task_archetype_core_activity",
        "task_archetypes", ["core_activity"], unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_task_archetype_core_activity", table_name="task_archetypes")
    op.drop_table("task_archetypes")

    op.drop_index(op.f("ix_curriculum_days_week_id"), table_name="curriculum_days")
    op.drop_index(op.f("ix_curriculum_days_day_id"), table_name="curriculum_days")
    op.drop_table("curriculum_days")

    op.drop_index("ix_curriculum_week_lookup", table_name="curriculum_weeks")
    op.drop_index(op.f("ix_curriculum_weeks_week_id"), table_name="curriculum_weeks")
    op.drop_table("curriculum_weeks")

    # Drop the three Postgres enum types we created. On SQLite these are no-ops.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        sa.Enum(name="core_activity_enum").drop(bind, checkfirst=True)
        sa.Enum(name="theme_type_enum").drop(bind, checkfirst=True)
        sa.Enum(name="course_length_enum").drop(bind, checkfirst=True)
