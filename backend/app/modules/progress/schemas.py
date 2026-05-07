"""Pydantic schemas for the progress module."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SkillScoreSnapshot(BaseModel):
    """One row in GET /progress/scores — current score for one skill.

    Used by the spider chart on the dashboard. Returns all 7 skills
    for the current user.
    """

    model_config = ConfigDict(from_attributes=True)

    skill_id: int
    skill_name: str
    score: float


class ProgressLogPoint(BaseModel):
    """One row in GET /progress/history — a single point on the line chart."""

    model_config = ConfigDict(from_attributes=True)

    score: float
    created_at: datetime


class WeeklySnapshot(BaseModel):
    """Aggregated weekly metrics for the stats page."""

    overall_score_change: float
    tasks_completed: int
    weekly_task_goal: int
    best_skill_name: str | None
    best_skill_score: float | None


class StatsMistake(BaseModel):
    """One mistake or strength row shown under a recent activity."""

    label: str
    issue: str
    correction: str | None = None


class RecentActivity(BaseModel):
    """Completed task summary with evaluator and feedback details."""

    id: int
    task_name: str
    task_type: str
    completed_at: datetime
    score: float
    mistake_count: int
    mistakes: list[StatsMistake]
    strength: StatsMistake | None = None


class StatsFeedback(BaseModel):
    """Feedback Agent highlights for strengths and focus areas."""

    strengths: list[str]
    focus_areas: list[str]


class StatsDashboard(BaseModel):
    """Everything the frontend stats page needs in one read-only response."""

    weekly_snapshot: WeeklySnapshot
    skill_scores: list[SkillScoreSnapshot]
    feedback: StatsFeedback
    recent_activities: list[RecentActivity]
