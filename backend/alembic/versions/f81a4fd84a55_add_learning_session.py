"""add_learning_session

Revision ID: f81a4fd84a55
Revises: l7g8h9i0j1k2
Create Date: 2026-05-08 11:31:08.604250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f81a4fd84a55'
down_revision: Union[str, Sequence[str], None] = 'l7g8h9i0j1k2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'learning_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('enrollment_id', sa.Integer(), nullable=False),
        sa.Column('phase', sa.String(length=32), nullable=False),
        sa.Column('topic', sa.String(length=200), nullable=False),
        sa.Column('skill_name', sa.String(length=50), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('task_type', sa.String(length=50), nullable=False),
        sa.Column('user_level', sa.Integer(), nullable=False),
        sa.Column('pre_generated_tasks', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('current_task_index', sa.Integer(), nullable=False),
        sa.Column('messages', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('user_submission', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('evaluation', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('feedback', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('understanding_confirmed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['enrollment_id'], ['user_enrollments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_learning_sessions_enrollment_id'),
        'learning_sessions',
        ['enrollment_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_learning_sessions_session_id'),
        'learning_sessions',
        ['session_id'],
        unique=True,
    )
    op.create_index(
        op.f('ix_learning_sessions_user_id'),
        'learning_sessions',
        ['user_id'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_learning_sessions_user_id'), table_name='learning_sessions')
    op.drop_index(op.f('ix_learning_sessions_session_id'), table_name='learning_sessions')
    op.drop_index(op.f('ix_learning_sessions_enrollment_id'), table_name='learning_sessions')
    op.drop_table('learning_sessions')
