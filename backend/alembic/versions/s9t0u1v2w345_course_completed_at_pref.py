"""course completion timestamp on preferences

Revision ID: s9t0u1v2w345
Revises: r8s9t0u1v234
Create Date: 2026-06-22 12:00:00.000000

Adds a nullable course_completed_at to user_course_preferences. It is stamped
once, the moment a learner finishes the final day of their course, and drives
the dashboard "course complete" state plus the completion certificate. Null for
everyone still in progress, so the column is inert for existing learners.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "s9t0u1v2w345"
down_revision: Union[str, Sequence[str], None] = "r8s9t0u1v234"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_course_preferences",
        sa.Column(
            "course_completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("user_course_preferences", "course_completed_at")
