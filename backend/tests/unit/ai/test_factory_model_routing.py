"""Phase 2 — per-agent model routing in the sessions factory.

Task generation rides its OWN client (``OPENAI_TASKGEN_MODEL``, the cheap
``gpt-4o-mini`` default) while the evaluator + feedback share the interactive
default (``OPENAI_CHAT_MODEL``). These tests pin that wiring so a future config
change can't silently collapse task-gen back onto the interactive client.
"""

from __future__ import annotations

from app.ai.sessions import factory
from app.core.config import Settings, settings


def test_taskgen_config_defaults() -> None:
    """The committed defaults keep task generation on the cheap non-reasoning
    gpt-4o-mini and the interactive agents on gpt-4.1-mini — independent of any
    local .env override (asserted against the class field defaults)."""
    fields = Settings.model_fields
    assert fields["OPENAI_TASKGEN_MODEL"].default == "gpt-4o-mini"
    assert fields["OPENAI_CHAT_MODEL"].default == "gpt-4.1-mini"


def test_task_generator_uses_dedicated_client() -> None:
    """build_default_agents wires the task generator to the task-gen client and
    the evaluator/feedback to the shared interactive default."""
    factory._shared_default_client.cache_clear()
    factory._shared_taskgen_client.cache_clear()
    try:
        evaluator, feedback, task_gen = factory.build_default_agents()

        gen_inner = task_gen.llm._inner
        eval_inner = evaluator.llm._inner
        fb_inner = feedback.llm._inner

        # Task generator: dedicated client on the configured task-gen model.
        assert gen_inner.model == settings.OPENAI_TASKGEN_MODEL
        # Only a reasoning task-gen model carries the effort knob; the default
        # gpt-4o-mini is non-reasoning, so this branch is skipped for it.
        if gen_inner._is_reasoning:
            assert (
                gen_inner._reasoning_effort == settings.OPENAI_TASKGEN_REASONING_EFFORT
            )

        # Evaluator + feedback share the fast interactive default client.
        assert eval_inner is fb_inner
        assert eval_inner.model == settings.OPENAI_CHAT_MODEL

        # The Phase 2 split: task-gen does NOT ride the interactive client.
        assert gen_inner is not eval_inner
    finally:
        factory._shared_default_client.cache_clear()
        factory._shared_taskgen_client.cache_clear()
