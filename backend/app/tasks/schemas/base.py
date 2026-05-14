"""
Base types shared across all task templates.

Every sub-skill template file (grammar_templates.py, vocab_templates.py, etc.)
imports from here. Keeps enums and shared classes in ONE place — change once,
update everywhere.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────
# Core Enums — the system's vocabulary
# ─────────────────────────────────────────────────────────────


class SubSkill(str, Enum):
    """The 7 sub-skills tracked by LingosAI."""

    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    PRONUNCIATION = "pronunciation"
    FLUENCY = "fluency"
    THOUGHT_ORGANIZATION = "thought_organization"
    LISTENING = "listening"
    TONE = "tone"


class Activity(str, Enum):
    """The 4 core activities — how a sub-skill is practiced."""

    READ = "read"
    WRITE = "write"
    LISTEN = "listen"
    SPEAK = "speak"


class ScoringMethod(str, Enum):
    """Maps 1:1 to an evaluator strategy function.

    Each value is the name of an EvaluationService method:
      RULE_EXACT_MATCH      → evaluate_fill_in_blanks / mcq style exact matching
      RULE_SENTENCE_MATCH   → evaluate_sentence_engineering / normalized match
      RULE_PARTIAL_CREDIT   → evaluate_error_spotting (0.5/1.0 partial scores)
      LLM_OPEN_WRITING      → evaluate_open_text_writing
      LLM_SPEAKING_GRAMMAR  → evaluate_grammar_speaking
      LLM_PARAPHRASE_STUB   → evaluate_paraphrasing / evaluate_sentence_transformation
      SPEECH_API            → Azure pronunciation (future)
    """

    RULE_EXACT_MATCH = "rule_exact_match"
    RULE_SENTENCE_MATCH = "rule_sentence_match"
    RULE_PARTIAL_CREDIT = "rule_partial_credit"
    LLM_OPEN_WRITING = "llm_open_writing"
    LLM_SPEAKING_GRAMMAR = "llm_speaking_grammar"
    LLM_PARAPHRASE_STUB = "llm_paraphrase_stub"
    SPEECH_API = "speech_api"


class FeedbackStyle(str, Enum):
    """Controls which feedback prompt + payload shape is used.

    PER_ITEM_ERRORS    → list of {question_id, why_wrong, rule, memory_tip}
                          (fill_in_blanks, MCQ, error_spotting)
    HOLISTIC_WRITING   → overall_message + per_item errors with main_mistakes
                          (open_text, structured_essay, timed_text)
    SPEAKING_RUBRIC    → per-prompt mistakes + grammar_rule_used + overall
                          (speak_and_record, storyboard)
    """

    PER_ITEM_ERRORS = "per_item_errors"
    HOLISTIC_WRITING = "holistic_writing"
    SPEAKING_RUBRIC = "speaking_rubric"


class DifficultyTier(str, Enum):
    """Maps the 10 sub-levels into 3 generation tiers."""

    BEGINNER = "beginner"          # sub-levels 1-3 (A1, A2)
    INTERMEDIATE = "intermediate"  # sub-levels 4-6 (B1, B2 lower)
    ADVANCED = "advanced"          # sub-levels 7-10 (B2 upper, C1, C2)


# ─────────────────────────────────────────────────────────────
# Base Pydantic Model — every generated task inherits this
# ─────────────────────────────────────────────────────────────


class GeneratedTaskBase(BaseModel):
    """
    Base class for ALL LLM-generated task content.

    Subclasses live in each `*_templates.py` file (e.g. FillInBlanksTask).
    Every generated task carries metadata so the evaluator + frontend
    know what they're handling without parsing the whole content.
    """

    task_intro: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="Friendly 1–2 sentence intro shown to the user.",
    )
    estimated_time_minutes: int = Field(
        ..., ge=1, le=30, description="How long the task should take."
    )


# ─────────────────────────────────────────────────────────────
# Difficulty Modifier Map (shared default — templates can override)
# ─────────────────────────────────────────────────────────────


def difficulty_tier_for_sublevel(sub_level: int) -> DifficultyTier:
    """Map a sub-level (1–10) to a tier. Used by the Task Selector."""
    if sub_level <= 3:
        return DifficultyTier.BEGINNER
    if sub_level <= 6:
        return DifficultyTier.INTERMEDIATE
    return DifficultyTier.ADVANCED


# ─────────────────────────────────────────────────────────────
# Template Schema — Layer 1 (the static template definition)
# ─────────────────────────────────────────────────────────────


class TaskTemplate(BaseModel):
    """
    A reusable task template. Loaded into memory at app startup.

    The Task Generator agent picks one of these, fills in the prompt
    placeholders with user-specific data, sends to the LLM, then validates
    the LLM's response against `output_model`.
    """

    template_id: str = Field(..., description="Unique stable ID, e.g. 'grammar_read_fill_blanks_v1'")
    version: str = Field(default="1.0")
    sub_skill: SubSkill
    activity: Activity
    task_type: str = Field(..., description="Specific format, e.g. 'fill_in_blanks'")

    difficulty_range: tuple[int, int] = Field(
        default=(1, 10),
        description="Inclusive (min, max) sub-levels this template supports.",
    )
    estimated_time_minutes: int
    scoring_method: ScoringMethod
    feedback_style: FeedbackStyle

    llm_prompt_template: str = Field(
        ..., description="Prompt with {placeholders} the generator fills in."
    )
    output_model_name: str = Field(
        ..., description="Class name of the Pydantic model that validates LLM output."
    )

    evaluation_logic: dict[str, Any] = Field(
        default_factory=dict,
        description="Rules for how the evaluator scores responses.",
    )
    difficulty_modifiers: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Per-tier knobs (word counts, blank counts, vocab level, etc.)",
    )

    model_config = {"frozen": True}  # immutable — templates shouldn't mutate at runtime
