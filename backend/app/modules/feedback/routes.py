"""User-facing feedback-prompt endpoints.

The prompt is checked during normal navigation (dashboard / lesson / progress);
the client never decides eligibility — it only relays the server's verdict.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.feedback.schemas import (
    DismissResponse,
    FeedbackSubmit,
    FeedbackSubmitResponse,
    ShouldShowResponse,
)
from app.modules.feedback.service import FeedbackPromptService

feedback_router = APIRouter(prefix="/feedback", tags=["feedback"])


@feedback_router.get("/should-show", response_model=ShouldShowResponse)
def should_show(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ShouldShowResponse:
    """Whether to surface the feedback prompt for this user right now."""
    return FeedbackPromptService(db).should_show(current_user)


@feedback_router.post(
    "/submit",
    response_model=FeedbackSubmitResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_feedback(
    payload: FeedbackSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeedbackSubmitResponse:
    review = FeedbackPromptService(db).record_submit(current_user, payload)
    return FeedbackSubmitResponse(review_id=review.id, created_at=review.created_at)


@feedback_router.post("/dismiss", response_model=DismissResponse)
def dismiss_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DismissResponse:
    FeedbackPromptService(db).record_dismiss(current_user)
    return DismissResponse(dismissed=True)
