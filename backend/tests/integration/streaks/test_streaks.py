"""StreakService state-machine tests against in-memory SQLite."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401 — populate Base.metadata
from app.core.database import Base
from app.modules.auth.models import User, UserProfile
from app.modules.curriculum.models import TaskArchetype
from app.modules.sessions.models import ActivityAttempt, DailySession
from app.modules.streaks import service as streak_service_module
from app.modules.streaks.models import DailyActivity, StreakFreezeUsage
from app.modules.streaks.service import StreakService
from scripts.seed_curriculum import seed_archetypes


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            UserProfile.__table__,
            DailyActivity.__table__,
            StreakFreezeUsage.__table__,
            TaskArchetype.__table__,
            DailySession.__table__,
            ActivityAttempt.__table__,
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        seed_archetypes(db)
        yield db
    finally:
        db.close()
        engine.dispose()


def _make_user(db, tz: str = "Asia/Kolkata") -> int:
    u = User(email="x@example.com", password_hash="x", name="L")
    db.add(u)
    db.flush()
    p = UserProfile(user_id=u.id, timezone=tz)
    db.add(p)
    db.commit()
    return u.id


def _fixed_utc(local_d: date, hour_utc: int = 6, tz: str = "Asia/Kolkata") -> datetime:
    """Return a UTC datetime that the streak service will map to `local_d`
    for the given IANA timezone. 06:00 UTC is 11:30 IST — safely mid-day."""
    return datetime.combine(
        local_d, datetime.min.time(), tzinfo=timezone.utc
    ) + timedelta(hours=hour_utc)


def _ist_late_night(local_d: date, hour_ist: int, minute: int = 0) -> datetime:
    """UTC instant for a given local time in Asia/Kolkata (UTC+5:30)."""
    # IST = UTC + 5:30 → UTC = local - 5:30
    local_dt = datetime.combine(local_d, datetime.min.time()) + timedelta(
        hours=hour_ist,
        minutes=minute,
    )
    return (local_dt - timedelta(hours=5, minutes=30)).replace(tzinfo=timezone.utc)


class TestRecord:
    def test_first_activity_sets_streak_to_1(self, db_session):
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        result = svc.record_in_same_tx(
            user_id=uid,
            now_utc=_fixed_utc(date(2026, 5, 19)),
        )
        db_session.commit()
        assert result.state == "FIRST_STREAK_EARNED"
        assert result.current_streak == 1
        assert result.animation_type == "rekindle"

        profile = db_session.query(UserProfile).filter_by(user_id=uid).one()
        assert profile.last_activity_date == date(2026, 5, 19)
        assert profile.longest_streak == 1
        assert profile.last_animation_type == "rekindle"

        row = db_session.query(DailyActivity).filter_by(user_id=uid).one()
        assert row.streak_awarded is True

    def test_two_activities_same_day_no_double_increment(self, db_session):
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        svc.record_in_same_tx(user_id=uid, now_utc=_fixed_utc(date(2026, 5, 19)))
        db_session.commit()
        result2 = svc.record_in_same_tx(
            user_id=uid,
            now_utc=_fixed_utc(date(2026, 5, 19), hour_utc=12),
        )
        db_session.commit()
        assert result2.state == "STREAK_ALREADY_COMPLETED_TODAY"
        assert result2.current_streak == 1
        assert result2.animation_type is None
        row = db_session.query(DailyActivity).filter_by(user_id=uid).one()
        assert row.activity_count == 2
        assert row.streak_awarded is True

    def test_consecutive_day_increments(self, db_session):
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        svc.record_in_same_tx(user_id=uid, now_utc=_fixed_utc(date(2026, 5, 19)))
        db_session.commit()
        result = svc.record_in_same_tx(
            user_id=uid,
            now_utc=_fixed_utc(date(2026, 5, 20)),
        )
        db_session.commit()
        assert result.state == "STREAK_CONTINUED"
        assert result.current_streak == 2
        assert result.animation_type == "on_fire"

    def test_one_missed_day_strict_resets_with_frozen_to_fire(self, db_session):
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        svc.record_in_same_tx(user_id=uid, now_utc=_fixed_utc(date(2026, 5, 19)))
        db_session.commit()
        result = svc.record_in_same_tx(
            user_id=uid,
            now_utc=_fixed_utc(date(2026, 5, 21)),
        )
        db_session.commit()
        assert result.state == "STREAK_RESET"
        assert result.current_streak == 1
        assert result.animation_type == "frozen_to_fire"

    def test_one_missed_day_with_freeze_protects(self, db_session, monkeypatch):
        monkeypatch.setattr(streak_service_module, "MAX_AUTO_FREEZE_DAYS", 1)
        uid = _make_user(db_session)
        profile = db_session.query(UserProfile).filter_by(user_id=uid).one()
        profile.streak_freezes = 1
        db_session.commit()

        svc = StreakService(db_session)
        svc.record_in_same_tx(user_id=uid, now_utc=_fixed_utc(date(2026, 5, 19)))
        db_session.commit()
        result = svc.record_in_same_tx(
            user_id=uid,
            now_utc=_fixed_utc(date(2026, 5, 21)),
        )
        db_session.commit()
        assert result.state == "STREAK_FROZEN"
        assert result.current_streak == 2
        assert result.freezes_remaining == 0
        assert result.animation_type == "frozen"
        freeze_row = db_session.query(StreakFreezeUsage).filter_by(user_id=uid).one()
        assert freeze_row.protected_date == date(2026, 5, 20)

    def test_midnight_boundary_two_local_days(self, db_session):
        """23:55 IST and 00:05 IST next calendar day → two streak days."""
        uid = _make_user(db_session, tz="Asia/Kolkata")
        svc = StreakService(db_session)
        d1 = date(2026, 5, 19)
        d2 = date(2026, 5, 20)
        svc.record_in_same_tx(user_id=uid, now_utc=_ist_late_night(d1, 23, 55))
        db_session.commit()
        result = svc.record_in_same_tx(
            user_id=uid,
            now_utc=_ist_late_night(d2, 0, 5),
        )
        db_session.commit()
        assert result.current_streak == 2
        assert result.animation_type == "on_fire"
        assert db_session.query(DailyActivity).filter_by(user_id=uid).count() == 2


class TestGetStreakData:
    def test_grid_length_91_and_intensity_clamps(self, db_session):
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        for h in range(5):
            svc.record_in_same_tx(
                user_id=uid,
                now_utc=_fixed_utc(date(2026, 5, 19), hour_utc=6 + h),
            )
        db_session.commit()

        data = svc.get_streak_data(user_id=uid)
        assert len(data.activity_grid) == 91
        row = db_session.query(DailyActivity).filter_by(user_id=uid).one()
        assert row.activity_count == 5
        assert all(c.intensity <= 4 for c in data.activity_grid)

    def test_animation_seen_marks_profile(self, db_session):
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        svc.record_in_same_tx(user_id=uid)
        db_session.commit()

        data = svc.get_streak_data(user_id=uid)
        assert data.today_complete is True
        assert data.today_streak_awarded is True
        assert data.should_show_animation is True
        assert data.animation_type == "rekindle"
        assert data.streak_status == "active"

        svc.mark_animation_seen(user_id=uid)
        data2 = svc.get_streak_data(user_id=uid)
        assert data2.should_show_animation is False
        assert data2.animation_type is None

    def test_streak_status_frozen_before_return(self, db_session, monkeypatch):
        """After a miss, status is frozen until the user completes today."""
        from app.modules.streaks.dates import get_user_local_date as _real_local_date

        def _patched_local_date(tz, now_utc=None):
            if now_utc is not None:
                return _real_local_date(tz, now_utc=now_utc)
            return date(2026, 5, 22)

        monkeypatch.setattr(
            streak_service_module,
            "get_user_local_date",
            _patched_local_date,
        )
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        svc.record_in_same_tx(user_id=uid, now_utc=_fixed_utc(date(2026, 5, 19)))
        db_session.commit()

        data = svc.get_streak_data(user_id=uid)
        assert data.streak_status == "frozen"
        assert data.today_complete is False

    def test_legacy_animation_coercion(self, db_session, monkeypatch):
        from app.modules.streaks.dates import get_user_local_date as _real_local_date

        fixed_today = date(2026, 5, 19)

        def _patched_local_date(tz, now_utc=None):
            if now_utc is not None:
                return _real_local_date(tz, now_utc=now_utc)
            return fixed_today

        monkeypatch.setattr(
            streak_service_module,
            "get_user_local_date",
            _patched_local_date,
        )
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        svc.record_in_same_tx(user_id=uid, now_utc=_fixed_utc(fixed_today))
        db_session.commit()
        profile = db_session.query(UserProfile).filter_by(user_id=uid).one()
        profile.last_animation_type = "continued"
        profile.last_seen_streak_animation_date = None
        db_session.commit()
        data = svc.get_streak_data(user_id=uid)
        assert data.animation_type == "on_fire"
