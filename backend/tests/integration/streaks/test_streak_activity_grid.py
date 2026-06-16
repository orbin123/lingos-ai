"""Heatmap counts evaluated activities, not completed sessions."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401
from app.core.database import Base
from app.modules.auth.models import User, UserProfile
from app.modules.sessions.models import ActivityAttempt, AttemptStatus, DailySession
from app.modules.streaks.activity_grid import count_evaluated_activities_by_local_date
from app.modules.streaks.models import DailyActivity, StreakFreezeUsage
from app.modules.streaks.service import StreakService
from scripts.seed_curriculum import seed_archetypes
from app.modules.curriculum.models import TaskArchetype


@pytest.fixture()
def grid_db():
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
        user = User(email="grid@example.com", password_hash="x", name="G")
        db.add(user)
        db.flush()
        db.add(UserProfile(user_id=user.id, timezone="Asia/Kolkata"))
        seed_archetypes(db)
        db.commit()
        yield db, user.id
    finally:
        db.close()
        engine.dispose()


def _utc(local_d: date, hour: int = 6) -> datetime:
    return datetime.combine(
        local_d, datetime.min.time(), tzinfo=timezone.utc
    ) + __import__("datetime").timedelta(hours=hour)


def _session_with_attempts(
    db,
    *,
    user_id: int,
    local_d: date,
    evaluated_count: int,
) -> None:
    session = DailySession(
        session_id=f"s-{local_d.isoformat()}",
        user_id=user_id,
        day_id="day_24_01_01",
        course_length="24w",
        status="in_progress",
        is_first_attempt=True,
        started_at=_utc(local_d),
    )
    db.add(session)
    db.flush()
    for seq in range(1, evaluated_count + 1):
        db.add(
            ActivityAttempt(
                session_id=session.id,
                archetype_id="READ_CLOZE",
                sequence=seq,
                status=AttemptStatus.EVALUATED,
                task_content={"prompt": "x"},
                submitted_at=_utc(local_d, hour=6 + seq),
            )
        )
    db.commit()


class TestActivityGridCounts:
    def test_counts_evaluated_attempts_not_sessions(self, grid_db):
        db, uid = grid_db
        target = date(2026, 5, 22)
        _session_with_attempts(db, user_id=uid, local_d=target, evaluated_count=4)

        counts = count_evaluated_activities_by_local_date(
            db,
            user_id=uid,
            tz="Asia/Kolkata",
            start=target,
            end=target,
        )
        assert counts[target] == 4

    def test_get_streak_data_uses_attempt_counts_for_intensity(
        self, grid_db, monkeypatch
    ):
        db, uid = grid_db
        target = date(2026, 5, 22)
        monkeypatch.setattr(
            "app.modules.streaks.service.get_user_local_date",
            lambda tz, now_utc=None: target,
        )
        _session_with_attempts(db, user_id=uid, local_d=target, evaluated_count=4)

        svc = StreakService(db)
        data = svc.get_streak_data(user_id=uid)
        today_cell = next(c for c in data.activity_grid if c.date == target.isoformat())
        assert today_cell.activity_count == 4
        assert today_cell.intensity == 4
        assert today_cell.completed is False

        svc.record_in_same_tx(user_id=uid, now_utc=_utc(target, hour=18))
        db.commit()
        data2 = svc.get_streak_data(user_id=uid)
        today_cell2 = next(
            c for c in data2.activity_grid if c.date == target.isoformat()
        )
        assert today_cell2.activity_count == 4
        assert today_cell2.intensity == 4
        assert today_cell2.completed is True
