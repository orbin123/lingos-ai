"""Data access for app reviews."""

from sqlalchemy import select
from sqlalchemy.orm import Session

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
    ) -> AppReview:
        review = AppReview(
            user_id=user_id,
            rating=rating,
            title=title,
            body=body,
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
