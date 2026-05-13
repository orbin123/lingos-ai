"""End-to-end integration test: Planner → DB → Teacher → Task Delivery → Evaluator
across 5 representative days of the 24w course.

For each day we verify:
  1. Planner emits a day-appropriate plan (sub_skill, sub_level match the topic).
  2. The plan persists and reloads from DB (cache path).
  3. The Teacher's user prompt mentions the correct sub_skill context.
  4. task_delivery_node picks the correct template_id for activity 1.
  5. The UI widget matches TEMPLATE_TO_WIDGET[output_model_name].
  6. evaluation_focus.level_note is appropriate for the sub_level (length sanity
     + presence of explicit level tag).
"""

from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401
from app.ai.agents import planner as planner_module
from app.ai.agents import teacher as teacher_module
from app.ai.agents.planner import (
    EvaluationFocus,
    PlannerLLMOutput,
    TeacherInstructions,
    generate_daily_plan,
)
from app.ai.agents.teacher import TeachingOutput, generate_teaching_turn
from app.ai.graphs import nodes as nodes_module
from app.ai.graphs.nodes import plan_loader_node, task_delivery_node
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.curriculum.models import DailyPlan
from app.modules.curriculum.repository import DailyPlanRepository
from app.modules.curriculum.topics import CourseTopic, get_course_topic
from app.tasks.schemas.full_tasks_templates import (
    TEMPLATE_TO_WIDGET,
    get_full_template_by_id,
)


DAYS = [
    {"week": 1, "day": 1, "sub_skill": "grammar", "sub_level": 1,
     "expected_template": "full_grammar_read_v1"},
    {"week": 1, "day": 2, "sub_skill": "vocabulary", "sub_level": 1,
     "expected_template": "full_vocabulary_read_v1"},
    {"week": 4, "day": 3, "sub_skill": "pronunciation", "sub_level": 3,
     "expected_template": "full_pronunciation_read_v1"},
    {"week": 8, "day": 5, "sub_skill": "expression", "sub_level": 5,
     "expected_template": "full_expression_read_v1"},
    {"week": 12, "day": 7, "sub_skill": "tone", "sub_level": 6,
     "expected_template": "full_tone_read_v1"},
]


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine, tables=[User.__table__, DailyPlan.__table__],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _user(db) -> User:
    u = User(email=f"learner@example.com", password_hash="x", name="Learner")
    db.add(u)
    db.flush()
    return u


def _planner_llm_output_for(sub_skill: str, sub_level: int) -> PlannerLLMOutput:
    """Build a believable PlannerLLMOutput shaped to the day."""
    return PlannerLLMOutput(
        teacher_instructions=TeacherInstructions(
            sub_skill_context=(
                f"This is a {sub_skill} session at sub-level {sub_level}. "
                "Tailor depth accordingly."
            ),
            learning_goal=f"Help the learner make progress on this {sub_skill} topic.",
            words_to_cover=None,
            teaching_approach=(
                f"Use {sub_skill}-appropriate examples. Keep sentences short for "
                f"sub-level {sub_level}."
            ),
            concept_check_focus=f"Ask a small {sub_skill} check question.",
            do_not_reveal="Do not reveal the MCQ options or task answers.",
        ),
        evaluation_focuses=[
            EvaluationFocus(
                focus_areas=[f"{sub_skill} core areas"],
                level_note=f"Sub-level {sub_level} guidance.",
                scoring_instruction=f"Score on {sub_skill} accuracy at sub-level {sub_level}.",
            )
            for _ in range(4)
        ],
    )


@pytest.mark.parametrize("case", DAYS, ids=lambda c: f"W{c['week']}D{c['day']}-{c['sub_skill']}")
def test_e2e_planner_flow_for_day(case, db_session, monkeypatch) -> None:
    week = case["week"]
    day = case["day"]
    expected_template_id = case["expected_template"]
    expected_widget = TEMPLATE_TO_WIDGET[
        get_full_template_by_id(expected_template_id).output_model_name
    ].value

    # ── (1) Planner LLM stub: returns shape-correct output for THIS sub_skill.
    class StubLLM:
        async def generate_structured(self, *, system_prompt, user_prompt,
                                      output_model, temperature=None):
            assert output_model is PlannerLLMOutput
            return _planner_llm_output_for(case["sub_skill"], case["sub_level"])

    monkeypatch.setattr(planner_module, "get_default_llm_client", lambda: StubLLM())

    # ── Topic must exist for this (week, day) in the real topics_24w.json.
    topic_entry = get_course_topic(duration_weeks=24, week=week, day=day)
    assert topic_entry is not None, f"No topic for W{week}D{day}"
    assert topic_entry.sub_skill == case["sub_skill"]
    assert topic_entry.sub_level == case["sub_level"]

    # ── (2) Stub plan_loader_node enrollment + topic so it can persist.
    user = _user(db_session)
    monkeypatch.setattr(
        nodes_module, "UserEnrollmentRepository",
        type(
            "FakeRepo", (),
            {
                "__init__": lambda self, db: None,
                "get_by_id": lambda self, eid: type(
                    "E", (), {
                        "id": 1, "user_id": user.id,
                        "current_week": week, "current_day_in_week": day,
                        "course": type("C", (), {
                            "slug": "beginner-24w", "duration_weeks": 24,
                        })(),
                    }
                )(),
            },
        ),
    )

    # Pipe the real Planner generation through plan_loader_node.
    monkeypatch.setattr(nodes_module, "generate_daily_plan", generate_daily_plan)

    state: dict = {
        "user_id": user.id, "enrollment_id": 1, "learner_profile": {},
    }
    update_1 = asyncio.run(plan_loader_node(state, db=db_session))
    plan = update_1["daily_plan"]

    # (1) Planner output checks
    assert plan["sub_skill"] == case["sub_skill"]
    assert plan["sub_level"] == case["sub_level"]
    assert case["sub_skill"] in plan["teacher_instructions"]["sub_skill_context"]
    assert len(plan["activities"]) == 4

    # (2) DB persistence: a second call must NOT regenerate (no LLM call).
    class ExplodingLLM:
        async def generate_structured(self, **kwargs):
            raise AssertionError("Planner should not be called on cache hit")
    monkeypatch.setattr(planner_module, "get_default_llm_client", lambda: ExplodingLLM())
    update_2 = asyncio.run(plan_loader_node(state, db=db_session))
    assert update_2["daily_plan"]["topic_id"] == plan["topic_id"]
    assert DailyPlanRepository(db_session).get_for_day(
        user_id=user.id, course_slug="beginner-24w", week=week, day=day,
    ) is not None

    # ── (3) Teacher: prompt must reference the correct sub_skill context.
    captured_prompts: list[str] = []

    class TeachStubLLM:
        async def generate_structured(self, *, system_prompt, user_prompt,
                                      output_model, temperature=None):
            captured_prompts.append(user_prompt)
            return TeachingOutput(messages=[f"Welcome to {case['sub_skill']}."])

    monkeypatch.setattr(teacher_module, "get_default_llm_client", lambda: TeachStubLLM())
    asyncio.run(generate_teaching_turn(
        topic=plan["topic_name"], sub_skill=case["sub_skill"],
        task_type="mcq", user_level=case["sub_level"],
        learner_profile={}, conversation=[],
        teacher_instructions=plan["teacher_instructions"],
    ))
    assert any(case["sub_skill"] in p for p in captured_prompts)
    assert any("Planner guidance for this lesson" in p for p in captured_prompts)

    # ── (4) + (5) task_delivery picks correct template + widget for activity 1.
    generator_calls: list[str] = []

    class StubGenerator:
        def __init__(self):
            pass

        async def generate(self, template, profile):
            generator_calls.append(template.template_id)
            return {
                "widget": TEMPLATE_TO_WIDGET[template.output_model_name].value,
                "task_intro": "intro",
                "estimated_time_minutes": 3,
            }

    monkeypatch.setattr(nodes_module, "TaskGeneratorAgent", StubGenerator)

    td_state: dict = {
        "daily_plan": plan, "current_activity_order": 1,
        "task_content": None, "task_queue": [{"sequence_index": 0}],
        "current_task_index": 0, "learner_profile": {}, "messages": [],
    }
    td_update = asyncio.run(task_delivery_node(td_state))

    assert generator_calls == [expected_template_id]
    ui = next(e for e in td_update["outgoing_events"] if e["type"] == "ui_event")
    assert ui["widget"] == expected_widget

    # ── (6) evaluation_focus sanity for activity 1.
    focus_1 = plan["activities"][0]["evaluation_focus"]
    assert focus_1["focus_areas"]
    assert str(case["sub_level"]) in focus_1["level_note"]
    assert focus_1["scoring_instruction"]
