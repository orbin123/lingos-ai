"""Planner Agent - produces a structured DailyPlan once per day.

Runs lazily on the first session open for a given (user, course, week, day).
Downstream agents (Teacher, Task Generator, Evaluator) all read from the
plan so they share one level-aware view of the day.

What the LLM generates here:
  1. teacher_instructions   - rich context the Teacher Agent needs, including
                              a concrete lesson_context drawn from the user's
                              structured_personalisation
  2. evaluation_focuses     - per-activity scoring guidance for the Evaluator

Everything else (template_id, widget, evaluation_method) is a deterministic
lookup against the existing full_tasks_templates registry.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.ai.llm import get_default_llm_client
from app.modules.curriculum.topics import CourseTopic
from app.tasks.schemas.base import Activity, SubSkill
from app.tasks.schemas.full_tasks_templates import (
    TEMPLATE_TO_WIDGET,
    get_full_template,
)

logger = logging.getLogger(__name__)


_ACTIVITY_ORDER: tuple[Activity, ...] = (
    Activity.READ,
    Activity.WRITE,
    Activity.LISTEN,
    Activity.SPEAK,
)

# The topic JSON labels ("expression", "comprehension") historically diverge
# from the SubSkill enum values ("thought_organization", "listening"). The
# template_id strings follow the topic JSON, so the lookup map below normalises
# the curriculum's external label to the enum the templates were registered
# with.
_SUB_SKILL_ALIASES: dict[str, SubSkill] = {
    "expression": SubSkill.THOUGHT_ORGANIZATION,
    "comprehension": SubSkill.LISTENING,
}


def _resolve_sub_skill(sub_skill: str) -> SubSkill:
    if sub_skill in _SUB_SKILL_ALIASES:
        return _SUB_SKILL_ALIASES[sub_skill]
    return SubSkill(sub_skill)


# ─────────────────────────────────────────────────────────────
# Pydantic output schemas
# ─────────────────────────────────────────────────────────────


class TeacherInstructions(BaseModel):
    sub_skill_context: str = Field(..., min_length=10)
    learning_goal: str = Field(..., min_length=10)
    words_to_cover: list[str] | None = Field(default=None)
    teaching_approach: str = Field(..., min_length=10)
    concept_check_focus: str = Field(..., min_length=5)
    do_not_reveal: str = Field(..., min_length=5)
    # NEW — personalization-driven lesson context. These three fields are
    # the bridge between the abstract curriculum objective and the concrete
    # scenario the learner experiences. They MUST reflect the user's
    # structured_personalisation when one is available.
    lesson_context: str = Field(..., min_length=5)
    vocabulary_domain: str = Field(..., min_length=3)
    conversation_style: str = Field(..., min_length=3)


class EvaluationFocus(BaseModel):
    focus_areas: list[str] = Field(..., min_length=1)
    level_note: str = Field(..., min_length=5)
    scoring_instruction: str = Field(..., min_length=5)


class PlannerLLMOutput(BaseModel):
    """Only the LLM-generated parts of the plan.

    The full DailyPlan is assembled by the agent — template_id, widget, and
    evaluation_method are looked up deterministically (not generated).
    """

    teacher_instructions: TeacherInstructions
    evaluation_focuses: list[EvaluationFocus] = Field(..., min_length=4, max_length=4)

    @field_validator("evaluation_focuses")
    @classmethod
    def _exactly_four(cls, value: list[EvaluationFocus]) -> list[EvaluationFocus]:
        if len(value) != 4:
            raise ValueError("evaluation_focuses must have exactly 4 entries")
        return value


# ─────────────────────────────────────────────────────────────
# Prompt building
# ─────────────────────────────────────────────────────────────


_SYSTEM_PROMPT = """
You are the Planner Agent for an English learning app.

The curriculum gives you TWO things:
1. communication_goal — what the learner should be able to DO in real life
   (e.g. "introduce yourself in a workplace setting").
2. language_focus — the linguistic anchor for the day (e.g. "present simple —
   affirmative"). This is non-negotiable: it must drive every example,
   word, and pattern in the lesson.

The learner profile gives you a STRUCTURED PERSONALISATION block — their
domain, communication contexts, priority skills, pain points, and tone
preference. Your job is to combine these so the lesson feels like it was
designed for THIS learner.

You must produce:
1. teacher_instructions — rich context the Teacher Agent needs, including
   a concrete lesson_context that the teaching turn will revolve around.
2. evaluation_focus for each of the 4 activities (read, write, listen,
   speak) in that exact order — level-aware scoring guidance.

Hard rules:
- Pick ONE concrete scenario for lesson_context that fits both the
  communication_goal AND the learner's communication_contexts. If the
  personalisation is empty/fallback, fall back to a neutral everyday
  scenario at this sub_level.
- vocabulary_domain must come from the learner's `domain` whenever it's
  more specific than "general". Otherwise pick a specific everyday domain.
- conversation_style follows the learner's tone_preference. Default to
  neutral for empty profiles.
- language_focus drives words_to_cover and the patterns the
  teaching_approach demonstrates. Never lose it in the personalisation.
- sub_level guards the difficulty ceiling. Do NOT pull jargon or
  sophisticated vocabulary into a sub_level 1-3 lesson even if the
  learner's domain would normally use it.
- Be lenient at sub_level 1-3, balanced at 4-6, rigorous at 7-10.
- do_not_reveal lists what the teacher should NOT say (so it doesn't
  leak task answers).
- Return only the structured JSON. No commentary.
""".strip()


def _format_structured_personalisation(structured: dict[str, Any] | None) -> str:
    """Render the structured personalisation block for the user prompt.

    Falls back to a neutral note when no payload exists yet.
    """
    if not structured:
        return (
            "Structured personalisation: not extracted yet — treat as empty. "
            "Pick a neutral, level-appropriate scenario."
        )

    source = structured.get("extraction_source", "llm")
    if source == "empty":
        return (
            "Structured personalisation: EMPTY (learner gave no personalisation "
            "context). Pick a neutral, level-appropriate everyday scenario."
        )

    domain = structured.get("domain") or "general"
    contexts = structured.get("communication_contexts") or []
    priority_skills = structured.get("priority_skills") or []
    pain_points = structured.get("pain_points") or []
    tone = structured.get("tone_preference") or "neutral"

    contexts_str = ", ".join(contexts) if contexts else "(none specified)"
    priority_str = ", ".join(priority_skills) if priority_skills else "(none specified)"
    pain_str = ", ".join(pain_points) if pain_points else "(none specified)"

    note = ""
    if source == "fallback":
        note = "  (extraction fell back to defaults — be conservative)\n"

    return (
        "Structured personalisation:\n"
        f"  domain: {domain}\n"
        f"  communication contexts: {contexts_str}\n"
        f"  priority skills: {priority_str}\n"
        f"  pain points: {pain_str}\n"
        f"  tone preference: {tone}\n"
        f"{note}"
    ).rstrip()


def _build_planner_prompt(
    *,
    topic_entry: CourseTopic,
    learner_profile: dict[str, Any],
) -> str:
    profile = learner_profile or {}
    interests = profile.get("interests") or "not specified"
    goals = profile.get("primary_goals") or profile.get("goal") or "general English"
    native_language = profile.get("native_language") or "not specified"
    structured = profile.get("structured_personalisation")

    activity_slots = "\n".join(
        f"  {i + 1}. {act.value}" for i, act in enumerate(_ACTIVITY_ORDER)
    )

    personalisation_block = _format_structured_personalisation(structured)

    return f"""
Lesson day:
  Course week: {topic_entry.week}
  Day in week: {topic_entry.day}
  Topic id: {topic_entry.topic_id}
  Communication goal: {topic_entry.communication_goal}
  Language focus (non-negotiable): {topic_entry.language_focus}
  Sub-skill focus: {topic_entry.sub_skill}
  Learner sub-level: {topic_entry.sub_level}/10

Learner profile:
  Interests: {interests}
  Goals: {goals}
  Native language: {native_language}

{personalisation_block}

You must produce evaluation_focuses for these 4 activity slots in exact order:
{activity_slots}

For teacher_instructions:
- lesson_context: a single concrete setting (e.g. "tech-startup standup
  meeting" or "first-day-on-campus self-introduction") that fits BOTH the
  communication_goal and the learner's communication_contexts. If the
  personalisation is EMPTY/FALLBACK, pick a neutral everyday scenario
  appropriate to sub_level {topic_entry.sub_level}.
- vocabulary_domain: a short label for the lexical territory the lesson
  should pull words from. Tie to the learner's `domain` when concrete;
  otherwise pick a specific everyday domain.
- conversation_style: short tag matching the tone_preference (e.g.
  "casual peer-to-peer", "professional but warm", "academic"). Default to
  neutral when no personalisation exists.
- learning_goal: one specific outcome the learner should reach today.
- teaching_approach: concrete tactics for this sub-level (sentence length
  limits, what to demonstrate, what to avoid). Language_focus must show
  up in the patterns to demonstrate.
- concept_check_focus: the small check question the Teacher should ask
  before the task. Phrase it as a practical scenario, not a textbook
  definition question.
- do_not_reveal: task-specific things the Teacher must not say.
- words_to_cover: 8-10 concrete examples (words/phrases/patterns) for
  vocabulary and pronunciation days. For other days, leave the list short
  or empty and put examples in teaching_approach.

For each evaluation_focus:
- focus_areas: 1-3 short tags describing what to assess in that activity.
- level_note: explicit guidance tied to sub_level {topic_entry.sub_level}.
- scoring_instruction: how to convert performance into a score at this level.

Return only the structured JSON.
""".strip()


# ─────────────────────────────────────────────────────────────
# Deterministic activity assembly (no LLM)
# ─────────────────────────────────────────────────────────────


def _build_deterministic_activities(
    *,
    sub_skill: str,
    evaluation_focuses: list[EvaluationFocus],
) -> list[dict[str, Any]]:
    """Assemble the 4 activity blocks from the templates registry.

    Pure function. No LLM. Caller supplies the 4 evaluation_focus blocks in
    read/write/listen/speak order (matches `_ACTIVITY_ORDER`).
    """
    if len(evaluation_focuses) != 4:
        raise ValueError("evaluation_focuses must contain exactly 4 entries")

    sub_skill_enum = _resolve_sub_skill(sub_skill)
    activities: list[dict[str, Any]] = []

    for index, activity in enumerate(_ACTIVITY_ORDER):
        template = get_full_template(sub_skill_enum, activity)
        widget = TEMPLATE_TO_WIDGET[template.output_model_name]
        focus = evaluation_focuses[index]
        activities.append({
            "order": index + 1,
            "activity": activity.value,
            "template_id": template.template_id,
            "widget": widget.value,
            "evaluation_method": template.scoring_method.value,
            "evaluation_focus": focus.model_dump(),
        })

    return activities


def _fallback_llm_output(topic_entry: CourseTopic) -> PlannerLLMOutput:
    """Conservative defaults so the session can still run if the LLM fails.

    The fallback keeps the new lesson_context / vocabulary_domain /
    conversation_style fields populated so downstream agents always read
    a complete object.
    """
    generic_focus = EvaluationFocus(
        focus_areas=["task completion"],
        level_note="Use level-appropriate, encouraging defaults.",
        scoring_instruction=(
            "Score based on whether the learner completed the task with "
            "reasonable accuracy."
        ),
    )
    return PlannerLLMOutput(
        teacher_instructions=TeacherInstructions(
            sub_skill_context="Introduce the topic gently and keep examples simple.",
            learning_goal=f"Make progress on: {topic_entry.communication_goal}.",
            words_to_cover=None,
            teaching_approach=(
                "Use short sentences and one example at a time. Check "
                "understanding before the task."
            ),
            concept_check_focus=(
                "Ask one simple practical question that confirms the learner "
                "got the main idea."
            ),
            do_not_reveal=(
                "Do not reveal the exact items, blanks, or answers from the "
                "upcoming practice task."
            ),
            lesson_context="an everyday situation the learner is likely to face",
            vocabulary_domain="everyday English",
            conversation_style="neutral and encouraging",
        ),
        evaluation_focuses=[generic_focus, generic_focus, generic_focus, generic_focus],
    )


# ─────────────────────────────────────────────────────────────
# Planner Agent
# ─────────────────────────────────────────────────────────────


class PlannerAgent:
    def __init__(self, *, temperature: float = 0.4) -> None:
        self._llm = get_default_llm_client()
        self._temperature = temperature

    async def generate(
        self,
        *,
        user_id: int,
        course_slug: str,
        topic_entry: CourseTopic,
        learner_profile: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        user_prompt = _build_planner_prompt(
            topic_entry=topic_entry,
            learner_profile=learner_profile or {},
        )

        try:
            llm_output = await self._llm.generate_structured(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                output_model=PlannerLLMOutput,
                temperature=self._temperature,
            )
        except Exception:
            logger.exception("PlannerAgent LLM call failed; using fallback plan")
            llm_output = _fallback_llm_output(topic_entry)

        activities = _build_deterministic_activities(
            sub_skill=topic_entry.sub_skill,
            evaluation_focuses=llm_output.evaluation_focuses,
        )

        return {
            "user_id": user_id,
            "course_slug": course_slug,
            "week": topic_entry.week,
            "day": topic_entry.day,
            "topic_id": topic_entry.topic_id,
            "topic_name": topic_entry.display_label,
            "communication_goal": topic_entry.communication_goal,
            "language_focus": topic_entry.language_focus,
            "sub_skill": topic_entry.sub_skill,
            "sub_level": topic_entry.sub_level,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "teacher_instructions": llm_output.teacher_instructions.model_dump(),
            "activities": activities,
        }


async def generate_daily_plan(
    *,
    user_id: int,
    course_slug: str,
    topic_entry: CourseTopic,
    learner_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Public entry point — produce the full DailyPlan contract JSON."""
    agent = PlannerAgent()
    return await agent.generate(
        user_id=user_id,
        course_slug=course_slug,
        topic_entry=topic_entry,
        learner_profile=learner_profile,
    )
