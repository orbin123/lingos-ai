"""``SessionService.force_regenerate_attempt``: unconditional fresh generation.

Backs the chat "retry" affordance for a failed task generation. Unlike
``prepare_attempt_for_delivery`` — which only regenerates when the lenient
validity gate fails — this must ALWAYS re-run the task agent, so a broken cached
payload (e.g. the WRITE_PARAPHRASE empty-``items`` failure) that happens to pass
the lenient gate is still replaced with a genuinely fresh task.
"""

from __future__ import annotations

import pytest

from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.feedback_generator import StubFeedbackGenerator
from app.modules.sessions.service import SessionService
from app.modules.sessions.task_generator import GeneratedTask
from app.modules.sessions.widget_mapping import normalize_widget_key
from app.scoring import CourseLength

from tests.integration.sessions._lifecycle_support import _user_id


class _SpyGenerator:
    """Counts generate() calls and returns renderable, tagged content."""

    def __init__(self) -> None:
        self.calls = 0

    async def generate(
        self,
        *,
        archetype,
        day_topic,
        explanation_brief,
        cefr_level,
        sub_level,
        user_interests=None,
        task_spec=None,
    ):
        self.calls += 1
        return GeneratedTask(
            content={
                "phase": "regen",
                "archetype_id": archetype.archetype_id,
                "archetype_name": archetype.name,
                "ui_widget": archetype.ui_widget,
                "widget": normalize_widget_key(archetype.ui_widget),
                "core_activity": archetype.core_activity,
                "topic": (task_spec or {}).get("topic_override") or day_topic,
                "explanation_brief": explanation_brief,
                "instructions": "Fresh regenerated task.",
                "cefr_level": cefr_level,
                "sub_level": sub_level,
                "regenerated": True,
            }
        )


@pytest.mark.asyncio
async def test_force_regenerate_reruns_agent_and_replaces_cached_content(
    db_session,
):
    gen = _SpyGenerator()
    service = SessionService(
        db_session,
        evaluator=StubEvaluator(),
        feedback_generator=StubFeedbackGenerator(),
        task_generator=gen,
    )
    session = await service.start_session(
        user_id=_user_id(db_session),
        day_id="day_24_09_03",
        course_length=CourseLength.WEEKS_24,
        tasks_per_day=4,
        allowed_activities={"read", "write", "listen", "speak"},
    )

    attempt = session.attempts[0]
    # Simulate broken cached content with NO __pending_taskgen recipe: a naive
    # re-delivery would just re-read this and fail validation again.
    attempt.task_content = {
        "phase": "broken",
        "archetype_id": attempt.archetype_id,
        "items": [],
    }
    db_session.commit()

    before = gen.calls
    regenerated = await service.force_regenerate_attempt(attempt)

    # The task agent ran again — cache was bypassed unconditionally.
    assert gen.calls == before + 1
    content = regenerated.task_content
    assert content.get("regenerated") is True
    assert content.get("phase") != "broken"
    # The placeholder recipe is gone; real content is persisted.
    assert "__pending_taskgen" not in content
