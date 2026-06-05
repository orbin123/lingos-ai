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
from app.ai.sessions.exceptions import TaskGenerationFailed
from app.ai.sessions.prompts import (
    build_task_gen_user_prompt,
    task_gen_system_prompt,
)
from app.modules.sessions.task_generator import (
    GeneratedTask,
    authored_error_spotting_content,
    authored_fill_in_blanks_content,
    authored_listen_and_respond_content,
    is_valid_error_spotting_payload,
    is_valid_listening_payload,
    is_valid_open_text_payload,
    is_valid_speak_and_record_payload,
    is_valid_error_correction_payload,
    is_valid_dialogue_speaking_payload,
    is_valid_interview_speaking_payload,
    is_valid_task_content,
    normalize_mcq_payload,
    normalize_interview_speaking_payload,
    normalize_error_spotting_payload,
    normalize_fill_in_blanks_payload,
    normalize_listen_and_respond_payload,
    normalize_listen_retell_payload,
    normalize_open_text_payload,
    normalize_speak_and_record_payload,
    normalize_speak_pic_desc_payload,
    normalize_dialogue_speaking_payload,
    normalize_error_correction_payload,
    normalize_read_aloud_payload,
    is_valid_read_aloud_payload,
    normalize_read_structure_payload,
    is_valid_read_structure_payload,
    normalize_sentence_transform_payload,
    is_valid_sentence_transform_payload,
)
from app.modules.sessions.widget_mapping import normalize_widget_key
from app.scoring import ArchetypeSpec
from app.tasks.schemas import FillInBlanksTask
from app.tasks.schemas.llm_output_schemas import FillInBlanksTaskLLM


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


class _TaskContentInvalid(Exception):
    """Internal: a generated payload failed its archetype validation.

    Used to trigger a retry inside ``LLMTaskGenerator.generate``; never escapes
    the module (the retry loop converts it to ``TaskGenerationFailed``).
    """


class TaskGenItem(BaseModel):
    """One activity item for generic (``TaskGenOutput``) structured generation."""

    model_config = ConfigDict(extra="forbid")

    item_id: str
    prompt: str | None = None
    sender: str | None = None
    message: str | None = None
    options: list[str] | None = None
    correct_index: int | None = None
    explanation: str | None = None
    correct_answer: str | None = None
    sample_answer: str | None = None
    answer_hints: list[str] | None = None
    sentence_with_blank: str | None = None
    base_verb: str | None = None
    distractors: list[str] | None = None
    grammar_rule: str | None = None
    source_sentence: str | None = None
    watch_hints: list[str] | None = None


class TaskGenDialogueTurn(BaseModel):
    """One turn in a roleplay/smalltalk dialogue."""

    model_config = ConfigDict(extra="forbid")

    role: str
    text: str
    speaker: Literal["partner", "learner"]


class TaskGenInterviewQuestion(BaseModel):
    """One question in a mini-interview speaking task (SPEAK_INTERVIEW)."""

    model_config = ConfigDict(extra="forbid")

    item_id: str | None = None
    interviewer_prompt: str
    sample_answer: str = ""
    answer_hint: str = ""


class TaskGenOutput(BaseModel):
    """LLM-side schema for one generated task."""

    model_config = ConfigDict(extra="forbid")

    topic: str
    instructions: str
    primary_text: str = ""
    target_words: list[str] = Field(default_factory=list)
    task_intro: str | None = None
    estimated_time_minutes: int | None = None

    items: list[TaskGenItem] = Field(default_factory=list)
    blanks: list[TaskGenItem] = Field(default_factory=list)
    passage: str | None = None
    passage_title: str | None = None
    grammar_rule_explained: str | None = None
    grammar_rule_to_practice: str | None = None
    common_mistakes: list[str] = Field(default_factory=list)
    audio_script: str | None = None
    audio_url: str | None = None
    audio_duration_seconds: int | None = None
    inner_widget: str | None = None
    speaking_duration_seconds: int | None = None
    text_to_read_aloud: str | None = None
    speaking_prompt: str | None = None
    speaking_prompts: list[str] = Field(default_factory=list)
    sample_response: str | None = None
    sample_responses: list[str] = Field(default_factory=list)
    passage_to_retell: str | None = None
    text_to_shadow: str | None = None
    image_alt: str | None = None
    dialogue_context: list[TaskGenDialogueTurn] = Field(default_factory=list)
    interview_context: str | None = None
    questions: list[TaskGenInterviewQuestion] = Field(default_factory=list)


class ErrorCorrectionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str
    incorrect_sentence: str
    sample_answer: str
    watch_hints: list[str] = Field(default_factory=list)


class ErrorCorrectionTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    model_config = ConfigDict(extra="forbid")

    token_id: str
    text: str
    is_error: bool = False


class ErrorSpottingError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token_id: str
    incorrect_phrase: str
    correction: str
    error_type: ErrorSpottingType
    rule: str
    explanation: str


class ErrorSpottingSentenceLLM(BaseModel):
    """Loose LLM output — ``is_error`` flags are synced in ``normalize_error_spotting_payload``."""

    model_config = ConfigDict(extra="forbid")

    sentence_id: str
    tokens: list[ErrorSpottingToken] = Field(min_length=1)
    error: ErrorSpottingError


class ErrorSpottingTaskLLM(BaseModel):
    """OpenAI structured-output schema for error spotting."""

    model_config = ConfigDict(extra="forbid")

    topic: str
    instructions: str
    task_intro: str
    primary_text: str = ""
    estimated_time_minutes: int | None = None
    passage_sentences: list[ErrorSpottingSentenceLLM] = Field(min_length=5, max_length=5)
    total_errors: int = 5


class ErrorSpottingSentence(BaseModel):
    model_config = ConfigDict(extra="forbid")

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

    model_config = ConfigDict(extra="forbid")

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
    """Production `TaskGenerator` — invokes the LLM and validates output.

    On a failed attempt it retries the LLM once; if the payload still fails
    validation it raises ``TaskGenerationFailed`` rather than substituting
    off-theme placeholder content."""

    def __init__(self, llm: ILLMClient, *, temperature: float | None = 0.7) -> None:
        self.llm = llm
        self.temperature = temperature

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

        authored_error_spotting_payload = (
            authored_error_spotting_content(spec_dict)
            if self._is_error_spotting_task(archetype)
            else None
        )
        if authored_error_spotting_payload is not None:
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
                    **authored_error_spotting_payload,
                }
            )

        last_exc: Exception | None = None
        for attempt_no in range(2):  # initial attempt + one retry
            try:
                content = await self._generate_once(
                    archetype=archetype,
                    day_topic=day_topic,
                    explanation_brief=explanation_brief,
                    cefr_level=cefr_level,
                    sub_level=sub_level,
                    user_interests=user_interests,
                    task_spec=task_spec,
                )
                return GeneratedTask(content=content)
            except (LLMError, ValidationError, ValueError, _TaskContentInvalid) as exc:
                last_exc = exc
                logger.warning(
                    "Task generation attempt %d/2 failed for archetype=%s: %s",
                    attempt_no + 1, archetype.archetype_id, exc,
                )

        raise TaskGenerationFailed(
            archetype.archetype_id,
            str(last_exc) if last_exc is not None else "unknown error",
        ) from last_exc

    async def _generate_once(
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
        """Run one full LLM generation attempt.

        Returns validated, render-ready task content, or raises (``LLMError`` /
        ``ValidationError`` / ``ValueError`` from the LLM call, or
        ``_TaskContentInvalid`` from payload validation) so the caller can retry
        and ultimately surface a clean error. Never substitutes placeholder
        content.
        """
        if self._is_error_spotting_task(archetype):
            output_model: type[BaseModel] = ErrorSpottingTaskLLM
        elif archetype.ui_widget == "ErrorCorrection":
            output_model = ErrorCorrectionTask
        elif archetype.ui_widget == "FillInBlanks":
            output_model = FillInBlanksTaskLLM
        else:
            output_model = TaskGenOutput

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
        if archetype.ui_widget == "SentenceTransform":
            generated_payload = normalize_sentence_transform_payload(generated_payload)
        if self._is_error_spotting_task(archetype):
            normalized = normalize_error_spotting_payload(generated_payload)
            strict_payload = {
                key: value for key, value in normalized.items() if key != "widget"
            }
            generated_payload = ErrorSpottingTask.model_validate(
                strict_payload
            ).model_dump(exclude_none=True)
            generated_payload = normalize_error_spotting_payload(generated_payload)

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
                raise _TaskContentInvalid(
                    f"open-text payload failed validation for {archetype.archetype_id}"
                )
        elif self._is_read_aloud_task(archetype):
            content = normalize_read_aloud_payload(content)
            if not is_valid_read_aloud_payload(content):
                raise _TaskContentInvalid(
                    f"read-aloud payload failed validation for {archetype.archetype_id}"
                )
        elif self._is_pic_desc_task(archetype):
            content = normalize_speak_pic_desc_payload(content)
            content = await self._attach_required_image(
                content=content,
                archetype=archetype,
            )
        elif self._is_dialogue_speaking_task(archetype):
            content = normalize_dialogue_speaking_payload(content)
            if not is_valid_dialogue_speaking_payload(content):
                raise _TaskContentInvalid(
                    f"dialogue-speaking payload failed validation for {archetype.archetype_id}"
                )
        elif self._is_speak_and_record_task(archetype):
            content = normalize_speak_and_record_payload(content)
            if not is_valid_speak_and_record_payload(content):
                raise _TaskContentInvalid(
                    f"speak-and-record payload failed validation for {archetype.archetype_id}"
                )
        elif self._is_interview_task(archetype):
            content = normalize_interview_speaking_payload(content)
            if not is_valid_interview_speaking_payload(content):
                raise _TaskContentInvalid(
                    f"interview-speaking payload failed validation for {archetype.archetype_id}"
                )
        if archetype.ui_widget == "ErrorCorrection":
            content = normalize_error_correction_payload(content)
            if not is_valid_error_correction_payload(content, expected_items=3):
                raise _TaskContentInvalid(
                    f"error-correction payload failed validation for {archetype.archetype_id}"
                )
        elif archetype.ui_widget == "SentenceTransform":
            content = normalize_sentence_transform_payload(content)
            if not is_valid_sentence_transform_payload(content, expected_items=3):
                raise _TaskContentInvalid(
                    f"sentence-transform payload failed validation for {archetype.archetype_id}"
                )
        elif self._is_error_spotting_task(archetype):
            content = normalize_error_spotting_payload(content)
            if not is_valid_error_spotting_payload(content):
                raise _TaskContentInvalid(
                    f"error-spotting payload failed validation for {archetype.archetype_id}"
                )
        elif self._is_read_structure_task(archetype):
            content = normalize_read_structure_payload(content)
            if not is_valid_read_structure_payload(content):
                raise _TaskContentInvalid(
                    f"read-structure payload failed validation for {archetype.archetype_id}"
                )
        elif self._is_listening_task(archetype):
            if archetype.archetype_id in {"LISTEN_RETELL", "LISTEN_SHADOW"}:
                content = normalize_listen_retell_payload(content)
            else:
                content = normalize_listen_and_respond_payload(content)
            if not is_valid_listening_payload(content):
                raise _TaskContentInvalid(
                    f"listening payload failed validation for {archetype.archetype_id}"
                )
            content = await self._attach_required_audio(
                content=content,
                archetype=archetype,
            )
        elif content.get("audio_script") and not content.get("audio_url"):
            content = await self._attach_optional_audio(
                content=content,
                archetype=archetype,
            )
        elif archetype.ui_widget == "MCQList":
            content = normalize_mcq_payload(content)
        elif archetype.ui_widget == "TrueFalseNotGiven":
            content = {**content, "widget": "true_false_not_given"}
        elif (
            archetype.ui_widget == "FillInBlanks"
            and archetype.core_activity == "read"
        ):
            content = normalize_fill_in_blanks_payload(content)

        if not is_valid_task_content(archetype.archetype_id, content):
            raise _TaskContentInvalid(
                f"task content failed validation for {archetype.archetype_id}"
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
    def _is_read_aloud_task(archetype: ArchetypeSpec) -> bool:
        return archetype.archetype_id == "SPEAK_READ_ALOUD"

    @staticmethod
    def _is_pic_desc_task(archetype: ArchetypeSpec) -> bool:
        return archetype.archetype_id == "SPEAK_PIC_DESC"

    @staticmethod
    def _is_dialogue_speaking_task(archetype: ArchetypeSpec) -> bool:
        return archetype.archetype_id in {"SPEAK_ROLEPLAY", "SPEAK_SMALLTALK"}

    @staticmethod
    def _is_speak_and_record_task(archetype: ArchetypeSpec) -> bool:
        return archetype.archetype_id == "SPEAK_TIMED"

    @staticmethod
    def _is_interview_task(archetype: ArchetypeSpec) -> bool:
        return archetype.archetype_id == "SPEAK_INTERVIEW"

    async def _attach_required_image(
        self,
        *,
        content: dict,
        archetype: ArchetypeSpec,
    ) -> dict:
        if content.get("image_url"):
            return content
        try:
            return await self._attach_image(content=content)
        except Exception as exc:
            logger.exception(
                "Required image generation failed for archetype=%s",
                archetype.archetype_id,
            )
            fallback = dict(content)
            fallback["image_url"] = None
            fallback["image_error"] = (
                f"Could not generate picture for {archetype.archetype_id}: {exc}"
            )
            return fallback

    @staticmethod
    async def _attach_image(*, content: dict) -> dict:
        image_alt = str(content.get("image_alt") or "").strip()
        if not image_alt:
            raise ValueError("image_alt is required for picture-description image generation")
        from app.ai.imagegen import get_default_imagegen_service

        service = get_default_imagegen_service()
        result = await service.generate(
            prompt=image_alt,
            aspect_ratio="landscape",
            style="clean educational illustration, simple everyday scene, no text or labels",
        )
        updated = dict(content)
        updated["image_url"] = result["image_url"]
        return updated

    @staticmethod
    def _is_error_spotting_task(archetype: ArchetypeSpec) -> bool:
        return (
            archetype.archetype_id == "READ_ERROR_SPOT"
            or archetype.ui_widget == "ErrorSpotting"
        )

    @staticmethod
    def _is_read_structure_task(archetype: ArchetypeSpec) -> bool:
        return archetype.archetype_id == "READ_STRUCTURE_ID"
