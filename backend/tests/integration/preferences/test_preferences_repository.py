"""Repository tests for `UserCoursePreference` against in-memory SQLite."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401 — populate Base.metadata
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.preferences.models import UserCoursePreference
from app.modules.preferences.repository import UserCoursePreferenceRepository


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


def _make_user(db, email: str = "a@example.com") -> int:
    u = User(email=email, password_hash="x", name="L")
    db.add(u)
    db.flush()
    return u.id


class TestGetOrCreate:
    def test_creates_row_with_defaults_when_missing(self, db_session):
        uid = _make_user(db_session)
        pref = UserCoursePreferenceRepository(db_session).get_or_create_for_user(uid)
        db_session.commit()
        db_session.refresh(pref)

        assert pref.user_id == uid
        assert pref.course_length == "24w"
        assert pref.tasks_per_day == 2
        assert pref.allow_read is True
        assert pref.allow_write is True
        assert pref.allow_listen is True
        assert pref.allow_speak is True
        assert pref.current_week == 1
        assert pref.current_day_in_week == 1
        assert pref.last_completed_on is None

    def test_returns_existing_row_on_second_call(self, db_session):
        uid = _make_user(db_session)
        repo = UserCoursePreferenceRepository(db_session)
        first = repo.get_or_create_for_user(uid)
        db_session.commit()
        first_id = first.id

        second = repo.get_or_create_for_user(uid)
        db_session.commit()
        assert second.id == first_id


class TestUpdateSettings:
    def test_partial_update_applies_only_provided_fields(self, db_session):
        uid = _make_user(db_session)
        repo = UserCoursePreferenceRepository(db_session)
        pref = repo.get_or_create_for_user(uid)
        db_session.commit()

        repo.update_settings(pref, tasks_per_day=4, allow_speak=False)
        db_session.commit()
        db_session.refresh(pref)

        assert pref.tasks_per_day == 4
        assert pref.allow_speak is False
        # Untouched fields keep their defaults.
        assert pref.allow_read is True
        assert pref.course_length == "24w"

    def test_unknown_field_raises(self, db_session):
        uid = _make_user(db_session)
        repo = UserCoursePreferenceRepository(db_session)
        pref = repo.get_or_create_for_user(uid)
        db_session.commit()

        with pytest.raises(AttributeError):
            repo.update_settings(pref, definitely_not_a_field=42)

    def test_none_values_are_ignored(self, db_session):
        uid = _make_user(db_session)
        repo = UserCoursePreferenceRepository(db_session)
        pref = repo.get_or_create_for_user(uid)
        db_session.commit()

        repo.update_settings(pref, tasks_per_day=None, allow_read=False)
        db_session.commit()
        db_session.refresh(pref)
        assert pref.tasks_per_day == 2  # unchanged
        assert pref.allow_read is False
