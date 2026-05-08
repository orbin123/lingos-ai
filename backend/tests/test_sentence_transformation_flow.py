from types import SimpleNamespace

import pytest

from app.ai.agents.evaluator import EvaluationService
from app.ai.agents.feedback import FeedbackOutput
from app.modules.responses.service import ResponseService
from app.modules.tasks.models import Task, TaskStatus, TaskType
from app.modules.tasks.service import TaskService
from app.tasks.schemas.base import Activity, ScoringMethod, SubSkill
from app.tasks.schemas.grammar_templates import (
    GRAMMAR_WRITE_SENTENCE_TRANSFORMATION_V1,
    SentenceTransformationTask,
)


def sentence_transformation_content() -> dict:
    return {
        "task_intro": "Practice making simple ideas richer with grammar patterns.",
        "estimated_time_minutes": 8,
        "instructions": "Rewrite each sentence using the requested grammar pattern.",
        "items": [
            {
                "item_id": "item_1",
                "original_sentence": "He was tired.",
                "transformation_target": "make_complex",
                "expected_pattern": "Although/Because + clause",
                "sample_correct_answer": "Although he was tired, he finished the work.",
                "grading_criteria": [
                    "uses subordinator",
                    "preserves meaning",
                    "grammatical",
                ],
            },
            {
                "item_id": "item_2",
                "original_sentence": "Sara missed the bus.",
                "transformation_target": "use_conditional",
                "expected_pattern": "If + past perfect, would have + participle",
                "sample_correct_answer": (
                    "If Sara had left earlier, she would not have missed the bus."
                ),
                "grading_criteria": [
                    "uses conditional",
                    "preserves meaning",
                    "grammatical",
                ],
            },
            {
                "item_id": "item_3",
                "original_sentence": "The teacher praised the student.",
                "transformation_target": "add_relative_clause",
                "expected_pattern": "relative pronoun + clause",
                "sample_correct_answer": (
                    "The teacher praised the student who had improved the most."
                ),
                "grading_criteria": [
                    "uses relative clause",
                    "preserves meaning",
                    "grammatical",
                ],
            },
        ],
    }


def test_sentence_transformation_template_contract_and_pydantic_model() -> None:
    template = GRAMMAR_WRITE_SENTENCE_TRANSFORMATION_V1

    assert template.template_id == "grammar_write_sentence_transformation_v1"
    assert template.task_type == "sentence_transformation"
    assert template.sub_skill == SubSkill.GRAMMAR
    assert template.activity == Activity.WRITE
    assert template.output_model_name == "SentenceTransformationTask"
    assert template.scoring_method == ScoringMethod.AI_BASED
    assert template.estimated_time_minutes == 8

    validated = SentenceTransformationTask.model_validate(
        sentence_transformation_content()
    )

    assert validated.estimated_time_minutes == 8
    assert validated.instructions == (
        "Rewrite each sentence using the requested grammar pattern."
    )
    assert validated.items[0].transformation_target == "make_complex"


def test_sentence_transformation_dispatch_and_stub_report_shape() -> None:
    content = sentence_transformation_content()
    answers = {
        "item_1": "Although he was tired, he finished the work.",
        "item_2": "If Sara had left earlier, she would not have missed the bus.",
        "item_3": "The teacher praised the student who had improved the most.",
    }

    assert ResponseService._first_activity_type(content) == "sentence_transformation"

    report = EvaluationService().evaluate(
        activity_type="sentence_transformation",
        task_content=content,
        user_answers=answers,
    )

    assert report["task_type"] == "sentence_transformation"
    assert report["total"] == 3
    assert report["correct_count"] == 3
    assert report["percentage"] == 70.0
    assert set(report["questions"]) == {"item_1", "item_2", "item_3"}

    first = report["questions"]["item_1"]
    assert first["correct"] is True
    assert first["score"] == 0.7
    assert first["error_type"] == "needs_review"
    assert first["original_sentence"] == "He was tired."
    assert first["transformation_target"] == "make_complex"
    assert first["expected_pattern"] == "Although/Because + clause"
    assert first["grading_criteria"] == [
        "uses subordinator",
        "preserves meaning",
        "grammatical",
    ]


def test_feedback_agent_standard_output_model_shape() -> None:
    feedback = FeedbackOutput.model_validate(
        {
            "overall_message": (
                "Your transformed sentences use the requested structures. "
                "Keep checking that each new clause preserves the original meaning."
            ),
            "errors": [],
            "score": 70,
            "overall_level": "good",
            "practice_suggestion": (
                "Rewrite three simple workplace sentences using although clauses."
            ),
        }
    )

    assert feedback.model_dump() == {
        "overall_message": (
            "Your transformed sentences use the requested structures. "
            "Keep checking that each new clause preserves the original meaning."
        ),
        "errors": [],
        "score": 70,
        "overall_level": "good",
        "practice_suggestion": (
            "Rewrite three simple workplace sentences using although clauses."
        ),
    }


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
        return sentence_transformation_content()


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


def test_superuser_jump_by_type_creates_ad_hoc_assignment(monkeypatch) -> None:
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
            "sub_level": 5,
            "weak_areas": "grammar",
            "topic": "workplace",
        },
    )

    bundle = service.superuser_jump_by_type(
        user_id=123,
        task_type="sentence_transformation",
    )

    assignment = bundle[0]
    created_task = next(obj for obj in service.db.added if isinstance(obj, Task))

    assert assignment.enrollment_id is None
    assert created_task.task_type == TaskType.SENTENCE_TRANSFORMATION
    assert created_task.status == TaskStatus.ACTIVE
    assert SentenceTransformationTask.model_validate(created_task.content)
