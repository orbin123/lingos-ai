"""A1A2 band teacher blueprint lint — structure and risky authoring patterns.

Guards ``source_L_A1A2.py`` (base + ``depth_day``) without live LLM or chat QA.
Risky-pattern hits are warnings so existing copy can be cleaned incrementally.
"""

from __future__ import annotations

import re
import warnings

import pytest

from app.modules.curriculum.blueprint_adapter import _teacher_script
from app.modules.curriculum.data.source_L_A1A2 import WEEKS_A1A2
from app.modules.curriculum.data.types import DaySource, TeacherBlueprint

# Illustrative question forms in step text often become a second ``?`` in model
# output and interact badly with teacher repair (see teacher._collapse_to_single_question).
_RISKY_ILLUSTRATION = re.compile(
    r"\(Do you|Did you|So you mean|Sorry, do you mean",
    re.IGNORECASE,
)
_ELLIPSIS_QUESTION = re.compile(r"…\?|\.\.\.\?")

A1A2_DAY_CASES: list[tuple[int, int, str, DaySource]] = []
for _week in WEEKS_A1A2:
    for _day_index, _day in enumerate(_week.days):
        A1A2_DAY_CASES.append((_week.week_number, _day_index + 1, "base", _day))
        if _day.depth_day is not None:
            A1A2_DAY_CASES.append(
                (_week.week_number, _day_index + 1, "depth", _day.depth_day)
            )

A1A2_DAY_IDS = [
    f"w{week:02d}_d{day_index:02d}_{variant}"
    for week, day_index, variant, _ in A1A2_DAY_CASES
]


def _lint_teacher_steps(
    *,
    label: str,
    teacher: TeacherBlueprint,
    scripted: tuple[str, ...],
) -> list[str]:
    issues: list[str] = []
    non_empty = [s for s in teacher.steps if s.instruction.strip()]
    if len(non_empty) < 3:
        issues.append(f"{label}: fewer than 3 non-empty teacher steps")
    if len(scripted) != len(non_empty):
        issues.append(
            f"{label}: scripted plan length {len(scripted)} != "
            f"{len(non_empty)} non-empty steps"
        )
    if not teacher.lesson_goal.strip():
        issues.append(f"{label}: empty lesson_goal")

    for index, step in enumerate(non_empty):
        instr = step.instruction.strip()
        step_label = f"{label} step {index + 1} ({step.id})"
        q_count = instr.count("?")
        is_readiness = "ready" in instr.lower() and "practice" in instr.lower()
        if q_count > 1:
            issues.append(f"{step_label}: {q_count} question marks in one step")
        if not is_readiness and _RISKY_ILLUSTRATION.search(instr):
            issues.append(
                f"{step_label}: illustrative question form in parentheses "
                "(prefer 'Do you plus verb' without ?)"
            )
        if not is_readiness and _ELLIPSIS_QUESTION.search(instr):
            issues.append(
                f"{step_label}: ellipsis question example (…? / ...?) "
                "often becomes a truncated learner-facing turn"
            )
    return issues


@pytest.mark.parametrize(
    "week_number,day_index,variant,day_source",
    A1A2_DAY_CASES,
    ids=A1A2_DAY_IDS,
)
def test_a1a2_teacher_blueprint_structure(
    week_number: int,
    day_index: int,
    variant: str,
    day_source: DaySource,
) -> None:
    label = f"A1A2 w{week_number} d{day_index} {variant}"
    teacher = day_source.teacher
    scripted = _teacher_script(day_source)

    assert teacher.readiness_prompt.strip(), f"{label}: empty readiness_prompt"
    assert len(day_source.activities) == 4, f"{label}: expected 4 activities"

    structural = [
        issue
        for issue in _lint_teacher_steps(
            label=label, teacher=teacher, scripted=scripted
        )
        if "fewer than 3" in issue
        or "scripted plan length" in issue
        or "empty lesson_goal" in issue
    ]
    assert not structural, structural

    risky = [
        issue
        for issue in _lint_teacher_steps(
            label=label, teacher=teacher, scripted=scripted
        )
        if issue not in structural
    ]
    for issue in risky:
        warnings.warn(issue, stacklevel=2)


def test_a1a2_band_has_full_depth_coverage() -> None:
    missing = [
        (w.week_number, di + 1)
        for w in WEEKS_A1A2
        for di, d in enumerate(w.days)
        if d.depth_day is None
    ]
    assert not missing, f"missing depth_day: {missing}"
    assert len(A1A2_DAY_CASES) == 8 * 7 * 2, "expected 112 base+depth day records"
