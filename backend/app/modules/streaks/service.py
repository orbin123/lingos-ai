"""Streak state machine and read API.

Two entry points:

* `record_in_same_tx` — called from `SessionService.submit_activity` after
  an activity is evaluated but BEFORE the outer commit. Flushes inserts
  so the unique constraint catches double-fires, but does NOT commit; the
  outer caller owns the transaction boundary.

* `get_streak_data` — pure read for the dashboard. Builds the 91-day grid
  and decides whether the celebration animation should play.

Freeze rule (MVP, strict): `DEFAULT_FREEZES_ON_SIGNUP = 0` and
`MAX_AUTO_FREEZE_DAYS = 0` mean every missed day resets. Code paths still
exist so the rule can be relaxed by tweaking the constants — no migration
needed.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.models import UserProfile
from app.modules.streaks.activity_grid import count_evaluated_activities_by_local_date
from app.modules.streaks.dates import (
    DEFAULT_TIMEZONE,
    build_last_n_days,
    get_previous_local_date,
    get_user_local_date,
)
from app.modules.streaks.models import DailyActivity, StreakFreezeUsage
from app.modules.streaks.repository import (
    DailyActivityRepository,
    StreakFreezeUsageRepository,
)
from app.modules.streaks.schemas import (
    ActivityGridCell,
    AnimationType,
    StreakDataResponse,
    StreakState,
    StreakStatus,
)

logger = logging.getLogger(__name__)


# Tuning constants — change here, no migration needed.
DEFAULT_FREEZES_ON_SIGNUP: int = 0
MAX_AUTO_FREEZE_DAYS: int = 0
GRID_DAYS: int = 91

_LEGACY_ANIMATION_MAP: dict[str, AnimationType] = {
    "initial": "rekindle",
    "continued": "on_fire",
    "reset": "frozen_to_fire",
    "frozen": "frozen",
}


@dataclass(frozen=True)
class StreakEventResult:
    state: StreakState
    current_streak: int
    longest_streak: int
    freezes_remaining: int
    animation_type: AnimationType | None


class StreakService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.activities = DailyActivityRepository(db)
        self.freezes = StreakFreezeUsageRepository(db)

    # ── write path ────────────────────────────────────────────────────

    def record_in_same_tx(
        self,
        *,
        user_id: int,
        session_id: int | None = None,
        now_utc: datetime | None = None,
    ) -> StreakEventResult:
        """Record one successful activity completion.

        Idempotent w.r.t. local date: a second call on the same local day
        bumps `activity_count` but never re-increments the streak. Caller
        owns the outer commit.
        """
        now_utc = now_utc or datetime.now(timezone.utc)
        profile = self._safe_load_profile(user_id)
        if profile is None:
            # Defensive: lesson completion must never fail because streak
            # tracking can't find a profile row (or the table isn't mapped
            # in a minimal test env). Log and no-op.
            logger.warning(
                "streak: skipping record — no UserProfile for user_id=%s",
                user_id,
            )
            return StreakEventResult(
                state="NO_STREAK_YET",
                current_streak=0,
                longest_streak=0,
                freezes_remaining=0,
                animation_type=None,
            )
        tz = profile.timezone or DEFAULT_TIMEZONE
        today = get_user_local_date(tz, now_utc=now_utc)

        existing = self.activities.get_for_date(user_id=user_id, local_date=today)
        if existing is not None:
            existing.activity_count += 1
            existing.completed_at = now_utc
            if session_id is not None:
                existing.last_session_id = session_id
            self.db.flush()
            return StreakEventResult(
                state="STREAK_ALREADY_COMPLETED_TODAY",
                current_streak=profile.current_streak,
                longest_streak=profile.longest_streak,
                freezes_remaining=profile.streak_freezes,
                animation_type=None,
            )

        try:
            self.activities.add(
                DailyActivity(
                    user_id=user_id,
                    local_date=today,
                    activity_count=1,
                    streak_awarded=True,
                    last_session_id=session_id,
                    completed_at=now_utc,
                )
            )
        except IntegrityError:
            # Concurrent double-fire: another call inserted the row
            # between our get/insert. Roll back the failed insert and
            # treat as the "already complete" path.
            self.db.rollback()
            existing = self.activities.get_for_date(user_id=user_id, local_date=today)
            if existing is None:
                raise
            # Re-load profile because rollback invalidated state.
            profile = self._load_profile_or_raise(user_id)
            existing.activity_count += 1
            existing.completed_at = now_utc
            if session_id is not None:
                existing.last_session_id = session_id
            self.db.flush()
            return StreakEventResult(
                state="STREAK_ALREADY_COMPLETED_TODAY",
                current_streak=profile.current_streak,
                longest_streak=profile.longest_streak,
                freezes_remaining=profile.streak_freezes,
                animation_type=None,
            )

        state, animation = self._advance_streak_counters(
            profile=profile,
            today=today,
            now_utc=now_utc,
        )
        profile.last_animation_type = animation
        self.db.flush()
        return StreakEventResult(
            state=state,
            current_streak=profile.current_streak,
            longest_streak=profile.longest_streak,
            freezes_remaining=profile.streak_freezes,
            animation_type=animation,
        )

    def _advance_streak_counters(
        self,
        *,
        profile: UserProfile,
        today: date,
        now_utc: datetime,
    ) -> tuple[StreakState, AnimationType]:
        last = profile.last_activity_date

        if last is None:
            profile.current_streak = 1
            profile.last_activity_date = today
            profile.longest_streak = max(profile.longest_streak, 1)
            return "FIRST_STREAK_EARNED", "rekindle"

        gap = (today - last).days
        if gap <= 0:
            # Should not happen — same-day path handled before this, and a
            # negative gap means the clock skewed. Be defensive: treat as
            # idempotent.
            logger.warning(
                "streak: non-positive gap=%s last=%s today=%s user_id=%s",
                gap,
                last,
                today,
                profile.user_id,
            )
            return "STREAK_ALREADY_COMPLETED_TODAY", "on_fire"

        if gap == 1:
            profile.current_streak += 1
            profile.last_activity_date = today
            profile.longest_streak = max(profile.longest_streak, profile.current_streak)
            return "STREAK_CONTINUED", "on_fire"

        # gap > 1 → missed days. Try to auto-protect (disabled when MAX=0).
        missed_days = gap - 1
        if (
            MAX_AUTO_FREEZE_DAYS > 0
            and missed_days <= MAX_AUTO_FREEZE_DAYS
            and profile.streak_freezes >= missed_days
        ):
            for offset in range(1, gap):
                missed_date = last + timedelta(days=offset)
                self.freezes.add(
                    StreakFreezeUsage(
                        user_id=profile.user_id,
                        protected_date=missed_date,
                        used_at=now_utc,
                        reason="auto_missed_day_protection",
                    )
                )
            profile.streak_freezes -= missed_days
            profile.current_streak += 1
            profile.last_activity_date = today
            profile.longest_streak = max(profile.longest_streak, profile.current_streak)
            return "STREAK_FROZEN", "frozen"

        profile.current_streak = 1
        profile.last_activity_date = today
        profile.longest_streak = max(profile.longest_streak, 1)
        return "STREAK_RESET", "frozen_to_fire"

    # ── read path ─────────────────────────────────────────────────────

    def get_streak_data(self, *, user_id: int) -> StreakDataResponse:
        profile = self._load_profile_or_raise(user_id)
        tz = profile.timezone or DEFAULT_TIMEZONE
        today = get_user_local_date(tz)
        window = build_last_n_days(today, GRID_DAYS)
        start = window[0]

        activities = self.activities.list_in_range(
            user_id=user_id,
            start=start,
            end=today,
        )
        freezes = self.freezes.list_in_range(
            user_id=user_id,
            start=start,
            end=today,
        )

        by_date_session = {a.local_date for a in activities}
        frozen_dates = {f.protected_date for f in freezes}
        by_date_activity = count_evaluated_activities_by_local_date(
            self.db,
            user_id=user_id,
            tz=tz,
            start=start,
            end=today,
        )

        grid = [
            ActivityGridCell(
                date=d.isoformat(),
                activity_count=by_date_activity.get(d, 0),
                completed=d in by_date_session,
                intensity=min(by_date_activity.get(d, 0), 4),
                frozen_protected=d in frozen_dates,
            )
            for d in window
        ]

        today_row = self.activities.get_for_date(user_id=user_id, local_date=today)
        today_complete = today in by_date_session
        today_streak_awarded = today_row is not None and today_row.streak_awarded
        streak_status = self._derive_streak_status(
            profile=profile,
            today=today,
            today_complete=today_complete,
        )
        streak_state = self._derive_ui_state(profile, today_complete)
        should_show_animation = (
            today_complete
            and profile.last_animation_type is not None
            and profile.last_seen_streak_animation_date != today
        )
        animation_type: AnimationType | None = (
            _coerce_animation(profile.last_animation_type)
            if should_show_animation
            else None
        )

        last_date = profile.last_activity_date
        return StreakDataResponse(
            current_streak=profile.current_streak,
            longest_streak=profile.longest_streak,
            freezes_remaining=profile.streak_freezes,
            today_complete=today_complete,
            today_streak_awarded=today_streak_awarded,
            last_activity_date=last_date,
            last_streak_date=last_date,
            streak_status=streak_status,
            streak_state_for_ui=streak_state,
            should_show_animation=should_show_animation,
            animation_type=animation_type,
            activity_grid=grid,
            timezone=tz,
        )

    def mark_animation_seen(self, *, user_id: int) -> StreakDataResponse:
        profile = self._load_profile_or_raise(user_id)
        tz = profile.timezone or DEFAULT_TIMEZONE
        today = get_user_local_date(tz)
        profile.last_seen_streak_animation_date = today
        self.db.commit()
        self.db.refresh(profile)
        return self.get_streak_data(user_id=user_id)

    # ── helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _derive_streak_status(
        *,
        profile: UserProfile,
        today: date,
        today_complete: bool,
    ) -> StreakStatus:
        last = profile.last_activity_date
        if last is None:
            return "new"
        if today_complete:
            return "active"
        yesterday = get_previous_local_date(today)
        if last == yesterday:
            return "active"
        if (today - last).days > 1:
            return "frozen"
        if profile.current_streak == 0:
            return "broken"
        return "active"

    @staticmethod
    def _derive_ui_state(profile: UserProfile, today_complete: bool) -> StreakState:
        if profile.current_streak == 0 and profile.last_activity_date is None:
            return "NO_STREAK_YET"
        if today_complete:
            return "STREAK_ALREADY_COMPLETED_TODAY"
        return "INACTIVE_TODAY"

    def _load_profile_or_raise(self, user_id: int) -> UserProfile:
        profile = (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .one_or_none()
        )
        if profile is None:
            raise RuntimeError(f"UserProfile missing for user_id={user_id}")
        return profile

    def _safe_load_profile(self, user_id: int) -> UserProfile | None:
        """Like `_load_profile_or_raise` but swallows OperationalError too —
        for test environments where the `user_profiles` table isn't created.

        Wraps the read in a SAVEPOINT so an OperationalError doesn't poison
        the outer transaction (which still owns the session-completion work).
        """
        try:
            with self.db.begin_nested():
                return (
                    self.db.query(UserProfile)
                    .filter(UserProfile.user_id == user_id)
                    .one_or_none()
                )
        except Exception:  # noqa: BLE001
            logger.warning(
                "streak: failed to load UserProfile for user_id=%s — skipping",
                user_id,
            )
            return None


def _coerce_animation(value: str | None) -> AnimationType | None:
    if value is None:
        return None
    if value in {"rekindle", "on_fire", "frozen_to_fire", "frozen"}:
        return value  # type: ignore[return-value]
    return _LEGACY_ANIMATION_MAP.get(value)
