import pytest

from app.ai.agents.evaluator import EvaluationService
from app.ai.agents.task_generator import TaskGeneratorAgent
from app.ai.graphs.nodes import task_delivery_node
from app.ai.llm.exceptions import LLMValidationError
from app.tasks.schemas.full_tasks_templates import FULL_GRAMMAR_READ_V1
from app.tasks.schemas.grammar_templates import GRAMMAR_READ_FILL_BLANKS_V1


def _linked_reading_content() -> dict:
    return {
        "widget": "fill_in_blanks",
        "topic_name": "Present Simple Tense — Basics",
        "passage": (
            "Maya ___ breakfast at seven every morning. "
            "Her brother ___ soccer after school. "
            "They ___ their homework before dinner. "
            "Their father ___ tea in the evening."
        ),
        "grammar_rule_explained": "Use -s with he, she, or it.",
        "items": [
            {
                "item_id": "g1",
                "sentence_with_blank": "Maya ___ breakfast at seven every morning.",
                "correct_answer": "eats",
                "explanation": "Maya is she, so use eats.",
            },
            {
                "item_id": "g2",
                "sentence_with_blank": "Her brother ___ soccer after school.",
                "correct_answer": "plays",
                "explanation": "Brother is he, so use plays.",
            },
            {
                "item_id": "g3",
                "sentence_with_blank": "They ___ their homework before dinner.",
                "correct_answer": "do",
                "explanation": "They takes the base verb do.",
            },
            {
                "item_id": "g4",
                "sentence_with_blank": "Their father ___ tea in the evening.",
                "correct_answer": "drinks",
                "explanation": "Father is he, so use drinks.",
            },
        ],
    }


def test_grammar_read_contract_requires_items_to_come_from_passage() -> None:
    content = _linked_reading_content()

    TaskGeneratorAgent._validate_template_contract(
        template=FULL_GRAMMAR_READ_V1,
        content=content,
        modifiers={},
    )


def test_grammar_read_contract_rejects_unlinked_items() -> None:
    content = _linked_reading_content()
    content["items"][0]["sentence_with_blank"] = "She ___ to the store every day."

    with pytest.raises(LLMValidationError):
        TaskGeneratorAgent._validate_template_contract(
            template=FULL_GRAMMAR_READ_V1,
            content=content,
            modifiers={},
        )


def test_grammar_read_contract_rejects_mcq_distractors() -> None:
    content = _linked_reading_content()
    content["items"][0]["distractors"] = ["eat", "eating", "ate"]

    with pytest.raises(LLMValidationError):
        TaskGeneratorAgent._validate_template_contract(
            template=FULL_GRAMMAR_READ_V1,
            content=content,
            modifiers={},
        )


def test_legacy_fill_blank_contract_rejects_mcq_options() -> None:
    content = {
        "passage_title": "Daily habits",
        "passage": (
            "Maya ___ breakfast at seven every morning. "
            "Her brother ___ soccer after school. "
            "They ___ their homework before dinner. "
            "Their father ___ tea in the evening. "
            "The family ___ together at night."
        ),
        "blanks": [
            {
                "blank_id": "b1",
                "sentence_with_blank": "Maya ___ breakfast at seven every morning.",
                "correct_answer": "eats",
                "options": ["eats", "eat", "eating", "ate"],
                "grammar_rule": "present_simple",
                "explanation": "Maya is she, so use eats.",
            },
            {
                "blank_id": "b2",
                "sentence_with_blank": "Her brother ___ soccer after school.",
                "correct_answer": "plays",
                "options": [],
                "grammar_rule": "present_simple",
                "explanation": "Brother is he, so use plays.",
            },
            {
                "blank_id": "b3",
                "sentence_with_blank": "They ___ their homework before dinner.",
                "correct_answer": "do",
                "options": [],
                "grammar_rule": "present_simple",
                "explanation": "They takes the base verb do.",
            },
            {
                "blank_id": "b4",
                "sentence_with_blank": "Their father ___ tea in the evening.",
                "correct_answer": "drinks",
                "options": [],
                "grammar_rule": "present_simple",
                "explanation": "Father is he, so use drinks.",
            },
            {
                "blank_id": "b5",
                "sentence_with_blank": "The family ___ together at night.",
                "correct_answer": "sits",
                "options": [],
                "grammar_rule": "present_simple",
                "explanation": "Family is a singular group noun here.",
            },
        ],
        "total_blanks": 5,
    }

    with pytest.raises(LLMValidationError):
        TaskGeneratorAgent._validate_template_contract(
            template=GRAMMAR_READ_FILL_BLANKS_V1,
            content=content,
            modifiers={"blank_count": 5},
        )


def test_curriculum_fill_in_blanks_scores_items_by_item_id() -> None:
    report = EvaluationService().evaluate(
        activity_type="curriculum_grammar_fill_blanks",
        task_content={
            "widget": "fill_in_blanks",
            "grammar_rule_explained": "Use -s with he, she, or it.",
            "items": [
                {
                    "item_id": "g1",
                    "sentence_with_blank": "She ___ every morning.",
                    "correct_answer": "walks",
                    "explanation": "She takes the third-person singular form.",
                },
                {
                    "item_id": "g2",
                    "sentence_with_blank": "They ___ after school.",
                    "correct_answer": "play",
                    "explanation": "They takes the base verb.",
                },
            ],
        },
        user_answers={"g1": "walks", "g2": "plays"},
    )

    assert report["task_type"] == "fill_in_blanks"
    assert report["total"] == 2
    assert report["correct_count"] == 1
    assert report["questions"]["g1"]["correct"] is True
    assert report["questions"]["g2"]["correct"] is False


def test_curriculum_grammar_listen_mcq_scores_inner_response_by_item_id() -> None:
    report = EvaluationService().evaluate(
        activity_type="curriculum_grammar_listen_mcq",
        task_content={
            "widget": "listen_and_respond",
            "activity": "listen",
            "sub_skill": "grammar",
            "items": [
                {
                    "item_id": "q1",
                    "prompt": "Which tense did Maya use?",
                    "options": ["past simple", "present simple", "future simple", "present perfect"],
                    "correct_index": 1,
                    "explanation": "Maya says walks and studies.",
                },
                {
                    "item_id": "q2",
                    "prompt": "Which sentence is correct?",
                    "options": ["She walk", "She walking", "She walks", "She walked"],
                    "correct_index": 2,
                    "explanation": "Third-person present simple takes -s.",
                },
            ],
        },
        user_answers={
            "listen_analytics": {
                "play_count": 1,
                "total_listen_seconds": 8,
                "transcript_revealed": False,
            },
            "inner_response": {
                "widget": "mcq",
                "answers": [
                    {"item_id": "q1", "selected_index": 1},
                    {"item_id": "q2", "selected_index": 0},
                ],
            },
        },
    )

    assert report["task_type"] == "curriculum_grammar_listen_mcq"
    assert report["total"] == 2
    assert report["correct_count"] == 1
    assert report["percentage"] == 50.0
    assert report["questions"]["q1"]["correct"] is True
    assert report["questions"]["q2"]["correct"] is False


@pytest.mark.asyncio
async def test_task_delivery_uses_widget_from_curriculum_payload() -> None:
    update = await task_delivery_node(
        {
            "task_type": "curriculum_grammar_fill_blanks",
            "task_content": {
                "widget": "fill_in_blanks",
                "topic_name": "Present Simple Tense — Basics",
                "items": [],
            },
            "messages": [],
        }
    )

    ui_event = update["outgoing_events"][1]
    assert ui_event["widget"] == "fill_in_blanks"
