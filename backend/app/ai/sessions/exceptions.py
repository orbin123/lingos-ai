"""Typed errors for the LLM-backed sessions agents."""

from __future__ import annotations


class TaskGenerationError(Exception):
    """Base class for task-generation failures."""


class TaskGenerationFailed(TaskGenerationError):
    """The LLM could not produce a valid task payload for an archetype.

    Raised after the generator has exhausted its retries. The orchestrator /
    WebSocket layer surfaces this as a clean ``type="error"`` event rather than
    silently substituting off-theme placeholder content.
    """

    def __init__(self, archetype_id: str, detail: str) -> None:
        self.archetype_id = archetype_id
        self.detail = detail
        super().__init__(
            f"task generation failed for archetype {archetype_id!r}: {detail}"
        )
