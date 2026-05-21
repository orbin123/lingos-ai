"""LLM-driven `TaskGenerator` implementation for the sessions flow.

Phase 4 MVP: ONE parameterized prompt produces a content payload sized
to the user's CEFR + sub_level. The payload carries the base fields the
frontend widget shell relies on plus a `primary_text` field with the
substantive content (passage / prompt / script / spoken prompt).

Phase 5+ can replace per-archetype with bespoke prompts that emit
archetype-specific shapes (MCQ items, fill-in-blanks, etc.).
"""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field

from app.ai.llm.exceptions import LLMError
from app.ai.llm.interface import ILLMClient
from app.ai.sessions.prompts import (
    build_task_gen_user_prompt,
    task_gen_system_prompt,
)
from app.modules.sessions.task_generator import GeneratedTask, StubTaskGenerator
from app.scoring import ArchetypeSpec


logger = logging.getLogger(__name__)

# Map archetype ui_widget values to the frontend WidgetKey enum so the
# LangGraph task_delivery_node can dispatch to the right React component.
_WIDGET_KEY: dict[str, str] = {
    "FillInBlanks": "fill_in_blanks",
    "MCQList": "mcq",
    "ListenAndAnswer+MCQList": "listen_and_respond",
    "ListenAndAnswer+FillInBlanks": "listen_and_respond",
    "ListenAndAnswer+OpenTextList": "listen_and_respond",
    "ListenAndAnswer+SpeakAndRecord": "listen_and_respond",
    "SpeakAndRecord": "speak_and_record",
    "Storyboard": "storyboard",
    "StructuredEssay": "structured_essay",
    "OpenTextList": "open_text",
    "SentenceTransform": "open_text",
    "ErrorCorrection": "open_text",
    "TimedText": "timed_text",
}


class TaskGenOutput(BaseModel):
    """LLM-side schema for one generated task."""

    topic: str
    instructions: str
    primary_text: str
    target_words: list[str] = Field(default_factory=list)


class LLMTaskGenerator:
    """Production `TaskGenerator` — invokes the LLM, validates output, falls
    back to the stub on failure."""

    def __init__(self, llm: ILLMClient, *, temperature: float | None = 0.7) -> None:
        self.llm = llm
        self.temperature = temperature
        self._fallback = StubTaskGenerator()

    async def generate(
        self,
        *,
        archetype: ArchetypeSpec,
        day_topic: str,
        explanation_brief: str,
        cefr_level: str,
        sub_level: int,
        user_interests: list[str] | None = None,
    ) -> GeneratedTask:
        try:
            output = await self.llm.generate_structured(
                system_prompt=task_gen_system_prompt(),
                user_prompt=build_task_gen_user_prompt(
                    archetype=archetype,
                    day_topic=day_topic,
                    explanation_brief=explanation_brief,
                    cefr_level=cefr_level,
                    sub_level=sub_level,
                    user_interests=user_interests,
                ),
                output_model=TaskGenOutput,
                temperature=self.temperature,
            )
        except LLMError as exc:
            logger.warning(
                "LLM task generator failed for archetype=%s: %s — using stub content",
                archetype.archetype_id, exc,
            )
            return await self._fallback.generate(
                archetype=archetype,
                day_topic=day_topic,
                explanation_brief=explanation_brief,
                cefr_level=cefr_level,
                sub_level=sub_level,
                user_interests=user_interests,
            )

        content = {
            "phase": "live",
            "archetype_id": archetype.archetype_id,
            "archetype_name": archetype.name,
            "ui_widget": archetype.ui_widget,
            "widget": _WIDGET_KEY.get(archetype.ui_widget, archetype.ui_widget),
            "core_activity": archetype.core_activity,
            "topic": output.topic,
            "explanation_brief": explanation_brief,
            "instructions": output.instructions,
            "primary_text": output.primary_text,
            "target_words": list(output.target_words),
            "cefr_level": cefr_level,
            "sub_level": sub_level,
        }
        return GeneratedTask(content=content)
