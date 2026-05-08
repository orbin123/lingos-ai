"""add speak_with_tense to task_type_enum

Revision ID: l7g8h9i0j1k2
Revises: k6f7g8h9i0j1
Create Date: 2026-05-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "l7g8h9i0j1k2"
down_revision: Union[str, Sequence[str], None] = "k6f7g8h9i0j1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text("ALTER TYPE task_type_enum ADD VALUE IF NOT EXISTS 'speak_with_tense'")
    )


def downgrade() -> None:
    # Postgres cannot drop individual enum values without a full rebuild.
    # The value is harmless to leave in place; a full rebuild is only needed
    # if you truly need to remove it.
    pass
