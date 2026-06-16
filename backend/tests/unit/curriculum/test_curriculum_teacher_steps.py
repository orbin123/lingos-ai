"""Authored-curriculum guard: teacher steps must obey the chat-teaching rules.

The teacher agent (``app.ai.agents.teacher``) enforces a strict single-turn
contract: during *teaching* it may only ever ask the learner for ONE short
sentence / word / phrase. Multi-sentence, paragraph, or story production belongs
to the practice *task*, never the chat. The three level-band source files feed
``TeacherStep.instruction`` strings straight into that agent as the authored
plan, so a stray "Ask them to write two sentences…" in the data silently fights
the runtime guard (it triggers repair/retry and can drop authored content).

This test walks every authored ``TeacherStep`` (including depth-day variants) and
fails if any instruction tells the teacher to ask the learner for extended
production. It is the data-level mirror of
``teacher._asks_for_extended_production``.
"""

from __future__ import annotations

import re

import pytest

from app.modules.curriculum.data.source_L_A1A2 import WEEKS_A1A2
from app.modules.curriculum.data.source_L_B1B2 import WEEKS_B1B2
from app.modules.curriculum.data.source_L_C1C2 import WEEKS_C1C2
from app.modules.curriculum.data.types import DaySource, TeacherStep, WeekSource

# An imperative that directs the LEARNER to produce something.
_ASK_LEARNER = re.compile(
    r"\b(?:ask|invite|prompt|encourage|elicit|nudge|push)\s+"
    r"(?:the\s+learner|them|him|her|the\s+student|for)\b"
    r"|\bhave\s+them\b|\bget\s+them\b",
    re.I,
)
# Targets that exceed the one-short-sentence ceiling.
_EXTENDED = re.compile(
    r"\b(?:one or two sentences|two or three sentences|two sentences|"
    r"three sentences|four sentences|five sentences|\d\s*[-–]\s*\d\s+sentences|"
    r"several sentences|multiple sentences|a few sentences|a paragraph|"
    r"write a paragraph|example story|"
    r"tell (?:me )?(?:a|one) (?:short |work )?story|pair of sentences)\b",
    re.I,
)
# Negated mentions ("…not a pair of sentences") reinforce the rule — allow them.
_NEGATION = re.compile(
    r"\b(?:not|never|no|rather than|instead of|avoid|don't|do not)\b", re.I
)


def _asks_learner_for_extended_production(instruction: str) -> str | None:
    """Return the offending clause, or None when the instruction is clean.

    Benign cases are deliberately *not* flagged:
    - the teacher's own speech ("Explain/Model in two sentences …"),
    - task previews ("preview … short paragraph …"),
    - conditions ("if the learner linked pronouns across two sentences …"),
    - negated targets ("ask for one sentence, not a pair of sentences").
    The extended target must follow the ask verb and not be negated.
    """

    for clause in re.split(r"(?<=[.?!])\s+", instruction):
        for ask in _ASK_LEARNER.finditer(clause):
            tail = clause[ask.end() :]
            target = _EXTENDED.search(tail)
            if target and not _NEGATION.search(
                tail[max(0, target.start() - 40) : target.start()]
            ):
                return clause.strip()
    return None


def _iter_days(day: DaySource):
    yield day
    if day.depth_day is not None:
        yield from _iter_days(day.depth_day)


def _all_teacher_steps() -> list[tuple[str, str, TeacherStep]]:
    steps: list[tuple[str, str, TeacherStep]] = []
    banks: list[tuple[str, tuple[WeekSource, ...]]] = [
        ("A1A2", WEEKS_A1A2),
        ("B1B2", WEEKS_B1B2),
        ("C1C2", WEEKS_C1C2),
    ]
    for band, weeks in banks:
        for week in weeks:
            for base_day in week.days:
                for day in _iter_days(base_day):
                    for step in day.teacher.steps:
                        loc = f"{band} w{week.week_number} '{day.title}' step[{step.id}]"
                        steps.append((band, loc, step))
    return steps


def test_source_files_have_teacher_steps() -> None:
    # Guard against the walk silently finding nothing (e.g. an import rename).
    assert len(_all_teacher_steps()) > 500


@pytest.mark.parametrize(
    "loc,step",
    [(loc, step) for _band, loc, step in _all_teacher_steps()],
    ids=[loc for _band, loc, _step in _all_teacher_steps()],
)
def test_teacher_step_does_not_ask_learner_for_extended_production(
    loc: str, step: TeacherStep
) -> None:
    offending = _asks_learner_for_extended_production(step.instruction)
    assert offending is None, (
        f"{loc} asks the learner for extended production during teaching: "
        f"{offending!r}. Teaching turns may ask for only ONE short sentence; "
        "multi-sentence/paragraph/story output belongs to the practice task."
    )


def test_detector_flags_a_known_bad_instruction() -> None:
    # Sanity-check the detector itself catches a clear violation.
    bad = "Affirm their idea. Ask them to defend one position in two sentences."
    assert _asks_learner_for_extended_production(bad) is not None


def test_detector_allows_teacher_speech_and_previews() -> None:
    benign = (
        "Explain in two sentences that simple present shows routines. "
        "Preview today's match, listening, short paragraph, and speaking tasks. "
        "Ask them to say one sentence about a friend (not a pair of sentences)."
    )
    assert _asks_learner_for_extended_production(benign) is None
