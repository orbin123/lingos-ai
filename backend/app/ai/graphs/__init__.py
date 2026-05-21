"""LangGraph orchestration for chat-driven learning sessions."""

from app.ai.graphs.state import LearningSessionState, PhaseType


def get_learning_session_graph():
    """Load the LangGraph workflow lazily.

    Some tests import lightweight graph nodes without needing the optional
    LangGraph workflow package path. Lazy import keeps those imports from
    failing when dependency versions drift.
    """
    from app.ai.graphs.learning_session_graph import (
        get_learning_session_graph as _get_learning_session_graph,
    )

    return _get_learning_session_graph()


__all__ = ["get_learning_session_graph", "LearningSessionState", "PhaseType"]
