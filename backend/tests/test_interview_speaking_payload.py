"""SPEAK_INTERVIEW payload normalization + validation."""

from app.modules.sessions.task_generator import (
    is_valid_interview_speaking_payload,
    normalize_interview_speaking_payload,
)


def _rich_interview_payload() -> dict:
    return {
        "archetype_id": "SPEAK_INTERVIEW",
        "task_intro": "Answer the interview questions out loud.",
        "instructions": "Answer three simple questions in one short full sentence each.",
        "interview_context": "A friendly mini interview about yourself.",
        "grammar_rule_to_practice": "Use simple present sentences.",
        "target_words": ["My name is", "I'm a", "I like"],
        "speaking_duration_seconds": 30,
        "questions": [
            {
                "item_id": "q1",
                "interviewer_prompt": "What is your name?",
                "sample_answer": "My name is Sam.",
                "answer_hint": "Use 'My name is'.",
            },
            {
                "interviewer_prompt": "What do you do?",
                "sample_answer": "I'm a teacher.",
            },
            {
                "prompt": "What is your hobby?",
                "sample_answer": "I like reading books.",
            },
        ],
    }


def test_valid_interview_payload_passes_validation() -> None:
    payload = normalize_interview_speaking_payload(_rich_interview_payload())
    assert is_valid_interview_speaking_payload(payload, expected_questions=3)
    questions = payload["questions"]
    assert len(questions) == 3
    # item_id is synthesized when absent, `prompt` aliases `interviewer_prompt`.
    assert questions[0]["item_id"] == "q1"
    assert questions[1]["item_id"] == "item_2"
    assert questions[2]["interviewer_prompt"] == "What is your hobby?"
    assert payload["interview_context"] == "A friendly mini interview about yourself."
    assert payload["speaking_duration_seconds"] == 30


def test_interview_payload_without_questions_fails_validation() -> None:
    payload = normalize_interview_speaking_payload(
        {
            "archetype_id": "SPEAK_INTERVIEW",
            "instructions": "Answer the questions.",
            "questions": [],
        }
    )
    assert payload["questions"] == []
    assert payload["interview_context"] == ""
    # default duration applied
    assert payload["speaking_duration_seconds"] == 30
    assert not is_valid_interview_speaking_payload(payload)


def test_interview_payload_drops_questions_missing_sample_answer() -> None:
    payload = normalize_interview_speaking_payload(_rich_interview_payload())
    payload["questions"][0]["sample_answer"] = ""
    assert not is_valid_interview_speaking_payload(payload, expected_questions=3)
