from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.modules.auth.models import User
from app.modules.challenges.models import (
    Challenge,
    ChallengeAttempt,
    ChallengeAttemptStatus,
    ChallengeLevel,
)
from app.modules.challenges.ielts_sprint.service import ChallengeReadService
from scripts.seed_ielts_challenge import seed_ielts_challenge


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            Challenge.__table__,
            ChallengeLevel.__table__,
            ChallengeAttempt.__table__,
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _make_user(db: Session) -> User:
    user = User(
        email="learner@example.com",
        password_hash="x",
        name="Learner",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _completed_attempt(
    db: Session,
    *,
    user_id: int,
    level_id: int,
    score: float,
    started_offset_minutes: int = 0,
) -> ChallengeAttempt:
    now = datetime.now(timezone.utc) + timedelta(minutes=started_offset_minutes)
    attempt = ChallengeAttempt(
        user_id=user_id,
        challenge_level_id=level_id,
        status=ChallengeAttemptStatus.COMPLETED,
        started_at=now,
        completed_at=now + timedelta(minutes=5),
        expires_at=now + timedelta(minutes=20),
        task_payload={"reading": {"questions": []}},
        response_payload={"reading": {}},
        overall_score=score,
        section_scores={"reading": score},
        passed=score >= 6.0,
        evaluation_report={"overall": "stub"},
        feedback_report={"summary": "stub"},
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def test_seed_ielts_challenge_is_idempotent(db_session: Session) -> None:
    first = seed_ielts_challenge(db_session)
    db_session.commit()
    second = seed_ielts_challenge(db_session)
    db_session.commit()

    challenge = db_session.query(Challenge).filter_by(slug="ielts").one()
    levels = (
        db_session.query(ChallengeLevel)
        .filter_by(challenge_id=challenge.id)
        .order_by(ChallengeLevel.level_number)
        .all()
    )

    assert first == {"inserted": 4, "updated": 0}
    assert second == {"inserted": 0, "updated": 0}
    assert challenge.name == "IELTS Sprint"
    assert challenge.icon == "award"
    assert [level.time_limit_seconds for level in levels] == [1200, 1800, 2400]
    assert levels[0].config["sections"]["reading"]["num_questions"] == 4


def test_unique_challenge_level_per_challenge(db_session: Session) -> None:
    seed_ielts_challenge(db_session)
    db_session.commit()
    challenge = db_session.query(Challenge).filter_by(slug="ielts").one()
    db_session.add(
        ChallengeLevel(
            challenge_id=challenge.id,
            level_number=1,
            name="Duplicate",
            time_limit_seconds=1200,
            pass_threshold=6.0,
            config={"sections": {}},
        )
    )

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_detail_tracks_best_scores_counts_and_unlocks(db_session: Session) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)
    challenge = db_session.query(Challenge).filter_by(slug="ielts").one()
    levels = (
        db_session.query(ChallengeLevel)
        .filter_by(challenge_id=challenge.id)
        .order_by(ChallengeLevel.level_number)
        .all()
    )
    _completed_attempt(db_session, user_id=user.id, level_id=levels[0].id, score=5.5)
    _completed_attempt(db_session, user_id=user.id, level_id=levels[0].id, score=6.5)
    _completed_attempt(db_session, user_id=user.id, level_id=levels[1].id, score=5.0)

    detail = ChallengeReadService(db_session).get_detail(
        slug="ielts",
        user_id=user.id,
    )

    assert [level.unlocked for level in detail.levels] == [True, True, False]
    assert [level.best_score for level in detail.levels] == [6.5, 5.0, None]
    assert [level.attempt_count for level in detail.levels] == [2, 1, 0]


def test_history_marks_best_attempt_per_level(db_session: Session) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)
    challenge = db_session.query(Challenge).filter_by(slug="ielts").one()
    level = (
        db_session.query(ChallengeLevel)
        .filter_by(challenge_id=challenge.id, level_number=1)
        .one()
    )
    low = _completed_attempt(
        db_session,
        user_id=user.id,
        level_id=level.id,
        score=5.5,
        started_offset_minutes=-10,
    )
    high = _completed_attempt(
        db_session,
        user_id=user.id,
        level_id=level.id,
        score=7.0,
        started_offset_minutes=0,
    )

    history = ChallengeReadService(db_session).get_history(
        slug="ielts",
        user_id=user.id,
    )

    rows_by_id = {row.id: row for row in history.attempts}
    assert [row.id for row in history.attempts] == [high.id, low.id]
    assert rows_by_id[low.id].is_best_for_level is False
    assert rows_by_id[high.id].is_best_for_level is True


def test_timed_out_passing_score_unlocks_next_level(db_session: Session) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)
    challenge = db_session.query(Challenge).filter_by(slug="ielts").one()
    level = (
        db_session.query(ChallengeLevel)
        .filter_by(challenge_id=challenge.id, level_number=1)
        .one()
    )
    now = datetime.now(timezone.utc)
    db_session.add(
        ChallengeAttempt(
            user_id=user.id,
            challenge_level_id=level.id,
            status=ChallengeAttemptStatus.TIMED_OUT,
            started_at=now - timedelta(minutes=25),
            timer_started_at=now - timedelta(minutes=25),
            completed_at=now - timedelta(minutes=1),
            expires_at=now - timedelta(minutes=5),
            task_payload={"sections": {}},
            response_payload={"reading": {}},
            overall_score=6.5,
            section_scores={"reading": 6.5},
            passed=True,
            evaluation_report={"overall": "stub"},
            feedback_report={"summary": "stub"},
        )
    )
    db_session.commit()

    detail = ChallengeReadService(db_session).get_detail(
        slug="ielts",
        user_id=user.id,
    )

    assert detail.levels[0].best_score == 6.5
    assert detail.levels[1].unlocked is True

