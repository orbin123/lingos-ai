"""admin roles and active users

Revision ID: 5c6d7e8f9012
Revises: 17e15923f549
Create Date: 2026-05-14 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5c6d7e8f9012"
down_revision: Union[str, Sequence[str], None] = "17e15923f549"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ROLE_NAMES = ("learner", "admin", "super_admin")


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_active",
                sa.Boolean(),
                server_default="true",
                nullable=False,
            )
        )

    op.create_table(
        "roles",
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_roles_name"), "roles", ["name"], unique=True)

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),
    )
    op.create_index(op.f("ix_user_roles_role_id"), "user_roles", ["role_id"], unique=False)
    op.create_index(op.f("ix_user_roles_user_id"), "user_roles", ["user_id"], unique=False)

    roles_table = sa.table(
        "roles",
        sa.column("name", sa.String),
    )
    op.bulk_insert(roles_table, [{"name": name} for name in ROLE_NAMES])

    bind = op.get_bind()
    role_rows = bind.execute(sa.text("SELECT id, name FROM roles")).mappings().all()
    role_ids = {row["name"]: row["id"] for row in role_rows}

    bind.execute(
        sa.text(
            "INSERT INTO user_roles (user_id, role_id) "
            "SELECT id, :role_id FROM users"
        ),
        {"role_id": role_ids["learner"]},
    )
    bind.execute(
        sa.text(
            "INSERT INTO user_roles (user_id, role_id) "
            "SELECT id, :role_id FROM users WHERE is_superuser = true"
        ),
        {"role_id": role_ids["super_admin"]},
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_roles_user_id"), table_name="user_roles")
    op.drop_index(op.f("ix_user_roles_role_id"), table_name="user_roles")
    op.drop_table("user_roles")
    op.drop_index(op.f("ix_roles_name"), table_name="roles")
    op.drop_table("roles")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("is_active")
