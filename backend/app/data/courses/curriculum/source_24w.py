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
            DaySource(
                title="Simple Past Tense — Regular and Irregular Verbs",
                description=(
                    "Learners understand that simple past describes completed actions. "
                    "They practise forming regular past verbs (verb + -ed) and common "
                    "irregular past verbs (go → went, eat → ate, have → had). "

                ),
                teacher_agent_behaviour=(
                "TURN 1 — Open: greet the learner, explain in two sentences that simple past describes something already finished and that regular verbs add -ed (walk → walked). Ask the learner to tell you one thing they did yesterday in a sentence. Stop here.",
                "TURN 2 — Regular vs irregular: use the learner's own sentence to confirm or correct the past form. Introduce three common irregular verbs: go → went, eat → ate, have → had. Ask the learner to write one sentence using any of those three irregular verbs in the past. If they get it wrong, give one brief correction and ask once more, then move on. Stop here.",
                "TURN 3 — Error awareness: show one example of a common past tense mistake (e.g. 'I goed to school') and ask the learner to correct it and explain why it is wrong in one sentence. If they get it wrong, give one brief correction and move on. Stop here.",
                "TURN 4 — Wrap-up: if the learner has shown the pattern at least once correctly across turns 2 and 3, ask exactly: Ready to try the practice task? Do not add any further explanation, review, or example.",
                ),
                task_archetypes_used=(
                    "READ_ERROR_SPOT",
                    "LISTEN_CLOZE",
                    "WRITE_ERROR_CORR",
                    "SPEAK_READ_ALOUD",
                ),
                task_specs=(
                    {
                        "topic_override": "Spot past tense errors",
                        "instructions_override": (
                            "Generate a 5-sentence passage about completed past events. "
                            "Each sentence must contain exactly one grammatical error, "
                            "so there are exactly 5 error tokens for the learner to tap. "
                            "Make the mistakes diverse across simple-past usage: include "
                            "irregular past form, did + base-verb alignment, missing "
                            "passive helper, past time-marker mismatch, and an object "
                            "or complement mismatch. Do not make all errors simple "
                            "regular verb + -ed mistakes."
                        ),
                        "widget_requirements": (
                            "Target widget 'error_spotting'. Return exactly 5 "
                            "`passage_sentences`. Each sentence must include "
                            "`sentence_id`, `tokens`, and one `error` object. "
                            "Each token needs stable `token_id`, `text`, and "
                            "`is_error`; exactly one token per sentence must have "
                            "`is_error: true`. Each `error` must include token_id, "
                            "incorrect_phrase, correction, error_type, rule, and "
                            "explanation. Set `total_errors` to 5. Allowed "
                            "error_type values: irregular_past, "
                            "missing_past_auxiliary, passive_helper_missing, "
                            "time_marker_mismatch, object_or_complement_mismatch, "
                            "past_participle_form, regular_past_ending."
                        ),
                    },
                    {
                        "topic_override": "Listen and fill past verb forms",
                        "instructions_override": (
                            "Listen to the short office stand-up audio, then complete "
                            "the paraphrased notes with the missing simple-past verbs "
                            "from the clip."
                        ),
                        "widget_requirements": (
                            "Set inner_widget to 'fill_in_blanks'. Use the authored "
                            "audio_script, passage, and 5 BlankItems exactly as "
                            "provided so rule-based scoring can compare each typed "
                            "verb with correct_answer."
                        ),
                        "listen_and_respond": {
                            "task_intro": "Listen, then complete the past-tense notes.",
                            "instructions": (
                                "Play the audio once, then type the missing past-tense "
                                "verbs in the paraphrased notes."
                            ),
                            "estimated_time_minutes": 3,
                            "inner_widget": "fill_in_blanks",
                            "audio_genre": "Office stand-up",
                            "audio_script": (
                                "Yesterday, Priya got up early because she had a job "
                                "interview at nine in the morning. The night before, "
                                "she prepared her answers carefully, so she felt "
                                "confident. After the interview, she sent a short "
                                "thank-you email to the manager."
                            ),
                            "passage_title": "Interview Day Notes",
                            "passage": (
                                "Last Monday, Priya ___ up early. She ___ a job "
                                "interview at 9 AM. She ___ her answers the night "
                                "before, so she ___ confident. After the interview, "
                                "she ___ a thank-you email."
                            ),
                            "items": [
                                {
                                    "item_id": "b1",
                                    "blank_id": "b1",
                                    "sentence_with_blank": "Last Monday, Priya ___ up early.",
                                    "base_verb": "get",
                                    "correct_answer": "got",
                                    "distractors": ["get", "getted"],
                                    "options": ["got", "get", "getted"],
                                    "grammar_rule": "Use the irregular past form got for get.",
                                    "explanation": "Get is irregular in the past: get becomes got.",
                                },
                                {
                                    "item_id": "b2",
                                    "blank_id": "b2",
                                    "sentence_with_blank": "She ___ a job interview at 9 AM.",
                                    "base_verb": "have",
                                    "correct_answer": "had",
                                    "distractors": ["haved", "has"],
                                    "options": ["had", "haved", "has"],
                                    "grammar_rule": "Use had as the past form of have.",
                                    "explanation": "Have is irregular in the past: have becomes had.",
                                },
                                {
                                    "item_id": "b3",
                                    "blank_id": "b3",
                                    "sentence_with_blank": "She ___ her answers the night before.",
                                    "base_verb": "prepare",
                                    "correct_answer": "prepared",
                                    "distractors": ["prepare", "preparing"],
                                    "options": ["prepared", "prepare", "preparing"],
                                    "grammar_rule": "Add -ed to regular verbs in the simple past.",
                                    "explanation": "Prepare is regular, so the past form is prepared.",
                                },
                                {
                                    "item_id": "b4",
                                    "blank_id": "b4",
                                    "sentence_with_blank": "She ___ confident.",
                                    "base_verb": "feel",
                                    "correct_answer": "felt",
                                    "distractors": ["feeled", "feel"],
                                    "options": ["felt", "feeled", "feel"],
                                    "grammar_rule": "Use felt as the past form of feel.",
                                    "explanation": "Feel is irregular in the past: feel becomes felt.",
                                },
                                {
                                    "item_id": "b5",
                                    "blank_id": "b5",
                                    "sentence_with_blank": (
                                        "After the interview, she ___ a thank-you email."
                                    ),
                                    "base_verb": "send",
                                    "correct_answer": "sent",
                                    "distractors": ["sended", "send"],
                                    "options": ["sent", "sended", "send"],
                                    "grammar_rule": "Use sent as the past form of send.",
                                    "explanation": "Send is irregular in the past: send becomes sent.",
                                },
                            ],
                            "target_words_in_audio": ["got", "had", "prepared", "felt", "sent"],
                        },
                    },
                    {
                        "topic_override": "Correct past tense mistakes",
                        "instructions_override": (
                            "Give the learner 3 sentences that each contain one past tense error — mix wrong irregular forms (e.g. 'eated') and missing -ed errors (e.g. 'She walk to school'). Ask the learner to rewrite each sentence correctly."
                        ),
                    },
        {
            "topic_override": "Read past simple passage aloud",
            "instructions_override": (
                "Give the learner a connected simple past narrative passage "
                "of 50-60 words to read aloud. Include a mix of regular past verbs "
                "ending in -ed (showing diverse pronunciation /t/, /d/, /ɪd/) "
                "and common irregular past verbs."
            ),
            "widget_requirements": (
                "Populate `text_to_read_aloud` with a single connected past tense "
                "passage (50-60 words) describing completed past events. "
                "Set `task_intro` to 'Read the passage above out loud.' "
                "Include `grammar_rule_to_practice` explaining simple past "
                "regular and irregular verbs, and `speaking_duration_seconds: 45`."
            ),
        },
    ),
),
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
