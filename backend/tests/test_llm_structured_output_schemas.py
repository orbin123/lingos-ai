"""Guardrails for OpenAI structured-output JSON schemas used in task generation."""

from app.ai.sessions.llm_task_generator import (
    ErrorCorrectionTask,
    ErrorSpottingTaskLLM,
    TaskGenOutput,
)
from app.tasks.schemas.llm_output_schemas import (
    FillInBlanksTaskLLM,
    assert_openai_structured_schema,
)


_LLM_BOUND_MODELS = (
    FillInBlanksTaskLLM,
    TaskGenOutput,
    ErrorCorrectionTask,
    ErrorSpottingTaskLLM,
)


def test_llm_task_generation_schemas_are_openai_compatible() -> None:
    for model in _LLM_BOUND_MODELS:
        assert_openai_structured_schema(model)
