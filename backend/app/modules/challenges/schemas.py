"""Pydantic schemas for the challenges read API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.challenges.models import ChallengeAttemptStatus


class ChallengeListItem(BaseModel):
    """Compact card data for a challenge."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    short_description: str
    icon: str | None
    level_count: int


class ChallengeLevelRead(BaseModel):
    """Challenge level data plus user-specific progress metadata."""

    id: int
    level_number: int
    name: str
    time_limit_seconds: int
    pass_threshold: float
    config: dict
    unlocked: bool
    best_score: float | None
    attempt_count: int


class ChallengeDetailRead(BaseModel):
    """Full challenge details for a learner."""

    id: int
    slug: str
    name: str
    short_description: str
    rules_md: str
    icon: str | None
    levels: list[ChallengeLevelRead]


class ChallengeAttemptRead(BaseModel):
    """Persisted state of one challenge attempt."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    challenge_level_id: int
    status: ChallengeAttemptStatus
    started_at: datetime
    completed_at: datetime | None
    expires_at: datetime
    task_payload: dict
    response_payload: dict | None
    overall_score: float | None
    section_scores: dict | None
    passed: bool | None
    evaluation_report: dict | None
    feedback_report: dict | None
    created_at: datetime


class ChallengeHistoryAttempt(BaseModel):
    """One personal attempt row for challenge history."""

    id: int
    challenge_level_id: int
    level_number: int
    level_name: str
    status: ChallengeAttemptStatus
    started_at: datetime
    completed_at: datetime | None
    expires_at: datetime
    overall_score: float | None
    section_scores: dict | None
    passed: bool | None
    is_best_for_level: bool
    created_at: datetime


class ChallengeHistoryRead(BaseModel):
    """Personal challenge history, newest attempt first."""

    challenge_slug: str
    challenge_name: str
    attempts: list[ChallengeHistoryAttempt]

