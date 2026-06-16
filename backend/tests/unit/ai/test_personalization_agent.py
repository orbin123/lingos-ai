"""Tests for the Personalization Engine — schemas, agent, and PII scrub."""

from __future__ import annotations

import asyncio

from app.ai.agents import personalization as personalization_module
from app.ai.agents.personalization import (
    PersonalizationAgent,
    _strip_pii,
    extract_structured_personalisation,
)
from app.modules.personalization.schemas import (
    ExtractionSource,
    StructuredPersonalisation,
    TonePreference,
    empty_personalisation,
    fallback_personalisation,
)


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------


def test_empty_personalisation_has_safe_defaults() -> None:
    payload = empty_personalisation()
    assert payload.extraction_source is ExtractionSource.EMPTY
    assert payload.domain == "general"
    assert payload.tone_preference is TonePreference.NEUTRAL
    assert payload.communication_contexts == []
    assert payload.priority_skills == []
    assert payload.pain_points == []


def test_fallback_personalisation_has_safe_defaults() -> None:
    payload = fallback_personalisation()
    assert payload.extraction_source is ExtractionSource.FALLBACK
    assert payload.domain == "general"
    assert payload.tone_preference is TonePreference.NEUTRAL


def test_structured_schema_cleans_blank_list_entries() -> None:
    s = StructuredPersonalisation(
        domain="tech / software engineering",
        communication_contexts=["standup", "", "  ", "PR review"],
        priority_skills=["explaining technical decisions"],
        pain_points=[],
        tone_preference=TonePreference.PROFESSIONAL,
        extraction_source=ExtractionSource.LLM,
    )
    # Blank/whitespace-only entries are dropped by the validator.
    assert s.communication_contexts == ["standup", "PR review"]


def test_structured_schema_falls_back_when_domain_is_blank() -> None:
    s = StructuredPersonalisation(
        domain="",
        communication_contexts=[],
        priority_skills=[],
        pain_points=[],
        tone_preference=TonePreference.NEUTRAL,
        extraction_source=ExtractionSource.LLM,
    )
    assert s.domain == "general"


# ---------------------------------------------------------------------------
# PII scrub
# ---------------------------------------------------------------------------


def test_strip_pii_removes_emails_and_phone_numbers() -> None:
    cleaned = _strip_pii(
        "Contact me at alice@example.com or +1 (415) 555-0199 if needed"
    )
    assert "alice@example.com" not in cleaned
    assert "555-0199" not in cleaned
    assert "Contact me at" in cleaned


# ---------------------------------------------------------------------------
# Agent behaviour
# ---------------------------------------------------------------------------


def test_extract_returns_empty_when_profile_is_blank(monkeypatch) -> None:
    """No personalisation context, no goals, no interests → empty sentinel.

    Important: this path must NOT call the LLM.
    """
    calls = {"n": 0}

    class LoudLLM:
        async def generate_structured(self, **kwargs):
            calls["n"] += 1
            raise RuntimeError("LLM should not have been called")

    monkeypatch.setattr(
        personalization_module,
        "get_default_llm_client",
        lambda: LoudLLM(),
    )

    result = asyncio.run(extract_structured_personalisation(profile={}))
    assert calls["n"] == 0
    assert result.extraction_source is ExtractionSource.EMPTY
    assert result.domain == "general"


def test_extract_falls_back_when_llm_raises(monkeypatch) -> None:
    class ExplodingLLM:
        async def generate_structured(self, **kwargs):
            raise RuntimeError("LLM unavailable")

    monkeypatch.setattr(
        personalization_module,
        "get_default_llm_client",
        lambda: ExplodingLLM(),
    )

    result = asyncio.run(
        extract_structured_personalisation(
            profile={"personalisation_context": "I'm a software engineer"}
        )
    )
    assert result.extraction_source is ExtractionSource.FALLBACK
    # Even the fallback payload is complete — never partial.
    assert result.domain
    assert result.tone_preference is TonePreference.NEUTRAL


def test_extract_passes_through_llm_output(monkeypatch) -> None:
    """Distinct personas → distinct domain/context strings."""
    llm_responses = [
        StructuredPersonalisation(
            domain="tech / software engineering",
            communication_contexts=["standup meeting", "PR review"],
            priority_skills=["explaining technical decisions"],
            pain_points=["filler words"],
            tone_preference=TonePreference.PROFESSIONAL,
            extraction_source=ExtractionSource.LLM,
        ),
        StructuredPersonalisation(
            domain="university student",
            communication_contexts=["first day on campus", "study group"],
            priority_skills=["academic writing"],
            pain_points=["confidence in group discussion"],
            tone_preference=TonePreference.NEUTRAL,
            extraction_source=ExtractionSource.LLM,
        ),
    ]

    class StubLLM:
        async def generate_structured(self, **kwargs):
            return llm_responses.pop(0)

    monkeypatch.setattr(
        personalization_module,
        "get_default_llm_client",
        lambda: StubLLM(),
    )

    engineer = asyncio.run(
        PersonalizationAgent().extract(
            profile={
                "personalisation_context": (
                    "I'm a software engineer at a startup. I explain technical "
                    "decisions in standups."
                ),
                "primary_goals": "workplace fluency",
            }
        )
    )
    student = asyncio.run(
        PersonalizationAgent().extract(
            profile={
                "personalisation_context": (
                    "I'm a university student in Tokyo planning to study abroad."
                ),
                "primary_goals": "study abroad",
            }
        )
    )

    assert engineer.domain != student.domain
    assert "standup meeting" in engineer.communication_contexts
    assert "first day on campus" in student.communication_contexts
    assert engineer.extraction_source is ExtractionSource.LLM
    assert student.extraction_source is ExtractionSource.LLM


def test_extract_sanitises_pii_from_llm_output(monkeypatch) -> None:
    """Even if the model echoes contact info, the persisted row must not contain it."""

    class LeakyLLM:
        async def generate_structured(self, **kwargs):
            return StructuredPersonalisation(
                domain="hospitality alice@example.com",
                communication_contexts=["guest check-in (call +1 415-555-0199)"],
                priority_skills=["polite refusals"],
                pain_points=["accent confidence"],
                tone_preference=TonePreference.PROFESSIONAL,
                extraction_source=ExtractionSource.LLM,
            )

    monkeypatch.setattr(
        personalization_module,
        "get_default_llm_client",
        lambda: LeakyLLM(),
    )

    result = asyncio.run(
        extract_structured_personalisation(
            profile={"personalisation_context": "I work at a hotel front desk"}
        )
    )
    assert "alice@example.com" not in result.domain
    assert not any("alice@example.com" in c for c in result.communication_contexts)
    assert not any("555-0199" in c for c in result.communication_contexts)
