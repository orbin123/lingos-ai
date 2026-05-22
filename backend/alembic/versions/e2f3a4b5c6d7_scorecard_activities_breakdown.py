"""add per-activity breakdown column to session_scorecards

Adds a nullable `activities` JSON column that stores the per-activity
score breakdown (archetype, raw_score, tier, base_reward, weighted_points)
for the end-of-session detailed scorecard UI. Existing rows stay NULL —
the frontend treats NULL as "legacy scorecard, no per-activity detail".

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-05-22

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e2f3a4b5c6d7"
down_revision: Union[str, Sequence[str], None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_JSON = sa.JSON().with_variant(sa.dialects.postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.add_column(
        "session_scorecards",
        sa.Column("activities", _JSON, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("session_scorecards", "activities")
