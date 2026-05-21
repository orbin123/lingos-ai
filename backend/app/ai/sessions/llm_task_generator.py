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

from pydantic import BaseModel, ConfigDict, Field

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

    model_config = ConfigDict(extra="allow")

    topic: str
    instructions: str
    primary_text: str = ""
    target_words: list[str] = Field(default_factory=list)
    task_intro: str | None = None
    estimated_time_minutes: int | None = None

    # Widget-specific fields. `extra="allow"` lets richer future widgets pass
    # through without changing the authoring service.
    items: list[dict] = Field(default_factory=list)
    blanks: list[dict] = Field(default_factory=list)
    passage: str | None = None
    passage_title: str | None = None
    grammar_rule_explained: str | None = None
    audio_script: str | None = None
    audio_url: str | None = None
    audio_duration_seconds: int | None = None
    inner_widget: str | None = None
    speaking_duration_seconds: int | None = None
    speaking_prompt: str | None = None
    speaking_prompts: list[str] = Field(default_factory=list)
    sample_response: str | None = None
    sample_responses: list[str] = Field(default_factory=list)


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
        task_spec: dict | None = None,
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
                    task_spec=task_spec,
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
                task_spec=task_spec,
            )

        generated_payload = output.model_dump(exclude_none=True)
        generated_payload.update(output.model_extra or {})
        content = {
            "phase": "live",
            "archetype_id": archetype.archetype_id,
            "archetype_name": archetype.name,
            "ui_widget": archetype.ui_widget,
            "widget": _WIDGET_KEY.get(archetype.ui_widget, archetype.ui_widget),
            "core_activity": archetype.core_activity,
            "explanation_brief": explanation_brief,
            "cefr_level": cefr_level,
            "sub_level": sub_level,
            **generated_payload,
        }
        if task_spec:
            if task_spec.get("task_intro") and not content.get("task_intro"):
                content["task_intro"] = task_spec["task_intro"]
            if task_spec.get("estimated_time_minutes") and not content.get(
                "estimated_time_minutes"
            ):
                content["estimated_time_minutes"] = task_spec[
                    "estimated_time_minutes"
                ]
        return GeneratedTask(content=content)
