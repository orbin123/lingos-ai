"""AI debug routes.

Lightweight endpoints for verifying the AI layer works end-to-end.
Mounted under /debug/ai.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.llm import get_default_llm_client
from app.ai.tts import (
    SynthesisResult,
    TTSError,
    get_default_tts_service,
)

router = APIRouter(prefix="/debug/ai", tags=["debug"])


# ---------------------------------------------------------------------------
# LLM ping
# ---------------------------------------------------------------------------
@router.get("/ping")
async def ping_llm() -> dict[str, str]:
    """Smoke test the LLM client.

    Sends one prompt to OpenAI and returns the reply. Useful for:
      - confirming OPENAI_API_KEY is set + valid
      - confirming LangSmith trace shows up under project
        'ai-english-coach'
      - sanity-checking the unified client after a deploy

    Safe to leave in production — it's a single short call.
    """
    client = get_default_llm_client()
    reply = await client.generate_text(
        system_prompt="You are a terse echo bot.",
        user_prompt="Say 'LangSmith trace working' in 5 words exactly.",
    )
    return {"reply": reply}


# ---------------------------------------------------------------------------
# TTS synthesize (debug)
# ---------------------------------------------------------------------------
class TTSRequest(BaseModel):
    """Body for /debug/ai/tts/synthesize."""
    text: str = Field(min_length=1, max_length=4000)
    voice: str | None = Field(
        default=None,
        description=(
            "Optional voice override. gpt-4o-mini-tts supports: "
            "alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, "
            "shimmer, verse."
        ),
    )
    speed: float = Field(default=1.0, ge=0.25, le=4.0)
    style_instructions: str | None = Field(
        default=None,
        description=(
            "Free-form style guidance, e.g. 'speak slowly and warmly'. "
            "Only used by gpt-4o-mini-tts."
        ),
    )


@router.post("/tts/synthesize")
async def tts_synthesize(req: TTSRequest) -> SynthesisResult:
    """Synthesize one short audio clip and return the URL.

    Useful for:
      - verifying OpenAI TTS is wired up
      - watching cache_hit flip from False -> True on the second call
      - copying the returned audio_url into a browser to hear the result

    First call:  OpenAI is hit, audio written to disk, cache_hit=False.
    Repeat call (same text+voice+speed+instructions): cache_hit=True,
    no provider charge.
    """
    service = get_default_tts_service()
    try:
        result = await service.synthesize(
            text=req.text,
            voice=req.voice,
            speed=req.speed,
            style_instructions=req.style_instructions,
        )
    except TTSError as exc:
        # 502: provider failed. We surface the message — debug-only,
        # safe to leak provider error text here.
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return result
