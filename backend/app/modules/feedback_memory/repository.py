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

    def get_by_vector_id(self, vector_id: str) -> FeedbackMemoryLog | None:
        return self.db.execute(
            select(FeedbackMemoryLog).where(FeedbackMemoryLog.vector_id == vector_id)
        ).scalar_one_or_none()

    def upsert_by_vector_id(
        self,
        *,
        vector_id: str,
        user_id: int,
        session_id: int,
        attempt_id: int | None,
        memory_type: str,
        document_text: str,
        metadata_json: dict,
    ) -> FeedbackMemoryLog:
        """Insert a log, or update the existing row with this vector_id.

        Keeps the Postgres mirror idempotent so re-storing the same
        attempt/session (stable vector_id) does not duplicate rows.
        """
        existing = self.get_by_vector_id(vector_id)
        if existing is not None:
            existing.document_text = document_text
            existing.metadata_json = metadata_json
            existing.memory_type = memory_type
            existing.session_id = session_id
            existing.attempt_id = attempt_id
            self.db.flush()
            return existing
        return self.add(
            FeedbackMemoryLog(
                user_id=user_id,
                session_id=session_id,
                attempt_id=attempt_id,
                memory_type=memory_type,
                vector_id=vector_id,
                document_text=document_text,
                metadata_json=metadata_json,
            )
        )

    def list_for_attempt(self, attempt_id: int) -> list[FeedbackMemoryLog]:
        return list(
            self.db.execute(
                select(FeedbackMemoryLog)
                .where(FeedbackMemoryLog.attempt_id == attempt_id)
                .order_by(FeedbackMemoryLog.id)
            ).scalars()
        )

    def get_session_summary_for_session(
        self, session_id: int
    ) -> FeedbackMemoryLog | None:
        return (
            self.db.execute(
                select(FeedbackMemoryLog)
                .where(FeedbackMemoryLog.session_id == session_id)
                .where(FeedbackMemoryLog.memory_type == "session_summary")
                .order_by(FeedbackMemoryLog.id.desc())
            )
            .scalars()
            .first()
        )

    def delete_by_vector_ids(self, vector_ids: list[str]) -> int:
        """Delete log rows by vector_id. Returns count deleted."""
        if not vector_ids:
            return 0
        rows = list(
            self.db.execute(
                select(FeedbackMemoryLog).where(
                    FeedbackMemoryLog.vector_id.in_(vector_ids)
                )
            ).scalars()
        )
        for row in rows:
            self.db.delete(row)
        self.db.flush()
        return len(rows)

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
