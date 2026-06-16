"""Headless archetype sweep — the 34 archetypes are the single source of truth.

This replaces manual day-by-day clicking. It proves, with
``settings.strict_contracts=True`` (set by ``conftest``):

1. The contract registry contains exactly the finalized 34 archetypes.
2. Every authored day across all 24 weeks resolves to archetypes that project
   cleanly through ``project_task_payload`` / ``project_evaluation`` /
   ``project_feedback``. Any contract failure is reported with the exact
   ``(week, day, archetype, field)``.
3. Every archetype referenced in ``source_24w.py`` is one of the 34.

Representative loose content is keyed by payload family — the same construction
pattern used by ``test_contract_projection.py``.
"""

from __future__ import annotations

import pytest

from app.core.config import settings
from app.modules.curriculum.data.source_24w import WEEKS_24
from app.modules.sessions.contracts import (
    ARCHETYPE_CONTRACTS,
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
from app.modules.sessions.contracts.registry import get_contract
from app.modules.sessions.evaluator import EvaluationResult
from app.modules.sessions.feedback_generator import FeedbackResult, MistakeOut


# ── THE source of truth — nothing else is valid ─────────────────────────────

THE_34: frozenset[str] = frozenset(
    {
        # Reading (8)
        "READ_COMP_MCQ",
        "READ_TFNG",
        "READ_ERROR_SPOT",
        "READ_CLOZE",
        "READ_WORD_MATCH",
        "READ_CONTEXT_MCQ",
        "READ_TONE_ID",
        "READ_STRUCTURE_ID",
        # Writing (10)
        "WRITE_OPEN_SENT",
        "WRITE_SENT_TRANS",
        "WRITE_ERROR_CORR",
        "WRITE_PARA",
        "WRITE_EMAIL",
        "WRITE_PARAPHRASE",
        "WRITE_BULLETS_TO_PARA",
        "WRITE_IDEA_PARA",
        "WRITE_WORD_UPGRADE",
        "WRITE_TIMED",
        # Listening (7)
        "LISTEN_MCQ",
        "LISTEN_CLOZE",
        "LISTEN_DICTATION",
        "LISTEN_INFER",
        "LISTEN_RETELL",
        "LISTEN_SHADOW",
        "LISTEN_TONE",
        # Speaking (9)
        "SPEAK_READ_ALOUD",
        "SPEAK_PIC_DESC",
        "SPEAK_TIMED",
        "SPEAK_INTERVIEW",
        "SPEAK_ROLEPLAY",
        "SPEAK_OPINION",
        "SPEAK_SMALLTALK",
        "SPEAK_DEBATE",
        "SPEAK_PRESENT",
    }
)


def test_strict_contracts_enabled() -> None:
    assert settings.strict_contracts is True, (
        "the sweep must run with STRICT_CONTRACTS=true (conftest sets it)"
    )


def test_registry_equals_the_34() -> None:
    assert len(THE_34) == 34
    registered = set(ARCHETYPE_CONTRACTS)
    assert registered == set(THE_34), {
        "missing_from_registry": sorted(set(THE_34) - registered),
        "unexpected_in_registry": sorted(registered - set(THE_34)),
    }


# ── Representative loose content per payload family ──────────────────────────

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
        "audio_url": "/audio/listen/sample.mp3",
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


def test_every_family_has_loose_content() -> None:
    """Guard: every one of the 34 maps to a family with a loose-content builder."""
    for archetype_id in sorted(THE_34):
        assert get_contract(archetype_id).task_payload in _CONTENT_BY_PAYLOAD, (
            archetype_id
        )


# ── Authored-curriculum sweep across all 24 weeks ───────────────────────────

DAY_CASES: list[tuple[int, int]] = [
    (week.week_number, day_index)
    for week in WEEKS_24
    for day_index in range(len(week.days))
]
DAY_IDS: list[str] = [f"w{week:02d}d{day + 1}" for week, day in DAY_CASES]


def _day_archetypes(week_number: int, day_index: int) -> list[str]:
    week = next(w for w in WEEKS_24 if w.week_number == week_number)
    day = week.days[day_index]
    return [activity.task.archetype_id for activity in day.activities]


def _authored_archetypes() -> set[str]:
    return {
        activity.task.archetype_id
        for week in WEEKS_24
        for day in week.days
        for activity in day.activities
    }


def test_every_authored_archetype_is_one_of_the_34() -> None:
    used = _authored_archetypes()
    extra = used - set(THE_34)
    assert not extra, (
        f"source_24w.py references non-canonical archetypes: {sorted(extra)}"
    )
    # Vice-versa, modulo unused: report (do not fail) any of the 34 never authored.
    unused = set(THE_34) - used
    if unused:
        print(
            f"Archetypes in THE_34 not authored by any day (allowed): {sorted(unused)}"
        )


@pytest.mark.parametrize("week_number,day_index", DAY_CASES, ids=DAY_IDS)
def test_authored_day_projects_end_to_end(week_number: int, day_index: int) -> None:
    """Every archetype on every authored day projects task + eval + feedback."""
    for archetype_id in _day_archetypes(week_number, day_index):
        where = f"week={week_number}, day={day_index + 1}, archetype={archetype_id}"
        assert archetype_id in THE_34, f"({where}) is not one of the 34"

        contract = get_contract(archetype_id)
        try:
            payload = project_task_payload(
                archetype_id,
                _content_for(archetype_id),
                activity_id="act-1",
                sequence=1,
            )
            contract.task_payload.model_validate(payload)

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
                    _PRONUNCIATION_ASSESSMENT if contract.has_pronunciation else None
                ),
            )
            assert eval_out["archetype_id"] == archetype_id

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
            assert fb_out["archetype_id"] == archetype_id
        except ContractValidationError as exc:
            pytest.fail(f"({where}, field={exc.detail})")
