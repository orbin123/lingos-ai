"""IELTS challenge task generator for text-only challenge content."""

from __future__ import annotations

import logging
from typing import Any

from app.ai.agents.prompt_loader import load_prompt, render_prompt_template
from app.ai.llm import ILLMClient, get_default_llm_client
from app.modules.challenges.ielts_sprint.generator_schemas import GeneratedIELTSTaskPayload


logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = (
    "You are an IELTS test content writer for an English learning app. "
    "Generate structured IELTS-style challenge content that matches the "
    "provided Pydantic schema exactly. Return only the structured object."
)


class IELTSChallengeGenerator:
    """Generate one IELTS challenge attempt payload through structured output."""

    def __init__(
        self,
        *,
        llm: ILLMClient | None = None,
        temperature: float = 0.8,
    ) -> None:
        self._llm = llm or get_default_llm_client()
        self._temperature = temperature

    async def generate(
        self,
        *,
        context: dict[str, Any],
        prompt_template: str = "ielts/generator",
    ) -> dict:
        """Return a validated task payload dict ready for JSONB persistence."""
        template = load_prompt(prompt_template)
        user_prompt = render_prompt_template(template, context)

        logger.info(
            "ielts_challenge_generate_start level=%s prompt_template=%s",
            context.get("level_number"),
            prompt_template,
        )
        validated = await self._llm.generate_structured(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=GeneratedIELTSTaskPayload,
            temperature=self._temperature,
        )
        logger.info(
            "ielts_challenge_generate_ok level=%s prompt_template=%s",
            context.get("level_number"),
            prompt_template,
        )
        return validated.model_dump()
