"""feedback reactions: unify learner 👍/👎; drop moderation tables

Revision ID: q7r8s9t0u123
Revises: p6q7r8s9t012
Create Date: 2026-06-13 16:00:00.000000

Replaces the Coach's-Note-only ``feedback_ratings`` and the admin-moderation
``feedback_reviews`` with one unified ``feedback_reactions`` table that captures
learner reactions to BOTH per-activity feedback and the session Coach's Note:

- Creates ``feedback_reactions`` (user_id, feedback_id, feedback_type, reaction)
  with a unique constraint per (user_id, feedback_id, feedback_type). Reaction
  values are plain strings (LIKE/DISLIKE today, FLAGGED_* later) so new kinds
  need no migration.
- Migrates every existing ``feedback_ratings`` row into it as a COACH_NOTE
  reaction (feedback_id = scorecard_id, reaction = UPPER(value)).
- Drops ``feedback_ratings`` and ``feedback_reviews`` (the moderation workflow
  no longer exists — users, not admins, evaluate feedback).

``downgrade`` recreates both tables and copies the COACH_NOTE reactions back.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "q7r8s9t0u123"
down_revision: Union[str, Sequence[str], None] = "p6q7r8s9t012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── feedback_reactions ───────────────────────────────────────────────
    op.create_table(
        "feedback_reactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("feedback_id", sa.Integer(), nullable=False),
        sa.Column("feedback_type", sa.String(length=40), nullable=False),
        sa.Column("reaction", sa.String(length=40), nullable=False),
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
        sa.UniqueConstraint(
            "user_id",
            "feedback_id",
            "feedback_type",
            name="uq_feedback_reaction_target",
        ),
    )
    op.create_index(
        op.f("ix_feedback_reactions_user_id"), "feedback_reactions", ["user_id"]
    )
    op.create_index(
        op.f("ix_feedback_reactions_feedback_id"),
        "feedback_reactions",
        ["feedback_id"],
    )
    op.create_index(
        op.f("ix_feedback_reactions_feedback_type"),
        "feedback_reactions",
        ["feedback_type"],
    )

    # Carry forward existing Coach's-Note ratings as COACH_NOTE reactions.
    op.execute(
        sa.text(
            """
            INSERT INTO feedback_reactions
                (user_id, feedback_id, feedback_type, reaction,
                 created_at, updated_at)
            SELECT user_id, scorecard_id, 'COACH_NOTE', UPPER(value),
                   created_at, updated_at
            FROM feedback_ratings
            """
        )
    )

    # ── Drop the retired tables ──────────────────────────────────────────
    op.drop_index(
        op.f("ix_feedback_ratings_user_id"), table_name="feedback_ratings"
    )
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


def downgrade() -> None:
    # ── Recreate feedback_reviews ────────────────────────────────────────
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

    # ── Recreate feedback_ratings ────────────────────────────────────────
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
        sa.UniqueConstraint(
            "scorecard_id", "user_id", name="uq_feedback_rating_user"
        ),
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

    # Copy the Coach's-Note reactions back into the legacy rating table.
    op.execute(
        sa.text(
            """
            INSERT INTO feedback_ratings
                (scorecard_id, user_id, value, created_at, updated_at)
            SELECT feedback_id, user_id, LOWER(reaction), created_at, updated_at
            FROM feedback_reactions
            WHERE feedback_type = 'COACH_NOTE'
              AND reaction IN ('LIKE', 'DISLIKE')
            """
        )
    )

    op.drop_index(
        op.f("ix_feedback_reactions_feedback_type"), table_name="feedback_reactions"
    )
    op.drop_index(
        op.f("ix_feedback_reactions_feedback_id"), table_name="feedback_reactions"
    )
    op.drop_index(
        op.f("ix_feedback_reactions_user_id"), table_name="feedback_reactions"
    )
    op.drop_table("feedback_reactions")
