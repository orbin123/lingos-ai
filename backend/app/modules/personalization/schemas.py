"""Pydantic schemas for the structured personalisation payload.

This is the single source of truth for the JSON shape that lives in
`user_profiles.structured_personalisation` and feeds every downstream
agent (planner, teacher, task generator, feedback).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class TonePreference(str, Enum):
    CASUAL = "casual"
    NEUTRAL = "neutral"
    PROFESSIONAL = "professional"
    ACADEMIC = "academic"


class ExtractionSource(str, Enum):
    """How a structured_personalisation row was produced.

    - LLM: extracted from real free-text input
    - FALLBACK: LLM failed or returned invalid output; defaults written
    - EMPTY: user provided no personalisation context; neutral defaults
    """

    LLM = "llm"
    FALLBACK = "fallback"
    EMPTY = "empty"


class StructuredPersonalisation(BaseModel):
    """Structured view of who the learner is, what they want to do in
    English, and what they need help with. Everything downstream consumes
    THIS, not the raw textarea.
    """

    domain: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description=(
            "Short label for the learner's professional or life context. "
            "Example: 'tech / software engineering', 'university student', "
            "'hospitality', 'general'."
        ),
    )
    communication_contexts: list[str] = Field(
        default_factory=list,
        max_length=8,
        description=(
            "Concrete settings the learner needs English in. "
            "Example: ['standup meeting', 'Slack reply', 'PR review']."
        ),
    )
    priority_skills: list[str] = Field(
        default_factory=list,
        max_length=6,
        description=(
            "Communication skills the learner most needs to grow. "
            "Example: ['explaining technical decisions', 'small talk']."
        ),
    )
    pain_points: list[str] = Field(
        default_factory=list,
        max_length=6,
        description=(
            "Specific struggles or fears the learner mentioned. "
            "Example: ['filler words', 'confidence in meetings']."
        ),
    )
    tone_preference: TonePreference = Field(
        default=TonePreference.NEUTRAL,
        description="Default register for teaching examples and roleplays.",
    )
    extraction_source: ExtractionSource = Field(
        default=ExtractionSource.LLM,
        description="How this row was produced (llm/fallback/empty).",
    )
    extracted_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of the last extraction run.",
    )

    @field_validator(
        "communication_contexts", "priority_skills", "pain_points", mode="before"
    )
    @classmethod
    def _clean_list(cls, value: object) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            return []
        cleaned: list[str] = []
        for item in value:
            if not isinstance(item, str):
                continue
            stripped = item.strip()
            if stripped:
                cleaned.append(stripped[:120])
        return cleaned

    @field_validator("domain", mode="before")
    @classmethod
    def _clean_domain(cls, value: object) -> str:
        if not isinstance(value, str):
            return "general"
        stripped = value.strip()
        return stripped[:200] if stripped else "general"


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------


def empty_personalisation() -> StructuredPersonalisation:
    """Default for users who have no personalisation_context yet."""
    return StructuredPersonalisation(
        domain="general",
        communication_contexts=[],
        priority_skills=[],
        pain_points=[],
        tone_preference=TonePreference.NEUTRAL,
        extraction_source=ExtractionSource.EMPTY,
    )


def fallback_personalisation() -> StructuredPersonalisation:
    """Safe default for when the LLM extraction fails."""
    return StructuredPersonalisation(
        domain="general",
        communication_contexts=[],
        priority_skills=[],
        pain_points=[],
        tone_preference=TonePreference.NEUTRAL,
        extraction_source=ExtractionSource.FALLBACK,
    )
