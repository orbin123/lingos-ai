"""WebSocket heartbeat: a `ping` is ponged without touching session logic.

The `LearningSession` model uses JSONB columns SQLite can't compile, so we
stub the service + auth helpers at the router module boundary rather than
loading a real session row. That keeps this test focused on the receive-loop
contract: ping → pong, and ping must NOT enter the rate-limit / session
pipeline (it is a keepalive, not a learner action).
"""

from __future__ import annotations

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.modules.learning_session import router as ws_router_module


class _FakeService:
    """Quacks like LearningSessionService for the WS route's happy path.

    Resume/initial streams yield nothing so we reach the receive loop
    immediately; ``process_message_stream`` records the message TYPES it sees
    so the test can prove a ping never reaches it.
    """

    process_calls: list[str] = []
    # Non-empty messages → the route takes the resume path.
    session = SimpleNamespace(
        user_id=1,
        messages=[{"role": "ai", "content": "hi", "type": "chat"}],
        phase="teaching",
    )

    def __init__(self, db) -> None:  # noqa: ANN001
        self.db = db
        self.session_repo = SimpleNamespace(
            get_by_session_id=lambda _sid: _FakeService.session
        )

    async def initial_messages_stream(self, _session_id):  # noqa: ANN001
        return
        yield  # pragma: no cover — empty async generator

    async def resume_messages_stream(self, _session_id):  # noqa: ANN001
        return
        yield  # pragma: no cover — empty async generator

    async def process_message_stream(self, _session_id, incoming):  # noqa: ANN001
        _FakeService.process_calls.append(incoming.type)
        return
        yield  # pragma: no cover — empty async generator


def _build_app(monkeypatch) -> FastAPI:
    _FakeService.process_calls = []
    _FakeService.session.phase = "teaching"

    fake_user = SimpleNamespace(id=1, has_any_role=lambda _roles: True)
    monkeypatch.setattr(
        ws_router_module, "_resolve_user_from_token", lambda _token, _db: fake_user
    )
    monkeypatch.setattr(ws_router_module, "check_ws_access", lambda _user, _db: True)
    monkeypatch.setattr(ws_router_module, "LearningSessionService", _FakeService)

    app = FastAPI()
    app.include_router(ws_router_module.ws_router)
    app.dependency_overrides[get_db] = lambda: SimpleNamespace()
    return app


def test_ping_is_ponged_without_entering_session_pipeline(monkeypatch) -> None:
    app = _build_app(monkeypatch)

    with TestClient(app) as client:
        with client.websocket_connect("/ws/learning/s1?token=x") as ws:
            ws.send_json({"type": "ping"})
            assert ws.receive_json() == {"type": "pong"}

            # The ping never reached the session pipeline.
            assert _FakeService.process_calls == []

            # A real learner message DOES reach the pipeline. The second ping is
            # a FIFO barrier: once its pong returns, the user_message before it
            # must already have been read and processed by the receive loop.
            ws.send_json({"type": "user_message", "content": "hello"})
            ws.send_json({"type": "ping"})
            assert ws.receive_json() == {"type": "pong"}

    assert _FakeService.process_calls == ["user_message"]
    # Ping is a no-op on session state — the stubbed session was never mutated.
    assert _FakeService.session.phase == "teaching"
