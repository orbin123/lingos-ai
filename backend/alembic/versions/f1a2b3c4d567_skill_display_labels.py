"""skills: add display_label column + backfill friendly names

Revision ID: f1a2b3c4d567
Revises: d1e0f234a567
Create Date: 2026-05-18 11:00:00.000000

Adds a `display_label` column to `skills` and populates it with the
user-facing labels we want shown on dashboards / scorecards / stats:

  grammar       → Grammar
  vocabulary    → Vocabulary
  pronunciation → Pronunciation
  fluency       → Fluency
  expression    → Thought Organization
  comprehension → Listening
  tone          → Tone & Social

The internal `name` column is unchanged — see RESTRUCTURE_DECISIONS.md §2
(legacy identifiers stay; only the user-facing label moves).

Idempotent: the upgrade re-applies UPDATE statements for every row whose
identifier matches one of the known names, so re-running on a partially
populated table is safe.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f1a2b3c4d567"
down_revision: Union[str, Sequence[str], None] = "d1e0f234a567"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_LABELS: tuple[tuple[str, str], ...] = (
    ("grammar",       "Grammar"),
    ("vocabulary",    "Vocabulary"),
    ("pronunciation", "Pronunciation"),
    ("fluency",       "Fluency"),
    ("expression",    "Thought Organization"),
    ("comprehension", "Listening"),
    ("tone",          "Tone & Social"),
)


def upgrade() -> None:
    # Add the column NOT NULL with a sane default so existing rows aren't
    # left in an invalid state during the transition.
    op.add_column(
        "skills",
        sa.Column(
            "display_label",
            sa.String(length=60),
            nullable=False,
            server_default="",
        ),
    )

    # Backfill: one UPDATE per known skill identifier. Skip rows whose name
    # is not one of the seven canonical sub-skills (defensive — should be a
    # no-op in production).
    bind = op.get_bind()
    for name, label in _LABELS:
        bind.execute(
            sa.text("UPDATE skills SET display_label = :label WHERE name = :name"),
            {"label": label, "name": name},
        )

    # Drop the temporary server_default so future inserts must specify a
    # label explicitly. (We don't want silent empty labels going forward.)
    op.alter_column("skills", "display_label", server_default=None)


def downgrade() -> None:
    op.drop_column("skills", "display_label")
