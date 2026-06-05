"""Task-content validation across all 34 archetypes."""

from __future__ import annotations

import pytest

from app.modules.sessions.contracts import (
    ARCHETYPE_CONTRACTS,
    ErrorCorrectionPayload,
    FillBlanksPayload,
    McqPayload,
    OpenTextPayload,
    SpeakingPayload,
    TfngPayload,
    TransformPayload,
    get_contract,
)
from app.modules.sessions.task_generator import is_valid_task_content
from app.scoring import get_archetype

THE_34 = frozenset(ARCHETYPE_CONTRACTS)


def _base(archetype_id: str) -> dict:
    spec = get_archetype(archetype_id)
    return {
        "phase": "live",
        "archetype_id": archetype_id,
        "ui_widget": spec.ui_widget,
        "widget": spec.ui_widget,
        "core_activity": spec.core_activity,
        "topic": "Sample topic",
        "instructions": "Follow the instructions.",
        "task_intro": "Complete the task.",
    }


def _valid_mcq_items() -> list[dict]:
    return [
        {
            "item_id": "q1",
            "prompt": "When does Maria wake up?",
            "options": ["Six", "Seven", "Eight"],
            "correct_index": 1,
            "explanation": "She wakes at seven.",
        }
    ]


def _valid_tone_items() -> list[dict]:
    return [
        {
            "item_id": "t1",
            "message": "I am absolutely thrilled about this result.",
            "prompt": "What is the writer's tone?",
            "options": ["Angry", "Excited", "Bored"],
            "correct_index": 1,
            "explanation": "Thrilled signals excitement.",
        }
    ]


def _valid_open_text_items() -> list[dict]:
    return [
        {
            "item_id": "o1",
            "prompt": "Describe your morning.",
            "sample_answer": "I usually wake up at seven.",
            "answer_hints": ["Use a frequency adverb."],
        }
    ]


def _valid_speaking_prompts() -> dict:
    return {
        "speaking_prompts": ["Describe your daily routine."],
        "sample_responses": ["I wake up at seven and drink coffee."],
        "speaking_duration_seconds": 45,
    }


def _valid_content_for(archetype_id: str) -> dict:
    content = _base(archetype_id)
    spec = get_archetype(archetype_id)
    payload_cls = get_contract(archetype_id).task_payload

    if spec.core_activity == "listen":
        content.update({
            "widget": "listen_and_respond",
            "audio_script": "Maria wakes up at seven every morning.",
            "audio_url": "/audio/sample.mp3",
            "audio_duration_seconds": 8,
        })
        if archetype_id == "LISTEN_CLOZE":
            content.update({
                "inner_widget": "fill_in_blanks",
                "passage": "Maria ___ up at seven.",
                "items": [
                    {
                        "item_id": "b1",
                        "sentence_with_blank": "Maria ___ up at seven.",
                        "correct_answer": "wakes",
                        "explanation": "Third person -s.",
                    }
                ],
            })
        elif archetype_id == "LISTEN_DICTATION":
            content.update({
                "inner_widget": "open_text",
                "items": [
                    {
                        "item_id": "d1",
                        "prompt": "Type sentence 1.",
                        "correct_answer": "Maria wakes up at seven every morning.",
                        "explanation": "Listen for the full sentence.",
                    }
                ],
            })
        elif archetype_id in {"LISTEN_RETELL", "LISTEN_SHADOW"}:
            content.update({
                "inner_widget": "speak_and_record",
                "text_to_shadow": "Maria wakes up at seven every morning.",
                "speaking_prompts": ["Retell what you heard in your own words."],
                "sample_responses": ["Maria wakes up at seven every morning."],
                "speaking_duration_seconds": 45,
            })
        else:
            content.update({
                "inner_widget": "mcq",
                "items": _valid_mcq_items(),
            })
        return content

    if archetype_id == "READ_TONE_ID":
        content.update({"items": _valid_tone_items()})
        return content

    if archetype_id == "READ_STRUCTURE_ID":
        content.update({
            "widget": "read_structure",
            "structure_labels": ["Intro", "Body", "Conclusion"],
            "items": [
                {
                    "item_id": "p1",
                    "paragraph": "Every morning I follow the same routine.",
                    "correct_answer": "Intro",
                    "explanation": "It introduces the topic.",
                }
            ],
        })
        return content

    if archetype_id == "READ_ERROR_SPOT":
        content.update({
            "widget": "error_spotting",
            "passage_sentences": [
                {
                    "sentence_id": "s1",
                    "tokens": [
                        {"token_id": "s1_t1", "text": "Yesterday", "is_error": False},
                        {"token_id": "s1_t2", "text": "I", "is_error": False},
                        {"token_id": "s1_t3", "text": "goed", "is_error": True},
                    ],
                    "error": {
                        "token_id": "s1_t3",
                        "incorrect_phrase": "goed",
                        "correction": "went",
                        "error_type": "irregular_past",
                        "rule": "Use went.",
                        "explanation": "Irregular past.",
                    },
                },
                {
                    "sentence_id": "s2",
                    "tokens": [
                        {"token_id": "s2_t1", "text": "She", "is_error": False},
                        {"token_id": "s2_t2", "text": "did", "is_error": False},
                        {"token_id": "s2_t3", "text": "finished", "is_error": True},
                    ],
                    "error": {
                        "token_id": "s2_t3",
                        "incorrect_phrase": "finished",
                        "correction": "finish",
                        "error_type": "missing_past_auxiliary",
                        "rule": "Use base verb after did.",
                        "explanation": "Did carries past.",
                    },
                },
                {
                    "sentence_id": "s3",
                    "tokens": [
                        {"token_id": "s3_t1", "text": "The", "is_error": False},
                        {"token_id": "s3_t2", "text": "manager", "is_error": False},
                        {"token_id": "s3_t3", "text": "was", "is_error": False},
                        {"token_id": "s3_t4", "text": "hire", "is_error": True},
                    ],
                    "error": {
                        "token_id": "s3_t4",
                        "incorrect_phrase": "hire",
                        "correction": "hired",
                        "error_type": "passive_helper_missing",
                        "rule": "Passive needs participle.",
                        "explanation": "Use hired.",
                    },
                },
                {
                    "sentence_id": "s4",
                    "tokens": [
                        {"token_id": "s4_t1", "text": "Last", "is_error": False},
                        {"token_id": "s4_t2", "text": "week", "is_error": False},
                        {"token_id": "s4_t3", "text": "we", "is_error": False},
                        {"token_id": "s4_t4", "text": "visit", "is_error": True},
                    ],
                    "error": {
                        "token_id": "s4_t4",
                        "incorrect_phrase": "visit",
                        "correction": "visited",
                        "error_type": "time_marker_mismatch",
                        "rule": "Past marker needs past verb.",
                        "explanation": "Use visited.",
                    },
                },
                {
                    "sentence_id": "s5",
                    "tokens": [
                        {"token_id": "s5_t1", "text": "They", "is_error": False},
                        {"token_id": "s5_t2", "text": "had", "is_error": False},
                        {"token_id": "s5_t3", "text": "good", "is_error": False},
                        {"token_id": "s5_t4", "text": "advices", "is_error": True},
                    ],
                    "error": {
                        "token_id": "s5_t4",
                        "incorrect_phrase": "advices",
                        "correction": "advice",
                        "error_type": "object_or_complement_mismatch",
                        "rule": "Advice is uncountable.",
                        "explanation": "No plural advice.",
                    },
                },
            ],
            "total_errors": 5,
        })
        return content

    if archetype_id == "SPEAK_READ_ALOUD":
        content.update({
            "text_to_read_aloud": (
                "Last Saturday, Maria visited her grandparents in the countryside. "
                "They played cards and talked about school. She ate homemade soup, "
                "watched an old film, and laughed with her cousins. Maria enjoyed "
                "the quiet evening and went home feeling happy. She told her parents "
                "about the trip before she fell asleep."
            ),
        })
        return content

    if archetype_id == "SPEAK_PIC_DESC":
        content.update({
            **_valid_speaking_prompts(),
            "image_alt": "A person reading in a park",
            "image_url": "/images/sample.png",
        })
        return content

    if archetype_id == "SPEAK_INTERVIEW":
        content.update({
            "questions": [
                {
                    "item_id": "q1",
                    "interviewer_prompt": "What is your name?",
                    "sample_answer": "My name is Sam.",
                    "answer_hint": "Start with 'My name is'.",
                },
                {
                    "item_id": "q2",
                    "interviewer_prompt": "What do you do?",
                    "sample_answer": "I'm a teacher.",
                    "answer_hint": "Start with 'I'm a'.",
                },
            ],
        })
        return content

    if archetype_id in {"SPEAK_ROLEPLAY", "SPEAK_SMALLTALK", "SPEAK_DEBATE"}:
        content.update({
            **_valid_speaking_prompts(),
            "dialogue_context": [
                {
                    "role": "Partner",
                    "text": (
                        "Hi there, welcome back to the office. "
                        "How was your weekend with your family?"
                    ),
                    "speaker": "partner",
                },
                {
                    "role": "You",
                    "text": "It was really nice, thanks for asking about it.",
                    "speaker": "learner",
                },
            ],
        })
        return content

    if payload_cls is McqPayload:
        content.update({"widget": "mcq", "items": _valid_mcq_items()})
        return content

    if payload_cls is TfngPayload:
        content.update({
            "widget": "true_false_not_given",
            "passage": "Cats are mammals.",
            "items": [
                {
                    "item_id": "t1",
                    "prompt": "Cats are mammals.",
                    "correct_answer": "True",
                    "explanation": "Stated directly.",
                }
            ],
        })
        return content

    if payload_cls is FillBlanksPayload:
        content.update({
            "widget": "fill_in_blanks",
            "passage": "Maria ___ up at seven.",
            "items": [
                {
                    "item_id": "b1",
                    "sentence_with_blank": "Maria ___ up at seven.",
                    "correct_answer": "wakes",
                    "explanation": "Third person -s.",
                }
            ],
        })
        return content

    if payload_cls is OpenTextPayload:
        items = _valid_open_text_items()
        if archetype_id == "WRITE_OPEN_SENT":
            items = items * 3
            for index, item in enumerate(items, start=1):
                item["item_id"] = f"o{index}"
        content.update({"widget": "open_text", "items": items})
        return content

    if payload_cls is TransformPayload:
        content.update({
            "widget": "sentence_transform",
            "items": [
                {
                    "item_id": "tr1",
                    "source_sentence": "The cat was chased by the dog.",
                    "sample_answer": "The dog chased the cat.",
                    "watch_hints": ["Move the object to subject."],
                }
            ]
            * 3,
        })
        return content

    if payload_cls is ErrorCorrectionPayload:
        content.update({
            "widget": "error_correction",
            "items": [
                {
                    "item_id": "e1",
                    "incorrect_sentence": "She walk to work.",
                    "sample_answer": "She walks to work.",
                    "watch_hints": ["Third person -s."],
                }
            ]
            * (3 if archetype_id == "WRITE_ERROR_CORR" else 1),
        })
        return content

    if payload_cls is SpeakingPayload:
        content.update({
            **_valid_speaking_prompts(),
            "widget": "speak_and_record",
            "speaking_duration_seconds": 45,
        })
        return content

    raise AssertionError(f"no valid fixture builder for {archetype_id}")


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
