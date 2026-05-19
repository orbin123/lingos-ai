"""Read/write helpers for `UserCoursePreference`. No business logic."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.preferences.models import UserCoursePreference


# Highest week number considered "within a course". Any advance past
# (max_week, day 7) clamps at the final day rather than rolling further.
# The 48w course is the longer of the two, so cap at 48.
_MAX_WEEK = 48


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

    def advance_day(
        self,
        pref: UserCoursePreference,
        *,
        now: datetime | None = None,
        today: date | None = None,
    ) -> UserCoursePreference:
        """Bump the day pointer forward by one.

        Rolls over to next week's day 1 after day 7. Clamps at the final
        week's day 7 (the caller is responsible for treating the course as
        "complete" once it stops moving).
        """
        now = now or datetime.now(timezone.utc)
        today = today or now.date()

        if pref.current_day_in_week >= 7:
            if pref.current_week >= _MAX_WEEK:
                # Stay parked at the final day — no further advance.
                pref.last_completed_on = today
                self.db.flush()
                return pref
            pref.current_week += 1
            pref.current_day_in_week = 1
        else:
            pref.current_day_in_week += 1

        pref.current_day_started_at = now
        pref.last_completed_on = today
        self.db.flush()
        return pref
