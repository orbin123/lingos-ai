"""Headless structural lint for file-authored curriculum calendar days.

Shared by ``tests/test_all_calendar_days_integrity.py`` and
``scripts/lint_curriculum_day.py``. Exercises no LLM and no DB — only checks
that composed source days flatten into a runtime shape the chat session can load.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from app.modules.curriculum import file_source
from app.modules.curriculum.data.composer import compose_weeks
from app.modules.curriculum.file_source import FileDayRecord, SCRIPTED_PLAN_KEY
from app.modules.learning_session.service import LearningSessionService
from app.modules.sessions.contracts import ARCHETYPE_CONTRACTS, get_contract
from app.modules.sessions.contracts.projection import ContractValidationError
from app.modules.sessions.contracts.validation import validate_and_project_task_content
from app.scoring import CourseLength

EXPECTED_ACTIVITY_ORDER = ("read", "listen", "write", "speak")
Severity = Literal["error", "warning"]


@dataclass(frozen=True)
class DayLintIssue:
    severity: Severity
    check: str
    message: str
    day_id: str
    archetype_id: str | None = None
    sequence: int | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "severity": self.severity,
            "check": self.check,
            "message": self.message,
            "day_id": self.day_id,
        }
        if self.archetype_id is not None:
            out["archetype_id"] = self.archetype_id
        if self.sequence is not None:
            out["sequence"] = self.sequence
        return out


def iter_calendar_day_ids(*, track: str = "all") -> list[str]:
    """Return ``day_24_*`` / ``day_48_*`` ids for the requested track."""
    lengths: tuple[CourseLength, ...]
    if track == "24w":
        lengths = (CourseLength.WEEKS_24,)
    elif track == "48w":
        lengths = (CourseLength.WEEKS_48,)
    else:
        lengths = (CourseLength.WEEKS_24, CourseLength.WEEKS_48)

    day_ids: list[str] = []
    for course_length in lengths:
        for week in compose_weeks(course_length):
            for day_index in range(len(week.days)):
                record = file_source.get_day(
                    week.week_number,
                    day_index,
                    course_length=course_length,
                )
                day_ids.append(record.day_id)
    return day_ids


def _issue(
    *,
    severity: Severity,
    check: str,
    message: str,
    day_id: str,
    archetype_id: str | None = None,
    sequence: int | None = None,
) -> DayLintIssue:
    return DayLintIssue(
        severity=severity,
        check=check,
        message=message,
        day_id=day_id,
        archetype_id=archetype_id,
        sequence=sequence,
    )


def _static_payload_from_spec(spec: dict) -> dict | None:
    payload = (
        spec.get("payload")
        or spec.get("content")
        or spec.get("fill_in_blanks")
        or spec.get("listen_and_respond")
    )
    return payload if isinstance(payload, dict) else None


def lint_day_structure(day: FileDayRecord) -> list[DayLintIssue]:
    """Structural checks (A–F) for one composed calendar day."""
    issues: list[DayLintIssue] = []
    day_id = day.day_id

    if not day.topic.strip():
        issues.append(
            _issue(
                severity="error",
                check="topic",
                message="empty topic",
                day_id=day_id,
            )
        )
    if not day.explanation_brief.strip():
        issues.append(
            _issue(
                severity="error",
                check="explanation_brief",
                message="empty explanation_brief",
                day_id=day_id,
            )
        )

    activity_count = len(day.task_archetypes_used)
    if not (len(day.task_specs) == len(day.activity_contracts) == activity_count == 4):
        issues.append(
            _issue(
                severity="error",
                check="activity_count",
                message=(
                    f"expected exactly 4 activities, got specs={len(day.task_specs)} "
                    f"contracts={len(day.activity_contracts)} "
                    f"archetypes={activity_count}"
                ),
                day_id=day_id,
            )
        )
        return issues

    sequences = [contract["sequence"] for contract in day.activity_contracts]
    if sequences != [1, 2, 3, 4]:
        issues.append(
            _issue(
                severity="error",
                check="activity_sequences",
                message=f"sequences not 1..4 contiguous: {sequences}",
                day_id=day_id,
            )
        )

    activities = [spec["activity"] for spec in day.task_specs]
    if activities != list(EXPECTED_ACTIVITY_ORDER):
        issues.append(
            _issue(
                severity="error",
                check="activity_order",
                message=(
                    f"activity order {activities} != {list(EXPECTED_ACTIVITY_ORDER)}"
                ),
                day_id=day_id,
            )
        )

    if not all(c["mandatory"] is True for c in day.activity_contracts):
        issues.append(
            _issue(
                severity="error",
                check="mandatory",
                message="every activity must be mandatory",
                day_id=day_id,
            )
        )

    activity_ids = [c["activity_id"] for c in day.activity_contracts]
    if len(activity_ids) != len(set(activity_ids)):
        issues.append(
            _issue(
                severity="error",
                check="activity_id_unique",
                message="duplicate activity_id within day",
                day_id=day_id,
            )
        )

    for i, archetype_id in enumerate(day.task_archetypes_used):
        seq = i + 1
        if archetype_id not in ARCHETYPE_CONTRACTS:
            issues.append(
                _issue(
                    severity="error",
                    check="archetype_registry",
                    message=f"unknown archetype {archetype_id!r}",
                    day_id=day_id,
                    archetype_id=archetype_id,
                    sequence=seq,
                )
            )
            continue

        contract = get_contract(archetype_id)
        activity_contract = day.activity_contracts[i]
        spec_activity = day.task_specs[i]["activity"]

        if contract.core_activity != spec_activity:
            issues.append(
                _issue(
                    severity="error",
                    check="core_activity",
                    message=(
                        f"core_activity {contract.core_activity!r} "
                        f"!= authored {spec_activity!r}"
                    ),
                    day_id=day_id,
                    archetype_id=archetype_id,
                    sequence=seq,
                )
            )
        if activity_contract["task_widget"] != contract.task_widget:
            issues.append(
                _issue(
                    severity="error",
                    check="task_widget",
                    message=(
                        f"task_widget {activity_contract['task_widget']!r} "
                        f"!= registry {contract.task_widget!r}"
                    ),
                    day_id=day_id,
                    archetype_id=archetype_id,
                    sequence=seq,
                )
            )
        if activity_contract["evaluation_widget"] != contract.evaluation_widget:
            issues.append(
                _issue(
                    severity="error",
                    check="evaluation_widget",
                    message=(
                        f"evaluation_widget "
                        f"{activity_contract['evaluation_widget']!r} != registry "
                        f"{contract.evaluation_widget!r}"
                    ),
                    day_id=day_id,
                    archetype_id=archetype_id,
                    sequence=seq,
                )
            )
        if activity_contract["feedback_widget"] != contract.feedback_widget:
            issues.append(
                _issue(
                    severity="error",
                    check="feedback_widget",
                    message=(
                        f"feedback_widget {activity_contract['feedback_widget']!r} "
                        f"!= registry {contract.feedback_widget!r}"
                    ),
                    day_id=day_id,
                    archetype_id=archetype_id,
                    sequence=seq,
                )
            )

    for i in range(4):
        seq = i + 1
        archetype_id = day.task_archetypes_used[i]
        spec = file_source.task_spec_for(day, i)
        has_payload = bool(spec.get("payload"))
        if not spec.get("instructions_override") and not has_payload:
            issues.append(
                _issue(
                    severity="error",
                    check="task_spec_content",
                    message="needs generation_instructions or static payload",
                    day_id=day_id,
                    archetype_id=archetype_id,
                    sequence=seq,
                )
            )
        if not spec.get("topic_override"):
            issues.append(
                _issue(
                    severity="error",
                    check="topic_override",
                    message="missing topic_override",
                    day_id=day_id,
                    archetype_id=archetype_id,
                    sequence=seq,
                )
            )
        if not has_payload and not spec.get("widget_requirements"):
            issues.append(
                _issue(
                    severity="warning",
                    check="widget_requirements",
                    message=(
                        "no widget_requirements and no static payload — task "
                        "generation leans on generation_instructions alone"
                    ),
                    day_id=day_id,
                    archetype_id=archetype_id,
                    sequence=seq,
                )
            )

    lesson_goal = str(day.teacher_instructions.get("lesson_goal") or "").strip()
    readiness_prompt = str(
        day.teacher_instructions.get("readiness_prompt") or ""
    ).strip()
    if not lesson_goal:
        issues.append(
            _issue(
                severity="error",
                check="lesson_goal",
                message="empty teacher.lesson_goal",
                day_id=day_id,
            )
        )
    if not readiness_prompt:
        issues.append(
            _issue(
                severity="error",
                check="readiness_prompt",
                message="empty teacher.readiness_prompt",
                day_id=day_id,
            )
        )

    non_empty_steps = [s for s in day.teacher_agent_behaviour if s.strip()]
    if len(non_empty_steps) < 3:
        issues.append(
            _issue(
                severity="error",
                check="teacher_steps",
                message=(
                    f"only {len(non_empty_steps)} non-empty teacher steps (need >=3)"
                ),
                day_id=day_id,
            )
        )
    if len(day.teacher_agent_behaviour) != len(non_empty_steps):
        issues.append(
            _issue(
                severity="error",
                check="scripted_plan",
                message="scripted plan length != non-empty teacher steps",
                day_id=day_id,
            )
        )

    if non_empty_steps:
        final_instruction = non_empty_steps[-1]
        lowered = final_instruction.lower()
        has_readiness_language = ("ready" in lowered and "practice" in lowered) or (
            final_instruction.strip() == readiness_prompt
        )
        if not has_readiness_language:
            issues.append(
                _issue(
                    severity="warning",
                    check="readiness_handoff",
                    message=(
                        "final teacher step lacks explicit readiness language "
                        "('ready' + 'practice') and does not match readiness_prompt"
                    ),
                    day_id=day_id,
                )
            )

    if day.final_review.get("scorecard_widget") != "final_scorecard":
        issues.append(
            _issue(
                severity="error",
                check="final_review",
                message="scorecard_widget must be final_scorecard",
                day_id=day_id,
            )
        )
    if day.final_review.get("rag_feedback_widget") != "rag_feedback":
        issues.append(
            _issue(
                severity="error",
                check="final_review",
                message="rag_feedback_widget must be rag_feedback",
                day_id=day_id,
            )
        )

    return issues


def lint_persona_round_trip(day: FileDayRecord) -> list[DayLintIssue]:
    """Verify chat persona loading matches the composed file day."""
    issues: list[DayLintIssue] = []
    day_id = day.day_id

    topic, skill_name, sub_level, instr = LearningSessionService._persona_from_file(
        None,  # type: ignore[arg-type]
        day_id,
    )

    if topic != day.topic:
        issues.append(
            _issue(
                severity="error",
                check="persona_topic",
                message=f"persona topic {topic!r} != file topic {day.topic!r}",
                day_id=day_id,
            )
        )
    if skill_name != day.theme_type:
        issues.append(
            _issue(
                severity="error",
                check="persona_skill",
                message=(
                    f"persona skill_name {skill_name!r} != theme_type {day.theme_type!r}"
                ),
                day_id=day_id,
            )
        )
    if sub_level != day.sub_level_min:
        issues.append(
            _issue(
                severity="error",
                check="persona_sub_level",
                message=(
                    f"persona sub_level {sub_level!r} != sub_level_min "
                    f"{day.sub_level_min!r}"
                ),
                day_id=day_id,
            )
        )
    if not isinstance(instr, dict):
        issues.append(
            _issue(
                severity="error",
                check="persona_instructions",
                message="teacher_instructions is not a dict",
                day_id=day_id,
            )
        )
        return issues

    scripted = instr.get(SCRIPTED_PLAN_KEY)
    if scripted != list(day.teacher_agent_behaviour):
        issues.append(
            _issue(
                severity="error",
                check="persona_scripted_plan",
                message="__scripted_plan does not match teacher_agent_behaviour",
                day_id=day_id,
            )
        )
    if instr.get("lesson_description") != day.explanation_brief:
        issues.append(
            _issue(
                severity="error",
                check="persona_lesson_description",
                message="lesson_description != explanation_brief",
                day_id=day_id,
            )
        )

    return issues


def lint_static_payloads(day: FileDayRecord) -> list[DayLintIssue]:
    """Project authored static payloads through the contract validation gate."""
    issues: list[DayLintIssue] = []
    for sequence, archetype_id in enumerate(day.task_archetypes_used):
        spec = file_source.task_spec_for(day, sequence)
        payload = _static_payload_from_spec(spec)
        if payload is None:
            continue
        content = {
            "phase": "authored",
            "archetype_id": archetype_id,
            "topic": payload.get("topic") or "Authored topic",
            "instructions": payload.get("instructions") or "Complete the activity.",
            **payload,
        }
        try:
            projected = validate_and_project_task_content(
                archetype_id,
                content,
                activity_id=f"{day.day_id}-{sequence}",
                sequence=sequence + 1,
            )
        except ContractValidationError as exc:
            issues.append(
                _issue(
                    severity="error",
                    check="static_payload_projection",
                    message=str(exc.detail),
                    day_id=day.day_id,
                    archetype_id=archetype_id,
                    sequence=sequence + 1,
                )
            )
            continue
        if projected.get("archetype_id") != archetype_id:
            issues.append(
                _issue(
                    severity="error",
                    check="static_payload_projection",
                    message="projected archetype_id mismatch",
                    day_id=day.day_id,
                    archetype_id=archetype_id,
                    sequence=sequence + 1,
                )
            )
    return issues


def lint_day_by_id(day_id: str) -> list[DayLintIssue]:
    """Run all lint checks for a single calendar day id."""
    day = file_source.get_day_by_id(day_id)
    issues: list[DayLintIssue] = []
    issues.extend(lint_day_structure(day))
    issues.extend(lint_persona_round_trip(day))
    issues.extend(lint_static_payloads(day))
    return issues


def lint_track(*, track: str = "all") -> list[DayLintIssue]:
    """Lint every calendar day on the requested track."""
    issues: list[DayLintIssue] = []
    for day_id in iter_calendar_day_ids(track=track):
        issues.extend(lint_day_by_id(day_id))
    return issues
