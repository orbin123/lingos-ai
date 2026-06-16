"""Cycle 1 structural integrity lint — weeks 1-4, days 1-7 (28 days).

A single parametrized "day lint" that guards the *structure* of every authored
Cycle-1 day so the human's manual live pass is feasible and diagnosable. It does
not exercise the LLM or DB; it only checks that the authored blueprints in
``source_24w.py`` flatten into a runtime shape that agrees with the canonical
archetype contract registry.

Layer 1 only — see the plan. Contract enablement / projection wiring is Layer 2.
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

# Cycle 1 = weeks 1-4 × days 1-7. ``day_index`` is 0-based.
CYCLE1_CASES: list[tuple[int, int]] = [
    (week, day_index) for week in range(1, 5) for day_index in range(7)
]
CYCLE1_IDS: list[str] = [
    f"day_24_{week:02d}_{day_index + 1:02d}" for week, day_index in CYCLE1_CASES
]

# Every authored Cycle-1 day ships in this fixed activity order. (The original
# brief's "read, write, listen, speak" table is inaccurate; the shipped data —
# and the existing W1D1 test — pin writing third.)
EXPECTED_ACTIVITY_ORDER = ["read", "listen", "write", "speak"]

# Guard against accidental archetype drift across Cycle 1.
EXPECTED_CYCLE1_ARCHETYPE_COUNT = 34


# ── A-F: per-day structural lint ─────────────────────────────────────────


@pytest.mark.parametrize("week,day_index", CYCLE1_CASES, ids=CYCLE1_IDS)
def test_cycle1_day_is_valid(week: int, day_index: int) -> None:
    expected_id = f"day_24_{week:02d}_{day_index + 1:02d}"

    # A. Addressable & populated.
    day = file_source.get_day(week, day_index)
    assert day.day_id == expected_id
    assert day.topic.strip(), f"{expected_id}: empty topic"
    assert day.explanation_brief.strip(), f"{expected_id}: empty explanation_brief"

    # B. Activity structure.
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
        f"{expected_id}: every Cycle-1 activity must be mandatory"
    )

    activity_ids = [c["activity_id"] for c in day.activity_contracts]
    assert len(activity_ids) == len(set(activity_ids)), (
        f"{expected_id}: duplicate activity_id within day"
    )

    # C. Archetype ↔ registry alignment. (The widget equalities double as a
    # check that any EvaluationBlueprint/FeedbackBlueprint override in source
    # matches the canonical registry — the adapter copies those into the
    # activity contract.)
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
            f"{expected_id}[{i}] {archetype_id}: task_widget "
            f"{activity_contract['task_widget']!r} != registry {contract.task_widget!r}"
        )
        assert activity_contract["evaluation_widget"] == contract.evaluation_widget, (
            f"{expected_id}[{i}] {archetype_id}: evaluation_widget "
            f"{activity_contract['evaluation_widget']!r} != registry "
            f"{contract.evaluation_widget!r}"
        )
        assert activity_contract["feedback_widget"] == contract.feedback_widget, (
            f"{expected_id}[{i}] {archetype_id}: feedback_widget "
            f"{activity_contract['feedback_widget']!r} != registry "
            f"{contract.feedback_widget!r}"
        )

    # D. Task spec completeness. A content source (generation_instructions or a
    # static payload) and topic_override are structurally required. Non-empty
    # widget_requirements drives task-gen quality but is warned, not asserted —
    # the original golden days (W1D1/W1D2) ship simple writing tasks without it.
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
                "widget_requirements and no static payload — task generation "
                "leans on generation_instructions alone; review before manual QA.",
                stacklevel=2,
            )

    # E. Teacher blueprint (strict structure; lenient final-step wording).
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
            "('ready' + 'practice') and does not match readiness_prompt — review "
            "before manual QA.",
            stacklevel=2,
        )

    # F. Final review widgets.
    assert day.final_review["scorecard_widget"] == "final_scorecard", expected_id
    assert day.final_review["rag_feedback_widget"] == "rag_feedback", expected_id


# ── G: file persona round-trip ───────────────────────────────────────────


@pytest.mark.parametrize("week,day_index", CYCLE1_CASES, ids=CYCLE1_IDS)
def test_cycle1_persona_round_trip(week: int, day_index: int) -> None:
    day = file_source.get_day(week, day_index)

    # ``_persona_from_file`` is an instance method but touches neither self.db
    # nor repos, so we call it on an unbound ``None`` self (matches the pattern
    # in test_learning_session_file_mode.py).
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


# ── Step 3: archetype coverage summary (informational guard) ─────────────


def test_cycle1_archetype_coverage() -> None:
    cycle1_archetypes = {
        archetype_id
        for week, day_index in CYCLE1_CASES
        for archetype_id in file_source.get_day(week, day_index).task_archetypes_used
    }

    assert len(cycle1_archetypes) == EXPECTED_CYCLE1_ARCHETYPE_COUNT, (
        f"expected {EXPECTED_CYCLE1_ARCHETYPE_COUNT} unique Cycle-1 archetypes, "
        f"found {len(cycle1_archetypes)}: {sorted(cycle1_archetypes)}"
    )

    for archetype_id in sorted(cycle1_archetypes):
        assert archetype_id in ARCHETYPE_REGISTRY, archetype_id
        assert archetype_id in ARCHETYPE_CONTRACTS, archetype_id
        # KNOWN_TASK_WIDGETS holds widget keys, not archetype ids — check the
        # archetype's resolved task widget is a known widget.
        assert get_contract(archetype_id).task_widget in KNOWN_TASK_WIDGETS, (
            archetype_id
        )


def _cycle1_archetypes() -> set[str]:
    return {
        archetype_id
        for week, day_index in CYCLE1_CASES
        for archetype_id in file_source.get_day(week, day_index).task_archetypes_used
    }


def test_authored_archetypes_all_have_contracts() -> None:
    """Drift guard: every archetype the authored Cycle-1 days reference must have
    a contract in the registry. The migration gate is gone — projection now runs
    unconditionally for all archetypes — so the invariant is contract coverage,
    not allowlist membership. Cycle-1 authors the full canonical set of 34."""
    authored = _cycle1_archetypes()
    missing = authored - set(ARCHETYPE_CONTRACTS)
    assert not missing, f"authored archetypes without a contract: {sorted(missing)}"
    assert authored == set(ARCHETYPE_CONTRACTS), {
        "authored_but_unregistered": sorted(authored - set(ARCHETYPE_CONTRACTS)),
        "registered_but_unauthored": sorted(set(ARCHETYPE_CONTRACTS) - authored),
    }
