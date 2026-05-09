"""Agent 1 — Task Generator Agent.

Turns a TaskTemplate (prompt skeleton + Pydantic output schema) into a
fully-formed task tailored to one user's profile. Output is a validated
dict ready to be persisted as Task.content (JSONB).

Migrated from `app/ai/task_generator.py` to live alongside the other
two agents. Now uses `app.ai.llm` for all LLM access — gets retries,
LangSmith tracing, and unified error handling for free.

Public surface (the only thing callers should import):
    - TaskGeneratorAgent  : class with .generate(template, profile)
    - generate_task       : thin async wrapper for the 3-agent contract
"""

from __future__ import annotations

import logging
import re

from app.ai.llm import LLMError, get_default_llm_client
from app.ai.llm.exceptions import LLMValidationError
from app.tasks.schemas import ALL_OUTPUT_MODELS
from app.tasks.schemas.base import TaskTemplate, difficulty_tier_for_sublevel

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# System prompt — kept SHORT. The detailed instructions live in each
# template's `llm_prompt_template`. This system message just sets the
# agent's role and the "stay strict to the schema" rule.
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = (
    "You are a task content generator for an English learning app. "
    "You produce structured tasks that match the requested schema exactly. "
    "Use the EXACT field names defined in the schema. "
    "Do NOT include any explanation, markdown, or commentary — only the "
    "structured object."
)


class TaskGeneratorAgent:
    """Generate tasks by filling a TaskTemplate prompt and calling the LLM.

    Stateless — safe to instantiate per-request OR reuse as a singleton.
    Today we instantiate per-request inside TaskService for clarity;
    the cost is negligible because the LLM client is itself a singleton.
    """

    def __init__(
        self,
        *,
        model: str | None = None,
        temperature: float = 0.7,
    ) -> None:
        # We use the default shared client so every agent shares the
        # same retry policy, usage logging, and LangSmith trace context.
        # Per-call temperature override is supported via generate_structured.
        self._llm = get_default_llm_client()
        self._temperature = temperature
        # `model` arg kept for API compatibility but currently unused —
        # the default client picks the model. Plumbing per-agent model
        # selection through is a Phase 2+ concern.
        self._model_override = model

    async def generate(
        self,
        template: TaskTemplate,
        user_profile: dict,
    ) -> dict:
        """Generate one task from a template + user context.

        Args:
            template: The TaskTemplate defining the prompt and output
                schema.
            user_profile: Must include at minimum:
                - sub_level (int): 1–10
                - weak_areas (str): comma-separated weak grammar areas
                - course_topic (str): the curriculum topic of the day
                - topic (str): learner-facing context/theme fallback

        Returns:
            A dict (the validated Pydantic model dumped to a dict),
            ready to drop into Task.content.

        Raises:
            ValueError: template misconfigured (unknown output model,
                missing prompt placeholder).
            LLMValidationError: the LLM returned something that didn't
                match the schema (very rare with structured output).
            LLMError: any other provider failure (timeout, auth, 5xx).
        """
        # 1. Resolve difficulty tier from the user's sub-level
        sub_level = user_profile.get("sub_level", 5)
        tier = difficulty_tier_for_sublevel(sub_level)

        # 2. Get tier-specific modifiers, with safe fallbacks so a
        #    template with sparse difficulty_modifiers never crashes.
        modifiers = template.difficulty_modifiers.get(tier.value)
        if modifiers is None:
            for fallback_tier in ("beginner", "intermediate", "advanced"):
                modifiers = template.difficulty_modifiers.get(fallback_tier)
                if modifiers is not None:
                    logger.warning(
                        "Template %s has no modifiers for tier=%r; "
                        "falling back to tier=%r",
                        template.template_id,
                        tier.value,
                        fallback_tier,
                    )
                    break
            if modifiers is None:
                modifiers = {}

        # 3. Fill the prompt template with user profile + tier modifiers.
        #    Defaults keep older templates/callers working while newer
        #    templates can use richer course + personalisation context.
        course_topic = (
            user_profile.get("course_topic")
            or user_profile.get("topic_of_day")
            or user_profile.get("topic")
            or "today's English topic"
        )
        interests = str(user_profile.get("interests") or "").strip()
        primary_goals = str(user_profile.get("primary_goals") or "").strip()
        personalisation_context = str(
            user_profile.get("personalisation_context") or ""
        ).strip()
        content_guidance = str(user_profile.get("content_guidance") or "").strip()
        if not content_guidance:
            if interests:
                content_guidance = (
                    "Use one of the learner's interests as a fresh scenario "
                    "only when it fits naturally."
                )
            else:
                content_guidance = (
                    "Use a fresh, everyday scenario appropriate for the course topic."
                )

        prompt_vars = {
            **user_profile,
            "tier": tier.value,
            "course_topic": course_topic,
            "topic_of_day": course_topic,
            "topic": user_profile.get("topic") or course_topic,
            "interests": interests or "not specified",
            "primary_goals": primary_goals or "general English improvement",
            "personalisation_context": personalisation_context or "none",
            "content_guidance": content_guidance,
            "avoid_example_reuse_instruction": (
                "Do not copy any seed/example passage, office story, names, "
                "setting, or sentence pattern. Keep the schema, but create "
                "new personalized content."
            ),
            **modifiers,
        }
        try:
            filled_prompt = template.llm_prompt_template.format(**prompt_vars)
        except KeyError as exc:
            # Treat as a configuration bug, not an LLM failure —
            # surfaces as a 500 in the route, which is correct.
            raise ValueError(
                f"Missing placeholder in prompt template "
                f"{template.template_id!r}: {exc}. "
                f"Available keys: {list(prompt_vars.keys())}"
            ) from exc

        # 4. Resolve the Pydantic output model from the registry
        output_model_cls = ALL_OUTPUT_MODELS.get(template.output_model_name)
        if output_model_cls is None:
            raise ValueError(
                f"Unknown output model: {template.output_model_name!r}. "
                f"Available: {list(ALL_OUTPUT_MODELS.keys())}"
            )

        logger.info(
            "task_generate_start template=%s tier=%s output_model=%s",
            template.template_id,
            tier.value,
            template.output_model_name,
        )

        # 5. Call the LLM with structured output. The client handles:
        #    - retries on transient errors
        #    - schema validation
        #    - LangSmith tracing
        #    - usage logging
        try:
            validated = await self._llm.generate_structured(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=filled_prompt,
                output_model=output_model_cls,
                temperature=self._temperature,
            )
        except LLMValidationError:
            # Re-raise unchanged — caller may want to log + retry with
            # a different template. Don't wrap in a generic exception.
            raise
        except LLMError:
            # Same — keep the typed error so the route layer can map it
            # to the right HTTP status (502 for provider failures).
            raise

        logger.info(
            "task_generate_ok template=%s output_model=%s",
            template.template_id,
            template.output_model_name,
        )
        content = validated.model_dump()
        self._validate_template_contract(
            template=template,
            content=content,
            modifiers=modifiers,
        )
        content["estimated_time_minutes"] = template.estimated_time_minutes
        return content

    @staticmethod
    def _validate_template_contract(
        *,
        template: TaskTemplate,
        content: dict,
        modifiers: dict,
    ) -> None:
        """Validate template-owned invariants that are not in static schemas."""
        if template.template_id == "full_grammar_read_v1":
            TaskGeneratorAgent._validate_fill_in_blank_passage_contract(
                content,
                expected_item_count=modifiers.get("item_count"),
            )
            return

        if template.template_id == "grammar_read_fill_blanks_v1":
            TaskGeneratorAgent._validate_fill_in_blank_passage_contract(
                content,
                expected_item_count=modifiers.get("blank_count"),
            )
            return

        if template.template_id != "grammar_read_error_spotting_v1":
            return

        expected_sentence_count = modifiers.get("sentence_count")
        expected_error_count = modifiers.get("error_count")
        sentences = content.get("sentences") or []
        actual_error_count = sum(
            1 for sentence in sentences if sentence.get("has_error") is True
        )

        if expected_sentence_count is not None and len(sentences) != expected_sentence_count:
            raise LLMValidationError(
                "ErrorSpottingTask sentence count mismatch: "
                f"expected {expected_sentence_count}, got {len(sentences)}"
            )

        if expected_error_count is not None and actual_error_count != expected_error_count:
            raise LLMValidationError(
                "ErrorSpottingTask error count mismatch: "
                f"expected {expected_error_count}, got {actual_error_count}"
            )

    @staticmethod
    def _normalize_for_passage_match(text: str) -> str:
        return " ".join(text.strip().lower().split())

    @staticmethod
    def _validate_fill_in_blank_passage_contract(
        content: dict,
        *,
        expected_item_count: int | None = None,
    ) -> None:
        """Ensure fill-in-blanks is a true typed-blank reading passage."""
        passage = content.get("passage")
        if not isinstance(passage, str) or not passage.strip():
            raise LLMValidationError(
                "Fill-in-blanks task must include a passage with the blanks inside it"
            )

        items = content.get("items") or content.get("blanks") or []
        if not items:
            raise LLMValidationError("Fill-in-blanks task must include blank items")

        if expected_item_count is not None and len(items) != expected_item_count:
            raise LLMValidationError(
                "Fill-in-blanks item count mismatch: "
                f"expected {expected_item_count}, got {len(items)}"
            )

        passage_norm = TaskGeneratorAgent._normalize_for_passage_match(passage)
        passage_blank_count = len(re.findall(r"___", passage))
        if passage_blank_count != len(items):
            raise LLMValidationError(
                "Fill-in-blanks passage blank count mismatch: "
                f"expected {len(items)}, got {passage_blank_count}"
            )

        missing: list[str] = []
        for item in items:
            if item.get("distractors") or item.get("options"):
                raise LLMValidationError(
                    "Fill-in-blanks must be typed answers, "
                    "not MCQ options or distractors"
                )
            sentence = item.get("sentence_with_blank")
            if not isinstance(sentence, str) or "___" not in sentence:
                raise LLMValidationError(
                    "Fill-in-blanks item is missing sentence_with_blank with ___"
                )
            sentence_norm = TaskGeneratorAgent._normalize_for_passage_match(sentence)
            if sentence_norm not in passage_norm:
                missing.append(str(item.get("item_id") or sentence))

        if missing:
            raise LLMValidationError(
                "Fill-in-blanks items must be copied from the passage. "
                f"Unlinked items: {missing}"
            )


# ---------------------------------------------------------------------------
# Convenience function for the 3-agent contract.
#
# Earlier this file was a placeholder that raised NotImplementedError.
# Today the real work lives in TaskGeneratorAgent.generate(...). We keep
# `generate_task(...)` for API symmetry with `generate_feedback(...)` —
# anything that wants the "one function per agent" pattern can import it.
# ---------------------------------------------------------------------------
async def generate_task(
    *,
    template: TaskTemplate,
    user_profile: dict,
) -> dict:
    """Functional wrapper around `TaskGeneratorAgent.generate(...)`.

    Useful when callers want the same shape as `generate_feedback(...)`
    and don't need to hold an agent instance.
    """
    agent = TaskGeneratorAgent()
    return await agent.generate(template, user_profile)
