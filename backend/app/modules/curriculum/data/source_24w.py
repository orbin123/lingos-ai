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

from dataclasses import dataclass, field
from typing import Literal, Any

Theme = Literal["grammar", "communication", "vocabulary", "confidence"]
ActivityKind = Literal["read", "write", "listen", "speak"]

@dataclass(frozen=True)
class TeacherStep:
    id: str
    goal: str
    instruction: str
    stop_after: bool = True


@dataclass(frozen=True)
class TeacherBlueprint:
    style: str = "strict_kind_a1_friendly"
    lesson_goal: str = ""
    steps: tuple[TeacherStep, ...] = ()
    readiness_prompt: str = "Ready to try the practice task?"


@dataclass(frozen=True)
class TaskBlueprint:
    archetype_id: str
    activity: ActivityKind
    task_widget: str
    topic_override: str = ""
    generation_instructions: str = ""
    widget_requirements: str = ""
    static_payload: dict[str, Any] | None = None


@dataclass(frozen=True)
class EvaluationBlueprint:
    evaluator: str = "default"
    evaluation_widget: str = "activity_score"
    rubric: dict[str, Any] = field(default_factory=dict)
    overrides: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FeedbackBlueprint:
    generator: str = "default"
    feedback_widget: str = "feedback_card"
    overrides: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActivityBlueprint:
    id: str
    sequence: int
    task: TaskBlueprint
    evaluation: EvaluationBlueprint = field(default_factory=EvaluationBlueprint)
    feedback: FeedbackBlueprint = field(default_factory=FeedbackBlueprint)
    mandatory: bool = True


@dataclass(frozen=True)
class FinalReviewBlueprint:
    scorecard_widget: str = "final_scorecard"
    rag_feedback_widget: str = "rag_feedback"


@dataclass(frozen=True)
class DaySource:
    title: str = ""
    description: str = ""
    teacher: TeacherBlueprint = field(default_factory=TeacherBlueprint)
    activities: tuple[ActivityBlueprint, ...] = ()
    final_review: FinalReviewBlueprint = field(default_factory=FinalReviewBlueprint)

    focus: str = ""
    tags: tuple[str, ...] = ()

    def __iter__(self):
        yield self.title
        yield self.description


@dataclass(frozen=True)
class WeekSource:
    week_number: int
    theme_type: Theme
    cefr_level: str
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
    title="Simple Present Tense - Subject-Verb Agreement",
    description=(
        "Learners understand that simple present describes facts, routines, "
        "and habits. They practise subject-verb agreement and frequency adverbs."
    ),
    focus="Simple present routines with subject-verb agreement.",
    teacher=TeacherBlueprint(
        lesson_goal="Teach simple present for facts, routines, and habits.",
        steps=(
            TeacherStep(
                id="open",
                goal="Introduce simple present.",
                instruction=(
                    "Greet the learner. Explain in two sentences that tense shows "
                    "when something happens and simple present is for facts, "
                    "routines, and habits. Ask for one real daily routine."
                ),
            ),
            TeacherStep(
                id="subject_verb_agreement",
                goal="Teach I/you/we/they vs he/she verb forms.",
                instruction=(
                    "Use the learner's sentence to explain subject-verb agreement. "
                    "Ask them to say the same routine with he or she."
                ),
            ),
            TeacherStep(
                id="frequency_adverbs",
                goal="Teach always, usually, often, sometimes, never.",
                instruction=(
                    "Introduce frequency adverbs. Ask for one routine sentence "
                    "using a frequency adverb and correct verb form."
                ),
            ),
            TeacherStep(
                id="wrap_up",
                goal="Move to practice.",
                instruction=(
                    "If the learner has shown the pattern at least once, ask only: "
                    "Ready to try the practice task?"
                ),
            ),
        ),
    ),
    activities=(
        ActivityBlueprint(
            id="read_cloze_simple_present",
            sequence=1,
            task=TaskBlueprint(
                archetype_id="READ_CLOZE",
                activity="read",
                task_widget="fill_blanks",
                topic_override="Simple present routines",
                generation_instructions=(
                    "Write a 5-7 sentence passage about a daily routine. "
                    "Focus on simple present and third-person -s."
                ),
                widget_requirements=(
                    "Always include base_verb for every blank."
                ),
            ),
            evaluation=EvaluationBlueprint(
                evaluator="rule_plus_llm",
                evaluation_widget="read_listen_evaluation",
            ),
            feedback=FeedbackBlueprint(
                generator="default",
                feedback_widget="read_listen_feedback",
            ),
        ),
        ActivityBlueprint(
            id="listen_mcq_simple_present",
            sequence=2,
            task=TaskBlueprint(
                archetype_id="LISTEN_MCQ",
                activity="listen",
                task_widget="listen_mcq",
                topic_override="Listening for daily routines",
                generation_instructions=(
                    "Generate a 60-90 word spoken passage about daily routines "
                    "using simple present and frequency adverbs."
                ),
                widget_requirements=(
                    "Generate 3-4 MCQ items with prompt, options, correct_index, "
                    "and explanation."
                ),
            ),
            evaluation=EvaluationBlueprint(
                evaluator="rule_based",
                evaluation_widget="read_listen_evaluation",
            ),
            feedback=FeedbackBlueprint(
                feedback_widget="read_listen_feedback",
            ),
        ),
        ActivityBlueprint(
            id="write_simple_present_sentences",
            sequence=3,
            task=TaskBlueprint(
                archetype_id="WRITE_OPEN_SENT",
                activity="write",
                task_widget="open_text",
                topic_override="Write simple present routine sentences",
                generation_instructions=(
                    "Ask for affirmative routine sentences using I, he, she, "
                    "and frequency adverbs."
                ),
            ),
            evaluation=EvaluationBlueprint(
                evaluator="llm_writing",
                evaluation_widget="write_speak_evaluation",
            ),
            feedback=FeedbackBlueprint(
                feedback_widget="write_speak_feedback",
            ),
        ),
        ActivityBlueprint(
            id="speak_simple_present_routines",
            sequence=4,
            task=TaskBlueprint(
                archetype_id="SPEAK_TIMED",
                activity="speak",
                task_widget="speak_timed",
                topic_override="Say simple present routines",
                generation_instructions=(
                    "Ask the learner to say short routine sentences using correct "
                    "simple present verb form and one frequency adverb."
                ),
                widget_requirements=(
                    "Create exactly 3 speaking prompts: one with I, one with he, "
                    "and one with she. Include speaking_duration_seconds: 45."
                ),
            ),
            evaluation=EvaluationBlueprint(
                evaluator="speaking_eval",
                evaluation_widget="write_speak_evaluation",
            ),
            feedback=FeedbackBlueprint(
                feedback_widget="write_speak_feedback",
            ),
        ),
    ),
),
            DaySource(
                title="Simple Past Tense — Regular and Irregular Verbs",
                description=(
                    "Learners understand that simple past describes completed actions. "
                    "They practise forming regular past verbs (verb + -ed) and common "
                    "irregular past verbs (go → went, eat → ate, have → had)."
                ),
                focus="Simple past with regular -ed and common irregular verbs.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach simple past for completed actions.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce simple past.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that simple past "
                                "describes something already finished and regular verbs add -ed "
                                "(walk → walked). Ask for one thing they did yesterday."
                            ),
                        ),
                        TeacherStep(
                            id="regular_vs_irregular",
                            goal="Teach regular vs irregular past forms.",
                            instruction=(
                                "Use the learner's sentence to confirm or correct the past form. "
                                "Introduce go → went, eat → ate, have → had. Ask for one sentence "
                                "using any of those irregular verbs in the past."
                            ),
                        ),
                        TeacherStep(
                            id="error_awareness",
                            goal="Spot common past tense mistakes.",
                            instruction=(
                                "Show one common mistake (e.g. 'I goed to school') and ask the "
                                "learner to correct it and explain why in one sentence."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has shown the pattern at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_error_spot_past",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_ERROR_SPOT",
                            activity="read",
                            task_widget="error_spotting",
                            topic_override="Spot past tense errors",
                            generation_instructions=(
                                "Generate a 5-sentence passage about completed past events. "
                                "Each sentence must contain exactly one grammatical error, "
                                "so there are exactly 5 error tokens for the learner to tap. "
                                "Make the mistakes diverse across simple-past usage: include "
                                "irregular past form, did + base-verb alignment, missing "
                                "passive helper, past time-marker mismatch, and an object "
                                "or complement mismatch. Do not make all errors simple "
                                "regular verb + -ed mistakes."
                            ),
                            widget_requirements=(
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
                        ),
                        evaluation=EvaluationBlueprint(
                            evaluator="rule_plus_llm",
                            evaluation_widget="read_listen_evaluation",
                        ),
                        feedback=FeedbackBlueprint(
                            feedback_widget="read_listen_feedback",
                        ),
                    ),
                    ActivityBlueprint(
                        id="listen_cloze_past",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_CLOZE",
                            activity="listen",
                            task_widget="listen_cloze",
                            topic_override="Listen and fill past verb forms",
                            generation_instructions=(
                                "Listen to the short office stand-up audio, then complete "
                                "the paraphrased notes with the missing simple-past verbs "
                                "from the clip."
                            ),
                            widget_requirements=(
                                "Set inner_widget to 'fill_in_blanks'. Use the authored "
                                "audio_script, passage, and 5 BlankItems exactly as "
                                "provided so rule-based scoring can compare each typed "
                                "verb with correct_answer."
                            ),
                            static_payload={
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
                        ),
                        evaluation=EvaluationBlueprint(
                            evaluator="rule_based",
                            evaluation_widget="read_listen_evaluation",
                        ),
                        feedback=FeedbackBlueprint(
                            feedback_widget="read_listen_feedback",
                        ),
                    ),
                    ActivityBlueprint(
                        id="write_error_corr_past",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_ERROR_CORR",
                            activity="write",
                            task_widget="error_correction",
                            topic_override="Correct past tense mistakes",
                            generation_instructions=(
                                "Give the learner 3 sentences that each contain one past tense "
                                "error — mix wrong irregular forms (e.g. 'eated') and missing "
                                "-ed errors (e.g. 'She walk to school'). Ask the learner to "
                                "rewrite each sentence correctly."
                            ),
                        ),
                        evaluation=EvaluationBlueprint(
                            evaluator="llm_writing",
                            evaluation_widget="write_speak_evaluation",
                        ),
                        feedback=FeedbackBlueprint(
                            feedback_widget="write_speak_feedback",
                        ),
                    ),
                    ActivityBlueprint(
                        id="speak_read_aloud_past",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_READ_ALOUD",
                            activity="speak",
                            task_widget="read_aloud",
                            topic_override="Read past simple passage aloud",
                            generation_instructions=(
                                "Give the learner a connected simple past narrative passage "
                                "of 50-60 words to read aloud. Include a mix of regular past "
                                "verbs ending in -ed (showing diverse pronunciation /t/, /d/, "
                                "/ɪd/) and common irregular past verbs."
                            ),
                            widget_requirements=(
                                "Populate `text_to_read_aloud` with a single connected past "
                                "tense passage (50-60 words) describing completed past events. "
                                "Set `task_intro` to 'Read the passage above out loud.' "
                                "Include `grammar_rule_to_practice` explaining simple past "
                                "regular and irregular verbs, and "
                                "`speaking_duration_seconds: 45`."
                            ),
                        ),
                        evaluation=EvaluationBlueprint(
                            evaluator="speaking_eval",
                            evaluation_widget="write_speak_evaluation",
                        ),
                        feedback=FeedbackBlueprint(
                            feedback_widget="write_speak_feedback",
                        ),
                    ),
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
