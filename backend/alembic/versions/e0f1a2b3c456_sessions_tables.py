"""sessions: daily_sessions, attempts, evaluations, feedback, scorecards

Revision ID: e0f1a2b3c456
Revises: d9e0f1a2b345
Create Date: 2026-05-18 09:30:00.000000

Adds the Phase 3 session-lifecycle tables:
  - daily_sessions
  - activity_attempts
  - activity_evaluations
  - activity_feedback
  - session_scorecards

Plus a nullable `session_id` FK on `skill_points_logs` so points written via
the new sessions path can be audited back to the session they came from.

These tables coexist with the legacy `learning_sessions`, `user_responses`,
`evaluations`, `feedbacks` tables (Phase 7 retires them).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "e0f1a2b3c456"
down_revision: Union[str, Sequence[str], None] = "d9e0f1a2b345"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    # daily_sessions: course_length_enum exists from the curriculum_v2 migration;
    # session_status_enum is new here.
    op.create_table(
        "daily_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("day_id", sa.String(length=24), nullable=False),
        sa.Column(
            "course_length",
            sa.Enum("24w", "48w", name="course_length_enum", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "in_progress", "completed", "abandoned",
                name="session_status_enum",
            ),
            nullable=False,
        ),
        sa.Column("is_first_attempt", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["day_id"], ["curriculum_days.day_id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_daily_sessions_session_id"),
        "daily_sessions", ["session_id"], unique=True,
    )
    op.create_index(
        op.f("ix_daily_sessions_user_id"),
        "daily_sessions", ["user_id"], unique=False,
    )
    op.create_index(
        op.f("ix_daily_sessions_day_id"),
        "daily_sessions", ["day_id"], unique=False,
    )
    op.create_index(
        op.f("ix_daily_sessions_status"),
        "daily_sessions", ["status"], unique=False,
    )

    # activity_attempts
    op.create_table(
        "activity_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("archetype_id", sa.String(length=40), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("is_mandatory", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "submitted", "evaluated",
                name="attempt_status_enum",
            ),
            nullable=False,
        ),
        sa.Column("task_content", _JSON, nullable=False),
        sa.Column("user_response", _JSON, nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
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
            ["session_id"], ["daily_sessions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["archetype_id"], ["task_archetypes.archetype_id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "sequence", name="uq_activity_attempt_sequence"),
    )
    op.create_index(
        op.f("ix_activity_attempts_session_id"),
        "activity_attempts", ["session_id"], unique=False,
    )
    op.create_index(
        op.f("ix_activity_attempts_archetype_id"),
        "activity_attempts", ["archetype_id"], unique=False,
    )

    # activity_evaluations
    op.create_table(
        "activity_evaluations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("attempt_id", sa.Integer(), nullable=False),
        sa.Column("raw_score", sa.Numeric(precision=4, scale=1), nullable=False),
        sa.Column("rubric_scores", _JSON, nullable=False),
        sa.Column("base_reward", sa.Integer(), nullable=False),
        sa.Column("weighted_points", _JSON, nullable=False),
        sa.Column("evaluator_notes", sa.Text(), nullable=True),
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
            ["attempt_id"], ["activity_attempts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("attempt_id", name="uq_activity_evaluation_attempt"),
    )
    op.create_index(
        op.f("ix_activity_evaluations_attempt_id"),
        "activity_evaluations", ["attempt_id"], unique=True,
    )

    # activity_feedback
    op.create_table(
        "activity_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("attempt_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("did_well", _JSON, nullable=False),
        sa.Column("mistakes", _JSON, nullable=False),
        sa.Column("next_tip", sa.Text(), nullable=True),
        sa.Column("sub_skill_breakdown", _JSON, nullable=False),
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
            ["attempt_id"], ["activity_attempts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("attempt_id", name="uq_activity_feedback_attempt"),
    )
    op.create_index(
        op.f("ix_activity_feedback_attempt_id"),
        "activity_feedback", ["attempt_id"], unique=True,
    )

    # session_scorecards
    op.create_table(
        "session_scorecards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("points_earned", _JSON, nullable=False),
        sa.Column("subskill_totals_after", _JSON, nullable=False),
        sa.Column("dashboard_after", _JSON, nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "points_applied",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"], ["daily_sessions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", name="uq_session_scorecard"),
    )
    op.create_index(
        op.f("ix_session_scorecards_session_id"),
        "session_scorecards", ["session_id"], unique=True,
    )

    # skill_points_logs: nullable session_id FK linking to daily_sessions.
    op.add_column(
        "skill_points_logs",
        sa.Column("session_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_skill_points_logs_session_id_daily_sessions",
        "skill_points_logs", "daily_sessions",
        ["session_id"], ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_skill_points_logs_session_id"),
        "skill_points_logs", ["session_id"], unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_skill_points_logs_session_id"), table_name="skill_points_logs")
    op.drop_constraint(
        "fk_skill_points_logs_session_id_daily_sessions",
        "skill_points_logs", type_="foreignkey",
    )
    op.drop_column("skill_points_logs", "session_id")

    op.drop_index(
        op.f("ix_session_scorecards_session_id"),
        table_name="session_scorecards",
    )
    op.drop_table("session_scorecards")

    op.drop_index(op.f("ix_activity_feedback_attempt_id"), table_name="activity_feedback")
    op.drop_table("activity_feedback")

    op.drop_index(op.f("ix_activity_evaluations_attempt_id"), table_name="activity_evaluations")
    op.drop_table("activity_evaluations")

    op.drop_index(op.f("ix_activity_attempts_archetype_id"), table_name="activity_attempts")
    op.drop_index(op.f("ix_activity_attempts_session_id"), table_name="activity_attempts")
    op.drop_table("activity_attempts")

    op.drop_index(op.f("ix_daily_sessions_status"), table_name="daily_sessions")
    op.drop_index(op.f("ix_daily_sessions_day_id"), table_name="daily_sessions")
    op.drop_index(op.f("ix_daily_sessions_user_id"), table_name="daily_sessions")
    op.drop_index(op.f("ix_daily_sessions_session_id"), table_name="daily_sessions")
    op.drop_table("daily_sessions")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        sa.Enum(name="attempt_status_enum").drop(bind, checkfirst=True)
        sa.Enum(name="session_status_enum").drop(bind, checkfirst=True)
