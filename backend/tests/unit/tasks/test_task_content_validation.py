"""Task-content validation across all 34 archetypes.

Representative valid payloads live in `tests/fixtures/task_content.py` (shared
with the contract-gate and LLM session-agent tests). This file keeps the
invalid-payload mutations and the assertions.
"""

from __future__ import annotations

import pytest

from app.modules.sessions.task_generator import is_valid_task_content
from app.scoring import get_archetype
from tests.fixtures.task_content import THE_34, _valid_content_for


def _invalid_content_for(archetype_id: str) -> dict:
    content = _valid_content_for(archetype_id)
    spec = get_archetype(archetype_id)

    if archetype_id == "READ_ERROR_SPOT":
        content["passage_sentences"] = []
    elif archetype_id == "SPEAK_READ_ALOUD":
        content["text_to_read_aloud"] = ""
        content["speaking_duration_seconds"] = 1
    elif archetype_id == "SPEAK_PIC_DESC":
        content["image_alt"] = ""
        content["image_url"] = ""
        content["speaking_duration_seconds"] = 1
    elif archetype_id == "SPEAK_INTERVIEW":
        content["questions"] = []
        content["speaking_duration_seconds"] = 1
    elif archetype_id in {"SPEAK_ROLEPLAY", "SPEAK_SMALLTALK", "SPEAK_DEBATE"}:
        content["dialogue_context"] = []
        content["speaking_duration_seconds"] = 1
    elif archetype_id in {"LISTEN_RETELL", "LISTEN_SHADOW"}:
        content["text_to_shadow"] = ""
        content["audio_script"] = ""
        content["audio_url"] = ""
        content["speaking_duration_seconds"] = 1
    elif spec.core_activity == "speak":
        content["speaking_duration_seconds"] = 1
    elif "items" in content:
        content["items"] = []
    else:
        content["items"] = []
    return content


@pytest.mark.parametrize("archetype_id", sorted(THE_34))
def test_valid_task_content_accepts_representative_payload(archetype_id: str) -> None:
    assert is_valid_task_content(archetype_id, _valid_content_for(archetype_id))


@pytest.mark.parametrize("archetype_id", sorted(THE_34))
def test_invalid_task_content_rejects_empty_render_fields(archetype_id: str) -> None:
    assert not is_valid_task_content(archetype_id, _invalid_content_for(archetype_id))


def test_live_phase_requires_render_fields() -> None:
    assert not is_valid_task_content(
        "READ_COMP_MCQ",
        {
            "phase": "live",
            "archetype_id": "READ_COMP_MCQ",
            "widget": "mcq",
            "ui_widget": "MCQList",
            "topic": "Sample topic",
            "instructions": "Answer the questions.",
            "items": [],
        },
    )


def test_registry_has_exactly_34_archetypes() -> None:
    assert len(THE_34) == 34
