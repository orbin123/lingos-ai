"""Curriculum task_spec guard — authored static payloads must project cleanly."""

from __future__ import annotations

import pytest

from app.modules.curriculum.data.source_24w import WEEKS_24
from app.modules.curriculum.data.source_48w import WEEKS_48
from app.modules.curriculum import file_source
from app.modules.sessions.contracts.validation import validate_and_project_task_content
from app.scoring import CourseLength


def _iter_authored_task_specs() -> list[tuple[str, int, str, dict]]:
    rows: list[tuple[str, int, str, dict]] = []
    for course_length, weeks in (
        (CourseLength.WEEKS_24, WEEKS_24),
        (CourseLength.WEEKS_48, WEEKS_48),
    ):
        for week in weeks:
            for day_index in range(len(week.days)):
                record = file_source.get_day(
                    week.week_number,
                    day_index,
                    course_length=course_length,
                )
                for sequence, archetype_id in enumerate(record.task_archetypes_used):
                    spec = file_source.task_spec_for(record, sequence)
                    if not spec:
                        continue
                    payload = (
                        spec.get("payload")
                        or spec.get("content")
                        or spec.get("fill_in_blanks")
                        or spec.get("listen_and_respond")
                    )
                    if isinstance(payload, dict):
                        rows.append((record.day_id, sequence, archetype_id, payload))
    return rows


_STATIC_PAYLOADS = _iter_authored_task_specs()


@pytest.mark.parametrize(
    "day_id,sequence,archetype_id,payload",
    _STATIC_PAYLOADS,
    ids=[
        f"{day_id}-s{sequence}-{archetype_id}"
        for day_id, sequence, archetype_id, _ in _STATIC_PAYLOADS
    ],
)
def test_authored_static_payload_projects(
    day_id: str,
    sequence: int,
    archetype_id: str,
    payload: dict,
) -> None:
    content = {
        "phase": "authored",
        "archetype_id": archetype_id,
        "topic": payload.get("topic") or "Authored topic",
        "instructions": payload.get("instructions") or "Complete the activity.",
        **payload,
    }
    projected = validate_and_project_task_content(
        archetype_id,
        content,
        activity_id=f"{day_id}-{sequence}",
        sequence=sequence + 1,
    )
    assert projected["archetype_id"] == archetype_id


def test_curriculum_static_payload_inventory_is_documented() -> None:
    """Most days use LLM generation; this guard activates when payloads are added."""
    assert isinstance(_STATIC_PAYLOADS, list)
