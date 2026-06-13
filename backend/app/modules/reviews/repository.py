"""Data access for app reviews."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.modules.reviews.models import AppReview


class AppReviewRepository:
    """All DB access for the app-review feature."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        user_id: int,
        rating: int,
        title: str | None,
        body: str | None,
        *,
        positive_feedback: str | None = None,
        improvement_feedback: str | None = None,
        bug_report: str | None = None,
        task_count_when_submitted: int | None = None,
        days_since_signup: int | None = None,
        app_version: str | None = None,
    ) -> AppReview:
        review = AppReview(
            user_id=user_id,
            rating=rating,
            title=title,
            body=body,
            positive_feedback=positive_feedback,
            improvement_feedback=improvement_feedback,
            bug_report=bug_report,
            task_count_when_submitted=task_count_when_submitted,
            days_since_signup=days_since_signup,
            app_version=app_version,
        )
        self.db.add(review)
        self.db.flush()
        return review

    def list_all(self, limit: int = 200) -> list[AppReview]:
        stmt = (
            select(AppReview)
            .order_by(AppReview.created_at.desc(), AppReview.id.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_for_admin(
        self, *, rating: int | None = None, limit: int = 200
    ) -> list[AppReview]:
        """Reviews for the admin list, newest first, with the user eager-loaded.

        ``rating`` narrows to a single star bucket (the admin filter).
        """
        stmt = (
            select(AppReview)
            .options(joinedload(AppReview.user))
            .order_by(AppReview.created_at.desc(), AppReview.id.desc())
        )
        if rating is not None:
            stmt = stmt.where(AppReview.rating == rating)
        stmt = stmt.limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    # ── Aggregates for admin analytics ────────────────────────────────

    def count(self) -> int:
        return self.db.execute(select(func.count(AppReview.id))).scalar_one() or 0

    def average_rating(self) -> float | None:
        return self.db.execute(select(func.avg(AppReview.rating))).scalar_one()

    def rating_distribution(self) -> dict[int, int]:
        """{star: count} for all five buckets (zero-filled)."""
        rows = self.db.execute(
            select(AppReview.rating, func.count(AppReview.id)).group_by(
                AppReview.rating
            )
        ).all()
        dist = {star: 0 for star in range(1, 6)}
        for rating, n in rows:
            if rating in dist:
                dist[rating] = n
        return dist

    def text_fields_since(
        self, since: datetime | None = None
    ) -> list[tuple[str | None, str | None]]:
        """(improvement_feedback, bug_report) pairs for theme tallying."""
        stmt = select(AppReview.improvement_feedback, AppReview.bug_report)
        if since is not None:
            stmt = stmt.where(AppReview.created_at >= since)
        return [tuple(row) for row in self.db.execute(stmt).all()]

    def trend_rows(
        self, since: datetime | None = None
    ) -> list[tuple[datetime, int]]:
        """(created_at, rating) rows for building the day-bucketed trend."""
        stmt = select(AppReview.created_at, AppReview.rating)
        if since is not None:
            stmt = stmt.where(AppReview.created_at >= since)
        stmt = stmt.order_by(AppReview.created_at.asc())
        return [(row[0], row[1]) for row in self.db.execute(stmt).all()]
