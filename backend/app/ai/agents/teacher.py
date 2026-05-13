"""Agent 0 - Teaching Agent.

Prepares the learner before the practice widget appears. The teaching
agent explains the concept behind the task, asks a short concept-check
question, and deliberately avoids leaking the generated practice answers.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.ai.llm import get_default_llm_client

logger = logging.getLogger(__name__)


class TeachingOutput(BaseModel):
    messages: list[str] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="Short chat messages to show to the learner.",
    )

    @field_validator("messages")
    @classmethod
    def clean_messages(cls, value: list[str]) -> list[str]:
        cleaned = [msg.strip() for msg in value if msg and msg.strip()]
        if not cleaned:
            raise ValueError("messages must contain at least one non-empty item")
        return cleaned[:3]


_GENERIC_TEACHING_STEPS = [
    (
        "concept",
        "Establish the core meaning of the topic using one learner-relevant example.",
    ),
    (
        "form",
        "Teach the main form or pattern the learner must notice in the task.",
    ),
    (
        "contrast",
        "Show a useful contrast or common trap so the learner can choose correctly.",
    ),
    (
        "application",
        "Ask the learner to transform or create one example using the pattern.",
    ),
    (
        "readiness",
        "Check readiness and move toward the practice task.",
    ),
]

_PRESENT_SIMPLE_TEACHING_STEPS = [
    (
        "habits_and_routines",
        "Confirm that Present Simple describes habits, routines, and facts.",
    ),
    (
        "base_verb_subjects",
        "Teach I/you/we/they + base verb: I read, you play, they study.",
    ),
    (
        "third_person_s",
        "Teach he/she/it + verb-s or -es: she reads, he studies, it works.",
    ),
    (
        "frequency_clues",
        "Teach frequency words and time clues: always, often, usually, every day, a few times a week.",
    ),
    (
        "fill_blank_strategy",
        "Apply the strategy for blanks: find the subject, find the time clue, choose the verb form.",
    ),
    (
        "readiness",
        "Check whether the learner is ready for the practice task.",
    ),
]

_SYSTEM_PROMPT = """
You are the Teaching Agent for an English learning app.

Your role:
- Teach the concept before the learner sees the practice task.
- Be warm, curious, and practical, like a strong one-on-one tutor.
- Focus on the thinking process the learner needs for the task.
- Ask one short concept-check or curiosity question.

Hard boundaries:
- Do not reveal answers from the practice task.
- Do not mention or quote the hidden generated passage.
- Do not create examples that are too similar to a likely practice passage.
- Do not write long lectures.
- Do not use markdown headings or bullet lists.
""".strip()


def _last_user_message(conversation: list[dict]) -> str:
    for message in reversed(conversation):
        if message.get("role") == "user":
            content = message.get("content")
            return str(content or "").strip()
    return ""


def _learner_needs_clarification(text: str) -> bool:
    cleaned = (text or "").strip().lower()
    if not cleaned:
        return False
    clarification_markers = (
        "don't understand", "dont understand", "do not understand",
        "didn't understand", "didnt understand", "did not understand",
        "not understand", "not clear", "unclear", "confused",
        "don't get", "dont get", "didn't get", "didnt get",
        "what is", "what are", "why", "how", "can you explain",
        "explain again", "not ready", "not yet",
    )
    return any(marker in cleaned for marker in clarification_markers)


def _recent_conversation_excerpt(conversation: list[dict], *, limit: int = 6) -> str:
    lines: list[str] = []
    for message in conversation[-limit:]:
        content = str(message.get("content") or "").strip()
        if not content or content.startswith("["):
            continue
        role = str(message.get("role") or "").lower()
        speaker = "Learner" if role == "user" else "Tutor"
        lines.append(f"{speaker}: {content[:500]}")
    return "\n".join(lines)


def _teaching_steps_for(topic: str) -> list[tuple[str, str]]:
    normalized = topic.lower()
    if "present simple" in normalized or "simple present" in normalized:
        return _PRESENT_SIMPLE_TEACHING_STEPS
    return _GENERIC_TEACHING_STEPS


def _learner_turn_count(conversation: list[dict]) -> int:
    return sum(1 for message in conversation if message.get("role") == "user")


def _teaching_step_index(conversation: list[dict], steps: list[tuple[str, str]]) -> int:
    if not steps:
        return 0
    return min(_learner_turn_count(conversation), len(steps) - 1)


def _format_teaching_agenda(
    *,
    topic: str,
    conversation: list[dict],
) -> tuple[str, str, str]:
    steps = _teaching_steps_for(topic)
    step_index = _teaching_step_index(conversation, steps)
    agenda_lines = []
    for index, (name, goal) in enumerate(steps):
        marker = "current" if index == step_index else "upcoming"
        if index < step_index:
            marker = "covered"
        agenda_lines.append(f"{index + 1}. {name} ({marker}): {goal}")
    current_name, current_goal = steps[step_index]
    return "\n".join(agenda_lines), current_name, current_goal


def _format_planner_section(teacher_instructions: dict[str, Any] | None) -> str:
    """Render the Planner's teacher_instructions as a prompt block, or empty."""
    if not teacher_instructions:
        return ""
    lines = ["Planner guidance for this lesson (prefer this over generic defaults):"]
    for key in (
        "sub_skill_context",
        "learning_goal",
        "teaching_approach",
        "concept_check_focus",
        "do_not_reveal",
    ):
        value = teacher_instructions.get(key)
        if isinstance(value, str) and value.strip():
            lines.append(f"- {key}: {value.strip()}")
    words = teacher_instructions.get("words_to_cover")
    if isinstance(words, list) and words:
        rendered = ", ".join(str(w) for w in words if str(w).strip())
        if rendered:
            lines.append(f"- words_to_cover: {rendered}")
    return "\n".join(lines)


def _build_user_prompt(
    *,
    topic: str,
    sub_skill: str,
    task_type: str,
    user_level: int,
    learner_profile: dict[str, Any],
    conversation: list[dict],
    stream_text: bool = False,
    teacher_instructions: dict[str, Any] | None = None,
) -> str:
    profile = learner_profile or {}
    interests = profile.get("interests") or "not specified"
    goals = profile.get("primary_goals") or profile.get("goal") or "general English"
    personalisation_context = profile.get("personalisation_context") or ""
    recent_user_message = _last_user_message(conversation or [])
    recent_conversation = _recent_conversation_excerpt(conversation or [])
    is_first_turn = not recent_user_message
    needs_clarification = _learner_needs_clarification(recent_user_message)
    agenda, current_step, current_goal = _format_teaching_agenda(
        topic=topic,
        conversation=conversation or [],
    )
    planner_section = _format_planner_section(teacher_instructions)
    if needs_clarification:
        current_step = "clarify_confusion"
        current_goal = (
            "Answer the learner's stated confusion before advancing the lesson."
        )

    output_instruction = (
        "Create one natural chat reply of 2-4 short sentences. Return only "
        "the message text. Do not use JSON, markdown headings, or bullets."
        if stream_text
        else "Create 2 or 3 chat messages."
    )

    final_instruction = (
        "Keep the reply short. Return only the message text."
        if stream_text
        else "Keep each message short. Return only structured data."
    )

    return f"""
Topic of the day: {topic}
Sub-skill: {sub_skill}
Practice task type coming next: {task_type}
Learner sub-level: {user_level}/10
Learner interests: {interests}
Learner goals: {goals}
Personalisation notes: {personalisation_context or "none"}
{planner_section or "Planner guidance: none — fall back to generic teaching defaults."}
Latest learner message: {recent_user_message or "none yet"}
Recent conversation:
{recent_conversation or "none yet"}
Teaching agenda:
{agenda}
Current teaching target: {current_step} — {current_goal}
Learner needs clarification: {"yes" if needs_clarification else "no"}

{output_instruction}

Teaching turn mode: {"first turn" if is_first_turn else "respond to learner"}

If this is the first teaching turn:
- Explain the key idea behind the topic in simple language.
- Teach the learner what to notice during a fill-in-the-blanks task.
- Ask a small question that checks understanding or makes them curious.

If the learner answered your previous concept-check question:
- Briefly respond to their answer.
- Connect their exact answer back to the grammar idea.
- If their answer has a grammar issue, correct only the most important one.
- Plain acknowledgements like "yes", "yeah", "ok", or "okay" are not concept-check answers.
- Do not treat them as answers to concept-check questions unless your previous
  message explicitly asked whether the concept was clear or whether they were ready.
- If the current teaching target is readiness, stop asking new grammar or
  personal-example questions. Ask directly whether the concept is clear and
  whether they feel ready for the practice task.
- Teach or probe the current teaching target above.
- Ask a new probing question that moves forward to the next grammatical idea,
  not another personal preference question.
- If their answer is already strong, ask whether they feel ready for practice.
- Do not ask the same question again.
- Do not restate the opening explanation.
- Do not move to practice yourself.

If the learner asked a question:
- Answer it directly.
- Then ask one small follow-up or readiness question.

If the learner says they do not understand, are confused, or are not ready:
- Pause the agenda and clarify the exact confusion.
- Do not move to the practice task.
- Do not ask if they are ready in this turn.
- Use one simple example, then ask a tiny check question about that confusion.

Avoid repetition:
- Do not begin with "The Present Simple tense is used..." after the first turn.
- Do not repeat the previous tutor message in different words.
- Do not keep asking about the same activity, book, genre, author, or routine.
- Personal examples are only scaffolding; use them to teach the next concept.
- Make the next reply depend on the learner's latest answer.

{final_instruction}
""".strip()


class TeachingAgent:
    def __init__(self, *, temperature: float = 0.55) -> None:
        self._llm = get_default_llm_client()
        self._temperature = temperature

    async def generate(
        self,
        *,
        topic: str,
        sub_skill: str,
        task_type: str,
        user_level: int,
        learner_profile: dict[str, Any] | None = None,
        conversation: list[dict] | None = None,
        teacher_instructions: dict[str, Any] | None = None,
    ) -> TeachingOutput:
        user_prompt = _build_user_prompt(
            topic=topic,
            sub_skill=sub_skill,
            task_type=task_type,
            user_level=user_level,
            learner_profile=learner_profile or {},
            conversation=conversation or [],
            teacher_instructions=teacher_instructions,
        )

        try:
            return await self._llm.generate_structured(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                output_model=TeachingOutput,
                temperature=self._temperature,
            )
        except Exception:
            logger.exception("TeachingAgent failed; using fallback teaching output")
            return TeachingOutput(
                messages=[
                    f"Today we are learning {topic}. Before the task, focus on the clue words around each blank.",
                    "Ask yourself: who is doing the action, and is the sentence about past, present, or future?",
                    "What clue would you check first when you see a blank in a sentence?",
                ]
            )

    async def stream_text(
        self,
        *,
        topic: str,
        sub_skill: str,
        task_type: str,
        user_level: int,
        learner_profile: dict[str, Any] | None = None,
        conversation: list[dict] | None = None,
        teacher_instructions: dict[str, Any] | None = None,
    ) -> AsyncIterator[str]:
        user_prompt = _build_user_prompt(
            topic=topic,
            sub_skill=sub_skill,
            task_type=task_type,
            user_level=user_level,
            learner_profile=learner_profile or {},
            conversation=conversation or [],
            stream_text=True,
            teacher_instructions=teacher_instructions,
        )
        async for chunk in self._llm.stream_text(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=self._temperature,
        ):
            yield chunk

    @staticmethod
    def _last_user_message(conversation: list[dict]) -> str:
        return _last_user_message(conversation)


async def generate_teaching_turn(
    *,
    topic: str,
    sub_skill: str,
    task_type: str,
    user_level: int,
    learner_profile: dict[str, Any] | None = None,
    conversation: list[dict] | None = None,
    teacher_instructions: dict[str, Any] | None = None,
) -> TeachingOutput:
    agent = TeachingAgent()
    return await agent.generate(
        topic=topic,
        sub_skill=sub_skill,
        task_type=task_type,
        user_level=user_level,
        learner_profile=learner_profile,
        conversation=conversation,
        teacher_instructions=teacher_instructions,
    )


async def stream_teaching_turn(
    *,
    topic: str,
    sub_skill: str,
    task_type: str,
    user_level: int,
    learner_profile: dict[str, Any] | None = None,
    conversation: list[dict] | None = None,
    teacher_instructions: dict[str, Any] | None = None,
) -> AsyncIterator[str]:
    agent = TeachingAgent()
    async for chunk in agent.stream_text(
        topic=topic,
        sub_skill=sub_skill,
        task_type=task_type,
        user_level=user_level,
        learner_profile=learner_profile,
        conversation=conversation,
        teacher_instructions=teacher_instructions,
    ):
        yield chunk
