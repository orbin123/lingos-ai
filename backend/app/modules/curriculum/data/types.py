"""Shared curriculum blueprint dataclasses for level-band source files."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Theme = Literal["grammar", "communication", "vocabulary", "confidence"]
ActivityKind = Literal["read", "write", "listen", "speak"]
LevelBand = Literal["A1A2", "B1B2", "C1C2"]


@dataclass(frozen=True)
class TeacherStep:
    id: str
    goal: str
    instruction: str
    stop_after: bool = True


@dataclass(frozen=True)
class TeacherBlueprint:
    style: str = "strict_kind_a1_friendly"
    lesson_goal: str = ""
    steps: tuple[TeacherStep, ...] = ()
    readiness_prompt: str = "Ready to try the practice task?"


@dataclass(frozen=True)
class TaskBlueprint:
    archetype_id: str
    activity: ActivityKind
    task_widget: str
    topic_override: str = ""
    generation_instructions: str = ""
    widget_requirements: str = ""
    static_payload: dict[str, Any] | None = None


@dataclass(frozen=True)
class EvaluationBlueprint:
    evaluator: str = "default"
    evaluation_widget: str = "activity_score"
    rubric: dict[str, Any] = field(default_factory=dict)
    overrides: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FeedbackBlueprint:
    generator: str = "default"
    feedback_widget: str = "feedback_card"
    overrides: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActivityBlueprint:
    id: str
    sequence: int
    task: TaskBlueprint
    evaluation: EvaluationBlueprint = field(default_factory=EvaluationBlueprint)
    feedback: FeedbackBlueprint = field(default_factory=FeedbackBlueprint)
    mandatory: bool = True


@dataclass(frozen=True)
class FinalReviewBlueprint:
    scorecard_widget: str = "final_scorecard"
    rag_feedback_widget: str = "rag_feedback"


@dataclass(frozen=True)
class DaySource:
    title: str = ""
    description: str = ""
    teacher: TeacherBlueprint = field(default_factory=TeacherBlueprint)
    activities: tuple[ActivityBlueprint, ...] = ()
    final_review: FinalReviewBlueprint = field(default_factory=FinalReviewBlueprint)
    depth_day: DaySource | None = None

    focus: str = ""
    tags: tuple[str, ...] = ()

    def __iter__(self):
        yield self.title
        yield self.description


@dataclass(frozen=True)
class WeekSource:
    week_number: int
    theme_type: Theme
    cefr_level: str
    sub_level_min: int
    sub_level_max: int
    days: tuple[DaySource, ...]
    title: str = ""
    learning_goal: str = ""
