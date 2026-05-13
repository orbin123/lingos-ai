"""Tests for task_delivery_node + followup_node plan-aware behavior."""

from __future__ import annotations

import asyncio

import pytest

from app.ai.graphs import nodes as nodes_module
from app.ai.graphs.nodes import (
    _find_plan_activity,
    followup_node,
    task_delivery_node,
)


VOCAB_PLAN = {
    "topic_name": "Everyday Words — Family & Home",
    "sub_skill": "vocabulary",
    "sub_level": 1,
    "teacher_instructions": {"learning_goal": "Teach family/home words."},
    "activities": [
        {
            "order": 1,
            "activity": "read",
            "template_id": "full_vocabulary_read_v1",
            "widget": "mcq",
            "evaluation_method": "rule_based",
            "evaluation_focus": {"focus_areas": ["meaning recognition"]},
        },
        {
            "order": 2,
            "activity": "write",
            "template_id": "full_vocabulary_write_v1",
            "widget": "open_text",
            "evaluation_method": "ai_based",
            "evaluation_focus": {"focus_areas": ["target word usage"]},
        },
        {
            "order": 3,
            "activity": "listen",
            "template_id": "full_vocabulary_listen_v1",
            "widget": "listen_and_respond",
            "evaluation_method": "rule_based",
            "evaluation_focus": {"focus_areas": ["audio comprehension"]},
        },
        {
            "order": 4,
            "activity": "speak",
            "template_id": "full_vocabulary_speak_v1",
            "widget": "speak_and_record",
            "evaluation_method": "ai_based",
            "evaluation_focus": {"focus_areas": ["pronunciation"]},
        },
    ],
}


class _StubGenerator:
    """Stand-in for TaskGeneratorAgent that records which template was used."""

    instances: list["_StubGenerator"] = []

    def __init__(self):
        self.calls: list[str] = []
        _StubGenerator.instances.append(self)

    async def generate(self, template, profile):
        self.calls.append(template.template_id)
        return {
            "widget": {
                "full_vocabulary_read_v1": "mcq",
                "full_vocabulary_write_v1": "open_text",
            }.get(template.template_id, "open_text"),
            "task_intro": "intro",
            "estimated_time_minutes": 3,
            "_used_template_id": template.template_id,
        }


@pytest.fixture(autouse=True)
def _reset_stub_generator():
    _StubGenerator.instances.clear()
    yield
    _StubGenerator.instances.clear()


@pytest.fixture()
def patch_generator(monkeypatch):
    monkeypatch.setattr(nodes_module, "TaskGeneratorAgent", _StubGenerator)
    return _StubGenerator


def _ui_event(update):
    return next(e for e in update["outgoing_events"] if e["type"] == "ui_event")


def test_find_plan_activity_returns_correct_order() -> None:
    state = {"daily_plan": VOCAB_PLAN, "current_activity_order": 2}
    activity = _find_plan_activity(state)
    assert activity is not None
    assert activity["template_id"] == "full_vocabulary_write_v1"


def test_find_plan_activity_returns_none_when_no_plan() -> None:
    assert _find_plan_activity({}) is None
    assert _find_plan_activity({"daily_plan": {}}) is None


def test_task_delivery_uses_plan_template_for_activity_1(patch_generator) -> None:
    state = {
        "daily_plan": VOCAB_PLAN,
        "current_activity_order": 1,
        "task_content": None,
        "task_queue": [{"sequence_index": 0}],
        "current_task_index": 0,
        "learner_profile": {},
        "messages": [],
    }
    update = asyncio.run(task_delivery_node(state))

    assert _StubGenerator.instances[0].calls == ["full_vocabulary_read_v1"]
    assert update["task_content"]["_used_template_id"] == "full_vocabulary_read_v1"

    ui = _ui_event(update)
    assert ui["widget"] == "mcq"


def test_task_delivery_uses_plan_template_for_activity_2(patch_generator) -> None:
    state = {
        "daily_plan": VOCAB_PLAN,
        "current_activity_order": 2,
        "task_content": None,
        "task_queue": [{"sequence_index": 0}],
        "current_task_index": 0,
        "learner_profile": {},
        "messages": [],
    }
    update = asyncio.run(task_delivery_node(state))

    assert _StubGenerator.instances[0].calls == ["full_vocabulary_write_v1"]
    ui = _ui_event(update)
    assert ui["widget"] == "open_text"
    assert update["task_content"]["_used_template_id"] == "full_vocabulary_write_v1"


def test_task_delivery_skips_generation_when_content_already_present(
    patch_generator,
) -> None:
    pre_generated = {"widget": "mcq", "items": [], "task_intro": "x", "estimated_time_minutes": 3}
    state = {
        "daily_plan": VOCAB_PLAN,
        "current_activity_order": 1,
        "task_content": pre_generated,
        "task_queue": [{"sequence_index": 0}],
        "current_task_index": 0,
        "learner_profile": {},
        "messages": [],
    }
    update = asyncio.run(task_delivery_node(state))

    # No generator instance should be created at all.
    assert _StubGenerator.instances == []
    ui = _ui_event(update)
    assert ui["widget"] == "mcq"
    assert ui["payload"]["items"] == []


def test_task_delivery_legacy_path_without_plan() -> None:
    state = {
        "task_content": {"widget": "fill_in_blanks", "items": []},
        "task_type": "fill_in_blanks",
        "task_queue": [],
        "current_task_index": 0,
        "messages": [],
    }
    update = asyncio.run(task_delivery_node(state))
    ui = _ui_event(update)
    assert ui["widget"] == "fill_in_blanks"


def test_followup_advances_activity_order_on_next_activity() -> None:
    state = {
        "daily_plan": VOCAB_PLAN,
        "current_activity_order": 1,
        "messages": [{"role": "user", "content": "Next activity"}],
    }
    update = asyncio.run(followup_node(state))
    assert update["current_activity_order"] == 2
    assert update["task_content"] is None
    assert update["phase"] == "teaching"


def test_followup_ends_session_after_last_activity() -> None:
    state = {
        "daily_plan": VOCAB_PLAN,
        "current_activity_order": 4,
        "messages": [{"role": "user", "content": "Next activity"}],
    }
    update = asyncio.run(followup_node(state))
    assert update["phase"] == "ended"
    # No activity-order increment when the day is finished.
    assert "current_activity_order" not in update
