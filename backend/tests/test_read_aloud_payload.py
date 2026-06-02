"""Read-aloud task content normalization and contract projection."""

import pytest

from app.ai.sessions.llm_task_generator import LLMTaskGenerator, TaskGenOutput
from app.modules.sessions.contracts import project_task_payload
from app.modules.sessions.task_generator import (
    is_valid_read_aloud_payload,
    normalize_read_aloud_payload,
)
from app.scoring import get_archetype
from tests.test_llm_session_agents import FakeLLMClient


_PAST_PASSAGE = (
    "Last Saturday, Maria visited her grandparents in the countryside. "
    "They played cards and talked about school. She ate homemade soup, "
    "watched an old film, and laughed with her cousins. Maria enjoyed "
    "the quiet evening and went home feeling happy. She told her parents "
    "about the trip before she fell asleep."
)


def test_normalize_read_aloud_maps_primary_text() -> None:
    normalized = normalize_read_aloud_payload(
        {"primary_text": _PAST_PASSAGE, "speaking_duration_seconds": 45}
    )
    assert normalized["text_to_read_aloud"] == _PAST_PASSAGE
    assert is_valid_read_aloud_payload(normalized)


def test_project_read_aloud_from_primary_text() -> None:
    payload = project_task_payload(
        "SPEAK_READ_ALOUD",
        {
            "topic": "Past simple read aloud",
            "task_intro": "Read the passage above out loud.",
            "instructions": "Read the connected passage aloud clearly.",
            "primary_text": _PAST_PASSAGE,
            "target_words": ["visited", "played"],
            "grammar_rule_to_practice": "Use simple past for completed actions.",
            "speaking_duration_seconds": 45,
        },
        activity_id="act-1",
        sequence=4,
    )
    assert payload["text_to_read_aloud"] == _PAST_PASSAGE
    assert payload["task_widget"] == "read_aloud"


@pytest.mark.asyncio
async def test_llm_read_aloud_output_projects_with_text_field() -> None:
    spec = get_archetype("SPEAK_READ_ALOUD")
    canned = TaskGenOutput(
        topic="Past simple weekend story",
        instructions="Read the connected passage aloud clearly.",
        task_intro="Read the passage above out loud.",
        text_to_read_aloud=_PAST_PASSAGE,
        primary_text=_PAST_PASSAGE,
        grammar_rule_to_practice="Use simple past for completed actions.",
        target_words=["visited", "played", "talked", "ate", "watched"],
        speaking_duration_seconds=45,
    )
    agent = LLMTaskGenerator(FakeLLMClient([canned]))
    generated = await agent.generate(
        archetype=spec,
        day_topic="Simple past",
        explanation_brief="Practice past tense pronunciation.",
        cefr_level="A1",
        sub_level=1,
    )
    assert generated.content["text_to_read_aloud"] == _PAST_PASSAGE
    payload = project_task_payload(
        "SPEAK_READ_ALOUD",
        dict(generated.content),
        activity_id="attempt-1",
        sequence=4,
    )
    assert payload["text_to_read_aloud"] == _PAST_PASSAGE
