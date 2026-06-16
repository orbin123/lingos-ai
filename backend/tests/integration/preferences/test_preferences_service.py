"""Service tests for PreferenceService."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.preferences.models import UserCoursePreference
from app.modules.preferences.service import PreferenceService


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[User.__table__, UserCoursePreference.__table__],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _make_user(db) -> int:
    u = User(email="b@example.com", password_hash="x", name="L")
    db.add(u)
    db.commit()
    return u.id


def test_get_lazy_creates_row(db_session):
    uid = _make_user(db_session)
    pref = PreferenceService(db_session).get(user_id=uid)
    assert pref.user_id == uid
    assert pref.course_length == "24w"
    assert pref.tasks_per_day == 2


def test_get_is_idempotent(db_session):
    uid = _make_user(db_session)
    svc = PreferenceService(db_session)
    p1 = svc.get(user_id=uid)
    p2 = svc.get(user_id=uid)
    assert p1.id == p2.id


def test_update_settings_persists(db_session):
    uid = _make_user(db_session)
    svc = PreferenceService(db_session)
    svc.update_settings(user_id=uid, tasks_per_day=3, allow_listen=False)
    pref = svc.get(user_id=uid)
    assert pref.tasks_per_day == 3
    assert pref.allow_listen is False
