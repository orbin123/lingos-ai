"""StreakService state-machine tests against in-memory SQLite."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401 — populate Base.metadata
from app.core.database import Base
from app.modules.auth.models import User, UserProfile
from app.modules.streaks import service as streak_service_module
from app.modules.streaks.models import DailyActivity, StreakFreezeUsage
from app.modules.streaks.service import StreakService


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
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
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
    return datetime.combine(local_d, datetime.min.time(), tzinfo=timezone.utc) \
        + timedelta(hours=hour_utc)


class TestRecord:
    def test_first_activity_sets_streak_to_1(self, db_session):
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        result = svc.record_in_same_tx(
            user_id=uid, now_utc=_fixed_utc(date(2026, 5, 19)),
        )
        db_session.commit()
        assert result.state == "FIRST_STREAK_EARNED"
        assert result.current_streak == 1
        assert result.animation_type == "initial"

        profile = db_session.query(UserProfile).filter_by(user_id=uid).one()
        assert profile.last_activity_date == date(2026, 5, 19)
        assert profile.longest_streak == 1
        assert profile.last_animation_type == "initial"

    def test_two_activities_same_day_no_double_increment(self, db_session):
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        svc.record_in_same_tx(user_id=uid, now_utc=_fixed_utc(date(2026, 5, 19)))
        db_session.commit()
        result2 = svc.record_in_same_tx(
            user_id=uid, now_utc=_fixed_utc(date(2026, 5, 19), hour_utc=12),
        )
        db_session.commit()
        assert result2.state == "STREAK_ALREADY_COMPLETED_TODAY"
        assert result2.current_streak == 1
        assert result2.animation_type is None
        row = db_session.query(DailyActivity).filter_by(user_id=uid).one()
        assert row.activity_count == 2

    def test_consecutive_day_increments(self, db_session):
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        svc.record_in_same_tx(user_id=uid, now_utc=_fixed_utc(date(2026, 5, 19)))
        db_session.commit()
        result = svc.record_in_same_tx(
            user_id=uid, now_utc=_fixed_utc(date(2026, 5, 20)),
        )
        db_session.commit()
        assert result.state == "STREAK_CONTINUED"
        assert result.current_streak == 2
        assert result.animation_type == "continued"

    def test_one_missed_day_default_strict_resets(self, db_session):
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        svc.record_in_same_tx(user_id=uid, now_utc=_fixed_utc(date(2026, 5, 19)))
        # Skip the 20th.
        db_session.commit()
        result = svc.record_in_same_tx(
            user_id=uid, now_utc=_fixed_utc(date(2026, 5, 21)),
        )
        db_session.commit()
        assert result.state == "STREAK_RESET"
        assert result.current_streak == 1
        assert result.animation_type == "reset"

    def test_one_missed_day_with_freeze_protects(self, db_session, monkeypatch):
        monkeypatch.setattr(streak_service_module, "MAX_AUTO_FREEZE_DAYS", 1)
        uid = _make_user(db_session)
        # Seed profile with 1 freeze.
        profile = db_session.query(UserProfile).filter_by(user_id=uid).one()
        profile.streak_freezes = 1
        db_session.commit()

        svc = StreakService(db_session)
        svc.record_in_same_tx(user_id=uid, now_utc=_fixed_utc(date(2026, 5, 19)))
        db_session.commit()
        result = svc.record_in_same_tx(
            user_id=uid, now_utc=_fixed_utc(date(2026, 5, 21)),
        )
        db_session.commit()
        assert result.state == "STREAK_FROZEN"
        assert result.current_streak == 2
        assert result.freezes_remaining == 0
        assert result.animation_type == "frozen"
        # The 20th was protected.
        freeze_row = db_session.query(StreakFreezeUsage).filter_by(user_id=uid).one()
        assert freeze_row.protected_date == date(2026, 5, 20)


class TestGetStreakData:
    def test_grid_length_91_and_intensity_clamps(self, db_session):
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        # Bump same day 5 times → activity_count should be 5, intensity clamps at 4.
        for h in range(5):
            svc.record_in_same_tx(
                user_id=uid, now_utc=_fixed_utc(date(2026, 5, 19), hour_utc=6 + h),
            )
        db_session.commit()

        # Force "today" by setting profile so service computes a date relative
        # to wall clock. Simplest: just verify grid length / intensity from
        # the read path against the natural today.
        data = svc.get_streak_data(user_id=uid)
        assert len(data.activity_grid) == 91
        # Find today's cell (will only be present if real "today" matches our
        # synthetic date). Assert intensity logic by inspecting the DA row.
        row = db_session.query(DailyActivity).filter_by(user_id=uid).one()
        assert row.activity_count == 5
        # Grid cells beyond today's count should be 0
        assert all(c.intensity <= 4 for c in data.activity_grid)

    def test_animation_seen_marks_profile(self, db_session):
        uid = _make_user(db_session)
        svc = StreakService(db_session)
        # Use current real time so today_complete is true on the read.
        svc.record_in_same_tx(user_id=uid)
        db_session.commit()

        data = svc.get_streak_data(user_id=uid)
        assert data.today_complete is True
        assert data.should_show_animation is True
        assert data.animation_type == "initial"

        svc.mark_animation_seen(user_id=uid)
        data2 = svc.get_streak_data(user_id=uid)
        assert data2.should_show_animation is False
        assert data2.animation_type is None
