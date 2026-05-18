"""Business logic for the challenges API."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Protocol

from pydantic import ValidationError

from app.ai.agents.ielts_challenge_evaluator import IELTSChallengeWritingEvaluator
from app.ai.agents.ielts_challenge_feedback import IELTSChallengeFeedbackAgent
from app.ai.agents.ielts_challenge_generator import IELTSChallengeGenerator
from app.ai.llm import LLMError
from app.modules.challenges.evaluation_schemas import (
    IELTSFeedbackReport,
    ReadingEvaluationReport,
    ReadingQuestionEvaluation,
    SectionFeedback,
    SectionScores,
    StubSectionEvaluation,
    UnifiedEvaluationReport,
    WritingCriteriaEvaluation,
    WritingCriterionEvaluation,
    WritingEvaluationReport,
    WritingIssue,
    WritingPromptEvaluation,
)
from app.modules.challenges.generator_schemas import GeneratedIELTSTaskPayload
from app.modules.challenges.models import (
    Challenge,
    ChallengeAttempt,
    ChallengeAttemptStatus,
    ChallengeLevel,
)
from app.modules.challenges.repository import (
    ChallengeAttemptRepository,
    ChallengeRepository,
)
from app.modules.challenges.schemas import (
    ChallengeDetailRead,
    ChallengeHistoryAttempt,
    ChallengeHistoryRead,
    ChallengeLevelRead,
    ChallengeListItem,
)


logger = logging.getLogger(__name__)

DAILY_ATTEMPT_LIMIT = 10
PHASE_4_PLACEHOLDER_BAND = 6.5


class ChallengeTaskGenerator(Protocol):
    async def generate(self, *, context: dict[str, Any]) -> dict:
        """Generate a challenge task payload from prompt context."""
        ...


class ChallengeWritingEvaluator(Protocol):
    async def evaluate(self, *, context: dict[str, Any]) -> WritingEvaluationReport:
        """Evaluate writing responses from prompt context."""
        ...


class ChallengeFeedbackGenerator(Protocol):
    async def generate(self, *, context: dict[str, Any]) -> IELTSFeedbackReport:
        """Generate learner feedback from evaluation context."""
        ...


class ChallengeNotFound(Exception):
    """Raised when an active challenge cannot be found."""


class ChallengeAttemptNotFound(Exception):
    """Raised when an attempt cannot be found for the current user."""


class ChallengeLevelNotFound(Exception):
    """Raised when a challenge level cannot be found."""


class ChallengeLevelLocked(Exception):
    """Raised when a learner tries to start a locked level."""


class ChallengeDailyAttemptLimitExceeded(Exception):
    """Raised when a learner exceeds the rolling challenge attempt cap."""


class ChallengeReadService:
    """Orchestration for challenge catalog, attempts and learner progress."""

    def __init__(
        self,
        db,
        *,
        generator: ChallengeTaskGenerator | None = None,
        writing_evaluator: ChallengeWritingEvaluator | None = None,
        feedback_generator: ChallengeFeedbackGenerator | None = None,
    ) -> None:
        self.db = db
        self.challenge_repo = ChallengeRepository(db)
        self.attempt_repo = ChallengeAttemptRepository(db)
        self._generator = generator
        self._writing_evaluator = writing_evaluator
        self._feedback_generator = feedback_generator

    def list_challenges(self) -> list[ChallengeListItem]:
        challenges = self.challenge_repo.list_active()
        return [
            ChallengeListItem(
                id=challenge.id,
                slug=challenge.slug,
                name=challenge.name,
                short_description=challenge.short_description,
                icon=challenge.icon,
                level_count=len(challenge.levels),
            )
            for challenge in challenges
        ]

    def get_detail(self, *, slug: str, user_id: int) -> ChallengeDetailRead:
        challenge = self.challenge_repo.get_active_by_slug(slug)
        if challenge is None:
            raise ChallengeNotFound(f"challenge {slug!r} not found")
        return self._detail_for(challenge=challenge, user_id=user_id)

    def get_history(self, *, slug: str, user_id: int) -> ChallengeHistoryRead:
        challenge = self.challenge_repo.get_active_by_slug(slug)
        if challenge is None:
            raise ChallengeNotFound(f"challenge {slug!r} not found")

        attempts = self.attempt_repo.list_for_challenge(
            user_id=user_id,
            challenge_id=challenge.id,
        )
        best_attempt_ids = self._best_attempt_ids(attempts)
        return ChallengeHistoryRead(
            challenge_slug=challenge.slug,
            challenge_name=challenge.name,
            attempts=[
                ChallengeHistoryAttempt(
                    id=attempt.id,
                    challenge_level_id=attempt.challenge_level_id,
                    level_number=attempt.level.level_number,
                    level_name=attempt.level.name,
                    status=attempt.status,
                    started_at=attempt.started_at,
                    completed_at=attempt.completed_at,
                    expires_at=attempt.expires_at,
                    overall_score=(
                        float(attempt.overall_score)
                        if attempt.overall_score is not None
                        else None
                    ),
                    section_scores=attempt.section_scores,
                    passed=attempt.passed,
                    is_best_for_level=attempt.id in best_attempt_ids,
                    created_at=attempt.created_at,
                )
                for attempt in attempts
            ],
        )

    def get_attempt(self, *, attempt_id: int, user_id: int) -> ChallengeAttempt:
        attempt = self.attempt_repo.get_for_user(attempt_id=attempt_id, user_id=user_id)
        if attempt is None:
            raise ChallengeAttemptNotFound(f"attempt {attempt_id!r} not found")
        return attempt

    async def start_attempt(
        self,
        *,
        slug: str,
        level_number: int,
        user_id: int,
    ) -> ChallengeAttempt:
        challenge = self.challenge_repo.get_active_by_slug(slug)
        if challenge is None:
            raise ChallengeNotFound(f"challenge {slug!r} not found")

        level = self._level_by_number(challenge=challenge, level_number=level_number)
        if level is None:
            raise ChallengeLevelNotFound(
                f"level {level_number!r} not found for challenge {slug!r}"
            )
        if not self._level_is_unlocked(challenge=challenge, level=level, user_id=user_id):
            raise ChallengeLevelLocked(
                f"level {level_number!r} is locked for challenge {slug!r}"
            )

        now = datetime.now(timezone.utc)
        self._check_daily_attempt_limit(user_id=user_id, now=now)
        task_payload = await self._generated_or_starter_task_payload(
            challenge=challenge,
            level=level,
            user_id=user_id,
        )
        attempt = self.attempt_repo.create(
            user_id=user_id,
            level_id=level.id,
            started_at=now,
            expires_at=now + timedelta(seconds=level.time_limit_seconds),
            task_payload=task_payload,
        )
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    async def submit_attempt(
        self,
        *,
        attempt_id: int,
        user_id: int,
        response_payload: dict,
    ) -> ChallengeAttempt:
        attempt = self.get_attempt(attempt_id=attempt_id, user_id=user_id)
        if attempt.status != ChallengeAttemptStatus.IN_PROGRESS:
            return attempt

        now = datetime.now(timezone.utc)
        expired = now > self._as_utc(attempt.expires_at) + timedelta(seconds=5)
        attempt.response_payload = response_payload
        attempt.completed_at = now
        attempt.status = (
            ChallengeAttemptStatus.TIMED_OUT
            if expired
            else ChallengeAttemptStatus.COMPLETED
        )

        evaluation_report = await self._evaluate_phase_4_attempt(
            attempt=attempt,
            response_payload=response_payload,
        )
        attempt.section_scores = evaluation_report.section_scores.model_dump()
        attempt.overall_score = evaluation_report.overall_score
        attempt.passed = evaluation_report.overall_score >= float(
            attempt.level.pass_threshold
        )
        attempt.evaluation_report = evaluation_report.model_dump()
        feedback_report = await self._feedback_phase_4_attempt(
            attempt=attempt,
            response_payload=response_payload,
            evaluation_report=evaluation_report,
        )
        attempt.feedback_report = feedback_report.model_dump()
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def _check_daily_attempt_limit(self, *, user_id: int, now: datetime) -> None:
        window_start = now - timedelta(hours=24)
        attempt_count = self.attempt_repo.count_started_since(
            user_id=user_id,
            since=window_start,
        )
        if attempt_count >= DAILY_ATTEMPT_LIMIT:
            raise ChallengeDailyAttemptLimitExceeded(
                f"daily challenge attempt limit of {DAILY_ATTEMPT_LIMIT} exceeded"
            )

    async def _evaluate_phase_4_attempt(
        self,
        *,
        attempt: ChallengeAttempt,
        response_payload: dict,
    ) -> UnifiedEvaluationReport:
        reading = grade_reading_section(
            task_payload=attempt.task_payload,
            response_payload=response_payload,
        )
        writing = await self._evaluate_writing_with_fallback(
            attempt=attempt,
            response_payload=response_payload,
        )
        listening = StubSectionEvaluation(
            mode="hardcoded_phase_4_placeholder",
            section_band=PHASE_4_PLACEHOLDER_BAND,
            summary=(
                "Listening is still a Phase 4 placeholder; real audio scoring "
                "arrives in Phase 5."
            ),
        )
        speaking = StubSectionEvaluation(
            mode="hardcoded_phase_4_placeholder",
            section_band=PHASE_4_PLACEHOLDER_BAND,
            summary=(
                "Speaking is still a Phase 4 placeholder; upload, transcription, "
                "and scoring arrive in Phase 6."
            ),
        )
        section_scores = SectionScores(
            listening=listening.section_band,
            reading=reading.section_band,
            writing=writing.section_band,
            speaking=speaking.section_band,
        )
        overall_score = round_to_half_band(
            (
                section_scores.listening
                + section_scores.reading
                + section_scores.writing
                + section_scores.speaking
            )
            / 4
        )
        return UnifiedEvaluationReport(
            mode="phase_4_text_sections",
            reading=reading,
            writing=writing,
            listening=listening,
            speaking=speaking,
            section_scores=section_scores,
            overall_score=overall_score,
        )

    async def _evaluate_writing_with_fallback(
        self,
        *,
        attempt: ChallengeAttempt,
        response_payload: dict,
    ) -> WritingEvaluationReport:
        if not _has_any_writing_response(response_payload):
            return self._fallback_writing_evaluation(
                attempt=attempt,
                response_payload=response_payload,
                reason="No writing response was submitted.",
            )

        evaluator = self._writing_evaluator or IELTSChallengeWritingEvaluator()
        context = self._writing_evaluation_context(
            attempt=attempt,
            response_payload=response_payload,
        )
        for attempt_number in (1, 2):
            try:
                report = await evaluator.evaluate(context=context)
                return self._normalise_writing_report(
                    WritingEvaluationReport.model_validate(report)
                )
            except (LLMError, ValidationError) as exc:
                if attempt_number == 1:
                    logger.warning(
                        "challenge_writing_evaluation_retry attempt_id=%s err=%s",
                        attempt.id,
                        exc,
                    )
                    continue
                logger.exception(
                    "challenge_writing_evaluation_fallback attempt_id=%s",
                    attempt.id,
                )
            except Exception:
                logger.exception(
                    "challenge_writing_evaluation_fallback_unexpected attempt_id=%s",
                    attempt.id,
                )
                break

        return self._fallback_writing_evaluation(
            attempt=attempt,
            response_payload=response_payload,
            reason="AI writing evaluation is temporarily unavailable.",
        )

    async def _feedback_phase_4_attempt(
        self,
        *,
        attempt: ChallengeAttempt,
        response_payload: dict,
        evaluation_report: UnifiedEvaluationReport,
    ) -> IELTSFeedbackReport:
        feedback_generator = self._feedback_generator or IELTSChallengeFeedbackAgent()
        context = {
            "attempt_id": attempt.id,
            "task_payload": attempt.task_payload,
            "response_payload": response_payload,
            "evaluation_report": evaluation_report.model_dump(),
        }
        try:
            report = await feedback_generator.generate(context=context)
            return IELTSFeedbackReport.model_validate(report)
        except (LLMError, ValidationError):
            logger.exception("challenge_feedback_fallback attempt_id=%s", attempt.id)
        except Exception:
            logger.exception(
                "challenge_feedback_fallback_unexpected attempt_id=%s",
                attempt.id,
            )
        return self._fallback_feedback_report(evaluation_report=evaluation_report)

    def _writing_evaluation_context(
        self,
        *,
        attempt: ChallengeAttempt,
        response_payload: dict,
    ) -> dict[str, Any]:
        task_payload = attempt.task_payload or {}
        sections = _as_dict(task_payload.get("sections"))
        return {
            "attempt_id": attempt.id,
            "task_payload": task_payload,
            "response_payload": response_payload,
            "writing_task": sections.get("writing", {}),
            "writing_responses": _as_dict(response_payload.get("writing")),
        }

    @staticmethod
    def _normalise_writing_report(
        report: WritingEvaluationReport,
    ) -> WritingEvaluationReport:
        items: list[WritingPromptEvaluation] = []
        for item in report.items:
            criterion_bands = [
                item.criteria.task_response.band,
                item.criteria.coherence_and_cohesion.band,
                item.criteria.lexical_resource.band,
                item.criteria.grammatical_range_and_accuracy.band,
            ]
            items.append(
                item.model_copy(
                    update={"band": round_to_half_band(sum(criterion_bands) / 4)}
                )
            )

        section_band = (
            round_to_half_band(sum(item.band for item in items) / len(items))
            if items
            else 0.0
        )
        return report.model_copy(
            update={
                "items": items,
                "section_band": section_band,
            }
        )

    def _fallback_writing_evaluation(
        self,
        *,
        attempt: ChallengeAttempt,
        response_payload: dict,
        reason: str,
    ) -> WritingEvaluationReport:
        task_payload = attempt.task_payload or {}
        sections = _as_dict(task_payload.get("sections"))
        writing_task = _as_dict(sections.get("writing"))
        prompts = _list_of_dicts(writing_task.get("items"))
        writing_responses = _as_dict(response_payload.get("writing"))
        any_response = _has_any_writing_response(response_payload)
        section_band = 5.0 if any_response else 0.0
        criteria = _fallback_writing_criteria(section_band=section_band, reason=reason)

        items: list[WritingPromptEvaluation] = []
        for index, prompt in enumerate(prompts):
            item_id = str(prompt.get("item_id") or f"w{index + 1}")
            response = str(writing_responses.get(item_id) or "")
            response_band = 5.0 if response.strip() else 0.0
            items.append(
                WritingPromptEvaluation(
                    item_id=item_id,
                    prompt=str(prompt.get("prompt") or "Writing prompt"),
                    response_excerpt=response[:240],
                    response_word_count=count_words(response),
                    criteria=(
                        _fallback_writing_criteria(
                            section_band=response_band,
                            reason=reason,
                        )
                    ),
                    issues=[
                        WritingIssue(
                            quote=response[:80] or "No submitted writing",
                            issue=reason,
                            correction="",
                            suggestion=(
                                "Review the prompt and write a clear position with "
                                "two supported ideas."
                            ),
                        )
                    ],
                    band=response_band,
                    summary=reason,
                )
            )

        if not items:
            items.append(
                WritingPromptEvaluation(
                    item_id="writing",
                    prompt="Writing prompt",
                    response_excerpt="",
                    response_word_count=0,
                    criteria=criteria,
                    issues=[
                        WritingIssue(
                            quote="No submitted writing",
                            issue=reason,
                            correction="",
                            suggestion=(
                                "Write at least one full paragraph before submitting."
                            ),
                        )
                    ],
                    band=section_band,
                    summary=reason,
                )
            )

        return WritingEvaluationReport(
            mode="ai_writing_phase_4",
            items=items,
            section_band=section_band,
            summary=reason,
        )

    @staticmethod
    def _fallback_feedback_report(
        *,
        evaluation_report: UnifiedEvaluationReport,
    ) -> IELTSFeedbackReport:
        reading_total = evaluation_report.reading.total_questions
        reading_correct = evaluation_report.reading.total_correct
        return IELTSFeedbackReport(
            mode="phase_4_feedback",
            overall_summary=(
                "Your responses were saved and scored. Detailed AI feedback is "
                "temporarily unavailable, so this report uses a concise local summary."
            ),
            sections={
                "listening": SectionFeedback(
                    went_well=["The placeholder listening section was included."],
                    needs_work=["Detailed listening scoring arrives in Phase 5."],
                    next_tip="Use the transcript to practise identifying key details.",
                ),
                "reading": SectionFeedback(
                    went_well=[
                        f"You answered {reading_correct} of {reading_total} reading items correctly."
                    ],
                    needs_work=[
                        "Review the generated explanations for any missed reading items."
                    ],
                    next_tip="Underline the exact sentence that supports each answer.",
                ),
                "writing": SectionFeedback(
                    went_well=[
                        f"Your Writing band was recorded as {evaluation_report.writing.section_band:.1f}."
                    ],
                    needs_work=[
                        "Detailed criterion feedback is temporarily unavailable."
                    ],
                    next_tip=(
                        "Revise one paragraph with a clear topic sentence and a "
                        "specific supporting example."
                    ),
                ),
                "speaking": SectionFeedback(
                    went_well=["The placeholder speaking section was included."],
                    needs_work=["Detailed speaking scoring arrives in Phase 6."],
                    next_tip="Practise one prompt aloud for 30 seconds.",
                ),
            },
        )

    def _detail_for(self, *, challenge: Challenge, user_id: int) -> ChallengeDetailRead:
        levels = sorted(challenge.levels, key=lambda level: level.level_number)
        level_ids = [level.id for level in levels]
        best_scores = self.attempt_repo.best_scores_by_level(
            user_id=user_id,
            level_ids=level_ids,
        )
        attempt_counts = self.attempt_repo.attempt_counts_by_level(
            user_id=user_id,
            level_ids=level_ids,
        )

        unlocked_level_numbers = {1}
        levels_by_number = {level.level_number: level for level in levels}
        for level in levels:
            previous = levels_by_number.get(level.level_number - 1)
            if previous is None:
                continue
            previous_best = best_scores.get(previous.id)
            if (
                previous_best is not None
                and previous_best >= float(previous.pass_threshold)
            ):
                unlocked_level_numbers.add(level.level_number)

        return ChallengeDetailRead(
            id=challenge.id,
            slug=challenge.slug,
            name=challenge.name,
            short_description=challenge.short_description,
            rules_md=challenge.rules_md,
            icon=challenge.icon,
            levels=[
                ChallengeLevelRead(
                    id=level.id,
                    level_number=level.level_number,
                    name=level.name,
                    time_limit_seconds=level.time_limit_seconds,
                    pass_threshold=float(level.pass_threshold),
                    config=level.config,
                    unlocked=level.level_number in unlocked_level_numbers,
                    best_score=best_scores.get(level.id),
                    attempt_count=attempt_counts.get(level.id, 0),
                )
                for level in levels
            ],
        )

    def _level_is_unlocked(
        self,
        *,
        challenge: Challenge,
        level: ChallengeLevel,
        user_id: int,
    ) -> bool:
        if level.level_number == 1:
            return True

        previous = self._level_by_number(
            challenge=challenge,
            level_number=level.level_number - 1,
        )
        if previous is None:
            return False

        best_scores = self.attempt_repo.best_scores_by_level(
            user_id=user_id,
            level_ids=[previous.id],
        )
        previous_best = best_scores.get(previous.id)
        return (
            previous_best is not None
            and previous_best >= float(previous.pass_threshold)
        )

    @staticmethod
    def _level_by_number(
        *,
        challenge: Challenge,
        level_number: int,
    ) -> ChallengeLevel | None:
        return next(
            (
                level
                for level in challenge.levels
                if level.level_number == level_number
            ),
            None,
        )

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    async def _generated_or_starter_task_payload(
        self,
        *,
        challenge: Challenge,
        level: ChallengeLevel,
        user_id: int,
    ) -> dict:
        generator = self._generator or IELTSChallengeGenerator()
        context = self._generator_context(
            challenge=challenge,
            level=level,
            user_id=user_id,
        )

        for attempt_number in (1, 2):
            try:
                payload = await generator.generate(context=context)
                return GeneratedIELTSTaskPayload.model_validate(payload).model_dump()
            except (LLMError, ValidationError) as exc:
                if attempt_number == 1:
                    logger.warning(
                        "challenge_generation_retry challenge=%s level=%s err=%s",
                        challenge.slug,
                        level.level_number,
                        exc,
                    )
                    continue
                logger.exception(
                    "challenge_generation_fallback challenge=%s level=%s",
                    challenge.slug,
                    level.level_number,
                )
            except Exception:
                logger.exception(
                    "challenge_generation_fallback_unexpected challenge=%s level=%s",
                    challenge.slug,
                    level.level_number,
                )
                break

        return self._starter_task_payload(challenge=challenge, level=level)

    def _generator_context(
        self,
        *,
        challenge: Challenge,
        level: ChallengeLevel,
        user_id: int,
    ) -> dict[str, Any]:
        return {
            "challenge_slug": challenge.slug,
            "challenge_name": challenge.name,
            "level_number": level.level_number,
            "level_name": level.name,
            "time_limit_seconds": level.time_limit_seconds,
            "level_config": level.config,
            "user_history_summary": self._user_history_summary(
                user_id=user_id,
                challenge=challenge,
            ),
        }

    def _user_history_summary(
        self,
        *,
        user_id: int,
        challenge: Challenge,
    ) -> str:
        recent_attempts = self.attempt_repo.list_recent_completed_for_challenge(
            user_id=user_id,
            challenge_id=challenge.id,
            limit=5,
        )
        topics: list[str] = []
        for attempt in recent_attempts:
            task_payload = attempt.task_payload or {}
            sections = task_payload.get("sections") or {}
            reading = sections.get("reading") or {}
            title = reading.get("passage_title")
            if isinstance(title, str) and title.strip():
                topics.append(title.strip())

        if not topics:
            return "No recent IELTS challenge history."

        unique_topics = list(dict.fromkeys(topics))
        return (
            "Recent IELTS challenge reading topics/passages: "
            f"{'; '.join(unique_topics)}. Avoid repeating these topics."
        )

    @staticmethod
    def _starter_task_payload(*, challenge: Challenge, level: ChallengeLevel) -> dict:
        sections = level.config.get("sections", {})
        reading_count = int(sections.get("reading", {}).get("num_questions", 4))
        listening_count = int(sections.get("listening", {}).get("num_questions", 3))
        writing_count = int(sections.get("writing", {}).get("prompt_count", 1))
        speaking_count = int(sections.get("speaking", {}).get("num_prompts", 1))
        writing_target = int(sections.get("writing", {}).get("target_word_count", 80))
        speaking_seconds = int(sections.get("speaking", {}).get("response_seconds", 30))

        reading_items = _take_items(
            [
                {
                    "item_id": "r1",
                    "prompt": "What is the main point of the passage?",
                    "options": [
                        "Small daily habits can compound into stronger fluency.",
                        "Technology is replacing classroom teachers.",
                        "IELTS reading is mostly a memory test.",
                        "Learners should avoid timed practice.",
                    ],
                    "correct_index": 0,
                    "explanation": "The passage argues for steady, focused practice.",
                },
                {
                    "item_id": "r2",
                    "prompt": "According to the passage, why should practice be timed?",
                    "options": [
                        "It makes all answers shorter.",
                        "It builds calm decision-making under pressure.",
                        "It removes the need for feedback.",
                        "It guarantees a higher IELTS band.",
                    ],
                    "correct_index": 1,
                    "explanation": "The passage links timing with pressure management.",
                },
                {
                    "item_id": "r3",
                    "prompt": "Which habit does the writer recommend after each attempt?",
                    "options": [
                        "Repeating the exact same answers.",
                        "Ignoring mistakes until the next week.",
                        "Reviewing errors and rewriting weak parts.",
                        "Starting a harder level immediately.",
                    ],
                    "correct_index": 2,
                    "explanation": "The review step is presented as part of improvement.",
                },
                {
                    "item_id": "r4",
                    "prompt": "The writer's tone is best described as...",
                    "options": [
                        "dismissive",
                        "uncertain",
                        "practical",
                        "humorous",
                    ],
                    "correct_index": 2,
                    "explanation": "The advice is direct, balanced, and practical.",
                },
                {
                    "item_id": "r5",
                    "prompt": "What does the passage imply about feedback?",
                    "options": [
                        "It is useful only for advanced learners.",
                        "It helps turn attempts into measurable progress.",
                        "It should replace independent practice.",
                        "It matters less than speed.",
                    ],
                    "correct_index": 1,
                    "explanation": "Feedback is described as the bridge to progress.",
                },
                {
                    "item_id": "r6",
                    "prompt": "Why might learners keep a short attempt history?",
                    "options": [
                        "To compare themes, scores, and recurring mistakes.",
                        "To avoid taking future timed tests.",
                        "To memorize old answer keys.",
                        "To reduce the number of sections.",
                    ],
                    "correct_index": 0,
                    "explanation": "A history makes patterns visible over time.",
                },
                {
                    "item_id": "r7",
                    "prompt": "Which idea is NOT supported by the passage?",
                    "options": [
                        "Timed practice should feel manageable.",
                        "Learners benefit from reviewing weak answers.",
                        "Every learner should study without breaks for hours.",
                        "Progress can come from repeated short attempts.",
                    ],
                    "correct_index": 2,
                    "explanation": "The passage favors short, focused practice.",
                },
                {
                    "item_id": "r8",
                    "prompt": "What does the word 'compound' most nearly mean here?",
                    "options": [
                        "grow gradually",
                        "become confusing",
                        "stay unchanged",
                        "move quickly",
                    ],
                    "correct_index": 0,
                    "explanation": "Compound means small gains build over time.",
                },
            ],
            reading_count,
        )
        listening_items = _take_items(
            [
                {
                    "item_id": "l1",
                    "prompt": "What is the speaker mainly describing?",
                    "options": [
                        "A weekly study routine",
                        "A library membership rule",
                        "A travel announcement",
                        "A restaurant booking",
                    ],
                    "correct_index": 0,
                    "explanation": "The transcript is a placeholder study routine.",
                },
                {
                    "item_id": "l2",
                    "prompt": "When does the speaker suggest reviewing mistakes?",
                    "options": [
                        "Before sleeping",
                        "Immediately after practice",
                        "At the end of the month",
                        "Only before exams",
                    ],
                    "correct_index": 1,
                    "explanation": "The transcript says review should happen right away.",
                },
                {
                    "item_id": "l3",
                    "prompt": "What should learners keep brief?",
                    "options": [
                        "Their reading passages",
                        "Their speaking recordings",
                        "Their notes after each attempt",
                        "Their login sessions",
                    ],
                    "correct_index": 2,
                    "explanation": "Short notes are easier to revisit.",
                },
                {
                    "item_id": "l4",
                    "prompt": "What does the speaker recommend doing twice a week?",
                    "options": [
                        "Taking a timed sprint",
                        "Changing exam goals",
                        "Skipping writing",
                        "Reading answer keys first",
                    ],
                    "correct_index": 0,
                    "explanation": "The suggested rhythm is two timed sprints weekly.",
                },
                {
                    "item_id": "l5",
                    "prompt": "What is the speaker's attitude toward mistakes?",
                    "options": [
                        "They are useful evidence.",
                        "They should be hidden.",
                        "They make practice pointless.",
                        "They are always caused by grammar.",
                    ],
                    "correct_index": 0,
                    "explanation": "Mistakes are framed as information for learning.",
                },
                {
                    "item_id": "l6",
                    "prompt": "Which section does the speaker mention recording?",
                    "options": ["Listening", "Reading", "Writing", "Speaking"],
                    "correct_index": 3,
                    "explanation": "The speaker refers to short speaking recordings.",
                },
                {
                    "item_id": "l7",
                    "prompt": "What should learners avoid during a timed sprint?",
                    "options": [
                        "Moving between sections",
                        "Pausing the timer",
                        "Answering reading questions",
                        "Writing a short essay",
                    ],
                    "correct_index": 1,
                    "explanation": "The sprint is designed to be uninterrupted.",
                },
                {
                    "item_id": "l8",
                    "prompt": "What is the final recommendation?",
                    "options": [
                        "Choose one correction to practise next.",
                        "Retake the same test immediately.",
                        "Focus only on vocabulary.",
                        "Ignore section scores.",
                    ],
                    "correct_index": 0,
                    "explanation": "The transcript ends with one concrete next step.",
                },
            ],
            listening_count,
        )
        writing_prompts = _take_items(
            [
                {
                    "item_id": "w1",
                    "prompt": (
                        "Some people believe short, regular practice is better than "
                        "occasional long study sessions. To what extent do you agree?"
                    ),
                    "target_word_count": writing_target,
                },
                {
                    "item_id": "w2",
                    "prompt": (
                        "Online learning tools are becoming common in language study. "
                        "Discuss the advantages and disadvantages."
                    ),
                    "target_word_count": writing_target,
                },
            ],
            writing_count,
        )
        speaking_prompts = _take_items(
            [
                "Describe a skill you improved through regular practice.",
                "Talk about a time when feedback helped you perform better.",
            ],
            speaking_count,
        )

        return {
            "meta": {
                "challenge_slug": challenge.slug,
                "challenge_name": challenge.name,
                "level_number": level.level_number,
                "level_name": level.name,
                "phase": 2,
            },
            "sections": {
                "listening": {
                    "widget": "listen_and_respond",
                    "task_intro": "Listen to the short talk and answer the questions.",
                    "instructions": "Audio is a placeholder in Phase 2.",
                    "audio_url": None,
                    "audio_script": (
                        "In this placeholder recording, a tutor explains that learners "
                        "should take short timed sprints, review mistakes immediately, "
                        "keep brief notes, and choose one correction to practise next."
                    ),
                    "audio_duration_seconds": 45,
                    "inner_widget": "mcq",
                    "items": listening_items,
                },
                "reading": {
                    "widget": "mcq",
                    "task_intro": "Read the passage and choose the best answers.",
                    "instructions": "Select one option for each question.",
                    "passage_title": "How Short Practice Builds Exam Confidence",
                    "passage": (
                        "Language learners often assume that progress requires long, "
                        "perfect study sessions. In reality, short attempts can be more "
                        "useful when they are focused and repeated. A timed sprint gives "
                        "learners a clear boundary, so they practise making decisions "
                        "under pressure without feeling trapped for an entire afternoon. "
                        "After each attempt, the most valuable habit is not simply to "
                        "look at the score. Learners should review their errors, rewrite "
                        "weak writing sentences, and notice which question types slowed "
                        "them down. Over time, these small reviews compound into better "
                        "fluency, calmer pacing, and more practical confidence."
                    ),
                    "items": reading_items,
                },
                "writing": {
                    "widget": "timed_text",
                    "task_intro": "Write a short IELTS-style response.",
                    "instructions": "Use the global challenge timer.",
                    "items": writing_prompts,
                    "target_word_count": writing_target,
                    "time_limit_seconds": level.time_limit_seconds,
                    "minimum_word_count": max(40, writing_target // 2),
                    "no_editing_allowed": False,
                    "sample_response": "",
                },
                "speaking": {
                    "widget": "speak_and_record",
                    "task_intro": "Record a short spoken answer.",
                    "instructions": "Recording stays local in Phase 2.",
                    "speaking_duration_seconds": speaking_seconds,
                    "speaking_prompts": speaking_prompts,
                    "sample_responses": [],
                },
            },
        }

    @staticmethod
    def _best_attempt_ids(attempts: list[ChallengeAttempt]) -> set[int]:
        best_by_level: dict[int, tuple[float, int]] = {}
        for attempt in attempts:
            if attempt.overall_score is None:
                continue
            score = float(attempt.overall_score)
            current = best_by_level.get(attempt.challenge_level_id)
            if current is None or score > current[0]:
                best_by_level[attempt.challenge_level_id] = (score, attempt.id)
        return {attempt_id for _score, attempt_id in best_by_level.values()}


def _take_items(items: list, count: int) -> list:
    if count <= len(items):
        return items[:count]
    repeated = []
    while len(repeated) < count:
        repeated.extend(items)
    return repeated[:count]


def round_to_half_band(value: float) -> float:
    """Round to the nearest IELTS half band using IELTS-style half-up ties."""
    rounded = (Decimal(str(value)) * Decimal("2")).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP,
    ) / Decimal("2")
    return float(max(Decimal("0"), min(Decimal("9"), rounded)))


def grade_reading_section(
    *,
    task_payload: dict,
    response_payload: dict,
) -> ReadingEvaluationReport:
    """Grade generated Reading MCQs from the persisted answer key."""
    sections = _as_dict((task_payload or {}).get("sections"))
    reading = _as_dict(sections.get("reading"))
    items = _list_of_dicts(reading.get("items"))
    responses = _as_dict((response_payload or {}).get("reading"))

    question_reports: list[ReadingQuestionEvaluation] = []
    total_correct = 0
    for index, item in enumerate(items):
        item_id = str(item.get("item_id") or f"r{index + 1}")
        options = [
            str(option)
            for option in item.get("options", [])
            if isinstance(option, str) and option.strip()
        ]
        correct_index = int(item.get("correct_index") or 0)
        if correct_index < 0 or correct_index > 3:
            correct_index = 0

        correct_letter = _option_letter(correct_index)
        user_answer = responses.get(item_id)
        user_letter = _normalise_option_letter(user_answer)
        correct = user_letter == correct_letter
        total_correct += int(correct)
        correct_answer = (
            options[correct_index]
            if correct_index < len(options)
            else f"Option {correct_letter}"
        )

        question_reports.append(
            ReadingQuestionEvaluation(
                item_id=item_id,
                prompt=str(item.get("prompt") or f"Reading question {index + 1}"),
                user_answer=str(user_answer) if user_answer is not None else None,
                correct_answer=correct_answer,
                correct_index=correct_index,
                correct=correct,
                explanation=str(item.get("explanation") or ""),
            )
        )

    total_questions = len(question_reports)
    raw_scaled_40 = _scale_raw_score_to_40(total_correct, total_questions)
    return ReadingEvaluationReport(
        mode="deterministic_answer_key",
        total_correct=total_correct,
        total_questions=total_questions,
        raw_scaled_40=raw_scaled_40,
        section_band=academic_reading_band(raw_scaled_40),
        questions=question_reports,
    )


def academic_reading_band(raw_score_out_of_40: int) -> float:
    """Map an IELTS Academic Reading raw score to an approximate band."""
    raw_score = max(0, min(40, int(raw_score_out_of_40)))
    thresholds = [
        (39, 9.0),
        (37, 8.5),
        (35, 8.0),
        (33, 7.5),
        (30, 7.0),
        (27, 6.5),
        (23, 6.0),
        (19, 5.5),
        (15, 5.0),
        (13, 4.5),
        (10, 4.0),
        (8, 3.5),
        (6, 3.0),
        (4, 2.5),
        (3, 2.0),
        (2, 1.5),
        (1, 1.0),
        (0, 0.0),
    ]
    for threshold, band in thresholds:
        if raw_score >= threshold:
            return band
    return 0.0


def count_words(text: str) -> int:
    return len(text.strip().split()) if text.strip() else 0


def _scale_raw_score_to_40(total_correct: int, total_questions: int) -> int:
    if total_questions <= 0:
        return 0
    scaled = Decimal(total_correct) * Decimal("40") / Decimal(total_questions)
    return int(scaled.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _option_letter(index: int) -> str:
    return chr(ord("A") + index)


def _normalise_option_letter(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, int) and 0 <= value <= 3:
        return _option_letter(value)
    text = str(value).strip().upper()
    if len(text) == 1 and "A" <= text <= "D":
        return text
    if text.isdigit():
        number = int(text)
        if 0 <= number <= 3:
            return _option_letter(number)
    return text


def _has_any_writing_response(response_payload: dict) -> bool:
    writing_responses = _as_dict((response_payload or {}).get("writing"))
    return any(str(value).strip() for value in writing_responses.values())


def _fallback_writing_criteria(
    *,
    section_band: float,
    reason: str,
) -> WritingCriteriaEvaluation:
    criterion = WritingCriterionEvaluation(
        band=section_band,
        rationale=reason,
    )
    return WritingCriteriaEvaluation(
        task_response=criterion,
        coherence_and_cohesion=criterion,
        lexical_resource=criterion,
        grammatical_range_and_accuracy=criterion,
    )


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _list_of_dicts(value: Any) -> list[dict]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]
