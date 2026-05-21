"""IELTS challenge feedback generator for Phase 4."""

from __future__ import annotations

import logging
from typing import Any

from app.ai.agents.prompt_loader import load_prompt, render_prompt_template
from app.ai.llm import ILLMClient, get_default_llm_client
from app.modules.challenges.evaluation_schemas import IELTSFeedbackReport


logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = (
    "You are a supportive IELTS coach. Turn a structured evaluation report "
    "into concise, specific learner feedback. Return only the structured "
    "feedback object."
)


class IELTSChallengeFeedbackAgent:
    """Generate user-facing IELTS feedback from an evaluation report."""

    def __init__(
        self,
        *,
        llm: ILLMClient | None = None,
        temperature: float = 0.4,
    ) -> None:
        self._llm = llm or get_default_llm_client()
        self._temperature = temperature

    async def generate(
        self,
        *,
        context: dict[str, Any],
        prompt_template: str = "ielts/feedback",
    ) -> IELTSFeedbackReport:
        """Return a validated feedback report."""
        template = load_prompt(prompt_template)
        user_prompt = render_prompt_template(template, context)

        logger.info(
            "ielts_challenge_feedback_start attempt_id=%s prompt_template=%s",
            context.get("attempt_id"),
            prompt_template,
        )
        report = await self._llm.generate_structured(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=IELTSFeedbackReport,
            temperature=self._temperature,
        )
        logger.info(
            "ielts_challenge_feedback_ok attempt_id=%s prompt_template=%s",
            context.get("attempt_id"),
            prompt_template,
        )
        return report
