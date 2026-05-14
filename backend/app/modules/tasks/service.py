"""Business logic for assigning the next task to a user.

Orchestrates: enrollment → rotation engine → task pool → assignment +
history update.  When an LLM-generated template is available the service
tries TaskGeneratorAgent first, falling back to the seeded pool on failure.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.agents.task_generator import TaskGeneratorAgent
from app.ai.tts import get_default_tts_service
from app.modules.curriculum.constants import SKILL_ACTIVITIES
from app.modules.curriculum.exceptions import (
    EnrollmentNotActive,
    NoTaskAvailable,
    NotEnrolled,
)
from app.modules.curriculum.models import EnrollmentStatus, UserEnrollment
from app.modules.curriculum.repository import (
    EnrollmentSkillHistoryRepository,
    UserEnrollmentRepository,
)
from app.modules.curriculum.rotation import RotationEngine
from app.modules.curriculum.topics import CourseTopic, get_course_topic
from app.modules.skills.repository import SkillRepository, UserSkillScoreRepository
from app.modules.tasks.models import (
    Task,
    TaskStatus,
    TaskType,
    UserTask,
    UserTaskStatus,
)
from app.modules.tasks.repository import TaskRepository, UserTaskRepository
from app.tasks.schemas import get_templates_for
from app.tasks.schemas.base import Activity
from app.tasks.schemas.full_tasks_templates import get_full_template

logger = logging.getLogger(__name__)

# Map DB TaskType → schema Activity so we can look up templates
_TASK_TYPE_TO_ACTIVITY = {
    "reading": Activity.READ,
    "writing": Activity.WRITE,
    "listening": Activity.LISTEN,
    "speaking": Activity.SPEAK,
}

# Reverse: schema Activity → DB TaskType (used when seeded-pool fallback needs sequence-based activity)
_ACTIVITY_TO_TASK_TYPE: dict[Activity, TaskType] = {
    Activity.READ: TaskType.READING,
    Activity.WRITE: TaskType.WRITING,
    Activity.LISTEN: TaskType.LISTENING,
    Activity.SPEAK: TaskType.SPEAKING,
}

# Fixed order used to cycle activities within a single day's task bundle.
# sequence_index 0→READ, 1→WRITE, 2→LISTEN, 3→SPEAK, then wraps.
_DAY_ACTIVITY_CYCLE = [Activity.READ, Activity.WRITE, Activity.LISTEN, Activity.SPEAK]

_SUBSKILL_LABELS: dict[str, str] = {
    "grammar": "Grammar",
    "vocabulary": "Vocabulary",
    "pronunciation": "Pronunciation",
    "fluency": "Fluency",
    "thought_organization": "Thought Organization",
    "listening": "Listening",
    "tone": "Tone",
}

_ACTIVITY_LABELS: dict[str, str] = {
    "read": "Read",
    "write": "Write",
    "listen": "Listen",
    "speak": "Speak",
}

_WIDGET_LABELS: dict[str, str] = {
    "mcq": "MCQ",
    "fill_in_blanks": "Fill in Blanks",
    "open_text": "Open Text",
    "timed_text": "Timed Text",
    "structured_essay": "Structured Essay",
    "speak_and_record": "Speak & Record",
    "listen_and_respond": "Listen & Respond",
    "storyboard": "Storyboard",
}


def _make_task_title(content: dict) -> str:
    """Build a consistent display title from task content fields."""
    sub = content.get("sub_skill", "")
    act = content.get("activity", "")
    wid = content.get("widget", "")
    sub_label = _SUBSKILL_LABELS.get(str(sub), str(sub).replace("_", " ").title())
    act_label = _ACTIVITY_LABELS.get(str(act), str(act).title())
    wid_label = _WIDGET_LABELS.get(str(wid), str(wid).replace("_", " ").title())
    if sub_label and act_label and wid_label:
        return f"{sub_label} - {act_label} - {wid_label}"
    return sub_label or "Task"


class DayNotComplete(Exception):
    """Raised when mark_day_complete is called but not all tasks are done."""
    pass


class TaskService:
    """Orchestrates day-bundle creation and day-completion logic."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.enrollment_repo = UserEnrollmentRepository(db)
        self.history_repo = EnrollmentSkillHistoryRepository(db)
        self.skill_repo = SkillRepository(db)
        self.score_repo = UserSkillScoreRepository(db)
        self.task_repo = TaskRepository(db)
        self.user_task_repo = UserTaskRepository(db)
        self.engine = RotationEngine()
        self.generator = TaskGeneratorAgent()

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _load_enrollment(self, user_id: int) -> UserEnrollment:
        """Load and validate the user's active enrollment."""
        enrollment = self.enrollment_repo.get_for_user(user_id)
        if enrollment is None:
            raise NotEnrolled(f"User {user_id} is not enrolled in any course")
        if enrollment.status != EnrollmentStatus.ACTIVE:
            raise EnrollmentNotActive(
                f"Enrollment {enrollment.id} status is {enrollment.status.value}"
            )
        return enrollment

    def _build_user_profile(
        self,
        user_id: int,
        *,
        enrollment: UserEnrollment | None = None,
        plan: "RotationEngine.Plan | None" = None,  # noqa: F821
        week: int | None = None,
        day: int | None = None,
    ) -> dict:
        """Assemble the user_profile dict the TaskGeneratorAgent needs.

        Includes sub_level, course topic, profile personalisation fields,
        and a small content guidance string. Broad weak skill areas are kept
        for older templates but should not drive grammar concept selection.
        """
        scores = self.score_repo.get_for_user(user_id)
        from app.modules.auth.repository import UserProfileRepository

        profile = UserProfileRepository(self.db).get_by_user_id(user_id)
        personalisation_context = (
            profile.personalisation_context.strip()
            if profile and profile.personalisation_context
            else ""
        )
        interests = profile.interests.strip() if profile and profile.interests else ""
        primary_goals = (
            profile.primary_goals.strip() if profile and profile.primary_goals else ""
        )
        self_assessed_level = (
            profile.self_assessed_level.value
            if profile and profile.self_assessed_level
            else "beginner"
        )
        course_topic = self._course_topic_for(
            enrollment=enrollment,
            plan=plan,
            week=week,
            day=day,
        )
        topic_name = course_topic.topic_name if course_topic else (
            plan.skill_name if plan else "today's English topic"
        )
        topic_sub_level = course_topic.sub_level if course_topic else None
        content_guidance = self._content_guidance(
            interests=interests,
            primary_goals=primary_goals,
            course_topic=topic_name,
        )
        if not scores:
            # No diagnosis yet — return safe defaults
            return {
                "sub_level": topic_sub_level or 3,
                "weak_areas": "general grammar, basic vocabulary",
                "topic": topic_name,
                "course_topic": topic_name,
                "topic_id": course_topic.topic_id if course_topic else "",
                "interests": interests,
                "primary_goals": primary_goals,
                "self_assessed_level": self_assessed_level,
                "personalisation_context": personalisation_context,
                "content_guidance": content_guidance,
            }

        # Sort ascending so weakest come first
        sorted_scores = sorted(scores, key=lambda s: float(s.score))
        weakest = sorted_scores[:3]  # bottom 3 skills
        avg_score = sum(float(s.score) for s in scores) / len(scores)

        # Map 0–10 score → 1–10 sub-level
        sub_level = max(1, min(10, round(avg_score)))

        weak_area_names = []
        for s in weakest:
            if s.skill and s.skill.name:
                weak_area_names.append(s.skill.name)
        weak_areas = ", ".join(weak_area_names) if weak_area_names else "general grammar"

        return {
            "sub_level": topic_sub_level or sub_level,
            "weak_areas": weak_areas,
            "topic": topic_name,
            "course_topic": topic_name,
            "topic_id": course_topic.topic_id if course_topic else "",
            "interests": interests,
            "primary_goals": primary_goals,
            "self_assessed_level": self_assessed_level,
            "personalisation_context": personalisation_context,
            "content_guidance": content_guidance,
        }

    @staticmethod
    def _course_topic_for(
        *,
        enrollment: UserEnrollment | None,
        plan: "RotationEngine.Plan | None" = None,  # noqa: F821
        week: int | None = None,
        day: int | None = None,
    ) -> CourseTopic | None:
        if enrollment is None or enrollment.course is None:
            return None
        topic = get_course_topic(
            duration_weeks=enrollment.course.duration_weeks,
            week=week or enrollment.current_week,
            day=day or enrollment.current_day_in_week,
        )
        if topic is None or plan is None:
            return topic
        return topic if topic.sub_skill == plan.skill_name else topic

    @staticmethod
    def _content_guidance(
        *,
        interests: str,
        primary_goals: str,
        course_topic: str,
    ) -> str:
        parts = [
            f"Keep the grammar concept anchored on '{course_topic}'.",
        ]
        if interests:
            parts.append(
                f"Use one learner interest as the surface context when natural: {interests}."
            )
        if primary_goals:
            parts.append(f"Prefer situations that support this goal: {primary_goals}.")
        parts.append(
            "Avoid generic office content unless the learner profile clearly points there."
        )
        return " ".join(parts)

    @staticmethod
    def _enabled_activity_types(enrollment: UserEnrollment) -> set[TaskType]:
        """Return the learner's enabled core activity types."""
        enabled: set[TaskType] = set()
        if enrollment.allow_reading:
            enabled.add(TaskType.READING)
        if enrollment.allow_writing:
            enabled.add(TaskType.WRITING)
        if enrollment.allow_listening:
            enabled.add(TaskType.LISTENING)
        if enrollment.allow_speaking:
            enabled.add(TaskType.SPEAKING)
        return enabled

    @staticmethod
    def _tasks_per_day(enrollment: UserEnrollment) -> int:
        return max(2, min(4, int(enrollment.tasks_per_day or 2)))

    @staticmethod
    def _activity_cycle_for_enrollment(
        *,
        enrollment: UserEnrollment,
        skill_name: str,
        fallback_activity: TaskType,
    ) -> list[Activity]:
        """Return today's enabled activity sequence in canonical UI order."""
        enabled = TaskService._enabled_activity_types(enrollment)
        configured = set(SKILL_ACTIVITIES.get(skill_name, []))
        if not configured:
            configured = {
                TaskType.READING,
                TaskType.WRITING,
                TaskType.LISTENING,
                TaskType.SPEAKING,
            }

        allowed_schema_activities = {
            _TASK_TYPE_TO_ACTIVITY[task_type.value]
            for task_type in enabled.intersection(configured)
            if task_type.value in _TASK_TYPE_TO_ACTIVITY
        }
        cycle = [
            activity
            for activity in _DAY_ACTIVITY_CYCLE
            if activity in allowed_schema_activities
        ]
        if cycle:
            return cycle

        fallback = _TASK_TYPE_TO_ACTIVITY.get(fallback_activity.value)
        return [fallback] if fallback is not None else []

    @staticmethod
    async def _postprocess_generated_content(content: dict) -> dict:
        """Attach generated assets required by widget contracts."""
        if content.get("widget") != "listen_and_respond":
            return content

        audio_url_key = "audio_url"

        script = content.get("audio_script")
        if not isinstance(script, str) or not script.strip():
            script = content.get("source_audio_script")
            audio_url_key = "source_audio_url"

        if not isinstance(script, str) or not script.strip():
            script = content.get("text_to_shadow")

        if not isinstance(script, str) or not script.strip():
            logger.warning(
                "[postprocess] listen_and_respond task has no audio script; "
                "audio_url will be null"
            )
            return {
                **content,
                audio_url_key: None,
                "audio_duration_seconds": None,
            }

        try:
            result = await get_default_tts_service().synthesize(
                text=script,
                style_instructions=(
                    "Speak clearly and naturally for an English learner. "
                    "Use a warm conversational tutor voice."
                ),
            )
        except Exception as exc:
            logger.warning(
                "[postprocess] TTS synthesis failed: %s — audio_url will be null",
                exc,
            )
            return {
                **content,
                audio_url_key: None,
                "audio_duration_seconds": None,
            }

        return {
            **content,
            audio_url_key: result["audio_url"],
            "audio_duration_seconds": result["duration_seconds"],
        }

    def _try_generate_task(
        self,
        *,
        user_id: int,
        plan: "RotationEngine.Plan",  # noqa: F821
        enrollment: UserEnrollment,
        user_profile: dict,
        skill_name_to_id: dict[str, int],
        sequence_index: int = 0,
    ) -> UserTask | None:
        """Attempt to generate a task via the LLM.

        Returns a UserTask if generation succeeds, None on any failure
        (so the caller can fall back to the seeded pool).
        """
        from app.tasks.schemas.base import SubSkill

        # Map the plan's skill name to a SubSkill enum
        # The schema SubSkill uses the DB skill name directly for grammar/vocabulary/tone;
        # for others we need a mapping.
        _SKILL_NAME_TO_SUBSKILL = {
            "grammar": SubSkill.GRAMMAR,
            "vocabulary": SubSkill.VOCABULARY,
            "pronunciation": SubSkill.PRONUNCIATION,
            "fluency": SubSkill.FLUENCY,
            "expression": SubSkill.THOUGHT_ORGANIZATION,
            "comprehension": SubSkill.LISTENING,
            "tone": SubSkill.TONE,
        }

        sub_skill = _SKILL_NAME_TO_SUBSKILL.get(plan.skill_name)
        if sub_skill is None:
            logger.warning("No SubSkill mapping for %r, skipping LLM gen", plan.skill_name)
            return None

        activity_cycle = self._activity_cycle_for_enrollment(
            enrollment=enrollment,
            skill_name=plan.skill_name,
            fallback_activity=plan.activity_type,
        )
        if not activity_cycle:
            logger.warning("No enabled activity cycle for %r, skipping LLM gen", plan.skill_name)
            return None
        schema_activity = activity_cycle[sequence_index % len(activity_cycle)]

        # Look up the single curriculum-driven template for this (sub_skill, activity) pair
        try:
            template = get_full_template(sub_skill, schema_activity)
        except KeyError:
            logger.warning(
                "No full curriculum template for sub_skill=%s activity=%s, skipping LLM gen",
                sub_skill.value, schema_activity.value,
            )
            return None

        # Enrich user_profile with curriculum-specific vars the new templates need
        sub_level = user_profile.get("sub_level", 5)
        user_profile = {
            **user_profile,
            "topic_name": user_profile.get("course_topic") or user_profile.get("topic") or "today's English topic",
            "week": plan.week_number,
            "day": plan.day_in_week,
            "sub_skill": sub_skill.value,
            "plan_type": f"{enrollment.course.duration_weeks}w" if enrollment.course else "24w",
            "domain": "general",
        }

        logger.info(
            "Attempting LLM generation: skill=%s activity=%s template=%s user_profile=%s",
            plan.skill_name, plan.activity_type.value,
            template.template_id, user_profile,
        )

        try:
            # FastAPI routes are synchronous (the router uses sync def).
            # asyncio.get_event_loop() inside a sync thread returns a loop
            # that is NOT running, so asyncio.run() is safe here.
            # We explicitly create a fresh loop to avoid any stale-loop
            # issues across requests.
            loop = asyncio.new_event_loop()
            try:
                content = loop.run_until_complete(
                    self.generator.generate(template, user_profile)
                )
                content = loop.run_until_complete(
                    self._postprocess_generated_content(content)
                )
            finally:
                loop.close()
        except Exception as exc:
            logger.warning(
                "[task_gen] ⚠️  LLM call FAILED for template=%s: %s — will fall back to seeded pool",
                template.template_id, exc,
            )
            return None

        # Map the template's task_type string (e.g. "fill_in_blanks") to the
        # TaskType enum so the frontend's isGeneratedTaskType() check works.
        from app.modules.tasks.models import TaskType as TT
        try:
            generated_task_type = TT(template.task_type)
        except ValueError:
            logger.warning(
                "template.task_type=%r has no matching TaskType enum value; "
                "falling back to activity type",
                template.task_type,
            )
            generated_task_type = plan.activity_type

        # Create a new Task row with the generated content
        task = Task(
            title=_make_task_title(content),
            task_type=generated_task_type,
            difficulty=sub_level,
            status=TaskStatus.ACTIVE,
            content=content,
        )
        self.db.add(task)
        self.db.flush()  # get task.id

        # Wire up the TaskSkill junction
        from app.modules.tasks.models import TaskSkill
        ts = TaskSkill(
            task_id=task.id,
            skill_id=plan.skill_id,
            weight=1.0,
        )
        self.db.add(ts)
        self.db.flush()

        # Assign to user
        assignment = self.user_task_repo.assign(
            user_id=user_id,
            task_id=task.id,
            enrollment_id=enrollment.id,
        )

        logger.info(
            "[task_gen] ✅ LLM task generated successfully: "
            "task_id=%s template=%s task_type=%s for user=%s",
            task.id, template.template_id, generated_task_type.value, user_id,
        )
        return assignment

    async def _try_generate_task_async(
        self,
        *,
        user_id: int,
        plan: "RotationEngine.Plan",  # noqa: F821
        enrollment: UserEnrollment,
        user_profile: dict,
        skill_name_to_id: dict[str, int],
        sequence_index: int = 0,
    ) -> UserTask | None:
        """Async version of _try_generate_task for chat session creation."""
        from app.tasks.schemas.base import SubSkill

        _SKILL_NAME_TO_SUBSKILL = {
            "grammar": SubSkill.GRAMMAR,
            "vocabulary": SubSkill.VOCABULARY,
            "pronunciation": SubSkill.PRONUNCIATION,
            "fluency": SubSkill.FLUENCY,
            "expression": SubSkill.THOUGHT_ORGANIZATION,
            "comprehension": SubSkill.LISTENING,
            "tone": SubSkill.TONE,
        }

        sub_skill = _SKILL_NAME_TO_SUBSKILL.get(plan.skill_name)
        if sub_skill is None:
            logger.warning("No SubSkill mapping for %r, skipping LLM gen", plan.skill_name)
            return None

        activity_cycle = self._activity_cycle_for_enrollment(
            enrollment=enrollment,
            skill_name=plan.skill_name,
            fallback_activity=plan.activity_type,
        )
        if not activity_cycle:
            logger.warning("No enabled activity cycle for %r, skipping LLM gen", plan.skill_name)
            return None
        schema_activity = activity_cycle[sequence_index % len(activity_cycle)]

        try:
            template = get_full_template(sub_skill, schema_activity)
        except KeyError:
            logger.warning(
                "No full curriculum template for sub_skill=%s activity=%s, skipping LLM gen",
                sub_skill.value, schema_activity.value,
            )
            return None

        sub_level = user_profile.get("sub_level", 5)
        user_profile = {
            **user_profile,
            "topic_name": user_profile.get("course_topic") or user_profile.get("topic") or "today's English topic",
            "week": plan.week_number,
            "day": plan.day_in_week,
            "sub_skill": sub_skill.value,
            "plan_type": f"{enrollment.course.duration_weeks}w" if enrollment.course else "24w",
            "domain": "general",
        }

        logger.info(
            "Attempting async LLM generation: skill=%s activity=%s template=%s",
            plan.skill_name, plan.activity_type.value, template.template_id,
        )

        try:
            content = await self.generator.generate(template, user_profile)
            content = await self._postprocess_generated_content(content)
        except Exception as exc:
            logger.warning(
                "[task_gen] async LLM call failed for template=%s: %s — will fall back to seeded pool",
                template.template_id, exc,
            )
            return None

        from app.modules.tasks.models import TaskType as TT
        try:
            generated_task_type = TT(template.task_type)
        except ValueError:
            logger.warning(
                "template.task_type=%r has no matching TaskType enum value; falling back to activity type",
                template.task_type,
            )
            generated_task_type = plan.activity_type

        task = Task(
            title=_make_task_title(content),
            task_type=generated_task_type,
            difficulty=sub_level,
            status=TaskStatus.ACTIVE,
            content=content,
        )
        self.db.add(task)
        self.db.flush()

        from app.modules.tasks.models import TaskSkill
        self.db.add(TaskSkill(task_id=task.id, skill_id=plan.skill_id, weight=1.0))
        self.db.flush()

        assignment = self.user_task_repo.assign(
            user_id=user_id,
            task_id=task.id,
            enrollment_id=enrollment.id,
        )
        logger.info(
            "[task_gen] async LLM task generated successfully: task_id=%s template=%s task_type=%s for user=%s",
            task.id, template.template_id, generated_task_type.value, user_id,
        )
        return assignment

    @staticmethod
    def _select_template_for_plan(
        *,
        templates: list,
        plan: "RotationEngine.Plan",  # noqa: F821
        sub_level: int,
        sequence_index: int = 0,
    ):
        """Choose the concrete activity format for this weekly plan.

        The rotation engine chooses the core activity (read/write/speak/listen).
        This helper rotates through the available template formats for that
        core activity on each repeat of that activity.
        """
        supported = [
            tpl
            for tpl in templates
            if tpl.difficulty_range[0] <= sub_level <= tpl.difficulty_range[1]
        ]
        candidates = supported or templates
        activity_cycle_length = max(plan.activity_cycle_length, 1)
        occurrence_index = (max(plan.week_number, 1) - 1) // activity_cycle_length
        template_index = occurrence_index + max(sequence_index, 0)
        return candidates[template_index % len(candidates)]

    @staticmethod
    def _template_order_for_plan(
        *,
        plan: "RotationEngine.Plan",  # noqa: F821
        sub_level: int,
    ) -> list[str]:
        """Return generated task_type order for an already-decided plan."""
        from app.tasks.schemas.base import SubSkill

        skill_name_to_subskill = {
            "grammar": SubSkill.GRAMMAR,
            "vocabulary": SubSkill.VOCABULARY,
            "pronunciation": SubSkill.PRONUNCIATION,
            "fluency": SubSkill.FLUENCY,
            "expression": SubSkill.THOUGHT_ORGANIZATION,
            "comprehension": SubSkill.LISTENING,
            "tone": SubSkill.TONE,
        }
        sub_skill = skill_name_to_subskill.get(plan.skill_name)
        if sub_skill is None:
            return []

        ordered_task_types: list[str] = []
        for task_type in SKILL_ACTIVITIES.get(plan.skill_name, []):
            schema_activity = _TASK_TYPE_TO_ACTIVITY.get(task_type.value)
            if schema_activity is None:
                continue
            try:
                ordered_task_types.append(
                    get_full_template(sub_skill, schema_activity).task_type
                )
            except KeyError:
                continue

        schema_activity = _TASK_TYPE_TO_ACTIVITY.get(plan.activity_type.value)
        if schema_activity is None:
            return ordered_task_types

        templates = get_templates_for(sub_skill, schema_activity)
        if not templates:
            return ordered_task_types

        supported = [
            tpl
            for tpl in templates
            if tpl.difficulty_range[0] <= sub_level <= tpl.difficulty_range[1]
        ]
        candidates = supported or templates
        activity_cycle_length = max(plan.activity_cycle_length, 1)
        occurrence_index = (max(plan.week_number, 1) - 1) // activity_cycle_length
        rotated = candidates[occurrence_index:] + candidates[:occurrence_index]
        ordered_task_types.extend(tpl.task_type for tpl in rotated)
        return ordered_task_types

    @staticmethod
    def _sort_day_bundle_for_plan(
        *,
        bundle: list[UserTask],
        plan: "RotationEngine.Plan",  # noqa: F821
        sub_level: int,
    ) -> list[UserTask]:
        """Keep today's list stable and aligned with the selected plan."""
        template_order = TaskService._template_order_for_plan(
            plan=plan,
            sub_level=sub_level,
        )
        priority = {task_type: index for index, task_type in enumerate(template_order)}
        fallback_priority = len(priority)

        activity_priority = {
            activity.value: index for index, activity in enumerate(_DAY_ACTIVITY_CYCLE)
        }
        fallback_activity_priority = len(activity_priority)

        def sort_key(user_task: UserTask) -> tuple[int, int, datetime, int]:
            task_type = user_task.task.task_type.value
            content = getattr(user_task.task, "content", {}) or {}
            activity = (
                content.get("activity")
                if isinstance(content, dict)
                else None
            )
            return (
                activity_priority.get(str(activity), fallback_activity_priority),
                priority.get(task_type, fallback_priority),
                user_task.created_at,
                user_task.id,
            )

        return sorted(bundle, key=sort_key)

    def _create_one_task(
        self,
        *,
        user_id: int,
        enrollment: UserEnrollment,
        skill_name_to_id: dict[str, int],
        history_by_skill_id: dict[int, str | None],
        sequence_index: int = 0,
    ) -> UserTask:
        """Run the rotation engine once, try LLM generation first, then
        fall back to the seeded task pool. Does NOT commit."""
        plan = self.engine.decide(
            week_number=enrollment.current_week,
            day_in_week=enrollment.current_day_in_week,
            skill_name_to_id=skill_name_to_id,
            history_by_skill_id=history_by_skill_id,
            allowed_activity_types=self._enabled_activity_types(enrollment),
        )

        # --- Try LLM generation first ---
        user_profile = self._build_user_profile(
            user_id,
            enrollment=enrollment,
            plan=plan,
        )
        # Derive the sequence-based activity so the fallback honours the same
        # READ→WRITE→LISTEN→SPEAK cycle that LLM generation uses.
        activity_cycle = self._activity_cycle_for_enrollment(
            enrollment=enrollment,
            skill_name=plan.skill_name,
            fallback_activity=plan.activity_type,
        )
        effective_activity = (
            _ACTIVITY_TO_TASK_TYPE.get(activity_cycle[sequence_index % len(activity_cycle)], plan.activity_type)
            if activity_cycle
            else plan.activity_type
        )

        assignment = self._try_generate_task(
            user_id=user_id,
            plan=plan,
            enrollment=enrollment,
            user_profile=user_profile,
            skill_name_to_id=skill_name_to_id,
            sequence_index=sequence_index,
        )
        if assignment is not None:
            # Update rotation memory
            self.history_repo.upsert_after_assignment(
                enrollment_id=enrollment.id,
                skill_id=plan.skill_id,
                activity_type=effective_activity,
            )
            return assignment

        # --- Fallback: seeded task pool ---
        logger.warning(
            "[task_gen] ⚠️  LLM generation FAILED or no template matched — "
            "falling back to seeded pool for skill=%s activity=%s (sequence_index=%d). "
            "User will receive a hand-authored task, NOT an AI-generated one.",
            plan.skill_name, effective_activity.value, sequence_index,
        )
        task = self.task_repo.find_for_plan(
            skill_id=plan.skill_id,
            activity_type=effective_activity,
            target_difficulty=plan.target_difficulty,
            exclude_completed_by_user_id=None,
        )
        if task is None:
            raise NoTaskAvailable(
                f"No task in pool for skill={plan.skill_name}, "
                f"activity={effective_activity.value}, "
                f"difficulty~{plan.target_difficulty}"
            )

        assignment = self.user_task_repo.assign(
            user_id=user_id,
            task_id=task.id,
            enrollment_id=enrollment.id,
        )

        # Update rotation memory so the NEXT call picks a different activity
        self.history_repo.upsert_after_assignment(
            enrollment_id=enrollment.id,
            skill_id=plan.skill_id,
            activity_type=effective_activity,
        )

        return assignment

    def _daily_session_queue_bundle(
        self,
        *,
        enrollment: UserEnrollment,
    ) -> list[UserTask] | None:
        """Return the frozen daily chat queue if one already exists.

        This keeps a started daily session stable even if the learner changes
        tasks_per_day before advancing from the dashboard.
        """
        from app.modules.learning_session.models import LearningSession

        rows = (
            self.db.query(LearningSession)
            .filter(
                LearningSession.user_id == enrollment.user_id,
                LearningSession.enrollment_id == enrollment.id,
                LearningSession.created_at >= enrollment.current_day_started_at,
            )
            .order_by(LearningSession.id.desc())
            .all()
        )
        for row in rows:
            queue = sorted(
                (row.task_queue or []),
                key=lambda item: int(item.get("sequence_index") or 0),
            )
            if not queue:
                continue

            bundle: list[UserTask] = []
            for item in queue:
                user_task_id = item.get("user_task_id")
                if user_task_id is None:
                    bundle = []
                    break
                user_task = self.user_task_repo.get_by_id(int(user_task_id))
                if user_task is None or user_task.enrollment_id != enrollment.id:
                    bundle = []
                    break
                bundle.append(user_task)

            if bundle:
                return bundle

        return None

    async def _create_one_task_async(
        self,
        *,
        user_id: int,
        enrollment: UserEnrollment,
        skill_name_to_id: dict[str, int],
        history_by_skill_id: dict[int, str | None],
        sequence_index: int = 0,
    ) -> UserTask:
        """Async version of _create_one_task for learning-session startup."""
        plan = self.engine.decide(
            week_number=enrollment.current_week,
            day_in_week=enrollment.current_day_in_week,
            skill_name_to_id=skill_name_to_id,
            history_by_skill_id=history_by_skill_id,
            allowed_activity_types=self._enabled_activity_types(enrollment),
        )

        user_profile = self._build_user_profile(
            user_id,
            enrollment=enrollment,
            plan=plan,
        )
        activity_cycle = self._activity_cycle_for_enrollment(
            enrollment=enrollment,
            skill_name=plan.skill_name,
            fallback_activity=plan.activity_type,
        )
        effective_activity = (
            _ACTIVITY_TO_TASK_TYPE.get(activity_cycle[sequence_index % len(activity_cycle)], plan.activity_type)
            if activity_cycle
            else plan.activity_type
        )

        assignment = await self._try_generate_task_async(
            user_id=user_id,
            plan=plan,
            enrollment=enrollment,
            user_profile=user_profile,
            skill_name_to_id=skill_name_to_id,
            sequence_index=sequence_index,
        )
        if assignment is not None:
            self.history_repo.upsert_after_assignment(
                enrollment_id=enrollment.id,
                skill_id=plan.skill_id,
                activity_type=effective_activity,
            )
            return assignment

        logger.warning(
            "[task_gen] async LLM generation failed or no template matched — "
            "falling back to seeded pool for skill=%s activity=%s (sequence_index=%d)",
            plan.skill_name, effective_activity.value, sequence_index,
        )
        task = self.task_repo.find_for_plan(
            skill_id=plan.skill_id,
            activity_type=effective_activity,
            target_difficulty=plan.target_difficulty,
            exclude_completed_by_user_id=None,
        )
        if task is None:
            raise NoTaskAvailable(
                f"No task in pool for skill={plan.skill_name}, "
                f"activity={effective_activity.value}, "
                f"difficulty~{plan.target_difficulty}"
            )

        assignment = self.user_task_repo.assign(
            user_id=user_id,
            task_id=task.id,
            enrollment_id=enrollment.id,
        )
        self.history_repo.upsert_after_assignment(
            enrollment_id=enrollment.id,
            skill_id=plan.skill_id,
            activity_type=effective_activity,
        )
        return assignment

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def get_or_create_day_bundle(self, *, user_id: int) -> list[UserTask]:
        """Return the user's current day bundle, creating tasks if needed.

        Idempotent: if the current-day bundle already has
        enrollment.tasks_per_day tasks, returns them as-is. Otherwise creates
        more until the bundle is full.

        Each new task in the bundle uses the same daily sub-skill/activity
        plan. When multiple generated templates exist for that slot, they
        are assigned in template order.

        Raises:
            NotEnrolled: user has no enrollment.
            EnrollmentNotActive: enrollment status != ACTIVE.
            NoTaskAvailable: rotation engine produced a plan but task pool
                is empty for that (skill, activity) combo.
        """
        enrollment = self._load_enrollment(user_id)
        frozen_bundle = self._daily_session_queue_bundle(enrollment=enrollment)
        if frozen_bundle is not None:
            return frozen_bundle

        # Check how many tasks already exist for the current day. This includes
        # completed tasks so a partially completed dashboard bundle cannot grow
        # duplicates after a refetch.
        existing = self.user_task_repo.list_for_enrollment_day(
            enrollment_id=enrollment.id,
            day_started_at=enrollment.current_day_started_at,
        )

        # Build lookup maps once
        skill_name_to_id = self.skill_repo.name_to_id_map()
        history_rows = self.history_repo.list_for_enrollment(enrollment.id)
        history_by_skill_id = {
            h.skill_id: h.last_activity_type for h in history_rows
        }
        plan = self.engine.decide(
            week_number=enrollment.current_week,
            day_in_week=enrollment.current_day_in_week,
            skill_name_to_id=skill_name_to_id,
            history_by_skill_id=history_by_skill_id,
            allowed_activity_types=self._enabled_activity_types(enrollment),
        )
        user_profile = self._build_user_profile(
            user_id,
            enrollment=enrollment,
            plan=plan,
        )

        needed = self._tasks_per_day(enrollment) - len(existing)
        if needed <= 0:
            return self._sort_day_bundle_for_plan(
                bundle=existing,
                plan=plan,
                sub_level=user_profile.get("sub_level", 5),
            )

        new_tasks: list[UserTask] = []
        for offset in range(needed):
            assignment = self._create_one_task(
                user_id=user_id,
                enrollment=enrollment,
                skill_name_to_id=skill_name_to_id,
                history_by_skill_id=history_by_skill_id,
                sequence_index=len(existing) + offset,
            )
            new_tasks.append(assignment)

            # Update the in-memory history map so the next iteration picks
            # a different activity (the DB row was already updated via
            # upsert_after_assignment, but the local dict needs refreshing).
            refreshed_rows = self.history_repo.list_for_enrollment(enrollment.id)
            history_by_skill_id = {
                h.skill_id: h.last_activity_type for h in refreshed_rows
            }

        # Commit everything
        self.db.commit()

        # Refresh all objects so they're serializable
        bundle = existing + new_tasks
        for ut in bundle:
            self.db.refresh(ut)
            self.db.refresh(ut.task)

        return self._sort_day_bundle_for_plan(
            bundle=bundle,
            plan=plan,
            sub_level=user_profile.get("sub_level", 5),
        )

    async def get_or_create_day_bundle_async(self, *, user_id: int) -> list[UserTask]:
        """Async day-bundle creation used by chat session startup."""
        enrollment = self._load_enrollment(user_id)
        frozen_bundle = self._daily_session_queue_bundle(enrollment=enrollment)
        if frozen_bundle is not None:
            return frozen_bundle

        existing = self.user_task_repo.list_for_enrollment_day(
            enrollment_id=enrollment.id,
            day_started_at=enrollment.current_day_started_at,
        )

        skill_name_to_id = self.skill_repo.name_to_id_map()
        history_rows = self.history_repo.list_for_enrollment(enrollment.id)
        history_by_skill_id = {
            h.skill_id: h.last_activity_type for h in history_rows
        }
        plan = self.engine.decide(
            week_number=enrollment.current_week,
            day_in_week=enrollment.current_day_in_week,
            skill_name_to_id=skill_name_to_id,
            history_by_skill_id=history_by_skill_id,
            allowed_activity_types=self._enabled_activity_types(enrollment),
        )
        user_profile = self._build_user_profile(
            user_id,
            enrollment=enrollment,
            plan=plan,
        )

        needed = self._tasks_per_day(enrollment) - len(existing)
        if needed <= 0:
            return self._sort_day_bundle_for_plan(
                bundle=existing,
                plan=plan,
                sub_level=user_profile.get("sub_level", 5),
            )

        new_tasks: list[UserTask] = []
        for offset in range(needed):
            assignment = await self._create_one_task_async(
                user_id=user_id,
                enrollment=enrollment,
                skill_name_to_id=skill_name_to_id,
                history_by_skill_id=history_by_skill_id,
                sequence_index=len(existing) + offset,
            )
            new_tasks.append(assignment)

            refreshed_rows = self.history_repo.list_for_enrollment(enrollment.id)
            history_by_skill_id = {
                h.skill_id: h.last_activity_type for h in refreshed_rows
            }

        self.db.commit()

        bundle = existing + new_tasks
        for ut in bundle:
            self.db.refresh(ut)
            self.db.refresh(ut.task)

        return self._sort_day_bundle_for_plan(
            bundle=bundle,
            plan=plan,
            sub_level=user_profile.get("sub_level", 5),
        )

    def superuser_jump_by_type(
        self,
        *,
        user_id: int,
        task_type: str,
    ) -> list[UserTask]:
        """Dev-only: generate a task for a SPECIFIC task_type string.

        Bypasses the rotation engine entirely. Finds the first template
        whose task_type matches the requested string, then calls the
        LLM to generate content. Falls back to the seeded pool if LLM
        fails, same as the normal path.

        Used by the SuperUser dev panel when the tester picks a specific
        task type (e.g. 'error_spotting') regardless of the curriculum day.
        """
        from app.tasks.schemas import ALL_TEMPLATES
        from app.modules.tasks.models import TaskType as TT

        enrollment = self._load_enrollment(user_id)
        try:
            user_profile = self._build_user_profile(user_id, enrollment=enrollment)
        except TypeError:
            # Some focused tests monkeypatch the old one-argument helper.
            user_profile = self._build_user_profile(user_id)

        # Find the first template that matches the requested task_type
        template = next(
            (t for t in ALL_TEMPLATES if t.task_type == task_type), None
        )
        if template is None:
            raise NoTaskAvailable(
                f"No template found for task_type={task_type!r}. "
                f"Check that it is defined in a *_templates.py file."
            )

        # Find the skill_id for this template's sub_skill
        skill_name_to_id = self.skill_repo.name_to_id_map()
        skill_id = skill_name_to_id.get(template.sub_skill.value)
        if skill_id is None:
            raise NoTaskAvailable(
                f"Skill '{template.sub_skill.value}' not found in DB skills table."
            )

        logger.info(
            "[superuser_jump_by_type] task_type=%r template=%s skill=%s",
            task_type, template.template_id, template.sub_skill.value,
        )

        # Curriculum-driven templates need extra vars not present in the normal profile
        if task_type.startswith("curriculum_"):
            user_profile = {
                **user_profile,
                "topic_name": user_profile.get("course_topic") or user_profile.get("topic") or "today's English topic",
                "week": enrollment.current_week,
                "day": enrollment.current_day_in_week,
                "sub_skill": template.sub_skill.value,
                "plan_type": f"{enrollment.course.duration_weeks}w" if enrollment.course else "24w",
                "domain": "general",
            }

        # Attempt LLM generation
        try:
            loop = asyncio.new_event_loop()
            try:
                content = loop.run_until_complete(
                    self.generator.generate(template, user_profile)
                )
            finally:
                loop.close()
        except Exception as exc:
            logger.warning(
                "[superuser_jump_by_type] ⚠️  LLM FAILED for template=%s: %s "
                "— falling back to seeded pool",
                template.template_id, exc,
            )
            content = None

        if content is not None:
            try:
                generated_task_type = TT(task_type)
            except ValueError:
                generated_task_type = TT.READING  # safe fallback, shouldn't happen

            task = Task(
                title=_make_task_title(content),
                task_type=generated_task_type,
                difficulty=user_profile.get("sub_level", 5),
                status=TaskStatus.ACTIVE,
                content=content,
            )
            self.db.add(task)
            self.db.flush()

            from app.modules.tasks.models import TaskSkill
            self.db.add(TaskSkill(task_id=task.id, skill_id=skill_id, weight=1.0))
            self.db.flush()

            assignment = self.user_task_repo.assign(
                user_id=user_id,
                task_id=task.id,
                enrollment_id=None,
            )
            logger.info(
                "[superuser_jump_by_type] ✅ Generated task_id=%s for user=%s",
                task.id, user_id,
            )
        else:
            # Seeded fallback — find any task with a matching task_type
            task = self.task_repo.find_by_task_type(
                task_type=task_type,
                target_difficulty=user_profile.get("sub_level", 5),
            )
            if task is None:
                raise NoTaskAvailable(
                    f"LLM failed and no seeded task exists for task_type={task_type!r}"
                )
            assignment = self.user_task_repo.assign(
                user_id=user_id,
                task_id=task.id,
                enrollment_id=None,
            )

        self.db.commit()
        self.db.refresh(assignment)
        self.db.refresh(assignment.task)
        return [assignment]

    def superuser_jump(
        self,
        *,
        user_id: int,
        week: int,
        day_in_week: int,
    ) -> list[UserTask]:
        """Create a fresh task bundle for an arbitrary (week, day).

        Used only by the superuser dev panel for UI testing.
        Bypasses the enrollment's current_week/current_day_in_week.
        Always creates new tasks — does NOT reuse existing ones.
        Does NOT advance or modify the user's enrollment state.
        The assignment is ad hoc (enrollment_id=NULL), so old dev-panel
        tasks cannot block the real enrolled day bundle.
        Does NOT update rotation history.
        Commits and returns the created UserTask objects.
        """
        enrollment = self._load_enrollment(user_id)

        skill_name_to_id = self.skill_repo.name_to_id_map()

        # Start from the first allowed activity every time so the jump
        # is deterministic for UI testing regardless of prior usage.
        history_by_skill_id: dict[int, None] = {}

        plan = self.engine.decide(
            week_number=week,
            day_in_week=day_in_week,
            skill_name_to_id=skill_name_to_id,
            history_by_skill_id=history_by_skill_id,
            allowed_activity_types=self._enabled_activity_types(enrollment),
        )
        user_profile = self._build_user_profile(
            user_id,
            enrollment=enrollment,
            plan=plan,
            week=week,
            day=day_in_week,
        )

        assignment = self._try_generate_task(
            user_id=user_id,
            plan=plan,
            enrollment=enrollment,
            user_profile=user_profile,
            skill_name_to_id=skill_name_to_id,
        )
        if assignment is not None:
            assignment.enrollment_id = None

        if assignment is None:
            task = self.task_repo.find_for_plan(
                skill_id=plan.skill_id,
                activity_type=plan.activity_type,
                target_difficulty=plan.target_difficulty,
                exclude_completed_by_user_id=None,
            )
            if task is None:
                raise NoTaskAvailable(
                    f"No task in pool for skill={plan.skill_name}, "
                    f"activity={plan.activity_type.value}"
                )
            assignment = self.user_task_repo.assign(
                user_id=user_id,
                task_id=task.id,
                enrollment_id=None,
            )

        self.db.commit()
        self.db.refresh(assignment)
        self.db.refresh(assignment.task)
        return [assignment]

    def mark_day_complete(self, *, user_id: int) -> UserEnrollment:
        """Advance the enrollment day if ALL tasks in the bundle are done.

        Checks that every UserTask for the current enrollment day has
        status == COMPLETED. If any are still open, raises DayNotComplete.

        Day/week rollover logic:
          - current_day_in_week increments 1 → 7
          - when day goes past 7, resets to 1 and current_week increments

        Returns the updated enrollment (for the response).

        Raises:
            NotEnrolled / EnrollmentNotActive: standard guards.
            DayNotComplete: at least one task is still pending/in_progress.
        """
        enrollment = self._load_enrollment(user_id)

        today_tasks = self._daily_session_queue_bundle(enrollment=enrollment)
        if today_tasks is None:
            today_tasks = self.user_task_repo.list_for_enrollment_day(
                enrollment_id=enrollment.id,
                day_started_at=enrollment.current_day_started_at,
            )
        if not today_tasks:
            if enrollment.last_completed_on == datetime.now(timezone.utc).date():
                return enrollment
            raise DayNotComplete(
                "No tasks have been assigned for the current day"
            )
        incomplete = [
            task for task in today_tasks if task.status != UserTaskStatus.COMPLETED
        ]
        if incomplete:
            raise DayNotComplete(
                f"{len(incomplete)} task(s) still pending for the current day"
            )

        # Advance day
        enrollment.last_completed_on = datetime.now(timezone.utc).date()
        enrollment = self.enrollment_repo.advance_day(enrollment)

        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def reset_for_retry(self, *, user_id: int, user_task_id: int) -> UserTask:
        """Reset a completed UserTask so the user can attempt it again.

        Deletes the existing UserResponse row (cascades to Evaluation and
        Feedback) so the next completion fully overwrites the previous score
        in recent activities and sub-skill bars.

        Raises:
            LookupError: task not found.
            PermissionError: task belongs to a different user.
            ValueError: task is not in COMPLETED status.
        """
        from app.modules.responses.repository import ResponseRepository

        user_task = self.user_task_repo.get_by_id(user_task_id)
        if user_task is None:
            raise LookupError(f"UserTask {user_task_id} does not exist")
        if user_task.user_id != user_id:
            raise PermissionError(
                f"UserTask {user_task_id} belongs to a different user"
            )
        if user_task.status != UserTaskStatus.COMPLETED:
            raise ValueError(
                f"UserTask {user_task_id} is {user_task.status.value} — only completed tasks can be retried"
            )

        # Delete old response (cascades to Evaluation, Feedback).
        existing = ResponseRepository(self.db).get_by_user_task_id(user_task_id)
        if existing is not None:
            self.db.delete(existing)
            self.db.flush()

        # Reset task status.
        user_task.status = UserTaskStatus.PENDING
        user_task.completed_at = None

        self.db.commit()
        self.db.refresh(user_task)
        return user_task
