"""PreferenceService — orchestrates reads and partial updates.

The service owns commit boundaries. Repository methods only flush.
Day advancement is handled exclusively by SessionService.advance_day().
"""

from __future__ import annotations

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

