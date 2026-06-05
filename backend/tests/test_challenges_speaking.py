from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.ai.llm import LLMProviderError
from app.ai.stt import STTProviderError
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.challenges.ielts_sprint.evaluation_schemas import (
    IELTSFeedbackReport,
    SectionFeedback,
    SpeakingCriteriaEvaluation,
    SpeakingCriterionEvaluation,
    SpeakingEvaluationReport,
    SpeakingPromptEvaluation,
    SpeakingPronunciationEvaluation,
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
from app.modules.challenges.ielts_sprint.service import (
    ChallengeAttemptNotFound,
    ChallengeReadService,
    ChallengeSpeakingUploadRejected,
)
from scripts.seed_ielts_challenge import seed_ielts_challenge


def _task_payload() -> dict:
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
                "task_intro": "Listen and answer.",
                "instructions": "Listen once.",
                "audio_url": None,
                "audio_script": "A speaker explains a study routine.",
                "audio_duration_seconds": 30,
                "inner_widget": "mcq",
                "items": [
                    {
                        "item_id": "l1",
                        "prompt": "What is discussed?",
                        "options": ["Study", "Travel", "Food", "Sport"],
                        "correct_index": 0,
                        "explanation": "The speaker discusses study.",
                    }
                ],
            },
            "reading": {
                "widget": "mcq",
                "task_intro": "Read and answer.",
                "instructions": "Choose.",
                "passage_title": "Study Routines",
                "passage": "Short daily routines can make practice easier.",
                "items": [
                    {
                        "item_id": "r1",
                        "prompt": "What can help learners?",
                        "options": ["Daily routines", "Long delays", "Noise", "Guessing"],
                        "correct_index": 0,
                        "explanation": "The passage supports routines.",
                    }
                ],
            },
            "writing": {
                "widget": "timed_text",
                "task_intro": "Write.",
                "instructions": "Use the timer.",
                "items": [
                    {
                        "item_id": "w1",
                        "prompt": "Some people prefer short daily practice. Do you agree?",
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
                "task_intro": "Record.",
                "instructions": "Answer aloud.",
                "speaking_duration_seconds": 30,
                "speaking_prompts": [
                    "Describe a useful study habit.",
                    "Describe feedback that helped you.",
                ],
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


def _make_user(db: Session, *, email: str = "speaker@example.com") -> User:
    user = User(email=email, password_hash="x", name="Speaker")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_completed_attempt(db: Session, *, user_id: int) -> ChallengeAttempt:
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
        completed_at=now + timedelta(minutes=3),
        expires_at=now + timedelta(minutes=20),
        task_payload=_task_payload(),
        response_payload={},
        overall_score=6.0,
        section_scores={"speaking": 6.0},
        passed=True,
        evaluation_report={},
        feedback_report={},
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


class FakeGenerator:
    async def generate(self, *, context: dict) -> dict:
        return deepcopy(_task_payload())


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
            "duration_seconds": 9.0,
            "cache_hit": False,
        }


class FakeBlobStorage:
    def __init__(self) -> None:
        self.store: dict[str, bytes] = {}

    async def put(self, *, key: str, data: bytes, content_type: str) -> dict:
        self.store[key] = data
        return {
            "public_url": f"/internal/{key}",
            "storage_key": key,
            "content_type": content_type,
            "size_bytes": len(data),
        }

    async def get(self, *, key: str) -> bytes | None:
        if key == "abcdef1234567890.mp3":
            return b"fake listening audio"
        return self.store.get(key)

    async def exists(self, *, key: str) -> bool:
        return key in self.store

    def url_for(self, *, key: str) -> str:
        return f"/internal/{key}"


class FakeSTTService:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[dict] = []

    async def transcribe(
        self,
        *,
        audio_bytes: bytes,
        filename: str,
        language: str = "en",
        with_timestamps: bool = False,
    ) -> dict:
        self.calls.append(
            {
                "audio_bytes": audio_bytes,
                "filename": filename,
                "language": language,
                "with_timestamps": with_timestamps,
            }
        )
        if self.fail:
            raise STTProviderError("provider unavailable")
        return {
            "text": "I improve by practising a little every day and reviewing feedback.",
            "language": language,
            "duration_seconds": 4.2,
            "words": None,
        }


def _writing_report() -> WritingEvaluationReport:
    criterion = WritingCriterionEvaluation(
        band=6.0,
        rationale="The writing is understandable.",
    )
    return WritingEvaluationReport(
        mode="ai_writing_phase_4",
        items=[
            WritingPromptEvaluation(
                item_id="w1",
                prompt="Some people prefer short daily practice.",
                response_excerpt="Short daily practice helps.",
                response_word_count=4,
                criteria=WritingCriteriaEvaluation(
                    task_response=criterion,
                    coherence_and_cohesion=criterion,
                    lexical_resource=criterion,
                    grammatical_range_and_accuracy=criterion,
                ),
                issues=[],
                band=6.0,
                summary="Understandable writing.",
            )
        ],
        section_band=6.0,
        summary="Understandable writing.",
    )


class FakeWritingEvaluator:
    async def evaluate(self, *, context: dict) -> WritingEvaluationReport:
        return _writing_report()


class FakeSpeakingEvaluator:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.contexts: list[dict] = []

    async def evaluate(self, *, context: dict) -> SpeakingEvaluationReport:
        self.contexts.append(context)
        if self.fail:
            raise LLMProviderError("speaking evaluator unavailable")
        criteria = SpeakingCriteriaEvaluation(
            fluency_and_coherence=SpeakingCriterionEvaluation(
                band=7.0,
                rationale="The transcript develops a clear answer.",
            ),
            lexical_resource=SpeakingCriterionEvaluation(
                band=7.0,
                rationale="Vocabulary is relevant to habits and feedback.",
            ),
            grammatical_range_and_accuracy=SpeakingCriterionEvaluation(
                band=8.0,
                rationale="Grammar is controlled in the transcript.",
            ),
            pronunciation=SpeakingPronunciationEvaluation(
                available=False,
                band=None,
                rationale=(
                    "Pronunciation requires audio-level scoring and is not evaluated "
                    "in Phase 6."
                ),
            ),
        )
        return SpeakingEvaluationReport(
            mode="ai_speaking_phase_6",
            items=[
                SpeakingPromptEvaluation(
                    item_id="s1",
                    prompt="Describe a useful study habit.",
                    transcript_excerpt=(
                        "I improve by practising a little every day and reviewing feedback."
                    ),
                    transcript_word_count=10,
                    criteria=criteria,
                    band=9.0,
                    summary="Clear transcript-only response.",
                )
            ],
            section_band=9.0,
            pronunciation_available=False,
            summary="Clear transcript-only response.",
        )


class FakeFeedbackAgent:
    async def generate(self, *, context: dict) -> IELTSFeedbackReport:
        section_feedback = SectionFeedback(
            went_well=["Your response was recorded."],
            needs_work=["Pronunciation is not scored yet."],
            next_tip="Record once, replay, then improve one sentence.",
        )
        return IELTSFeedbackReport(
            mode="phase_4_feedback",
            overall_summary="Fake speaking feedback.",
            sections={
                "listening": section_feedback,
                "reading": section_feedback,
                "writing": section_feedback,
                "speaking": section_feedback,
            },
        )


async def _started_attempt_service(
    db_session: Session,
    *,
    user_id: int,
    speaking_audio_storage: FakeBlobStorage | None = None,
    stt_service: FakeSTTService | None = None,
    speaking_evaluator: FakeSpeakingEvaluator | None = None,
) -> tuple[ChallengeReadService, ChallengeAttempt]:
    service = ChallengeReadService(
        db_session,
        generator=FakeGenerator(),
        writing_evaluator=FakeWritingEvaluator(),
        speaking_evaluator=speaking_evaluator or FakeSpeakingEvaluator(),
        feedback_generator=FakeFeedbackAgent(),
        tts_service=FakeTTSService(),
        blob_storage=FakeBlobStorage(),
        speaking_audio_storage=speaking_audio_storage or FakeBlobStorage(),
        stt_service=stt_service or FakeSTTService(),
    )
    attempt = await service.start_attempt(slug="ielts", level_number=1, user_id=user_id)
    return service, attempt


@pytest.mark.asyncio
async def test_speaking_upload_validation(db_session: Session) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)
    other = _make_user(db_session, email="other-speaker@example.com")
    service, attempt = await _started_attempt_service(db_session, user_id=user.id)

    with pytest.raises(ChallengeAttemptNotFound):
        await service.upload_speaking_response(
            attempt_id=attempt.id,
            user_id=other.id,
            prompt_id="s1",
            audio_bytes=b"audio",
            content_type="audio/webm",
        )

    completed = _make_completed_attempt(db_session, user_id=user.id)
    with pytest.raises(ChallengeSpeakingUploadRejected) as non_progress:
        await service.upload_speaking_response(
            attempt_id=completed.id,
            user_id=user.id,
            prompt_id="s1",
            audio_bytes=b"audio",
            content_type="audio/webm",
        )
    assert non_progress.value.status_code == 409

    cases = [
        ("s9", b"audio", "audio/webm", 404),
        ("s1", b"", "audio/webm", 400),
        ("s1", b"x" * (5 * 1024 * 1024 + 1), "audio/webm", 413),
        ("s1", b"audio", "text/plain", 415),
    ]
    for prompt_id, audio_bytes, content_type, status_code in cases:
        with pytest.raises(ChallengeSpeakingUploadRejected) as rejected:
            await service.upload_speaking_response(
                attempt_id=attempt.id,
                user_id=user.id,
                prompt_id=prompt_id,
                audio_bytes=audio_bytes,
                content_type=content_type,
            )
        assert rejected.value.status_code == status_code


@pytest.mark.asyncio
async def test_speaking_upload_stores_protected_metadata(
    db_session: Session,
) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)
    speaking_storage = FakeBlobStorage()
    service, attempt = await _started_attempt_service(
        db_session,
        user_id=user.id,
        speaking_audio_storage=speaking_storage,
    )

    result = await service.upload_speaking_response(
        attempt_id=attempt.id,
        user_id=user.id,
        prompt_id="s1",
        audio_bytes=b"webm bytes",
        content_type="audio/webm;codecs=opus",
    )

    assert result["prompt_id"] == "s1"
    assert result["audio_url"] == (
        f"/api/v1/challenge-attempts/{attempt.id}/speaking/s1/audio/"
        f"{result['audio_storage_key']}"
    )
    assert result["content_type"] == "audio/webm"
    assert speaking_storage.store[result["audio_storage_key"]] == b"webm bytes"

    audio_bytes, content_type = await service.get_speaking_audio(
        attempt_id=attempt.id,
        user_id=user.id,
        prompt_id="s1",
        audio_key=result["audio_storage_key"],
    )
    assert audio_bytes == b"webm bytes"
    assert content_type == "audio/webm"


@pytest.mark.asyncio
async def test_submit_transcribes_and_scores_speaking(
    db_session: Session,
) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)
    speaking_storage = FakeBlobStorage()
    stt = FakeSTTService()
    speaking_evaluator = FakeSpeakingEvaluator()
    service, attempt = await _started_attempt_service(
        db_session,
        user_id=user.id,
        speaking_audio_storage=speaking_storage,
        stt_service=stt,
        speaking_evaluator=speaking_evaluator,
    )
    upload = await service.upload_speaking_response(
        attempt_id=attempt.id,
        user_id=user.id,
        prompt_id="s1",
        audio_bytes=b"speaking bytes",
        content_type="audio/webm",
    )

    submitted = await service.submit_attempt(
        attempt_id=attempt.id,
        user_id=user.id,
        response_payload={
            "listening": {"l1": "A"},
            "reading": {"r1": "A"},
            "writing": {"w1": "Short daily practice helps."},
            "speaking": {"s1": upload},
        },
    )

    speaking_response = submitted.response_payload["speaking"]["s1"]
    assert stt.calls[0]["audio_bytes"] == b"speaking bytes"
    assert speaking_response["transcript"].startswith("I improve by practising")
    assert speaking_response["transcript_language"] == "en"
    assert submitted.evaluation_report["mode"] == "phase_6_speaking"
    assert submitted.evaluation_report["speaking"]["section_band"] == 7.5
    assert submitted.evaluation_report["speaking"]["pronunciation_available"] is False
    assert submitted.section_scores["speaking"] == 7.5
    assert speaking_evaluator.contexts[0]["speaking_responses"]["s1"][
        "transcript"
    ].startswith("I improve")


@pytest.mark.asyncio
async def test_stt_failure_preserves_metadata_and_scores_zero(
    db_session: Session,
) -> None:
    seed_ielts_challenge(db_session)
    user = _make_user(db_session)
    speaking_storage = FakeBlobStorage()
    service, attempt = await _started_attempt_service(
        db_session,
        user_id=user.id,
        speaking_audio_storage=speaking_storage,
        stt_service=FakeSTTService(fail=True),
    )
    upload = await service.upload_speaking_response(
        attempt_id=attempt.id,
        user_id=user.id,
        prompt_id="s1",
        audio_bytes=b"speaking bytes",
        content_type="audio/webm",
    )

    submitted = await service.submit_attempt(
        attempt_id=attempt.id,
        user_id=user.id,
        response_payload={
            "listening": {"l1": "A"},
            "reading": {"r1": "A"},
            "writing": {"w1": "Short daily practice helps."},
            "speaking": {"s1": upload},
        },
    )

    speaking_response = submitted.response_payload["speaking"]["s1"]
    assert speaking_response["audio_storage_key"] == upload["audio_storage_key"]
    assert speaking_response["transcript"] == ""
    assert "Transcription failed" in speaking_response["transcript_error"]
    assert submitted.status == ChallengeAttemptStatus.COMPLETED
    assert submitted.section_scores["speaking"] == 0.0
    assert submitted.evaluation_report["speaking"]["pronunciation_available"] is False
    assert submitted.evaluation_report["speaking"]["items"][0]["criteria"][
        "pronunciation"
    ]["available"] is False
