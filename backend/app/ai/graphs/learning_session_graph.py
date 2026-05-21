"""Compiled LangGraph for the chat-driven learning session.

The chat flow is driven turn-by-turn from the WebSocket layer — this
compiled graph exists for tests and for documenting the high-level flow:

    plan_loader (placeholder) -> teach -> task_delivery -> followup -> END

Evaluation and feedback DB writes are owned by the V2 sessions service
(`SessionService.submit_activity`), not by graph nodes — so neither node
is present here. The service composes the chat-side feedback message from
the V2 feedback row at the call site.
"""

from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.ai.graphs.nodes import (
    followup_node,
    task_delivery_node,
    teach_node,
)
from app.ai.graphs.state import LearningSessionState


def _route_after_teach(state: LearningSessionState) -> str:
    return "task_delivery" if state.get("understanding_confirmed") else "teach"


def _route_after_followup(state: LearningSessionState) -> str:
    return "end" if state.get("phase") == "ended" else "teach"


async def _plan_loader_passthrough(state: LearningSessionState) -> dict:
    """Structural placeholder for plan_loader in the compiled graph.

    The actual plan loading needs a DB session and runs inside the
    WebSocket layer (see `LearningSessionService.initial_messages*`).
    """
    return {}


def build_graph() -> StateGraph:
    graph: StateGraph = StateGraph(LearningSessionState)

    graph.add_node("plan_loader", _plan_loader_passthrough)
    graph.add_node("teach", teach_node)
    graph.add_node("task_delivery", task_delivery_node)
    graph.add_node("followup", followup_node)

    graph.add_edge(START, "plan_loader")
    graph.add_edge("plan_loader", "teach")
    graph.add_conditional_edges(
        "teach",
        _route_after_teach,
        {"teach": "teach", "task_delivery": "task_delivery"},
    )
    graph.add_edge("task_delivery", "followup")
    graph.add_conditional_edges(
        "followup",
        _route_after_followup,
        {"end": END, "teach": "teach"},
    )

    return graph


@lru_cache(maxsize=1)
def get_learning_session_graph():
    """Return a compiled graph (cached as a process-wide singleton)."""
    return build_graph().compile()
