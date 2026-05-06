import pytest

from app.ai.agents.evaluator import EvaluationService
from app.ai.agents.task_generator import TaskGeneratorAgent
from app.ai.llm.exceptions import LLMValidationError
from app.tasks.schemas.grammar_templates import (
    GRAMMAR_READ_ERROR_SPOTTING_V1,
    ErrorSpottingTask,
)


def _valid_error_spotting_content() -> dict:
    return {
        "task_intro": "Read each sentence and choose whether it is correct.",
        "estimated_time_minutes": 6,
        "instructions": "Select correct or the grammar error type.",
        "sentences": [
            {
                "sentence_id": "s1",
                "sentence": "She goes to school every day.",
                "has_error": False,
                "error_type": None,
                "incorrect_phrase": None,
                "correction": None,
                "explanation": None,
            },
            {
                "sentence_id": "s2",
                "sentence": "He go to work by bus.",
                "has_error": True,
                "error_type": "subject_verb_agreement",
                "incorrect_phrase": "go",
                "correction": "goes",
                "explanation": "A third-person singular subject takes a verb ending in -s.",
            },
            {
                "sentence_id": "s3",
                "sentence": "I arrived to the station early.",
                "has_error": True,
                "error_type": "preposition",
                "incorrect_phrase": "to the station",
                "correction": "at the station",
                "explanation": "Use 'arrive at' for a specific place.",
            },
            {
                "sentence_id": "s4",
                "sentence": "If I will see her, I will call you.",
                "has_error": True,
                "error_type": "conditional",
                "incorrect_phrase": "will see",
                "correction": "see",
                "explanation": "Use present simple in the if-clause of a first conditional.",
            },
            {
                "sentence_id": "s5",
                "sentence": "The meeting starts at nine.",
                "has_error": False,
                "error_type": None,
                "incorrect_phrase": None,
                "correction": None,
                "explanation": None,
            },
            {
                "sentence_id": "s6",
                "sentence": "A apple is on the table.",
                "has_error": True,
                "error_type": "article",
                "incorrect_phrase": "A apple",
                "correction": "An apple",
                "explanation": "Use 'an' before a vowel sound.",
            },
        ],
        "total_with_errors": 4,
    }


def test_error_spotting_pydantic_accepts_valid_content() -> None:
    task = ErrorSpottingTask.model_validate(_valid_error_spotting_content())

    assert len(task.sentences) == 6
    assert task.total_with_errors == 4
    assert task.estimated_time_minutes == 6


def test_error_spotting_pydantic_rejects_bad_error_metadata() -> None:
    content = _valid_error_spotting_content()
    content["sentences"][1]["correction"] = None

    with pytest.raises(ValueError, match="error sentences must include"):
        ErrorSpottingTask.model_validate(content)


def test_error_spotting_pydantic_rejects_clean_sentence_metadata() -> None:
    content = _valid_error_spotting_content()
    content["sentences"][0]["explanation"] = "This should be null."

    with pytest.raises(ValueError, match="clean sentences"):
        ErrorSpottingTask.model_validate(content)


def test_error_spotting_pydantic_rejects_wrong_total_with_errors() -> None:
    content = _valid_error_spotting_content()
    content["total_with_errors"] = 3

    with pytest.raises(ValueError, match="total_with_errors"):
        ErrorSpottingTask.model_validate(content)


def test_error_spotting_evaluator_all_required_cases() -> None:
    report = EvaluationService().evaluate_error_spotting(
        task_content=_valid_error_spotting_content(),
        user_answers={
            "s1": "correct",
            "s2": "subject_verb_agreement",
            "s3": "article",
            "s4": "correct",
            "s5": "preposition",
        },
    )

    assert report["task_type"] == "error_spotting"
    assert report["total"] == 6
    assert report["correct_count"] == 2
    assert report["percentage"] == 41.67

    questions = report["questions"]
    assert questions["s1"]["score"] == 1.0
    assert questions["s1"]["correct"] is True
    assert questions["s2"]["score"] == 1.0
    assert questions["s2"]["correct"] is True
    assert questions["s3"]["score"] == 0.5
    assert questions["s3"]["error_classification"] == "wrong_error_type"
    assert questions["s4"]["score"] == 0.0
    assert questions["s4"]["error_classification"] == "false_negative"
    assert questions["s5"]["score"] == 0.0
    assert questions["s5"]["error_classification"] == "false_positive"
    assert questions["s6"]["score"] == 0.0
    assert questions["s6"]["error_classification"] == "missing_answer"
    assert questions["s6"]["correction"] == "An apple"


def test_error_spotting_generator_contract_checks_tier_counts() -> None:
    content = _valid_error_spotting_content()

    with pytest.raises(LLMValidationError, match="sentence count mismatch"):
        TaskGeneratorAgent._validate_template_contract(
            template=GRAMMAR_READ_ERROR_SPOTTING_V1,
            content=content,
            modifiers={"sentence_count": 5, "error_count": 4},
        )
