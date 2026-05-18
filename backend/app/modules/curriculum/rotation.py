"""DEPRECATED — Phase 7. Skill-as-spine is dead.

The new sessions flow uses theme-week + day-topic from `curriculum_v2`
and a deterministic planner (`app.modules.sessions.planner`). This
rotation engine + `WEEK_SCHEDULE` only serve the legacy /tasks/next
bundle path. Phase 8 retires both.

Rotation engine — decides which (skill, activity, difficulty) the user
should practice today.

This module is INTENTIONALLY DB-FREE. It takes plain data in, returns plain
data out. No SQLAlchemy. No commits. The service layer fetches the data,
calls into here, and writes the results.

Why? Pure logic is easy to test. Pedagogy rules will evolve — keeping them
out of DB code means we can change them without DB risk.

Inputs:
  - week_number          : 1..duration_weeks
  - day_in_week          : 1..7
  - skill_name_to_id     : {'grammar': 1, 'vocabulary': 2, ...}
  - history_by_skill_id  : legacy input, not used by the weekly rotation

Output:
  - Plan(skill_id, activity_type, target_difficulty)
"""

from dataclasses import dataclass

from app.modules.curriculum.constants import (
    SKILL_ACTIVITIES,
    WEEK_SCHEDULE,
    difficulty_for_week,
)
from app.modules.tasks.models import TaskType


@dataclass(frozen=True)
class Plan:
    """The rotation engine's recommendation for today."""

    skill_id: int
    skill_name: str          # convenience for logging / future LLM prompts
    activity_type: TaskType
    target_difficulty: int
    activity_cycle_length: int
    week_number: int
    day_in_week: int

    def __repr__(self) -> str:
        return (
            f"Plan(skill={self.skill_name}, activity={self.activity_type.value}, "
            f"difficulty={self.target_difficulty})"
        )
    
class RotationEngine:
    """Decides today's plan based on enrollment state and skill history.

    Stateless: same inputs always produce the same output.

    Decision flow:
      1. Pick the skill — fixed by day_in_week (WEEK_SCHEDULE).
      2. Pick the activity — weekly round-robin from SKILL_ACTIVITIES[skill].
         Week 1 uses the first allowed activity, week 2 the next, and so on.
      3. Pick the difficulty — from the week-number curve.
    """

    def decide(
        self,
        *,
        week_number: int,
        day_in_week: int,
        skill_name_to_id: dict[str, int],
        history_by_skill_id: dict[int, TaskType | None],
        allowed_activity_types: set[TaskType] | None = None,
    ) -> Plan:
        """Return today's plan.

        Args:
            week_number: 1-based, 1..duration_weeks of the course.
            day_in_week: 1..7. Day 1 is the first day of the week.
            skill_name_to_id: maps skill names ('grammar') to DB ids.
            history_by_skill_id: legacy per-skill activity memory. The weekly
                rotation does not read it, but services still pass it while
                existing history rows are kept for analytics/backward data.
            allowed_activity_types: optional user preference filter over the
                four core activity types.

        Raises:
            ValueError: invalid day_in_week, missing skill in name_to_id, or
                an empty allowed-activities list (config error).
        """
        # ---- 1. Pick the skill ----
        if day_in_week not in WEEK_SCHEDULE:
            raise ValueError(
                f"day_in_week must be 1..7, got {day_in_week}"
            )
        skill_name = WEEK_SCHEDULE[day_in_week]
        if skill_name not in skill_name_to_id:
            raise ValueError(
                f"Skill {skill_name!r} not in DB. Did you run seed_skills?"
            )

        skill_id = skill_name_to_id[skill_name]
        configured = SKILL_ACTIVITIES.get(skill_name, [])
        if not configured:
            raise ValueError(f"No activities configured for skill {skill_name!r}")

        allowed = (
            [activity for activity in configured if activity in allowed_activity_types]
            if allowed_activity_types is not None
            else configured
        )
        if not allowed:
            raise ValueError(
                f"No enabled activities can be matched to scheduled skill {skill_name!r}"
            )

        activity_type = self._activity_for_week(allowed, week_number)

        # ---- 3. Pick the difficulty ----
        target_difficulty = difficulty_for_week(week_number)

        return Plan(
            skill_id=skill_id,
            skill_name=skill_name,
            activity_type=activity_type,
            target_difficulty=target_difficulty,
            activity_cycle_length=len(allowed),
            week_number=week_number,
            day_in_week=day_in_week,
        )

    @staticmethod
    def _activity_for_week(
        allowed: list[TaskType],
        week_number: int,
    ) -> TaskType:
        """Weekly round-robin through the allowed activities.

        - Week 1 → first activity
        - Week 2 → second activity
        - Week N beyond the list length → wrap around
        """
        week_index = max(week_number, 1) - 1
        return allowed[week_index % len(allowed)]
    
