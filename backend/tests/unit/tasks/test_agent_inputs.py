"""Agent input boundary contracts + strict-mode enforcement (Layer 2).

Covers the service→agent input models (``agent_inputs.py``), the
``build_agent_input`` strict/non-strict helper, and that ``strict_contracts``
makes the delivery-time task projection (``_apply_task_contract``) fail loudly
instead of falling back to legacy content.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.modules.sessions.contracts.agent_inputs import (
    EvaluatorAgentInput,
    FeedbackAgentInput,
    TaskGenAgentInput,
    TeacherAgentInput,
    build_agent_input,
)


# ── Model shape ─────────────────────────────────────────────────────


def test_teacher_input_requires_topic_and_forbids_extras() -> None:
    ok = TeacherAgentInput(topic="Simple present", scripted_plan=("a", "b"))
    assert ok.topic == "Simple present"
    assert ok.lesson_description == ""  # defaulted

    with pytest.raises(ValidationError):
        TeacherAgentInput()  # missing required topic

    with pytest.raises(ValidationError):
        TeacherAgentInput(topic="x", unexpected_key="boom")  # extra="forbid"


def test_task_gen_input_requires_core_context() -> None:
    ok = TaskGenAgentInput(
        archetype_id="READ_CLOZE",
        day_topic="Routines",
        explanation_brief="brief",
        cefr_level="A1",
        sub_level=1,
    )
    assert ok.task_spec == {}  # defaulted

    with pytest.raises(ValidationError):
        TaskGenAgentInput(archetype_id="READ_CLOZE")  # missing day_topic/brief/cefr


def test_evaluator_and_feedback_inputs_default_dicts() -> None:
    ev = EvaluatorAgentInput(archetype_id="READ_CLOZE")
    assert ev.task_content == {} and ev.user_response == {}

    fb = FeedbackAgentInput(archetype_id="READ_CLOZE")
    assert fb.evaluation == {}

    with pytest.raises(ValidationError):
        EvaluatorAgentInput(archetype_id="READ_CLOZE", user_response="not-a-dict")


# ── build_agent_input strict / non-strict ───────────────────────────


def test_build_agent_input_returns_model_on_valid() -> None:
    model = build_agent_input(TeacherAgentInput, strict=True, topic="Past tense")
    assert isinstance(model, TeacherAgentInput)
    assert model.topic == "Past tense"


def test_build_agent_input_returns_none_when_lenient_and_invalid() -> None:
    assert build_agent_input(TeacherAgentInput, strict=False) is None


def test_build_agent_input_raises_when_strict_and_invalid() -> None:
    with pytest.raises(ValidationError):
        build_agent_input(TeacherAgentInput, strict=True)


# ── strict_contracts gates the delivery-time task projection ─────────


def _malformed_attempt() -> SimpleNamespace:
    # READ_CLOZE is contract-enabled; empty items fails FillBlanksPayload
    # (min_length=1), so projection raises ContractValidationError.
    return SimpleNamespace(
        id=1,
        archetype_id="READ_CLOZE",
        sequence=1,
        task_content={"items": []},
    )


def test_apply_task_contract_raises_under_strict(monkeypatch) -> None:
    from app.modules.learning_session import service as ls
    from app.modules.sessions.contracts import ContractValidationError

    monkeypatch.setattr(ls.settings, "strict_contracts", True)
    with pytest.raises(ContractValidationError):
        # self is unused on the failure path — pass a placeholder.
        ls.LearningSessionService._apply_task_contract(
            SimpleNamespace(), _malformed_attempt()
        )


def test_apply_task_contract_falls_back_when_not_strict(monkeypatch) -> None:
    from app.modules.learning_session import service as ls

    monkeypatch.setattr(ls.settings, "strict_contracts", False)
    # Logs a warning and returns without raising; content is left unchanged.
    attempt = _malformed_attempt()
    result = ls.LearningSessionService._apply_task_contract(SimpleNamespace(), attempt)
    assert result is None
    assert attempt.task_content == {"items": []}
