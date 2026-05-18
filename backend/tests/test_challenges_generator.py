from __future__ import annotations

import logging
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.ai.llm import LLMProviderError
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.challenges.generator_schemas import GeneratedIELTSTaskPayload
from app.modules.challenges.models import (
    Challenge,
    ChallengeAttempt,
    ChallengeAttemptStatus,
    ChallengeLevel,
)
from app.modules.challenges.service import ChallengeReadService
from scripts.seed_ielts_challenge import seed_ielts_challenge


def _valid_generated_payload() -> dict:
    return {
        "meta": {
            "challenge_slug": "ielts",
            "challenge_name": "IELTS Sprint",
            "level_number": 1,
            "level_name": "Level 1 - Quick Sprint",
            "phase": 3,
        },
        "sections": {
            "listening": {
                "widget": "listen_and_respond",
                "task_intro": "Listen to the talk and answer the questions.",
                "instructions": "Audio arrives in Phase 5.",
                "audio_url": None,
                "audio_script": "The speaker describes a community repair cafe.",
                "audio_duration_seconds": 45,
                "inner_widget": "mcq",
                "items": [
                    {
                        "item_id": "l1",
                        "prompt": "What is the speaker mainly describing?",
                        "options": [
                            "A repair cafe",
                            "A hotel policy",
                            "A bus delay",
                            "A sports event",
                        ],
                        "correct_index": 0,
                        "explanation": "The transcript is about a repair cafe.",
                    }
                ],
            },
            "reading": {
                "widget": "mcq",
                "task_intro": "Read the passage and choose the best answers.",
                "instructions": "Select one option for each question.",
                "passage_title": "Community Repair Cafes",
                "passage": (
                    "Community repair cafes invite residents to bring broken household "
                    "items and learn how to fix them with help from volunteers."
                ),
                "items": [
                    {
                        "item_id": "r1",
                        "prompt": "What is the main idea of the passage?",
                        "options": [
                            "Repair cafes help people fix items together",
                            "Shopping malls are replacing libraries",
                            "Volunteers should avoid practical work",
                            "Household items are impossible to repair",
                        ],
                        "correct_index": 0,
                        "explanation": "The passage focuses on shared repair work.",
                    }
                ],
            },
            "writing": {
                "widget": "timed_text",
                "task_intro": "Write an IELTS-style response.",
                "instructions": "Use the global challenge timer.",
                "items": [
                    {
                        "item_id": "w1",
                        "prompt": (
                            "Some people believe communities should teach practical "
                            "repair skills. To what extent do you agree?"
                        ),
                        "target_word_count": 80,
                    }
                ],
                "target_word_count": 80,
                "time_limit_seconds": 1200,
                "minimum_word_count": 40,
                "no_editing_allowed": False,
                "sample_response": "",
            },
            "speaking": {
                "widget": "speak_and_record",
                "task_intro": "Record a short spoken answer.",
                "instructions": "Speaking upload arrives in Phase 6.",
                "speaking_duration_seconds": 30,
                "speaking_prompts": ["Describe something useful you learned recently."],
                "sample_responses": [],
            },
        },
    }


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


def _level_one(db: Session) -> ChallengeLevel:
    challenge = db.query(Challenge).filter_by(slug="ielts").one()
    return (
        db.query(ChallengeLevel)
        .filter_by(challenge_id=challenge.id, level_number=1)
        .one()
    )


def _completed_attempt_with_topic(
    db: Session,
    *,
    user_id: int,
    level_id: int,
    title: str,
) -> None:
    now = datetime.now(timezone.utc) - timedelta(days=1)
    db.add(
        ChallengeAttempt(
            user_id=user_id,
            challenge_level_id=level_id,
            status=ChallengeAttemptStatus.COMPLETED,
            started_at=now,
            completed_at=now + timedelta(minutes=5),
            expires_at=now + timedelta(minutes=20),
            task_payload={
                "sections": {"reading": {"passage_title": title}},
            },
            response_payload={"reading": {"r1": "A"}},
            overall_score=6.5,
            section_scores={"reading": 6.5},
            passed=True,
            evaluation_report={"overall": "stub"},
            feedback_report={"summary": "stub"},
        )
    )
    db.commit()


class FakeTTSService:
    async def synthesize(
        self,
        *,
        text: str,
        voice: str | None = None,
        speed: float = 1.0,
        style_instructions: str | None = None,
    ) -> dict:
        return {
            "audio_url": "/audio/ab/abcdef1234567890.mp3",
            "duration_seconds": 10.0,
            "cache_hit": True,
        }


def test_generated_ielts_payload_schema_accepts_valid_payload() -> None:
    payload = GeneratedIELTSTaskPayload.model_validate(_valid_generated_payload())

    assert payload.meta.phase == 3
    assert payload.sections.reading.items[0].options[0] == (
        "Repair cafes help people fix items together"
    )


def test_generated_reading_mcq_requires_exactly_four_options() -> None:
    payload = _valid_generated_payload()
    payload["sections"]["reading"]["items"][0]["options"] = ["A", "B", "C"]

    with pytest.raises(ValidationError):
        GeneratedIELTSTaskPayload.model_validate(payload)


def test_generated_reading_mcq_requires_valid_answer_and_explanation() -> None:
    payload = _valid_generated_payload()
    payload["sections"]["reading"]["items"][0]["correct_index"] = 4
    payload["sections"]["reading"]["items"][0]["explanation"] = ""

    with pytest.raises(ValidationError):
        GeneratedIELTSTaskPayload.model_validate(payload)


def test_generated_payload_forbids_extra_keys() -> None:
    payload = _valid_generated_payload()
    payload["sections"]["reading"]["difficulty"] = "easy"

    with pytest.raises(ValidationError):
        GeneratedIELTSTaskPayload.model_validate(payload)


@pytest.mark.asyncio
async def test_start_attempt_uses_generator_and_user_history(
    db_session: Session,
) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)
    level = _level_one(db_session)
    _completed_attempt_with_topic(
        db_session,
        user_id=user.id,
        level_id=level.id,
        title="Floating Farms",
    )

    class FakeGenerator:
        def __init__(self) -> None:
            self.contexts: list[dict] = []

        async def generate(self, *, context: dict) -> dict:
            self.contexts.append(context)
            return deepcopy(_valid_generated_payload())

    generator = FakeGenerator()
    attempt = await ChallengeReadService(
        db_session,
        generator=generator,
        tts_service=FakeTTSService(),
    ).start_attempt(
        slug="ielts",
        level_number=1,
        user_id=user.id,
    )

    assert attempt.task_payload["meta"]["phase"] == 3
    assert attempt.task_payload["sections"]["reading"]["passage_title"] == (
        "Community Repair Cafes"
    )
    assert attempt.task_payload["sections"]["writing"]["items"][0]["item_id"] == "w1"
    assert attempt.task_payload["sections"]["listening"]["audio_storage_key"] == (
        "abcdef1234567890.mp3"
    )
    assert generator.contexts[0]["level_config"]["sections"]["reading"][
        "num_questions"
    ] == 4
    assert "Floating Farms" in generator.contexts[0]["user_history_summary"]


@pytest.mark.asyncio
async def test_start_attempt_falls_back_to_starter_after_generator_failures(
    db_session: Session,
    caplog: pytest.LogCaptureFixture,
) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)

    class FailingGenerator:
        def __init__(self) -> None:
            self.calls = 0

        async def generate(self, *, context: dict) -> dict:
            self.calls += 1
            raise LLMProviderError("provider unavailable")

    generator = FailingGenerator()
    with caplog.at_level(logging.ERROR):
        attempt = await ChallengeReadService(
            db_session,
            generator=generator,
            tts_service=FakeTTSService(),
        ).start_attempt(
            slug="ielts",
            level_number=1,
            user_id=user.id,
        )

    assert generator.calls == 2
    assert attempt.task_payload["meta"]["phase"] == 2
    assert attempt.task_payload["sections"]["reading"]["passage_title"] == (
        "How Short Practice Builds Exam Confidence"
    )
    assert "challenge_generation_fallback" in caplog.text
