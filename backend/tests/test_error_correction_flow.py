from types import SimpleNamespace

import pytest

from app.ai.agents.evaluator import EvaluationService
from app.ai.agents.feedback import FeedbackOutput
from app.modules.responses.service import ResponseService
from app.modules.tasks.models import Task, TaskStatus, TaskType
from app.modules.tasks.service import TaskService
from app.tasks.schemas.base import Activity, ScoringMethod, SubSkill
from app.tasks.schemas.grammar_templates import (
    GRAMMAR_WRITE_ERROR_CORRECTION_V1,
    ErrorCorrectionTask,
)


def error_correction_content() -> dict:
    return {
        "task_intro": "Read each sentence carefully and rewrite it correctly.",
        "estimated_time_minutes": 7,
        "instructions": "Rewrite each sentence correctly.",
        "items": [
            {
                "item_id": "item_1",
                "incorrect_sentence": "She don't likes apples.",
                "correct_sentence": "She doesn't like apples.",
                "error_type": "subject_verb_agreement",
                "explanation": "After 'doesn't', the verb stays in base form.",
            },
            {
                "item_id": "item_2",
                "incorrect_sentence": "He go to school every day.",
                "correct_sentence": "He goes to school every day.",
                "error_type": "present_simple",
                "explanation": "Third-person singular present simple requires -s.",
            },
            {
                "item_id": "item_3",
                "incorrect_sentence": "They was playing football.",
                "correct_sentence": "They were playing football.",
                "error_type": "past_continuous",
                "explanation": "'They' requires 'were' not 'was'.",
            },
        ],
    }


# ─── Template contract ───────────────────────────────────────────────

def test_error_correction_template_contract() -> None:
    template = GRAMMAR_WRITE_ERROR_CORRECTION_V1

    assert template.template_id == "grammar_write_error_correction_v1"
    assert template.task_type == "error_correction"
    assert template.sub_skill == SubSkill.GRAMMAR
    assert template.activity == Activity.WRITE
    assert template.output_model_name == "ErrorCorrectionTask"
    assert template.scoring_method == ScoringMethod.RULE_SENTENCE_MATCH
    assert template.estimated_time_minutes == 7
    assert template.evaluation_logic["method"] == "rule_first_then_ai"
    assert template.difficulty_modifiers == {
        "beginner": {"item_count": 3},
        "intermediate": {"item_count": 5},
        "advanced": {"item_count": 8},
    }


# ─── Pydantic model validation ───────────────────────────────────────

def test_error_correction_pydantic_model_validates() -> None:
    validated = ErrorCorrectionTask.model_validate(error_correction_content())

    assert validated.estimated_time_minutes == 7
    assert validated.instructions == "Rewrite each sentence correctly."
    assert len(validated.items) == 3
    assert validated.items[0].item_id == "item_1"
    assert validated.items[0].incorrect_sentence == "She don't likes apples."
    assert validated.items[0].correct_sentence == "She doesn't like apples."
    assert validated.items[0].error_type == "subject_verb_agreement"


def test_error_correction_pydantic_accepts_beginner_3_items() -> None:
    """Beginner difficulty generates 3 items — model must accept min_length=3."""
    content = error_correction_content()
    assert len(content["items"]) == 3
    ErrorCorrectionTask.model_validate(content)  # must not raise


# ─── Activity-type fingerprint ───────────────────────────────────────

def test_first_activity_type_detects_error_correction() -> None:
    assert ResponseService._first_activity_type(error_correction_content()) == (
        "error_correction"
    )


# ─── Dispatcher ─────────────────────────────────────────────────────

def test_evaluate_dispatcher_routes_to_error_correction() -> None:
    report = EvaluationService().evaluate(
        activity_type="error_correction",
        task_content=error_correction_content(),
        user_answers={
            "item_1": "She doesn't like apples.",
            "item_2": "He goes to school every day.",
            "item_3": "They were playing football.",
        },
    )

    assert report["task_type"] == "error_correction"


# ─── Evaluator report shape ──────────────────────────────────────────

def test_evaluate_error_correction_report_shape() -> None:
    content = error_correction_content()
    answers = {
        "item_1": "She doesn't like apples.",
        "item_2": "He goes to school every day.",
        "item_3": "They were playing football.",
    }

    report = EvaluationService().evaluate_error_correction(
        task_content=content,
        user_answers=answers,
    )

    assert report["task_type"] == "error_correction"
    assert report["total"] == 3
    assert report["correct_count"] == 3
    assert report["percentage"] == 100.0

    first = report["questions"]["item_1"]
    assert first == {
        "correct": True,
        "user_answer": "She doesn't like apples.",
        "correct_answer": "She doesn't like apples.",
        "error_type": "correct",
        "score": 1.0,
        "incorrect_sentence": "She don't likes apples.",
        "item_error_type": "subject_verb_agreement",
        "explanation": "After 'doesn't', the verb stays in base form.",
    }


# ─── Scoring rules ────────────────────────────────────────────────────

@pytest.mark.parametrize(
    ("answer", "expected_error_type", "expected_correct", "expected_score"),
    [
        # Exact match
        ("She doesn't like apples.", "correct", True, 1.0),
        # Different capitalisation
        ("she doesn't like apples.", "correct", True, 1.0),
        # Trailing period variant
        ("She doesn't like apples", "correct", True, 1.0),
        # Trailing exclamation mark
        ("She doesn't like apples!", "correct", True, 1.0),
        # Trailing question mark (normalised away)
        ("She doesn't like apples?", "correct", True, 1.0),
        # Empty → missing
        ("", "missing_answer", False, 0.0),
        # Wrong answer
        ("She not like apples.", "wrong_answer", False, 0.0),
    ],
)
def test_evaluate_error_correction_answer_outcomes(
    answer: str,
    expected_error_type: str,
    expected_correct: bool,
    expected_score: float,
) -> None:
    report = EvaluationService().evaluate(
        activity_type="error_correction",
        task_content=error_correction_content(),
        user_answers={
            "item_1": answer,
            "item_2": "He goes to school every day.",
            "item_3": "They were playing football.",
        },
    )

    result = report["questions"]["item_1"]
    assert result["error_type"] == expected_error_type
    assert result["correct"] is expected_correct
    assert result["score"] == expected_score


# ─── Feedback output shape ────────────────────────────────────────────

def test_feedback_agent_standard_output_model_shape_for_error_correction() -> None:
    feedback = FeedbackOutput.model_validate(
        {
            "overall_message": (
                "Good work on spotting agreement issues. Remember that after "
                "'doesn't' the verb always stays in base form."
            ),
            "errors": [
                {
                    "question_id": "item_1",
                    "user_answer": "She don't like apples.",
                    "correct_answer": "She doesn't like apples.",
                    "error_type": "subject_verb_agreement",
                    "why_wrong": "The contraction 'don't' is used for 'I/you/we/they', not 'she'.",
                    "rule": "Use 'doesn't' with third-person singular subjects.",
                    "memory_tip": "She/He/It → doesn't; I/You/We/They → don't.",
                }
            ],
            "score": 67,
            "overall_level": "okay",
            "practice_suggestion": "Rewrite five sentences using 'doesn't' and 'don't' correctly.",
        }
    )

    assert feedback.score == 67
    assert feedback.errors[0].question_id == "item_1"


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
        return error_correction_content()


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


def test_superuser_jump_by_error_correction_creates_non_blocking_ad_hoc_assignment(
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
            "topic": "daily life",
        },
    )

    bundle = service.superuser_jump_by_type(
        user_id=123,
        task_type="error_correction",
    )

    assignment = bundle[0]
    created_task = next(obj for obj in service.db.added if isinstance(obj, Task))

    assert assignment.enrollment_id is None
    assert created_task.task_type == TaskType.ERROR_CORRECTION
    assert created_task.status == TaskStatus.ACTIVE
    assert ErrorCorrectionTask.model_validate(created_task.content)
