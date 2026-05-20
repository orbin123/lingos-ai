"""Route tests for /preferences — GET and PATCH via TestClient + overrides."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.core.database import Base, get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.preferences.models import UserCoursePreference
from app.modules.preferences.routes import router as preferences_router


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
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


@pytest.fixture()
def user(db_session):
    u = User(email="c@example.com", password_hash="x", name="L")
    db_session.add(u)
    db_session.commit()
    return u


@pytest.fixture()
def client(db_session, user):
    app = FastAPI()
    app.include_router(preferences_router, prefix="/api")

    def _override_db():
        yield db_session

    def _override_user():
        return user

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _override_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestGet:
    def test_returns_defaults_for_new_user(self, client):
        resp = client.get("/api/preferences")
        assert resp.status_code == 200
        body = resp.json()
        assert body["course_length"] == "24w"
        assert body["tasks_per_day"] == 2
        assert body["allow_read"] is True
        assert body["current_week"] == 1
        assert body["current_day_in_week"] == 1
        assert body["last_completed_on"] is None


class TestPatch:
    def test_partial_update_round_trips(self, client):
        resp = client.patch(
            "/api/preferences",
            json={"tasks_per_day": 4, "allow_speak": False, "course_length": "48w"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["tasks_per_day"] == 4
        assert body["allow_speak"] is False
        assert body["course_length"] == "48w"
        # Unmentioned fields keep their defaults.
        assert body["allow_read"] is True

        # Re-fetch — confirm persistence.
        again = client.get("/api/preferences").json()
        assert again["tasks_per_day"] == 4
        assert again["course_length"] == "48w"

    def test_tasks_per_day_out_of_range_422(self, client):
        resp = client.patch("/api/preferences", json={"tasks_per_day": 5})
        assert resp.status_code == 422

    def test_invalid_course_length_422(self, client):
        resp = client.patch("/api/preferences", json={"course_length": "12w"})
        assert resp.status_code == 422
