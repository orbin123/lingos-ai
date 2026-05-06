"""Business logic for accepting + grading a user's response to a task."""

from sqlalchemy.orm import Session

import logging

from app.ai.embeddings import EmbeddingError, EmbeddingService
from app.ai.agents import EvaluationService
from app.modules.progress.service import ScoreUpdaterService
from app.modules.responses.exceptions import (
    NotResponseOwner,
    UserTaskNotFound,
    UserTaskNotSubmittable,
)
from app.modules.responses.feedback_service import FeedbackService
from app.modules.responses.models import Evaluation, Feedback, UserResponse
from app.modules.responses.repository import (
    EvaluationRepository,
    ResponseRepository,
)
from app.modules.skills.models import UserSkillScore
from app.modules.tasks.models import UserTaskStatus
from app.modules.tasks.repository import UserTaskRepository

logger = logging.getLogger(__name__)

# Statuses that allow a response to be submitted
_SUBMITTABLE_STATUSES = {UserTaskStatus.PENDING, UserTaskStatus.IN_PROGRESS}


class ResponseService:
    """Orchestrates the full submit → evaluate → feedback → score loop."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_task_repo = UserTaskRepository(db)
        self.response_repo = ResponseRepository(db)
        self.evaluation_repo = EvaluationRepository(db)
        # Sub-services — each owns its own commit boundary
        self.evaluator = EvaluationService()
        self.feedback_service = FeedbackService(db)
        self.score_updater = ScoreUpdaterService(db)
        self.embedding_service = EmbeddingService()   

    # ---- Step 1: persist response only (private, reused by submit_and_grade) ----
    def _persist_response(
        self,
        *,
        user_id: int,
        user_task_id: int,
        content: dict,
        raw_text: str | None,
    ) -> UserResponse:
        """Validate ownership/state and save the UserResponse row.

        Same guards as before: 404 / 403 / 409. One commit.
        """
        # 1. Load the assignment
        user_task = self.user_task_repo.get_by_id(user_task_id)
        if user_task is None:
            raise UserTaskNotFound(f"UserTask {user_task_id} does not exist")

        # 2. Ownership check
        if user_task.user_id != user_id:
            raise NotResponseOwner(
                f"User {user_id} cannot submit a response for UserTask "
                f"{user_task_id} (owner: {user_task.user_id})"
            )

        # 3. State check — block only truly unsubmittable states (skipped)
        if user_task.status == UserTaskStatus.SKIPPED:
            raise UserTaskNotSubmittable(
                f"UserTask {user_task_id} is skipped — cannot submit"
            )

        # 4. Overwrite any previous response (+ cascade deletes evaluation,
        #    feedback via DB ondelete=CASCADE so every resubmit is a clean slate).
        existing = self.response_repo.get_by_user_task_id(user_task_id)
        if existing is not None:
            logger.info(
                "UserTask %s already has response %s — deleting and rewriting",
                user_task_id, existing.id,
            )
            self.db.delete(existing)
            self.db.flush()  # remove before inserting the new one

        # 5. Create the new response row
        response = self.response_repo.create(
            user_task_id=user_task_id,
            content=content,
            raw_text=raw_text,
        )

        # 6. Reset the assignment status so the task can be re-evaluated
        user_task.status = UserTaskStatus.IN_PROGRESS

        # 7. Commit response + status flip atomically
        self.db.commit()
        self.db.refresh(response)
        return response

    # ---- Step 2: run the rule-based evaluator and save it ----
    def _evaluate_and_persist(
        self, *, response: UserResponse
    ) -> Evaluation:
        """Run the rule-based evaluator and save the Evaluation row."""
        # Overwrite existing evaluation if present (resubmit scenario)
        existing = self.evaluation_repo.get_by_response_id(response.id)
        if existing is not None:
            self.db.delete(existing)
            self.db.flush()

        # Walk back to the Task to get the answer key + activity type
        user_task = self.user_task_repo.get_by_id(response.user_task_id)
        task = user_task.task

        logger.info(
            "[evaluator] evaluating response=%s user_task=%s task=%s task_type=%s",
            response.id, response.user_task_id, task.id, task.task_type,
        )

        activity_type = self._first_activity_type(task.content)
        logger.info("[evaluator] resolved activity_type=%r", activity_type)

        report = self.evaluator.evaluate(
            activity_type=activity_type,
            task_content=task.content,
            user_answers=response.content,
        )
        logger.info(
            "[evaluator] scored: total=%s correct=%s percentage=%s%%",
            report.get("total"), report.get("correct_count"), report.get("percentage"),
        )

        # overall_score = percentage / 10 → 0–10 scale (matches Numeric(4,2))
        percentage = float(report["percentage"])
        overall_score = round(percentage / 10.0, 2)

        evaluation = self.evaluation_repo.create(
            response_id=response.id,
            overall_score=overall_score,
            percentage=percentage,
            report=report,
        )
        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation

    @staticmethod
    def _first_activity_type(task_content: dict) -> str:
        """Detect the activity_type to use for evaluation.

        Two content shapes exist:

        1. SEEDED tasks (old hand-authored content):
              {"activities": [{"activity_type": "fill_in_the_blanks", ...}]}
           → return activities[0]["activity_type"]

        2. GENERATED tasks (LLM output, no "activities" key):
           Shape is inferred from which top-level / item-level keys are present.
           Each generated Pydantic model has a unique fingerprint field.

        Raises ValueError only if the shape is genuinely unrecognisable.
        """
        # ── Seeded path ──────────────────────────────────────────────
        activities = task_content.get("activities") or []
        if activities:
            detected = activities[0]["activity_type"]
            logger.debug("[evaluator] seeded task → activity_type=%r", detected)
            return detected

        # ── Generated path — infer from content fingerprint ──────────
        # Check more-specific shapes first so there's no ambiguity.

        if "blanks" in task_content:
            logger.debug("[evaluator] generated task fingerprint='blanks' → fill_in_blanks")
            return "fill_in_blanks"

        if "sentences" in task_content and "total_with_errors" in task_content:
            logger.debug("[evaluator] generated task fingerprint='sentences+total_with_errors' → error_spotting")
            return "error_spotting"

        if "items" in task_content:
            items = task_content["items"]
            if items:
                first = items[0]
                if "direction" in first:
                    logger.debug("[evaluator] generated task fingerprint='items[].direction' → voice_conversion")
                    return "voice_conversion"
                if "incorrect_sentence" in first:
                    logger.debug("[evaluator] generated task fingerprint='items[].incorrect_sentence' → error_correction")
                    return "error_correction"
                if "transformation_target" in first:
                    logger.debug("[evaluator] generated task fingerprint='items[].transformation_target' → sentence_transformation")
                    return "sentence_transformation"

        raise ValueError(
            f"Cannot detect activity_type from task content. "
            f"Top-level keys present: {list(task_content.keys())}"
        )
    
    # ---- Step 5 (side-effect): embed response + store vector ----
    async def _embed_response(self, *, response: UserResponse) -> None:
        """Embed raw_text + upsert into Pinecone. Best-effort.

        - If raw_text is missing -> mark as 'skipped', return.
        - On HF/Pinecone failure -> log + mark 'failed'. Never raises.
          A future background job will retry rows where status != 'success'.
        """
        # Skip non-text submissions (MCQ-only, fill-in-blanks-only, etc.)
        if not response.raw_text or not response.raw_text.strip():
            self.response_repo.set_embedding_result(
                response_id=response.id, status="skipped"
            )
            self.db.commit()
            return

        # Reload user_task to pull user_id + task_id for metadata
        user_task = self.user_task_repo.get_by_id(response.user_task_id)
        vector_id = f"response:{response.id}"
        metadata = {
            "response_id": response.id,
            "user_id": user_task.user_id,
            "user_task_id": response.user_task_id,
            "task_id": user_task.task_id,
            "raw_text": response.raw_text[:1000],  # Pinecone metadata size cap
        }

        try:
            await self.embedding_service.embed_and_store(
                vector_id=vector_id,
                text=response.raw_text,
                metadata=metadata,
            )
        except EmbeddingError as e:
            # Log + mark failed, but DO NOT raise — user already got feedback
            logger.warning(
                "Embedding failed for response %s: %s", response.id, e
            )
            self.response_repo.set_embedding_result(
                response_id=response.id, status="failed"
            )
            self.db.commit()
            return

        # Success path
        self.response_repo.set_embedding_result(
            response_id=response.id,
            status="success",
            pinecone_vector_id=vector_id,
        )
        self.db.commit()

    # ---- The whole loop ----
    async def submit_and_grade(
        self,
        *,
        user_id: int,
        user_task_id: int,
        content: dict,
        raw_text: str | None = None,
    ) -> tuple[UserResponse, Evaluation, Feedback, list[UserSkillScore]]:
        """Submit a response and run the entire grading loop.

        Returns a 4-tuple: (response, evaluation, feedback, updated_scores).
        Routes layer turns this into the public schema.

        Failure modes:
          - 404/403/409 from _persist_response (handled in route)
          - LLM failure from FeedbackService → bubbles up as
            FeedbackGenerationFailed (route maps to 502)
        """
        # 1. Save response (commit 1)
        response = self._persist_response(
            user_id=user_id,
            user_task_id=user_task_id,
            content=content,
            raw_text=raw_text,
        )

        # 2. Evaluate + save (commit 2)
        evaluation = self._evaluate_and_persist(response=response)

        # 3. Generate feedback via LLM + save (commit 3, may fail loudly)
        feedback = await self.feedback_service.generate_for_evaluation(
            evaluation.id
        )

        # 4. Update skill scores + log progress (commit 4)
        updated_scores = self.score_updater.apply(evaluation.id)

        # 5. Mark the assignment completed so /tasks/complete-day can advance.
        user_task = self.user_task_repo.get_by_id(user_task_id)
        if user_task is not None:
            self.user_task_repo.mark_completed(user_task)
            self.db.commit()

        # 6. Embed response — best-effort, never blocks the user (commit 6)
        await self._embed_response(response=response)

        return response, evaluation, feedback, updated_scores
