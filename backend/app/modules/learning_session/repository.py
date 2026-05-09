"""DB access for LearningSession rows."""

from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.modules.learning_session.models import LearningSession


class LearningSessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_session_id(self, session_id: str) -> LearningSession | None:
        return (
            self.db.query(LearningSession)
            .filter(LearningSession.session_id == session_id)
            .first()
        )

    def create(
        self,
        *,
        session_id: str,
        user_id: int,
        enrollment_id: int,
        user_task_id: int | None = None,
        topic: str,
        skill_name: str,
        activity_type: str,
        task_type: str,
        user_level: int,
        pre_generated_tasks: dict,
    ) -> LearningSession:
        row = LearningSession(
            session_id=session_id,
            user_id=user_id,
            enrollment_id=enrollment_id,
            user_task_id=user_task_id,
            phase="teaching",
            topic=topic,
            skill_name=skill_name,
            activity_type=activity_type,
            task_type=task_type,
            user_level=user_level,
            pre_generated_tasks=pre_generated_tasks,
            current_task_index=0,
            messages=[],
            understanding_confirmed=False,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def save(self, session: LearningSession) -> LearningSession:
        """Mark JSONB columns dirty and flush."""
        for column in ("messages", "pre_generated_tasks", "user_submission",
                       "evaluation", "feedback"):
            if getattr(session, column) is not None:
                flag_modified(session, column)
        self.db.flush()
        return session
