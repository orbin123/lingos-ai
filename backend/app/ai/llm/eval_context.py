"""Per-request correlation context for AI observability.

A single learner action (e.g. submitting an activity) fans out into several
LLM calls — evaluator, feedback, mentor note. We want every operational
`AIRequestLog` row from that action to share one ``trace_id`` (and carry the
acting ``user_id``) without threading those values through every collaborator
method signature.

This module keeps that context in a :class:`contextvars.ContextVar`. The caller
sets it once at the top of the action; the ``LoggingLLMClient`` reads it when it
records a row. ``contextvars`` is asyncio-aware: each task gets its own copy, so
concurrent requests never see each other's trace id.
"""

from __future__ import annotations

import contextvars
from dataclasses import dataclass


@dataclass(frozen=True)
class EvalContext:
    """Correlation data attached to the current async context."""

    trace_id: str | None = None
    user_id: int | None = None


_EVAL_CONTEXT: contextvars.ContextVar[EvalContext] = contextvars.ContextVar(
    "ai_eval_context", default=EvalContext()
)


def get_eval_context() -> EvalContext:
    """Return the context for the current async task (empty if unset)."""
    return _EVAL_CONTEXT.get()


def set_eval_context(
    *, trace_id: str | None, user_id: int | None
) -> contextvars.Token[EvalContext]:
    """Set the context and return a token for :func:`reset_eval_context`."""
    return _EVAL_CONTEXT.set(EvalContext(trace_id=trace_id, user_id=user_id))


def reset_eval_context(token: contextvars.Token[EvalContext]) -> None:
    """Restore the context to its value before the matching ``set`` call."""
    _EVAL_CONTEXT.reset(token)
