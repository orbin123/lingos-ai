"""Shared task schema primitives.

This module intentionally stays small. The old template registry referenced
many schema modules that are not present in this codebase; the active sessions
flow only needs these enums plus concrete widget payload models.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict


class SubSkill(StrEnum):
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    PRONUNCIATION = "pronunciation"
    FLUENCY = "fluency"
    EXPRESSION = "expression"
    COMPREHENSION = "comprehension"
    TONE = "tone"


class Activity(StrEnum):
    READ = "read"
    WRITE = "write"
    LISTEN = "listen"
    SPEAK = "speak"


class ScoringMethod(StrEnum):
    RULE_BASED = "rule_based"
    LLM_OPEN_WRITING = "llm_open_writing"


class DifficultyTier(StrEnum):
    FOUNDATION = "foundation"
    BUILDING = "building"
    ADVANCING = "advancing"


class GeneratedTaskBase(BaseModel):
    model_config = ConfigDict(extra="allow")


@dataclass(frozen=True)
class TaskTemplate:
    template_id: str
    sub_skill: SubSkill
    activity: Activity
    output_model: type[GeneratedTaskBase]
    metadata: dict[str, Any] | None = None


def difficulty_tier_for_sublevel(sub_level: int) -> DifficultyTier:
    if sub_level <= 3:
        return DifficultyTier.FOUNDATION
    if sub_level <= 7:
        return DifficultyTier.BUILDING
    return DifficultyTier.ADVANCING
