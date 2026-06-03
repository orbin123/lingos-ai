"""Tests for listen-retell / listen-shadow payload normalization."""

from __future__ import annotations

from app.modules.sessions.contracts.projection import project_task_payload
from app.modules.sessions.task_generator import (
    is_valid_listening_payload,
    normalize_listen_retell_payload,
)


def test_normalize_listen_retell_fills_passage_and_samples_from_aliases() -> None:
    content = {
        "archetype_id": "LISTEN_RETELL",
        "audio_script": "In the park there is a fountain next to a bakery.",
        "sample_response": "There is a fountain in the park beside a bakery.",
        "speaking_prompt": "Retell the main ideas.",
    }
    normalized = normalize_listen_retell_payload(content)

    assert normalized["inner_widget"] == "speak_and_record"
    assert normalized["speaking_prompts"] == ["Retell the main ideas."]
    assert normalized["sample_responses"] == [
        "There is a fountain in the park beside a bakery.",
    ]
    assert normalized["passage_to_retell"] == (
        "There is a fountain in the park beside a bakery."
    )
    assert is_valid_listening_payload(normalized)


def test_normalize_listen_retell_passage_from_primary_text_when_not_audio() -> None:
    content = {
        "archetype_id": "LISTEN_RETELL",
        "audio_script": "Short monologue about travel.",
        "primary_text": "The traveler described a park with a fountain.",
    }
    normalized = normalize_listen_retell_payload(content)

    assert normalized["passage_to_retell"] == "The traveler described a park with a fountain."
    assert normalized["sample_responses"] == ["The traveler described a park with a fountain."]


def test_normalize_listen_retell_default_prompt_when_missing() -> None:
    content = {
        "archetype_id": "LISTEN_RETELL",
        "audio_script": "A story about a city park.",
        "passage_to_retell": "A park has a fountain.",
    }
    normalized = normalize_listen_retell_payload(content)

    assert normalized["speaking_prompts"] == ["Retell what you heard in your own words."]


def test_normalize_listen_shadow_sets_text_to_shadow() -> None:
    content = {
        "archetype_id": "LISTEN_SHADOW",
        "audio_script": "She walked quickly to the station.",
    }
    normalized = normalize_listen_retell_payload(content)

    assert normalized["inner_widget"] == "speak_and_record"
    assert normalized["text_to_shadow"] == "She walked quickly to the station."
    assert is_valid_listening_payload(normalized)


def test_project_listen_retell_carries_model_answer_fields() -> None:
    content = normalize_listen_retell_payload({
        "archetype_id": "LISTEN_RETELL",
        "topic": "Prepositions",
        "instructions": "Listen and retell.",
        "audio_script": "At the center of town there is a park.",
        "passage_to_retell": "In the center of town there is a park.",
        "sample_responses": ["In the center of town there is a park."],
        "speaking_prompts": ["Retell what you heard in your own words."],
        "grammar_rule_to_practice": "Use prepositions of place.",
        "target_words": ["in", "next to"],
    })
    payload = project_task_payload(
        "LISTEN_RETELL", content, activity_id="act-1", sequence=2
    )

    assert payload["passage_to_retell"] == "In the center of town there is a park."
    assert payload["sample_responses"] == ["In the center of town there is a park."]
    assert payload["task_widget"] == "listen_retell"


def test_adapter_field_resolution_mirror() -> None:
    """Mirrors frontend ``resolveListenRetellModelAnswer`` fallback order."""

    def resolve(payload: dict) -> str:
        audio_script = str(payload.get("audio_script") or "").strip()
        samples = payload.get("sample_responses") or payload.get("sample_answers") or []
        if not isinstance(samples, list):
            samples = []
        samples = [str(s).strip() for s in samples if str(s).strip()]
        fallback = str(payload.get("sample_response") or "").strip()
        all_samples = samples if samples else ([fallback] if fallback else [])
        passage = str(payload.get("passage_to_retell") or "").strip()
        read_aloud = str(payload.get("text_to_read_aloud") or "").strip()
        distinct = read_aloud if read_aloud and read_aloud != audio_script else ""
        return passage or (all_samples[0] if all_samples else "") or distinct

    assert (
        resolve({"passage_to_retell": "Model retell.", "audio_script": "Audio."})
        == "Model retell."
    )
    assert (
        resolve({"sample_response": "From alias.", "audio_script": "Audio."})
        == "From alias."
    )
    assert (
        resolve({
            "text_to_read_aloud": "Distinct summary.",
            "audio_script": "Longer audio monologue.",
        })
        == "Distinct summary."
    )
    assert resolve({"audio_script": "Only audio."}) == ""
