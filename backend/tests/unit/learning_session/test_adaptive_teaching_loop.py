"""Adaptive teaching loop (Tier B): classify-then-route + green-path cursor.

The teaching phase used to be a turn-count cursor walker: every teacher
message advanced the script cursor, so a redirect or a re-teach pushed the
learner toward the practice task, and a confused learner near the end was
force-wrapped with "Ready to try the practice task?". A correct in-chat
answer was never acknowledged.

These tests pin the new behaviour:
- the cursor advances ONLY on a genuine answer (green path); redirects and
  re-teaches hold it (derived from message tags, no DB column);
- confusion routes to a re-teach (``stayed=True``), never to the readiness
  question — even when the authored plan is exhausted (Failure 2 guard);
- a short relevant answer ("on") advances and is not redirected (Failure 1
  guard).
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.ai.agents.relevance_classifier import RelevanceVerdict
from app.ai.agents.teacher import _system_prompt
from app.modules.learning_session import service as ls_service
from app.modules.learning_session.service import (
    LearningSessionService,
    _count_green_path_turns,
    _count_trailing_stays,
    _stuck_on_step_count,
)
from app.modules.learning_session.schemas import WSIncomingMessage

_PLAN_KEY = "__scripted_plan"


# ── Pure helpers ────────────────────────────────────────────────────────────


def test_count_trailing_stays() -> None:
    assert _count_trailing_stays([]) == 0
    messages = [
        {"role": "ai", "content": "Step.", "type": "chat"},
        {"role": "user", "content": "huh?", "type": "chat"},
        {"role": "ai", "content": "Re-teach.", "type": "chat", "stayed": True},
        {"role": "user", "content": "still lost", "type": "chat"},
        {"role": "ai", "content": "Re-teach again.", "type": "chat", "stayed": True},
    ]
    assert _count_trailing_stays(messages) == 2
    # A normal (advancing) teacher turn breaks the streak.
    messages.append({"role": "user", "content": "on", "type": "chat"})
    messages.append({"role": "ai", "content": "Yes — 'on'.", "type": "chat"})
    assert _count_trailing_stays(messages) == 0


def test_count_green_path_turns_excludes_redirects_and_stays() -> None:
    messages = [
        {"role": "ai", "content": "Opener.", "type": "chat"},  # green (step 1)
        {"role": "user", "content": "asdkjfh", "type": "chat"},
        {"role": "ai", "content": "Off-topic.", "type": "chat", "redirect": True},
        {"role": "user", "content": "huh?", "type": "chat"},
        {"role": "ai", "content": "Re-teach.", "type": "chat", "stayed": True},
        {"role": "user", "content": "on", "type": "chat"},
        {"role": "ai", "content": "Yes — 'on'.", "type": "chat"},  # green (step 2)
    ]
    # Only the two untagged teacher turns count toward the cursor.
    assert _count_green_path_turns(messages) == 2
    assert _count_green_path_turns([]) == 0


def test_stuck_on_step_count_combines_redirects_and_stays() -> None:
    messages = [
        {"role": "ai", "content": "Step.", "type": "chat"},
        {"role": "user", "content": "x", "type": "chat"},
        {"role": "ai", "content": "Off-topic.", "type": "chat", "redirect": True},
        {"role": "user", "content": "y", "type": "chat"},
        {"role": "ai", "content": "Re-teach.", "type": "chat", "stayed": True},
    ]
    assert _stuck_on_step_count(messages) == 2


# ── Test scaffolding ────────────────────────────────────────────────────────


def _make_service() -> LearningSessionService:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service._apply_update = MagicMock()
    return service


def _stub_teacher_stream(
    *,
    text: str = "Stub teaching turn. Can you try one short sentence?",
    captured: dict | None = None,
):
    async def _stream(**kwargs):
        if captured is not None:
            captured.update(kwargs)
        yield text

    return _stream


def _state(
    messages: list[dict], *, plan_len: int = 4, topic: str = "Prepositions"
) -> dict:
    plan = [f"Step {i} teaching beat." for i in range(1, plan_len + 1)]
    return {
        "phase": "teaching",
        "topic": topic,
        "skill_name": "grammar",
        "task_type": "fill_in_blanks",
        "user_level": 1,
        "learner_profile": {},
        "messages": messages,
        "daily_plan": {"teacher_instructions": {_PLAN_KEY: plan}},
    }


async def _drain(agen) -> list:
    return [item async for item in agen]


# ── Cursor: advance on accept, hold + tag on re-teach ───────────────────────


@pytest.mark.asyncio
async def test_stream_teaching_turn_advances_cursor_on_accept(monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        ls_service, "stream_teaching_turn", _stub_teacher_stream(captured=captured)
    )
    service = _make_service()
    messages = [
        {"role": "ai", "content": "Opener: step 1.", "type": "chat"},
        {"role": "user", "content": "on", "type": "chat"},
    ]
    state = _state(messages)

    await _drain(service._stream_teaching_turn(MagicMock(), state, stay_on_step=False))

    # One green-path turn so far (the opener) -> next turn is step 2.
    assert captured["current_step_index"] == 2
    persisted = service._apply_update.call_args.args[1]
    assert "stayed" not in persisted["messages"][-1]
    hint = captured["teacher_instructions"]["authored_plan_status"]
    assert "Advance only" in hint


@pytest.mark.asyncio
async def test_stream_teaching_turn_holds_cursor_and_tags_stayed(monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        ls_service, "stream_teaching_turn", _stub_teacher_stream(captured=captured)
    )
    service = _make_service()
    messages = [
        {"role": "ai", "content": "Opener: step 1.", "type": "chat"},
        {"role": "user", "content": "on the table", "type": "chat"},
        {"role": "ai", "content": "Step 2 teaching.", "type": "chat"},
        {"role": "user", "content": "I don't understand", "type": "chat"},
    ]
    state = _state(messages)

    await _drain(service._stream_teaching_turn(MagicMock(), state, stay_on_step=True))

    # Two green-path turns -> cursor would be step 3, but a re-teach HOLDS at 2.
    assert captured["current_step_index"] == 2
    persisted = service._apply_update.call_args.args[1]
    assert persisted["messages"][-1]["stayed"] is True
    hint = captured["teacher_instructions"]["authored_plan_status"]
    assert "confused" in hint.lower()


@pytest.mark.asyncio
async def test_stream_teaching_turn_eases_forward_when_stuck(monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        ls_service, "stream_teaching_turn", _stub_teacher_stream(captured=captured)
    )
    service = _make_service()
    # Three consecutive non-advancing trailing turns -> safety-net kicks in.
    messages = [
        {"role": "ai", "content": "Opener.", "type": "chat"},
        {"role": "user", "content": "huh", "type": "chat"},
        {"role": "ai", "content": "Re-teach 1.", "type": "chat", "stayed": True},
        {"role": "user", "content": "what", "type": "chat"},
        {"role": "ai", "content": "Re-teach 2.", "type": "chat", "stayed": True},
        {"role": "user", "content": "still lost", "type": "chat"},
        {"role": "ai", "content": "Off-topic.", "type": "chat", "redirect": True},
        {"role": "user", "content": "no idea", "type": "chat"},
    ]
    state = _state(messages)

    await _drain(service._stream_teaching_turn(MagicMock(), state, stay_on_step=True))

    hint = captured["teacher_instructions"]["authored_plan_status"]
    assert "stuck" in hint.lower()
    assert "tiny hint" in hint.lower()


# ── Router: verdict -> route (driving _handle_user_message_stream) ──────────


@pytest.mark.asyncio
async def test_relevant_short_answer_advances_not_redirect(monkeypatch) -> None:
    """Failure 1 guard: a correct one-word answer is accepted, not redirected."""

    async def _classify(**_):
        return RelevanceVerdict(verdict="RELEVANT")

    monkeypatch.setattr(ls_service, "classify_reply_relevance", _classify)
    monkeypatch.setattr(ls_service, "stream_teaching_turn", _stub_teacher_stream())
    service = _make_service()
    messages = [
        {
            "role": "ai",
            "content": "What preposition fits 'the book ___ the table'?",
            "type": "chat",
        },
    ]
    state = _state(messages)
    msg = WSIncomingMessage(type="user_message", content="on")

    await _drain(service._handle_user_message_stream(MagicMock(), state, msg))

    last = service._apply_update.call_args.args[1]["messages"][-1]
    assert last.get("redirect") is not True
    assert last.get("stayed") is not True
    assert "off-topic" not in (last["content"] or "").lower()


@pytest.mark.asyncio
async def test_confusion_reteaches_not_readiness_when_plan_exhausted(
    monkeypatch,
) -> None:
    """Failure 2 guard: confusion re-teaches even with the plan exhausted and
    the last tutor message being the readiness prompt — never force-wrap."""

    async def _classify(**_):  # deterministic confusion -> classifier must not run
        raise AssertionError("classifier should not run for deterministic confusion")

    monkeypatch.setattr(ls_service, "classify_reply_relevance", _classify)
    monkeypatch.setattr(
        ls_service,
        "stream_teaching_turn",
        _stub_teacher_stream(text="Let me re-explain. Can you try one short sentence?"),
    )
    service = _make_service()
    messages = [
        {"role": "ai", "content": "Step 1.", "type": "chat"},
        {"role": "user", "content": "in", "type": "chat"},
        {"role": "ai", "content": "Step 2.", "type": "chat"},
        {"role": "user", "content": "on", "type": "chat"},
        {"role": "ai", "content": "Step 3.", "type": "chat"},
        {"role": "user", "content": "at", "type": "chat"},
        {"role": "ai", "content": "Ready to try the practice task?", "type": "chat"},
    ]
    state = _state(messages, plan_len=4)
    msg = WSIncomingMessage(
        type="user_message",
        content="I don't understand the question, could you explain it",
    )

    await _drain(service._handle_user_message_stream(MagicMock(), state, msg))

    last = service._apply_update.call_args.args[1]["messages"][-1]
    assert last["type"] == "chat"
    assert last.get("stayed") is True
    # Routed to a re-teach, not the readiness/practice transition.
    assert "ready to try the practice task" not in (last["content"] or "").lower()


@pytest.mark.asyncio
async def test_classifier_confused_verdict_reteaches(monkeypatch) -> None:
    async def _classify(**_):
        return RelevanceVerdict(verdict="CONFUSED")

    monkeypatch.setattr(ls_service, "classify_reply_relevance", _classify)
    monkeypatch.setattr(ls_service, "stream_teaching_turn", _stub_teacher_stream())
    service = _make_service()
    messages = [
        {"role": "ai", "content": "What preposition fits here?", "type": "chat"}
    ]
    state = _state(messages)
    # Not caught by deterministic _is_confusion/_is_structural_gibberish, so the
    # CONFUSED classifier verdict is what routes it to a re-teach.
    msg = WSIncomingMessage(type="user_message", content="the dog runs fast")

    await _drain(service._handle_user_message_stream(MagicMock(), state, msg))

    last = service._apply_update.call_args.args[1]["messages"][-1]
    assert last.get("stayed") is True


@pytest.mark.asyncio
async def test_off_topic_redirects(monkeypatch) -> None:
    async def _classify(**_):
        return RelevanceVerdict(verdict="OFF_TOPIC")

    monkeypatch.setattr(ls_service, "classify_reply_relevance", _classify)
    monkeypatch.setattr(ls_service, "stream_teaching_turn", _stub_teacher_stream())
    service = _make_service()
    messages = [
        {"role": "ai", "content": "What preposition fits here?", "type": "chat"}
    ]
    state = _state(messages)
    msg = WSIncomingMessage(
        type="user_message", content="I had pizza for lunch yesterday"
    )

    await _drain(service._handle_user_message_stream(MagicMock(), state, msg))

    last = service._apply_update.call_args.args[1]["messages"][-1]
    assert last["redirect"] is True


@pytest.mark.asyncio
async def test_gibberish_redirects(monkeypatch) -> None:
    async def _classify(**_):  # structural gibberish is deterministic
        raise AssertionError("classifier should not run for structural gibberish")

    monkeypatch.setattr(ls_service, "classify_reply_relevance", _classify)
    monkeypatch.setattr(ls_service, "stream_teaching_turn", _stub_teacher_stream())
    service = _make_service()
    messages = [
        {"role": "ai", "content": "What preposition fits here?", "type": "chat"}
    ]
    state = _state(messages)
    msg = WSIncomingMessage(type="user_message", content="asdkjfh")

    await _drain(service._handle_user_message_stream(MagicMock(), state, msg))

    last = service._apply_update.call_args.args[1]["messages"][-1]
    assert last["redirect"] is True


# ── Teacher prompt: forcing removed, inline grade + re-teach present ────────


def test_system_prompt_drops_unconditional_turn_ceiling() -> None:
    prompt = _system_prompt()
    assert "TURN-CEILING RULE" not in prompt
    assert "By turn 5 at the absolute latest" not in prompt
    assert "SAFETY-CEILING RULE" in prompt


def test_system_prompt_has_inline_grade_split_and_reteach() -> None:
    one_line = " ".join(_system_prompt().split())
    # Inline correct/wrong grading split.
    assert "If the answer is CORRECT" in one_line
    assert "WRONG but genuine attempt" in one_line
    # Fail-soft: never re-ask just because unsure.
    assert "treat it as a reasonable attempt" in one_line
    # Confusion re-teaches and never jumps to readiness.
    assert "do NOT advance to the next step" in one_line
