"""Learner response routes.

`POST /responses/transcribe-audio` — used by the SpeakRecordWidget on the
session/chat page. The widget records a blob, posts it here, and uses the
returned transcript + audio_url in its local `recordings[]` answer state.
The transcript is what the evaluator + feedback generator then grade on
submit.
"""

from __future__ import annotations

import hashlib
import logging
import time

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.ai.storage import get_default_blob_storage
from app.ai.stt import get_default_stt_service
from app.ai.stt.exceptions import (
    STTError,
    STTPayloadTooLarge,
    STTValidationError,
)
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/responses", tags=["responses"])


class TranscribeResponse(BaseModel):
    transcript: str
    audio_url: str


_AUDIO_EXTENSIONS = {
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/mp4": ".mp4",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/flac": ".flac",
}


def _extension_for(filename: str, content_type: str | None) -> str:
    name = (filename or "").lower()
    for ext in (".webm", ".ogg", ".mp4", ".m4a", ".mp3", ".wav", ".flac"):
        if name.endswith(ext):
            return ext
    if content_type:
        primary = content_type.split(";", 1)[0].strip().lower()
        if primary in _AUDIO_EXTENSIONS:
            return _AUDIO_EXTENSIONS[primary]
    return ".webm"


@router.post("/transcribe-audio", response_model=TranscribeResponse)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Learner audio recording."),
    language: str = Form(default="en"),
    current_user: User = Depends(get_current_user),
) -> TranscribeResponse:
    """Persist the uploaded clip and return its Whisper transcript + URL.

    The widget uses `audio_url` to play back the learner's clip alongside
    feedback after the activity is submitted.
    """
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio upload.")

    ext = _extension_for(audio.filename or "", audio.content_type)

    digest = hashlib.sha256(audio_bytes).hexdigest()[:24]
    storage_key = f"learner-{current_user.id}-{int(time.time() * 1000)}-{digest}{ext}"

    storage = get_default_blob_storage()
    try:
        stored = await storage.put(
            key=storage_key,
            data=audio_bytes,
            content_type=audio.content_type or "audio/webm",
        )
    except Exception as exc:
        logger.exception("Failed to persist learner audio key=%s", storage_key)
        raise HTTPException(
            status_code=500, detail="Could not save audio."
        ) from exc

    stt = get_default_stt_service()
    try:
        result = await stt.transcribe(
            audio_bytes=audio_bytes,
            filename=audio.filename or f"recording{ext}",
            language=language,
            with_timestamps=False,
        )
    except STTPayloadTooLarge as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except STTValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except STTError as exc:
        logger.warning("STT failed for key=%s: %s", storage_key, exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    transcript = (result.get("text") or "").strip()
    return TranscribeResponse(transcript=transcript, audio_url=stored["public_url"])
