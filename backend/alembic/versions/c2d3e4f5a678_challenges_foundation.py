"""challenges foundation read tables

Revision ID: c2d3e4f5a678
Revises: f1a2b3c4d567
Create Date: 2026-05-18 12:00:00.000000

Adds generic challenge catalog, levels, and attempts tables. IELTS Sprint is
seeded by scripts/seed_ielts_challenge.py rather than by this schema migration.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "c2d3e4f5a678"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d567"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")
_ATTEMPT_STATUS = ("in_progress", "completed", "abandoned", "timed_out")


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        postgresql.ENUM(
            *_ATTEMPT_STATUS,
            name="challenge_attempt_status_enum",
        ).create(bind, checkfirst=True)

    op.create_table(
        "challenges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("short_description", sa.String(length=255), nullable=False),
        sa.Column("rules_md", sa.Text(), nullable=False),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_challenges_slug"), "challenges", ["slug"], unique=True)
    op.create_index(
        "ix_challenges_active_sort",
        "challenges",
        ["is_active", "sort_order"],
        unique=False,
    )

    op.create_table(
        "challenge_levels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("level_number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("time_limit_seconds", sa.Integer(), nullable=False),
        sa.Column("pass_threshold", sa.Numeric(precision=3, scale=1), nullable=False),
        sa.Column("config", _JSON, nullable=False),
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
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "challenge_id",
            "level_number",
            name="uq_challenge_levels_challenge_level",
        ),
    )
    op.create_index(
        "ix_challenge_levels_challenge_id",
        "challenge_levels",
        ["challenge_id"],
        unique=False,
    )

    op.create_table(
        "challenge_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("challenge_level_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                *_ATTEMPT_STATUS,
                name="challenge_attempt_status_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("task_payload", _JSON, nullable=False),
        sa.Column("response_payload", _JSON, nullable=True),
        sa.Column("overall_score", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column("section_scores", _JSON, nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=True),
        sa.Column("evaluation_report", _JSON, nullable=True),
        sa.Column("feedback_report", _JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["challenge_level_id"], ["challenge_levels.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_challenge_attempts_user_id"),
        "challenge_attempts",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_challenge_attempts_challenge_level_id"),
        "challenge_attempts",
        ["challenge_level_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_challenge_attempts_status"),
        "challenge_attempts",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_challenge_attempts_user_level_status",
        "challenge_attempts",
        ["user_id", "challenge_level_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_challenge_attempts_user_created_at",
        "challenge_attempts",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_challenge_attempts_expires_at",
        "challenge_attempts",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_challenge_attempts_expires_at", table_name="challenge_attempts")
    op.drop_index("ix_challenge_attempts_user_created_at", table_name="challenge_attempts")
    op.drop_index(
        "ix_challenge_attempts_user_level_status",
        table_name="challenge_attempts",
    )
    op.drop_index(op.f("ix_challenge_attempts_status"), table_name="challenge_attempts")
    op.drop_index(
        op.f("ix_challenge_attempts_challenge_level_id"),
        table_name="challenge_attempts",
    )
    op.drop_index(op.f("ix_challenge_attempts_user_id"), table_name="challenge_attempts")
    op.drop_table("challenge_attempts")

    op.drop_index("ix_challenge_levels_challenge_id", table_name="challenge_levels")
    op.drop_table("challenge_levels")

    op.drop_index("ix_challenges_active_sort", table_name="challenges")
    op.drop_index(op.f("ix_challenges_slug"), table_name="challenges")
    op.drop_table("challenges")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        sa.Enum(name="challenge_attempt_status_enum").drop(bind, checkfirst=True)
