"""Admin monitoring models."""

from sqlalchemy import (
    ForeignKey,
    JSON,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import CreatedAtMixin, IDMixin


class AdminAuditLog(Base, IDMixin, CreatedAtMixin):
    """Append-only record of important admin actions."""

    __tablename__ = "admin_audit_logs"

    admin_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    old_value: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    new_value: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)

    admin_user = relationship("User")


class AIRequestLog(Base, IDMixin, CreatedAtMixin):
    """Append-only operational log for AI provider calls."""

    __tablename__ = "ai_request_logs"

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    trace_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    input_tokens: Mapped[int | None] = mapped_column(nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(120), nullable=True)

    user = relationship("User")


class AIEvaluation(Base, IDMixin, CreatedAtMixin):
    """LLM-as-judge quality scores for one generated AI output.

    Append-only event table (Part B Phase 2). Each row is one judge run over a
    single production LLM output, keyed by the same ``trace_id`` stamped on the
    matching ``ai_request_logs`` row(s) so cost/latency join to quality. Scores
    are 0–10; ``faithfulness`` is RAG-only (mentor note) and stays null here.

    Privacy: store scores + a short rationale only — never raw learner text.
    """

    __tablename__ = "ai_evaluations"

    # Join key to ai_request_logs (same per-submit correlation id).
    trace_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    # "feedback" | "mentor_note" | "task_generation" | "evaluation"
    target_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    # The judged artifact's id (e.g. activity_feedback.id), stringified.
    target_id: Mapped[str | None] = mapped_column(
        String(120), nullable=True, index=True
    )
    judge_model: Mapped[str] = mapped_column(String(120), nullable=False)
    accuracy: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    relevance: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    helpfulness: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    correctness: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    # RAG-only (faithfulness to retrieved context); null for non-RAG targets.
    faithfulness: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    # "online" (production sampling) | "offline" (golden-set / CI)
    eval_mode: Mapped[str] = mapped_column(String(20), nullable=False)
