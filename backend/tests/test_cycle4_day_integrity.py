"""Cycle 4 structural integrity lint — weeks 13-16, days 1-7 (28 days).

Mirror of ``test_cycle3_day_integrity`` for the B1+ cycle authored in
``source_24w.py``.
"""

from __future__ import annotations

import warnings

import pytest

from app.modules.curriculum import file_source
from app.modules.curriculum.data.source_24w import WEEKS_24
from app.modules.curriculum.file_source import SCRIPTED_PLAN_KEY
from app.modules.learning_session.service import LearningSessionService
from app.modules.sessions.contracts import (
    ARCHETYPE_CONTRACTS,
    KNOWN_TASK_WIDGETS,
    get_contract,
)
from app.scoring import ARCHETYPE_REGISTRY

CYCLE4_CASES: list[tuple[int, int]] = [
    (week, day_index) for week in range(13, 17) for day_index in range(7)
]
CYCLE4_IDS: list[str] = [
    f"day_24_{week:02d}_{day_index + 1:02d}" for week, day_index in CYCLE4_CASES
]

EXPECTED_ACTIVITY_ORDER = ["read", "listen", "write", "speak"]
EXPECTED_CYCLE4_ARCHETYPE_COUNT = 34


@pytest.mark.parametrize("week,day_index", CYCLE4_CASES, ids=CYCLE4_IDS)
def test_cycle4_day_is_valid(week: int, day_index: int) -> None:
    expected_id = f"day_24_{week:02d}_{day_index + 1:02d}"

    day = file_source.get_day(week, day_index)
    assert day.day_id == expected_id
    assert day.cefr_level == "B1+", f"{expected_id}: Cycle 4 must be B1+"
    assert day.topic.strip(), f"{expected_id}: empty topic"
    assert day.explanation_brief.strip(), f"{expected_id}: empty explanation_brief"

    assert (
        len(day.task_specs)
        == len(day.activity_contracts)
        == len(day.task_archetypes_used)
        == 4
    ), f"{expected_id}: expected exactly 4 activities"

    sequences = [contract["sequence"] for contract in day.activity_contracts]
    assert sequences == [1, 2, 3, 4], f"{expected_id}: sequences not 1..4 contiguous"

    activities = [spec["activity"] for spec in day.task_specs]
    assert activities == EXPECTED_ACTIVITY_ORDER, (
        f"{expected_id}: activity order {activities} != {EXPECTED_ACTIVITY_ORDER}"
    )

    assert all(c["mandatory"] is True for c in day.activity_contracts), (
        f"{expected_id}: every Cycle-4 activity must be mandatory"
    )

    activity_ids = [c["activity_id"] for c in day.activity_contracts]
    assert len(activity_ids) == len(set(activity_ids)), (
        f"{expected_id}: duplicate activity_id within day"
    )

    for i, archetype_id in enumerate(day.task_archetypes_used):
        assert archetype_id in ARCHETYPE_CONTRACTS, (
            f"{expected_id}[{i}]: unknown archetype {archetype_id!r}"
        )
        contract = get_contract(archetype_id)
        activity_contract = day.activity_contracts[i]
        spec_activity = day.task_specs[i]["activity"]

        assert contract.core_activity == spec_activity, (
            f"{expected_id}[{i}] {archetype_id}: core_activity "
            f"{contract.core_activity!r} != authored {spec_activity!r}"
        )
        assert activity_contract["task_widget"] == contract.task_widget, (
            f"{expected_id}[{i}] {archetype_id}: task_widget mismatch"
        )
        assert activity_contract["evaluation_widget"] == contract.evaluation_widget, (
            f"{expected_id}[{i}] {archetype_id}: evaluation_widget mismatch"
        )
        assert activity_contract["feedback_widget"] == contract.feedback_widget, (
            f"{expected_id}[{i}] {archetype_id}: feedback_widget mismatch"
        )

    for i in range(4):
        spec = file_source.task_spec_for(day, i)
        has_payload = bool(spec.get("payload"))
        assert spec.get("instructions_override") or has_payload, (
            f"{expected_id}[{i}]: needs generation_instructions or static payload"
        )
        assert spec.get("topic_override"), f"{expected_id}[{i}]: missing topic_override"
        if not has_payload and not spec.get("widget_requirements"):
            warnings.warn(
                f"{expected_id}[{i}] {day.task_archetypes_used[i]}: no "
                "widget_requirements and no static payload — review before manual QA.",
                stacklevel=2,
            )

    teacher = WEEKS_24[week - 1].days[day_index].teacher
    assert teacher.lesson_goal.strip(), f"{expected_id}: empty teacher.lesson_goal"
    assert teacher.readiness_prompt.strip(), (
        f"{expected_id}: empty teacher.readiness_prompt"
    )
    non_empty_steps = [s for s in teacher.steps if s.instruction.strip()]
    assert len(non_empty_steps) >= 3, (
        f"{expected_id}: only {len(non_empty_steps)} non-empty teacher steps (need >=3)"
    )
    assert len(day.teacher_agent_behaviour) == len(non_empty_steps), (
        f"{expected_id}: scripted plan length != non-empty teacher steps"
    )

    final_instruction = non_empty_steps[-1].instruction
    lowered = final_instruction.lower()
    has_readiness_language = ("ready" in lowered and "practice" in lowered) or (
        final_instruction.strip() == teacher.readiness_prompt.strip()
    )
    if not has_readiness_language:
        warnings.warn(
            f"{expected_id}: final teacher step lacks explicit readiness language "
            "('ready' + 'practice') and does not match readiness_prompt.",
            stacklevel=2,
        )

    assert day.final_review["scorecard_widget"] == "final_scorecard", expected_id
    assert day.final_review["rag_feedback_widget"] == "rag_feedback", expected_id


@pytest.mark.parametrize("week,day_index", CYCLE4_CASES, ids=CYCLE4_IDS)
def test_cycle4_persona_round_trip(week: int, day_index: int) -> None:
    day = file_source.get_day(week, day_index)

    topic, skill_name, sub_level, instr = LearningSessionService._persona_from_file(
        None,  # type: ignore[arg-type]
        day.day_id,
    )

    assert topic == day.topic
    assert skill_name == day.theme_type
    assert sub_level == day.sub_level_min

    assert isinstance(instr, dict)
    assert instr[SCRIPTED_PLAN_KEY] == list(day.teacher_agent_behaviour)
    assert instr["lesson_description"] == day.explanation_brief


def test_cycle4_archetype_coverage() -> None:
    cycle4_archetypes = {
        archetype_id
        for week, day_index in CYCLE4_CASES
        for archetype_id in file_source.get_day(week, day_index).task_archetypes_used
    }

    assert len(cycle4_archetypes) == EXPECTED_CYCLE4_ARCHETYPE_COUNT, (
        f"expected {EXPECTED_CYCLE4_ARCHETYPE_COUNT} unique Cycle-4 archetypes, "
        f"found {len(cycle4_archetypes)}: {sorted(cycle4_archetypes)}"
    )

    for archetype_id in sorted(cycle4_archetypes):
        assert archetype_id in ARCHETYPE_REGISTRY, archetype_id
        assert archetype_id in ARCHETYPE_CONTRACTS, archetype_id
        assert get_contract(archetype_id).task_widget in KNOWN_TASK_WIDGETS, archetype_id


@pytest.mark.parametrize("week,day_index", CYCLE4_CASES, ids=CYCLE4_IDS)
def test_cycle4_mirrors_cycle3_archetypes(week: int, day_index: int) -> None:
    """Day-for-day archetype layout must match week W-4 (cycle 3)."""
    expected = file_source.get_day(week - 4, day_index).task_archetypes_used
    actual = file_source.get_day(week, day_index).task_archetypes_used
    assert actual == expected, (
        f"day_24_{week:02d}_{day_index + 1:02d}: archetypes {actual} != mirror {expected}"
    )
