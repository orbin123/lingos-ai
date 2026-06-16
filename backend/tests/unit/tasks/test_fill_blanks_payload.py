"""Fill-in-the-blanks payload normalization."""

from app.modules.sessions.task_generator import normalize_fill_in_blanks_payload


def test_normalize_fill_blanks_strips_pronoun_hints_and_misused_base_verbs() -> None:
    normalized = normalize_fill_in_blanks_payload(
        {
            "passage_title": "A family visit",
            "passage": (
                "Last weekend, ___ (visit) (I) visited my grandparents. "
                "They were very happy to see ___ (see) (me)."
            ),
            "items": [
                {
                    "item_id": "b1",
                    "sentence_with_blank": "Last weekend, ___ (visit) (I) visited my grandparents.",
                    "base_verb": "visit",
                    "correct_answer": "I",
                    "explanation": "Subject pronoun for the person doing the action.",
                },
                {
                    "item_id": "b2",
                    "sentence_with_blank": "They were very happy to see ___ (see) (me).",
                    "base_verb": "see",
                    "correct_answer": "me",
                    "explanation": "Object pronoun for the person receiving the action.",
                },
            ],
        }
    )

    assert "base_verb" not in normalized["items"][0]
    assert "base_verb" not in normalized["items"][1]
    assert normalized["passage"] == (
        "Last weekend, ___ visited my grandparents. "
        "They were very happy to see ___."
    )
    assert normalized["items"][0]["sentence_with_blank"] == (
        "Last weekend, ___ visited my grandparents."
    )


def test_normalize_fill_blanks_keeps_base_verb_for_inflection_blanks() -> None:
    normalized = normalize_fill_in_blanks_payload(
        {
            "passage": "Maria ___ (wake) up at seven. She always ___ (drink) coffee first.",
            "items": [
                {
                    "item_id": "b1",
                    "sentence_with_blank": "Maria ___ (wake) up at seven.",
                    "base_verb": "wake",
                    "correct_answer": "wakes",
                    "explanation": "Third person singular adds -s.",
                },
                {
                    "item_id": "b2",
                    "sentence_with_blank": "She always ___ (drink) coffee first.",
                    "base_verb": "drink",
                    "correct_answer": "drinks",
                    "explanation": "Third person singular adds -s.",
                },
            ],
        }
    )

    assert normalized["items"][0]["base_verb"] == "wake"
    assert normalized["items"][1]["base_verb"] == "drink"
    assert normalized["passage"] == "Maria ___ up at seven. She always ___ coffee first."


def test_normalize_fill_blanks_masks_inline_answers_into_blanks() -> None:
    normalized = normalize_fill_in_blanks_payload(
        {
            "passage": "She wakes up at seven. He drinks coffee first.",
            "items": [
                {
                    "item_id": "b1",
                    "sentence_with_blank": "She wakes up at seven.",
                    "base_verb": "wake",
                    "correct_answer": "wakes",
                    "explanation": "Third person singular adds -s.",
                },
                {
                    "item_id": "b2",
                    "sentence_with_blank": "He drinks coffee first.",
                    "base_verb": "drink",
                    "correct_answer": "drinks",
                    "explanation": "Third person singular adds -s.",
                },
            ],
        }
    )

    # The answer must never be visible — it is replaced by a blank everywhere.
    assert normalized["passage"] == "She ___ up at seven. He ___ coffee first."
    assert normalized["items"][0]["sentence_with_blank"] == "She ___ up at seven."
    assert normalized["items"][1]["sentence_with_blank"] == "He ___ coffee first."
    assert "wakes" not in normalized["passage"]
    assert "drinks" not in normalized["passage"]


def test_normalize_fill_blanks_drops_base_verb_when_it_equals_answer() -> None:
    normalized = normalize_fill_in_blanks_payload(
        {
            "passage": "The weather is ___ today.",
            "items": [
                {
                    "item_id": "b1",
                    "sentence_with_blank": "The weather is ___ today.",
                    "base_verb": "sunny",
                    "correct_answer": "sunny",
                    "explanation": "Vocabulary blank.",
                },
            ],
        }
    )

    # A hint that just repeats the answer is suppressed.
    assert "base_verb" not in normalized["items"][0]
