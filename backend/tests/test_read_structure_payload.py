"""Tests for read-structure (paragraph labelling) payload normalization.

Regression: the generic task-gen schema can only emit READ_STRUCTURE items in
an MCQ-ish shape (``prompt`` = paragraph, ``options`` = labels, ``correct_index``
/ ``correct_answer`` = right label) with no ``paragraph`` field and no top-level
``structure_labels``. Without a normalize/validate branch that content was judged
valid and served, so the widget rendered blank paragraphs with no label options.
"""

from __future__ import annotations

import pytest

from app.modules.sessions.contracts.projection import project_task_payload
from app.modules.sessions.task_generator import (
    StubTaskGenerator,
    is_valid_read_structure_payload,
    normalize_read_structure_payload,
)
from app.scoring import get_archetype


def _mcq_shaped_content() -> dict:
    """The shape the live LLM generator actually persisted (see DB row)."""
    return {
        "widget": "read_structure",
        "archetype_id": "READ_STRUCTURE_ID",
        "passage_title": "My Morning Routine",
        "items": [
            {
                "item_id": "1",
                "prompt": "Every morning, I have a routine that helps me start my day.",
                "options": ["Intro", "Body", "Conclusion"],
                "correct_index": 0,
                "correct_answer": "Intro",
                "explanation": "It introduces the main idea.",
            },
            {
                "item_id": "2",
                "prompt": "First, I brush my teeth. Then, I take a shower.",
                "options": ["Intro", "Body", "Conclusion"],
                "correct_index": 1,
                "correct_answer": "Body",
                "explanation": "Ordered details with sequence words.",
            },
            {
                "item_id": "3",
                "prompt": "In conclusion, my routine helps me prepare for the day.",
                "options": ["Intro", "Body", "Conclusion"],
                "correct_index": 2,
                "correct_answer": "Conclusion",
                "explanation": "A closing thought.",
            },
        ],
    }


def test_mcq_shaped_content_is_invalid_before_normalization() -> None:
    raw = _mcq_shaped_content()
    # No top-level structure_labels and no items[].paragraph -> not renderable.
    assert raw.get("structure_labels") is None
    assert is_valid_read_structure_payload(raw) is False


def test_normalize_remaps_prompt_and_options_into_structure_shape() -> None:
    normalized = normalize_read_structure_payload(_mcq_shaped_content())

    assert normalized["structure_labels"] == ["Intro", "Body", "Conclusion"]
    assert [item["correct_answer"] for item in normalized["items"]] == [
        "Intro",
        "Body",
        "Conclusion",
    ]
    assert all(item["paragraph"].strip() for item in normalized["items"])
    assert is_valid_read_structure_payload(normalized)


def test_normalize_derives_correct_answer_from_correct_index() -> None:
    content = _mcq_shaped_content()
    for item in content["items"]:
        item.pop("correct_answer")  # only correct_index remains
    normalized = normalize_read_structure_payload(content)
    assert [item["correct_answer"] for item in normalized["items"]] == [
        "Intro",
        "Body",
        "Conclusion",
    ]
    assert is_valid_read_structure_payload(normalized)


def test_normalized_payload_projects_onto_contract() -> None:
    normalized = normalize_read_structure_payload(_mcq_shaped_content())
    payload = project_task_payload(
        "READ_STRUCTURE_ID", normalized, activity_id="a", sequence=1
    )
    assert payload["task_widget"] == "read_structure"
    assert payload["structure_labels"] == ["Intro", "Body", "Conclusion"]
    assert [item["paragraph"] for item in payload["items"]] == [
        item["paragraph"] for item in normalized["items"]
    ]


@pytest.mark.asyncio
async def test_stub_generator_produces_renderable_read_structure() -> None:
    archetype = get_archetype("READ_STRUCTURE_ID")
    generated = await StubTaskGenerator().generate(
        archetype=archetype,
        day_topic="Daily routines",
        explanation_brief="",
        cefr_level="B1",
        sub_level=1,
    )
    assert is_valid_read_structure_payload(generated.content)
    project_task_payload(
        "READ_STRUCTURE_ID", generated.content, activity_id="a", sequence=1
    )
