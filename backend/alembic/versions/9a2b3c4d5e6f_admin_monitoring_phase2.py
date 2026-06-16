"""admin monitoring phase 2

Revision ID: 9a2b3c4d5e6f
Revises: 5c6d7e8f9012
Create Date: 2026-05-14 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "9a2b3c4d5e6f"
down_revision: Union[str, Sequence[str], None] = "5c6d7e8f9012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_audit_logs",
        sa.Column("admin_user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=120), nullable=False),
        sa.Column(
            "old_value",
            sa.JSON().with_variant(
                postgresql.JSONB(astext_type=sa.Text()),
                "postgresql",
            ),
            nullable=True,
        ),
        sa.Column(
            "new_value",
            sa.JSON().with_variant(
                postgresql.JSONB(astext_type=sa.Text()),
                "postgresql",
            ),
            nullable=True,
        ),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["admin_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_admin_audit_logs_action"),
        "admin_audit_logs",
        ["action"],
        unique=False,
    )
    op.create_index(
        op.f("ix_admin_audit_logs_admin_user_id"),
        "admin_audit_logs",
        ["admin_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_admin_audit_logs_resource_id"),
        "admin_audit_logs",
        ["resource_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_admin_audit_logs_resource_type"),
        "admin_audit_logs",
        ["resource_type"],
        unique=False,
    )

    op.create_table(
        "ai_request_logs",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("trace_id", sa.String(length=120), nullable=True),
        sa.Column("agent_name", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("prompt_version", sa.String(length=120), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ai_request_logs_agent_name"),
        "ai_request_logs",
        ["agent_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_request_logs_status"),
        "ai_request_logs",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_request_logs_trace_id"),
        "ai_request_logs",
        ["trace_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_request_logs_user_id"),
        "ai_request_logs",
        ["user_id"],
        unique=False,
    )

    with op.batch_alter_table("feedbacks") as batch_op:
        batch_op.add_column(
            sa.Column(
                "review_status",
                sa.String(length=30),
                server_default="pending",
                nullable=False,
            )
        )
        batch_op.add_column(sa.Column("reviewed_by", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(sa.Column("admin_note", sa.Text(), nullable=True))
        batch_op.create_foreign_key(
            "fk_feedbacks_reviewed_by_users",
            "users",
            ["reviewed_by"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index(
            op.f("ix_feedbacks_review_status"),
            ["review_status"],
            unique=False,
        )
        batch_op.create_index(
            op.f("ix_feedbacks_reviewed_by"),
            ["reviewed_by"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("feedbacks") as batch_op:
        batch_op.drop_index(op.f("ix_feedbacks_reviewed_by"))
        batch_op.drop_index(op.f("ix_feedbacks_review_status"))
        batch_op.drop_constraint(
            "fk_feedbacks_reviewed_by_users",
            type_="foreignkey",
        )
        batch_op.drop_column("admin_note")
        batch_op.drop_column("reviewed_at")
        batch_op.drop_column("reviewed_by")
        batch_op.drop_column("review_status")

    op.drop_index(op.f("ix_ai_request_logs_user_id"), table_name="ai_request_logs")
    op.drop_index(op.f("ix_ai_request_logs_trace_id"), table_name="ai_request_logs")
    op.drop_index(op.f("ix_ai_request_logs_status"), table_name="ai_request_logs")
    op.drop_index(op.f("ix_ai_request_logs_agent_name"), table_name="ai_request_logs")
    op.drop_table("ai_request_logs")

    op.drop_index(
        op.f("ix_admin_audit_logs_resource_type"),
        table_name="admin_audit_logs",
    )
    op.drop_index(
        op.f("ix_admin_audit_logs_resource_id"),
        table_name="admin_audit_logs",
    )
    op.drop_index(
        op.f("ix_admin_audit_logs_admin_user_id"),
        table_name="admin_audit_logs",
    )
    op.drop_index(op.f("ix_admin_audit_logs_action"), table_name="admin_audit_logs")
    op.drop_table("admin_audit_logs")
