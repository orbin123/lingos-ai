"""Planner unit tests — pure logic, no DB or service."""

from __future__ import annotations

import pytest

from app.modules.curriculum.models import CurriculumDay
from app.modules.sessions.exceptions import (
    InvalidTasksPerDay,
    NoActivitiesPlanned,
)
from app.modules.sessions.planner import plan_session


def _make_day(
    *,
    mandatory: list[str],
    suggested: dict[str, list[str]],
    day_id: str = "day_24_99_01",
) -> CurriculumDay:
    """Build an unattached CurriculumDay for planner input."""
    return CurriculumDay(
        day_id=day_id,
        week_id=0,
        day_number=1,
        topic="t",
        explanation_brief="b",
        default_activities=["read", "write", "listen", "speak"],
        mandatory_activities=mandatory,
        suggested_archetypes=suggested,
    )


class TestPlanSession:
    def test_picks_mandatory_first_then_optional(self):
        day = _make_day(
            mandatory=["read", "write"],
            suggested={
                "read": ["READ_CLOZE"],
                "write": ["WRITE_SENT_TRANS"],
                "listen": ["LISTEN_MCQ"],
                "speak": ["SPEAK_TIMED"],
            },
        )
        plan = plan_session(
            day,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        assert [(a.sequence, a.archetype_id, a.is_mandatory) for a in plan] == [
            (1, "READ_CLOZE", True),
            (2, "WRITE_SENT_TRANS", True),
            (3, "LISTEN_MCQ", False),
            (4, "SPEAK_TIMED", False),
        ]

    def test_caps_at_tasks_per_day(self):
        day = _make_day(
            mandatory=["read", "write"],
            suggested={
                "read": ["READ_CLOZE"],
                "write": ["WRITE_SENT_TRANS"],
                "listen": ["LISTEN_MCQ"],
                "speak": ["SPEAK_TIMED"],
            },
        )
        plan = plan_session(
            day,
            tasks_per_day=2,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        assert len(plan) == 2
        assert all(a.is_mandatory for a in plan)

    def test_drops_disabled_optional_activity(self):
        day = _make_day(
            mandatory=["read", "write"],
            suggested={
                "read": ["READ_CLOZE"],
                "write": ["WRITE_SENT_TRANS"],
                "listen": ["LISTEN_MCQ"],
                "speak": ["SPEAK_TIMED"],
            },
        )
        plan = plan_session(
            day,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen"},  # speak off
        )
        # 4 slots requested, but speak disabled -> only 3 produced.
        activities = [a.archetype_id for a in plan]
        assert activities == ["READ_CLOZE", "WRITE_SENT_TRANS", "LISTEN_MCQ"]

    def test_mandatory_activity_dropped_when_user_disabled(self):
        day = _make_day(
            mandatory=["listen", "speak"],
            suggested={
                "read": ["READ_CLOZE"],
                "write": ["WRITE_SENT_TRANS"],
                "listen": ["LISTEN_MCQ"],
                "speak": ["SPEAK_TIMED"],
            },
        )
        plan = plan_session(
            day,
            tasks_per_day=4,
            allowed_activities={"read", "write", "speak"},  # listen off (mandatory!)
        )
        # listen mandatory but disabled — its slot is empty; optionals fill.
        ids = [a.archetype_id for a in plan]
        assert "LISTEN_MCQ" not in ids
        assert "SPEAK_TIMED" in ids

    def test_first_suggested_archetype_wins(self):
        """Deterministic pick — first suggestion in the list, regardless of theme."""
        day = _make_day(
            mandatory=["read"],
            suggested={
                "read": ["READ_TFNG", "READ_CLOZE", "READ_COMP_MCQ"],
                "write": ["WRITE_PARA"],
            },
        )
        plan = plan_session(day, tasks_per_day=2, allowed_activities={"read", "write"})
        assert plan[0].archetype_id == "READ_TFNG"

    def test_invalid_tasks_per_day_raises(self):
        day = _make_day(mandatory=["read"], suggested={"read": ["READ_CLOZE"]})
        with pytest.raises(InvalidTasksPerDay):
            plan_session(day, tasks_per_day=1, allowed_activities={"read"})
        with pytest.raises(InvalidTasksPerDay):
            plan_session(day, tasks_per_day=5, allowed_activities={"read"})

    def test_empty_plan_raises(self):
        day = _make_day(
            mandatory=["read"],
            suggested={"read": []},  # no suggestions
        )
        with pytest.raises(NoActivitiesPlanned):
            plan_session(day, tasks_per_day=2, allowed_activities={"read"})

    def test_all_activities_disabled_raises(self):
        day = _make_day(
            mandatory=["read"],
            suggested={"read": ["READ_CLOZE"], "write": ["WRITE_SENT_TRANS"]},
        )
        with pytest.raises(NoActivitiesPlanned):
            plan_session(day, tasks_per_day=2, allowed_activities=set())

    def test_is_deterministic(self):
        day = _make_day(
            mandatory=["read", "write"],
            suggested={
                "read": ["READ_CLOZE", "READ_COMP_MCQ"],
                "write": ["WRITE_SENT_TRANS"],
                "listen": ["LISTEN_MCQ"],
                "speak": ["SPEAK_TIMED"],
            },
        )
        runs = [
            plan_session(
                day,
                tasks_per_day=3,
                allowed_activities={"read", "write", "listen", "speak"},
            )
            for _ in range(5)
        ]
        first = [(a.sequence, a.archetype_id) for a in runs[0]]
        for run in runs[1:]:
            assert [(a.sequence, a.archetype_id) for a in run] == first
