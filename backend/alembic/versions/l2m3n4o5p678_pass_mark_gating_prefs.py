"""pass-mark gating preferences

Revision ID: l2m3n4o5p678
Revises: k1l2m3n4o567
Create Date: 2026-06-09 12:00:00.000000

Adds require_pass_to_advance and pass_threshold_pct to user_course_preferences
so a learner can opt into mastery-based advancement (retry an activity until
they clear the threshold). Off by default; threshold defaults to 65%.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "l2m3n4o5p678"
down_revision: Union[str, Sequence[str], None] = "k1l2m3n4o567"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_course_preferences",
        sa.Column(
            "require_pass_to_advance",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.add_column(
        "user_course_preferences",
        sa.Column(
            "pass_threshold_pct",
            sa.Integer(),
            nullable=False,
            server_default="65",
        ),
    )
    op.create_check_constraint(
        "ck_user_course_preferences_pass_threshold_0_100",
        "user_course_preferences",
        "pass_threshold_pct BETWEEN 0 AND 100",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_user_course_preferences_pass_threshold_0_100",
        "user_course_preferences",
        type_="check",
    )
    op.drop_column("user_course_preferences", "pass_threshold_pct")
    op.drop_column("user_course_preferences", "require_pass_to_advance")
