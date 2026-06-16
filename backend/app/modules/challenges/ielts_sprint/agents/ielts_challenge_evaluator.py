"""IELTS challenge writing evaluator for Phase 4."""

from __future__ import annotations

import logging
from typing import Any

from app.ai.agents.prompt_loader import load_prompt, render_prompt_template
from app.ai.llm import ILLMClient, get_default_llm_client
from app.modules.challenges.ielts_sprint.evaluation_schemas import (
    WritingEvaluationReport,
)


logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = (
    "You are an IELTS Writing Task 2 examiner for a practice app. "
    "Score learner writing against the official IELTS criteria and return "
    "only the structured evaluation object."
)


class IELTSChallengeWritingEvaluator:
    """Evaluate IELTS Writing responses through structured LLM output."""

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
        prompt_template: str = "ielts/evaluator",
    ) -> WritingEvaluationReport:
        """Return a validated writing evaluation report."""
        template = load_prompt(prompt_template)
        user_prompt = render_prompt_template(template, context)

        logger.info(
            "ielts_challenge_writing_evaluate_start attempt_id=%s prompt_template=%s",
            context.get("attempt_id"),
            prompt_template,
        )
        report = await self._llm.generate_structured(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=WritingEvaluationReport,
            temperature=self._temperature,
        )
        logger.info(
            "ielts_challenge_writing_evaluate_ok attempt_id=%s prompt_template=%s",
            context.get("attempt_id"),
            prompt_template,
        )
        return report
