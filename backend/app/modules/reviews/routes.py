"""User-facing app-review endpoints.

The submission UI is added later; this exposes the create endpoint now so the
data path exists. Admin listing lives in the admin module.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.reviews.repository import AppReviewRepository
from app.modules.reviews.schemas import AppReviewCreate, AppReviewRead

reviews_router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@reviews_router.post(
    "",
    response_model=AppReviewRead,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    payload: AppReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AppReviewRead:
    """Submit an app review. Frontend submission UI is a later task."""
    review = AppReviewRepository(db).create(
        user_id=current_user.id,
        rating=payload.rating,
        title=payload.title,
        body=payload.body,
    )
    db.commit()
    db.refresh(review)
    return AppReviewRead.model_validate(review)
