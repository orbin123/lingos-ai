"""extend task_type_enum for LLM-generated task types

Adds fill_in_blanks, error_spotting, sentence_transformation,
voice_conversion, and error_correction to the task_type_enum so the
Task Generator agent can store generated tasks with their specific type
(which the frontend uses to pick the correct rendering component).

Revision ID: f1a2b3c4d5e6
Revises: 46b0f444b4ea
Create Date: 2026-05-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "aaa000000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# New values we are adding to the Postgres enum.
NEW_VALUES = [
    "fill_in_blanks",
    "error_spotting",
    "sentence_transformation",
    "voice_conversion",
    "error_correction",
]


def upgrade() -> None:
    """Add generated task type values to task_type_enum."""
    # Postgres enums cannot be altered in a transaction, so we use
    # COMMIT/BEGIN around each ALTER TYPE statement.
    conn = op.get_bind()
    for value in NEW_VALUES:
        conn.execute(
            sa.text(f"ALTER TYPE task_type_enum ADD VALUE IF NOT EXISTS '{value}'")
        )


def downgrade() -> None:
    """Remove generated task type values — requires a full enum rebuild.

    Postgres has no DROP VALUE for enums, so we:
      1. Rename the old enum out of the way.
      2. Create the original enum with only the four base values.
      3. Cast the column to the new enum (rows with generated types become invalid
         and are set to 'reading' as a safe default).
      4. Drop the old enum.

    WARNING: any tasks with generated task types will have their type reset
    to 'reading' during downgrade.
    """
    conn = op.get_bind()

    # Step 1 — rename current enum
    conn.execute(sa.text("ALTER TYPE task_type_enum RENAME TO task_type_enum_old"))

    # Step 2 — create original enum
    conn.execute(
        sa.text(
            "CREATE TYPE task_type_enum AS ENUM "
            "('reading', 'writing', 'speaking', 'listening')"
        )
    )

    # Step 3 — migrate the column, coercing unknown values to 'reading'
    conn.execute(
        sa.text(
            """
            ALTER TABLE tasks
              ALTER COLUMN task_type TYPE task_type_enum
              USING CASE
                WHEN task_type::text IN ('reading','writing','speaking','listening')
                THEN task_type::text::task_type_enum
                ELSE 'reading'::task_type_enum
              END
            """
        )
    )

    # Step 4 — drop old enum
    conn.execute(sa.text("DROP TYPE task_type_enum_old"))
