"""Tests for the admin-console rework: subscribers (2-year access window +
trial derivation), feedback reaction analytics, and user progress.

Uses an explicit table subset (like the other session route tests) so the
SQLite engine never has to create the raw-JSONB `learning_sessions` table.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (populate the mapper registry)
from app.core.database import Base
from app.modules.admin.models import AdminAuditLog
from app.modules.admin.service import AdminService
from app.modules.auth.models import Role, User, UserRole
from app.modules.progress.models import SkillPoints
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
from app.modules.skills.models import Skill
from app.modules.subscriptions.models import (
    Purchase,
    Subscription,
    SubscriptionStatus,
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
            Role.__table__,
            UserRole.__table__,
            Skill.__table__,
            SkillPoints.__table__,
            Purchase.__table__,
            Subscription.__table__,
            DailySession.__table__,
            ActivityAttempt.__table__,
            ActivityFeedback.__table__,
            SessionScorecard.__table__,
            FeedbackReaction.__table__,
            AdminAuditLog.__table__,
        ],
    )
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    yield session
    session.close()


def _user(db, name: str, *, days_ago: int) -> User:
    user = User(
        name=name,
        email=f"{name.lower()}@example.com",
        password_hash="x",
        is_active=True,
        email_verified=True,
        created_at=NOW - timedelta(days=days_ago),
    )
    db.add(user)
    db.flush()
    return user


def _paid_purchase(db, user: User, *, expires_in_days: int) -> Purchase:
    purchase = Purchase(
        user_id=user.id,
        plan_id="beginner-48w",
        plan_name="48-Week Plan",
        amount_paid=1999.0,
        currency="INR",
        status="paid",
        access_expires_at=NOW + timedelta(days=expires_in_days),
    )
    db.add(purchase)
    db.flush()
    return purchase


# ── Subscribers ────────────────────────────────────────────────────


def _trial_subscription(db, user: User, *, ends_in_days: int) -> Subscription:
    row = Subscription(
        user_id=user.id,
        provider="internal",
        plan_id="beginner-24w",
        plan_name="24-Week Foundation",
        status=SubscriptionStatus.TRIAL.value,
        trial_started_at=NOW + timedelta(days=ends_in_days - 7),
        trial_ends_at=NOW + timedelta(days=ends_in_days),
    )
    db.add(row)
    db.flush()
    return row


def test_subscribers_split_paying_and_trial(db):
    """Trial state comes from the STORED subscription row (§8.8), never
    derived from signup date."""
    active = _user(db, "Active", days_ago=400)
    expired_sub = _user(db, "ExpiredSub", days_ago=900)
    fresh_trial = _user(db, "FreshTrial", days_ago=2)
    old_trial = _user(db, "OldTrial", days_ago=30)
    never_started = _user(db, "NeverStarted", days_ago=60)
    _paid_purchase(db, active, expires_in_days=300)
    _paid_purchase(db, expired_sub, expires_in_days=-5)
    fresh_row = _trial_subscription(db, fresh_trial, ends_in_days=5)
    _trial_subscription(db, old_trial, ends_in_days=-23)
    db.commit()

    overview = AdminService(db).list_subscribers()

    subs = {s.user_id: s for s in overview.subscribers}
    assert subs[active.id].status == "active"
    assert subs[expired_sub.id].status == "expired"
    assert active.id not in {t.user_id for t in overview.trials}

    trials = {t.user_id: t for t in overview.trials}
    assert trials[fresh_trial.id].status == "trial"
    assert trials[old_trial.id].status == "expired"
    # A verified user who never started a trial is "not_started" — old-signup
    # users no longer look like expired trials.
    assert trials[never_started.id].status == "not_started"
    assert trials[never_started.id].trial_ends_at is None
    # Trial end is the stored value, not signup + TRIAL_DAYS.
    assert trials[fresh_trial.id].trial_ends_at == fresh_row.trial_ends_at


def test_subscriber_access_update_extends_window(db):
    user = _user(db, "Sub", days_ago=10)
    _paid_purchase(db, user, expires_in_days=-1)  # currently expired
    db.commit()

    actor = _user(db, "Admin", days_ago=1)
    db.commit()

    new_expiry = NOW + timedelta(days=365)
    result = AdminService(db).update_subscriber_access(
        user_id=user.id, access_expires_at=new_expiry, actor=actor
    )
    assert result is not None
    assert result.status == "active"
    # Audit row written.
    assert (
        db.query(AdminAuditLog).filter_by(action="purchase.access_update").count() == 1
    )


# ── Feedback analytics (reactions) ─────────────────────────────────


def _react(db, user, *, feedback_id, feedback_type, reaction):
    row = FeedbackReaction(
        user_id=user.id,
        feedback_id=feedback_id,
        feedback_type=feedback_type.value,
        reaction=reaction.value,
    )
    db.add(row)
    db.flush()
    return row


def test_feedback_analytics_lists_both_types_with_reaction(db):
    learner = _user(db, "Learner", days_ago=5)
    feedback, scorecard = _seed_feedback(db, learner)
    _react(
        db,
        learner,
        feedback_id=scorecard.id,
        feedback_type=FeedbackType.COACH_NOTE,
        reaction=ReactionValue.DISLIKE,
    )
    db.commit()

    items = AdminService(db).list_feedback_analytics()
    by_type = {i.feedback_type: i for i in items}
    assert set(by_type) == {"ACTIVITY_FEEDBACK", "COACH_NOTE"}
    assert by_type["ACTIVITY_FEEDBACK"].score == 6.0
    assert by_type["ACTIVITY_FEEDBACK"].user_reaction is None
    assert by_type["COACH_NOTE"].mentor_note.startswith("You keep mixing")
    assert by_type["COACH_NOTE"].user_reaction == "DISLIKE"
    # The disliked item is surfaced first (needs attention).
    assert items[0].feedback_type == "COACH_NOTE"


def test_feedback_analytics_filters_by_type_and_reaction(db):
    learner = _user(db, "Learner", days_ago=5)
    feedback, scorecard = _seed_feedback(db, learner)
    _react(
        db,
        learner,
        feedback_id=feedback.id,
        feedback_type=FeedbackType.ACTIVITY_FEEDBACK,
        reaction=ReactionValue.LIKE,
    )
    db.commit()
    svc = AdminService(db)

    # Type filter.
    coach_only = svc.list_feedback_analytics(feedback_type="COACH_NOTE")
    assert {i.feedback_type for i in coach_only} == {"COACH_NOTE"}

    # Reaction filter: only the liked activity feedback.
    liked = svc.list_feedback_analytics(reaction="LIKE")
    assert len(liked) == 1
    assert liked[0].feedback_type == "ACTIVITY_FEEDBACK"

    # No-reaction filter: only the un-reacted Coach Note.
    none = svc.list_feedback_analytics(reaction="NONE")
    assert {i.feedback_type for i in none} == {"COACH_NOTE"}
    assert none[0].user_reaction is None


def test_feedback_reaction_stats(db):
    learner = _user(db, "Learner", days_ago=5)
    feedback, scorecard = _seed_feedback(db, learner)  # 2 feedback items total
    _react(
        db,
        learner,
        feedback_id=feedback.id,
        feedback_type=FeedbackType.ACTIVITY_FEEDBACK,
        reaction=ReactionValue.LIKE,
    )
    db.commit()

    stats = AdminService(db).feedback_reaction_stats()
    assert stats.total_items == 2  # 1 activity feedback + 1 coach note
    assert stats.liked == 1
    assert stats.disliked == 0
    assert stats.no_reaction == 1
    # liked / (liked + disliked) = 1 / 1.
    assert stats.positive_rate == 1.0


def _seed_feedback(db, user: User) -> tuple[ActivityFeedback, SessionScorecard]:
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


# ── User progress ──────────────────────────────────────────────────


def test_user_progress_reports_activities_and_score(db):
    learner = _user(db, "Learner", days_ago=5)
    _paid_purchase(db, learner, expires_in_days=300)
    _seed_feedback(db, learner)  # one EVALUATED attempt
    skill = Skill(name="Grammar")
    db.add(skill)
    db.flush()
    db.add(
        SkillPoints(
            user_id=learner.id, skill_id=skill.id, points=120, display_score=6.0
        )
    )
    db.commit()

    items = {i.user_id: i for i in AdminService(db).list_user_progress()}
    row = items[learner.id]
    assert row.activities_completed == 1
    assert row.purchase_complete is True
    assert row.plan_id == "beginner-48w"
    assert row.dashboard_score == 6.0
