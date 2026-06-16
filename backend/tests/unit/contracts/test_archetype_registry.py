"""Registry-level invariants — every archetype is well-formed."""

import pytest

from app.scoring.archetypes import (
    ARCHETYPE_REGISTRY,
    get_archetype,
    list_mvp_archetypes,
)
from app.scoring.constants import ARCHETYPE_WEIGHT_TOLERANCE, SUB_SKILLS


# Widgets known to the frontend registry. Composite listen archetypes use the
# "ListenAndAnswer + inner" convention from the spec §10.
_KNOWN_WIDGETS = {
    "MCQList",
    "TrueFalseNotGiven",
    "ErrorSpotting",
    "FillInBlanks",
    "OpenTextList",
    "SentenceTransform",
    "ErrorCorrection",
    "StructuredEssay",
    "PassageSummary",
    "TimedWriting",
    "SpeakAndRecord",
    "Storyboard",
    "ListenAndAnswer+MCQList",
    "ListenAndAnswer+FillInBlanks",
    "ListenAndAnswer+OpenTextList",
    "ListenAndAnswer+SpeakAndRecord",
    # Frontend WidgetKey values — used directly by archetypes that map 1:1
    "open_text",
    "fill_in_blanks",
    "listen_and_respond",
    "speak_and_record",
    "mcq",
    "timed_text",
    "storyboard",
    "structured_essay",
}


_PREFIX_TO_ACTIVITY = {
    "READ_": "read",
    "WRITE_": "write",
    "LISTEN_": "listen",
    "SPEAK_": "speak",
}


def test_registry_is_populated():
    # The registry is finalized at exactly the canonical 34 archetypes (the
    # single source of truth). See tests/test_archetype_sweep.py::THE_34.
    assert len(ARCHETYPE_REGISTRY) == 34


def test_no_duplicate_ids():
    ids = [s.archetype_id for s in ARCHETYPE_REGISTRY.values()]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize(
    "spec",
    list(ARCHETYPE_REGISTRY.values()),
    ids=lambda s: s.archetype_id,
)
def test_weights_sum_to_one(spec):
    total = sum(spec.weight_map.values())
    assert abs(total - 1.0) < ARCHETYPE_WEIGHT_TOLERANCE, (
        f"{spec.archetype_id} weights sum to {total}"
    )


@pytest.mark.parametrize(
    "spec",
    list(ARCHETYPE_REGISTRY.values()),
    ids=lambda s: s.archetype_id,
)
def test_weights_reference_known_sub_skills(spec):
    unknown = set(spec.weight_map) - set(SUB_SKILLS)
    assert not unknown, f"{spec.archetype_id} references unknown skills: {unknown}"


@pytest.mark.parametrize(
    "spec",
    list(ARCHETYPE_REGISTRY.values()),
    ids=lambda s: s.archetype_id,
)
def test_no_doc_aliased_names_leak_into_weight_map(spec):
    # We must not store doc names ("thought_org" etc.) in weight maps.
    leaks = {
        k for k in spec.weight_map if k in {"thought_org", "listening", "tone_social"}
    }
    assert not leaks, f"{spec.archetype_id} uses doc alias {leaks} — should be legacy"


@pytest.mark.parametrize(
    "spec",
    list(ARCHETYPE_REGISTRY.values()),
    ids=lambda s: s.archetype_id,
)
def test_ui_widget_is_known(spec):
    assert spec.ui_widget in _KNOWN_WIDGETS, (
        f"{spec.archetype_id} uses unknown widget {spec.ui_widget!r}"
    )


@pytest.mark.parametrize(
    "spec",
    list(ARCHETYPE_REGISTRY.values()),
    ids=lambda s: s.archetype_id,
)
def test_core_activity_matches_id_prefix(spec):
    for prefix, activity in _PREFIX_TO_ACTIVITY.items():
        if spec.archetype_id.startswith(prefix):
            assert spec.core_activity == activity, (
                f"{spec.archetype_id} prefix says {activity!r} "
                f"but core_activity is {spec.core_activity!r}"
            )
            return
    pytest.fail(f"{spec.archetype_id} has an unrecognised prefix")


def test_get_archetype_returns_matching_spec():
    spec = get_archetype("WRITE_EMAIL")
    assert spec.archetype_id == "WRITE_EMAIL"
    assert spec.weight_map == {
        "grammar": 0.25,
        "vocabulary": 0.20,
        "expression": 0.15,
        "tone": 0.40,
    }


def test_get_archetype_unknown_raises():
    with pytest.raises(KeyError, match="unknown archetype_id"):
        get_archetype("WRITE_DOES_NOT_EXIST")


def test_list_mvp_archetypes_returns_only_mvp():
    mvp = list_mvp_archetypes()
    assert all(s.mvp for s in mvp)
    assert len(mvp) == sum(1 for s in ARCHETYPE_REGISTRY.values() if s.mvp)
