"""Model-aware construction of OpenAILLMClient.

gpt-5 (and the o-series) are reasoning models: the OpenAI API rejects any
custom `temperature`, so the client must omit it and use `reasoning_effort`
instead. Non-reasoning models (gpt-4o*) keep passing temperature through.
These tests pin that split so a future model swap can't silently regress into
400s on the learner's critical path.
"""

from __future__ import annotations

import pytest

from app.ai.llm.openai_client import OpenAILLMClient, _is_reasoning_model


@pytest.mark.parametrize(
    "model,expected",
    [
        ("gpt-5", True),
        ("gpt-5-mini", True),
        ("gpt-5-nano", True),
        ("o1", True),
        ("o3-mini", True),
        ("o4-mini", True),
        ("gpt-4o-mini", False),
        ("gpt-4o", False),
        ("gpt-4.1", False),
    ],
)
def test_is_reasoning_model(model: str, expected: bool) -> None:
    assert _is_reasoning_model(model) is expected


def test_reasoning_model_omits_temperature_and_sets_effort() -> None:
    client = OpenAILLMClient(model="gpt-5", reasoning_effort="medium")
    assert client._is_reasoning is True
    # No temperature reaches the API; reasoning_effort carries the knob instead.
    assert client._chat.temperature is None
    assert client._chat.reasoning_effort == "medium"


def test_reasoning_model_ignores_per_call_temperature_override() -> None:
    # Evaluator/feedback/task-gen pass per-call temps (0.2/0.4/0.7). For a
    # reasoning model the rebind must be a no-op (same instance), not a new
    # ChatOpenAI that would 400 on the custom temperature.
    client = OpenAILLMClient(model="gpt-5", reasoning_effort="medium")
    assert client._maybe_rebind_temperature(0.0) is client._chat
    assert client._maybe_rebind_temperature(0.7) is client._chat


def test_non_reasoning_model_still_honours_temperature() -> None:
    client = OpenAILLMClient(model="gpt-4o-mini", temperature=0.7)
    assert client._is_reasoning is False
    assert client._chat.temperature == 0.7
    # reasoning_effort is never sent for non-reasoning models.
    assert client._reasoning_effort is None
    assert client._chat.reasoning_effort is None
    # A per-call override builds a fresh instance at the requested temperature.
    rebound = client._maybe_rebind_temperature(0.2)
    assert rebound is not client._chat
    assert rebound.temperature == 0.2
