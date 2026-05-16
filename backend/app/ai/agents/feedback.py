"""Agent 3 — Feedback Agent.

Generates human-readable corrective feedback for a learner.

Input  : original task + user's answer + evaluation report
Output : structured JSON matching FeedbackOutput schema
Rule   : Never says "Good job!" alone. Every praise must be followed
         by a specific correction.

Implementation: LLM-backed via the unified `app.ai.llm` client. The
client gives us retries, LangSmith tracing, exception translation, and
usage logging for free — this file just owns the prompt + schema.

The single public entry point is `generate_feedback(...)`.
"""

import json
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.ai.llm import LLMError, LLMValidationError, get_default_llm_client


# ---------------------------------------------------------------------------
# 1. OUTPUT SCHEMA — what we force the LLM to return
# ---------------------------------------------------------------------------
class ErrorExplanation(BaseModel):
    """One mistake, fully explained for the learner."""

    question_id: str = Field(description="e.g 'Q1', 'Q2'")
    user_answer: str = Field(description="What the user wrote")
    correct_answer: str = Field(description="The right answer")
    correction: str | None = Field(
        default=None,
        description="Corrected phrase or sentence when the evaluation report provides one",
    )
    error_type: str = Field(description="Plain-English reason, 1-2 sentences")
    why_wrong: str = Field(description="Plain-English reason, 1-2 sentences")
    rule: str = Field(description="The grammar/usage rule in simple words")
    memory_tip: str = Field(description="A short trick to remember it")


class FeedbackOutput(BaseModel):
    """Full feedback payload — saved into Feedback.body JSONB."""

    overall_message: str = Field(
        description=(
            "2-3 sentences. Acknowledge effort + name the main weakness. "
            "Never end with empty praise"
        )
    )
    errors: list[ErrorExplanation] = Field(
        description="One entry per wrong answer. Empty list if all correct."
    )
    score: int = Field(ge=0, le=100, description="Percentage 0-100")
    overall_level: Literal["needs_work", "okay", "good", "excellent"]
    practice_suggestion: str = Field(
        description="One concrete next step (e.g. 'Write 5 past-tense sentences')"
    )


# ---------------------------------------------------------------------------
# 2. SYSTEM PROMPT — agent personality + rules (constant per call)
# ---------------------------------------------------------------------------
FEEDBACK_SYSTEM_PROMPT = """\
You are a strict but kind English communication coach. You give feedback
to non-native English learners on their task answers.

You speak like a mentor who knows the learner's real-life context — not
like a textbook. When a lesson_context or learner personalisation is
provided, tie your feedback back to the situations the learner actually
faces (e.g. "in your next standup…", "when you introduce yourself on
campus…"). When it's not provided, stay neutral and encouraging.

YOUR RULES (follow exactly):
1. NEVER write empty praise like "Good job!" or "Well done!" alone.
   Every positive comment must be followed by a specific correction or tip.
2. Be FACTUAL and SPECIFIC. Point to the exact word or phrase that is wrong.
3. Use SIMPLE English. The learner is not a native speaker.
4. For each error, explain:
   - what is wrong
   - why it is wrong (the rule)
   - a small memory trick to remember the rule
5. End with ONE concrete practice suggestion. Not vague advice. Anchor it
   in the learner's lesson_context or domain whenever possible.
6. If all answers are correct, still give one tip to push the learner
   to the next level — phrased for their real-life context when known.
7. For error_spotting reports:
   - false_positive: explain that the sentence was already correct.
   - false_negative: explain what the learner missed, using correction
     and explanation from the evaluation report.
   - wrong_error_type: say the learner correctly spotted an error, but
     chose the wrong grammar label.
   - Include correction when the evaluation report provides it.
8. For open_text writing reports (task_type = curriculum_grammar_open_text):
   - The evaluation report contains "main_mistakes" (top mistakes across all items)
     and per-question "mistakes" lists with specific grammar errors.
   - Create one ErrorExplanation entry per item that has non-empty "mistakes".
   - question_id: use the item number (e.g. "Item 1", "Item 2").
   - user_answer: the learner's full written answer for that item.
   - correct_answer: the sample_answer from that item in the task.
   - Build why_wrong and rule from the specific mistakes listed.
   - Acknowledge the subskill_score (if present) in overall_message
     (e.g. "Grammar score: 7/10").
9. For grammar speaking reports (task_type = curriculum_grammar_speak):
   - Use each transcript as the user_answer and each sample response as
     correct_answer.
   - Build feedback from the per-question "mistakes" and the target grammar rule.
   - Mention the grammar speaking score if subskill_score is present.

You will receive:
- The original task (passage + questions)
- The user's answers
- An evaluation report (which answers are right/wrong, error types,
  and for writing tasks: subskill_score, main_mistakes, per-item mistakes)

Return your response in the required JSON schema. Nothing else.
"""


# ---------------------------------------------------------------------------
# 3. HUMAN MESSAGE TEMPLATE — formats the per-call data
# ---------------------------------------------------------------------------
def _format_personalisation_block(
    *,
    structured_personalisation: dict[str, Any] | None,
    lesson_context: str | None,
) -> str:
    """Render the optional contextual block for the human message.

    Empty when no personalisation is available — caller-friendly defaults
    keep the prompt working for evaluations that pre-date personalisation.
    """
    if not structured_personalisation and not lesson_context:
        return ""
    lines = ["LEARNER CONTEXT (use to tailor tone, not to change scoring):"]
    if lesson_context:
        lines.append(f"- lesson_context: {lesson_context}")
    if structured_personalisation:
        source = structured_personalisation.get("extraction_source") or "llm"
        if source == "empty":
            lines.append("- personalisation: empty (use neutral encouragement)")
        else:
            domain = structured_personalisation.get("domain") or "general"
            contexts = structured_personalisation.get("communication_contexts") or []
            pain = structured_personalisation.get("pain_points") or []
            tone = structured_personalisation.get("tone_preference") or "neutral"
            lines.append(f"- domain: {domain}")
            lines.append(f"- tone: {tone}")
            if contexts:
                lines.append("- communication_contexts: " + ", ".join(contexts))
            if pain:
                lines.append("- pain_points: " + ", ".join(pain))
    return "\n".join(lines) + "\n\n"


def _build_human_message(
    task_content: dict,
    user_answers: dict,
    evaluation_report: dict,
    score: int,
    *,
    structured_personalisation: dict[str, Any] | None = None,
    lesson_context: str | None = None,
) -> str:
    """Format task + answers + eval into one message for the LLM."""
    personalisation_block = _format_personalisation_block(
        structured_personalisation=structured_personalisation,
        lesson_context=lesson_context,
    )
    return f"""\
{personalisation_block}ORIGINAL TASK:
{json.dumps(task_content, indent=2)}

USER's ANSWERS:
{json.dumps(user_answers, indent=2)}

EVALUATION REPORT:
{json.dumps(evaluation_report, indent=2)}

SCORE: {score}/100

Generate corrective feedback now.
"""


# ---------------------------------------------------------------------------
# 4. PUBLIC ENTRY POINT
# ---------------------------------------------------------------------------
async def generate_feedback(
    task_content: dict,
    user_answers: dict,
    evaluation_report: dict,
    score: int,
    *,
    structured_personalisation: dict[str, Any] | None = None,
    lesson_context: str | None = None,
) -> FeedbackOutput:
    """Call the Feedback Agent. Returns a validated FeedbackOutput.

    Uses the unified LLM client, so this call automatically gets:
      - 3-attempt retry on transient failures (timeout, rate limit, 5xx)
      - LangSmith tracing under project `ai-english-coach`
      - Token + cost logging at INFO level
      - Provider-error translation into our LLMError family

    `structured_personalisation` and `lesson_context` are optional. When
    provided, the agent uses them to make the tone contextual and
    motivational (e.g. "in your next standup…"). They have NO effect on
    scoring — that comes from the evaluation_report.

    Raises:
        LLMValidationError: the LLM returned content that didn't match
            the FeedbackOutput schema (very rare with structured output).
        LLMError: any other provider failure (timeout, auth, rate limit).
    """
    client = get_default_llm_client()
    human_message = _build_human_message(
        task_content,
        user_answers,
        evaluation_report,
        score,
        structured_personalisation=structured_personalisation,
        lesson_context=lesson_context,
    )

    try:
        result = await client.generate_structured(
            system_prompt=FEEDBACK_SYSTEM_PROMPT,
            user_prompt=human_message,
            output_model=FeedbackOutput,
        )
    except (LLMValidationError, LLMError):
        # Re-raise unchanged — caller (FeedbackService) maps these to
        # the right HTTP status. Don't wrap in a generic exception.
        raise

    return result
