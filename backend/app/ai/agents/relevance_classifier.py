"""Tiny relevance classifier for learner replies during the teaching phase.

A cheap, single-call gate that decides whether a learner's chat reply is a
genuine attempt to engage with the current lesson step. It complements the
free, deterministic structural-gibberish heuristic in the learning_session
service: that heuristic catches obvious junk ("asdkjfh", "!!!"); this catches
text that *looks* like English but is off-topic ("what's the weather?").

Design notes:
- Low temperature for deterministic classification.
- **Fail-open**: on any LLM error the classifier returns ``None`` and the
  caller treats that as RELEVANT. Blocking a paying learner because the API
  timed out is a worse outcome than letting one off-topic line through.
"""

from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field

from app.ai.llm import get_default_llm_client

logger = logging.getLogger(__name__)

Verdict = Literal["RELEVANT", "OFF_TOPIC", "CONFUSED"]


class RelevanceVerdict(BaseModel):
    """Structured output for the relevance classifier."""

    verdict: Verdict = Field(
        ...,
        description=(
            "RELEVANT if the reply is a genuine attempt to answer the lesson "
            "step (even if grammatically wrong); OFF_TOPIC if it is unrelated "
            "to the lesson; CONFUSED if the learner is expressing confusion or "
            "asking for help."
        ),
    )


_SYSTEM_PROMPT = """\
You are a classifier for an English tutoring chat. The tutor is teaching one
small lesson step and the learner just replied. Decide whether the learner's
reply is a genuine attempt to engage with that step.

Answer with exactly one verdict:
- RELEVANT: a sincere attempt to answer the step, even if the grammar or
  vocabulary is wrong, incomplete, or in broken English. Wrong answers are
  still RELEVANT.
- OFF_TOPIC: unrelated to the lesson (random remarks, jokes, complaints,
  changing the subject, or text in another language that is not an attempt at
  the answer).
- CONFUSED: the learner is signalling they do not understand or are asking the
  tutor for help instead of answering.

Be lenient: only choose OFF_TOPIC when the reply clearly does not try to
address the step. A short or imperfect answer is RELEVANT.
"""


def _build_user_prompt(*, topic: str, current_step: str, learner_reply: str) -> str:
    return f"""\
LESSON TOPIC: {topic}

CURRENT STEP (the tutor's last message / question the learner is replying to):
{current_step or "(none)"}

LEARNER'S REPLY:
{learner_reply}

Classify the reply now.
"""


async def classify_reply_relevance(
    *,
    topic: str,
    current_step: str,
    learner_reply: str,
) -> RelevanceVerdict | None:
    """Classify a learner reply as RELEVANT / OFF_TOPIC / CONFUSED.

    Returns ``None`` on any LLM failure so the caller can fail open (treat the
    reply as RELEVANT and let the normal teaching flow proceed).
    """
    client = get_default_llm_client()
    try:
        return await client.generate_structured(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=_build_user_prompt(
                topic=topic,
                current_step=current_step,
                learner_reply=learner_reply,
            ),
            output_model=RelevanceVerdict,
            temperature=0.0,
        )
    except Exception as exc:  # noqa: BLE001 - fail open on any error
        logger.warning("relevance classification failed (assuming RELEVANT): %s", exc)
        return None
