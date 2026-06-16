"""sessions: repair missing activity_feedback table (Phase 8 prep)

Revision ID: d6e7f8a0b1c2
Revises: c5d6e7f8a0b1
Create Date: 2026-05-20 10:00:00.000000

Some development databases at head c5d6e7f8a0b1 are missing the
`activity_feedback` table that `e0f1a2b3c456_sessions_tables.py`
should have created. Root cause was a manual intervention outside
alembic; the alembic_version row still reports head, so a plain
upgrade would not re-create the table.

This migration is a self-healing repair. It runs immediately before
the Phase 8 destructive drop so anyone whose DB has the same gap
ends up with the new-flow schema intact before legacy tables go.

Upgrade: create `activity_feedback` only if it is missing. Safe on
a healthy DB where the table is already present.

Downgrade: unconditionally drop `activity_feedback`. The previous
state at `c5d6e7f8a0b1` was "table missing" — going back restores
that. Data loss on rollback is acceptable per the project's
"schema reversible, data lost" rollback contract.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "d6e7f8a0b1c2"
down_revision: Union[str, Sequence[str], None] = "c5d6e7f8a0b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "activity_feedback" in inspector.get_table_names():
        return

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
        "activity_feedback",
        ["attempt_id"],
        unique=True,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "activity_feedback" not in inspector.get_table_names():
        return

    op.drop_index(
        op.f("ix_activity_feedback_attempt_id"), table_name="activity_feedback"
    )
    op.drop_table("activity_feedback")
