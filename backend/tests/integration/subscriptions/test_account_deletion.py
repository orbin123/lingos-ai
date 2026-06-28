"""DELETE /api/users/me — learners can self-delete, admins cannot.

Admin / super-admin accounts are kept permanent: there is no app-layer
path to recreate an admin, so self-deletion is blocked with a 403 and the
row must survive.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (populate the ORM registry for cascade deletes)
from app.core.database import Base, get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.subscriptions.routes import users_router
from tests.factories.users import make_admin, make_super_admin, make_verified_user


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Account deletion cascades across many tables (oauth_accounts,
    # auth_sessions, subscriptions, …) — create the full schema so the
    # cascade has somewhere to land.
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _client(db, user: User) -> TestClient:
    app = FastAPI()
    app.include_router(users_router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


def test_learner_can_delete_account(db_session):
    user = make_verified_user(db_session)
    user_id = user.id
    with _client(db_session, user) as client:
        res = client.delete("/api/users/me")
    assert res.status_code == 204
    assert db_session.get(User, user_id) is None


def test_admin_cannot_delete_account(db_session):
    admin = make_admin(db_session)
    admin_id = admin.id
    with _client(db_session, admin) as client:
        res = client.delete("/api/users/me")
    assert res.status_code == 403
    assert res.json()["detail"]["code"] == "account_not_deletable"
    assert db_session.get(User, admin_id) is not None


def test_super_admin_cannot_delete_account(db_session):
    super_admin = make_super_admin(db_session)
    super_admin_id = super_admin.id
    with _client(db_session, super_admin) as client:
        res = client.delete("/api/users/me")
    assert res.status_code == 403
    assert res.json()["detail"]["code"] == "account_not_deletable"
    assert db_session.get(User, super_admin_id) is not None
