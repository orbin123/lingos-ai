"""admin permissions and billing phase 3

Revision ID: b7c8d9e0f123
Revises: 9a2b3c4d5e6f
Create Date: 2026-05-15 09:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7c8d9e0f123"
down_revision: Union[str, Sequence[str], None] = "9a2b3c4d5e6f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PERMISSIONS = (
    ("users.read", "View user accounts in the admin console."),
    ("users.update_status", "Activate or deactivate user accounts."),
    ("users.view_progress", "View learner progress and task history."),
    ("task_templates.read", "View task templates."),
    ("task_templates.create", "Create task templates."),
    ("task_templates.update", "Update task templates."),
    ("task_templates.archive", "Archive task templates."),
    ("feedback_logs.read", "View feedback review queues and logs."),
    ("feedback_quality.review", "Review and annotate AI feedback quality."),
    ("ai_logs.read", "View AI request logs."),
    ("ai_costs.read", "View AI usage and cost information."),
    ("payments.read", "View limited payment and billing information."),
    ("subscriptions.manage", "Manage subscription status and periods."),
    ("audit_logs.read", "View admin audit logs."),
    ("admins.manage", "Assign or remove administrator roles."),
    ("roles.manage", "Update role permission grants."),
)

ADMIN_PERMISSION_KEYS = (
    "users.read",
    "users.update_status",
    "users.view_progress",
    "task_templates.read",
    "task_templates.create",
    "task_templates.update",
    "task_templates.archive",
    "feedback_logs.read",
    "feedback_quality.review",
    "ai_logs.read",
    "ai_costs.read",
    "payments.read",
    "audit_logs.read",
)


def upgrade() -> None:
    op.create_table(
        "permissions",
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_permissions_key"), "permissions", ["key"], unique=True)

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["permission_id"], ["permissions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )
    op.create_index(
        op.f("ix_role_permissions_permission_id"),
        "role_permissions",
        ["permission_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_role_permissions_role_id"),
        "role_permissions",
        ["role_id"],
        unique=False,
    )

    op.create_table(
        "subscriptions",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_customer_id", sa.String(length=255), nullable=True),
        sa.Column("provider_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("plan_name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_subscriptions_current_period_end"),
        "subscriptions",
        ["current_period_end"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscriptions_provider"),
        "subscriptions",
        ["provider"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscriptions_provider_customer_id"),
        "subscriptions",
        ["provider_customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscriptions_provider_subscription_id"),
        "subscriptions",
        ["provider_subscription_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_subscriptions_status"),
        "subscriptions",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscriptions_user_id"),
        "subscriptions",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "payments",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_payment_id", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payments_paid_at"), "payments", ["paid_at"], unique=False)
    op.create_index(
        op.f("ix_payments_provider"),
        "payments",
        ["provider"],
        unique=False,
    )
    op.create_index(
        op.f("ix_payments_provider_payment_id"),
        "payments",
        ["provider_payment_id"],
        unique=True,
    )
    op.create_index(op.f("ix_payments_status"), "payments", ["status"], unique=False)
    op.create_index(op.f("ix_payments_user_id"), "payments", ["user_id"], unique=False)

    permissions_table = sa.table(
        "permissions",
        sa.column("key", sa.String),
        sa.column("description", sa.String),
    )
    op.bulk_insert(
        permissions_table,
        [{"key": key, "description": description} for key, description in PERMISSIONS],
    )

    bind = op.get_bind()
    role_rows = bind.execute(sa.text("SELECT id, name FROM roles")).mappings().all()
    permission_rows = (
        bind.execute(sa.text("SELECT id, key FROM permissions")).mappings().all()
    )
    role_ids = {row["name"]: row["id"] for row in role_rows}
    permission_ids = {row["key"]: row["id"] for row in permission_rows}

    role_permission_rows = []
    for permission_key in ADMIN_PERMISSION_KEYS:
        role_permission_rows.append(
            {
                "role_id": role_ids["admin"],
                "permission_id": permission_ids[permission_key],
            }
        )
    for permission_key, _description in PERMISSIONS:
        role_permission_rows.append(
            {
                "role_id": role_ids["super_admin"],
                "permission_id": permission_ids[permission_key],
            }
        )

    role_permissions_table = sa.table(
        "role_permissions",
        sa.column("role_id", sa.Integer),
        sa.column("permission_id", sa.Integer),
    )
    op.bulk_insert(role_permissions_table, role_permission_rows)


def downgrade() -> None:
    op.drop_index(op.f("ix_payments_user_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_status"), table_name="payments")
    op.drop_index(op.f("ix_payments_provider_payment_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_provider"), table_name="payments")
    op.drop_index(op.f("ix_payments_paid_at"), table_name="payments")
    op.drop_table("payments")

    op.drop_index(op.f("ix_subscriptions_user_id"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_status"), table_name="subscriptions")
    op.drop_index(
        op.f("ix_subscriptions_provider_subscription_id"),
        table_name="subscriptions",
    )
    op.drop_index(
        op.f("ix_subscriptions_provider_customer_id"),
        table_name="subscriptions",
    )
    op.drop_index(op.f("ix_subscriptions_provider"), table_name="subscriptions")
    op.drop_index(
        op.f("ix_subscriptions_current_period_end"),
        table_name="subscriptions",
    )
    op.drop_table("subscriptions")

    op.drop_index(
        op.f("ix_role_permissions_role_id"),
        table_name="role_permissions",
    )
    op.drop_index(
        op.f("ix_role_permissions_permission_id"),
        table_name="role_permissions",
    )
    op.drop_table("role_permissions")
    op.drop_index(op.f("ix_permissions_key"), table_name="permissions")
    op.drop_table("permissions")
