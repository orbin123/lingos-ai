"""Schema-boundary projection guarantees (M2 + M3).

The projection layer is the validate-then-normalize boundary between the agents
and the orchestrator. These tests prove that loose runtime payloads are
projected onto the strict contracts — across every task family — and that
malformed output is rejected rather than silently forwarded to a widget.
"""

from __future__ import annotations

import pytest

from app.modules.sessions.contracts import (
    DictationPayload,
    ErrorCorrectionPayload,
    ErrorSpottingPayload,
    FillBlanksPayload,
    McqPayload,
    OpenTextPayload,
    ReadStructurePayload,
    SpeakingPayload,
    TfngPayload,
    TransformPayload,
    project_evaluation,
    project_feedback,
    project_task_payload,
)
from app.modules.sessions.contracts.projection import ContractValidationError
from app.modules.sessions.evaluator import EvaluationResult
from app.modules.sessions.feedback_generator import FeedbackResult, MistakeOut
from app.scoring.constants import Tier


def _cloze_content() -> dict:
    return {
        "archetype_id": "READ_CLOZE",
        "widget": "fill_in_blanks",
        "core_activity": "read",
        "topic": "Simple present routines",
        "instructions": "Fill each blank with the correct verb.",
        "passage_title": "Maria's morning",
        "passage": "Maria ___ up at seven. She ___ coffee first.",
        "items": [
            {
                "item_id": "b1",
                "sentence_with_blank": "Maria ___ up at seven.",
                "base_verb": "wake",
                "correct_answer": "wakes",
                "explanation": "Third person singular adds -s.",
                "blank_index": 0,  # legacy extra — must be dropped, not rejected
            },
            {
                "item_id": "b2",
                "sentence_with_blank": "She ___ coffee first.",
                "correct_answer": "drinks",
                "explanation": "Third person singular adds -s.",
            },
        ],
    }


def test_read_cloze_task_projects_to_fill_blanks_contract() -> None:
    payload = project_task_payload(
        "READ_CLOZE", _cloze_content(), activity_id="act-1", sequence=1
    )
    # Round-trips through the strict model — proves it is a valid contract payload.
    model = FillBlanksPayload.model_validate(payload)
    assert model.task_widget == "fill_blanks"
    assert model.archetype_id == "READ_CLOZE"
    assert model.activity_id == "act-1"
    assert model.section_label == "Reading"
    assert len(model.items) == 2
    assert model.items[0].base_verb == "wake"
    # Legacy/unknown keys were stripped, not smuggled through.
    assert "blank_index" not in payload["items"][0]


def test_task_projection_uses_primary_text_when_passage_absent() -> None:
    content = _cloze_content()
    content["passage"] = ""
    content["primary_text"] = "Maria ___ up at seven."
    payload = project_task_payload(
        "READ_CLOZE", content, activity_id="a", sequence=1
    )
    assert payload["passage"] == "Maria ___ up at seven."


def test_task_projection_rejects_payload_with_no_items() -> None:
    content = _cloze_content()
    content["items"] = []
    with pytest.raises(ContractValidationError):
        project_task_payload("READ_CLOZE", content, activity_id="a", sequence=1)


def test_evaluation_projection_derives_tier_and_percentage() -> None:
    result = EvaluationResult(
        raw_score=8.0,
        rubric_scores={"accuracy": 8.0},
        evaluator_notes="ok",
    )
    out = project_evaluation(
        "READ_CLOZE",
        activity_id="act-1",
        evaluation=result,
        sub_skill_breakdown={"verb_forms": 8.0},
    )
    assert out["tier"] == Tier.EXCELLENT.value
    assert out["percentage"] == 80.0
    assert out["raw_score"] == 8.0
    assert out["rubric_scores"] == {"accuracy": 8.0}
    assert out["pronunciation_assessment"] is None


def test_evaluation_projection_clamps_out_of_range_score() -> None:
    out = project_evaluation(
        "READ_CLOZE",
        activity_id="a",
        evaluation=EvaluationResult(raw_score=99.0),
    )
    assert out["raw_score"] == 10.0
    assert out["percentage"] == 100.0


def test_feedback_projection_maps_mistakes_and_optionals() -> None:
    fb = FeedbackResult(
        score=7,
        summary="Good work.",
        did_well=("Correct verb endings.",),
        mistakes=(
            MistakeOut(
                issue="Missing -s",
                user_wrote="She drink",
                correction="She drinks",
                rule="3rd person singular -s",
                sub_skills_affected=("verb_forms",),
            ),
        ),
        next_tip=None,
        sub_skill_breakdown={"verb_forms": 7},
    )
    out = project_feedback("READ_CLOZE", activity_id="act-1", feedback=fb)
    assert out["score"] == 7
    assert out["next_tip"] == ""  # None coerced to empty string by the contract
    assert out["mistakes"][0]["correction"] == "She drinks"
    assert out["did_well"] == ["Correct verb endings."]


# ── Per-family task projections (M3) ────────────────────────────────


def test_mcq_family_projects_with_audio_for_listening() -> None:
    content = {
        "topic": "Daily routines",
        "instructions": "Choose the best answer.",
        "audio_script": "Maria wakes up at seven.",
        "audio_url": "/audio/listen/maria.mp3",
        "audio_genre": "monologue",
        "audio_duration_seconds": 20,
        "items": [
            {
                "item_id": "q1",
                "prompt": "When does Maria wake up?",
                "options": ["Six", "Seven", "Eight"],
                "correct_index": 1,
                "explanation": "She wakes at seven.",
                "stray": "dropped",
            }
        ],
    }
    payload = project_task_payload("LISTEN_MCQ", content, activity_id="a", sequence=2)
    model = McqPayload.model_validate(payload)
    assert model.task_widget == "listen_mcq"
    assert model.items[0].correct_index == 1
    assert model.audio_script == "Maria wakes up at seven."
    assert model.audio_url == "/audio/listen/maria.mp3"
    assert "stray" not in payload["items"][0]


def test_tfng_family_coerces_answer_casing() -> None:
    content = {
        "passage": "Cats are mammals.",
        "instructions": "Decide.",
        "items": [
            {
                "item_id": "t1",
                "prompt": "Cats are mammals.",
                "correct_answer": "true",
                "explanation": "Stated directly.",
            },
            {
                "item_id": "t2",
                "prompt": "Cats can fly.",
                "correct_answer": "NOT GIVEN",
                "explanation": "Not stated.",
            },
        ],
    }
    payload = project_task_payload("READ_TFNG", content, activity_id="a", sequence=1)
    model = TfngPayload.model_validate(payload)
    assert [i.correct_answer for i in model.items] == ["True", "Not Given"]


def test_error_spotting_family_maps_sentences_and_drops_error_type() -> None:
    content = {
        "instructions": "Tap the wrong word.",
        "passage_sentences": [
            {
                "sentence_id": "s1",
                "tokens": [
                    {"token_id": "s1_t1", "text": "She", "is_error": False},
                    {"token_id": "s1_t2", "text": "goed", "is_error": True},
                ],
                "error": {
                    "token_id": "s1_t2",
                    "incorrect_phrase": "goed",
                    "correction": "went",
                    "error_type": "irregular_past",  # not in the strict contract
                    "rule": "Irregular past.",
                    "explanation": "go → went.",
                },
            }
        ],
    }
    payload = project_task_payload(
        "READ_ERROR_SPOT", content, activity_id="a", sequence=1
    )
    model = ErrorSpottingPayload.model_validate(payload)
    assert model.sentences[0].error.correction == "went"
    assert "error_type" not in payload["sentences"][0]["error"]


def test_dictation_family_requires_audio() -> None:
    content = {
        "instructions": "Type what you hear.",
        "audio_genre": "monologue",
        "audio_script": "She walks to work.",
        "audio_duration_seconds": 8,
        "items": [
            {
                "item_id": "d1",
                "prompt": "Sentence 1",
                "correct_answer": "She walks to work.",
                "explanation": "Listen for -s.",
            }
        ],
    }
    payload = project_task_payload(
        "LISTEN_DICTATION", content, activity_id="a", sequence=1
    )
    model = DictationPayload.model_validate(payload)
    assert model.audio_duration_seconds == 8
    assert len(model.items) == 1


def test_open_text_family_projects_items_and_hints() -> None:
    content = {
        "instructions": "Write three sentences.",
        "items": [
            {
                "item_id": "o1",
                "prompt": "Describe your morning.",
                "sample_answer": "I usually wake up at seven.",
                "answer_hints": ["Use a frequency adverb."],
            }
        ],
    }
    payload = project_task_payload(
        "WRITE_OPEN_SENT", content, activity_id="a", sequence=1
    )
    model = OpenTextPayload.model_validate(payload)
    assert model.items[0].answer_hints == ("Use a frequency adverb.",)


def test_transform_family_maps_source_alias() -> None:
    content = {
        "instructions": "Rewrite.",
        "items": [
            {
                "item_id": "tr1",
                "source": "The cat was chased by the dog.",  # alias for source_sentence
                "sample_answer": "The dog chased the cat.",
                "watch_hints": ["Move the object to subject."],
            }
        ],
    }
    payload = project_task_payload(
        "WRITE_SENT_TRANS", content, activity_id="a", sequence=1
    )
    model = TransformPayload.model_validate(payload)
    assert model.items[0].source_sentence == "The cat was chased by the dog."


def test_error_correction_family_projects_items() -> None:
    content = {
        "instructions": "Fix it.",
        "items": [
            {
                "item_id": "e1",
                "incorrect_sentence": "She walk to work.",
                "sample_answer": "She walks to work.",
                "watch_hints": ["Third person -s."],
            }
        ],
    }
    payload = project_task_payload(
        "WRITE_ERROR_CORR", content, activity_id="a", sequence=1
    )
    model = ErrorCorrectionPayload.model_validate(payload)
    assert model.items[0].sample_answer == "She walks to work."


def test_read_structure_family_projects_labels() -> None:
    content = {
        "instructions": "Label each paragraph.",
        "structure_labels": ["Intro", "Body", "Conclusion"],
        "items": [
            {
                "item_id": "p1",
                "paragraph": "This essay argues...",
                "correct_answer": "Intro",
                "explanation": "It introduces the thesis.",
            }
        ],
    }
    payload = project_task_payload(
        "READ_STRUCTURE_ID", content, activity_id="a", sequence=1
    )
    model = ReadStructurePayload.model_validate(payload)
    assert model.structure_labels == ("Intro", "Body", "Conclusion")


def test_speaking_family_maps_prompt_aliases() -> None:
    content = {
        "instructions": "Speak for 45 seconds.",
        "speaking_prompts": ["Describe your daily routine."],
        "sample_responses": ["I wake up at seven and..."],
        "speaking_duration_seconds": 60,
    }
    payload = project_task_payload("SPEAK_TIMED", content, activity_id="a", sequence=1)
    model = SpeakingPayload.model_validate(payload)
    assert model.prompts == ("Describe your daily routine.",)
    assert model.speaking_duration_seconds == 60


def test_speaking_family_maps_grammar_rule_to_practice_alias() -> None:
    content = {
        "instructions": "Speak for 45 seconds.",
        "speaking_prompts": ["Describe your morning routine."],
        "grammar_rule_to_practice": "Use simple present with frequency adverbs.",
    }
    payload = project_task_payload("SPEAK_TIMED", content, activity_id="a", sequence=1)
    model = SpeakingPayload.model_validate(payload)
    assert model.grammar_rule == "Use simple present with frequency adverbs."


def test_every_contract_archetype_has_a_task_builder() -> None:
    """Each registered archetype's payload model must have a projection builder
    so promoting it to the contract path can never hit the 'no builder' guard."""
    from app.modules.sessions.contracts import ARCHETYPE_CONTRACTS
    from app.modules.sessions.contracts.projection import _BODY_BUILDERS

    for contract in ARCHETYPE_CONTRACTS.values():
        assert contract.task_payload in _BODY_BUILDERS, contract.archetype_id
