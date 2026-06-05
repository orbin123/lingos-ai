"""Strict chat-session payload contracts + the Archetype Contract Registry.

This package is the schema boundary between the LLM agents and the reusable
chat widgets. Agent output is validated/normalized into these models before the
orchestrator emits it; a payload that validates here is guaranteed renderable.

  - ``base`` / ``task_payloads`` — task-agent output, one model per render family.
  - ``evaluation`` — evaluation-agent output + final scorecard.
  - ``feedback`` — feedback-agent + RAG output.
  - ``registry`` — archetype_id → (widgets, agents, schemas).
"""

from __future__ import annotations

from app.modules.sessions.contracts.agent_inputs import (
    EvaluatorAgentInput,
    FeedbackAgentInput,
    TaskGenAgentInput,
    TeacherAgentInput,
    build_agent_input,
)
from app.modules.sessions.contracts.evaluation import (
    ActivityEvaluationOutput,
    OverallScorecard,
    PronunciationAssessment,
    ScorecardActivity,
)
from app.modules.sessions.contracts.feedback import (
    ActivityFeedbackOutput,
    FeedbackMistake,
    RagFeedbackOutput,
)
from app.modules.sessions.contracts.registry import (
    ARCHETYPE_CONTRACTS,
    EVALUATION_WIDGETS,
    FEEDBACK_WIDGETS,
    KNOWN_TASK_WIDGETS,
    ArchetypeContract,
    get_contract,
)
from app.modules.sessions.contracts.projection import (
    ContractValidationError,
    contract_widgets,
    project_evaluation,
    project_feedback,
    project_task_payload,
)
from app.modules.sessions.contracts.validation import (
    infer_listen_inner_widget,
    normalize_task_content,
    validate_and_project_task_content,
)
from app.modules.sessions.contracts.task_payloads import (
    DictationPayload,
    ErrorCorrectionPayload,
    ErrorSpottingPayload,
    FillBlanksPayload,
    McqPayload,
    OpenTextPayload,
    ReadStructurePayload,
    SpeakingPayload,
    TfngPayload,
    TransformPayload,
)

__all__ = [
    # registry
    "ArchetypeContract",
    "ARCHETYPE_CONTRACTS",
    "get_contract",
    "KNOWN_TASK_WIDGETS",
    "EVALUATION_WIDGETS",
    "FEEDBACK_WIDGETS",
    # projection (schema boundary)
    "ContractValidationError",
    "contract_widgets",
    "project_task_payload",
    "project_evaluation",
    "project_feedback",
    "infer_listen_inner_widget",
    "normalize_task_content",
    "validate_and_project_task_content",
    # task payloads
    "FillBlanksPayload",
    "McqPayload",
    "TfngPayload",
    "ErrorSpottingPayload",
    "DictationPayload",
    "OpenTextPayload",
    "TransformPayload",
    "ErrorCorrectionPayload",
    "ReadStructurePayload",
    "SpeakingPayload",
    # evaluation
    "ActivityEvaluationOutput",
    "OverallScorecard",
    "ScorecardActivity",
    "PronunciationAssessment",
    # feedback
    "ActivityFeedbackOutput",
    "FeedbackMistake",
    "RagFeedbackOutput",
    # agent inputs (service→agent boundary)
    "TeacherAgentInput",
    "TaskGenAgentInput",
    "EvaluatorAgentInput",
    "FeedbackAgentInput",
    "build_agent_input",
]
