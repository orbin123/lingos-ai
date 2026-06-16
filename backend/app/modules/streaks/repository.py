"""Repositories for streak module — read/write helpers, no business logic."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.streaks.models import DailyActivity, StreakFreezeUsage


class DailyActivityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_for_date(self, *, user_id: int, local_date: date) -> DailyActivity | None:
        return self.db.execute(
            select(DailyActivity).where(
                DailyActivity.user_id == user_id,
                DailyActivity.local_date == local_date,
            )
        ).scalar_one_or_none()

    def exists_for_date(self, *, user_id: int, local_date: date) -> bool:
        return self.get_for_date(user_id=user_id, local_date=local_date) is not None

    def list_in_range(
        self,
        *,
        user_id: int,
        start: date,
        end: date,
    ) -> list[DailyActivity]:
        return list(
            self.db.execute(
                select(DailyActivity)
                .where(
                    DailyActivity.user_id == user_id,
                    DailyActivity.local_date >= start,
                    DailyActivity.local_date <= end,
                )
                .order_by(DailyActivity.local_date.asc())
            ).scalars()
        )

    def add(self, row: DailyActivity) -> DailyActivity:
        self.db.add(row)
        self.db.flush()
        return row


class StreakFreezeUsageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, row: StreakFreezeUsage) -> StreakFreezeUsage:
        self.db.add(row)
        self.db.flush()
        return row

    def list_in_range(
        self,
        *,
        user_id: int,
        start: date,
        end: date,
    ) -> list[StreakFreezeUsage]:
        return list(
            self.db.execute(
                select(StreakFreezeUsage)
                .where(
                    StreakFreezeUsage.user_id == user_id,
                    StreakFreezeUsage.protected_date >= start,
                    StreakFreezeUsage.protected_date <= end,
                )
                .order_by(StreakFreezeUsage.protected_date.asc())
            ).scalars()
        )
