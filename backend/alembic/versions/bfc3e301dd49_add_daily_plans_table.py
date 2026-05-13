"""add daily_plans table

Revision ID: bfc3e301dd49
Revises: o2p3q4r5s6t7
Create Date: 2026-05-13 17:59:59.614613

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bfc3e301dd49'
down_revision: Union[str, Sequence[str], None] = 'o2p3q4r5s6t7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'daily_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_slug', sa.String(length=50), nullable=False),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('day', sa.Integer(), nullable=False),
        sa.Column('topic_id', sa.String(length=16), nullable=False),
        sa.Column(
            'plan_json',
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'),
            nullable=False,
        ),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'user_id', 'course_slug', 'week', 'day',
            name='uq_daily_plan_user_day',
        ),
    )
    op.create_index(
        'ix_daily_plan_lookup', 'daily_plans',
        ['user_id', 'course_slug', 'week', 'day'], unique=False,
    )
    op.create_index(
        op.f('ix_daily_plans_course_slug'), 'daily_plans',
        ['course_slug'], unique=False,
    )
    op.create_index(
        op.f('ix_daily_plans_user_id'), 'daily_plans',
        ['user_id'], unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_daily_plans_user_id'), table_name='daily_plans')
    op.drop_index(op.f('ix_daily_plans_course_slug'), table_name='daily_plans')
    op.drop_index('ix_daily_plan_lookup', table_name='daily_plans')
    op.drop_table('daily_plans')
