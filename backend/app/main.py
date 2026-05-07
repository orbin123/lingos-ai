"""FastAPI application entry point."""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.ai.routes import router as ai_router
from app.core.config import settings
from app.modules.auth.routes import router as auth_router
from app.modules.curriculum.routes import router as curriculum_router
from app.modules.diagnosis.routes import router as diagnosis_router
from app.modules.progress.routes import router as progress_router
from app.modules.responses.routes import router as responses_router
from app.modules.subscriptions.routes import (
    subscription_router,
    users_router,
)
from app.modules.tasks.routes import router as tasks_router

load_dotenv("../.env")

app = FastAPI(
    title="LingosAI - English Tutor API",
    version='0.1.0',
    redirect_slashes=False,  # prevents 307 redirect on /auth/google/callback
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Static files: serve cached AI blobs written by LocalBlobStorage.
#
# Today that includes:
#   - TTS audio under /audio/<shard>/<key>.mp3
#   - image-generation outputs under /images/<shard>/<key>.png
#
# In production this would likely move to S3 / Cloudflare R2 with a CDN.
# For dev, StaticFiles is the simplest possible path: the same files
# `LocalBlobStorage` writes to disk become directly fetchable here.
# ---------------------------------------------------------------------------
_audio_root = Path(settings.TTS_CACHE_DIR).resolve()
_audio_root.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.TTS_PUBLIC_URL_PREFIX,
    StaticFiles(directory=_audio_root),
    name="audio",
)

_image_root = Path(settings.IMAGEGEN_CACHE_DIR).resolve()
_image_root.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.IMAGEGEN_PUBLIC_URL_PREFIX,
    StaticFiles(directory=_image_root),
    name="images",
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Liveness probe - confirms server is up."""
    return {"status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(diagnosis_router, prefix="/diagnosis", tags=["diagnosis"])
app.include_router(curriculum_router)
app.include_router(tasks_router)
app.include_router(responses_router)
app.include_router(progress_router)
app.include_router(ai_router)
app.include_router(subscription_router)
app.include_router(users_router)
