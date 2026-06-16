"""Teacher agent — single-turn guardrails: message validation + deterministic repair.

Split out of the former monolithic test_teacher_agent_prompt.py."""

from __future__ import annotations

import pytest

from app.ai.agents.teacher import (
    TeachingOutput,
    _collapse_to_single_question,
    _deterministic_repair,
    _question_positions_outside_quotes,
    validate_teaching_message,
)
# Canonical fake (Phase 3 — moved out of this file into tests/mocks/).

# --- Guardrail tests: single-turn contract -----------------------------------


def test_validate_clean_message_returns_no_violations() -> None:
    assert validate_teaching_message("Nice work. Can you change it to he?") == []


def test_validate_flags_empty_praise_without_specific_learner_phrase() -> None:
    msg = "Great! Can you try a sentence with sometimes?"
    violations = validate_teaching_message(msg)
    assert "empty_praise" in violations


def test_validate_allows_specific_positive_feedback() -> None:
    msg = "You used 'always assists' correctly. Ready to try the practice task?"
    assert validate_teaching_message(msg) == []


def test_validate_flags_extended_production_ask() -> None:
    msg = (
        "Good fix. Can you tell me a short story with 4-5 sentences "
        "about your graduation day?"
    )
    violations = validate_teaching_message(msg)
    assert "extended_production_ask" in violations


def test_validate_allows_one_sentence_ask() -> None:
    msg = (
        "You fixed **go** after **did**. "
        "Can you say one sentence about your graduation day?"
    )
    assert validate_teaching_message(msg) == []


def test_teaching_output_rejects_extended_production_ask() -> None:
    with pytest.raises(ValueError, match="extended_production_ask"):
        TeachingOutput(messages=["Nice. Can you write a paragraph about yesterday?"])


def test_validate_flags_multiple_questions() -> None:
    msg = "Good. Can you say it with he? And what about she?"
    violations = validate_teaching_message(msg)
    assert "multiple_questions" in violations


def test_validate_allows_question_inside_learner_quote() -> None:
    msg = (
        'Nice — you asked "Do you usually hike?" clearly. '
        "Can you answer it with Yes, I do?"
    )
    assert validate_teaching_message(msg) == []


def test_validate_flags_too_long() -> None:
    msg = " ".join(["word"] * 100) + "?"
    violations = validate_teaching_message(msg)
    assert "too_long" in violations


def test_validate_flags_empty() -> None:
    assert validate_teaching_message("   ") == ["empty"]


def test_validate_flags_readiness_combined_with_teaching() -> None:
    msg = (
        "With he or she we add an s to the verb. Now you understand the rule. "
        "Always use this for routines. Ready to try the practice task?"
    )
    violations = validate_teaching_message(msg)
    assert "readiness_combined_with_teaching" in violations


def test_validate_flags_duplicate_of_previous() -> None:
    prev = "Hello! Today we will learn about the simple present tense."
    # Same words, slight reorder — Jaccard well above threshold.
    msg = "Hello! Today we learn about the simple present tense will."
    violations = validate_teaching_message(msg, previous_assistant_message=prev)
    assert "duplicate_of_previous" in violations


def test_validate_not_duplicate_when_content_differs() -> None:
    prev = "Hello! Today we will learn about the simple present tense."
    msg = "You used 'analyze'. Can you say it with he?"
    violations = validate_teaching_message(msg, previous_assistant_message=prev)
    assert "duplicate_of_previous" not in violations


def test_teaching_output_rejects_multiple_messages() -> None:
    with pytest.raises(ValueError, match="exactly one message"):
        TeachingOutput(messages=["one?", "two?"])


def test_teaching_output_rejects_multiple_questions() -> None:
    with pytest.raises(ValueError, match="multiple_questions"):
        TeachingOutput(messages=["A? B?"])


def test_question_marks_inside_quotes_do_not_count_as_extra_questions() -> None:
    msg = (
        'You wrote "Do you usually hike?" — that is a good wh-question! '
        "Now, can you give me a short answer for it?"
    )
    assert _question_positions_outside_quotes(msg) == [len(msg) - 1]
    assert validate_teaching_message(msg) == []
    assert _deterministic_repair(msg) == msg


def test_repair_closes_dangling_quote_before_final_question() -> None:
    raw = 'For example, you could say, "Do you usually smoke?'
    repaired = _deterministic_repair(raw)
    assert repaired.count('"') % 2 == 0
    assert repaired.endswith('smoke?"')


def test_repair_strips_orphan_leading_quote_before_em_dash() -> None:
    raw = '" — that is a great question! Now, can you give me a short answer?'
    repaired = _deterministic_repair(raw)
    assert not repaired.startswith('"')
    assert repaired.startswith("—") or repaired.startswith("that")


def test_collapse_keeps_longest_probe_not_illustrative_example() -> None:
    """Depth-day opener: inline ``Do you…?`` must not beat the real ask."""

    raw = (
        "Hello! Yesterday, you practiced simple present routines. Today, we "
        "will add questions like Do you...? Can you ask one yes/no question "
        "about a daily routine?"
    )
    collapsed = _collapse_to_single_question(raw)
    assert collapsed.count("?") == 1
    assert "yes/no question" in collapsed
    assert collapsed.endswith("about a daily routine?")


def test_collapse_keeps_primary_probe_over_follow_up() -> None:
    bad = (
        "Great sentence! For 'I' use the base verb 'analyze'. For 'he' add an "
        "s to make 'analyzes'. Now can you say it with he? Also what about she?"
    )
    collapsed = _collapse_to_single_question(bad)
    assert collapsed.count("?") == 1
    assert "say it with he" in collapsed
    assert "Also what about she" not in collapsed


def test_deterministic_repair_uses_longest_question() -> None:
    repaired = _deterministic_repair(
        "Today we add Do you...? Can you ask one routine question?"
    )
    assert repaired.count("?") == 1
    assert repaired.endswith("routine question?")
