"""AI debug routes.

Lightweight endpoints for verifying the LLM layer works end-to-end
(API key valid, network reachable, LangSmith tracing flowing).
Mounted under /debug/ai.
"""

from fastapi import APIRouter

from app.ai.llm import get_default_llm_client

router = APIRouter(prefix="/debug/ai", tags=["debug"])


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
