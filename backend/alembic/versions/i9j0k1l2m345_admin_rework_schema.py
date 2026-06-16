"""admin rework: purchase access window, feedback reviews/ratings, app reviews

Revision ID: i9j0k1l2m345
Revises: h8i9j0k1l234
Create Date: 2026-06-05 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "i9j0k1l2m345"
down_revision: Union[str, Sequence[str], None] = "h8i9j0k1l234"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── purchases.access_expires_at (+ 2-year backfill) ──────────────
    op.add_column(
        "purchases",
        sa.Column("access_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        op.f("ix_purchases_access_expires_at"),
        "purchases",
        ["access_expires_at"],
    )
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "UPDATE purchases "
            "SET access_expires_at = created_at + INTERVAL '2 years' "
            "WHERE access_expires_at IS NULL"
        )
    else:
        # SQLite and friends: datetime() with a relative modifier.
        op.execute(
            "UPDATE purchases "
            "SET access_expires_at = datetime(created_at, '+2 years') "
            "WHERE access_expires_at IS NULL"
        )

    # ── feedback_reviews ─────────────────────────────────────────────
    op.create_table(
        "feedback_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("feedback_type", sa.String(length=20), nullable=False),
        sa.Column("feedback_id", sa.Integer(), nullable=False),
        sa.Column(
            "review_status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("admin_note", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint(
            "feedback_type", "feedback_id", name="uq_feedback_review_target"
        ),
    )
    op.create_index(
        op.f("ix_feedback_reviews_feedback_type"),
        "feedback_reviews",
        ["feedback_type"],
    )
    op.create_index(
        op.f("ix_feedback_reviews_feedback_id"),
        "feedback_reviews",
        ["feedback_id"],
    )
    op.create_index(
        op.f("ix_feedback_reviews_review_status"),
        "feedback_reviews",
        ["review_status"],
    )

    # ── feedback_ratings ─────────────────────────────────────────────
    op.create_table(
        "feedback_ratings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scorecard_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.String(length=10), nullable=False),
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
            ["scorecard_id"], ["session_scorecards.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("scorecard_id", "user_id", name="uq_feedback_rating_user"),
    )
    op.create_index(
        op.f("ix_feedback_ratings_scorecard_id"),
        "feedback_ratings",
        ["scorecard_id"],
    )
    op.create_index(
        op.f("ix_feedback_ratings_user_id"),
        "feedback_ratings",
        ["user_id"],
    )

    # ── app_reviews ──────────────────────────────────────────────────
    op.create_table(
        "app_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="published",
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_app_reviews_user_id"), "app_reviews", ["user_id"])
    op.create_index(op.f("ix_app_reviews_status"), "app_reviews", ["status"])

    # ── prune retired task_templates.* permissions ───────────────────
    # Task Templates were removed in this rework; drop the now-orphaned
    # permission rows (and their role grants) so they stop showing up in
    # the Roles & Permissions admin surface. Harmless if already absent.
    op.execute(
        "DELETE FROM role_permissions WHERE permission_id IN ("
        "  SELECT id FROM permissions WHERE key LIKE 'task_templates.%'"
        ")"
    )
    op.execute("DELETE FROM permissions WHERE key LIKE 'task_templates.%'")


def downgrade() -> None:
    op.drop_index(op.f("ix_app_reviews_status"), table_name="app_reviews")
    op.drop_index(op.f("ix_app_reviews_user_id"), table_name="app_reviews")
    op.drop_table("app_reviews")

    op.drop_index(op.f("ix_feedback_ratings_user_id"), table_name="feedback_ratings")
    op.drop_index(
        op.f("ix_feedback_ratings_scorecard_id"), table_name="feedback_ratings"
    )
    op.drop_table("feedback_ratings")

    op.drop_index(
        op.f("ix_feedback_reviews_review_status"), table_name="feedback_reviews"
    )
    op.drop_index(
        op.f("ix_feedback_reviews_feedback_id"), table_name="feedback_reviews"
    )
    op.drop_index(
        op.f("ix_feedback_reviews_feedback_type"), table_name="feedback_reviews"
    )
    op.drop_table("feedback_reviews")

    op.drop_index(op.f("ix_purchases_access_expires_at"), table_name="purchases")
    op.drop_column("purchases", "access_expires_at")
