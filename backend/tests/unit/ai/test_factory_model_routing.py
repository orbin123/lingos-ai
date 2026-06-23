"""Phase 2 — per-agent model routing in the sessions factory.

Task generation rides its OWN reasoning-model client (gpt-5 at high effort)
while the evaluator + feedback share the fast non-reasoning interactive default.
gpt-5 ignores ``temperature``, so the lever for generation quality is the model +
``reasoning_effort``, not temperature — these tests pin that wiring so a future
config change can't silently collapse task-gen back onto the interactive model.
"""

from __future__ import annotations

from app.ai.sessions import factory
from app.core.config import Settings, settings


def test_taskgen_config_defaults_are_gpt5_high() -> None:
    """The committed defaults route task generation to gpt-5 at high effort and
    keep the interactive agents on the fast non-reasoning model — independent of
    any local .env override (asserted against the class field defaults)."""
    fields = Settings.model_fields
    assert fields["OPENAI_TASKGEN_MODEL"].default == "gpt-5"
    assert fields["OPENAI_TASKGEN_REASONING_EFFORT"].default == "high"
    assert fields["OPENAI_CHAT_MODEL"].default == "gpt-4.1-mini"


def test_task_generator_uses_dedicated_reasoning_client() -> None:
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
        # A reasoning task-gen model (the default gpt-5) carries the effort knob;
        # temperature is dropped for it, so effort is the only lever.
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
