"""PreferenceService — orchestrates reads, partial updates, and the
single-day advance triggered when a session is completed.

The service owns commit boundaries. Repository methods only flush.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.modules.preferences.models import UserCoursePreference
from app.modules.preferences.repository import UserCoursePreferenceRepository


class PreferenceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserCoursePreferenceRepository(db)

    # ── read ──────────────────────────────────────────────────────────

    def get(self, user_id: int) -> UserCoursePreference:
        """Return the user's preference row, creating one with defaults if
        missing. Lazy-create covers diagnosis-only users who have not yet
        been backfilled from a legacy `UserEnrollment`.
        """
        pref = self.repo.get_or_create_for_user(user_id)
        self.db.commit()
        self.db.refresh(pref)
        return pref

    # ── write ─────────────────────────────────────────────────────────

    def update_settings(self, user_id: int, **fields: Any) -> UserCoursePreference:
        """Apply non-None fields to the user's preference row."""
        pref = self.repo.get_or_create_for_user(user_id)
        self.repo.update_settings(pref, **fields)
        self.db.commit()
        self.db.refresh(pref)
        return pref

    def advance_after_session_complete(
        self,
        user_id: int,
        *,
        now: datetime | None = None,
    ) -> UserCoursePreference:
        """Bump the day pointer after a successful session completion."""
        pref = self.repo.get_or_create_for_user(user_id)
        self.repo.advance_day(pref, now=now)
        self.db.commit()
        self.db.refresh(pref)
        return pref
