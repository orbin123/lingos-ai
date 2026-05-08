from datetime import datetime, timezone
from types import SimpleNamespace

from app.modules.curriculum.constants import WEEK_SCHEDULE
from app.modules.curriculum.rotation import RotationEngine
from app.modules.tasks.models import TaskType
from app.modules.tasks.service import TaskService
from app.tasks.schemas import get_templates_for
from app.tasks.schemas.base import Activity, SubSkill


SKILL_IDS = {
    "grammar": 1,
    "vocabulary": 2,
    "pronunciation": 3,
    "fluency": 4,
    "expression": 5,
    "comprehension": 6,
    "tone": 7,
}


def test_week_schedule_uses_all_seven_sub_skills_in_order() -> None:
    assert WEEK_SCHEDULE == {
        1: "grammar",
        2: "vocabulary",
        3: "pronunciation",
        4: "fluency",
        5: "expression",
        6: "comprehension",
        7: "tone",
    }


def test_activity_rotates_by_week_not_assignment_history() -> None:
    engine = RotationEngine()
    history = {SKILL_IDS["grammar"]: TaskType.SPEAKING}

    week_1 = engine.decide(
        week_number=1,
        day_in_week=1,
        skill_name_to_id=SKILL_IDS,
        history_by_skill_id=history,
    )
    week_2 = engine.decide(
        week_number=2,
        day_in_week=1,
        skill_name_to_id=SKILL_IDS,
        history_by_skill_id=history,
    )
    week_3 = engine.decide(
        week_number=3,
        day_in_week=1,
        skill_name_to_id=SKILL_IDS,
        history_by_skill_id=history,
    )
    week_4 = engine.decide(
        week_number=4,
        day_in_week=1,
        skill_name_to_id=SKILL_IDS,
        history_by_skill_id=history,
    )

    assert [week_1.activity_type, week_2.activity_type, week_3.activity_type] == [
        TaskType.READING,
        TaskType.WRITING,
        TaskType.SPEAKING,
    ]
    assert week_4.activity_type == TaskType.READING


def test_activity_rotation_respects_enabled_activity_filter() -> None:
    engine = RotationEngine()
    allowed = {TaskType.WRITING, TaskType.SPEAKING}

    week_1 = engine.decide(
        week_number=1,
        day_in_week=1,
        skill_name_to_id=SKILL_IDS,
        history_by_skill_id={},
        allowed_activity_types=allowed,
    )
    week_2 = engine.decide(
        week_number=2,
        day_in_week=1,
        skill_name_to_id=SKILL_IDS,
        history_by_skill_id={},
        allowed_activity_types=allowed,
    )
    week_3 = engine.decide(
        week_number=3,
        day_in_week=1,
        skill_name_to_id=SKILL_IDS,
        history_by_skill_id={},
        allowed_activity_types=allowed,
    )

    assert [week_1.activity_type, week_2.activity_type, week_3.activity_type] == [
        TaskType.WRITING,
        TaskType.SPEAKING,
        TaskType.WRITING,
    ]


def test_rotation_does_not_skip_scheduled_sub_skill_when_settings_do_not_match() -> None:
    engine = RotationEngine()

    try:
        engine.decide(
            week_number=1,
            day_in_week=3,
            skill_name_to_id=SKILL_IDS,
            history_by_skill_id={},
            allowed_activity_types={TaskType.READING, TaskType.WRITING},
        )
    except ValueError as exc:
        assert "pronunciation" in str(exc)
    else:
        raise AssertionError("Expected pronunciation day to stay fixed and fail")


def test_template_format_rotates_on_repeated_core_activity() -> None:
    engine = RotationEngine()
    week_1_plan = engine.decide(
        week_number=1,
        day_in_week=1,
        skill_name_to_id=SKILL_IDS,
        history_by_skill_id={},
    )
    week_4_plan = engine.decide(
        week_number=4,
        day_in_week=1,
        skill_name_to_id=SKILL_IDS,
        history_by_skill_id={},
    )
    templates = get_templates_for(SubSkill.GRAMMAR, Activity.READ)

    week_1_template = TaskService._select_template_for_plan(
        templates=templates,
        plan=week_1_plan,
        sub_level=5,
    )
    week_4_template = TaskService._select_template_for_plan(
        templates=templates,
        plan=week_4_plan,
        sub_level=5,
    )

    assert week_1_template.template_id == "grammar_read_fill_blanks_v1"
    assert week_4_template.template_id == "grammar_read_error_spotting_v1"


def test_template_format_advances_for_multiple_tasks_in_same_day() -> None:
    engine = RotationEngine()
    plan = engine.decide(
        week_number=1,
        day_in_week=1,
        skill_name_to_id=SKILL_IDS,
        history_by_skill_id={},
    )
    templates = get_templates_for(SubSkill.GRAMMAR, Activity.READ)

    first = TaskService._select_template_for_plan(
        templates=templates,
        plan=plan,
        sub_level=5,
        sequence_index=0,
    )
    second = TaskService._select_template_for_plan(
        templates=templates,
        plan=plan,
        sub_level=5,
        sequence_index=1,
    )

    assert first.template_id == "grammar_read_fill_blanks_v1"
    assert second.template_id == "grammar_read_error_spotting_v1"


def test_existing_day_bundle_is_sorted_by_plan_template_order() -> None:
    engine = RotationEngine()
    plan = engine.decide(
        week_number=1,
        day_in_week=1,
        skill_name_to_id=SKILL_IDS,
        history_by_skill_id={},
    )
    now = datetime.now(timezone.utc)
    speak = SimpleNamespace(
        id=1,
        created_at=now,
        task=SimpleNamespace(task_type=SimpleNamespace(value="speak_with_tense")),
    )
    fill = SimpleNamespace(
        id=2,
        created_at=now,
        task=SimpleNamespace(task_type=SimpleNamespace(value="fill_in_blanks")),
    )

    sorted_bundle = TaskService._sort_day_bundle_for_plan(
        bundle=[speak, fill],
        plan=plan,
        sub_level=5,
    )

    assert [task.task.task_type.value for task in sorted_bundle] == [
        "fill_in_blanks",
        "speak_with_tense",
    ]
