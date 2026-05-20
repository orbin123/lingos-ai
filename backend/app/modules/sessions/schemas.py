"""Pydantic shapes for the session REST API + internal payloads.

The wire schemas mirror the restructure spec §16.5 (`session_scorecard`),
§16.7 (`feedback_result`), and the `start / next-activity / submit / complete`
contract defined in §19.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.sessions.models import (
    AttemptStatus,
    SessionStatus,
)


# ── Activity preferences ───────────────────────────────────────────


class ActivityPreferences(BaseModel):
    """Which activity types the user is willing to do today.

    Defaults to "everything on" — production flows pull these from the user's
    enrollment. Phase 3 keeps them as request inputs for easier testing.
    """

    model_config = ConfigDict(frozen=True)

    allow_read: bool = True
    allow_write: bool = True
    allow_listen: bool = True
    allow_speak: bool = True

    def allowed_activities(self) -> set[str]:
        mapping = {
            "read": self.allow_read,
            "write": self.allow_write,
            "listen": self.allow_listen,
            "speak": self.allow_speak,
        }
        return {activity for activity, on in mapping.items() if on}


# ── Start ──────────────────────────────────────────────────────────


class SessionStartRequest(BaseModel):
    """Body for `POST /sessions/start`."""

    day_id: str = Field(..., description="Curriculum day id, e.g. 'day_24_05_03'.")
    course_length: str = Field(..., pattern=r"^(24w|48w)$")
    tasks_per_day: int = Field(..., ge=2, le=4)
    preferences: ActivityPreferences = Field(default_factory=ActivityPreferences)


class AttemptSkeleton(BaseModel):
    """One activity slot in the session skeleton returned by `start`."""

    model_config = ConfigDict(from_attributes=True)

    sequence: int
    archetype_id: str
    archetype_name: str
    is_mandatory: bool
    status: AttemptStatus


class SessionStartResponse(BaseModel):
    """Response shape for `POST /sessions/start`."""

    model_config = ConfigDict(from_attributes=True)

    session_id: str
    day_id: str
    course_length: str
    status: SessionStatus
    is_first_attempt: bool
    started_at: datetime
    attempts: list[AttemptSkeleton]


class DashboardPlanActivity(BaseModel):
    """One activity row for the dashboard's read-only daily plan."""

    sequence: int
    archetype_id: str
    archetype_name: str
    core_activity: str
    ui_widget: str
    is_mandatory: bool
    status: AttemptStatus


class DashboardTodayPlanResponse(BaseModel):
    """Read-only dashboard view of today's v2 plan."""

    day_id: str
    topic: str
    session_id: str | None = None
    status: SessionStatus | None = None
    is_preview: bool
    activities: list[DashboardPlanActivity]


class DashboardStartResponse(DashboardTodayPlanResponse):
    """Start/continue response for the dashboard CTA."""

    mode: str


# ── Next-activity ──────────────────────────────────────────────────


class NextActivityResponse(BaseModel):
    """Response shape for `GET /sessions/{id}/next-activity`."""

    model_config = ConfigDict(from_attributes=True)

    sequence: int
    archetype_id: str
    is_mandatory: bool
    status: AttemptStatus
    ui_widget: str
    task_content: dict


# ── Submit ─────────────────────────────────────────────────────────


class SubmitActivityRequest(BaseModel):
    """Body for `POST /sessions/{id}/activities/{seq}/submit`."""

    user_response: dict


class MistakeRead(BaseModel):
    """One mistake inside a feedback record — matches spec §14."""

    user_wrote: str | None = None
    issue: str
    correction: str | None = None
    rule: str | None = None
    sub_skills_affected: list[str] = Field(default_factory=list)


class FeedbackRead(BaseModel):
    """Structured feedback returned alongside the evaluation."""

    model_config = ConfigDict(from_attributes=True)

    score: int
    summary: str
    did_well: list[str]
    mistakes: list[MistakeRead]
    next_tip: str | None
    sub_skill_breakdown: dict[str, int]


class EvaluationRead(BaseModel):
    """Scoring output (deterministic side of an attempt)."""

    model_config = ConfigDict(from_attributes=True)

    raw_score: float
    rubric_scores: dict[str, float]
    base_reward: int
    weighted_points: dict[str, float]
    evaluator_notes: str | None


class SubmitActivityResponse(BaseModel):
    """Response shape for the submit endpoint."""

    sequence: int
    status: AttemptStatus
    evaluation: EvaluationRead
    feedback: FeedbackRead


# ── Complete / scorecard ───────────────────────────────────────────


class SessionScorecardRead(BaseModel):
    """Persisted scorecard returned by `complete` and `GET .../scorecard`.

    `skill_labels` maps the internal sub-skill identifiers used as keys in
    `points_earned` / `subskill_totals_after` / `dashboard_after` to their
    user-facing display labels (Phase 5). Frontend renders the labels and
    keys data by the identifier.
    """

    model_config = ConfigDict(from_attributes=True)

    session_id: str
    points_earned: dict[str, int]
    subskill_totals_after: dict[str, int]
    dashboard_after: dict[str, float]
    skill_labels: dict[str, str]
    completed_at: datetime
    points_applied: bool
