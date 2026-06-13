"""feedback review system: extend app_reviews + feedback_prompt_logs

Revision ID: p6q7r8s9t012
Revises: o5p6q7r8s901
Create Date: 2026-06-13 14:00:00.000000

Adds the storage for the in-app feedback-prompt system:

- Six nullable columns on the existing ``app_reviews`` table so the prompt's
  structured fields (positive/improvement/bug) and submission-context snapshot
  (task count, days since signup, app version) live alongside the rating the
  admin "User Reviews" page already reads. All nullable → no backfill needed.
- ``feedback_prompt_logs``: one row per displayed prompt, driving cooldowns and
  the admin submission-rate metric.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "p6q7r8s9t012"
down_revision: Union[str, Sequence[str], None] = "o5p6q7r8s901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Extend app_reviews ────────────────────────────────────────────────
    op.add_column("app_reviews", sa.Column("positive_feedback", sa.Text(), nullable=True))
    op.add_column("app_reviews", sa.Column("improvement_feedback", sa.Text(), nullable=True))
    op.add_column("app_reviews", sa.Column("bug_report", sa.Text(), nullable=True))
    op.add_column(
        "app_reviews",
        sa.Column("task_count_when_submitted", sa.Integer(), nullable=True),
    )
    op.add_column("app_reviews", sa.Column("days_since_signup", sa.Integer(), nullable=True))
    op.add_column("app_reviews", sa.Column("app_version", sa.String(length=40), nullable=True))

    # ── feedback_prompt_logs ──────────────────────────────────────────────
    op.create_table(
        "feedback_prompt_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("prompted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "dismissed", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "submitted", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("trigger_type", sa.String(length=40), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        op.f("ix_feedback_prompt_logs_user_id"),
        "feedback_prompt_logs",
        ["user_id"],
    )
    op.create_index(
        "ix_feedback_prompt_user_created",
        "feedback_prompt_logs",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_feedback_prompt_user_created", table_name="feedback_prompt_logs"
    )
    op.drop_index(
        op.f("ix_feedback_prompt_logs_user_id"), table_name="feedback_prompt_logs"
    )
    op.drop_table("feedback_prompt_logs")

    op.drop_column("app_reviews", "app_version")
    op.drop_column("app_reviews", "days_since_signup")
    op.drop_column("app_reviews", "task_count_when_submitted")
    op.drop_column("app_reviews", "bug_report")
    op.drop_column("app_reviews", "improvement_feedback")
    op.drop_column("app_reviews", "positive_feedback")
