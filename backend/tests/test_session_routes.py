"""Route-level smoke test — confirms all sessions endpoints are mounted.

Deep service behavior is covered by `test_session_lifecycle.py` and
`test_session_replay_and_scoring.py`. This file just asserts the wiring.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.sessions.routes import router as sessions_router


def _build_client() -> TestClient:
    """Build a minimal FastAPI app with just the sessions router mounted."""
    app = FastAPI()
    app.include_router(sessions_router, prefix="/api")
    return TestClient(app)


class TestEndpointDiscovery:
    def test_all_endpoints_are_mounted(self):
        client = _build_client()
        paths = [r.path for r in client.app.router.routes]
        assert "/api/sessions/start" in paths
        assert "/api/sessions/start-today" in paths
        assert "/api/sessions/{session_id}/next-activity" in paths
        assert "/api/sessions/{session_id}/activities/{sequence}/submit" in paths
        assert "/api/sessions/{session_id}/complete" in paths
        assert "/api/sessions/{session_id}/scorecard" in paths
