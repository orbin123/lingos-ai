"""Shared FastAPI `TestClient` fixtures with dependency overrides.

`client` wires the app's `get_db` to the in-memory `db_session` so HTTP tests
hit the same DB the test seeds. `auth_client` additionally overrides
`get_current_user` with a freshly-made verified learner, exposing it as
`auth_client.user` for assertions.

Both clear `app.dependency_overrides` on teardown so overrides never leak
between tests (the app object is a module-level singleton).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app as fastapi_app
from app.modules.auth.dependencies import get_current_user
from tests.factories.users import make_verified_user


@pytest.fixture
def client(db_session):
    """TestClient whose `get_db` yields the shared in-memory session."""
    fastapi_app.dependency_overrides[get_db] = lambda: db_session
    try:
        with TestClient(fastapi_app) as test_client:
            yield test_client
    finally:
        fastapi_app.dependency_overrides.clear()


@pytest.fixture
def auth_client(db_session):
    """TestClient authenticated as a verified learner (`.user` is the row)."""
    user = make_verified_user(db_session)
    fastapi_app.dependency_overrides[get_db] = lambda: db_session
    fastapi_app.dependency_overrides[get_current_user] = lambda: user
    try:
        with TestClient(fastapi_app) as test_client:
            test_client.user = user
            yield test_client
    finally:
        fastapi_app.dependency_overrides.clear()
