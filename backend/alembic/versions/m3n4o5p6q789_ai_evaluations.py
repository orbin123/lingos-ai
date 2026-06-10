"""ai_evaluations (LLM-as-judge quality scores)

Revision ID: m3n4o5p6q789
Revises: l2m3n4o5p678
Create Date: 2026-06-09 13:00:00.000000

Part B Phase 2. Append-only table holding LLM-as-judge quality scores for
generated AI outputs, keyed by the same trace_id stamped on ai_request_logs so
cost/latency join to quality. Scores are Numeric(4,2), 0–10; faithfulness is
RAG-only (mentor note) and stays null for feedback rows.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "m3n4o5p6q789"
down_revision: Union[str, Sequence[str], None] = "l2m3n4o5p678"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_evaluations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trace_id", sa.String(length=120), nullable=True),
        sa.Column("target_type", sa.String(length=40), nullable=False),
        sa.Column("target_id", sa.String(length=120), nullable=True),
        sa.Column("judge_model", sa.String(length=120), nullable=False),
        sa.Column("accuracy", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("relevance", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("helpfulness", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("correctness", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("faithfulness", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("eval_mode", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        op.f("ix_ai_evaluations_trace_id"), "ai_evaluations", ["trace_id"]
    )
    op.create_index(
        op.f("ix_ai_evaluations_target_type"), "ai_evaluations", ["target_type"]
    )
    op.create_index(
        op.f("ix_ai_evaluations_target_id"), "ai_evaluations", ["target_id"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_evaluations_target_id"), table_name="ai_evaluations")
    op.drop_index(op.f("ix_ai_evaluations_target_type"), table_name="ai_evaluations")
    op.drop_index(op.f("ix_ai_evaluations_trace_id"), table_name="ai_evaluations")
    op.drop_table("ai_evaluations")
