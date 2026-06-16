"""Readiness gate, turn-ceiling, gibberish/confusion, and redirect helpers.

Split out of the former monolithic test_learning_session_file_mode.py —
pure functions on ``LearningSessionService``'s module (no DB, no mocks).
"""

from __future__ import annotations

from app.modules.learning_session.service import (
    _build_redirect_message,
    _count_trailing_redirects,
    _is_confusion,
    _is_structural_gibberish,
    _looks_like_ready_for_practice,
    _should_force_transition_to_practice,
    _tutor_asked_readiness,
)


def test_ready_gate_requires_previous_readiness_prompt() -> None:
    previous = "Nice. Ready to try the practice task?"

    assert _looks_like_ready_for_practice("ready", previous_tutor_message=previous)
    assert _looks_like_ready_for_practice("yes", previous_tutor_message=previous)
    assert not _looks_like_ready_for_practice(
        "I spend my mornings training machine learning models.",
        previous_tutor_message="Tell me one daily routine.",
    )
    assert not _looks_like_ready_for_practice(
        "I understand",
        previous_tutor_message="Tell me one daily routine.",
    )
    assert not _looks_like_ready_for_practice(
        "not ready",
        previous_tutor_message=previous,
    )


def test_looks_like_ready_for_practice_typo() -> None:
    """Common short-affirmative typos (yys, yse, okk, …) should pass the gate."""
    previous = "Great. Ready to try the practice task?"

    for typo in ("yys", "yse", "yeas", "yse!", "okk", "okey", "redy", "sury"):
        assert _looks_like_ready_for_practice(
            typo, previous_tutor_message=previous,
        ), f"expected typo {typo!r} to be treated as an affirmative"

    # Longer non-affirmative sentences must still be rejected even though they
    # contain a near-affirmative substring. The typo branch only fires when
    # the entire reply is a single short token.
    assert not _looks_like_ready_for_practice(
        "I think yys is what they meant, but please explain again.",
        previous_tutor_message=previous,
    )
    assert not _looks_like_ready_for_practice(
        "I would normally say yys here.",
        previous_tutor_message=previous,
    )


def test_readiness_prompt_soft_transitions() -> None:
    """Soft transition phrasings the teacher LLM emits must count as readiness prompts."""
    soft_transitions = (
        "Now, let's get started with the practice task. Good luck!",
        "Great! Let's begin the practice task. Please follow the instructions carefully.",
        "Time for the practice task!",
        "Ready for the practice exercise?",
        "Let's move on to the practice activity.",
        "Begin the practice task whenever you're set.",
        "Let's start with the practice task.",
    )
    for phrase in soft_transitions:
        assert _tutor_asked_readiness(phrase), (
            f"expected {phrase!r} to be recognised as a readiness prompt"
        )

    # Should not trigger on unrelated tutor messages.
    assert not _tutor_asked_readiness(
        "Now tell me one daily routine sentence."
    )
    assert not _tutor_asked_readiness(
        "Use 'usually' in a sentence about a habit."
    )


def test_turn_ceiling_force_transition_after_authored_plan() -> None:
    """After teacher exhausts the authored plan + mentions practice, plain
    "okay" must force a transition even when the strict gate misses it.
    """
    scripted = [
        "TURN 1 — Open the lesson",
        "TURN 2 — Subject-verb agreement",
        "TURN 3 — Frequency adverbs",
        "TURN 4 — Wrap-up: ask 'Ready to try the practice task?'",
    ]
    state = {
        "daily_plan": {
            "teacher_instructions": {"__scripted_plan": scripted},
        },
    }
    messages = [
        {"role": "ai", "content": "Hi! Today we learn the simple present.", "type": "chat"},
        {"role": "user", "content": "I analyze data every day.", "type": "chat"},
        {"role": "ai", "content": "Good. Now use 'he' or 'she'.", "type": "chat"},
        {"role": "user", "content": "He analyzes data every day.", "type": "chat"},
        {"role": "ai", "content": "Nice. Add a frequency adverb.", "type": "chat"},
        {"role": "user", "content": "She usually analyzes data.", "type": "chat"},
        {"role": "ai", "content": "Are you ready to try the practice task?", "type": "chat"},
        {"role": "user", "content": "yys", "type": "chat"},
        # Recovery message that the strict gate does not match.
        {
            "role": "ai",
            "content": "Got it — I think you meant yes. Let's begin the practice task. Good luck!",
            "type": "chat",
        },
    ]

    # Plain "okay" with no recognised readiness prompt should still
    # transition via the escape valve.
    assert _should_force_transition_to_practice(
        user_text="okay",
        messages=messages,
        state=state,
    )

    # Negation must still block the escape valve.
    assert not _should_force_transition_to_practice(
        user_text="not yet",
        messages=messages,
        state=state,
    )

    # Empty conversation: cannot force.
    assert not _should_force_transition_to_practice(
        user_text="ok",
        messages=[],
        state=state,
    )

    # No prior tutor mentioned 'practice task': cannot force.
    no_mention = [
        {"role": "ai", "content": "Step 1 explanation.", "type": "chat"},
        {"role": "ai", "content": "Step 2 explanation.", "type": "chat"},
        {"role": "ai", "content": "Step 3 explanation.", "type": "chat"},
        {"role": "ai", "content": "Step 4 explanation.", "type": "chat"},
    ]
    assert not _should_force_transition_to_practice(
        user_text="okay",
        messages=no_mention,
        state=state,
    )


# ── Learner input gate: gibberish / off-topic during teaching ───────────────


def test_is_structural_gibberish_flags_junk() -> None:
    for junk in ("", "   ", "!!!", "...", "aaaaaa", "zzzzz", "asdkjfh", "qwrtpln"):
        assert _is_structural_gibberish(junk), f"expected {junk!r} to be gibberish"


def test_is_structural_gibberish_allows_short_valid_answers() -> None:
    # Length alone is never a trigger — short real answers must pass.
    for ok in (
        "Walk.",
        "I go.",
        "yes",
        "She walk to school",  # wrong grammar but relevant
        "I goes to work every day",
        "He play football",
    ):
        assert not _is_structural_gibberish(ok), f"expected {ok!r} to pass"


def test_is_confusion_recognises_not_understanding() -> None:
    assert _is_confusion("I don't understand")
    assert _is_confusion("can you explain again")
    assert _is_confusion("not clear")
    assert not _is_confusion("She walks to school")


def test_count_trailing_redirects() -> None:
    assert _count_trailing_redirects([]) == 0
    messages = [
        {"role": "ai", "content": "Give me a sentence.", "type": "chat"},
        {"role": "user", "content": "asdkjfh", "type": "chat"},
        {"role": "ai", "content": "Off-topic.", "type": "chat", "redirect": True},
        {"role": "user", "content": "lol no", "type": "chat"},
        {"role": "ai", "content": "Off-topic.", "type": "chat", "redirect": True},
    ]
    assert _count_trailing_redirects(messages) == 2
    # A normal (non-redirect) teacher turn breaks the streak.
    messages.append({"role": "user", "content": "I walk", "type": "chat"})
    messages.append({"role": "ai", "content": "Nice!", "type": "chat"})
    assert _count_trailing_redirects(messages) == 0


def test_build_redirect_message_restates_topic_and_reasks() -> None:
    msg = _build_redirect_message(
        topic="the simple present",
        previous_tutor_message="Give me one sentence in the simple present.",
        redirect_count=0,
        reason="off_topic",
    )
    assert "off-topic" in msg.lower()
    assert "the simple present" in msg
    assert "Give me one sentence in the simple present." in msg


def test_build_redirect_message_escalates_after_threshold() -> None:
    msg = _build_redirect_message(
        topic="the simple present",
        previous_tutor_message="Give me one sentence.",
        redirect_count=3,
        reason="gibberish",
    )
    assert "easier version" in msg.lower()
    # Escalation drops the verbatim re-ask in favour of a gentler nudge.
    assert "Give me one sentence." not in msg
