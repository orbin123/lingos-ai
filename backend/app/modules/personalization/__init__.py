"""Personalization module — turns raw learner profile data into the
structured context used by the planner, teacher, task, and feedback agents.

Note: this `__init__` exports the lightweight schemas only. Import the
service explicitly when you need DB / LLM-touching code:

    from app.modules.personalization.service import PersonalizationService

That keeps consumers that only need the schema (frontend type generation,
unit tests on the data shape) free of the DB / LLM import chain.
"""

from app.modules.personalization.schemas import (
    ExtractionSource,
    StructuredPersonalisation,
    TonePreference,
    empty_personalisation,
    fallback_personalisation,
)

__all__ = [
    "StructuredPersonalisation",
    "TonePreference",
    "ExtractionSource",
    "empty_personalisation",
    "fallback_personalisation",
]
