"""Teaching-stream timeout regression guards (Phase 1, post GPT-5 migration).

The teacher buffers its whole LLM turn before yielding a single chunk, so the
service's FIRST-chunk timeout must cover a full generate (+ a possible
validation retry), not just first-token latency. The old 8s budget assumed
gpt-4o-mini's ~1-2s first token; on a slower model it expired, `_timed_chunks`
broke with an empty buffer, and `_stream_teaching_turn` emitted its hardcoded
"wait" fallback — i.e. zero teaching. These pin (a) the raised budget and
(b) that a valid teacher turn actually flows through.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.modules.learning_session import service as ls_service
from app.modules.learning_session.service import LearningSessionService

# A fragment unique to the service's canned fallback when no teacher content
# arrives in time (service.py `_stream_teaching_turn`). The whole bug is that
# the learner saw a canned message instead of a real lesson; the fallback now
# teaches rather than telling the learner to wait, so this fragment must never
# appear when the teacher streams a real turn.
_OUTER_FALLBACK_FRAGMENT = "We'll learn the key idea together"


def test_teaching_first_chunk_timeout_is_at_least_30s() -> None:
    """Budget must absorb a full buffered turn + one retry on the fast model."""
    assert ls_service._TEACHING_STREAM_FIRST_CHUNK_TIMEOUT_S >= 30.0
    assert ls_service._FOLLOWUP_STREAM_FIRST_CHUNK_TIMEOUT_S >= 30.0


@pytest.mark.asyncio
async def test_stream_teaching_turn_yields_llm_turn_not_outer_fallback(
    monkeypatch,
) -> None:
    """When the teacher streams a valid turn, the service emits THAT turn and
    persists it — never the canned outer fallback."""
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service._apply_update = MagicMock()

    turn = (
        "You used **walk** — that's the base verb. Can you change it to talk about she?"
    )

    async def _fast_teacher_stream(**_kwargs):
        # The real teacher buffers then yields once; mimic a single fast chunk.
        yield turn

    monkeypatch.setattr(ls_service, "stream_teaching_turn", _fast_teacher_stream)

    session = MagicMock()
    state = {
        "topic": "the simple present",
        "skill_name": "grammar",
        "task_type": "fill_in_blanks",
        "user_level": 1,
        "learner_profile": {},
        "messages": [],
        "daily_plan": {},
    }

    messages = [msg async for msg in service._stream_teaching_turn(session, state)]

    end = next(m for m in messages if m.type == "chat_stream_end")
    assert end.content == turn
    assert _OUTER_FALLBACK_FRAGMENT not in (end.content or "")

    # The streamed deltas reconstruct the real turn (not the fallback).
    deltas = "".join(m.content or "" for m in messages if m.type == "chat_stream_delta")
    assert deltas == turn

    # The persisted transcript ends with the real teaching turn.
    persisted = service._apply_update.call_args.args[1]
    assert persisted["phase"] == "teaching"
    assert persisted["messages"][-1]["content"] == turn
    assert _OUTER_FALLBACK_FRAGMENT not in persisted["messages"][-1]["content"]
