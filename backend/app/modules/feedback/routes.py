"""User-facing feedback-prompt endpoints.

The prompt is checked during normal navigation (dashboard / lesson / progress);
the client never decides eligibility — it only relays the server's verdict.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.feedback.schemas import (
    DismissResponse,
    FeedbackSubmit,
    FeedbackSubmitResponse,
    ReactionRequest,
    ReactionResponse,
    ShouldShowResponse,
)
from app.modules.feedback.service import FeedbackPromptService, FeedbackReactionService
from app.modules.sessions.models import FeedbackType

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


@feedback_router.post("/reaction", response_model=ReactionResponse)
def set_reaction(
    payload: ReactionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReactionResponse:
    """Set, switch, or clear (toggle-off) the learner's reaction to feedback."""
    try:
        result = FeedbackReactionService(db).set_reaction(
            current_user,
            feedback_id=payload.feedback_id,
            feedback_type=payload.feedback_type,
            reaction=payload.reaction,
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return ReactionResponse(user_reaction=result)


@feedback_router.get("/reaction", response_model=ReactionResponse)
def get_reaction(
    feedback_id: int,
    feedback_type: FeedbackType,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReactionResponse:
    """The current learner's reaction to one feedback target (null if none)."""
    result = FeedbackReactionService(db).get_reaction(
        current_user, feedback_id=feedback_id, feedback_type=feedback_type
    )
    return ReactionResponse(user_reaction=result)
