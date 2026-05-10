"""HTTP endpoints for response submission."""

import hashlib
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.progress.exceptions import TaskHasNoTargetSkills
from app.modules.responses.exceptions import (
    FeedbackAlreadyExists,
    FeedbackGenerationFailed,
    NotResponseOwner,
    ResponseAlreadySubmitted,
    UserTaskNotFound,
    UserTaskNotSubmittable,
)
from app.modules.responses.schemas import (
    EvaluationRead,
    FeedbackRead,
    ResponseGradedRead,
    ResponseRead,
    ResponseSubmit,
    SkillScoreRead,
)
from app.modules.responses.service import ResponseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/responses", tags=["responses"])


@router.post(
    "/submit",
    response_model=ResponseGradedRead,
    status_code=status.HTTP_201_CREATED,
)
async def submit_response(
    payload: ResponseSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResponseGradedRead:
    """Submit a response and run the full grading loop.

    Pipeline (per request):
      1. Persist UserResponse, flip UserTask → IN_PROGRESS
      2. Run rule-based evaluator → save Evaluation
      3. Call Feedback Agent (LLM) → save Feedback
      4. Update UserSkillScore (WMA) + insert ProgressLog rows

    Returns the full bundle in one round trip:
      response, evaluation, feedback, skill_scores

    Errors:
      403 — UserTask belongs to a different user
      404 — UserTask does not exist
      409 — UserTask already completed/skipped, response already submitted,
            or feedback already generated (retry)
      422 — Task has no target skills (data integrity bug)
      502 — LLM call failed; response & evaluation are saved, retry later
    """
    service = ResponseService(db)
    try:
        response, evaluation, feedback, updated_scores = (
            await service.submit_and_grade(
                user_id=current_user.id,
                user_task_id=payload.user_task_id,
                content=payload.content,
                raw_text=payload.raw_text,
            )
        )
    except UserTaskNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotResponseOwner as e:
        raise HTTPException(status_code=403, detail=str(e))
    except (
        UserTaskNotSubmittable,
        ResponseAlreadySubmitted,
        FeedbackAlreadyExists,
    ) as e:
        raise HTTPException(status_code=409, detail=str(e))
    except TaskHasNoTargetSkills as e:
        raise HTTPException(status_code=422, detail=str(e))
    except FeedbackGenerationFailed as e:
        raise HTTPException(status_code=502, detail=str(e))

    # Build skill_scores with the skill name (frontend-friendly).
    # The score_updater already loaded skill rows via the upsert; the
    # `.skill` relationship is on UserSkillScore, so this is one extra
    # SELECT per row at worst — fine for 1–3 skills per task.
    skill_scores = [
        SkillScoreRead(
            skill_id=row.skill_id,
            skill_name=row.skill.name,
            score=float(row.score),
        )
        for row in updated_scores
    ]

    return ResponseGradedRead(
        response=ResponseRead.model_validate(response),
        evaluation=EvaluationRead.model_validate(evaluation),
        feedback=FeedbackRead.model_validate(feedback),
        skill_scores=skill_scores,
    )


@router.get(
    "/by-task/{user_task_id}",
    response_model=ResponseGradedRead,
    status_code=status.HTTP_200_OK,
)
def get_response_by_task(
    user_task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResponseGradedRead:
    """Return the stored graded result for a completed task.

    Used by the history/snapshot page to display a read-only view of what
    the user submitted and how it was scored.

    Errors:
      403 — task belongs to a different user
      404 — task, response, evaluation, or feedback not found
    """
    from app.modules.tasks.models import UserTask
    from app.modules.responses.models import UserResponse, Evaluation, Feedback
    from app.modules.skills.models import UserSkillScore

    user_task = db.query(UserTask).filter(UserTask.id == user_task_id).first()
    if user_task is None:
        raise HTTPException(status_code=404, detail="UserTask not found")
    if user_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    response = (
        db.query(UserResponse)
        .filter(UserResponse.user_task_id == user_task_id)
        .first()
    )
    if response is None:
        raise HTTPException(status_code=404, detail="No response found for this task")

    evaluation = response.evaluation
    if evaluation is None:
        raise HTTPException(status_code=404, detail="No evaluation found for this task")

    feedback = evaluation.feedback
    if feedback is None:
        raise HTTPException(status_code=404, detail="No feedback found for this task")

    return ResponseGradedRead(
        response=ResponseRead.model_validate(response),
        evaluation=EvaluationRead.model_validate(evaluation),
        feedback=FeedbackRead.model_validate(feedback),
        skill_scores=[],
    )


class TranscribeAudioResponse(BaseModel):
    transcript: str
    audio_url: str


@router.post(
    "/transcribe-audio",
    response_model=TranscribeAudioResponse,
    status_code=status.HTTP_200_OK,
)
async def transcribe_audio(
    audio: UploadFile = File(
        ..., description="Learner's recorded audio (webm, mp3, wav, ogg, m4a)"
    ),
    language: str = Form(default="en"),
    _current_user: User = Depends(get_current_user),
) -> TranscribeAudioResponse:
    """Transcribe learner-recorded audio for a speaking task.

    Flow:
      1. Read uploaded audio bytes.
      2. Save to disk under the TTS static-file root so it is retrievable later
         (for re-evaluation or audit). Path: user-recordings/<sha256[:16]>.webm
      3. Transcribe via the cached STT service (OpenAI Whisper-1).
      4. Return transcript text + the public audio URL.

    The public URL is constructed from `TTS_PUBLIC_URL_PREFIX` so it is
    served by the existing StaticFiles mount in main.py without any extra
    configuration.

    Errors:
      400 — empty or malformed audio
      413 — audio over 25 MB (Whisper hard limit)
      502 — STT provider failure
    """
    from app.ai.stt import get_default_stt_service
    from app.ai.stt.exceptions import STTError, STTPayloadTooLarge, STTValidationError

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio upload.")

    # Derive a stable filename from the content hash (deduplicate re-uploads).
    content_hash = hashlib.sha256(audio_bytes).hexdigest()[:16]
    original_ext = Path(audio.filename or "recording.webm").suffix or ".webm"
    filename_on_disk = f"{content_hash}{original_ext}"

    # Save under the TTS cache root (already mounted as /audio in main.py).
    recordings_dir = Path(settings.TTS_CACHE_DIR).resolve() / "user-recordings"
    recordings_dir.mkdir(parents=True, exist_ok=True)
    audio_path = recordings_dir / filename_on_disk
    if not audio_path.exists():
        audio_path.write_bytes(audio_bytes)
        logger.info(
            "[transcribe_audio] saved %d bytes → %s", len(audio_bytes), audio_path
        )
    else:
        logger.debug("[transcribe_audio] cache hit for %s", filename_on_disk)

    audio_url = f"{settings.TTS_PUBLIC_URL_PREFIX}/user-recordings/{filename_on_disk}"

    # Transcribe via the STT service.
    service = get_default_stt_service()
    try:
        result = await service.transcribe(
            audio_bytes=audio_bytes,
            filename=audio.filename or filename_on_disk,
            language=language,
            with_timestamps=False,
        )
    except STTPayloadTooLarge as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except STTValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except STTError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return TranscribeAudioResponse(
        transcript=result["text"],
        audio_url=audio_url,
    )