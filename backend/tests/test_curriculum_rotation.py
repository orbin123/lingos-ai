from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

import app.modules.tasks.service as task_service_module
from app.modules.curriculum.constants import WEEK_SCHEDULE
from app.modules.curriculum.rotation import RotationEngine
from app.modules.tasks.models import Task, TaskType
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
        TaskType.LISTENING,
    ]
    assert week_4.activity_type == TaskType.SPEAKING


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


def test_grammar_activity_cycle_uses_all_four_enabled_activities() -> None:
    enrollment = SimpleNamespace(
        allow_reading=True,
        allow_writing=True,
        allow_listening=True,
        allow_speaking=True,
    )

    cycle = TaskService._activity_cycle_for_enrollment(
        enrollment=enrollment,
        skill_name="grammar",
        fallback_activity=TaskType.READING,
    )

    assert cycle == [Activity.READ, Activity.WRITE, Activity.LISTEN, Activity.SPEAK]


@pytest.mark.asyncio
async def test_grammar_day_generation_creates_four_curriculum_tasks_with_tts(
    monkeypatch,
) -> None:
    class FakeDb:
        def __init__(self) -> None:
            self.added: list[object] = []
            self._next_id = 100

        def add(self, obj: object) -> None:
            self.added.append(obj)

        def flush(self) -> None:
            for obj in self.added:
                if getattr(obj, "id", None) is None:
                    setattr(obj, "id", self._next_id)
                    self._next_id += 1

    class FakeGenerator:
        async def generate(self, template, user_profile):  # noqa: ANN001, ANN202
            activity = template.activity.value
            base = {
                "task_intro": "Intro",
                "estimated_time_minutes": template.estimated_time_minutes,
                "topic_id": "1:1",
                "topic_name": "Present Simple Tense",
                "sub_skill": "grammar",
                "sub_level": 3,
                "activity": activity,
                "instructions": "Do the task.",
            }
            if activity == "read":
                return {
                    **base,
                    "widget": "fill_in_blanks",
                    "passage": "She ___ every day.",
                    "items": [],
                    "grammar_rule_explained": "Use present simple.",
                }
            if activity == "write":
                return {
                    **base,
                    "widget": "open_text",
                    "items": [],
                    "grammar_rule_explained": "Use present simple.",
                    "common_mistakes": ["Missing -s"],
                }
            if activity == "listen":
                return {
                    **base,
                    "widget": "listen_and_respond",
                    "audio_script": "Maya walks to class and studies every day.",
                    "audio_url": None,
                    "inner_widget": "mcq",
                    "items": [],
                }
            return {
                **base,
                "widget": "speak_and_record",
                "speaking_prompts": ["Tell me about your routine."],
                "sample_responses": ["I study every morning."],
                "grammar_rule_to_practice": "present simple",
                "speaking_duration_seconds": 60,
            }

    class FakeTTS:
        async def synthesize(self, **kwargs):  # noqa: ANN003, ANN202
            assert kwargs["text"] == "Maya walks to class and studies every day."
            return {
                "audio_url": "/audio/listen.mp3",
                "duration_seconds": 4.2,
                "cache_hit": False,
            }

    class FakeUserTaskRepo:
        def assign(self, *, user_id, task_id, enrollment_id):  # noqa: ANN001, ANN202
            return SimpleNamespace(
                id=task_id + 1000,
                user_id=user_id,
                task_id=task_id,
                enrollment_id=enrollment_id,
            )

    monkeypatch.setattr(
        task_service_module,
        "get_default_tts_service",
        lambda: FakeTTS(),
    )

    service = TaskService.__new__(TaskService)
    service.db = FakeDb()
    service.generator = FakeGenerator()
    service.user_task_repo = FakeUserTaskRepo()

    plan = SimpleNamespace(
        skill_name="grammar",
        activity_type=TaskType.READING,
        skill_id=1,
        week_number=1,
        day_in_week=1,
    )
    enrollment = SimpleNamespace(
        id=7,
        allow_reading=True,
        allow_writing=True,
        allow_listening=True,
        allow_speaking=True,
        course=SimpleNamespace(duration_weeks=24),
    )
    profile = {"sub_level": 3, "course_topic": "Present Simple Tense"}

    for sequence_index in range(4):
        await service._try_generate_task_async(
            user_id=42,
            plan=plan,
            enrollment=enrollment,
            user_profile=profile,
            skill_name_to_id={"grammar": 1},
            sequence_index=sequence_index,
        )

    tasks = [obj for obj in service.db.added if isinstance(obj, Task)]
    assert [task.task_type.value for task in tasks] == [
        "curriculum_grammar_fill_blanks",
        "curriculum_grammar_open_text",
        "curriculum_grammar_listen_mcq",
        "curriculum_grammar_speak",
    ]
    listen_task = tasks[2]
    assert listen_task.content["audio_url"] == "/audio/listen.mp3"
    assert listen_task.content["audio_duration_seconds"] == 4.2
