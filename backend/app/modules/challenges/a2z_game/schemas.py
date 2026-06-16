"""Pydantic schemas for the A2Z Challenge API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ── Request schemas ──────────────────────────────────────────────────


class StartRoundRequest(BaseModel):
    """Body for ``POST /challenges/a2z/rounds``."""

    mode: Literal["spin", "pick"]
    letter: str | None = Field(
        default=None,
        description="Required when mode='pick'. Single uppercase A-Z letter.",
        min_length=1,
        max_length=1,
    )


class FinishRoundRequest(BaseModel):
    """Optional body for ``POST /challenges/a2z/rounds/{round_id}/finish``."""

    client_elapsed_seconds: float | None = None
    final_chunk_uploaded: bool = False


# ── Evaluation report ────────────────────────────────────────────────


class A2ZEvaluationReport(BaseModel):
    """Deterministic evaluation result for one A2Z round."""

    valid_words: list[str]
    valid_word_count: int
    target_words: int
    passed: bool


# ── Response schemas ─────────────────────────────────────────────────


class A2ZLevelRead(BaseModel):
    """One level's metadata for the progress endpoint."""

    level_number: int
    name: str
    target_words: int
    round_time_seconds: int


class A2ZProgressRead(BaseModel):
    """Everything the home screen needs. Returned by ``GET /progress``."""

    challenge_slug: str
    letters: list[str]
    levels: list[A2ZLevelRead]
    current_level_number: int
    cleared_by_level: dict[str, list[str]]
    open_letters: list[str]
    game_completed: bool
    can_restart: bool


class StartRoundResponse(BaseModel):
    """Returned by ``POST /rounds``."""

    round_id: int
    letter: str
    target_words: int
    round_time_seconds: int
    expires_at: datetime
    level_number: int


class AudioChunkResponse(BaseModel):
    """Returned by ``POST /rounds/{round_id}/audio-chunks``."""

    new_words: list[str]
    accepted_words: list[str]
    valid_word_count: int
    target_words: int
    passed_so_far: bool


class FinishRoundResponse(BaseModel):
    """Returned by ``POST /rounds/{round_id}/finish``."""

    passed: bool
    letter: str
    valid_words: list[str]
    valid_word_count: int
    target_words: int
    level_number: int
    level_cleared: bool
    game_completed: bool
    progress: A2ZProgressRead
