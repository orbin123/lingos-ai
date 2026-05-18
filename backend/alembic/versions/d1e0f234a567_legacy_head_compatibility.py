"""legacy head compatibility

Revision ID: d1e0f234a567
Revises: e0f1a2b3c456
Create Date: 2026-05-18 10:30:00.000000

Some local databases were stamped with this revision after the sessions
migration. The schema state matches e0f1a2b3c456, so this revision is a no-op
bridge that lets those databases continue to newer migrations.
"""

from typing import Sequence, Union


revision: str = "d1e0f234a567"
down_revision: Union[str, Sequence[str], None] = "e0f1a2b3c456"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
