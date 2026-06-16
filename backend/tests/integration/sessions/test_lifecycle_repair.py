"""Self-healing repair for stale listening/speaking attempt payloads.

Split out of the former monolithic ``test_session_lifecycle.py``.
"""

from __future__ import annotations

import pytest

from app.modules.curriculum.models import (
    CurriculumDay,
    CurriculumWeek,
    ThemeType,
)
from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.feedback_generator import StubFeedbackGenerator
from app.modules.sessions.service import SessionService
from app.modules.sessions.task_generator import GeneratedTask
from app.modules.sessions.widget_mapping import normalize_widget_key
from app.scoring import ARCHETYPE_REGISTRY, CourseLength

from tests.integration.sessions._lifecycle_support import _user_id


class TestAttemptDeliveryRepair:
    """Older code paths could persist listening attempts with no
    `audio_script` / `items` / `inner_widget`, which renders as the
    "Audio could not be prepared" dead-end in the widget. The repair
    method must rebuild a renderable payload before the route returns.
    """

    class CapturingTaskGenerator:
        def __init__(self) -> None:
            self.calls = []

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
            self.calls.append({
                "archetype_id": archetype.archetype_id,
                "task_spec": dict(task_spec or {}),
            })
            content = {
                "phase": "test",
                "archetype_id": archetype.archetype_id,
                "archetype_name": archetype.name,
                "ui_widget": archetype.ui_widget,
                "widget": normalize_widget_key(archetype.ui_widget),
                "core_activity": archetype.core_activity,
                "topic": (task_spec or {}).get("topic_override") or day_topic,
                "explanation_brief": explanation_brief,
                "instructions": (task_spec or {}).get("instructions_override")
                or "Complete the activity.",
                "cefr_level": cefr_level,
                "sub_level": sub_level,
            }
            if archetype.archetype_id == "SPEAK_TIMED":
                content.update({
                    "task_intro": "Record your routine sentences.",
                    "speaking_duration_seconds": 45,
                    "speaking_prompts": [
                        "Say one routine sentence with I and a frequency adverb.",
                        "Say one routine sentence with he and a frequency adverb.",
                        "Say one routine sentence with she and a frequency adverb.",
                    ],
                    "sample_responses": [
                        "I usually drink water in the morning.",
                        "He often walks to school.",
                        "She always eats breakfast at seven.",
                    ],
                })
            elif archetype.core_activity == "listen":
                content.update({
                    "audio_script": "Maria wakes up at seven every morning.",
                    "audio_duration_seconds": 8,
                    "inner_widget": (
                        "fill_in_blanks"
                        if archetype.archetype_id == "LISTEN_CLOZE"
                        else "open_text"
                        if archetype.archetype_id == "LISTEN_DICTATION"
                        else "mcq"
                    ),
                    "items": (
                        [
                            {
                                "item_id": "d1",
                                "prompt": "Type sentence 1.",
                                "correct_answer": "Maria wakes up at seven every morning.",
                                "explanation": "Listen for the full sentence.",
                            }
                        ]
                        if archetype.archetype_id == "LISTEN_DICTATION"
                        else [
                            {
                                "item_id": "q1",
                                "prompt": "What time does Maria wake up?",
                                "options": ["Six", "Seven", "Eight"],
                                "correct_index": 1,
                                "explanation": "She wakes at seven.",
                            }
                        ]
                    ),
                })
            return GeneratedTask(content=content)

    @pytest.mark.asyncio
    async def test_listening_attempt_with_empty_audio_is_repaired(
        self, db_session,
    ):
        service = SessionService(
            db_session,
            evaluator=StubEvaluator(),
            feedback_generator=StubFeedbackGenerator(),
        )
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )

        listening = next(
            a for a in session.attempts
            if ARCHETYPE_REGISTRY[a.archetype_id].core_activity == "listen"
        )
        # Simulate a stale row written by an older code path.
        listening.task_content = {
            "phase": "stub",
            "archetype_id": listening.archetype_id,
            "topic": "Listening for daily routines",
            "instructions": "Use short A1 routine sentences.",
            "cefr_level": "A2",
            "sub_level": 3,
        }
        db_session.commit()

        repaired = await service.prepare_attempt_for_delivery(listening)
        content = repaired.task_content
        expected_inner = {
            "LISTEN_CLOZE": "fill_in_blanks",
            "LISTEN_DICTATION": "open_text",
        }.get(listening.archetype_id, "mcq")
        assert content["inner_widget"] == expected_inner
        assert isinstance(content.get("items"), list)
        assert len(content["items"]) >= 1
        assert str(content.get("audio_script") or "").strip() != ""

    @pytest.mark.asyncio
    async def test_valid_attempt_content_is_returned_unchanged(self, db_session):
        service = SessionService(
            db_session,
            evaluator=StubEvaluator(),
            feedback_generator=StubFeedbackGenerator(),
        )
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        listening = next(
            a for a in session.attempts
            if ARCHETYPE_REGISTRY[a.archetype_id].core_activity == "listen"
        )
        original = dict(listening.task_content)
        repaired = await service.prepare_attempt_for_delivery(listening)
        assert repaired.task_content == original

    @pytest.mark.asyncio
    async def test_speaking_attempt_without_prompt_is_repaired_from_source_spec(
        self, db_session,
    ):
        week = CurriculumWeek(
            week_id="wk_24_01",
            course_length="24w",
            week_number=1,
            theme_type=ThemeType.GRAMMAR,
            title="Simple Present",
            cefr_level="A1",
            sub_level_min=1,
            sub_level_max=2,
            learning_goal="Simple present routines.",
        )
        db_session.add(week)
        db_session.flush()
        db_session.add(
            CurriculumDay(
                day_id="day_24_01_01",
                week_id=week.id,
                day_number=1,
                topic="Old DB topic",
                explanation_brief="Old DB brief.",
                default_activities=["read", "write", "listen", "speak"],
                mandatory_activities=["read"],
                suggested_archetypes={"speak": ["SPEAK_TIMED"]},
            )
        )
        db_session.commit()

        task_generator = self.CapturingTaskGenerator()
        service = SessionService(
            db_session,
            evaluator=StubEvaluator(),
            feedback_generator=StubFeedbackGenerator(),
            task_generator=task_generator,
        )
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_01_01",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        speaking = next(a for a in session.attempts if a.archetype_id == "SPEAK_TIMED")
        speaking.task_content = {
            "phase": "stale",
            "archetype_id": "SPEAK_TIMED",
            "ui_widget": "SpeakAndRecord",
            "widget": "speak_and_record",
            "core_activity": "speak",
            "topic": "Old DB topic",
            "instructions": "Prompt the learner to speak.",
            "task_intro": "Record your response",
            "cefr_level": "A1",
            "sub_level": 1,
        }
        db_session.commit()

        repaired = await service.prepare_attempt_for_delivery(speaking)
        content = repaired.task_content
        assert content["widget"] == "speak_and_record"
        assert len(content["speaking_prompts"]) == 3
        assert all(prompt.strip() for prompt in content["speaking_prompts"])

        repair_call = task_generator.calls[-1]
        assert repair_call["archetype_id"] == "SPEAK_TIMED"
        assert repair_call["task_spec"]["topic_override"] == "Say simple present routines"
        assert "3 speaking prompts" in repair_call["task_spec"]["widget_requirements"]
