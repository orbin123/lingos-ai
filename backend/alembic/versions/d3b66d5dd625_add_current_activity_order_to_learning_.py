"""add current_activity_order to learning_sessions

Revision ID: d3b66d5dd625
Revises: bfc3e301dd49
Create Date: 2026-05-13 18:39:21.916275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd3b66d5dd625'
down_revision: Union[str, Sequence[str], None] = 'bfc3e301dd49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'learning_sessions',
        sa.Column(
            'current_activity_order',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('1'),
        ),
    )
    # Drop the server default once existing rows are backfilled — going
    # forward the application supplies the value explicitly.
    op.alter_column('learning_sessions', 'current_activity_order', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('learning_sessions', 'current_activity_order')
