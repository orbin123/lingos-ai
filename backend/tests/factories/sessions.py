"""DailySession / ActivityAttempt factories.

Convenience builders for tests that need session rows without driving the full
`SessionService` (e.g. progress/streak/replay tests). The Complete Learning
Loop intentionally uses the real service instead of these.

Note: SQLite does not enforce FKs by default, so `day_id`/`archetype_id` need
not pre-exist — but pass real values when running against a seeded curriculum.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.modules.sessions.models import (
    ActivityAttempt,
    AttemptStatus,
    DailySession,
    SessionStatus,
)


def make_daily_session(
    db: Session,
    user,
    *,
    day_id: str = "day_24_09_03",
    course_length: str = "24w",
    status: SessionStatus = SessionStatus.IN_PROGRESS,
    is_first_attempt: bool = True,
    session_id: str | None = None,
    started_at: datetime | None = None,
    completed_at: datetime | None = None,
) -> DailySession:
    """Persist a `DailySession` for `user`."""
    now = datetime.now(timezone.utc)
    if completed_at is None and status is SessionStatus.COMPLETED:
        completed_at = now
    session = DailySession(
        session_id=session_id or str(uuid.uuid4()),
        user_id=user.id,
        day_id=day_id,
        course_length=course_length,
        status=status,
        is_first_attempt=is_first_attempt,
        started_at=started_at or now,
        completed_at=completed_at,
    )
    db.add(session)
    db.commit()
    return session


def make_activity_attempt(
    db: Session,
    session: DailySession,
    *,
    archetype_id: str = "READ_CLOZE",
    sequence: int = 0,
    is_mandatory: bool = True,
    status: AttemptStatus = AttemptStatus.PENDING,
    task_content: dict | None = None,
    user_response: dict | None = None,
) -> ActivityAttempt:
    """Persist one `ActivityAttempt` under `session`."""
    attempt = ActivityAttempt(
        session_id=session.id,
        archetype_id=archetype_id,
        sequence=sequence,
        is_mandatory=is_mandatory,
        status=status,
        task_content=task_content or {},
        user_response=user_response,
    )
    db.add(attempt)
    db.commit()
    return attempt
