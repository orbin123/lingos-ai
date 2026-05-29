"""Contract-registry guarantees.

These tests are the M1 referential-integrity guard: every scoring archetype has
a renderable contract, every authored curriculum day references only archetypes
that exist, and the strict payload schemas actually reject malformed output.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.sessions.contracts import (
    ARCHETYPE_CONTRACTS,
    EVALUATION_WIDGETS,
    FEEDBACK_WIDGETS,
    KNOWN_TASK_WIDGETS,
    TfngPayload,
    get_contract,
)
from app.modules.curriculum.data.source_24w import WEEKS_24
from app.scoring import ARCHETYPE_REGISTRY


def test_every_scoring_archetype_has_a_contract() -> None:
    assert set(ARCHETYPE_CONTRACTS) == set(ARCHETYPE_REGISTRY)


def test_contracts_reference_only_known_widgets() -> None:
    for contract in ARCHETYPE_CONTRACTS.values():
        assert contract.task_widget in KNOWN_TASK_WIDGETS, contract.archetype_id
        assert contract.evaluation_widget in EVALUATION_WIDGETS, contract.archetype_id
        assert contract.feedback_widget in FEEDBACK_WIDGETS, contract.archetype_id


def test_contract_rubric_matches_scoring_spec() -> None:
    for aid, spec in ARCHETYPE_REGISTRY.items():
        contract = get_contract(aid)
        assert contract.rubric == spec.rubric
        assert contract.weight_map == dict(spec.weight_map)


def test_authored_days_reference_only_contracted_archetypes() -> None:
    """No authored blueprint may name an archetype without a contract."""
    seen = 0
    for week in WEEKS_24:
        for day in week.days:
            for activity in day.activities:
                aid = activity.task.archetype_id
                assert aid in ARCHETYPE_CONTRACTS, (
                    f"week {week.week_number} names un-contracted archetype {aid!r}"
                )
                seen += 1
    assert seen > 0, "expected at least one authored activity in WEEKS_24"


def test_strict_payload_rejects_unknown_keys() -> None:
    with pytest.raises(ValidationError):
        TfngPayload(
            activity_id="a1",
            sequence=1,
            archetype_id="READ_TFNG",
            task_widget="read_tfng",
            core_activity="read",
            section_label="Reading",
            topic="t",
            task_intro="ti",
            instructions="do it",
            sub_skill="Comprehension",
            passage="p",
            items=[
                {
                    "item_id": "q1",
                    "prompt": "x",
                    "correct_answer": "True",
                    "explanation": "e",
                }
            ],
            bogus_field="nope",  # type: ignore[call-arg]
        )


def test_strict_payload_rejects_bad_tfng_enum() -> None:
    with pytest.raises(ValidationError):
        TfngPayload(
            activity_id="a1",
            sequence=1,
            archetype_id="READ_TFNG",
            task_widget="read_tfng",
            core_activity="read",
            section_label="Reading",
            topic="t",
            task_intro="ti",
            instructions="do it",
            sub_skill="Comprehension",
            passage="p",
            items=[
                {
                    "item_id": "q1",
                    "prompt": "x",
                    "correct_answer": "Maybe",  # not in enum
                    "explanation": "e",
                }
            ],
        )
