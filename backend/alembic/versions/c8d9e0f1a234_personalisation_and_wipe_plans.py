"""add structured personalisation column and wipe stale daily plans

Revision ID: c8d9e0f1a234
Revises: b7c8d9e0f123
Create Date: 2026-05-15 12:00:00.000000

The user_profiles table gains two columns:
- structured_personalisation (JSONB) — cached output of the
  Personalization Engine, consumed by the planner / teacher / task
  generator / feedback agents.
- structured_personalisation_updated_at — staleness marker.

Existing daily_plans rows are deleted on upgrade. They were generated
under the old "Family & Home"-style topic_name semantics and would mix
inconsistently with new objective-driven plans. The plan cache is
lazy-regenerated on next session open, so no user-visible work is lost.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "c8d9e0f1a234"
down_revision: Union[str, Sequence[str], None] = "b7c8d9e0f123"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # JSONB on Postgres, plain JSON elsewhere (e.g. SQLite for tests).
    op.add_column(
        "user_profiles",
        sa.Column(
            "structured_personalisation",
            sa.JSON().with_variant(
                postgresql.JSONB(astext_type=sa.Text()), "postgresql"
            ),
            nullable=True,
        ),
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "structured_personalisation_updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # One-time wipe of the cached planner output. Daily plans regenerate
    # lazily on next session open, picking up the new objective-driven
    # curriculum + personalisation flow.
    op.execute("DELETE FROM daily_plans")


def downgrade() -> None:
    op.drop_column("user_profiles", "structured_personalisation_updated_at")
    op.drop_column("user_profiles", "structured_personalisation")
