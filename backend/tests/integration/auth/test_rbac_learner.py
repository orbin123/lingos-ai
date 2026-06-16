"""RBAC tests for the learner-surface guard (require_learner).

Enforcement is inclusive by design: User.role_names() defaults to "learner"
when a user has no role rows, admins typically also hold the learner role,
and super admins are allowed through (owner accounts predate the role tables
and may hold only admin roles). Only tokens scoped exclusively to the plain
"admin" role are rejected.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401 — populate the ORM registry
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.modules.auth.dependencies import get_current_user, require_learner
from app.modules.auth.models import (
    ROLE_ADMIN,
    ROLE_LEARNER,
    ROLE_SUPER_ADMIN,
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
)
from app.modules.preferences.models import UserCoursePreference
from app.modules.preferences.routes import router as preferences_router


def _user_with_roles(*role_names: str) -> User:
    """Build a transient (non-persisted) user holding the given roles."""
    user = User(email="rbac@example.com", password_hash="x", name="R")
    for name in role_names:
        user.role_links.append(UserRole(role=Role(name=name)))
    return user


class TestRequireLearnerUnit:
    def test_user_with_no_roles_passes(self):
        user = _user_with_roles()
        assert require_learner(current_user=user) is user

    def test_learner_passes(self):
        user = _user_with_roles(ROLE_LEARNER)
        assert require_learner(current_user=user) is user

    def test_admin_who_also_holds_learner_passes(self):
        user = _user_with_roles(ROLE_LEARNER, ROLE_ADMIN)
        assert require_learner(current_user=user) is user

    def test_admin_only_rejected_403(self):
        user = _user_with_roles(ROLE_ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            require_learner(current_user=user)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Insufficient role"

    def test_super_admin_without_learner_passes(self):
        # Owner accounts predate the role tables and may hold only admin
        # roles — super admins keep access to the learner surface.
        user = _user_with_roles(ROLE_ADMIN, ROLE_SUPER_ADMIN)
        assert require_learner(current_user=user) is user

    def test_legacy_is_superuser_flag_passes(self):
        user = _user_with_roles()
        user.is_superuser = True
        assert require_learner(current_user=user) is user


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            Role.__table__,
            UserRole.__table__,
            Permission.__table__,
            RolePermission.__table__,
            UserCoursePreference.__table__,
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _persist_user_with_roles(db_session, *role_names: str) -> User:
    user = User(email=f"{'-'.join(role_names) or 'norole'}@example.com",
                password_hash="x", name="R")
    for name in role_names:
        user.role_links.append(UserRole(role=Role(name=name)))
    db_session.add(user)
    db_session.commit()
    return user


def _client_for(db_session, user: User) -> TestClient:
    app = FastAPI()
    app.include_router(preferences_router, prefix="/api")
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


class TestLearnerRouterGuard:
    """The router-level guard applies on top of overridden get_current_user."""

    def test_no_role_user_gets_200(self, db_session):
        user = _persist_user_with_roles(db_session)
        with _client_for(db_session, user) as client:
            assert client.get("/api/preferences").status_code == 200

    def test_admin_only_user_gets_403(self, db_session):
        user = _persist_user_with_roles(db_session, ROLE_ADMIN)
        with _client_for(db_session, user) as client:
            resp = client.get("/api/preferences")
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Insufficient role"}


class TestWebSocketResolvers:
    def test_learning_ws_resolver_returns_user_with_roles_loaded(self, db_session):
        from app.modules.learning_session.router import _resolve_user_from_token

        user = _persist_user_with_roles(db_session, ROLE_LEARNER)
        token = create_access_token({"sub": str(user.id)})
        resolved = _resolve_user_from_token(token, db_session)
        assert resolved is not None
        assert resolved.id == user.id
        assert resolved.has_any_role({ROLE_LEARNER})

    def test_a2z_resolver_accepts_no_role_user(self, db_session):
        from app.modules.challenges.a2z_game.ws_stream import _resolve_user_id

        user = _persist_user_with_roles(db_session)
        token = create_access_token({"sub": str(user.id)})
        assert _resolve_user_id(token, db_session) == user.id

    def test_a2z_resolver_rejects_admin_only_user(self, db_session):
        from app.modules.challenges.a2z_game.ws_stream import _resolve_user_id

        user = _persist_user_with_roles(db_session, ROLE_ADMIN)
        token = create_access_token({"sub": str(user.id)})
        assert _resolve_user_id(token, db_session) is None
