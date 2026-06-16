"""Tests for listen-dictation payload normalization and validation."""

from __future__ import annotations

from app.modules.sessions.contracts.projection import project_task_payload
from app.modules.sessions.task_generator import (
    is_valid_dictation_payload,
    is_valid_listening_payload,
    normalize_dictation_payload,
)


def test_normalize_dictation_coerces_correct_answer_and_inner_widget() -> None:
    content = {
        "archetype_id": "LISTEN_DICTATION",
        "audio_script": "She walks to work. He reads the news.",
        "items": [
            {
                "item_id": "d1",
                "prompt": "Type sentence 1.",
                "correct_answer": "She walks to work.",
                "explanation": "Listen for the full sentence.",
            },
            {
                "prompt": "Type sentence 2.",
                "correct_answer": "He reads the news.",
                "explanation": "Listen for the full sentence.",
            },
        ],
    }
    normalized = normalize_dictation_payload(content)

    assert normalized["widget"] == "listen_and_respond"
    assert normalized["inner_widget"] == "open_text"
    assert normalized["items"][0]["sample_answer"] == "She walks to work."
    assert normalized["items"][1]["item_id"] == "d2"
    assert is_valid_dictation_payload(normalized)
    assert not is_valid_listening_payload(normalized)


def test_normalize_dictation_fills_answer_from_target_words() -> None:
    content = {
        "audio_script": "I am reading. They are studying.",
        "target_words": ["am reading", "are studying"],
        "items": [
            {
                "item_id": "d1",
                "prompt": "I ___ a book.",
                "explanation": "Present continuous with I.",
            },
            {
                "item_id": "d2",
                "prompt": "They ___ together.",
                "explanation": "Present continuous with they.",
            },
        ],
    }
    normalized = normalize_dictation_payload(content)

    assert normalized["items"][0]["correct_answer"] == "I am reading a book."
    assert normalized["items"][1]["correct_answer"] == "They are studying together."
    assert is_valid_dictation_payload(normalized)


def test_is_valid_dictation_rejects_missing_audio_and_empty_items() -> None:
    base = {
        "widget": "listen_and_respond",
        "inner_widget": "open_text",
        "items": [
            {
                "item_id": "d1",
                "prompt": "Type it.",
                "correct_answer": "Hello.",
                "explanation": "Full sentence.",
            }
        ],
    }
    assert not is_valid_dictation_payload({**base, "audio_script": ""})
    assert not is_valid_dictation_payload({**base, "items": []})
    assert not is_valid_dictation_payload(
        {
            **base,
            "items": [{"item_id": "d1", "prompt": "Type it.", "correct_answer": "Hi."}],
        }
    )


def test_normalize_dictation_replaces_answer_leaking_prompts_with_keywords() -> None:
    content = {
        "audio_script": (
            "I am eating breakfast right now. I usually eat cereal in the morning. "
            "She is taking a shower at the moment. They always go to school at 8 AM."
        ),
        "target_words": ["am eating", "usually eat", "is taking", "always go"],
        "items": [
            {
                "item_id": "d1",
                "prompt": "Write this sentence: I am eating breakfast right now.",
                "correct_answer": "I am eating breakfast right now.",
                "explanation": "Present continuous for now.",
            },
            {
                "item_id": "d2",
                "prompt": "Write this sentence: I usually eat cereal in the morning.",
                "correct_answer": "I usually eat cereal in the morning.",
                "explanation": "Simple present for habits.",
            },
            {
                "item_id": "d3",
                "prompt": "Sentence 3: take, shower",
                "correct_answer": "She is taking a shower at the moment.",
                "explanation": "Present continuous for now.",
            },
        ],
    }
    normalized = normalize_dictation_payload(content)

    assert normalized["items"][0]["prompt"] == "Write this sentence: eat, breakfast"
    assert (
        normalized["items"][0]["correct_answer"] == "I am eating breakfast right now."
    )
    assert (
        normalized["items"][1]["prompt"] == "Write this sentence: eat, cereal, morning"
    )
    assert normalized["items"][2]["prompt"] == "Sentence 3: take, shower"


def test_project_listen_dictation_after_normalize() -> None:
    content = normalize_dictation_payload(
        {
            "topic": "Dictation practice",
            "instructions": "Type what you hear.",
            "audio_script": "She walks to work.",
            "audio_duration_seconds": 8,
            "items": [
                {
                    "item_id": "d1",
                    "prompt": "Sentence 1",
                    "correct_answer": "She walks to work.",
                    "explanation": "Listen for -s.",
                }
            ],
        }
    )
    payload = project_task_payload(
        "LISTEN_DICTATION", content, activity_id="act-1", sequence=2
    )

    assert payload["task_widget"] == "listen_dictation"
    assert payload["items"][0]["correct_answer"] == "She walks to work."
