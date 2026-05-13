"""Planner Agent - produces a structured DailyPlan once per day.

Runs lazily on the first session open for a given (user, course, week, day).
Downstream agents (Teacher, Task Generator, Evaluator) all read from the
plan so they share one level-aware view of the day.

What the LLM generates here:
  1. teacher_instructions   - rich context the Teacher Agent needs
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

Your job: Given a daily lesson topic and learner profile, produce:
1. Rich teacher_instructions - context the Teacher Agent needs to run an
   effective lesson (not just the topic name).
2. evaluation_focus for each of the 4 activities (read, write, listen, speak)
   in that exact order - level-aware scoring guidance for the Evaluation
   Agent.

Rules:
- teacher_instructions must be specific to this sub_skill, topic, and sub_level.
- evaluation_focus must reflect what a learner at this exact sub_level should
  be assessed on - be lenient for beginners (1-3), balanced for intermediate
  (4-6), rigorous for advanced (7-10).
- do_not_reveal must list what the teacher should NOT say (to avoid leaking
  task answers).
- Return only the structured JSON. No commentary.
""".strip()


def _build_planner_prompt(
    *,
    topic_entry: CourseTopic,
    learner_profile: dict[str, Any],
) -> str:
    profile = learner_profile or {}
    interests = profile.get("interests") or "not specified"
    goals = profile.get("primary_goals") or profile.get("goal") or "general English"
    personalisation = profile.get("personalisation_context") or "none"
    native_language = profile.get("native_language") or "not specified"

    activity_slots = "\n".join(
        f"  {i + 1}. {act.value}" for i, act in enumerate(_ACTIVITY_ORDER)
    )

    return f"""
Lesson day:
  Course week: {topic_entry.week}
  Day in week: {topic_entry.day}
  Topic id: {topic_entry.topic_id}
  Topic: {topic_entry.topic_name}
  Sub-skill focus: {topic_entry.sub_skill}
  Learner sub-level: {topic_entry.sub_level}/10

Learner profile:
  Interests: {interests}
  Goals: {goals}
  Native language: {native_language}
  Personalisation notes: {personalisation}

You must produce evaluation_focuses for these 4 activity slots in exact order:
{activity_slots}

For teacher_instructions:
- Pick 8-10 concrete examples (words, phrases, or patterns) appropriate to
  this topic and sub-level. Populate words_to_cover with them when the
  sub-skill is vocabulary/pronunciation; otherwise leave the list short or
  empty and put examples inside teaching_approach.
- learning_goal should be one specific outcome the learner should reach.
- teaching_approach should give the Teacher Agent concrete tactics for this
  sub-level (sentence length limits, what to avoid, what to demonstrate).
- concept_check_focus describes the small check question the Teacher should
  ask before the task starts.
- do_not_reveal lists task-specific things the Teacher should not say.

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


def _fallback_llm_output() -> PlannerLLMOutput:
    """Conservative defaults so the session can still run if the LLM fails."""
    generic_focus = EvaluationFocus(
        focus_areas=["task completion"],
        level_note="Use level-appropriate, encouraging defaults.",
        scoring_instruction="Score based on whether the learner completed the task with reasonable accuracy.",
    )
    return PlannerLLMOutput(
        teacher_instructions=TeacherInstructions(
            sub_skill_context="Introduce the topic gently and keep examples simple.",
            learning_goal="Help the learner make progress on today's topic.",
            words_to_cover=None,
            teaching_approach="Use short sentences and one example at a time. Check understanding before the task.",
            concept_check_focus="Ask one simple question that confirms the learner understood the main idea.",
            do_not_reveal="Do not reveal the exact items, blanks, or answers from the upcoming practice task.",
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
            llm_output = _fallback_llm_output()

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
            "topic_name": topic_entry.topic_name,
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
