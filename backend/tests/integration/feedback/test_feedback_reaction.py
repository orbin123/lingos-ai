"""Tests for the unified feedback-reaction system (learner 👍/👎).

Exercises the FeedbackReactionService directly: create / switch / toggle-off,
ownership enforcement, the one-row-per-target invariant, and both feedback
types (per-activity feedback + the session Coach's Note).
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (populate the mapper registry)
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.feedback.service import FeedbackReactionService, lookup_reaction
from app.modules.sessions.models import (
    ActivityAttempt,
    ActivityFeedback,
    AttemptStatus,
    DailySession,
    FeedbackReaction,
    FeedbackType,
    ReactionValue,
    SessionScorecard,
    SessionStatus,
)

NOW = datetime.now(timezone.utc)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            DailySession.__table__,
            ActivityAttempt.__table__,
            ActivityFeedback.__table__,
            SessionScorecard.__table__,
            FeedbackReaction.__table__,
        ],
    )
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    yield session
    session.close()


def _user(db, name: str) -> User:
    user = User(
        name=name,
        email=f"{name.lower()}@example.com",
        password_hash="x",
        is_active=True,
        email_verified=True,
        created_at=NOW,
    )
    db.add(user)
    db.flush()
    return user


def _seed(db, user: User) -> tuple[ActivityFeedback, SessionScorecard]:
    session = DailySession(
        session_id=f"sess-{user.id}",
        user_id=user.id,
        day_id="day_48_01_01",
        course_length="48w",
        status=SessionStatus.COMPLETED,
        started_at=NOW,
        completed_at=NOW,
    )
    db.add(session)
    db.flush()
    attempt = ActivityAttempt(
        session_id=session.id,
        archetype_id="WRITE_ERROR_CORR",
        sequence=1,
        status=AttemptStatus.EVALUATED,
        task_content={},
    )
    db.add(attempt)
    db.flush()
    feedback = ActivityFeedback(
        attempt_id=attempt.id,
        score=6,
        summary="Good effort",
        did_well=["clarity"],
        mistakes=[{"issue": "tense"}],
        next_tip="Watch verb tense",
        sub_skill_breakdown={},
    )
    db.add(feedback)
    scorecard = SessionScorecard(
        session_id=session.id,
        points_earned={},
        subskill_totals_after={},
        dashboard_after={},
        completed_at=NOW,
        mentor_note="You keep mixing past and present tense.",
    )
    db.add(scorecard)
    db.flush()
    return feedback, scorecard


def _count(db) -> int:
    return db.query(func.count(FeedbackReaction.id)).scalar() or 0


def test_create_switch_and_toggle_off(db):
    learner = _user(db, "Learner")
    feedback, _ = _seed(db, learner)
    db.commit()
    svc = FeedbackReactionService(db)

    # Create.
    result = svc.set_reaction(
        learner,
        feedback_id=feedback.id,
        feedback_type=FeedbackType.ACTIVITY_FEEDBACK,
        reaction=ReactionValue.LIKE,
    )
    assert result == ReactionValue.LIKE
    assert _count(db) == 1

    # Switch like -> dislike updates in place (still one row).
    result = svc.set_reaction(
        learner,
        feedback_id=feedback.id,
        feedback_type=FeedbackType.ACTIVITY_FEEDBACK,
        reaction=ReactionValue.DISLIKE,
    )
    assert result == ReactionValue.DISLIKE
    assert _count(db) == 1

    # Re-sending the stored reaction clears it (toggle-off).
    result = svc.set_reaction(
        learner,
        feedback_id=feedback.id,
        feedback_type=FeedbackType.ACTIVITY_FEEDBACK,
        reaction=ReactionValue.DISLIKE,
    )
    assert result is None
    assert _count(db) == 0


def test_get_reaction_and_lookup(db):
    learner = _user(db, "Learner")
    _, scorecard = _seed(db, learner)
    db.commit()
    svc = FeedbackReactionService(db)

    assert (
        svc.get_reaction(
            learner,
            feedback_id=scorecard.id,
            feedback_type=FeedbackType.COACH_NOTE,
        )
        is None
    )

    svc.set_reaction(
        learner,
        feedback_id=scorecard.id,
        feedback_type=FeedbackType.COACH_NOTE,
        reaction=ReactionValue.LIKE,
    )
    assert (
        svc.get_reaction(
            learner,
            feedback_id=scorecard.id,
            feedback_type=FeedbackType.COACH_NOTE,
        )
        == ReactionValue.LIKE
    )
    # The reusable hydration helper returns the raw string value.
    assert (
        lookup_reaction(
            db,
            user_id=learner.id,
            feedback_id=scorecard.id,
            feedback_type=FeedbackType.COACH_NOTE.value,
        )
        == "LIKE"
    )


def test_reaction_rejects_non_owner(db):
    owner = _user(db, "Owner")
    intruder = _user(db, "Intruder")
    feedback, scorecard = _seed(db, owner)
    db.commit()
    svc = FeedbackReactionService(db)

    with pytest.raises(LookupError):
        svc.set_reaction(
            intruder,
            feedback_id=feedback.id,
            feedback_type=FeedbackType.ACTIVITY_FEEDBACK,
            reaction=ReactionValue.LIKE,
        )
    with pytest.raises(LookupError):
        svc.set_reaction(
            intruder,
            feedback_id=scorecard.id,
            feedback_type=FeedbackType.COACH_NOTE,
            reaction=ReactionValue.LIKE,
        )
    assert _count(db) == 0


def test_reaction_rejects_missing_target(db):
    learner = _user(db, "Learner")
    db.commit()
    with pytest.raises(LookupError):
        FeedbackReactionService(db).set_reaction(
            learner,
            feedback_id=99999,
            feedback_type=FeedbackType.ACTIVITY_FEEDBACK,
            reaction=ReactionValue.LIKE,
        )
