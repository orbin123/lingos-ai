from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.challenges.models import (
    Challenge,
    ChallengeAttempt,
    ChallengeAttemptStatus,
    ChallengeLevel,
)
from app.modules.challenges.routes import router as challenges_router
from scripts.seed_ielts_challenge import seed_ielts_challenge


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
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


@pytest.fixture()
def learner(db_session: Session) -> User:
    user = User(
        email="learner@example.com",
        password_hash="x",
        name="Learner",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def client(db_session: Session, learner: User):
    app = FastAPI()
    app.include_router(challenges_router, prefix="/api")

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return learner

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _make_attempt(db: Session, *, user_id: int) -> ChallengeAttempt:
    seed_ielts_challenge(db)
    challenge = db.query(Challenge).filter_by(slug="ielts").one()
    level = (
        db.query(ChallengeLevel)
        .filter_by(challenge_id=challenge.id, level_number=1)
        .one()
    )
    now = datetime.now(timezone.utc)
    attempt = ChallengeAttempt(
        user_id=user_id,
        challenge_level_id=level.id,
        status=ChallengeAttemptStatus.COMPLETED,
        started_at=now,
        completed_at=now + timedelta(minutes=4),
        expires_at=now + timedelta(minutes=20),
        task_payload={"reading": {"questions": []}},
        response_payload={"reading": {}},
        overall_score=6.5,
        section_scores={"reading": 6.5},
        passed=True,
        evaluation_report={"overall": "stub"},
        feedback_report={"summary": "stub"},
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def test_all_challenge_read_routes_are_mounted() -> None:
    app = FastAPI()
    app.include_router(challenges_router, prefix="/api")
    paths = [route.path for route in app.router.routes]

    assert "/api/v1/challenges" in paths
    assert "/api/v1/challenges/{slug}" in paths
    assert "/api/v1/challenges/{slug}/history" in paths
    assert "/api/v1/challenge-attempts/{attempt_id}" in paths


def test_list_challenges(client: TestClient, db_session: Session) -> None:
    seed_ielts_challenge(db_session)
    db_session.commit()

    response = client.get("/api/v1/challenges")

    assert response.status_code == 200
    body = response.json()
    assert body[0]["slug"] == "ielts"
    assert body[0]["level_count"] == 3


def test_challenge_detail_includes_progress(
    client: TestClient,
    db_session: Session,
    learner: User,
) -> None:
    _make_attempt(db_session, user_id=learner.id)

    response = client.get("/api/v1/challenges/ielts")

    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "ielts"
    assert body["levels"][0]["best_score"] == 6.5
    assert body["levels"][0]["attempt_count"] == 1
    assert body["levels"][1]["unlocked"] is True


def test_challenge_history_is_personal_and_marks_best(
    client: TestClient,
    db_session: Session,
    learner: User,
) -> None:
    attempt = _make_attempt(db_session, user_id=learner.id)

    response = client.get("/api/v1/challenges/ielts/history")

    assert response.status_code == 200
    body = response.json()
    assert body["challenge_slug"] == "ielts"
    assert body["attempts"][0]["id"] == attempt.id
    assert body["attempts"][0]["is_best_for_level"] is True


def test_get_attempt_requires_current_user(
    client: TestClient,
    db_session: Session,
    learner: User,
) -> None:
    attempt = _make_attempt(db_session, user_id=learner.id)
    other = User(email="other@example.com", password_hash="x", name="Other")
    db_session.add(other)
    db_session.commit()
    foreign_attempt = _make_attempt(db_session, user_id=other.id)

    own_response = client.get(f"/api/v1/challenge-attempts/{attempt.id}")
    foreign_response = client.get(f"/api/v1/challenge-attempts/{foreign_attempt.id}")

    assert own_response.status_code == 200
    assert own_response.json()["id"] == attempt.id
    assert foreign_response.status_code == 404
