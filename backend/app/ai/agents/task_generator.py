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
                - topic (str): context topic, e.g. "workplace"

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

        # 3. Fill the prompt template with user profile + tier modifiers
        prompt_vars = {**user_profile, **modifiers}
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
        return validated.model_dump()


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
