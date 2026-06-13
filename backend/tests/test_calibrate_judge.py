"""Smoke test for the judge-vs-learner calibration script (Part B Phase 3).

Seeds ``ai_evaluations`` + ``feedback_reactions`` rows on in-memory SQLite and
asserts the agreement maths (and the dangerous false-negative count) come out
right. A learner DISLIKE is the human "flag"; a LIKE is a pass.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (populate the mapper registry)
from app.core.database import Base
from app.modules.admin.models import AIEvaluation
from app.modules.sessions.models import (
    FeedbackReaction,
    FeedbackType,
    ReactionValue,
)
from scripts.calibrate_judge import calibrate


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine, tables=[AIEvaluation.__table__, FeedbackReaction.__table__]
    )
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    yield session
    session.close()
    engine.dispose()


def _eval(db, *, target_id, target_type="feedback", **scores):
    row = AIEvaluation(
        trace_id="t",
        target_type=target_type,
        target_id=target_id,
        judge_model="gpt-4.1",
        eval_mode="online",
        **scores,
    )
    db.add(row)
    db.flush()
    return row


def _reaction(
    db, *, feedback_id, reaction, feedback_type=FeedbackType.ACTIVITY_FEEDBACK
):
    row = FeedbackReaction(
        user_id=1,
        feedback_id=feedback_id,
        feedback_type=feedback_type.value,
        reaction=reaction.value,
    )
    db.add(row)
    db.flush()
    return row


def test_calibrate_agreement_and_false_negatives(db):
    # 1) judge pass, learner like  -> TN, agree
    _eval(db, target_id="1", accuracy=8, relevance=8, helpfulness=8, correctness=8)
    _reaction(db, feedback_id=1, reaction=ReactionValue.LIKE)

    # 2) judge flag (corr 3), learner dislike -> TP, agree
    _eval(db, target_id="2", accuracy=7, relevance=7, helpfulness=7, correctness=3)
    _reaction(db, feedback_id=2, reaction=ReactionValue.DISLIKE)

    # 3) judge pass, learner dislike -> FN (the dangerous miss), disagree
    _eval(db, target_id="3", accuracy=8, relevance=8, helpfulness=8, correctness=8)
    _reaction(db, feedback_id=3, reaction=ReactionValue.DISLIKE)

    # 4) judge flag (acc 4), learner like -> FP, disagree
    _eval(db, target_id="4", accuracy=4, relevance=8, helpfulness=8, correctness=8)
    _reaction(db, feedback_id=4, reaction=ReactionValue.LIKE)

    # 5) no reaction -> excluded from matched
    _eval(db, target_id="5", accuracy=8, relevance=8, helpfulness=8, correctness=8)

    # 6) no reaction -> excluded from matched
    _eval(db, target_id="6", accuracy=8, relevance=8, helpfulness=8, correctness=8)

    db.commit()

    report = calibrate(db, limit=100)

    assert report.judged_total == 6
    assert report.matched == 4  # the two un-reacted evals are excluded
    assert report.true_pos == 1
    assert report.true_neg == 1
    assert report.false_pos == 1
    assert report.false_neg == 1
    assert report.agree == 2
    assert report.agreement_rate == 0.5


def test_calibrate_matches_mentor_note_via_coach_note(db):
    # mentor_note target joins feedback_reactions via feedback_type=COACH_NOTE.
    _eval(
        db,
        target_id="42",
        target_type="mentor_note",
        accuracy=8,
        relevance=8,
        helpfulness=8,
        correctness=8,
        faithfulness=2,  # low faithfulness trips the judge flag
    )
    _reaction(
        db,
        feedback_id=42,
        reaction=ReactionValue.DISLIKE,
        feedback_type=FeedbackType.COACH_NOTE,
    )
    db.commit()

    report = calibrate(db, limit=100)
    assert report.matched == 1
    assert report.true_pos == 1
    assert report.agreement_rate == 1.0
