"""Roleplay/smalltalk dialogue speaking payload normalization."""

from app.modules.sessions.task_generator import (
    is_valid_dialogue_speaking_payload,
    normalize_dialogue_speaking_payload,
)


def _rich_roleplay_payload() -> dict:
    return {
        "archetype_id": "SPEAK_ROLEPLAY",
        "task_intro": "Act out your role in the conversation.",
        "instructions": "Respond to your partner using possessive and object pronouns.",
        "grammar_rule_to_practice": "Use possessive pronouns like mine and object pronouns like him.",
        "target_words": ["mine", "yours", "she", "him", "he"],
        "speaking_duration_seconds": 45,
        "dialogue_context": [
            {
                "role": "Partner",
                "text": (
                    "Hi! I found a blue notebook on the desk near the window. "
                    "It has a name written inside. Do you know who it belongs to?"
                ),
                "speaker": "partner",
            },
            {
                "role": "You",
                "text": (
                    "No, it is not mine. I think it belongs to Emily. "
                    "She lent it to him yesterday, but he forgot to bring it back."
                ),
                "speaker": "learner",
            },
        ],
        "speaking_prompts": [
            "Tell your partner whether the notebook is yours and explain who it belongs to."
        ],
        "sample_responses": [
            (
                "No, it is not mine. I think it belongs to Emily. "
                "She lent it to him yesterday, but he forgot to bring it back."
            )
        ],
    }


def test_valid_dialogue_payload_passes_validation() -> None:
    payload = normalize_dialogue_speaking_payload(_rich_roleplay_payload())
    assert is_valid_dialogue_speaking_payload(payload)


def test_short_one_liner_roleplay_payload_fails_validation() -> None:
    payload = normalize_dialogue_speaking_payload(
        {
            "archetype_id": "SPEAK_ROLEPLAY",
            "task_intro": "Act out your role.",
            "instructions": "Use pronouns.",
            "dialogue_context": [
                {
                    "role": "Partner",
                    "text": "Is this book yours?",
                    "speaker": "partner",
                },
                {
                    "role": "You",
                    "text": "Yes, it is mine.",
                    "speaker": "learner",
                },
            ],
            "speaking_prompts": ["Answer using a possessive pronoun."],
            "sample_responses": ["Yes, it is mine."],
        }
    )
    assert not is_valid_dialogue_speaking_payload(payload)


def test_normalize_derives_prompt_and_sample_from_dialogue() -> None:
    normalized = normalize_dialogue_speaking_payload(
        {
            "archetype_id": "SPEAK_ROLEPLAY",
            "task_intro": "Act out your role in the conversation.",
            "instructions": "Respond with pronouns.",
            "dialogue_context": _rich_roleplay_payload()["dialogue_context"],
        }
    )

    assert normalized["speaking_prompts"] == [
        "Respond to your partner in 2-3 connected sentences using the target pronouns."
    ]
    assert normalized["sample_responses"] == [
        (
            "No, it is not mine. I think it belongs to Emily. "
            "She lent it to him yesterday, but he forgot to bring it back."
        )
    ]
    assert normalized["speaking_duration_seconds"] == 45
