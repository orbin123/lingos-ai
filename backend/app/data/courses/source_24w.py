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
                    "Learners understand that simple present describes facts, routines, "
                    "and habits. They practise subject-verb agreement (I/you/we/they + "
                    "base verb; he/she + verb-s) and use frequency adverbs (always, "
                    "usually, often, sometimes, never) in original sentences."
                ),

                teacher_agent_behaviour=(
                    "TURN 1 — Open: greet the learner, explain in two sentences that tense shows when something happens and that simple present is for facts, routines, and habits. Then ask for one real daily routine in a sentence. Stop here.",
                    "TURN 2 — Subject-verb agreement: use the learner's own sentence to explain the rule (I/you/we/they + base verb; he/she + verb-s). Ask the learner to say the same routine with 'he' or 'she' as the subject. If they get it wrong, give one brief correction and ask once more, then move on. Stop here.",
                    "TURN 3 — Frequency adverbs: introduce the words always, usually, often, sometimes, never in one sentence. Ask the learner to write any routine sentence that uses one frequency adverb and the correct verb form. If they get it wrong, give one brief correction and move on. Stop here.",
                    "TURN 4 — Wrap-up: if the learner has shown the pattern at least once correctly across turns 2 and 3, ask exactly: Ready to try the practice task? Do not add any further explanation, review, or example.",
                ),
                task_archetypes_used=(
                    "READ_CLOZE",
                    "LISTEN_MCQ",
                    "WRITE_OPEN_SENT",
                    "SPEAK_TIMED",
                ),
                task_specs=(
                    {
                        "topic_override": "Simple present routines",
                        "instructions_override": (
                            "Write a 5–7 sentence connected passage about a "
                            "daily routine. Base the topic and characters on "
                            "the learner's interests. Focus on simple present "
                            "and third-person -s. Always include base_verb "
                            "for every blank."
                        ),
                    },
                    {
                        "topic_override": "Listening for daily routines",
                        "instructions_override": (
                            "Generate a short spoken passage (60-90 words) about daily routines "
                            "using simple present and frequency adverbs. Then write 3-4 MCQ "
                            "comprehension questions testing what was heard."
                        ),
                        "widget_requirements": (
                            "Set inner_widget to 'mcq'. Generate 3-4 comprehension questions "
                            "in `items` — each with item_id (q1, q2 …), prompt, options (4 "
                            "choices as strings), correct_index (0-based integer), and explanation."
                        ),
                    },
                    {
                        "topic_override": "Write simple present routine sentences",
                        "instructions_override": (
                            "Ask for affirmative routine sentences using "
                            "I/he/she and frequency adverbs."
                        ),
                    },
                    {
                        "topic_override": "Say simple present routines",
                        "instructions_override": (
                            "Tap the mic and say one short routine "
                            "sentence for each prompt. Use the correct "
                            "simple present verb form and one frequency "
                            "adverb (always, usually, often, sometimes, "
                            "never)."
                        ),
                        "widget_requirements": (
                            "Populate `speaking_prompts` with exactly 3 "
                            "items: one prompting an 'I' routine sentence, "
                            "one a 'he' routine sentence, and one a 'she' "
                            "routine sentence. Each prompt must explicitly "
                            "ask the learner to use a frequency adverb. "
                            "Populate `sample_responses` with one model "
                            "spoken answer per prompt (same order, same "
                            "length). Set `task_intro` to a short "
                            "imperative like 'Record your routine "
                            "sentences.' Include "
                            "`target_words: [\"always\", \"usually\", "
                            "\"often\", \"sometimes\", \"never\"]`, "
                            "`grammar_rule_to_practice` describing the "
                            "I/he/she base-verb-vs-(-s) rule, and "
                            "`speaking_duration_seconds: 45`."
                        ),
                    },
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
