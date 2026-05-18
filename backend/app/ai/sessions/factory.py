"""Factory for wiring the production LLM-driven agents.

Routes call `build_default_agents()` and pass the trio to `SessionService`.
The LLM client is instantiated once per request (cheap — it's a wrapper
around the langchain_openai object). Tests bypass this entirely and inject
the Stub* agents.
"""

from __future__ import annotations

from app.ai.llm.interface import ILLMClient
from app.ai.llm.openai_client import OpenAILLMClient
from app.ai.sessions.llm_evaluator import LLMEvaluator
from app.ai.sessions.llm_feedback import LLMFeedbackGenerator
from app.ai.sessions.llm_task_generator import LLMTaskGenerator
from app.modules.sessions.evaluator import Evaluator
from app.modules.sessions.feedback_generator import FeedbackGenerator
from app.modules.sessions.task_generator import TaskGenerator


def build_default_agents(
    *,
    llm: ILLMClient | None = None,
) -> tuple[Evaluator, FeedbackGenerator, TaskGenerator]:
    """Return (evaluator, feedback_generator, task_generator) wired to the LLM.

    Pass `llm` to override the default OpenAI client (mainly for tests
    or for swapping providers in environment-specific code paths).
    """
    client = llm or OpenAILLMClient()
    return (
        LLMEvaluator(client),
        LLMFeedbackGenerator(client),
        LLMTaskGenerator(client),
    )
