"""seed skills: insert the 7 canonical sub-skill master rows

Revision ID: r8s9t0u1v234
Revises: q7r8s9t0u123
Create Date: 2026-06-19 16:30:00.000000

The `skills` master table was created by the squashed initial schema but never
seeded by any migration — `seed_curriculum.py` only seeds archetypes/curriculum,
and `f1a2b3c4d567_skill_display_labels` only *updates* labels (a no-op on an
empty table). As a result production ran with an empty `skills` table, so
`SkillRepository.name_to_id_map()` returned `{}` and the first real writer —
`POST /diagnosis/submit` — crashed with `KeyError: 'grammar'` (and any
`SkillPoints` writer would have failed the same way).

This migration inserts the 7 canonical sub-skill rows (name, description,
display_label) from the single source of truth `app.modules.skills.seed_data`.

Idempotent: each row is inserted only if no row with that `name` exists, so it
is safe to re-run and safe whether the table is empty or partially populated.
`created_at` is left to the column's `server_default = now()`.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.modules.skills.seed_data import SKILL_SEED


revision: str = "r8s9t0u1v234"
down_revision: Union[str, Sequence[str], None] = "q7r8s9t0u123"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    # `name` carries a unique index (ix_skills_name), so ON CONFLICT makes this
    # idempotent — safe to re-run and safe whether the table is empty or partial.
    insert_stmt = sa.text(
        """
        INSERT INTO skills (name, description, display_label)
        VALUES (:name, :description, :display_label)
        ON CONFLICT (name) DO NOTHING
        """
    )
    for name, description, display_label in SKILL_SEED:
        bind.execute(
            insert_stmt,
            {"name": name, "description": description, "display_label": display_label},
        )


def downgrade() -> None:
    bind = op.get_bind()
    names = [name for name, _description, _label in SKILL_SEED]
    # FK from skill_points → skills is ON DELETE CASCADE, so dependent rows go
    # with these. Downgrade on prod is not expected.
    bind.execute(
        sa.text("DELETE FROM skills WHERE name = ANY(:names)"),
        {"names": names},
    )
