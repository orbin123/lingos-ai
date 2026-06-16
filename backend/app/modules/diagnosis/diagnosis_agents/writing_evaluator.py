"""Agent — Diagnosis Writing Evaluator.

Scores the learner's short free-writing answer from the diagnosis flow.
Called once by ``DiagnosisService`` for the writing mini-task.

Replaces the old word-count stub (``TextEvaluator``): a real LLM now reads
the writing and returns an honest quality score plus the three sub-dimension
scores the master scoring formula consumes.

Input  : the writing prompt id + the learner's response text
Output : DiagnosisWritingScores (structured JSON from the LLM)

Implementation: LLM-backed via the unified ``app.ai.llm`` client. Retries,
LangSmith tracing, and usage logging are handled by the client.
"""

from pydantic import BaseModel, Field

from app.ai.llm import LLMError, LLMValidationError, get_default_llm_client


# ---------------------------------------------------------------------------
# 1. OUTPUT SCHEMA — what the LLM must return
# ---------------------------------------------------------------------------


class DiagnosisWritingScores(BaseModel):
    """Structured writing assessment used by the diagnosis scoring formula.

    The three sub-scores are normalized to 0.0–1.0 because
    ``scoring.compute_skill_scores`` adds them straight onto the level/exposure
    base. ``writing_score`` is the human-facing 0–10 headline number.
    """

    writing_score: float = Field(
        ge=0.0,
        le=10.0,
        description=(
            "Overall writing quality on a 0–10 scale. Judge grammar, clarity, "
            "vocabulary, and how well the answer addresses the prompt. Be "
            "honest: a short or error-filled answer should score low."
        ),
    )
    expression_score: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "0.0–1.0. How clearly and coherently ideas are organised and "
            "connected (sentence flow, structure, logical order)."
        ),
    )
    vocabulary_score: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "0.0–1.0. Range and accuracy of word choice. Repetitive or very "
            "basic vocabulary scores low; varied, precise wording scores high."
        ),
    )
    tone_score: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "0.0–1.0. Appropriateness and naturalness of tone/register for "
            "the writing task."
        ),
    )


# ---------------------------------------------------------------------------
# 2. SYSTEM PROMPT
# ---------------------------------------------------------------------------

WRITING_EVALUATOR_SYSTEM_PROMPT = """\
You are an English writing examiner for LingosAI, an English-learning app.

You read one short free-writing answer from a learner's diagnostic test and
score it. The learner is a non-native English speaker describing their typical
day in a few sentences.

SCORING RULES:
1. Be HONEST and consistent. Do not be generous. A two-word answer, an
   off-topic answer, or an answer full of grammar errors must score low.
2. `writing_score` is the overall 0–10 quality (grammar + clarity + vocabulary
   + task completion).
3. `expression_score`, `vocabulary_score`, and `tone_score` are each on a
   0.0–1.0 scale and judge one dimension only.
4. Judge ONLY what is written. Do not invent strengths that are not there.

Return your answer in the required JSON schema. Nothing else.
"""


# ---------------------------------------------------------------------------
# 3. HUMAN MESSAGE BUILDER
# ---------------------------------------------------------------------------


def _build_human_message(*, prompt_id: str, response_text: str) -> str:
    return f"""\
WRITING TASK
  Prompt id : {prompt_id}
  Task      : The learner was asked to describe their typical day in 3–5
              sentences.

LEARNER'S ANSWER:
\"\"\"
{response_text.strip()}
\"\"\"

Score this answer now.
"""


# ---------------------------------------------------------------------------
# 4. PUBLIC ENTRY POINT
# ---------------------------------------------------------------------------


async def evaluate_writing(
    *,
    prompt_id: str,
    response_text: str,
) -> DiagnosisWritingScores:
    """Call the LLM and return validated writing scores.

    Uses the unified LLM client, so this call automatically gets retries,
    LangSmith tracing, token/cost logging, and provider-error translation.

    Raises:
        LLMValidationError: the LLM returned content that didn't match the
            DiagnosisWritingScores schema.
        LLMError: any other provider failure.
    """
    client = get_default_llm_client()
    human_message = _build_human_message(
        prompt_id=prompt_id,
        response_text=response_text,
    )

    try:
        result = await client.generate_structured(
            system_prompt=WRITING_EVALUATOR_SYSTEM_PROMPT,
            user_prompt=human_message,
            output_model=DiagnosisWritingScores,
        )
    except (LLMValidationError, LLMError):
        # Re-raise unchanged — DiagnosisService maps these to the right HTTP
        # status. Don't wrap in a generic exception.
        raise

    return result
