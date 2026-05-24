"""SQLAlchemy model for the feedback memory audit log.

PostgreSQL is the source of truth. Every memory document that gets upserted
into Pinecone is also logged here so that:
  1. The vector index can be rebuilt from scratch if Pinecone data is lost.
  2. Operators can debug which memories exist for a user.
  3. Data-retention / GDPR deletion cascades correctly (user delete → rows
     deleted via FK cascade → background job cleans Pinecone).
"""

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import CreatedAtMixin, IDMixin


class FeedbackMemoryLog(Base, IDMixin, CreatedAtMixin):
    """One row per memory document upserted to the vector DB."""

    __tablename__ = "feedback_memory_logs"
    __table_args__ = (
        Index("ix_feedback_memory_user", "user_id"),
        Index("ix_feedback_memory_session", "session_id"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("daily_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    attempt_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("activity_attempts.id", ondelete="CASCADE"),
        nullable=True,
    )
    memory_type: Mapped[str] = mapped_column(
        String(30), nullable=False,
    )  # "activity_feedback" | "session_summary"
    vector_id: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False,
    )
    document_text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="'{}'",
    )

    def __repr__(self) -> str:
        return (
            f"<FeedbackMemoryLog(id={self.id}, user={self.user_id}, "
            f"type={self.memory_type!r}, vector={self.vector_id!r})>"
        )
