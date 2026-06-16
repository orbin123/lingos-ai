"""require_verified guard: unit behavior + diagnosis-router wiring."""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.modules.auth.dependencies import get_current_user, require_verified
from app.modules.auth.models import User
from app.modules.diagnosis.routes import router as diagnosis_router


def _user(verified: bool) -> User:
    return User(
        email="v@example.com", password_hash="x", name="V", email_verified=verified
    )


class TestUnit:
    def test_verified_user_passes(self):
        user = _user(True)
        assert require_verified(current_user=user) is user

    def test_unverified_user_403_with_code(self):
        with pytest.raises(HTTPException) as exc_info:
            require_verified(current_user=_user(False))
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "email_unverified"


class TestDiagnosisRouterWiring:
    def test_router_declares_require_verified(self):
        dependency_funcs = [dep.dependency for dep in diagnosis_router.dependencies]
        assert require_verified in dependency_funcs


class TestRouterIntegration:
    """The guard composes with an overridden get_current_user the same way
    the diagnosis router applies it."""

    def _client(self, user: User) -> TestClient:
        app = FastAPI()

        @app.get("/guarded", dependencies=[Depends(require_verified)])
        def guarded() -> dict[str, bool]:
            return {"ok": True}

        app.dependency_overrides[get_current_user] = lambda: user
        return TestClient(app)

    def test_verified_200(self):
        with self._client(_user(True)) as client:
            assert client.get("/guarded").status_code == 200

    def test_unverified_403(self):
        with self._client(_user(False)) as client:
            res = client.get("/guarded")
            assert res.status_code == 403
            assert res.json()["detail"]["code"] == "email_unverified"
