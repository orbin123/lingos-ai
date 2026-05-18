"""Route-level smoke tests — the new sessions endpoints honor the feature flag.

Deep service behavior is covered by `test_session_lifecycle.py` and
`test_session_replay_and_scoring.py`. This file checks only:
  - all 4 endpoints return 404 when `use_new_session_flow` is off
  - all 4 endpoints are mounted under `/api/sessions`
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import settings
from app.modules.sessions.routes import router as sessions_router


def _build_client() -> TestClient:
    """Build a minimal FastAPI app with just the sessions router mounted."""
    app = FastAPI()
    app.include_router(sessions_router, prefix="/api")
    return TestClient(app)


class TestFeatureFlagGate:
    def test_start_returns_404_when_flag_off(self, monkeypatch):
        monkeypatch.setattr(settings, "use_new_session_flow", False)
        client = _build_client()
        resp = client.post("/api/sessions/start", json={
            "day_id": "day_24_01_01",
            "course_length": "24w",
            "tasks_per_day": 2,
        })
        assert resp.status_code == 404
        assert "USE_NEW_SESSION_FLOW" in resp.text

    def test_next_activity_returns_404_when_flag_off(self, monkeypatch):
        monkeypatch.setattr(settings, "use_new_session_flow", False)
        client = _build_client()
        resp = client.get("/api/sessions/abc-123/next-activity")
        assert resp.status_code == 404

    def test_submit_returns_404_when_flag_off(self, monkeypatch):
        monkeypatch.setattr(settings, "use_new_session_flow", False)
        client = _build_client()
        resp = client.post(
            "/api/sessions/abc-123/activities/1/submit",
            json={"user_response": {}},
        )
        assert resp.status_code == 404

    def test_complete_returns_404_when_flag_off(self, monkeypatch):
        monkeypatch.setattr(settings, "use_new_session_flow", False)
        client = _build_client()
        resp = client.post("/api/sessions/abc-123/complete")
        assert resp.status_code == 404

    def test_scorecard_returns_404_when_flag_off(self, monkeypatch):
        monkeypatch.setattr(settings, "use_new_session_flow", False)
        client = _build_client()
        resp = client.get("/api/sessions/abc-123/scorecard")
        assert resp.status_code == 404


class TestEndpointDiscovery:
    def test_all_endpoints_are_mounted(self):
        client = _build_client()
        paths = [r.path for r in client.app.router.routes]
        assert "/api/sessions/start" in paths
        assert "/api/sessions/{session_id}/next-activity" in paths
        assert "/api/sessions/{session_id}/activities/{sequence}/submit" in paths
        assert "/api/sessions/{session_id}/complete" in paths
        assert "/api/sessions/{session_id}/scorecard" in paths
