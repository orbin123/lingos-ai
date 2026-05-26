"""Agent 0 -- Teacher Agent for chat-driven learning sessions."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any, TypeAlias

from pydantic import BaseModel, Field, field_validator

from app.ai.llm import get_default_llm_client

logger = logging.getLogger(__name__)

TeacherInstructions: TypeAlias = dict[str, Any]

_TEMPERATURE = 0.4
# Conversation context size shown to the teacher LLM. Sized so a full
# 4-step authored plan plus a couple of recovery exchanges still fits and
# the LLM can see where it is in the plan instead of restarting from
# step 1 once early messages roll out of the window.
_MAX_RECENT_MESSAGES = 16
_MAX_WORDS_PER_TURN = 80
_DUPLICATE_JACCARD_THRESHOLD = 0.85
_READINESS_SENTENCE = "ready to try the practice task?"
_PLANNER_ONLY_KEYS = {
    "learning_goal",
    "sub_skill_context",
    "lesson_context",
    "display_label",
}


def validate_teaching_message(
    text: str,
    *,
    previous_assistant_message: str | None = None,
) -> list[str]:
    """Return a list of violation codes; empty list means the message is clean.

    Pure function — used both for schema validation and for the post-process
    repair step in generate_teaching_turn / stream_teaching_turn.
    """

    violations: list[str] = []
    if not text or not text.strip():
        violations.append("empty")
        return violations

    if text.count("?") > 1:
        violations.append("multiple_questions")

    if len(text.split()) > _MAX_WORDS_PER_TURN:
        violations.append("too_long")

    lowered = text.lower()
    if _READINESS_SENTENCE in lowered:
        idx = lowered.find(_READINESS_SENTENCE)
        before = text[:idx].strip()
        # The readiness probe must be its own turn. A short acknowledgement
        # ("Nice work.") is fine; anything resembling fresh teaching content
        # (>15 words before the readiness sentence) is not.
        if len(before.split()) > 15:
            violations.append("readiness_combined_with_teaching")

    if previous_assistant_message and _is_near_duplicate(
        text, previous_assistant_message
    ):
        violations.append("duplicate_of_previous")

    return violations


def _is_near_duplicate(a: str, b: str) -> bool:
    tokens_a = {tok.lower().strip(".,!?'\"") for tok in a.split() if tok}
    tokens_b = {tok.lower().strip(".,!?'\"") for tok in b.split() if tok}
    if not tokens_a or not tokens_b:
        return False
    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    if union == 0:
        return False
    return (intersection / union) >= _DUPLICATE_JACCARD_THRESHOLD


class TeachingOutput(BaseModel):
    """Teacher messages to append to the chat transcript.

    Enforces the single-turn contract: exactly one assistant message per
    LLM call, at most one question mark, length-capped for A1 learners.
    """

    messages: list[str] = Field(default_factory=list)

    @field_validator("messages")
    @classmethod
    def _validate_messages(cls, msgs: list[str]) -> list[str]:
        if len(msgs) > 1:
            raise ValueError(
                f"teacher must emit exactly one message per turn; got {len(msgs)}"
            )
        for msg in msgs:
            problems = validate_teaching_message(msg)
            # Duplicate-of-previous is checked at call sites where the
            # previous assistant message is known; skip it here.
            problems = [p for p in problems if p != "duplicate_of_previous"]
            if problems:
                raise ValueError(
                    f"teacher message failed validation: {problems}: {msg!r}"
                )
        return msgs


def _system_prompt() -> str:
    return """\
You are LingosAI's teacher agent: a strict, kind, human-feeling English coach.

Teach only the current lesson. Do not deliver the practice task and do not
evaluate a submitted task. Use A1-friendly English.

TURN CONTRACT (MANDATORY — never violate):
1. Output exactly ONE message per turn.
2. The message contains AT MOST ONE question mark (?), and that question is
   the final sentence. Never bundle two questions in one turn.
3. The message is short: 60 words or less. Two to four sentences is ideal.
4. After your question, STOP. Do not preview the next step, do not add a
   second teaching point, do not ask "and also...". Wait for the learner.

ACKNOWLEDGE-THEN-PROBE (every turn after the opener):
Begin by referring to something SPECIFIC the learner just said — quote a word
or phrase from their last message. Never use empty praise like "Great!",
"Good job!", or "Nice sentence!" with nothing else. If they wrote "I analyze
data", say "You used 'analyze' — that's the base verb." Then introduce at
most one new teaching point and end with one question.

ONE IDEA PER TURN:
Introduce at most one new rule, pattern, or example per turn. If the learner
has NOT yet demonstrated the previous point, do not add another — re-probe
the same point with a smaller, easier question instead.

CONFUSION HANDLER:
If the learner's last message signals confusion ("I don't understand",
"what?", "huh", "not clear", silence/empty), restate the CURRENT teaching
point in simpler words with one concrete example. Do NOT introduce a new
rule. Ask one easier question.

OFF-TOPIC / NON-ENGLISH HANDLER:
If the learner's reply is gibberish, off-topic, or written in another
language, kindly ask them to try the previous question again in English.
Do not advance to the next step.

AUTHORED BEHAVIOR RULE (highest priority):
When AUTHORED TEACHER BEHAVIOR steps are provided, those steps are the
COMPLETE and EXCLUSIVE curriculum for this session. Follow them one by one
in the listed order. Do NOT introduce any grammar pattern, vocabulary,
example topic, or explanation that is not explicitly mentioned in those
steps — even if you believe it is relevant or foundational. Only personalize
the surface wording and examples from the learner profile; never add new
teaching content.

PROGRESSION RULE:
Each step in the authored plan is done ONCE. When the learner gives a correct
or acceptable response to a step, immediately advance to the next step — do
NOT repeat the same probe with a different sentence, do NOT invent a new
variant of the same exercise, and do NOT ask for "one more example" of
something they have already demonstrated. The only exception is step-level
error recovery: if the learner's response is wrong, apply the single
correction described in the plan and ask once more; if they then succeed,
advance. Never loop the same step more than twice regardless of outcome.

NO-REPEAT RULE:
Never repeat the greeting, opening, or any earlier teacher turn. Each turn
moves the conversation forward.

TURN-CEILING RULE:
Count every teacher turn (L) in the conversation. The authored plan defines
the exact number of turns — never exceed it. When the plan ends, ask "Ready
to try the practice task?" immediately. By turn 5 at the absolute latest,
ask "Ready to try the practice task?" regardless of outcome. Never add a
summary, review, or recap step — those are not in the authored plan. Go
straight from the final authored step to the readiness question.

READINESS RULE:
"Ready to try the practice task?" is a STANDALONE turn. Send it by itself
(optionally with a one-sentence acknowledgement before it). Never combine it
with new teaching content or any other question. Ask it only after the
learner has shown understanding of the target pattern. If the learner is
confused or makes the target mistake, correct it and ask one focused
question instead — do not ask readiness yet.

NO-SPOILING RULE:
When asking the learner to produce, transform, or complete a sentence, never
include the target answer — or any part of it — inside the question itself.
Ask for what they need to produce, not the production itself. Wrong: "Can
you change 'I walk' to 'He walks'?" Right: "Can you change that sentence so
it talks about he instead of I?" If the learner is stuck after one attempt,
give a minimal hint about the rule, never the answer.

TYPO HANDLING:
If the learner's response has only a small typo but the meaning is correct,
gently correct it, then advance — do not ask the same type of question
twice.
"""


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def _format_profile(learner_profile: dict[str, Any]) -> str:
    if not learner_profile:
        return "No learner profile provided."

    structured = learner_profile.get("structured_personalisation")
    lines = [
        f"Interests: {_stringify(learner_profile.get('interests')) or 'unknown'}",
        f"Primary goals: {_stringify(learner_profile.get('primary_goals')) or 'unknown'}",
        "Personalisation context: "
        f"{_stringify(learner_profile.get('personalisation_context')) or 'none'}",
        "Self-assessed level: "
        f"{_stringify(learner_profile.get('self_assessed_level')) or 'beginner'}",
    ]
    if isinstance(structured, dict):
        domain = _stringify(structured.get("domain"))
        contexts = _stringify(structured.get("communication_contexts"))
        pain_points = _stringify(structured.get("pain_points"))
        tone = _stringify(structured.get("tone_preference"))
        if domain:
            lines.append(f"Domain: {domain}")
        if contexts:
            lines.append(f"Communication contexts: {contexts}")
        if pain_points:
            lines.append(f"Pain points: {pain_points}")
        if tone:
            lines.append(f"Tone preference: {tone}")
    return "\n".join(lines)


def _format_conversation(conversation: list[dict[str, Any]]) -> str:
    if not conversation:
        return "No previous messages."
    recent = conversation[-_MAX_RECENT_MESSAGES:]
    lines: list[str] = []
    for message in recent:
        role = str(message.get("role") or "unknown")
        content = _stringify(message.get("content"))
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines) if lines else "No previous messages."


def _format_scripted_plan(scripted_plan: list[str] | None) -> str:
    if not scripted_plan:
        return "No authored step list provided."
    return "\n".join(
        f"{index}. {step.strip()}"
        for index, step in enumerate(scripted_plan, start=1)
        if step.strip()
    )


def _format_extra_instructions(
    teacher_instructions: TeacherInstructions | None,
    *,
    scripted_plan: list[str] | None,
) -> str:
    if not teacher_instructions:
        return "No extra teacher instructions."

    ignored = _PLANNER_ONLY_KEYS if scripted_plan else set()
    lines: list[str] = []
    for key, value in teacher_instructions.items():
        if key in ignored or key == "lesson_description":
            continue
        text = _stringify(value)
        if text:
            lines.append(f"{key}: {text}")
    return "\n".join(lines) if lines else "No extra teacher instructions."


def _build_user_prompt(
    *,
    topic: str,
    sub_skill: str,
    task_type: str,
    user_level: int,
    learner_profile: dict[str, Any],
    conversation: list[dict[str, Any]],
    teacher_instructions: TeacherInstructions | None = None,
    scripted_plan: list[str] | None = None,
    lesson_description: str | None = None,
) -> str:
    """Build the teacher prompt from curriculum + learner context."""

    instructions = dict(teacher_instructions or {})
    description = (
        lesson_description
        or _stringify(instructions.get("lesson_description"))
        or "No lesson description provided."
    )

    return f"""\
Lesson title: {topic}
Lesson description: {description}
Skill/theme: {sub_skill}
Learner sub-level: {user_level}/10
Current task type after teaching: {task_type}

LEARNER PROFILE
{_format_profile(learner_profile)}

AUTHORED TEACHER BEHAVIOR
{_format_scripted_plan(scripted_plan)}

EXTRA TEACHER INSTRUCTIONS
{_format_extra_instructions(instructions, scripted_plan=scripted_plan)}

RECENT CONVERSATION
{_format_conversation(conversation)}

Write the next teacher chat message now.
"""


def _last_user_message(conversation: list[dict[str, Any]]) -> str:
    for message in reversed(conversation):
        if message.get("role") == "user":
            return _stringify(message.get("content"))
    return ""


def _last_assistant_message(conversation: list[dict[str, Any]]) -> str:
    for message in reversed(conversation):
        role = message.get("role")
        if role in ("ai", "assistant"):
            return _stringify(message.get("content"))
    return ""


def _truncate_at_first_question(text: str) -> str:
    idx = text.find("?")
    if idx == -1:
        return text.strip()
    return text[: idx + 1].strip()


def _retry_instruction(violations: list[str], previous_assistant: str) -> str:
    parts = ["Your previous draft violated the TURN CONTRACT. Fix it:"]
    if "multiple_questions" in violations:
        parts.append("- Ask exactly ONE question. Remove any extra question.")
    if "too_long" in violations:
        parts.append("- Keep the message under 60 words. Two to four sentences.")
    if "duplicate_of_previous" in violations and previous_assistant:
        snippet = previous_assistant[:200]
        parts.append(
            "- Your last turn already said: "
            f"«{snippet}». Do NOT repeat it. Acknowledge what the learner just "
            "said specifically and move the lesson forward by one step."
        )
    if "readiness_combined_with_teaching" in violations:
        parts.append(
            "- Send the readiness question by itself, with no extra teaching "
            "content in the same turn."
        )
    parts.append("Rewrite the message now, following every rule.")
    return "\n".join(parts)


def _fallback_text(
    *,
    topic: str,
    conversation: list[dict[str, Any]],
    scripted_plan: list[str] | None,
) -> str:
    """Deterministic teacher turn used when the LLM is unavailable."""

    last_user = _last_user_message(conversation).lower()
    ai_turns = sum(
        1
        for message in conversation
        if message.get("role") in ("ai", "assistant")
        and str(message.get("type") or "chat") == "chat"
    )

    if not conversation or ai_turns == 0:
        if scripted_plan:
            return (
                f"Hi! Today our lesson is {topic}. Let's start with the "
                "first step from today's lesson. Tell me one short answer "
                "connected to this topic."
            )
        return (
            f"Hi! Today our lesson is about tense: {topic}. Tense tells us "
            "when an action or state happens. The simple present is for facts, "
            "routines, and habits, like 'I work every day.' Tell me one real "
            "daily routine you have."
        )

    if any(phrase in last_user for phrase in ("don't understand", "dont understand", "confused", "not clear")):
        if scripted_plan:
            return (
                f"No problem. We are still on {topic}. I will keep it simple: "
                "try one short answer for the current lesson step."
            )
        return (
            "No problem. Simple present is for things that happen again and "
            "again. Say one short sentence about your day, like 'I study at "
            "night' or 'I work in the morning.'"
        )

    if scripted_plan:
        if ai_turns >= len(scripted_plan):
            return "Ready to try the practice task?"
        return (
            "Good. Let's continue with the next step from today's lesson. "
            f"Give one short answer about {topic}."
        )

    if " am " in f" {last_user} " and any(
        verb in last_user for verb in ("work", "study", "go", "eat", "play")
    ):
        return (
            "Small correction: do not use 'am' before an action verb here. "
            "Say 'I work' or 'I study', not 'I am work'. Now change this to "
            "he or she: 'I work every morning.'"
        )

    if ai_turns <= 1:
        return (
            "Good. With I, you, we, and they, use the base verb: 'I work.' "
            "With he or she, add -s: 'She works.' Change your sentence to "
            "he or she now."
        )

    if ai_turns <= 2:
        return (
            "Nice. Now add a frequency adverb: always, usually, often, "
            "sometimes, or never. Write one routine sentence with a frequency "
            "adverb and the correct verb form."
        )

    return (
        "That shows the pattern. Simple present describes routines and habits. "
        "Ready to try the practice task?"
    )


async def _call_llm(system_prompt: str, user_prompt: str) -> str:
    client = get_default_llm_client()
    text = await client.generate_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=_TEMPERATURE,
    )
    return (text or "").strip()


def _deterministic_repair(text: str) -> str:
    """Apply repairs that can be done without re-asking the LLM."""

    if not text:
        return ""
    text = text.strip()
    if text.count("?") > 1:
        text = _truncate_at_first_question(text)
        logger.warning("teacher repair: truncated extra questions")
    return text


async def generate_teaching_turn(
    *,
    topic: str,
    sub_skill: str,
    task_type: str,
    user_level: int,
    learner_profile: dict[str, Any],
    conversation: list[dict[str, Any]],
    teacher_instructions: TeacherInstructions | None = None,
    scripted_plan: list[str] | None = None,
    lesson_description: str | None = None,
) -> TeachingOutput:
    """Generate one teacher turn, enforcing the single-turn contract."""

    system_prompt = _system_prompt()
    user_prompt = _build_user_prompt(
        topic=topic,
        sub_skill=sub_skill,
        task_type=task_type,
        user_level=user_level,
        learner_profile=learner_profile,
        conversation=conversation,
        teacher_instructions=teacher_instructions,
        scripted_plan=scripted_plan,
        lesson_description=lesson_description,
    )
    previous_assistant = _last_assistant_message(conversation) or None

    try:
        raw = await _call_llm(system_prompt, user_prompt)
    except Exception:
        logger.exception("teacher generation failed; using deterministic fallback")
        raw = ""

    text, violations = _repair_and_check(raw, previous_assistant)
    if text and not violations:
        return TeachingOutput(messages=[text])

    if violations:
        logger.warning("teacher repair triggered: %s", violations)
        retry_prompt = (
            user_prompt
            + "\n\n"
            + _retry_instruction(violations, previous_assistant or "")
        )
        try:
            retry_raw = await _call_llm(system_prompt, retry_prompt)
        except Exception:
            logger.exception("teacher retry failed")
            retry_raw = ""

        retry_text, retry_violations = _repair_and_check(retry_raw, previous_assistant)
        if retry_text and not retry_violations:
            return TeachingOutput(messages=[retry_text])
        if retry_violations:
            logger.warning(
                "teacher repair: retry still invalid (%s); using fallback",
                retry_violations,
            )

    fallback = _deterministic_repair(
        _fallback_text(
            topic=topic,
            conversation=conversation,
            scripted_plan=scripted_plan,
        )
    )
    return TeachingOutput(messages=[fallback])


def _repair_and_check(
    raw: str, previous_assistant: str | None
) -> tuple[str, list[str]]:
    """Deterministic repair + validation. Returns (repaired_text, violations)."""

    repaired = _deterministic_repair(raw)
    if not repaired:
        return "", ["empty"]
    violations = validate_teaching_message(
        repaired, previous_assistant_message=previous_assistant
    )
    return repaired, violations


async def stream_teaching_turn(
    *,
    topic: str,
    sub_skill: str,
    task_type: str,
    user_level: int,
    learner_profile: dict[str, Any],
    conversation: list[dict[str, Any]],
    teacher_instructions: TeacherInstructions | None = None,
    scripted_plan: list[str] | None = None,
    lesson_description: str | None = None,
) -> AsyncIterator[str]:
    """Stream one teacher turn.

    Chunks are buffered, validated, and (if necessary) repaired before being
    yielded. This guarantees the single-turn contract on the streaming path
    just as on the non-streaming path; turn outputs are short enough (<= 60
    words) that buffering does not meaningfully affect perceived latency.
    """

    system_prompt = _system_prompt()
    user_prompt = _build_user_prompt(
        topic=topic,
        sub_skill=sub_skill,
        task_type=task_type,
        user_level=user_level,
        learner_profile=learner_profile,
        conversation=conversation,
        teacher_instructions=teacher_instructions,
        scripted_plan=scripted_plan,
        lesson_description=lesson_description,
    )
    previous_assistant = _last_assistant_message(conversation)

    previous_assistant_or_none = previous_assistant or None
    buffered = ""
    try:
        client = get_default_llm_client()
        async for chunk in client.stream_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=_TEMPERATURE,
        ):
            if chunk:
                buffered += chunk
    except Exception:
        logger.exception("teacher streaming failed; using deterministic fallback")
        buffered = ""

    text, violations = _repair_and_check(buffered, previous_assistant_or_none)
    if text and not violations:
        yield text
        return

    if violations:
        logger.warning("teacher repair triggered (stream): %s", violations)
        retry_prompt = (
            user_prompt
            + "\n\n"
            + _retry_instruction(violations, previous_assistant)
        )
        try:
            retry_raw = await _call_llm(system_prompt, retry_prompt)
        except Exception:
            logger.exception("teacher streaming retry failed")
            retry_raw = ""

        retry_text, retry_violations = _repair_and_check(
            retry_raw, previous_assistant_or_none
        )
        if retry_text and not retry_violations:
            yield retry_text
            return

    fallback = _deterministic_repair(
        _fallback_text(
            topic=topic,
            conversation=conversation,
            scripted_plan=scripted_plan,
        )
    )
    yield fallback
