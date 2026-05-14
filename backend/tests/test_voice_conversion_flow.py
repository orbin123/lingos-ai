from types import SimpleNamespace

import pytest

from app.ai.agents.evaluator import EvaluationService
from app.ai.agents.feedback import FeedbackOutput
from app.modules.responses.service import ResponseService
from app.modules.tasks.models import Task, TaskStatus, TaskType
from app.modules.tasks.service import TaskService
from app.tasks.schemas.base import Activity, ScoringMethod, SubSkill
from app.tasks.schemas.grammar_templates import (
    GRAMMAR_WRITE_VOICE_CONVERSION_V1,
    VoiceConversionTask,
)


def voice_conversion_content() -> dict:
    return {
        "task_intro": "Practice switching sentences between active and passive voice.",
        "estimated_time_minutes": 6,
        "instructions": "Convert each sentence between active and passive voice.",
        "items": [
            {
                "item_id": "item_1",
                "original_sentence": "John wrote the letter.",
                "direction": "active_to_passive",
                "correct_answer": "The letter was written by John.",
                "common_mistake": "Forgetting to change tense of helping verb.",
            },
            {
                "item_id": "item_2",
                "original_sentence": "The report was reviewed by Maria.",
                "direction": "passive_to_active",
                "correct_answer": "Maria reviewed the report.",
                "common_mistake": "Keeping the passive helping verb in the active sentence.",
            },
            {
                "item_id": "item_3",
                "original_sentence": "Aisha will submit the form.",
                "direction": "active_to_passive",
                "correct_answer": "The form will be submitted by Aisha.",
                "common_mistake": "Dropping be after will in the passive sentence.",
            },
        ],
    }


def test_voice_conversion_template_contract_and_pydantic_model() -> None:
    template = GRAMMAR_WRITE_VOICE_CONVERSION_V1

    assert template.template_id == "grammar_write_voice_conversion_v1"
    assert template.task_type == "voice_conversion"
    assert template.sub_skill == SubSkill.GRAMMAR
    assert template.activity == Activity.WRITE
    assert template.output_model_name == "VoiceConversionTask"
    assert template.scoring_method == ScoringMethod.RULE_SENTENCE_MATCH
    assert template.estimated_time_minutes == 6
    assert template.evaluation_logic["method"] == "exact_match"
    assert template.difficulty_modifiers == {
        "beginner": {"item_count": 3},
        "intermediate": {"item_count": 4},
        "advanced": {"item_count": 6},
    }
    assert "BOTH directions mixed in the same task" in template.llm_prompt_template

    validated = VoiceConversionTask.model_validate(voice_conversion_content())

    assert validated.estimated_time_minutes == 6
    assert validated.instructions == (
        "Convert each sentence between active and passive voice."
    )
    assert validated.items[0].direction == "active_to_passive"


def test_voice_conversion_content_has_both_directions() -> None:
    directions = {
        item["direction"] for item in voice_conversion_content()["items"]
    }

    assert directions == {"active_to_passive", "passive_to_active"}


def test_first_activity_type_detects_voice_conversion() -> None:
    assert ResponseService._first_activity_type(voice_conversion_content()) == (
        "voice_conversion"
    )


def test_evaluate_voice_conversion_report_shape_and_exact_matches() -> None:
    content = voice_conversion_content()
    answers = {
        "item_1": "The letter was written by John.",
        "item_2": "Maria reviewed the report.",
        "item_3": "The form will be submitted by Aisha.",
    }

    report = EvaluationService().evaluate_voice_conversion(
        task_content=content,
        user_answers=answers,
    )

    assert report["task_type"] == "voice_conversion"
    assert report["total"] == 3
    assert report["correct_count"] == 3
    assert report["percentage"] == 100.0

    first = report["questions"]["item_1"]
    assert first == {
        "correct": True,
        "user_answer": "The letter was written by John.",
        "correct_answer": "The letter was written by John.",
        "error_type": "correct",
        "score": 1.0,
        "direction": "active_to_passive",
        "original_sentence": "John wrote the letter.",
        "common_mistake": "Forgetting to change tense of helping verb.",
    }


@pytest.mark.parametrize(
    ("answer", "expected_type", "expected_correct", "expected_score"),
    [
        ("the letter was written by john", "correct", True, 1.0),
        ("The letter was written by John!", "correct", True, 1.0),
        ("The letter was written by John?", "correct", True, 1.0),
        ("", "missing_answer", False, 0.0),
        ("The letter wrote John.", "wrong_answer", False, 0.0),
    ],
)
def test_evaluate_voice_conversion_answer_outcomes(
    answer: str,
    expected_type: str,
    expected_correct: bool,
    expected_score: float,
) -> None:
    report = EvaluationService().evaluate(
        activity_type="voice_conversion",
        task_content=voice_conversion_content(),
        user_answers={
            "item_1": answer,
            "item_2": "Maria reviewed the report.",
            "item_3": "The form will be submitted by Aisha.",
        },
    )

    result = report["questions"]["item_1"]
    assert result["error_type"] == expected_type
    assert result["correct"] is expected_correct
    assert result["score"] == expected_score


def test_feedback_agent_standard_output_model_shape_for_voice_conversion() -> None:
    feedback = FeedbackOutput.model_validate(
        {
            "overall_message": (
                "You handled the voice changes accurately. Keep watching the "
                "helping verb because it carries the tense in passive voice."
            ),
            "errors": [
                {
                    "question_id": "item_1",
                    "user_answer": "The letter wrote by John.",
                    "correct_answer": "The letter was written by John.",
                    "error_type": "missing helping verb",
                    "why_wrong": "Passive voice needs be plus the past participle.",
                    "rule": "Use the correct form of be before the past participle.",
                    "memory_tip": "In passive voice, ask: be plus verb three?",
                }
            ],
            "score": 67,
            "overall_level": "okay",
            "practice_suggestion": (
                "Convert three past-simple active sentences into passive voice."
            ),
        }
    )

    assert feedback.score == 67
    assert feedback.errors[0].question_id == "item_1"


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
        return voice_conversion_content()


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


def test_superuser_jump_by_voice_conversion_creates_non_blocking_ad_hoc_assignment(
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
            "sub_level": 3,
            "weak_areas": "grammar",
            "topic": "workplace",
        },
    )

    bundle = service.superuser_jump_by_type(
        user_id=123,
        task_type="voice_conversion",
    )

    assignment = bundle[0]
    created_task = next(obj for obj in service.db.added if isinstance(obj, Task))

    assert assignment.enrollment_id is None
    assert created_task.task_type == TaskType.VOICE_CONVERSION
    assert created_task.status == TaskStatus.ACTIVE
    assert VoiceConversionTask.model_validate(created_task.content)
