"""Shared canned-output builders for the split LLM session-agent tests.

Extracted from the former monolithic ``test_llm_session_agents.py``. The
``test_llm_*.py`` files import the helpers they need from here:
``_error_spotting_content`` (evaluator/feedback/schema/taskgen-text),
``_dictation_canned`` (taskgen-media), ``_canned_llm_output_for``
(archetype roundtrip → contract projection).
"""

from __future__ import annotations

from pydantic import BaseModel

from app.ai.sessions.llm_task_generator import (
    ErrorCorrectionTask,
    ErrorSpottingTask,
    ListenClozeTaskLLM,
    ListenDictationTaskLLM,
    ListenMcqTaskLLM,
    ListenRetellTaskLLM,
    TaskGenOutput,
)
from app.scoring import get_archetype
from app.tasks.schemas import FillInBlanksTask
from tests.fixtures.task_content import _valid_content_for


def _error_spotting_content() -> dict:
    return {
        "topic": "Spot past tense errors",
        "instructions": "Tap each word in the passage that contains a grammatical error.",
        "task_intro": "Tap each word that has a grammatical error.",
        "passage_sentences": [
            {
                "sentence_id": "s1",
                "tokens": [
                    {"token_id": "s1_t1", "text": "Yesterday", "is_error": False},
                    {"token_id": "s1_t2", "text": "I", "is_error": False},
                    {"token_id": "s1_t3", "text": "goed", "is_error": True},
                ],
                "error": {
                    "token_id": "s1_t3",
                    "incorrect_phrase": "goed",
                    "correction": "went",
                    "error_type": "irregular_past",
                    "rule": "Use went as the past form of go.",
                    "explanation": "Go is irregular in the past.",
                },
            },
            {
                "sentence_id": "s2",
                "tokens": [
                    {"token_id": "s2_t1", "text": "She", "is_error": False},
                    {"token_id": "s2_t2", "text": "did", "is_error": False},
                    {"token_id": "s2_t3", "text": "finished", "is_error": True},
                ],
                "error": {
                    "token_id": "s2_t3",
                    "incorrect_phrase": "finished",
                    "correction": "finish",
                    "error_type": "missing_past_auxiliary",
                    "rule": "After did, use the base verb.",
                    "explanation": "Did already carries the past tense.",
                },
            },
            {
                "sentence_id": "s3",
                "tokens": [
                    {"token_id": "s3_t1", "text": "The", "is_error": False},
                    {"token_id": "s3_t2", "text": "manager", "is_error": False},
                    {"token_id": "s3_t3", "text": "was", "is_error": False},
                    {"token_id": "s3_t4", "text": "hire", "is_error": True},
                ],
                "error": {
                    "token_id": "s3_t4",
                    "incorrect_phrase": "hire",
                    "correction": "hired",
                    "error_type": "passive_helper_missing",
                    "rule": "Use was/were + past participle in passive voice.",
                    "explanation": "The passive form needs the past participle.",
                },
            },
            {
                "sentence_id": "s4",
                "tokens": [
                    {"token_id": "s4_t1", "text": "Last", "is_error": False},
                    {"token_id": "s4_t2", "text": "week", "is_error": False},
                    {"token_id": "s4_t3", "text": "we", "is_error": False},
                    {"token_id": "s4_t4", "text": "visit", "is_error": True},
                ],
                "error": {
                    "token_id": "s4_t4",
                    "incorrect_phrase": "visit",
                    "correction": "visited",
                    "error_type": "time_marker_mismatch",
                    "rule": "Use a past verb with a past time marker.",
                    "explanation": "Last week points to finished time.",
                },
            },
            {
                "sentence_id": "s5",
                "tokens": [
                    {"token_id": "s5_t1", "text": "They", "is_error": False},
                    {"token_id": "s5_t2", "text": "had", "is_error": False},
                    {"token_id": "s5_t3", "text": "good", "is_error": False},
                    {"token_id": "s5_t4", "text": "advices", "is_error": True},
                    {"token_id": "s5_t5", "text": "yesterday.", "is_error": False},
                ],
                "error": {
                    "token_id": "s5_t4",
                    "incorrect_phrase": "advices",
                    "correction": "advice",
                    "error_type": "object_or_complement_mismatch",
                    "rule": "Advice is uncountable.",
                    "explanation": "Use advice, not advices.",
                },
            },
        ],
        "total_errors": 5,
    }


def _dictation_canned() -> TaskGenOutput:
    return TaskGenOutput(
        topic="Dictation practice",
        instructions="Type each sentence exactly as you hear it.",
        audio_script=(
            "Maria wakes up at seven. "
            "She always drinks coffee first. "
            "Then she reads the news."
        ),
        items=[
            {
                "item_id": "d1",
                "prompt": "Type sentence 1.",
                "correct_answer": "Maria wakes up at seven.",
                "explanation": "Listen for the full sentence.",
            },
            {
                "item_id": "d2",
                "prompt": "Type sentence 2.",
                "correct_answer": "She always drinks coffee first.",
                "explanation": "Listen for the full sentence.",
            },
            {
                "item_id": "d3",
                "prompt": "Type sentence 3.",
                "correct_answer": "Then she reads the news.",
                "explanation": "Listen for the full sentence.",
            },
        ],
    )


def _sentence_transform_canned() -> TaskGenOutput:
    return TaskGenOutput(
        topic="Rewrite into present continuous",
        instructions="Rewrite each sentence in the present continuous.",
        items=[
            {
                "item_id": "tr1",
                "source_sentence": "She plays tennis every Saturday.",
                "sample_answer": "She is playing tennis right now.",
                "watch_hints": ["she -> is", "play -> playing"],
            },
            {
                "item_id": "tr2",
                "source_sentence": "They study English on Mondays.",
                "sample_answer": "They are studying English right now.",
                "watch_hints": ["they -> are", "study -> studying"],
            },
            {
                "item_id": "tr3",
                "source_sentence": "I read the news every morning.",
                "sample_answer": "I am reading the news right now.",
                "watch_hints": ["I -> am", "read -> reading"],
            },
        ],
    )


def _canned_llm_output_for(archetype_id: str) -> BaseModel:
    """Map contract-valid fixture content to the LLM output model the generator expects."""
    if archetype_id == "WRITE_SENT_TRANS":
        return _sentence_transform_canned()

    content = _valid_content_for(archetype_id)
    spec = get_archetype(archetype_id)

    if archetype_id == "READ_ERROR_SPOT":
        return ErrorSpottingTask.model_validate(_error_spotting_content())

    if spec.ui_widget == "FillInBlanks" and spec.core_activity == "read":
        return FillInBlanksTask(
            topic=content["topic"],
            instructions=content["instructions"],
            items=content["items"],
            passage=content.get("passage"),
        )

    if spec.ui_widget == "ErrorCorrection":
        return ErrorCorrectionTask(
            topic=content["topic"],
            instructions=content["instructions"],
            task_intro=content.get("task_intro", "Complete the task."),
            items=content["items"],
        )

    if archetype_id == "WRITE_PARAPHRASE":
        paraphrase_items = [
            {
                "item_id": raw["item_id"],
                "prompt": raw["incorrect_sentence"],
                "sample_answer": raw["sample_answer"],
                "answer_hints": raw.get("watch_hints", []),
            }
            for raw in content.get("items", [])
        ]
        return TaskGenOutput(
            topic=content["topic"],
            instructions=content["instructions"],
            items=paraphrase_items,
        )

    if archetype_id == "READ_STRUCTURE_ID":
        structure_items = []
        labels = content.get("structure_labels", [])
        for raw in content.get("items", []):
            structure_items.append(
                {
                    "item_id": raw["item_id"],
                    "prompt": raw["paragraph"],
                    "options": labels,
                    "correct_answer": raw["correct_answer"],
                    "explanation": raw.get("explanation", ""),
                }
            )
        return TaskGenOutput(
            topic=content["topic"],
            instructions=content["instructions"],
            items=structure_items,
        )

    if archetype_id == "LISTEN_DICTATION":
        return ListenDictationTaskLLM(
            topic=content["topic"],
            instructions=content["instructions"],
            audio_script=content["audio_script"],
            items=content["items"],
        )

    if archetype_id in {"LISTEN_MCQ", "LISTEN_INFER", "LISTEN_TONE"}:
        return ListenMcqTaskLLM(
            topic=content["topic"],
            instructions=content["instructions"],
            audio_script=content["audio_script"],
            items=content["items"],
        )

    if archetype_id == "LISTEN_CLOZE":
        items = list(content["items"])
        while len(items) < 4:
            clone = dict(items[0])
            clone["item_id"] = f"b{len(items) + 1}"
            items.append(clone)
        return ListenClozeTaskLLM(
            topic=content["topic"],
            instructions=content["instructions"],
            audio_script=content["audio_script"],
            passage=content["passage"],
            items=items[:4],
        )

    if archetype_id in {"LISTEN_RETELL", "LISTEN_SHADOW"}:
        return ListenRetellTaskLLM(
            topic=content["topic"],
            instructions=content["instructions"],
            audio_script=content["audio_script"],
            speaking_prompts=content["speaking_prompts"],
            sample_responses=content.get("sample_responses", []),
            text_to_shadow=content.get("text_to_shadow"),
            speaking_duration_seconds=content.get("speaking_duration_seconds", 45),
        )

    task_gen_fields = {
        "topic": content["topic"],
        "instructions": content["instructions"],
        "task_intro": content.get("task_intro"),
        "items": content.get("items", []),
        "passage": content.get("passage"),
        "primary_text": content.get("primary_text") or content.get("passage") or "",
        "audio_script": content.get("audio_script"),
        "inner_widget": content.get("inner_widget"),
        "speaking_duration_seconds": content.get("speaking_duration_seconds"),
        "speaking_prompts": content.get("speaking_prompts", []),
        "sample_responses": content.get("sample_responses", []),
        "text_to_read_aloud": content.get("text_to_read_aloud"),
        "text_to_shadow": content.get("text_to_shadow"),
        "image_alt": content.get("image_alt"),
        "dialogue_context": content.get("dialogue_context", []),
        "questions": content.get("questions", []),
    }
    return TaskGenOutput(**{k: v for k, v in task_gen_fields.items() if v is not None})
