"""Thin repositories for curriculum tables.

Data-access only: no business logic, no scoring decisions. The session
planner reads through these.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.curriculum.models import (
    CurriculumDay,
    CurriculumWeek,
    TaskArchetype,
)


class CurriculumWeekRepository:
    """Read/write `curriculum_weeks` rows."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_week_id(self, week_id: str) -> CurriculumWeek | None:
        return self.db.execute(
            select(CurriculumWeek).where(CurriculumWeek.week_id == week_id)
        ).scalar_one_or_none()

    def get_by_number(
        self, *, course_length: str, week_number: int
    ) -> CurriculumWeek | None:
        return self.db.execute(
            select(CurriculumWeek).where(
                CurriculumWeek.course_length == course_length,
                CurriculumWeek.week_number == week_number,
            )
        ).scalar_one_or_none()

    def list_for_course(
        self, course_length: str, *, with_days: bool = False
    ) -> list[CurriculumWeek]:
        stmt = (
            select(CurriculumWeek)
            .where(CurriculumWeek.course_length == course_length)
            .order_by(CurriculumWeek.week_number)
        )
        if with_days:
            stmt = stmt.options(selectinload(CurriculumWeek.days))
        return list(self.db.execute(stmt).scalars())


class CurriculumDayRepository:
    """Read `curriculum_days` rows."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_day_id(self, day_id: str) -> CurriculumDay | None:
        return self.db.execute(
            select(CurriculumDay).where(CurriculumDay.day_id == day_id)
        ).scalar_one_or_none()

    def get_for_week(
        self, *, week_pk: int, day_number: int
    ) -> CurriculumDay | None:
        return self.db.execute(
            select(CurriculumDay).where(
                CurriculumDay.week_id == week_pk,
                CurriculumDay.day_number == day_number,
            )
        ).scalar_one_or_none()


class TaskArchetypeRepository:
    """Read `task_archetypes` rows. The Python registry remains authoritative."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, archetype_id: str) -> TaskArchetype | None:
        return self.db.get(TaskArchetype, archetype_id)

    def list_all(self) -> list[TaskArchetype]:
        return list(self.db.execute(select(TaskArchetype)).scalars())

    def list_by_activity(self, core_activity: str) -> list[TaskArchetype]:
        return list(
            self.db.execute(
                select(TaskArchetype).where(
                    TaskArchetype.core_activity == core_activity
                )
            ).scalars()
        )
