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


def test_dictation_family_fills_correct_answer_from_sample_or_target_words() -> None:
    content = {
        "instructions": "Type what you hear.",
        "audio_genre": "classroom",
        "audio_script": "I am reading a book. The students are studying together.",
        "audio_duration_seconds": 12,
        "target_words": ["am reading", "are studying"],
        "items": [
            {
                "item_id": "d1",
                "prompt": "I ___ a book.",
                "sample_answer": "am reading",
                "explanation": "Use am with I.",
            },
            {
                "item_id": "d2",
                "prompt": "The students ___ together.",
                "explanation": "Plural subject uses are.",
            },
        ],
    }
    payload = project_task_payload(
        "LISTEN_DICTATION", content, activity_id="a", sequence=1
    )
    assert payload["items"][0]["correct_answer"] == "I am reading a book."
    assert payload["items"][1]["correct_answer"] == "The students are studying together."


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


def test_transform_family_maps_prompt_alias() -> None:
    content = {
        "instructions": "Rewrite into present continuous.",
        "items": [
            {
                "item_id": "st1",
                "prompt": "She walks to school.",
                "sample_answer": "She is walking to school.",
                "watch_hints": ["she -> is", "walk -> walking"],
            }
        ],
    }
    payload = project_task_payload(
        "WRITE_SENT_TRANS", content, activity_id="a", sequence=1
    )
    model = TransformPayload.model_validate(payload)
    assert model.items[0].source_sentence == "She walks to school."


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


def test_speak_pic_desc_maps_image_fields() -> None:
    content = {
        "instructions": "Describe the picture aloud.",
        "speaking_prompts": ["Describe the cat using 'a' or 'the'."],
        "sample_responses": ["I see a cat on the sofa."],
        "image_alt": "A cat sleeping on a sofa next to an open book.",
        "image_url": "/images/ab/scene.png",
        "speaking_duration_seconds": 45,
    }
    payload = project_task_payload("SPEAK_PIC_DESC", content, activity_id="a", sequence=1)
    model = SpeakingPayload.model_validate(payload)
    assert model.task_widget == "speak_pic_desc"
    assert model.image_alt == "A cat sleeping on a sofa next to an open book."
    assert model.image_url == "/images/ab/scene.png"
    assert model.prompts == ("Describe the cat using 'a' or 'the'.",)


def test_speak_interview_projects_questions_and_context() -> None:
    content = {
        "instructions": "Answer the interview questions aloud.",
        "interview_context": "A friendly mini interview about yourself.",
        "questions": [
            {
                "interviewer_prompt": "What is your name?",
                "sample_answer": "My name is Sam.",
                "answer_hint": "Use 'My name is'.",
            },
            {
                "prompt": "What do you do?",
                "sample_answer": "I'm a teacher.",
            },
        ],
        "speaking_duration_seconds": 30,
    }
    payload = project_task_payload("SPEAK_INTERVIEW", content, activity_id="a", sequence=1)
    model = SpeakingPayload.model_validate(payload)
    assert model.task_widget == "speak_interview"
    assert model.interview_context == "A friendly mini interview about yourself."
    assert len(model.questions) == 2
    assert model.questions[0].item_id == "item_1"
    assert model.questions[0].interviewer_prompt == "What is your name?"
    assert model.questions[0].sample_answer == "My name is Sam."
    assert model.questions[0].answer_hint == "Use 'My name is'."
    # Falls back from `prompt` alias and synthesizes item_id.
    assert model.questions[1].item_id == "item_2"
    assert model.questions[1].interviewer_prompt == "What do you do?"


def test_every_contract_archetype_has_a_task_builder() -> None:
    """Each registered archetype's payload model must have a projection builder
    so promoting it to the contract path can never hit the 'no builder' guard."""
    from app.modules.sessions.contracts import ARCHETYPE_CONTRACTS
    from app.modules.sessions.contracts.projection import _BODY_BUILDERS

    for contract in ARCHETYPE_CONTRACTS.values():
        assert contract.task_payload in _BODY_BUILDERS, contract.archetype_id


# ── Cycle-1: every archetype projects task + eval + feedback ────────────────
#
# All 34 Cycle-1 archetypes flow through the strict schema-boundary path
# unconditionally (no allowlist). This block proves each one projects end to
# end — loose content → strict task contract, EvaluationResult → eval contract,
# FeedbackResult → feedback contract — so the runtime can never silently fall
# back to legacy.

from app.modules.sessions.contracts.evaluation import (  # noqa: E402
    ActivityEvaluationOutput,
    PronunciationAssessment,
)
from app.modules.sessions.contracts.feedback import (  # noqa: E402
    ActivityFeedbackOutput,
)
from app.modules.sessions.contracts.registry import get_contract  # noqa: E402

# The 34 unique archetypes authored across Cycle-1 (weeks 1-4). Kept explicit
# here; ``test_cycle1_day_integrity`` guards the count/membership against source.
CYCLE1_ARCHETYPES: tuple[str, ...] = (
    "READ_CLOZE", "READ_COMP_MCQ", "READ_CONTEXT_MCQ", "READ_ERROR_SPOT",
    "READ_STRUCTURE_ID", "READ_TFNG", "READ_TONE_ID", "READ_WORD_MATCH",
    "WRITE_BULLETS_TO_PARA", "WRITE_EMAIL", "WRITE_ERROR_CORR", "WRITE_IDEA_PARA",
    "WRITE_OPEN_SENT", "WRITE_PARA", "WRITE_PARAPHRASE", "WRITE_SENT_TRANS",
    "WRITE_TIMED", "WRITE_WORD_UPGRADE",
    "LISTEN_CLOZE", "LISTEN_DICTATION", "LISTEN_INFER", "LISTEN_MCQ",
    "LISTEN_RETELL", "LISTEN_SHADOW", "LISTEN_TONE",
    "SPEAK_DEBATE", "SPEAK_INTERVIEW", "SPEAK_OPINION", "SPEAK_PIC_DESC",
    "SPEAK_PRESENT", "SPEAK_READ_ALOUD", "SPEAK_ROLEPLAY", "SPEAK_SMALLTALK",
    "SPEAK_TIMED",
)

_PRONUNCIATION_ASSESSMENT = {
    "overall_score": 82.0,
    "accuracy_score": 85.0,
    "fluency_score": 80.0,
    "completeness_score": 90.0,
    "words": [{"word": "walked", "accuracy_score": 88.0, "error_type": "none"}],
}


def _fill_blanks_loose() -> dict:
    return {
        "passage": "Maria ___ up at seven. She ___ coffee first.",
        "items": [
            {
                "item_id": "b1",
                "sentence_with_blank": "Maria ___ up at seven.",
                "base_verb": "wake",
                "correct_answer": "wakes",
                "explanation": "Third person singular adds -s.",
            },
        ],
    }


def _mcq_loose() -> dict:
    return {
        "items": [
            {
                "item_id": "q1",
                "prompt": "When does Maria wake up?",
                "options": ["Six", "Seven", "Eight"],
                "correct_index": 1,
                "explanation": "She wakes at seven.",
            }
        ],
    }


def _tfng_loose() -> dict:
    return {
        "passage": "Cats are mammals.",
        "items": [
            {
                "item_id": "t1",
                "prompt": "Cats are mammals.",
                "correct_answer": "true",
                "explanation": "Stated directly.",
            }
        ],
    }


def _error_spotting_loose() -> dict:
    return {
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
                    "rule": "Irregular past.",
                    "explanation": "go → went.",
                },
            }
        ],
    }


def _dictation_loose() -> dict:
    return {
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


def _open_text_loose() -> dict:
    return {
        "items": [
            {
                "item_id": "o1",
                "prompt": "Describe your morning.",
                "sample_answer": "I usually wake up at seven.",
                "answer_hints": ["Use a frequency adverb."],
            }
        ],
    }


def _transform_loose() -> dict:
    return {
        "items": [
            {
                "item_id": "tr1",
                "source_sentence": "The cat was chased by the dog.",
                "sample_answer": "The dog chased the cat.",
                "watch_hints": ["Move the object to subject."],
            }
        ],
    }


def _error_correction_loose() -> dict:
    return {
        "items": [
            {
                "item_id": "e1",
                "incorrect_sentence": "She walk to work.",
                "sample_answer": "She walks to work.",
                "watch_hints": ["Third person -s."],
            }
        ],
    }


def _read_structure_loose() -> dict:
    return {
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


def _speaking_loose() -> dict:
    return {
        "speaking_prompts": ["Describe your daily routine."],
        "sample_responses": ["I wake up at seven and..."],
        "speaking_duration_seconds": 60,
    }


_CONTENT_BY_PAYLOAD = {
    FillBlanksPayload: _fill_blanks_loose,
    McqPayload: _mcq_loose,
    TfngPayload: _tfng_loose,
    ErrorSpottingPayload: _error_spotting_loose,
    DictationPayload: _dictation_loose,
    OpenTextPayload: _open_text_loose,
    TransformPayload: _transform_loose,
    ErrorCorrectionPayload: _error_correction_loose,
    ReadStructurePayload: _read_structure_loose,
    SpeakingPayload: _speaking_loose,
}


def _content_for(archetype_id: str) -> dict:
    """Minimal valid loose content for an archetype, keyed by its payload family."""
    return _CONTENT_BY_PAYLOAD[get_contract(archetype_id).task_payload]()


def test_cycle1_fixture_factory_covers_every_family() -> None:
    """Guard: every Cycle-1 archetype maps to a family with a loose-content builder."""
    for archetype_id in CYCLE1_ARCHETYPES:
        assert get_contract(archetype_id).task_payload in _CONTENT_BY_PAYLOAD, archetype_id


@pytest.mark.parametrize("archetype_id", CYCLE1_ARCHETYPES)
def test_cycle1_archetype_projects_end_to_end(archetype_id: str) -> None:
    contract = get_contract(archetype_id)

    # 1-3. Task content projects and round-trips through its strict contract.
    payload = project_task_payload(
        archetype_id, _content_for(archetype_id), activity_id="act-1", sequence=1
    )
    task_model = contract.task_payload.model_validate(payload)
    assert task_model.archetype_id == archetype_id
    assert task_model.task_widget == contract.task_widget
    assert task_model.core_activity == contract.core_activity

    # 4 + 6. Evaluation projects; pronunciation archetypes carry an assessment.
    is_pronunciation = contract.has_pronunciation
    eval_out = project_evaluation(
        archetype_id,
        activity_id="act-1",
        evaluation=EvaluationResult(
            raw_score=8.0,
            rubric_scores={"accuracy": 8.0},
            evaluator_notes="ok",
        ),
        sub_skill_breakdown={"grammar": 8.0},
        pronunciation_assessment=(
            _PRONUNCIATION_ASSESSMENT if is_pronunciation else None
        ),
    )
    ActivityEvaluationOutput.model_validate(eval_out)  # round-trips
    assert eval_out["archetype_id"] == archetype_id
    if is_pronunciation:
        assert eval_out["pronunciation_assessment"] is not None
        PronunciationAssessment.model_validate(eval_out["pronunciation_assessment"])
    else:
        assert eval_out["pronunciation_assessment"] is None

    # 5. Feedback projects and round-trips.
    fb_out = project_feedback(
        archetype_id,
        activity_id="act-1",
        feedback=FeedbackResult(
            score=7,
            summary="Good effort.",
            did_well=("Clear structure.",),
            mistakes=(
                MistakeOut(
                    issue="Minor slip",
                    user_wrote="She walk",
                    correction="She walks",
                    rule="3rd person -s",
                    sub_skills_affected=("grammar",),
                ),
            ),
            next_tip=None,
            sub_skill_breakdown={"grammar": 7},
        ),
    )
    ActivityFeedbackOutput.model_validate(fb_out)  # round-trips
    assert fb_out["archetype_id"] == archetype_id
