"""Course topic lookup for week/day learning plans.

Each curriculum entry is objective-driven: it pairs a communication goal
(what the learner should be able to *do*) with a language focus (the
linguistic anchor — grammar pattern, sound set, fluency drill, etc.).
The Planner combines this objective with the learner's structured
personalisation to pick the concrete scenario.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CourseTopic:
    week: int
    day: int
    topic_id: str
    sub_skill: str
    sub_level: int
    communication_goal: str
    language_focus: str

    @property
    def display_label(self) -> str:
        """Human-readable label used by legacy consumers (frontend, task content)."""
        return f"{self.communication_goal} — {self.language_focus}"


_COURSE_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "courses"


@lru_cache(maxsize=2)
def _load_topics(duration_weeks: int) -> dict[tuple[int, int], CourseTopic]:
    filename = f"topics_{duration_weeks}w.json"
    path = _COURSE_DATA_DIR / filename
    with path.open("r", encoding="utf-8") as fh:
        payload: dict[str, Any] = json.load(fh)

    topics: dict[tuple[int, int], CourseTopic] = {}
    for item in payload.get("topics", []):
        topic = CourseTopic(
            week=int(item["week"]),
            day=int(item["day"]),
            topic_id=str(item["topic_id"]),
            sub_skill=str(item["sub_skill"]),
            sub_level=int(item["sub_level"]),
            communication_goal=str(item["communication_goal"]),
            language_focus=str(item["language_focus"]),
        )
        topics[(topic.week, topic.day)] = topic
    return topics


def get_course_topic(
    *,
    duration_weeks: int,
    week: int,
    day: int,
) -> CourseTopic | None:
    """Return the configured topic for a course week/day, if available."""
    try:
        topics = _load_topics(duration_weeks)
    except FileNotFoundError:
        return None
    return topics.get((week, day))
