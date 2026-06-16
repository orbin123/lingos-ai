"""Personalization Agent — turns raw learner profile data into the
structured context every downstream agent (planner, teacher, task,
feedback) reads.

Runs once on profile save / diagnosis completion. The result is cached
on `user_profiles.structured_personalisation` so lesson-time calls are
free.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from app.ai.llm import get_default_llm_client
from app.modules.personalization.schemas import (
    ExtractionSource,
    StructuredPersonalisation,
    TonePreference,
    empty_personalisation,
    fallback_personalisation,
)

logger = logging.getLogger(__name__)


_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"\+?\d[\d\s\-().]{6,}\d")


_SYSTEM_PROMPT = """
You are the Personalization Engine for an English learning app.

Given raw learner profile data, produce a STRUCTURED view that downstream
teaching agents will use to choose scenarios, vocabulary, and tone.

Rules:
- Always output English, even if the input is in another language.
  Translate first, then extract.
- `domain` is a short label (under ~80 chars) for the learner's
  professional or life context. Examples: "tech / software engineering",
  "university student", "hospitality", "customer support", "stay-at-home
  parent", "general". Use "general" when the input is too thin.
- `communication_contexts` is 0-6 concrete settings the learner needs
  English in. Use the situations the learner actually mentions — do not
  invent generic ones. Examples: "standup meeting", "Slack reply",
  "PR review", "first day on campus", "guest check-in".
- `priority_skills` is 0-4 skills the learner most needs to GROW.
  Examples: "explaining technical decisions", "small talk", "academic
  writing", "polite refusals".
- `pain_points` is 0-4 specific struggles the learner names. Examples:
  "filler words", "confidence in meetings", "freezing under questions".
- `tone_preference` is exactly one of: casual, neutral, professional,
  academic. Pick based on the goal/profession; default to neutral when
  unclear.
- DO NOT include emails, phone numbers, or other personal contact info
  in any field.
- Be specific but compact. No paragraphs. No restating the input.
- If the personalisation context is empty or vacuous (e.g. "I want to
  learn English"), still produce a valid object with sensible defaults
  (`domain: "general"`, empty lists, `tone_preference: neutral`).
""".strip()


def _build_user_prompt(profile: dict[str, Any]) -> str:
    personalisation = (profile.get("personalisation_context") or "").strip()
    primary_goals = (profile.get("primary_goals") or "").strip()
    interests = (profile.get("interests") or "").strip()
    goal_enum = (profile.get("goal") or "").strip()
    native_language = (profile.get("native_language") or "").strip()
    country = (profile.get("country") or "").strip()
    self_assessed_level = (profile.get("self_assessed_level") or "").strip()

    return f"""
Learner profile data:
- Free-text personalisation: {personalisation or "(none)"}
- Primary goals (pipe-separated): {primary_goals or "(none)"}
- Interests: {interests or "(none)"}
- Goal category: {goal_enum or "(none)"}
- Native language: {native_language or "(unspecified)"}
- Country: {country or "(unspecified)"}
- Self-assessed level: {self_assessed_level or "(unspecified)"}

Produce the structured personalisation now. Return only the structured JSON.
""".strip()


def _strip_pii(value: str) -> str:
    """Defensive PII strip — remove emails/phones in case the model echoed any."""
    cleaned = _EMAIL_RE.sub("", value)
    cleaned = _PHONE_RE.sub("", cleaned)
    return cleaned.strip()


def _sanitise(payload: StructuredPersonalisation) -> StructuredPersonalisation:
    """Drop PII from any string field on the structured output."""
    return StructuredPersonalisation(
        domain=_strip_pii(payload.domain) or "general",
        communication_contexts=[
            cleaned
            for item in payload.communication_contexts
            if (cleaned := _strip_pii(item))
        ],
        priority_skills=[
            cleaned for item in payload.priority_skills if (cleaned := _strip_pii(item))
        ],
        pain_points=[
            cleaned for item in payload.pain_points if (cleaned := _strip_pii(item))
        ],
        tone_preference=payload.tone_preference,
        extraction_source=payload.extraction_source,
        extracted_at=payload.extracted_at,
    )


def _is_effectively_empty(profile: dict[str, Any]) -> bool:
    """True when the profile has nothing personal to extract from."""
    relevant_fields = (
        "personalisation_context",
        "primary_goals",
        "interests",
        "goal",
    )
    for field in relevant_fields:
        value = (profile.get(field) or "").strip()
        if value:
            return False
    return True


class PersonalizationAgent:
    def __init__(self, *, temperature: float = 0.2) -> None:
        self._llm = get_default_llm_client()
        self._temperature = temperature

    async def extract(self, *, profile: dict[str, Any]) -> StructuredPersonalisation:
        if _is_effectively_empty(profile):
            return empty_personalisation()

        user_prompt = _build_user_prompt(profile)

        try:
            llm_output = await self._llm.generate_structured(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                output_model=StructuredPersonalisation,
                temperature=self._temperature,
            )
        except Exception:
            logger.exception(
                "PersonalizationAgent LLM call failed; using fallback structure"
            )
            return fallback_personalisation()

        # The model may have its own tone guess, but extraction_source must
        # reflect that this came from a real LLM run.
        llm_output = StructuredPersonalisation(
            domain=llm_output.domain,
            communication_contexts=llm_output.communication_contexts,
            priority_skills=llm_output.priority_skills,
            pain_points=llm_output.pain_points,
            tone_preference=llm_output.tone_preference or TonePreference.NEUTRAL,
            extraction_source=ExtractionSource.LLM,
        )
        return _sanitise(llm_output)


async def extract_structured_personalisation(
    *, profile: dict[str, Any]
) -> StructuredPersonalisation:
    """Public entry point — single LLM round-trip with safe fallbacks."""
    agent = PersonalizationAgent()
    return await agent.extract(profile=profile)
