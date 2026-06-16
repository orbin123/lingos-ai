"""Agent 0 -- Teacher Agent for chat-driven learning sessions.

Prompt vs system boundary
-------------------------
* **LLM / prompt** owns: 60--80 word budget, one question per turn, one-sentence
  learner probes, following the current authored step, readiness as a standalone
  final turn.
* **System** owns: structural repair (multi-question collapse, quote fixes),
  hard reject >80 words (retry then step-aware fallback — never word-slice),
  ``extended_production_ask`` detection, duplicate-of-previous detection.
* **Deterministic bypass** emits ``readiness_prompt`` verbatim on the final
  authored step without calling the LLM.
"""

from __future__ import annotations

import logging
import re
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
_TARGET_WORDS = 60
_HARD_MAX_WORDS = 80
_MAX_WORDS_PER_TURN = _HARD_MAX_WORDS
_DEFAULT_READINESS_PROMPT = "Ready to try the practice task?"
_DUPLICATE_JACCARD_THRESHOLD = 0.85
_READINESS_SENTENCE = "ready to try the practice task?"
_EMPTY_PRAISE_PREFIXES = ("great!", "good job!", "nice sentence!")
_EXTENDED_PRODUCTION_PATTERNS = (
    re.compile(r"\b\d+\s*(?:–|-)\s*\d+\s+sentences?\b", re.I),
    re.compile(
        r"\b(?:two|three|four|five|2|3|4|5)\s+sentences?\b",
        re.I,
    ),
    re.compile(r"\b(?:short|mini[- ]?)story\b", re.I),
    re.compile(r"\btell (?:me )?(?:a |your )?(?:short )?story\b", re.I),
    re.compile(r"\bwrite a paragraph\b", re.I),
    re.compile(r"\bpair of sentences\b", re.I),
    re.compile(r"\bseveral sentences\b", re.I),
    re.compile(r"\bmultiple sentences\b", re.I),
)
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

    if len(_question_positions_outside_quotes(text)) > 1:
        violations.append("multiple_questions")

    if len(text.split()) > _MAX_WORDS_PER_TURN:
        violations.append("too_long")

    lowered = text.lower()
    if lowered.startswith(_EMPTY_PRAISE_PREFIXES) and not any(
        quote in text for quote in ("'", '"')
    ):
        violations.append("empty_praise")

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

    if _asks_for_extended_production(text):
        violations.append("extended_production_ask")

    return violations


def _asks_for_extended_production(text: str) -> bool:
    """True when the teacher asks the learner for multi-sentence output."""

    positions = _question_positions_outside_quotes(text)
    probe = text
    if positions:
        _, probe = _clause_for_question_mark(text, positions[-1])
    lowered = probe.lower()
    if "one sentence" in lowered or "in one sentence" in lowered:
        return False
    return any(pattern.search(probe) for pattern in _EXTENDED_PRODUCTION_PATTERNS)


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
3. The message is short: target 60 words or less (two to four sentences is
   ideal); 80 words is a hard ceiling. If a draft runs long, REWRITE it
   shorter — finish every sentence. A turn is always a COMPLETE message: never
   truncate or cut off mid-sentence, so the learner never sees a clipped reply.
4. After your question, STOP. Do not preview the next step, do not add a
   second teaching point, do not ask "and also...". Wait for the learner.

FORMATTING (inline emphasis only — keep the chat conversational):
Use lightweight Markdown in the message text. No headings, bullet lists,
numbered lists, links, or code blocks.
- Wrap the one or two grammar tokens or contrast pairs the learner must notice
  in double asterisks, e.g. **do**, **doesn't**, **-s**, or a short quoted
  learner phrase like **I walk**.
- At most two bold spans per turn. Do not bold whole sentences.
- If the learner profile lists a native language, you may add a very short
  L1 gloss (1–3 words) in single asterisks immediately after a tricky English
  word, e.g. *fumo* after "smoke". Skip L1 glosses when native language is
  unknown or English.
- Italics are only for those brief L1 glosses, not for English teaching text.

ACKNOWLEDGE-THEN-PROBE (every turn after the opener):
Begin by referring to something SPECIFIC the learner just said — quote a word
or phrase from their last message. Never use empty praise like "Great!",
"Good job!", or "Nice sentence!" with nothing else. If they wrote "I analyze
data", say "You used 'analyze' — that's the base verb." Then introduce at
most one new teaching point and end with one question.
Specific praise is enough: quote the useful learner phrase, say why it works
in simple words, and move forward. Do not add celebration filler.

ONE IDEA PER TURN:
Introduce at most one new rule, pattern, or example per turn. If the learner
has NOT yet demonstrated the previous point, do not add another — re-probe
the same point with a smaller, easier question instead.

LEARNER PRODUCTION RULE (MANDATORY during teaching):
Every question you ask the learner must expect ONE short sentence (or a
single word/phrase) — never a paragraph, story, list, or multi-sentence
answer. Focus only on the current step's main grammar point.
Never ask for "4-5 sentences", "a short story", "tell me about…" in depth,
"a paragraph", "several sentences", or "a pair of sentences". If an authored
step mentions longer writing, that happens only in the practice task — not
in chat teaching. When previewing practice, say the task will use a short
passage; do not ask the learner to produce that passage now.

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

SUCCESS ACCEPTANCE RULE:
Accept any valid answer that demonstrates the target pattern, even if it uses
a different example, subject, verb, adverb, or object than you expected. For
frequency-adverb steps, always, usually, often, sometimes, and never all
count as successful when the sentence is grammatical enough. After success,
do not ask the learner to try another adverb, another subject, or another
version. Move to the next authored step.

FINAL TRANSITION RULE:
If the next authored step is a wrap-up, readiness, task-transition, or says
to ask "Ready to try the practice task?", treat it as the end of teaching.
Do not add a new teaching point, recap, or extra check. Ask only "Ready to
try the practice task?" after a brief specific acknowledgement if needed.

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

QUOTING RULE:
When you quote the learner, use straight quotes and always close them. Prefer
"You used hike — that works." over a leading " — praise fragment. Never leave
an open quote before your final question. Example sentences inside your turn
may use single quotes or no quotes; do not put a question mark inside a quoted
example if your turn already ends with a real question for the learner.
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
        f"Native language: {_stringify(learner_profile.get('native_language')) or 'unknown'}",
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


def _count_teacher_chat_turns(conversation: list[dict[str, Any]]) -> int:
    count = 0
    for message in conversation:
        if message.get("role") not in ("ai", "assistant"):
            continue
        if str(message.get("type") or "chat") != "chat":
            continue
        count += 1
    return count


def _readiness_prompt_from_instructions(
    teacher_instructions: TeacherInstructions | None,
) -> str:
    prompt = _stringify((teacher_instructions or {}).get("readiness_prompt"))
    return prompt or _DEFAULT_READINESS_PROMPT


def _current_step_index(
    conversation: list[dict[str, Any]],
    scripted_plan: list[str] | None,
    *,
    explicit_index: int | None = None,
) -> int | None:
    if not scripted_plan:
        return None
    if explicit_index is not None:
        return min(max(explicit_index, 1), len(scripted_plan))
    return min(_count_teacher_chat_turns(conversation) + 1, len(scripted_plan))


def _step_instruction(scripted_plan: list[str] | None, step_index: int | None) -> str:
    if not scripted_plan or step_index is None:
        return ""
    idx = step_index - 1
    if idx < 0 or idx >= len(scripted_plan):
        return ""
    return scripted_plan[idx].strip()


def _is_readiness_step_text(text: str) -> bool:
    lowered = text.lower()
    return "ready" in lowered and "practice" in lowered


def _should_emit_readiness_turn(
    *,
    conversation: list[dict[str, Any]],
    scripted_plan: list[str] | None,
    teacher_instructions: TeacherInstructions | None,
    current_step_index: int | None,
) -> bool:
    if not scripted_plan:
        return False
    plan_len = len(scripted_plan)
    final_step = scripted_plan[-1]
    if not _is_readiness_step_text(final_step):
        return False
    ai_turns = _count_teacher_chat_turns(conversation)
    step_index = _current_step_index(
        conversation, scripted_plan, explicit_index=current_step_index
    )
    return step_index == plan_len and ai_turns >= plan_len - 1


def _format_current_step_block(
    scripted_plan: list[str] | None, step_index: int | None
) -> str:
    step_text = _step_instruction(scripted_plan, step_index)
    if not step_text:
        return "No current authored step (follow the lesson description)."
    return f"{step_index}. {step_text}"


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
    current_step_index: int | None = None,
) -> str:
    """Build the teacher prompt from curriculum + learner context."""

    instructions = dict(teacher_instructions or {})
    description = (
        lesson_description
        or _stringify(instructions.get("lesson_description"))
        or "No lesson description provided."
    )
    step_index = _current_step_index(
        conversation, scripted_plan, explicit_index=current_step_index
    )
    current_step_block = _format_current_step_block(scripted_plan, step_index)

    return f"""\
Lesson title: {topic}
Lesson description: {description}
Skill/theme: {sub_skill}
Learner sub-level: {user_level}/10
Current task type after teaching: {task_type}

TURN BUDGET: Your next message must be {_TARGET_WORDS}--{_HARD_MAX_WORDS} words
total (aim for ~{_TARGET_WORDS}). Include acknowledgement + one teaching point
+ exactly one short question. Complete every sentence — never cut off mid-thought.

LEARNER PROFILE
{_format_profile(learner_profile)}

CURRENT STEP (execute ONLY this step this turn — do not skip ahead or repeat earlier steps)
{current_step_block}

AUTHORED TEACHER BEHAVIOR (full plan — reference only; do not execute multiple steps in one turn)
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


def _is_contraction_apostrophe(text: str, index: int) -> bool:
    if text[index] != "'":
        return False
    if index > 0 and text[index - 1].isalpha():
        return True
    if index + 1 < len(text) and text[index + 1].isalpha():
        return True
    return False


def _question_positions_outside_quotes(text: str) -> list[int]:
    """Indices of ``?`` that count toward the one-question turn contract."""

    positions: list[int] = []
    in_double = False
    in_single = False
    index = 0
    while index < len(text):
        char = text[index]
        if char == '"':
            in_double = not in_double
        elif char == "'" and not in_double:
            if not _is_contraction_apostrophe(text, index):
                in_single = not in_single
        elif char == "?" and not in_double and not in_single:
            positions.append(index)
        index += 1
    return positions


def _balance_double_quotes(text: str) -> str:
    """Close a single dangling double-quote so repair logic sees a full clause."""

    if text.count('"') % 2 == 0:
        return text
    question_index = text.rfind("?")
    if question_index != -1:
        return text[: question_index + 1] + '"' + text[question_index + 1 :]
    return f'{text}"'


def _fix_orphan_leading_quote(text: str) -> str:
    """Remove a stray opening quote before em-dash praise (``" — Great!``)."""

    stripped = text.lstrip()
    if stripped.startswith(('" —', '" -', "' —", "' -")):
        return stripped[1:].lstrip()
    if stripped.startswith('"') and stripped.count('"') == 1:
        return stripped[1:].lstrip()
    return text


def _clause_for_question_mark(text: str, question_end: int) -> tuple[int, str]:
    """Return (start_index, clause) for the question ending at question_end."""

    prev_q = text.rfind("?", 0, question_end)
    if prev_q != -1:
        start = prev_q + 1
        while start < len(text) and text[start] in " \n":
            start += 1
    else:
        prev_period = text.rfind(". ", 0, question_end)
        start = 0 if prev_period == -1 else prev_period + 2
    return start, text[start : question_end + 1].strip()


def _collapse_to_single_question(text: str) -> str:
    """When the model emits multiple questions, keep one complete probe.

    Truncating at the *first* ``?`` drops the real learner-facing question when
    an earlier clause only illustrates a pattern (e.g. depth-day ``Do you…?``).
    We keep the longest question *clause* (split on ``?``, not only ``. ``) and
    preserve teaching preamble before dropped illustrative questions.
    """

    text = text.strip()
    positions = _question_positions_outside_quotes(text)
    if not text or len(positions) <= 1:
        return text
    candidates: list[tuple[int, int, str, int]] = []
    for q_end in positions:
        start, clause = _clause_for_question_mark(text, q_end)
        candidates.append((start, q_end, clause, len(clause.split())))

    # Prefer the longest probe; on a tie, keep the last question (usually the
    # authored ask rather than an earlier chained prompt).
    best_start, best_end, best_clause, _ = max(
        candidates, key=lambda item: (item[3], item[1])
    )

    if best_end == positions[0]:
        collapsed = text[: best_end + 1].strip()
    else:
        pre_first_q = text[: positions[0]].rstrip()
        last_period = pre_first_q.rfind(". ")
        if last_period != -1:
            preamble = pre_first_q[: last_period + 1].strip()
        elif pre_first_q.endswith((".", "!")):
            preamble = pre_first_q
        else:
            # No completed sentence before the dropped question (e.g. "Info one?").
            preamble = ""
        if preamble:
            collapsed = f"{preamble} {best_clause}".strip()
        else:
            collapsed = best_clause

    if collapsed != text:
        logger.warning(
            "teacher repair: collapsed extra questions (%d -> %d words): %r -> %r",
            len(text.split()),
            len(collapsed.split()),
            text[:120],
            collapsed[:120],
        )
    return collapsed


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
    if "extended_production_ask" in violations:
        parts.append(
            "- Ask for ONE short sentence (or one word/phrase) only. Never ask "
            "for a story, paragraph, or multiple sentences during teaching."
        )
    parts.append("Rewrite the message now, following every rule.")
    return "\n".join(parts)


def _fallback_text(
    *,
    topic: str,
    conversation: list[dict[str, Any]],
    scripted_plan: list[str] | None,
    teacher_instructions: TeacherInstructions | None = None,
    current_step_index: int | None = None,
) -> str:
    """Deterministic teacher turn used when the LLM is unavailable."""

    last_user = _last_user_message(conversation)
    last_user_lower = last_user.lower()
    ai_turns = _count_teacher_chat_turns(conversation)
    readiness_prompt = _readiness_prompt_from_instructions(teacher_instructions)
    step_index = _current_step_index(
        conversation, scripted_plan, explicit_index=current_step_index
    )
    step_text = _step_instruction(scripted_plan, step_index)

    if not conversation or ai_turns == 0:
        if step_text:
            return (
                f"Hi! Today our lesson is {topic}. "
                "Tell me one short answer to start today's first step."
            )
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

    if any(
        phrase in last_user_lower
        for phrase in ("don't understand", "dont understand", "confused", "not clear")
    ):
        if step_text:
            return (
                f"No problem — we are still on {topic}. "
                "Try one short sentence for the current step."
            )
        return (
            "No problem. Simple present is for things that happen again and "
            "again. Say one short sentence about your day, like 'I study at "
            "night' or 'I work in the morning.'"
        )

    if scripted_plan:
        if ai_turns >= len(scripted_plan) or (
            step_text and _is_readiness_step_text(step_text)
        ):
            return readiness_prompt
        if last_user:
            snippet = last_user.strip()[:40]
            return (
                f"You said '{snippet}' — good. "
                "Can you give me one short sentence for the next part of today's lesson?"
            )
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
    text = _balance_double_quotes(text)
    text = _fix_orphan_leading_quote(text)
    if len(_question_positions_outside_quotes(text)) > 1:
        text = _collapse_to_single_question(text)
    text = _balance_double_quotes(text)
    text = _fix_orphan_leading_quote(text)
    return text


def _readiness_turn_text(
    *,
    conversation: list[dict[str, Any]],
    scripted_plan: list[str] | None,
    teacher_instructions: TeacherInstructions | None,
    current_step_index: int | None,
) -> str | None:
    if not _should_emit_readiness_turn(
        conversation=conversation,
        scripted_plan=scripted_plan,
        teacher_instructions=teacher_instructions,
        current_step_index=current_step_index,
    ):
        return None
    return _readiness_prompt_from_instructions(teacher_instructions)


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
    current_step_index: int | None = None,
) -> TeachingOutput:
    """Generate one teacher turn, enforcing the single-turn contract."""

    readiness_text = _readiness_turn_text(
        conversation=conversation,
        scripted_plan=scripted_plan,
        teacher_instructions=teacher_instructions,
        current_step_index=current_step_index,
    )
    if readiness_text is not None:
        logger.info("teacher: deterministic readiness turn (no LLM)")
        return TeachingOutput(messages=[readiness_text])

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
        current_step_index=current_step_index,
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
            violations = retry_violations

    logger.warning(
        "teacher.fallback_used: violations=%s step_index=%s",
        violations if violations else ["llm_unavailable"],
        _current_step_index(
            conversation, scripted_plan, explicit_index=current_step_index
        ),
    )
    fallback = _deterministic_repair(
        _fallback_text(
            topic=topic,
            conversation=conversation,
            scripted_plan=scripted_plan,
            teacher_instructions=teacher_instructions,
            current_step_index=current_step_index,
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
    current_step_index: int | None = None,
) -> AsyncIterator[str]:
    """Stream one teacher turn.

    Chunks are buffered, validated, and (if necessary) repaired before being
    yielded. This guarantees the single-turn contract on the streaming path
    just as on the non-streaming path; turn outputs are short enough (<= 60
    words) that buffering does not meaningfully affect perceived latency.
    """

    readiness_text = _readiness_turn_text(
        conversation=conversation,
        scripted_plan=scripted_plan,
        teacher_instructions=teacher_instructions,
        current_step_index=current_step_index,
    )
    if readiness_text is not None:
        logger.info("teacher: deterministic readiness turn (no LLM, stream)")
        yield readiness_text
        return

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
        current_step_index=current_step_index,
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
            user_prompt + "\n\n" + _retry_instruction(violations, previous_assistant)
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
        if retry_violations:
            violations = retry_violations

    logger.warning(
        "teacher.fallback_used (stream): violations=%s step_index=%s",
        violations if violations else ["llm_unavailable"],
        _current_step_index(
            conversation, scripted_plan, explicit_index=current_step_index
        ),
    )
    fallback = _deterministic_repair(
        _fallback_text(
            topic=topic,
            conversation=conversation,
            scripted_plan=scripted_plan,
            teacher_instructions=teacher_instructions,
            current_step_index=current_step_index,
        )
    )
    yield fallback
