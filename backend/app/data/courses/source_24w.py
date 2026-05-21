"""24-week curriculum source data.

Content authored from the restructure spec §6. Each `WeekSource` lists 7 day
entries as `DaySource` values. `DaySource.__iter__` keeps the legacy loader
compatible by exposing each day as (topic, explanation_brief).

When updating content here:
  - Keep the 24 weeks structured as 6 cycles × 4 themes (grammar →
    communication → vocabulary → confidence). Tests enforce this.
  - Keep exactly 7 days per week. Tests enforce this.
  - Use legacy DB sub-skill names ONLY in code; this file is content-facing,
    so theme_type uses the doc names (grammar/communication/vocabulary/
    confidence), which are themes, not sub-skills.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DaySource:
    title: str = ""
    description: str = ""
    teacher_agent_behaviour: tuple[str, ...] = ()
    task_archetypes_used: tuple[str, ...] = ()

    # Optional compatibility context. File-authored teacher behavior should
    # normally live in `title`, `description`, and `teacher_agent_behaviour`.
    teacher_instructions: dict = field(default_factory=dict)

    # Per-activity hints to the task generator, one entry per archetype in
    # `task_archetypes_used`, same order. Empty tuple = generator runs
    # purely off archetype + day topic. Each dict may contain:
    # topic_override, instructions_override, primary_text_seed,
    # target_words (list), difficulty_note.
    task_specs: tuple[dict, ...] = ()

    # Optional nudges for the evaluator / feedback agents. Empty by default.
    evaluator_overrides: dict = field(default_factory=dict)
    feedback_overrides: dict = field(default_factory=dict)

    def __iter__(self):
        yield self.title
        yield self.description


@dataclass(frozen=True)
class WeekSource:
    week_number: int
    theme_type: str   # grammar | communication | vocabulary | confidence
    cefr_level: str   # A1 | A2 | B1 | B1+ | B2 | C1 | C2
    sub_level_min: int
    sub_level_max: int
    days: tuple[DaySource, ...]
    title: str = ""
    learning_goal: str = ""


WEEKS_24: tuple[WeekSource, ...] = (
    # ── Cycle 1 — Foundation (A1) ─────────────────────────────────
    WeekSource(
        week_number=1,
        theme_type="grammar",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=(
            DaySource(
                title="Simple Present Tense — Subject-Verb Agreement",
                description=(
                    "Use simple present in affirmative sentences: I work, he/she works. "
                    "Teach subject-verb agreement, especially third-person -s. "
                    "Use frequency adverbs: always, usually, often, sometimes, never. "
                    "Contrast action verbs with 'to be' so the learner does not mix "
                    "forms like 'I am work' and 'I work'."
                ),
                teacher_agent_behaviour=(
                    "Greet the learner and say today's lesson is about tense.",
                    "Briefly explain that tense shows when an action or state happens.",
                    "Teach that the simple present is used for facts, routines, and habits.",
                    "Ask the learner to give one real daily routine in a sentence.",
                    "Use the learner's routine to teach subject-verb agreement: I/you/we/they + base verb, he/she + verb-s.",
                    "Probe the pattern by asking the learner to change one sentence between I and he/she.",
                    "Teach frequency adverbs like always, usually, often, sometimes, and never.",
                    "Ask the learner for one final routine sentence using a frequency adverb and the correct verb form.",
                    "If the learner is still confused or makes the target mistake, correct it and ask one more focused question.",
                    "Only after the learner shows understanding, ask exactly: Ready to try the practice task?",
                ),
                task_archetypes_used=(
                    "READ_CLOZE",
                    "LISTEN_MCQ",
                    "WRITE_OPEN_SENT",
                    "SPEAK_TIMED",
                ),
            ),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=2,
        theme_type="communication",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=3,
        theme_type="vocabulary",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=4,
        theme_type="confidence",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),

    # ── Cycle 2 — Daily Life (A2) ─────────────────────────────────
    WeekSource(
        week_number=5,
        theme_type="grammar",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=6,
        theme_type="communication",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=7,
        theme_type="vocabulary",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=8,
        theme_type="confidence",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),

    # ── Cycle 3 — Functioning (B1) ────────────────────────────────
    WeekSource(
        week_number=9,
        theme_type="grammar",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=10,
        theme_type="communication",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=11,
        theme_type="vocabulary",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=12,
        theme_type="confidence",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),

    # ── Cycle 4 — Connecting (B1+ / B2) ───────────────────────────
    WeekSource(
        week_number=13,
        theme_type="grammar",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=14,
        theme_type="communication",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=15,
        theme_type="vocabulary",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=16,
        theme_type="confidence",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),

    # ── Cycle 5 — Reasoning (B2) ──────────────────────────────────
    WeekSource(
        week_number=17,
        theme_type="grammar",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=18,
        theme_type="communication",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=19,
        theme_type="vocabulary",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=20,
        theme_type="confidence",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),

    # ── Cycle 6 — Polishing (C1) ──────────────────────────────────
    WeekSource(
        week_number=21,
        theme_type="grammar",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=22,
        theme_type="communication",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=23,
        theme_type="vocabulary",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
    WeekSource(
        week_number=24,
        theme_type="confidence",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        days=(
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
            DaySource(),
        ),
    ),
)
