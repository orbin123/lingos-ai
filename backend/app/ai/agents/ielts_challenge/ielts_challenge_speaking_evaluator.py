"""IELTS challenge speaking evaluator for Phase 6."""

from __future__ import annotations

import logging
from typing import Any

from app.ai.agents.prompt_loader import load_prompt, render_prompt_template
from app.ai.llm import ILLMClient, get_default_llm_client
from app.modules.challenges.evaluation_schemas import SpeakingEvaluationReport


logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = (
    "You are an IELTS Speaking examiner for a practice app. Score only from "
    "transcripts, mark pronunciation unavailable, and return only the structured "
    "evaluation object."
)


class IELTSChallengeSpeakingEvaluator:
    """Evaluate IELTS Speaking transcripts through structured LLM output."""

    def __init__(
        self,
        *,
        llm: ILLMClient | None = None,
        temperature: float = 0.1,
    ) -> None:
        self._llm = llm or get_default_llm_client()
        self._temperature = temperature

    async def evaluate(
        self,
        *,
        context: dict[str, Any],
        prompt_template: str = "ielts/speaking_evaluator",
    ) -> SpeakingEvaluationReport:
        """Return a validated transcript-only speaking evaluation report."""
        template = load_prompt(prompt_template)
        user_prompt = render_prompt_template(template, context)

        logger.info(
            "ielts_challenge_speaking_evaluate_start attempt_id=%s prompt_template=%s",
            context.get("attempt_id"),
            prompt_template,
        )
        report = await self._llm.generate_structured(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=SpeakingEvaluationReport,
            temperature=self._temperature,
        )
        logger.info(
            "ielts_challenge_speaking_evaluate_ok attempt_id=%s prompt_template=%s",
            context.get("attempt_id"),
            prompt_template,
        )
        return report
