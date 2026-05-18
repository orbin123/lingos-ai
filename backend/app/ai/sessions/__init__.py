"""LLM-driven agents for the new sessions flow.

Three concrete implementations, one per Protocol defined in
`app.modules.sessions.{evaluator,feedback_generator,task_generator}`:

  - `LLMEvaluator`        → Evaluator
  - `LLMFeedbackGenerator` → FeedbackGenerator
  - `LLMTaskGenerator`     → TaskGenerator

`build_default_agents()` returns a wired trio for production routes. Tests
inject the Stub* variants directly.
"""

from app.ai.sessions.factory import build_default_agents
from app.ai.sessions.llm_evaluator import LLMEvaluator
from app.ai.sessions.llm_feedback import LLMFeedbackGenerator
from app.ai.sessions.llm_task_generator import LLMTaskGenerator

__all__ = [
    "LLMEvaluator",
    "LLMFeedbackGenerator",
    "LLMTaskGenerator",
    "build_default_agents",
]
