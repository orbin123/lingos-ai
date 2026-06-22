"""Route-level error translation for the dashboard "Start session" button.

A transient ``TaskGenerationFailed`` (the LLM couldn't produce renderable
content after retries) must surface as a 503 with a machine-readable
``task_generation_failed`` code — not a dead-end 500 — so the dashboard can
flip the button to a red "Retry session" affordance.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.ai.sessions.exceptions import TaskGenerationFailed
from app.modules.learning_session import router as ls_router


@pytest.mark.asyncio
async def test_start_session_translates_taskgen_failure_to_503(monkeypatch):
    class _FailingService:
        def __init__(self, _db):
            pass

        async def create_session(self, **_kwargs):
            raise TaskGenerationFailed("READ_ERROR_SPOT", "no valid payload")

    monkeypatch.setattr(ls_router, "LearningSessionService", _FailingService)

    with pytest.raises(HTTPException) as exc_info:
        await ls_router.start_session(
            payload=None,
            current_user=SimpleNamespace(id=1),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail["code"] == "task_generation_failed"
