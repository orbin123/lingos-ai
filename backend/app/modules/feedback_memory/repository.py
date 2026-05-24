"""Repository for feedback memory audit logs.

Read- and write-helpers only. Business decisions live in `rag_service.py`.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.feedback_memory.models import FeedbackMemoryLog


class FeedbackMemoryRepository:
    """CRUD for feedback_memory_logs — the Postgres source of truth."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, log: FeedbackMemoryLog) -> FeedbackMemoryLog:
        self.db.add(log)
        self.db.flush()
        return log

    def list_for_user(
        self, user_id: int, *, memory_type: str | None = None
    ) -> list[FeedbackMemoryLog]:
        stmt = (
            select(FeedbackMemoryLog)
            .where(FeedbackMemoryLog.user_id == user_id)
            .order_by(FeedbackMemoryLog.id.desc())
        )
        if memory_type is not None:
            stmt = stmt.where(FeedbackMemoryLog.memory_type == memory_type)
        return list(self.db.execute(stmt).scalars())

    def list_for_session(self, session_id: int) -> list[FeedbackMemoryLog]:
        return list(
            self.db.execute(
                select(FeedbackMemoryLog)
                .where(FeedbackMemoryLog.session_id == session_id)
                .order_by(FeedbackMemoryLog.id)
            ).scalars()
        )

    def delete_for_user(self, user_id: int) -> int:
        """Delete all memory logs for a user. Returns count deleted."""
        rows = self.list_for_user(user_id)
        count = len(rows)
        for row in rows:
            self.db.delete(row)
        self.db.flush()
        return count
