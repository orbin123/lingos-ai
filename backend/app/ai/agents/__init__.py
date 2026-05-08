"""The agent system for LingosAI.

Each agent lives in its own file, has a single responsibility, and exposes
a small public surface so callers do not need to know whether the
implementation is rule-based, LLM-based, or a future swap.

    Agent 0 — Teaching         →  teacher.generate_teaching_turn()
    Agent 1 — Task Generator   →  task_generator.generate_task()
    Agent 2 — Evaluator        →  evaluator.EvaluationService
    Agent 3 — Feedback         →  feedback.generate_feedback()

Re-exporting the public symbols here lets callers do the clean import:

    from app.ai.agents import generate_feedback, EvaluationService
"""

from app.ai.agents.evaluator import EvaluationService
from app.ai.agents.feedback import FeedbackOutput, generate_feedback
from app.ai.agents.task_generator import generate_task
from app.ai.agents.teacher import TeachingOutput, generate_teaching_turn

__all__ = [
    "EvaluationService",
    "FeedbackOutput",
    "TeachingOutput",
    "generate_feedback",
    "generate_task",
    "generate_teaching_turn",
]
