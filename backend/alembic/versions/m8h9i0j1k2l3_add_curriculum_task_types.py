"""add curriculum task types to task_type_enum

Revision ID: m8h9i0j1k2l3
Revises: f81a4fd84a55
Create Date: 2026-05-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "m8h9i0j1k2l3"
down_revision: Union[str, Sequence[str], None] = "f81a4fd84a55"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NEW_VALUES = [
    "curriculum_grammar_fill_blanks",
    "curriculum_grammar_open_text",
    "curriculum_grammar_listen_mcq",
    "curriculum_grammar_speak",
    "curriculum_vocab_mcq",
    "curriculum_vocab_open_text",
    "curriculum_vocab_listen_mcq",
    "curriculum_vocab_speak",
    "curriculum_pron_read_aloud",
    "curriculum_pron_phonetic_mcq",
    "curriculum_pron_listen_discriminate",
    "curriculum_pron_speak_drill",
    "curriculum_fluency_speed_read",
    "curriculum_fluency_timed_write",
    "curriculum_fluency_shadow",
    "curriculum_fluency_speak",
    "curriculum_expression_summarize",
    "curriculum_expression_essay",
    "curriculum_expression_listen_structure",
    "curriculum_expression_storyboard",
    "curriculum_comprehension_read_mcq",
    "curriculum_comprehension_write_answers",
    "curriculum_comprehension_listen_mcq",
    "curriculum_comprehension_retell",
    "curriculum_tone_read_mcq",
    "curriculum_tone_rewrite",
    "curriculum_tone_listen_mcq",
    "curriculum_tone_roleplay",
]


def upgrade() -> None:
    conn = op.get_bind()
    for value in _NEW_VALUES:
        conn.execute(
            sa.text(f"ALTER TYPE task_type_enum ADD VALUE IF NOT EXISTS '{value}'")
        )


def downgrade() -> None:
    # Postgres cannot drop individual enum values without a full rebuild.
    pass
