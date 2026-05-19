"""Agent 0 - Teaching Agent.

Talks the learner through the lesson before the practice widget appears.
The teacher is a communication coach, NOT a textbook quizmaster:
- It anchors every lesson in the planner's concrete lesson_context.
- It draws vocabulary and examples from the learner's vocabulary_domain.
- It reframes concept checks as practical scenarios, never "What is X?".
- It never reveals practice-task answers.
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


_SYSTEM_PROMPT = """
You are the Teaching Agent for an English learning app. You are a
communication coach, not a textbook quizmaster.

Your job each turn:
- Anchor the lesson in the lesson_context the Planner gave you.
- Teach the language_focus through that scenario — never as an abstract
  grammar rule.
- Use vocabulary from the vocabulary_domain when picking examples.
- Reframe concept-check questions as practical scenarios the learner would
  actually face. Ask "How would you say this to your team lead in
  standup?" — not "What is father?" or "What is the present simple?"

Voice:
- Warm, curious, direct. Like a strong one-on-one mentor.
- One coaching nudge per turn. Short. Conversational.
- Match the conversation_style the Planner specified.

Hard bans:
- No textbook framing ("The Present Simple is used to express…").
- No childish or family-based examples for learners with a professional
  or academic domain.
- No "What is X?" definition questions. Ask scenario-based questions.
- No markdown headings, no bullet lists, no long lectures.
- Do not reveal answers from the practice task.
- Do not quote or invent passages that mirror the upcoming practice item.
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
        "can you explain", "explain again", "not ready", "not yet",
    )
    return any(marker in cleaned for marker in clarification_markers)


def _recent_conversation_excerpt(conversation: list[dict], *, limit: int = 6) -> str:
    lines: list[str] = []
    for message in conversation[-limit:]:
        content = str(message.get("content") or "").strip()
        if not content or content.startswith("["):
            continue
        role = str(message.get("role") or "").lower()
        speaker = "Learner" if role == "user" else "Coach"
        lines.append(f"{speaker}: {content[:500]}")
    return "\n".join(lines)


def _format_planner_section(teacher_instructions: dict[str, Any] | None) -> str:
    """Render the Planner's teacher_instructions as a prompt block.

    The new fields (lesson_context, vocabulary_domain, conversation_style)
    are highlighted at the top because they steer the coach's voice.
    """
    if not teacher_instructions:
        return (
            "Planner guidance: none — use a neutral, level-appropriate "
            "everyday scenario and a warm, encouraging coach voice."
        )
    lines = ["Planner guidance for this lesson (load-bearing — follow it):"]
    for key in (
        "lesson_context",
        "vocabulary_domain",
        "conversation_style",
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


def _format_structured_personalisation(structured: dict[str, Any] | None) -> str:
    """Surface the learner's personalisation so the coach can match voice."""
    if not structured:
        return "Learner personalisation: not extracted yet — use neutral defaults."
    source = structured.get("extraction_source", "llm")
    if source == "empty":
        return "Learner personalisation: empty — use a neutral everyday scenario."
    domain = structured.get("domain") or "general"
    contexts = structured.get("communication_contexts") or []
    pain = structured.get("pain_points") or []
    tone = structured.get("tone_preference") or "neutral"
    parts = [f"domain={domain}", f"tone={tone}"]
    if contexts:
        parts.append("contexts=[" + ", ".join(contexts) + "]")
    if pain:
        parts.append("pain_points=[" + ", ".join(pain) + "]")
    return "Learner personalisation: " + "; ".join(parts)


def _learner_turn_count(conversation: list[dict]) -> int:
    return sum(1 for m in conversation if m.get("role") == "user")


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
    structured = profile.get("structured_personalisation")
    recent_user_message = _last_user_message(conversation or [])
    recent_conversation = _recent_conversation_excerpt(conversation or [])
    is_first_turn = not recent_user_message
    needs_clarification = _learner_needs_clarification(recent_user_message)
    planner_section = _format_planner_section(teacher_instructions)
    personalisation_section = _format_structured_personalisation(structured)
    turn_count = _learner_turn_count(conversation or [])

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

    readiness_rule = (
        f"\nREQUIRED — Learner turn count: {turn_count}. "
        "You have already exchanged enough turns. "
        "Do NOT ask another concept-check or scenario question this turn. "
        "Give one short wrap-up sentence that ties what the learner said to "
        "the lesson pattern, then ask EXACTLY: "
        '"Ready to try the practice task?" — nothing else after that.'
        if turn_count >= 3 and not needs_clarification
        else ""
    )

    return f"""
Lesson topic label: {topic}
Sub-skill: {sub_skill}
Practice task type coming next: {task_type}
Learner sub-level: {user_level}/10
Learner interests: {interests}
Learner goals: {goals}
Learner turns so far: {turn_count}
{personalisation_section}

{planner_section}

Latest learner message: {recent_user_message or "none yet"}
Recent conversation:
{recent_conversation or "none yet"}
Learner needs clarification: {"yes" if needs_clarification else "no"}

{output_instruction}

Teaching turn mode: {"first turn" if is_first_turn else "respond to learner"}

If this is the first teaching turn:
- Open with a single sentence that puts the learner inside the
  lesson_context above. Make it feel real, not academic.
- Introduce the key idea behind the language_focus using one example
  drawn from vocabulary_domain. Keep it under three short sentences.
- Ask ONE concept-check question phrased as a practical scenario the
  learner would actually face. Never "What is X?".

If the learner answered your previous concept-check question:
- Briefly acknowledge what they said.
- Tie their answer back to the language pattern you're teaching.
- If their answer has a language slip, correct only the most important
  one — gently, in passing.
- Plain acknowledgements like "yes", "yeah", "ok" are not real answers.
  Treat them as "ready?" cues only if you just asked about readiness.
- If teaching_approach is mostly covered, ask whether they feel ready
  for the practice task — but only when it's natural to ask.

If the learner asked a question:
- Answer it directly, anchored back in the lesson_context.
- Then a single small follow-up that moves the lesson forward.

If the learner says they don't understand, are confused, or are not ready:
- Pause and clarify the exact confusion using one fresh example from the
  vocabulary_domain.
- Do not move to the practice task this turn.
- Do not ask if they are ready in this turn.

Avoid repetition:
- Do not start with "The Present Simple is used…" or any textbook
  opener. Stay inside the scenario.
- Do not repeat the previous coach message in different words.
- Do not loop on the same example. Each turn should advance.
- Use vocabulary from vocabulary_domain. If the learner has a clear
  professional domain, do not pull family/school/childhood examples.
{readiness_rule}
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
                    f"Let's work on {topic} through a real situation.",
                    "Pay attention to the language pattern in the example I just used.",
                    "When you're ready, tell me how you'd say something similar in your own words.",
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
