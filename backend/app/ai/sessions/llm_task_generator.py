"""LLM-driven `TaskGenerator` implementation for the sessions flow.

Phase 4 MVP: ONE parameterized prompt produces a content payload sized
to the user's CEFR + sub_level. The payload carries the base fields the
frontend widget shell relies on plus a `primary_text` field with the
substantive content (passage / prompt / script / spoken prompt).

Phase 5+ can replace per-archetype with bespoke prompts that emit
archetype-specific shapes (MCQ items, fill-in-blanks, etc.).
"""

from __future__ import annotations

import json
import logging
import time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.ai.llm.exceptions import LLMError
from app.ai.llm.interface import ILLMClient
from app.ai.sessions.prompts import (
    build_task_gen_user_prompt,
    task_gen_system_prompt,
)
from app.modules.sessions.task_generator import (
    GeneratedTask,
    StubTaskGenerator,
    authored_fill_in_blanks_content,
    authored_listen_and_respond_content,
    build_simple_present_open_text_content,
    build_simple_present_speak_and_record_content,
    build_past_error_spotting_content,
    build_past_listening_cloze_content,
    build_past_error_correction_content,
    is_valid_error_spotting_payload,
    is_valid_listening_payload,
    is_valid_open_text_payload,
    is_valid_speak_and_record_payload,
    is_valid_error_correction_payload,
    normalize_error_spotting_payload,
    normalize_fill_in_blanks_payload,
    normalize_listen_and_respond_payload,
    normalize_open_text_payload,
    normalize_speak_and_record_payload,
    normalize_error_correction_payload,
)
from app.modules.sessions.widget_mapping import normalize_widget_key
from app.scoring import ArchetypeSpec
from app.tasks.schemas import FillInBlanksTask


logger = logging.getLogger(__name__)


def _agent_debug_log(message: str, data: dict, hypothesis_id: str) -> None:
    # region agent log
    try:
        with open("/Users/orbin/Documents/GitHub/ai-english-tutor/.cursor/debug-dfa507.log", "a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "sessionId": "dfa507",
                "runId": "initial",
                "hypothesisId": hypothesis_id,
                "location": "backend/app/ai/sessions/llm_task_generator.py",
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000),
            }, default=str) + "\n")
    except Exception:
        pass
    # endregion


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


class ErrorCorrectionItem(BaseModel):
    item_id: str
    incorrect_sentence: str
    sample_answer: str
    watch_hints: list[str] = Field(default_factory=list)


class ErrorCorrectionTask(BaseModel):
    model_config = ConfigDict(extra="allow")

    topic: str
    instructions: str
    task_intro: str
    estimated_time_minutes: int | None = None
    items: list[ErrorCorrectionItem] = Field(min_length=3, max_length=3)


ErrorSpottingType = Literal[
    "irregular_past",
    "missing_past_auxiliary",
    "passive_helper_missing",
    "time_marker_mismatch",
    "object_or_complement_mismatch",
    "past_participle_form",
    "regular_past_ending",
]


class ErrorSpottingToken(BaseModel):
    token_id: str
    text: str
    is_error: bool = False


class ErrorSpottingError(BaseModel):
    token_id: str
    incorrect_phrase: str
    correction: str
    error_type: ErrorSpottingType
    rule: str
    explanation: str


class ErrorSpottingSentence(BaseModel):
    sentence_id: str
    tokens: list[ErrorSpottingToken] = Field(min_length=1)
    error: ErrorSpottingError

    @model_validator(mode="after")
    def validate_single_error_token(self) -> "ErrorSpottingSentence":
        error_tokens = [token.token_id for token in self.tokens if token.is_error]
        if len(error_tokens) != 1:
            raise ValueError("each sentence must mark exactly one error token")
        if self.error.token_id not in error_tokens:
            raise ValueError("error.token_id must match the marked error token")
        return self


class ErrorSpottingTask(BaseModel):
    """Strict LLM-side schema for word-level error spotting."""

    model_config = ConfigDict(extra="allow")

    topic: str
    instructions: str
    task_intro: str
    primary_text: str = ""
    estimated_time_minutes: int | None = None
    passage_sentences: list[ErrorSpottingSentence] = Field(min_length=5, max_length=5)
    total_errors: int = 5

    @model_validator(mode="after")
    def validate_five_diverse_errors(self) -> "ErrorSpottingTask":
        if self.total_errors != 5:
            raise ValueError("total_errors must be exactly 5")
        categories = {sentence.error.error_type for sentence in self.passage_sentences}
        if len(categories) < 4:
            raise ValueError("use at least four distinct past-tense error categories")
        return self


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
        spec_dict = task_spec or {}
        authored_payload = (
            authored_fill_in_blanks_content(spec_dict)
            if archetype.ui_widget == "FillInBlanks"
            else None
        )
        if authored_payload is not None:
            return GeneratedTask(
                content={
                    "phase": "authored",
                    "archetype_id": archetype.archetype_id,
                    "archetype_name": archetype.name,
                    "ui_widget": archetype.ui_widget,
                    "widget": normalize_widget_key(archetype.ui_widget),
                    "core_activity": archetype.core_activity,
                    "topic": spec_dict.get("topic_override") or day_topic,
                    "explanation_brief": explanation_brief,
                    "cefr_level": cefr_level,
                    "sub_level": sub_level,
                    **authored_payload,
                }
            )

        authored_listening_payload = (
            authored_listen_and_respond_content(spec_dict)
            if self._is_listening_task(archetype)
            else None
        )
        if authored_listening_payload is not None:
            content = {
                "phase": "authored",
                "archetype_id": archetype.archetype_id,
                "archetype_name": archetype.name,
                "ui_widget": archetype.ui_widget,
                "widget": normalize_widget_key(archetype.ui_widget),
                "core_activity": archetype.core_activity,
                "topic": spec_dict.get("topic_override") or day_topic,
                "explanation_brief": explanation_brief,
                "cefr_level": cefr_level,
                "sub_level": sub_level,
                **authored_listening_payload,
            }
            content = normalize_listen_and_respond_payload(content)
            content = await self._attach_required_audio(
                content=content,
                archetype=archetype,
            )
            return GeneratedTask(content=content)

        if self._is_error_spotting_task(archetype):
            output_model: type[BaseModel] = ErrorSpottingTask
        elif archetype.ui_widget == "ErrorCorrection":
            output_model = ErrorCorrectionTask
        elif archetype.ui_widget == "FillInBlanks":
            output_model = FillInBlanksTask
        else:
            output_model = TaskGenOutput
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
                output_model=output_model,
                temperature=self.temperature,
            )
            generated_payload = output.model_dump(exclude_none=True)
            generated_payload.update(output.model_extra or {})
            if archetype.ui_widget == "FillInBlanks":
                generated_payload = FillInBlanksTask.model_validate(
                    generated_payload
                ).model_dump(exclude_none=True)
                generated_payload = normalize_fill_in_blanks_payload(generated_payload)
            if archetype.ui_widget == "ErrorCorrection":
                generated_payload = ErrorCorrectionTask.model_validate(
                    generated_payload
                ).model_dump(exclude_none=True)
                generated_payload = normalize_error_correction_payload(generated_payload)
            if self._is_error_spotting_task(archetype):
                generated_payload = ErrorSpottingTask.model_validate(
                    generated_payload
                ).model_dump(exclude_none=True)
                generated_payload = normalize_error_spotting_payload(generated_payload)
        except (LLMError, ValidationError, ValueError) as exc:
            logger.warning(
                "LLM task generator failed for archetype=%s: %s — using stub content",
                archetype.archetype_id, exc,
            )
            fallback_content = await self._fallback_content(
                archetype=archetype,
                day_topic=day_topic,
                explanation_brief=explanation_brief,
                cefr_level=cefr_level,
                sub_level=sub_level,
                user_interests=user_interests,
                task_spec=task_spec,
            )
            return GeneratedTask(content=fallback_content)

        content = {
            **generated_payload,
            "phase": "live",
            "archetype_id": archetype.archetype_id,
            "archetype_name": archetype.name,
            "ui_widget": archetype.ui_widget,
            "widget": normalize_widget_key(archetype.ui_widget),
            "core_activity": archetype.core_activity,
            "explanation_brief": explanation_brief,
            "cefr_level": cefr_level,
            "sub_level": sub_level,
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

        if self._is_open_text_writing_task(archetype):
            content = normalize_open_text_payload(content)
            if not is_valid_open_text_payload(content, expected_items=3):
                logger.warning(
                    "Invalid open-text payload for archetype=%s — using stub content",
                    archetype.archetype_id,
                )
                content = await self._fallback_content(
                    archetype=archetype,
                    day_topic=day_topic,
                    explanation_brief=explanation_brief,
                    cefr_level=cefr_level,
                    sub_level=sub_level,
                    user_interests=user_interests,
                    task_spec=task_spec,
                )
        elif self._is_speak_and_record_task(archetype):
            raw_prompts = generated_payload.get("speaking_prompts")
            raw_samples = generated_payload.get("sample_responses")
            logger.info(
                "speak_and_record LLM output: prompts=%d samples=%d "
                "task_intro=%r instructions_len=%d",
                len(raw_prompts) if isinstance(raw_prompts, list) else -1,
                len(raw_samples) if isinstance(raw_samples, list) else -1,
                (generated_payload.get("task_intro") or "")[:60],
                len(str(generated_payload.get("instructions") or "")),
            )
            content = normalize_speak_and_record_payload(content)
            valid = is_valid_speak_and_record_payload(content)
            logger.info(
                "speak_and_record after normalize: valid=%s prompts=%d samples=%d "
                "task_intro=%r",
                valid,
                len(content.get("speaking_prompts") or []),
                len(content.get("sample_responses") or []),
                (content.get("task_intro") or "")[:60],
            )
            if not valid:
                logger.warning(
                    "Invalid speak-and-record payload for archetype=%s — using stub content",
                    archetype.archetype_id,
                )
                content = await self._fallback_content(
                    archetype=archetype,
                    day_topic=day_topic,
                    explanation_brief=explanation_brief,
                    cefr_level=cefr_level,
                    sub_level=sub_level,
                    user_interests=user_interests,
                    task_spec=task_spec,
                )
                logger.info(
                    "speak_and_record fallback applied: prompts=%d task_intro=%r",
                    len(content.get("speaking_prompts") or []),
                    (content.get("task_intro") or "")[:60],
                )
        if archetype.ui_widget == "ErrorCorrection":
            content = normalize_error_correction_payload(content)
            if not is_valid_error_correction_payload(content, expected_items=3):
                logger.warning(
                    "Invalid error-correction payload for archetype=%s — using stub content",
                    archetype.archetype_id,
                )
                content = await self._fallback_content(
                    archetype=archetype,
                    day_topic=day_topic,
                    explanation_brief=explanation_brief,
                    cefr_level=cefr_level,
                    sub_level=sub_level,
                    user_interests=user_interests,
                    task_spec=task_spec,
                )
        elif self._is_error_spotting_task(archetype):
            content = normalize_error_spotting_payload(content)
            if not is_valid_error_spotting_payload(content):
                logger.warning(
                    "Invalid error-spotting payload for archetype=%s — using stub content",
                    archetype.archetype_id,
                )
                content = await self._fallback_content(
                    archetype=archetype,
                    day_topic=day_topic,
                    explanation_brief=explanation_brief,
                    cefr_level=cefr_level,
                    sub_level=sub_level,
                    user_interests=user_interests,
                    task_spec=task_spec,
                )
        elif self._is_listening_task(archetype):
            content = normalize_listen_and_respond_payload(content)
            if not is_valid_listening_payload(content):
                logger.warning(
                    "Invalid listening payload for archetype=%s — using stub content",
                    archetype.archetype_id,
                )
                content = await self._fallback_content(
                    archetype=archetype,
                    day_topic=day_topic,
                    explanation_brief=explanation_brief,
                    cefr_level=cefr_level,
                    sub_level=sub_level,
                    user_interests=user_interests,
                    task_spec=task_spec,
                )
            else:
                content = await self._attach_required_audio(
                    content=content,
                    archetype=archetype,
                )
        elif content.get("audio_script") and not content.get("audio_url"):
            content = await self._attach_optional_audio(
                content=content,
                archetype=archetype,
            )

        return GeneratedTask(content=content)

    async def _fallback_content(
        self,
        *,
        archetype: ArchetypeSpec,
        day_topic: str,
        explanation_brief: str,
        cefr_level: str,
        sub_level: int,
        user_interests: list[str] | None,
        task_spec: dict | None,
    ) -> dict:
        fallback = await self._fallback.generate(
            archetype=archetype,
            day_topic=day_topic,
            explanation_brief=explanation_brief,
            cefr_level=cefr_level,
            sub_level=sub_level,
            user_interests=user_interests,
            task_spec=task_spec,
        )
        content = dict(fallback.content)
        if self._is_open_text_writing_task(archetype):
            content = normalize_open_text_payload(content)
            if not is_valid_open_text_payload(content, expected_items=3):
                content.update(
                    build_simple_present_open_text_content(
                        str(content.get("topic") or day_topic)
                    )
                )
                content = normalize_open_text_payload(content)
        if self._is_speak_and_record_task(archetype):
            content = normalize_speak_and_record_payload(content)
            if not is_valid_speak_and_record_payload(content):
                content.update(
                    build_simple_present_speak_and_record_content(
                        str(content.get("topic") or day_topic)
                    )
                )
                content = normalize_speak_and_record_payload(content)
        if self._is_error_spotting_task(archetype):
            content = normalize_error_spotting_payload(content)
            if not is_valid_error_spotting_payload(content):
                content.update(
                    build_past_error_spotting_content(
                        str(content.get("topic") or day_topic)
                    )
                )
                content = normalize_error_spotting_payload(content)
        if archetype.ui_widget == "ErrorCorrection":
            content = normalize_error_correction_payload(content)
            if not is_valid_error_correction_payload(content):
                content.update(
                    build_past_error_correction_content(
                        str(content.get("topic") or day_topic)
                    )
                )
                content = normalize_error_correction_payload(content)
        if self._is_listening_task(archetype):
            content = normalize_listen_and_respond_payload(content)
            if not is_valid_listening_payload(content):
                if archetype.archetype_id == "LISTEN_CLOZE":
                    content.update(
                        build_past_listening_cloze_content(
                            str(content.get("topic") or day_topic)
                        )
                    )
                    content = normalize_listen_and_respond_payload(content)
                if not is_valid_listening_payload(content):
                    raise ValueError(
                        f"Fallback listening payload is invalid for {archetype.archetype_id}"
                    )
            content = await self._attach_required_audio(
                content=content,
                archetype=archetype,
            )
        return content

    async def _attach_optional_audio(
        self,
        *,
        content: dict,
        archetype: ArchetypeSpec,
    ) -> dict:
        try:
            return await self._attach_audio(content=content)
        except Exception as exc:
            logger.warning(
                "TTS synthesis failed for archetype=%s: %s — audio_url will be null",
                archetype.archetype_id, exc,
            )
            return content

    async def _attach_required_audio(
        self,
        *,
        content: dict,
        archetype: ArchetypeSpec,
    ) -> dict:
        if content.get("audio_url"):
            _agent_debug_log(
                "Required audio already present",
                {
                    "archetype_id": archetype.archetype_id,
                    "audio_url": content.get("audio_url"),
                    "browser_tts_fallback": content.get("browser_tts_fallback"),
                    "audio_script_len": len(str(content.get("audio_script") or "")),
                    "items_len": len(content.get("items") or []),
                },
                "H1",
            )
            return content
        try:
            updated = await self._attach_audio(content=content)
            _agent_debug_log(
                "Required TTS synthesis succeeded",
                {
                    "archetype_id": archetype.archetype_id,
                    "audio_url": updated.get("audio_url"),
                    "duration": updated.get("audio_duration_seconds"),
                    "audio_script_len": len(str(updated.get("audio_script") or "")),
                    "items_len": len(updated.get("items") or []),
                },
                "H1",
            )
            return updated
        except Exception as exc:
            logger.exception(
                "Required TTS synthesis failed for archetype=%s",
                archetype.archetype_id,
            )
            fallback = dict(content)
            fallback["audio_url"] = None
            fallback["audio_duration_seconds"] = max(
                1,
                int(round(len(str(fallback.get("audio_script") or "").split()) / 2.3)),
            )
            fallback["browser_tts_fallback"] = True
            fallback["tts_error"] = (
                f"Could not synthesize listening audio for {archetype.archetype_id}"
            )
            _agent_debug_log(
                "Required TTS synthesis failed; using browser fallback",
                {
                    "archetype_id": archetype.archetype_id,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "browser_tts_fallback": fallback.get("browser_tts_fallback"),
                    "audio_script_len": len(str(fallback.get("audio_script") or "")),
                    "items_len": len(fallback.get("items") or []),
                },
                "H1,H2",
            )
            return fallback

    @staticmethod
    async def _attach_audio(*, content: dict) -> dict:
        audio_script = str(content.get("audio_script") or "").strip()
        if not audio_script:
            raise ValueError("audio_script is required for TTS synthesis")
        from app.ai.tts import get_default_tts_service

        tts = get_default_tts_service()
        result = await tts.synthesize(text=audio_script)
        updated = dict(content)
        updated["audio_url"] = result["audio_url"]
        updated["audio_duration_seconds"] = int(result["duration_seconds"])
        return updated

    @staticmethod
    def _is_listening_task(archetype: ArchetypeSpec) -> bool:
        return archetype.core_activity == "listen"

    @staticmethod
    def _is_open_text_writing_task(archetype: ArchetypeSpec) -> bool:
        return archetype.archetype_id == "WRITE_OPEN_SENT"

    @staticmethod
    def _is_speak_and_record_task(archetype: ArchetypeSpec) -> bool:
        return (
            archetype.archetype_id == "SPEAK_TIMED"
            or archetype.ui_widget == "SpeakAndRecord"
        )

    @staticmethod
    def _is_error_spotting_task(archetype: ArchetypeSpec) -> bool:
        return (
            archetype.archetype_id == "READ_ERROR_SPOT"
            or archetype.ui_widget == "ErrorSpotting"
        )
