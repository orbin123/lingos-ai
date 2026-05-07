"""fix enum values to lowercase for curriculum enums

The original migration (e6b355a12fa1) created three Postgres enum types
with UPPERCASE values. The Python models use lowercase values (e.g. "active"
not "ACTIVE"), which causes a LookupError when SQLAlchemy reads rows.

This migration rebuilds all three enums with lowercase values:
  - enrollment_status_enum: ACTIVE/PAUSED/COMPLETED/ABANDONED → active/paused/completed/abandoned
  - course_status_enum:     DRAFT/ACTIVE/ARCHIVED             → draft/active/archived
  - course_level_enum:      BEGINNER/INTERMEDIATE/ADVANCED    → beginner/intermediate/advanced

Strategy (Postgres has no ALTER TYPE ... RENAME VALUE in older versions):
  1. Add a temporary TEXT column.
  2. Copy the old enum column into it.
  3. Drop the old enum column.
  4. Rename the old enum type (keep data safe).
  5. Create a new enum type with lowercase values.
  6. Add the real column back with the new enum type, casting via LOWER().
  7. Drop the temp column and the old enum type.

Revision ID: g2b3c4d5e6f7
Revises: f1a2b3c4d5e6
Create Date: 2026-05-05 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "g2b3c4d5e6f7"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _rename_enum_values_to_lower(conn, table: str, column: str, enum_name: str, old_values: list[str], new_values: list[str]) -> None:
    """Rebuild a single enum column with lowercase values."""

    old_enum_name = f"{enum_name}_old"

    # 1. Add temp TEXT column
    conn.execute(sa.text(f'ALTER TABLE {table} ADD COLUMN {column}_tmp TEXT'))

    # 2. Copy data as text (lowercased)
    conn.execute(sa.text(f'UPDATE {table} SET {column}_tmp = LOWER({column}::text)'))

    # 3. Drop original enum column
    conn.execute(sa.text(f'ALTER TABLE {table} DROP COLUMN {column}'))

    # 4. Rename old enum type
    conn.execute(sa.text(f'ALTER TYPE {enum_name} RENAME TO {old_enum_name}'))

    # 5. Create new enum with lowercase values
    values_sql = ", ".join(f"'{v}'" for v in new_values)
    conn.execute(sa.text(f'CREATE TYPE {enum_name} AS ENUM ({values_sql})'))

    # 6. Add the real column back, then copy from TEXT to the new enum.
    # PostgreSQL only supports USING with ALTER COLUMN TYPE, not ADD COLUMN.
    conn.execute(sa.text(f'ALTER TABLE {table} ADD COLUMN {column} {enum_name}'))
    conn.execute(sa.text(
        f'UPDATE {table} SET {column} = {column}_tmp::{enum_name}'
    ))

    # 7. Drop temp column and old enum
    conn.execute(sa.text(f'ALTER TABLE {table} DROP COLUMN {column}_tmp'))
    conn.execute(sa.text(f'DROP TYPE {old_enum_name}'))


def upgrade() -> None:
    conn = op.get_bind()

    # Fix enrollment_status_enum on user_enrollments.status
    _rename_enum_values_to_lower(
        conn,
        table="user_enrollments",
        column="status",
        enum_name="enrollment_status_enum",
        old_values=["ACTIVE", "PAUSED", "COMPLETED", "ABANDONED"],
        new_values=["active", "paused", "completed", "abandoned"],
    )

    # Fix course_status_enum on courses.status
    _rename_enum_values_to_lower(
        conn,
        table="courses",
        column="status",
        enum_name="course_status_enum",
        old_values=["DRAFT", "ACTIVE", "ARCHIVED"],
        new_values=["draft", "active", "archived"],
    )

    # Fix course_level_enum on courses.target_level
    _rename_enum_values_to_lower(
        conn,
        table="courses",
        column="target_level",
        enum_name="course_level_enum",
        old_values=["BEGINNER", "INTERMEDIATE", "ADVANCED"],
        new_values=["beginner", "intermediate", "advanced"],
    )

    # Restore NOT NULL constraints (they were lost when we dropped+re-added columns)
    conn.execute(sa.text("ALTER TABLE user_enrollments ALTER COLUMN status SET NOT NULL"))
    conn.execute(sa.text("ALTER TABLE courses ALTER COLUMN status SET NOT NULL"))
    conn.execute(sa.text("ALTER TABLE courses ALTER COLUMN target_level SET NOT NULL"))

    # Restore default for user_enrollments.status
    conn.execute(sa.text("ALTER TABLE user_enrollments ALTER COLUMN status SET DEFAULT 'active'::enrollment_status_enum"))

    # Restore default for courses.status
    conn.execute(sa.text("ALTER TABLE courses ALTER COLUMN status SET DEFAULT 'active'::course_status_enum"))


def downgrade() -> None:
    """Revert lowercase enums back to UPPERCASE."""
    conn = op.get_bind()

    _rename_enum_values_to_lower(
        conn,
        table="user_enrollments",
        column="status",
        enum_name="enrollment_status_enum",
        old_values=["active", "paused", "completed", "abandoned"],
        new_values=["ACTIVE", "PAUSED", "COMPLETED", "ABANDONED"],
    )

    _rename_enum_values_to_lower(
        conn,
        table="courses",
        column="status",
        enum_name="course_status_enum",
        old_values=["draft", "active", "archived"],
        new_values=["DRAFT", "ACTIVE", "ARCHIVED"],
    )

    _rename_enum_values_to_lower(
        conn,
        table="courses",
        column="target_level",
        enum_name="course_level_enum",
        old_values=["beginner", "intermediate", "advanced"],
        new_values=["BEGINNER", "INTERMEDIATE", "ADVANCED"],
    )

    conn.execute(sa.text("ALTER TABLE user_enrollments ALTER COLUMN status SET NOT NULL"))
    conn.execute(sa.text("ALTER TABLE courses ALTER COLUMN status SET NOT NULL"))
    conn.execute(sa.text("ALTER TABLE courses ALTER COLUMN target_level SET NOT NULL"))
