"""merge heads: 7024024c9c33 and cba14daab518

Merges all independent migration branches so alembic has a single head.
No schema changes — this is a bookkeeping-only migration.

Revision ID: aaa000000001
Revises: 7024024c9c33, cba14daab518
Create Date: 2026-05-04 12:00:00.000000

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "aaa000000001"
down_revision: Union[str, Sequence[str], None] = ("7024024c9c33", "cba14daab518")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No schema changes — merge only."""
    pass


def downgrade() -> None:
    """No schema changes — merge only."""
    pass
