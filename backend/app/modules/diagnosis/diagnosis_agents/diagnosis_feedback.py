"""Agent — Diagnosis Feedback.

Generates the human-facing interpretation of the learner's diagnosis result.
Called once by ``DiagnosisService`` right after the 7 skill scores are computed.

It produces everything the result page renders in prose / stat-card form:
  - an estimated level label + a one-line description of what it means
  - a short, honest summary of the learner's overall profile
  - the "biggest weakness", "strongest skill", and "first focus" stat cards
    (each a short value/title plus a one-sentence description)

The weakest/strongest skills themselves are chosen deterministically from the
scores by the service and passed in — the LLM only writes the descriptions,
so it can never disagree with the numbers on screen.

Implementation: LLM-backed via the unified ``app.ai.llm`` client. Retries,
LangSmith tracing, and usage logging are handled by the client.
"""

from pydantic import BaseModel, Field

from app.ai.llm import LLMError, LLMValidationError, get_default_llm_client


# ---------------------------------------------------------------------------
# 1. OUTPUT SCHEMA — what the LLM must return
# ---------------------------------------------------------------------------

class SkillCallout(BaseModel):
    """A skill stat card: which skill, plus a one-sentence description."""

    skill_name: str = Field(
        description=(
            "The skill identifier exactly as given to you "
            "(e.g. 'tone', 'comprehension'). Do NOT change or pick a "
            "different skill."
        )
    )
    description: str = Field(
        description=(
            "ONE short sentence describing this skill for the learner, tied "
            "to their goal. For a weakness, say what tends to go wrong. For a "
            "strength, say what they do well."
        )
    )


class FocusCallout(BaseModel):
    """The 'first focus' stat card: a short title plus a description."""

    title: str = Field(
        description=(
            "A short, punchy focus area for the first week "
            "(2–4 words, e.g. 'Speaking confidence', 'Tone calibration')."
        )
    )
    description: str = Field(
        description=(
            "ONE short sentence on what the learner will practise first and "
            "why it matters for their goal."
        )
    )


class DiagnosisFeedbackOutput(BaseModel):
    """Full diagnosis feedback payload returned to the frontend."""

    estimated_level_label: str = Field(
        description=(
            "A short human-friendly level label, CEFR-flavoured. "
            "Examples: 'A2 · Elementary', 'B1 · Intermediate', "
            "'B2 · Upper Intermediate', 'C1 · Advanced'. Pick the closest "
            "match to the scores."
        )
    )
    level_description: str = Field(
        description=(
            "ONE short sentence explaining what this level means in practice "
            "for the learner."
        )
    )
    summary: str = Field(
        description=(
            "2-3 sentences. Summarise the learner's overall English profile "
            "honestly. Name their strongest area briefly and their main "
            "weakness clearly. No empty praise like 'Great job!'. Be direct "
            "and kind, in simple English."
        )
    )
    biggest_weakness: SkillCallout = Field(
        description="Describe the weakest skill that was passed to you."
    )
    strongest_skill: SkillCallout = Field(
        description="Describe the strongest skill that was passed to you."
    )
    first_focus: FocusCallout = Field(
        description="What the learner's first week of coaching will focus on."
    )


# ---------------------------------------------------------------------------
# 2. SYSTEM PROMPT
# ---------------------------------------------------------------------------

DIAGNOSIS_FEEDBACK_SYSTEM_PROMPT = """\
You are a diagnostic interpreter for LingosAI, an AI-powered English learning app.

Your job: take a new learner's skill scores from a short diagnostic test and
explain their profile to them in plain, honest, encouraging English.

YOUR RULES:
1. Use SIMPLE English. The learner is a non-native speaker.
2. Be HONEST. If scores are low, say so clearly but kindly. Do not sugarcoat.
3. NEVER use generic phrases like "Great job!" or "Keep it up!" on their own.
   Any encouragement must be specific and tied to their goal.
4. Always connect skills to the learner's GOAL:
   - professional → emails, meetings, workplace conversation
   - academic → essays, presentations, study
   - casual → everyday conversation
5. For `biggest_weakness` and `strongest_skill`, you MUST use the exact skill
   names handed to you. Do not substitute a different skill.
6. Keep every field short and focused. Do not repeat yourself across fields.

You will receive:
- The learner's self-assessed level (beginner / intermediate / advanced)
- Their goal (professional / academic / casual)
- Their 7 skill scores (scale 1.0 to 4.0)
- Which skill is their weakest and which is their strongest

Return your response in the required JSON schema. Nothing else.
"""


# ---------------------------------------------------------------------------
# 3. HUMAN MESSAGE BUILDER
# ---------------------------------------------------------------------------

def _build_human_message(
    self_assessed_level: str,
    goal: str,
    skill_scores: dict[str, float],
    weakest_skill: str,
    strongest_skill: str,
) -> str:
    scores_text = "\n".join(
        f"  {name}: {score:.2f} / 4.00"
        for name, score in sorted(skill_scores.items(), key=lambda kv: kv[1])
    )

    return f"""\
LEARNER PROFILE:
  Self-assessed level : {self_assessed_level}
  Goal                : {goal}

SKILL SCORES (1.0 = very weak, 4.0 = excellent):
{scores_text}

WEAKEST SKILL (use this exact name for biggest_weakness): {weakest_skill}
STRONGEST SKILL (use this exact name for strongest_skill): {strongest_skill}

Generate the diagnosis feedback now.
"""


# ---------------------------------------------------------------------------
# 4. PUBLIC ENTRY POINT
# ---------------------------------------------------------------------------

async def generate_diagnosis_feedback(
    *,
    self_assessed_level: str,
    goal: str,
    skill_scores: dict[str, float],
    weakest_skill: str,
    strongest_skill: str,
) -> DiagnosisFeedbackOutput:
    """Call the LLM and return a validated DiagnosisFeedbackOutput.

    Uses the unified LLM client, so this call automatically gets retries,
    LangSmith tracing, token/cost logging, and provider-error translation.

    Args:
        self_assessed_level: "beginner" | "intermediate" | "advanced"
        goal: "professional" | "academic" | "casual"
        skill_scores: dict of 7 skill names → float scores
        weakest_skill: the skill name with the lowest score
        strongest_skill: the skill name with the highest score

    Returns:
        DiagnosisFeedbackOutput — structured, validated feedback object.

    Raises:
        LLMValidationError: the LLM returned content that didn't match the
            DiagnosisFeedbackOutput schema.
        LLMError: any other provider failure.
    """
    client = get_default_llm_client()
    human_message = _build_human_message(
        self_assessed_level=self_assessed_level,
        goal=goal,
        skill_scores=skill_scores,
        weakest_skill=weakest_skill,
        strongest_skill=strongest_skill,
    )

    try:
        result = await client.generate_structured(
            system_prompt=DIAGNOSIS_FEEDBACK_SYSTEM_PROMPT,
            user_prompt=human_message,
            output_model=DiagnosisFeedbackOutput,
        )
    except (LLMValidationError, LLMError):
        # Re-raise unchanged — DiagnosisService maps these to the right HTTP
        # status. Don't wrap in a generic exception.
        raise

    return result
