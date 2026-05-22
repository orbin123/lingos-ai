"""Compatibility entry point for task generation agents."""

from __future__ import annotations

from app.ai.llm import get_default_llm_client
from app.ai.sessions.llm_task_generator import LLMTaskGenerator
from app.modules.sessions.task_generator import GeneratedTask
from app.scoring import ArchetypeSpec


async def generate_task(
    *,
    archetype: ArchetypeSpec,
    day_topic: str,
    explanation_brief: str,
    cefr_level: str,
    sub_level: int,
    user_interests: list[str] | None = None,
    task_spec: dict | None = None,
) -> GeneratedTask:
    """Generate one activity payload through the sessions task generator.

    This keeps the older ``app.ai.agents`` import surface alive while the
    production session flow uses the newer ``app.ai.sessions`` generator stack.
    """

    generator = LLMTaskGenerator(get_default_llm_client())
    return await generator.generate(
        archetype=archetype,
        day_topic=day_topic,
        explanation_brief=explanation_brief,
        cefr_level=cefr_level,
        sub_level=sub_level,
        user_interests=user_interests,
        task_spec=task_spec,
    )
