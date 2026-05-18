from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.ai.llm import LLMProviderError
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.challenges.evaluation_schemas import (
    IELTSFeedbackReport,
    SectionFeedback,
    WritingCriteriaEvaluation,
    WritingCriterionEvaluation,
    WritingEvaluationReport,
    WritingPromptEvaluation,
)
from app.modules.challenges.models import (
    Challenge,
    ChallengeAttempt,
    ChallengeAttemptStatus,
    ChallengeLevel,
)
from app.modules.challenges.service import (
    ChallengeDailyAttemptLimitExceeded,
    ChallengeReadService,
    academic_reading_band,
    grade_reading_section,
    round_to_half_band,
)
from scripts.seed_ielts_challenge import seed_ielts_challenge


def _generated_payload() -> dict:
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
                "audio_script": "A tutor discusses better public parks.",
                "audio_duration_seconds": 45,
                "inner_widget": "mcq",
                "items": [
                    {
                        "item_id": "l1",
                        "prompt": "What is the talk about?",
                        "options": ["Parks", "Banks", "Trains", "Phones"],
                        "correct_index": 0,
                        "explanation": "The talk is about public parks.",
                    }
                ],
            },
            "reading": {
                "widget": "mcq",
                "task_intro": "Read and answer.",
                "instructions": "Choose the best option.",
                "passage_title": "Better Public Parks",
                "passage": "Public parks can improve health and community trust.",
                "items": [
                    {
                        "item_id": "r1",
                        "prompt": "What is the passage mainly about?",
                        "options": ["Public parks", "Online exams", "Airports", "Museums"],
                        "correct_index": 0,
                        "explanation": "The passage focuses on public parks.",
                    },
                    {
                        "item_id": "r2",
                        "prompt": "Which benefit is mentioned?",
                        "options": ["Long flights", "Community trust", "Lower taxes", "Faster trains"],
                        "correct_index": 1,
                        "explanation": "The passage mentions community trust.",
                    },
                ],
            },
            "writing": {
                "widget": "timed_text",
                "task_intro": "Write an IELTS-style response.",
                "instructions": "Use the global timer.",
                "items": [
                    {
                        "item_id": "w1",
                        "prompt": "Some people think cities should invest in public parks. To what extent do you agree?",
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
                "speaking_prompts": ["Describe a park you know."],
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
        email="phase4@example.com",
        password_hash="x",
        name="Phase Four",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _fake_writing_report() -> WritingEvaluationReport:
    criteria = WritingCriteriaEvaluation(
        task_response=WritingCriterionEvaluation(
            band=6.0,
            rationale="The response presents a relevant position.",
        ),
        coherence_and_cohesion=WritingCriterionEvaluation(
            band=7.0,
            rationale="Ideas progress clearly with minor cohesion issues.",
        ),
        lexical_resource=WritingCriterionEvaluation(
            band=6.0,
            rationale="Vocabulary is adequate but not very flexible.",
        ),
        grammatical_range_and_accuracy=WritingCriterionEvaluation(
            band=7.0,
            rationale="Grammar is mostly controlled.",
        ),
    )
    return WritingEvaluationReport(
        mode="ai_writing_phase_4",
        items=[
            WritingPromptEvaluation(
                item_id="w1",
                prompt="Some people think cities should invest in public parks.",
                response_excerpt="Cities should invest in parks because they help health.",
                response_word_count=9,
                criteria=criteria,
                issues=[],
                band=9.0,
                summary="Useful position with room for support.",
            )
        ],
        section_band=9.0,
        summary="Useful position with room for support.",
    )


def _fake_feedback_report() -> IELTSFeedbackReport:
    section_feedback = SectionFeedback(
        went_well=["You completed the section."],
        needs_work=["Add more precise support."],
        next_tip="Review one weak answer and rewrite it.",
    )
    return IELTSFeedbackReport(
        mode="phase_4_feedback",
        overall_summary="Specific fake feedback.",
        sections={
            "listening": section_feedback,
            "reading": section_feedback,
            "writing": section_feedback,
            "speaking": section_feedback,
        },
    )


class FakeGenerator:
    async def generate(self, *, context: dict) -> dict:
        return deepcopy(_generated_payload())


class FakeWritingEvaluator:
    async def evaluate(self, *, context: dict) -> WritingEvaluationReport:
        return _fake_writing_report()


class FailingWritingEvaluator:
    def __init__(self) -> None:
        self.calls = 0

    async def evaluate(self, *, context: dict) -> WritingEvaluationReport:
        self.calls += 1
        raise LLMProviderError("writing evaluator unavailable")


class FakeFeedbackAgent:
    async def generate(self, *, context: dict) -> IELTSFeedbackReport:
        return _fake_feedback_report()


class FailingFeedbackAgent:
    async def generate(self, *, context: dict) -> IELTSFeedbackReport:
        raise LLMProviderError("feedback unavailable")


def test_rounding_and_academic_reading_band() -> None:
    assert round_to_half_band(6.125) == 6.0
    assert round_to_half_band(6.25) == 6.5
    assert round_to_half_band(6.75) == 7.0
    assert academic_reading_band(40) == 9.0
    assert academic_reading_band(30) == 7.0
    assert academic_reading_band(23) == 6.0
    assert academic_reading_band(0) == 0.0


def test_reading_answer_key_grading() -> None:
    report = grade_reading_section(
        task_payload=_generated_payload(),
        response_payload={"reading": {"r1": "A", "r2": "C"}},
    )

    assert report.total_correct == 1
    assert report.total_questions == 2
    assert report.raw_scaled_40 == 20
    assert report.section_band == 5.5
    assert report.questions[0].correct is True
    assert report.questions[1].correct is False


def test_writing_schema_rejects_non_half_band() -> None:
    report = _fake_writing_report().model_dump()
    report["items"][0]["criteria"]["task_response"]["band"] = 6.25

    with pytest.raises(ValidationError):
        WritingEvaluationReport.model_validate(report)


@pytest.mark.asyncio
async def test_submit_persists_phase4_scores_and_feedback(db_session: Session) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)
    service = ChallengeReadService(
        db_session,
        generator=FakeGenerator(),
        writing_evaluator=FakeWritingEvaluator(),
        feedback_generator=FakeFeedbackAgent(),
    )
    attempt = await service.start_attempt(slug="ielts", level_number=1, user_id=user.id)

    submitted = await service.submit_attempt(
        attempt_id=attempt.id,
        user_id=user.id,
        response_payload={
            "reading": {"r1": "A", "r2": "C"},
            "writing": {"w1": "Cities should invest in parks because they help health."},
            "listening": {},
            "speaking": {},
        },
    )

    assert submitted.status == ChallengeAttemptStatus.COMPLETED
    assert submitted.response_payload["writing"]["w1"].startswith("Cities")
    assert submitted.section_scores == {
        "listening": 6.5,
        "reading": 5.5,
        "writing": 6.5,
        "speaking": 6.5,
    }
    assert float(submitted.overall_score) == 6.5
    assert submitted.evaluation_report["reading"]["total_correct"] == 1
    assert submitted.evaluation_report["writing"]["section_band"] == 6.5
    assert submitted.feedback_report["overall_summary"] == "Specific fake feedback."


@pytest.mark.asyncio
async def test_evaluator_failure_uses_fallback_without_losing_response(
    db_session: Session,
) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)
    evaluator = FailingWritingEvaluator()
    service = ChallengeReadService(
        db_session,
        generator=FakeGenerator(),
        writing_evaluator=evaluator,
        feedback_generator=FakeFeedbackAgent(),
    )
    attempt = await service.start_attempt(slug="ielts", level_number=1, user_id=user.id)

    submitted = await service.submit_attempt(
        attempt_id=attempt.id,
        user_id=user.id,
        response_payload={
            "reading": {"r1": "A", "r2": "B"},
            "writing": {"w1": "I agree because public parks are useful."},
            "listening": {},
            "speaking": {},
        },
    )

    assert evaluator.calls == 2
    assert submitted.response_payload["writing"]["w1"] == (
        "I agree because public parks are useful."
    )
    assert submitted.section_scores["reading"] == 9.0
    assert submitted.section_scores["writing"] == 5.0
    assert submitted.evaluation_report["writing"]["summary"] == (
        "AI writing evaluation is temporarily unavailable."
    )


@pytest.mark.asyncio
async def test_feedback_failure_stores_local_fallback(db_session: Session) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)
    service = ChallengeReadService(
        db_session,
        generator=FakeGenerator(),
        writing_evaluator=FakeWritingEvaluator(),
        feedback_generator=FailingFeedbackAgent(),
    )
    attempt = await service.start_attempt(slug="ielts", level_number=1, user_id=user.id)

    submitted = await service.submit_attempt(
        attempt_id=attempt.id,
        user_id=user.id,
        response_payload={
            "reading": {"r1": "A", "r2": "B"},
            "writing": {"w1": "Parks are useful for many people."},
            "listening": {},
            "speaking": {},
        },
    )

    assert "temporarily unavailable" in submitted.feedback_report["overall_summary"]
    assert submitted.feedback_report["sections"]["writing"]["next_tip"]


@pytest.mark.asyncio
async def test_expired_submit_marks_timed_out_and_still_evaluates(
    db_session: Session,
) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)
    service = ChallengeReadService(
        db_session,
        generator=FakeGenerator(),
        writing_evaluator=FakeWritingEvaluator(),
        feedback_generator=FakeFeedbackAgent(),
    )
    attempt = await service.start_attempt(slug="ielts", level_number=1, user_id=user.id)
    attempt.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)
    db_session.commit()

    submitted = await service.submit_attempt(
        attempt_id=attempt.id,
        user_id=user.id,
        response_payload={
            "reading": {"r1": "A", "r2": "B"},
            "writing": {"w1": "Parks are useful for many people."},
            "listening": {},
            "speaking": {},
        },
    )

    assert submitted.status == ChallengeAttemptStatus.TIMED_OUT
    assert submitted.overall_score is not None
    assert submitted.feedback_report["overall_summary"] == "Specific fake feedback."


@pytest.mark.asyncio
async def test_daily_attempt_cap_rejects_eleventh_start(db_session: Session) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)
    challenge = db_session.query(Challenge).filter_by(slug="ielts").one()
    level = (
        db_session.query(ChallengeLevel)
        .filter_by(challenge_id=challenge.id, level_number=1)
        .one()
    )
    now = datetime.now(timezone.utc)
    for index in range(10):
        db_session.add(
            ChallengeAttempt(
                user_id=user.id,
                challenge_level_id=level.id,
                status=ChallengeAttemptStatus.COMPLETED,
                started_at=now - timedelta(minutes=index),
                completed_at=now,
                expires_at=now + timedelta(minutes=20),
                task_payload={"sections": {}},
                response_payload={},
                overall_score=6.0,
                section_scores={"reading": 6.0},
                passed=True,
                evaluation_report={"overall": "stub"},
                feedback_report={"summary": "stub"},
            )
        )
    db_session.commit()

    with pytest.raises(ChallengeDailyAttemptLimitExceeded):
        await ChallengeReadService(
            db_session,
            generator=FakeGenerator(),
        ).start_attempt(slug="ielts", level_number=1, user_id=user.id)
