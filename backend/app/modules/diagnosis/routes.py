"""Diagnosis HTTP routes."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.ai.stt import (
    STTError,
    STTPayloadTooLarge,
    STTValidationError,
    get_default_stt_service,
)
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.repository import UserProfileRepository
from app.modules.diagnosis.exceptions import (
    DiagnosisAlreadyCompleted,
    DiagnosisInvalidPayload,
)
from app.modules.diagnosis.schemas import (
    DiagnosisFeedbackOut,
    DiagnosisSubmitRequest,
    DiagnosisSubmitResponse,
    TranscribeResponse,
    WeakSkillExplanationOut,
)
from app.modules.diagnosis.service import DiagnosisService

router = APIRouter()

# Floor used to satisfy `TranscribeResponse.duration_seconds > 0` if Whisper
# ever returns 0.0 for very short audio. Real recordings are always > 0.01s,
# so this clamp only fires on degenerate inputs and keeps us from 500ing.
_MIN_REPORTED_DURATION_S = 0.01


@router.post("/start", status_code=status.HTTP_200_OK)
def start_diagnosis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Prepare the current user to enter the diagnosis flow.

    This supports retakes. Existing progress rows are left untouched; the
    next diagnosis submission updates the current skill scores.
    """
    profile_repo = UserProfileRepository(db)
    profile = profile_repo.get_by_user_id(current_user.id)
    if profile is None:
        profile = profile_repo.create_default(current_user.id)

    profile.diagnosis_completed = False
    db.commit()
    return {"next": "/diagnosis"}


@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    status_code=status.HTTP_200_OK,
)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio recording from the read-aloud step"),
    current_user: User = Depends(get_current_user),
) -> TranscribeResponse:
    """Transcribe a read-aloud audio recording via the shared STT service.

    The STT service (`app.ai.stt`) handles:
      - calling OpenAI Whisper with `verbose_json` so duration is real,
        not estimated from byte size
      - requesting word timestamps so we can do pacing + mismatch analysis
      - 25 MB pre-flight size check (raises STTPayloadTooLarge)
      - hash-based caching — re-uploads of the same recording are free
      - retries on transient OpenAI failures

    We deliberately do NOT validate `audio.content_type` here. Browser
    MIME labels are unreliable (some clients send `application/octet-stream`
    for valid webm), and Whisper detects the format from the file's
    extension via the multipart filename. Filename is what matters.

    Returns: transcript text + duration in seconds.
    Auth: Bearer token required.
    """
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is empty.",
        )

    # Whisper sniffs the format from the filename extension, so we always
    # hand it one. If the upload didn't carry a name, default to .webm —
    # the format the diagnosis frontend records in via MediaRecorder.
    filename = audio.filename or "recording.webm"

    service = get_default_stt_service()
    try:
        result = await service.transcribe(
            audio_bytes=audio_bytes,
            filename=filename,
            language="en",
            with_timestamps=True,
        )
    except STTPayloadTooLarge as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc
    except STTValidationError as exc:
        # Empty bytes / bad filename / unsupported format — caller's fault.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except STTError as exc:
        # Provider-side failure (timeout, rate limit, 5xx). 502 keeps the
        # original signal: "upstream is the problem, not your request."
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Transcription failed: {exc}",
        ) from exc

    duration = max(result["duration_seconds"], _MIN_REPORTED_DURATION_S)
    return TranscribeResponse(
        transcript=result["text"].strip(),
        duration_seconds=round(duration, 2),
        words=result["words"] or [],
    )


@router.post(
    "/submit",
    response_model=DiagnosisSubmitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_diagnosis(
    payload: DiagnosisSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DiagnosisSubmitResponse:
    """Submit diagnosis answers, compute skill scores, and return AI feedback.

    Auth: Bearer token required.
    """
    try:
        skill_scores, ai_feedback, read_aloud_analysis = await DiagnosisService(db).run_diagnosis(
            user_id=current_user.id,
            payload=payload,
        )
    except DiagnosisAlreadyCompleted:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Diagnosis already completed for this user.",
        )
    except DiagnosisInvalidPayload as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    weakest = sorted(skill_scores.items(), key=lambda kv: kv[1])[:2]
    weakest_skill_names = [name for name, _ in weakest]

    feedback_out = DiagnosisFeedbackOut(
        estimated_level_label=ai_feedback.estimated_level_label,
        summary=ai_feedback.summary,
        weak_skill_explanations=[
            WeakSkillExplanationOut(
                skill_name=e.skill_name,
                what_it_means=e.what_it_means,
                why_it_matters=e.why_it_matters,
                what_to_expect=e.what_to_expect,
            )
            for e in ai_feedback.weak_skill_explanations
        ],
        motivation=ai_feedback.motivation,
        first_week_focus=ai_feedback.first_week_focus,
    )

    return DiagnosisSubmitResponse(
        skill_scores=skill_scores,
        weakest_skills=weakest_skill_names,
        feedback=feedback_out,
        read_aloud_analysis=read_aloud_analysis,
    )
