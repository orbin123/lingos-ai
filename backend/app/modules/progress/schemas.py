"""Pydantic schemas for the progress module."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class SkillScoreSnapshot(BaseModel):
    """One row in GET /progress/scores — current score for one skill.

    Used by the spider chart on the dashboard. Returns all 7 skills
    for the current user.

    `skill_name` is the stable internal identifier (e.g. 'expression').
    `display_label` is the user-facing label (e.g. 'Thought Organization').
    The frontend renders `display_label` and keys data by `skill_name`.
    """

    model_config = ConfigDict(from_attributes=True)

    skill_id: int
    skill_name: str
    display_label: str
    score: float


class ProgressLogPoint(BaseModel):
    """One row in GET /progress/history — a single point on the line chart."""

    model_config = ConfigDict(from_attributes=True)

    score: float
    created_at: datetime


class SkillHistorySeries(BaseModel):
    """Per-skill score history for the progression chart."""

    skill_id: int
    skill_name: str
    display_label: str
    scores: list[float]


class DifficultyDistribution(BaseModel):
    """Task difficulty breakdown since the user started."""

    beginner: int
    intermediate: int
    advanced: int
    total: int


class WeeklySnapshot(BaseModel):
    """Aggregated weekly metrics for the stats page.

    Deprecated: kept for backward compatibility with the current frontend.
    New consumers should read ``PeriodSnapshot`` (range-aware). This mirrors
    the selected period's headline numbers so the legacy card keeps working
    during the migration.
    """

    overall_score: float
    overall_score_change: float
    tasks_completed: int
    weekly_task_goal: int
    best_skill_name: str | None
    best_skill_display_label: str | None
    best_skill_score: float | None


class PeriodSnapshot(BaseModel):
    """Range-aware headline KPIs for the stats page.

    Everything here is computed against the learner's *curriculum* calendar
    for the requested ``range`` (see ``curriculum_periods``), not the
    wall-clock week.
    """

    range: Literal["week", "month", "all"]
    overall_score: float
    overall_score_change: float
    tasks_completed: int
    tasks_goal: int
    completion_pct: float
    time_practiced_seconds: int
    time_practiced_change_seconds: int | None
    best_skill_name: str | None
    best_skill_display_label: str | None
    best_skill_score: float | None
    curriculum_week: int
    curriculum_day: int
    weeks_completed: int


class CurriculumMilestone(BaseModel):
    """Where the learner sits in their course — drives the milestone card."""

    current_week: int
    current_day: int
    total_weeks: int
    course_length: str
    overall_score: float


class PracticePatterns(BaseModel):
    """Behavioural patterns over the selected curriculum period."""

    most_active_day: str | None
    best_day: str | None
    avg_session_seconds: int | None
    sessions_count: int
    subtitle: str


class StatsMistake(BaseModel):
    """One mistake or strength row shown under a recent activity."""

    label: str
    issue: str
    correction: str | None = None


class RecentActivity(BaseModel):
    """Completed task summary with evaluator and feedback details."""

    id: int
    user_task_id: int
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
    """Everything the frontend stats page needs in one read-only response.

    Range-dependent sections (``period_snapshot``, ``skill_history*``,
    ``practice_patterns``, ``recent_activities``) reflect the requested
    ``range``. ``skill_scores`` and ``difficulty_distribution`` are always
    all-time (the sub-skill overview and difficulty donut ignore the range).
    """

    range: Literal["week", "month", "all"]
    period_snapshot: PeriodSnapshot
    curriculum_milestone: CurriculumMilestone
    practice_patterns: PracticePatterns
    weekly_snapshot: WeeklySnapshot
    skill_scores: list[SkillScoreSnapshot]
    weekly_points_by_skill: dict[int, int]
    difficulty_distribution: DifficultyDistribution
    skill_history_labels: list[str]
    skill_history: list[SkillHistorySeries]
    feedback: StatsFeedback
    recent_activities: list[RecentActivity]


class SkillPointsRead(BaseModel):
    """Current points for one (user, skill) pair."""

    model_config = ConfigDict(from_attributes=True)

    skill_id: int
    points: int
    display_score: float


class SkillPointsLogRead(BaseModel):
    """One row from the points-earned audit log."""

    model_config = ConfigDict(from_attributes=True)

    skill_id: int
    points_earned: int
    reason: str
    created_at: datetime


class SkillWithPointsRead(BaseModel):
    """Combined WMA + points view for a single skill (dashboard-friendly)."""

    skill_id: int
    skill_name: str
    display_label: str
    wma_score: float
    points_score: float
    points: int
