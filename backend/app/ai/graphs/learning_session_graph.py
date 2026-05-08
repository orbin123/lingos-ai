"""Compiled LangGraph for the chat-driven learning session.

Flow (high level — actual orchestration of which node runs is driven
by the WebSocket layer based on the incoming message type):

    teach_node ── if understanding_confirmed ──▶ task_delivery_node
        ▲                                              │
        └──────── else ─── teach_node (loop)           │
                                                       ▼
                                          (await user submission)
                                                       │
                                                       ▼
                                              evaluation_node
                                                       │
                                                       ▼
                                              feedback_node
                                                       │
                                                       ▼
                                              followup_node
                                                       │
                                          ┌────────────┼────────────┐
                                          ▼                         ▼
                                       END / ended            teach_node
"""

from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.ai.graphs.nodes import (
    evaluation_node,
    feedback_node,
    followup_node,
    task_delivery_node,
    teach_node,
)
from app.ai.graphs.state import LearningSessionState


def _route_after_teach(state: LearningSessionState) -> str:
    return "task_delivery" if state.get("understanding_confirmed") else "teach"


def _route_after_followup(state: LearningSessionState) -> str:
    return "end" if state.get("phase") == "ended" else "teach"


def build_graph() -> StateGraph:
    graph: StateGraph = StateGraph(LearningSessionState)

    graph.add_node("teach", teach_node)
    graph.add_node("task_delivery", task_delivery_node)
    graph.add_node("evaluation", evaluation_node)
    graph.add_node("feedback", feedback_node)
    graph.add_node("followup", followup_node)

    graph.add_edge(START, "teach")
    graph.add_conditional_edges(
        "teach",
        _route_after_teach,
        {"teach": "teach", "task_delivery": "task_delivery"},
    )
    graph.add_edge("task_delivery", "evaluation")
    graph.add_edge("evaluation", "feedback")
    graph.add_edge("feedback", "followup")
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
