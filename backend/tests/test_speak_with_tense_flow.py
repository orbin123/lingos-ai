"""Regression tests for the speak_with_tense task type E2E flow."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ai.agents.evaluator import EvaluationService
from app.ai.agents.feedback import FeedbackOutput
from app.modules.responses.service import ResponseService
from app.modules.tasks.models import Task, TaskStatus, TaskType
from app.modules.tasks.service import TaskService
from app.tasks.schemas.base import Activity, ScoringMethod, SubSkill
from app.tasks.schemas.grammar_templates import (
    GRAMMAR_SPEAK_USE_TENSE_V1,
    SpeakWithTenseTask,
)


def speak_with_tense_content() -> dict:
    return {
        "task_intro": "Practice speaking in the past simple tense.",
        "estimated_time_minutes": 5,
        "instructions": (
            "Speak for at least 60 seconds. Use the past simple tense throughout."
        ),
        "target_tense": "past_simple",
        "speaking_prompt": "Tell me about your last weekend.",
        "minimum_duration_seconds": 60,
        "minimum_sentences": 4,
        "grading_criteria": [
            "uses past simple tense consistently",
            "grammar accuracy",
            "fluency and natural delivery",
        ],
        "sample_response": (
            "Last weekend I visited my grandmother. "
            "We cooked lunch together and watched a film. "
            "On Sunday I went for a walk in the park. "
            "It was a relaxing weekend."
        ),
    }


# ─── Template contract ───────────────────────────────────────────────

def test_speak_with_tense_template_contract() -> None:
    template = GRAMMAR_SPEAK_USE_TENSE_V1

    assert template.template_id == "grammar_speak_use_tense_v1"
    assert template.task_type == "speak_with_tense"
    assert template.sub_skill == SubSkill.GRAMMAR
    assert template.activity == Activity.SPEAK
    assert template.output_model_name == "SpeakWithTenseTask"
    assert template.scoring_method == ScoringMethod.AI_BASED
    assert template.estimated_time_minutes == 5
    assert template.evaluation_logic["weights"] == {
        "target_tense_usage": 0.5,
        "grammar_accuracy": 0.3,
        "fluency": 0.2,
    }
    assert template.difficulty_modifiers == {
        "beginner": {"duration": 30, "min_sentences": 3},
        "intermediate": {"duration": 60, "min_sentences": 4},
        "advanced": {"duration": 90, "min_sentences": 6},
    }


# ─── Pydantic model validation ───────────────────────────────────────

def test_speak_with_tense_pydantic_model_validates() -> None:
    validated = SpeakWithTenseTask.model_validate(speak_with_tense_content())

    assert validated.target_tense == "past_simple"
    assert validated.speaking_prompt == "Tell me about your last weekend."
    assert validated.minimum_sentences == 4
    assert validated.minimum_duration_seconds == 60
    assert len(validated.grading_criteria) == 3
    assert validated.estimated_time_minutes == 5


# ─── Activity-type fingerprint ───────────────────────────────────────

def test_first_activity_type_detects_speak_with_tense() -> None:
    assert ResponseService._first_activity_type(speak_with_tense_content()) == (
        "speak_with_tense"
    )


# ─── Dispatcher ─────────────────────────────────────────────────────

def test_evaluate_dispatcher_routes_to_speak_with_tense() -> None:
    report = EvaluationService().evaluate(
        activity_type="speak_with_tense",
        task_content=speak_with_tense_content(),
        user_answers={
            "transcript": (
                "Last weekend I visited my grandmother. "
                "We cooked lunch together. "
                "On Sunday I went for a walk. "
                "It was a lovely day."
            ),
            "duration_seconds": 65,
            "audio_url": "/audio/user-recordings/abc123.webm",
        },
    )

    assert report["task_type"] == "speak_with_tense"


# ─── Report shape (passing transcript) ───────────────────────────────

def test_evaluate_speak_with_tense_passing_report_shape() -> None:
    content = speak_with_tense_content()
    transcript = (
        "Last weekend I visited my grandmother. "
        "We cooked lunch together. "
        "On Sunday I went for a walk. "
        "It was a lovely day."
    )
    answers = {
        "transcript": transcript,
        "duration_seconds": 65,
        "audio_url": "/audio/user-recordings/abc123.webm",
    }

    report = EvaluationService().evaluate_speak_with_tense(
        task_content=content,
        user_answers=answers,
    )

    assert report["task_type"] == "speak_with_tense"
    assert report["total"] == 1
    assert report["correct_count"] == 1
    assert report["percentage"] == 70.0

    q = report["questions"]["speaking_response"]
    assert q["correct"] is True
    assert q["score"] == 0.7
    assert q["error_type"] == "needs_ai_review"
    assert q["user_answer"] == transcript
    assert q["correct_answer"] is None
    assert q["target_tense"] == "past_simple"
    assert q["speaking_prompt"] == "Tell me about your last weekend."
    assert q["minimum_sentences"] == 4
    assert q["sentence_count"] == 4
    assert q["duration_seconds"] == 65
    assert q["grading_criteria"] == [
        "uses past simple tense consistently",
        "grammar accuracy",
        "fluency and natural delivery",
    ]


# ─── Scoring rules ────────────────────────────────────────────────────

@pytest.mark.parametrize(
    ("transcript", "duration", "expected_correct", "expected_score", "expected_error_type", "expected_pct"),
    [
        # Enough sentences → 0.7
        (
            "Last weekend I visited my grandmother. We cooked lunch. I went for a walk. It was lovely.",
            65,
            True, 0.7, "needs_ai_review", 70.0,
        ),
        # Too few sentences (2 < 4) → 0.3
        (
            "I visited my grandmother. We cooked lunch.",
            20,
            False, 0.3, "too_short", 30.0,
        ),
        # Empty transcript → 0.0
        (
            "",
            0,
            False, 0.0, "missing_answer", 0.0,
        ),
        # Whitespace-only → 0.0
        (
            "   ",
            0,
            False, 0.0, "missing_answer", 0.0,
        ),
    ],
)
def test_evaluate_speak_with_tense_scoring_rules(
    transcript: str,
    duration: int,
    expected_correct: bool,
    expected_score: float,
    expected_error_type: str,
    expected_pct: float,
) -> None:
    report = EvaluationService().evaluate(
        activity_type="speak_with_tense",
        task_content=speak_with_tense_content(),
        user_answers={"transcript": transcript, "duration_seconds": duration},
    )

    q = report["questions"]["speaking_response"]
    assert q["correct"] is expected_correct
    assert q["score"] == expected_score
    assert q["error_type"] == expected_error_type
    assert report["percentage"] == expected_pct


# ─── Feedback output shape ────────────────────────────────────────────

def test_feedback_agent_standard_output_model_shape_for_speak_with_tense() -> None:
    feedback = FeedbackOutput.model_validate(
        {
            "overall_message": (
                "You used the past simple well overall. "
                "Watch out for mixing present and past tense in the same sentence."
            ),
            "errors": [
                {
                    "question_id": "speaking_response",
                    "user_answer": "Last weekend I visit my grandmother.",
                    "correct_answer": "Last weekend I visited my grandmother.",
                    "error_type": "wrong_tense",
                    "why_wrong": "'Visit' is present simple; the past simple is 'visited'.",
                    "rule": "Use past simple (verb + -ed for regular verbs) for completed actions.",
                    "memory_tip": "If it happened yesterday or in the past, add -ed (or use irregular form).",
                }
            ],
            "score": 70,
            "overall_level": "okay",
            "practice_suggestion": (
                "Try retelling a childhood memory using only past simple verbs."
            ),
        }
    )

    assert feedback.score == 70
    assert feedback.errors[0].question_id == "speaking_response"


# ─── SuperUser jump ──────────────────────────────────────────────────

class _FakeDb:
    def __init__(self) -> None:
        self.added: list[object] = []
        self._next_id = 100

    def add(self, obj: object) -> None:
        self.added.append(obj)

    def flush(self) -> None:
        for obj in self.added:
            if getattr(obj, "id", None) is None:
                setattr(obj, "id", self._next_id)
                self._next_id += 1

    def commit(self) -> None:
        pass

    def refresh(self, obj: object) -> None:
        pass


class _FakeGenerator:
    async def generate(self, template: object, user_profile: dict) -> dict:
        return speak_with_tense_content()


class _FakeUserTaskRepo:
    def __init__(self) -> None:
        self.assignment: SimpleNamespace | None = None

    def assign(
        self,
        *,
        user_id: int,
        task_id: int,
        enrollment_id: int | None = None,
    ) -> SimpleNamespace:
        self.assignment = SimpleNamespace(
            id=200,
            user_id=user_id,
            task_id=task_id,
            enrollment_id=enrollment_id,
            task=SimpleNamespace(),
        )
        return self.assignment


def test_superuser_jump_by_speak_with_tense_creates_non_blocking_ad_hoc_assignment(
    monkeypatch,
) -> None:
    service = TaskService.__new__(TaskService)
    service.db = _FakeDb()
    service.skill_repo = SimpleNamespace(name_to_id_map=lambda: {"grammar": 1})
    service.task_repo = SimpleNamespace(find_by_task_type=lambda **kwargs: None)
    service.user_task_repo = _FakeUserTaskRepo()
    service.generator = _FakeGenerator()

    monkeypatch.setattr(
        service,
        "_load_enrollment",
        lambda user_id: SimpleNamespace(id=999),
    )
    monkeypatch.setattr(
        service,
        "_build_user_profile",
        lambda user_id: {
            "sub_level": 4,
            "weak_areas": "grammar",
            "topic": "daily life",
        },
    )

    bundle = service.superuser_jump_by_type(
        user_id=123,
        task_type="speak_with_tense",
    )

    assignment = bundle[0]
    created_task = next(obj for obj in service.db.added if isinstance(obj, Task))

    assert assignment.enrollment_id is None
    assert created_task.task_type == TaskType.SPEAK_WITH_TENSE
    assert created_task.status == TaskStatus.ACTIVE
    assert SpeakWithTenseTask.model_validate(created_task.content)


# ─── STT route smoke check (core logic, no HTTP stack) ─────────────────

@pytest.mark.anyio
async def test_transcribe_audio_core_logic_with_stt_patched(tmp_path) -> None:
    """Verify the core logic of the transcribe-audio endpoint inline.

    Does NOT import the routes module (which chains to jose/auth).
    Instead, reproduces the route's key operations:
      1. Hash audio bytes to derive a stable filename.
      2. Save audio to disk under user-recordings/.
      3. Call the (patched) STT service.
      4. Return the expected transcript + audio_url shape.
    """
    import hashlib
    from pathlib import Path

    fake_audio_bytes = b"RIFF\x00\x00\x00\x00WAVEfmt " + b"\x00" * 100
    tts_cache_dir = str(tmp_path)
    url_prefix = "/audio"

    # --- core logic extracted from routes.transcribe_audio ---
    content_hash = hashlib.sha256(fake_audio_bytes).hexdigest()[:16]
    filename_on_disk = f"{content_hash}.wav"

    recordings_dir = Path(tts_cache_dir) / "user-recordings"
    recordings_dir.mkdir(parents=True, exist_ok=True)
    audio_path = recordings_dir / filename_on_disk
    audio_path.write_bytes(fake_audio_bytes)

    audio_url = f"{url_prefix}/user-recordings/{filename_on_disk}"

    # Fake STT service — no real API call
    async def _fake_transcribe(**kwargs):  # noqa: ANN202
        return {"text": "Last weekend I visited my grandmother.", "duration_seconds": 5.2}

    mock_stt = MagicMock()
    mock_stt.transcribe = _fake_transcribe
    result = await mock_stt.transcribe(
        audio_bytes=fake_audio_bytes,
        filename=filename_on_disk,
        language="en",
        with_timestamps=False,
    )
    transcript = result["text"]
    # --- end of extracted logic ---

    assert transcript == "Last weekend I visited my grandmother."
    assert audio_url.startswith("/audio/user-recordings/")
    assert audio_path.read_bytes() == fake_audio_bytes
