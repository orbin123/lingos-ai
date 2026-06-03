"""Read/write helpers for `UserCoursePreference`. No business logic."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.preferences.models import UserCoursePreference


class UserCoursePreferenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ── read ──────────────────────────────────────────────────────────

    def get_for_user(self, user_id: int) -> UserCoursePreference | None:
        return self.db.execute(
            select(UserCoursePreference).where(
                UserCoursePreference.user_id == user_id
            )
        ).scalar_one_or_none()

    # ── upsert ────────────────────────────────────────────────────────

    def get_or_create_for_user(self, user_id: int) -> UserCoursePreference:
        """Return the user's preference row, creating one with defaults if
        missing. Concurrent calls race-safe via UNIQUE(user_id)."""
        existing = self.get_for_user(user_id)
        if existing is not None:
            return existing

        row = UserCoursePreference(user_id=user_id)
        self.db.add(row)
        try:
            self.db.flush()
        except IntegrityError:
            self.db.rollback()
            existing = self.get_for_user(user_id)
            if existing is None:
                raise
            return existing
        return row

    # ── update ────────────────────────────────────────────────────────

    def update_settings(
        self,
        pref: UserCoursePreference,
        **fields: Any,
    ) -> UserCoursePreference:
        """Apply non-None fields to the row. Unknown fields raise AttributeError."""
        for key, value in fields.items():
            if value is None:
                continue
            if not hasattr(pref, key):
                raise AttributeError(
                    f"UserCoursePreference has no field {key!r}"
                )
            setattr(pref, key, value)
        self.db.flush()
        return pref

