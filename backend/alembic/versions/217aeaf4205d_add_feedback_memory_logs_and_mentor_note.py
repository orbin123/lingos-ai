"""add_feedback_memory_logs_and_mentor_note

Revision ID: 217aeaf4205d
Revises: g4h5i6j7k890
Create Date: 2026-05-23 23:20:11.966245

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "217aeaf4205d"
down_revision: Union[str, Sequence[str], None] = "g4h5i6j7k890"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add feedback_memory_logs table and mentor_note column."""
    # 1. Create feedback_memory_logs table
    op.create_table(
        "feedback_memory_logs",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("attempt_id", sa.Integer(), nullable=True),
        sa.Column("memory_type", sa.String(length=30), nullable=False),
        sa.Column("vector_id", sa.String(length=120), nullable=False),
        sa.Column("document_text", sa.Text(), nullable=False),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["attempt_id"], ["activity_attempts.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["session_id"], ["daily_sessions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vector_id"),
    )
    op.create_index(
        "ix_feedback_memory_session",
        "feedback_memory_logs",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        "ix_feedback_memory_user", "feedback_memory_logs", ["user_id"], unique=False
    )

    # 2. Add mentor_note column to session_scorecards
    op.add_column(
        "session_scorecards", sa.Column("mentor_note", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    """Remove feedback_memory_logs table and mentor_note column."""
    op.drop_column("session_scorecards", "mentor_note")
    op.drop_index("ix_feedback_memory_user", table_name="feedback_memory_logs")
    op.drop_index("ix_feedback_memory_session", table_name="feedback_memory_logs")
    op.drop_table("feedback_memory_logs")
