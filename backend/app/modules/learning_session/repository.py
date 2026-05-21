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

    def get_by_daily_session_id(self, daily_session_id: int) -> LearningSession | None:
        return (
            self.db.query(LearningSession)
            .filter(LearningSession.daily_session_id == daily_session_id)
            .order_by(LearningSession.id.desc())
            .first()
        )

    def create(
        self,
        *,
        session_id: str,
        user_id: int,
        daily_session_id: int,
        topic: str,
        skill_name: str,
        activity_type: str,
        task_type: str,
        user_level: int,
        pre_generated_tasks: dict | None = None,
        task_queue: list | None = None,
        teacher_instructions: dict | None = None,
    ) -> LearningSession:
        row = LearningSession(
            session_id=session_id,
            user_id=user_id,
            daily_session_id=daily_session_id,
            phase="teaching",
            topic=topic,
            skill_name=skill_name,
            activity_type=activity_type,
            task_type=task_type,
            user_level=user_level,
            pre_generated_tasks=pre_generated_tasks or {},
            task_queue=task_queue or [],
            current_task_index=0,
            messages=[],
            understanding_confirmed=False,
            teacher_instructions=teacher_instructions,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def save(self, session: LearningSession) -> LearningSession:
        """Mark JSONB columns dirty and flush."""
        for column in (
            "messages",
            "pre_generated_tasks",
            "task_queue",
            "user_submission",
            "evaluation",
            "feedback",
            "teacher_instructions",
        ):
            if getattr(session, column) is not None:
                flag_modified(session, column)
        self.db.flush()
        return session
