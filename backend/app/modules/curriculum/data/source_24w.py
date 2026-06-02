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
                    "Write a 4-5 blank connected passage about a daily routine. "
                    "Focus on simple present and third-person -s."
                ),
                widget_requirements=(
                    "Always include base_verb for every blank. "
                    "Do not repeat base_verb inline in the passage after each ___ — the UI shows it separately."
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
                            evaluation_widget="read_aloud_assessment",
                        ),
                        feedback=FeedbackBlueprint(
                            feedback_widget="read_aloud_assessment",
                        ),
                    ),
                ),
            ),
            DaySource(
                title="Present Continuous - Actions Happening Now",
                description=(
                    "Learners use present continuous (am/is/are + verb-ing) to "
                    "describe actions happening right now, choose the correct "
                    "helper from the subject, and contrast it with simple present."
                ),
                focus="Present continuous with am, is, are, and verb-ing for actions happening right now.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach present continuous for actions happening now.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce present continuous.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that present "
                                "continuous uses am, is, or are plus verb-ing for actions "
                                "happening now (I am reading, she is cooking). Ask them to "
                                "look around and write one action happening right now."
                            ),
                        ),
                        TeacherStep(
                            id="choose_helper",
                            goal="Teach am/is/are agreement.",
                            instruction=(
                                "Use the learner's sentence to confirm the helper. Explain "
                                "am with I, is with he/she/one name, are with you/we/they. "
                                "Ask them to change one simple present sentence such as "
                                "'She walks to school' into present continuous."
                            ),
                        ),
                        TeacherStep(
                            id="contrast_now",
                            goal="Contrast routines vs now.",
                            instruction=(
                                "Confirm simple present describes routines and present "
                                "continuous describes what is happening now. Ask for one "
                                "sentence with they and an action happening right now."
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
                        id="read_comp_mcq_present_continuous",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Understand actions happening now",
                            generation_instructions=(
                                "Write a 50-60 word passage describing a busy scene (for "
                                "example a community center) where several people are each "
                                "doing something right now, using present continuous. Then "
                                "ask comprehension questions about who is doing what, and "
                                "include one item that asks which sentence uses present "
                                "continuous correctly."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, "
                                "passage, and 4 MCQ items, each with prompt, options, "
                                "correct_index, and explanation."
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
                        id="listen_dictation_present_continuous",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="Hear present continuous chunks",
                            generation_instructions=(
                                "Generate a 30-40 word live-classroom audio script of 4 short "
                                "present continuous sentences with varied subjects (I, plural "
                                "students, one name, the teacher). The learner types each "
                                "sentence exactly as heard."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_dictation'. Provide audio_script and "
                                "4 dictation items, each with prompt, correct_answer, and "
                                "explanation. Set target_words to the present continuous verb "
                                "chunks (for example 'am opening', 'are taking', 'is asking', "
                                "'is writing')."
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
                        id="write_sent_trans_present_continuous",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Rewrite into present continuous",
                            generation_instructions=(
                                "Give the learner 3 simple present sentences with varied "
                                "subjects (she, they, I) and ask them to rewrite each as a "
                                "present continuous sentence about what is happening now, "
                                "choosing the helper from the subject."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 3 items, each "
                                "with source_sentence, sample_answer, and watch_hints (for "
                                "example 'they -> are', 'play -> playing')."
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
                        id="speak_timed_present_continuous",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe what people are doing now",
                            generation_instructions=(
                                "Ask the learner to say one present continuous sentence per "
                                "prompt describing what is happening right now, choosing am, "
                                "is, or are correctly from the subject."
                            ),
                            widget_requirements=(
                                "Create exactly 3 speaking prompts: one about what you are "
                                "doing now, one about what one person is doing now, and one "
                                "about what two or more people are doing now. Include "
                                "speaking_duration_seconds: 45."
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
                title="Articles - A, An, The",
                description=(
                    "Learners use a before consonant sounds, an before vowel "
                    "sounds, and the for specific or unique nouns, in reading, "
                    "listening, writing, and speaking."
                ),
                focus="Using a, an, and the correctly.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach the articles a, an, and the.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce a vs an.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that we use a "
                                "before consonant sounds and an before vowel sounds. Ask "
                                "which one they use before 'apple'."
                            ),
                        ),
                        TeacherStep(
                            id="the_specific",
                            goal="Teach 'the' for specific or unique nouns.",
                            instruction=(
                                "Confirm 'an apple'. Explain we use the for a specific thing "
                                "or something there is only one of (the sun). Ask how they "
                                "would refer to a specific book they already bought."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Confirm the pattern with a short example (I bought a book. "
                                "The book is interesting.) and then ask only: Ready to try "
                                "the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_articles",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Match articles to nouns",
                            generation_instructions=(
                                "Ask the learner to match a, an, or the to several nouns "
                                "based on the article rules: a before consonant sounds, an "
                                "before vowel sounds, and the for unique nouns such as sun."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options ['a', "
                                "'an', 'the'] and 3-4 items, each with prompt (the noun), "
                                "correct_answer, and explanation."
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
                        id="listen_mcq_articles",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Hearing articles in natural speech",
                            generation_instructions=(
                                "Generate a 30-40 word short dialogue that introduces a noun "
                                "with a/an and then refers back to it with the (for example "
                                "buying a book, then 'the book'). Include an example of an "
                                "before a vowel sound."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 2-3 "
                                "MCQ items, each with prompt, options, correct_index, and "
                                "explanation."
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
                        id="write_open_sent_articles",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_OPEN_SENT",
                            activity="write",
                            task_widget="open_text",
                            topic_override="Write sentences using a, an, and the",
                            generation_instructions=(
                                "Ask for three short sentences, one using a, one using an, "
                                "and one using the. Remind the learner to match a/an to the "
                                "first sound and use the for specific or unique nouns."
                            ),
                            widget_requirements=(
                                "Target widget 'open_text'. Provide target_words ['a', 'an', "
                                "'the'], common_mistakes, and 3 items, each with prompt, "
                                "sample_answer, and answer_hints."
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
                        id="speak_pic_desc_articles",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a picture using articles",
                            generation_instructions=(
                                "Ask the learner to describe a simple everyday scene aloud, "
                                "using a/an when mentioning something for the first time and "
                                "the when it is specific or already mentioned."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "a simple scene (for example a cat sleeping on a sofa next to "
                                "an open book), grammar_rule, and speaking_duration_seconds: "
                                "45."
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
                title="Pronouns - Subject, Object, and Possessives",
                description=(
                    "Learners use subject pronouns for the actor, object pronouns "
                    "for the receiver, and possessive pronouns for ownership, and "
                    "resolve who ambiguous pronouns refer to."
                ),
                focus="Using subject, object, and possessive pronouns correctly in conversation and writing.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach subject, object, and possessive pronouns.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce the three pronoun types.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that subject "
                                "pronouns (I, he, she, they) do the action and object "
                                "pronouns (me, him, her, them) receive it. Ask them to "
                                "complete 'I like Sarah. I gave ___ a gift.'"
                            ),
                        ),
                        TeacherStep(
                            id="possessive",
                            goal="Teach possessive pronouns.",
                            instruction=(
                                "Confirm 'her'. Explain possessive pronouns (mine, yours, "
                                "his, hers, ours, theirs) show ownership. Ask them to "
                                "complete 'This book belongs to me. This book is ___.'"
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used the correct pronoun at least once, "
                                "ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_cloze_pronouns",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CLOZE",
                            activity="read",
                            task_widget="fill_blanks",
                            topic_override="Fill pronoun blanks",
                            generation_instructions=(
                                "Write a short 4-5 sentence family-visit passage with blanks "
                                "that require a subject pronoun, two object pronouns, and a "
                                "possessive pronoun, so the learner picks the right pronoun "
                                "by its role in the sentence."
                            ),
                            widget_requirements=(
                                "Target widget 'fill_blanks'. Provide passage_title, passage, "
                                "and a BlankItem per blank with base_verb (the cue pronoun), "
                                "correct_answer, and explanation."
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
                        id="listen_infer_pronouns",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Implied meaning of pronouns",
                            generation_instructions=(
                                "Generate a 30-40 word audio clip in which two people are "
                                "described with several she/her pronouns so the referents "
                                "are ambiguous. Ask the learner to infer who each pronoun "
                                "refers to (for example who got the promotion, who buys "
                                "dinner)."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_infer'. Provide audio_script, "
                                "intent_focus, and 2 MCQ items, each with prompt, options, "
                                "correct_index, and explanation."
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
                        id="write_para_pronouns",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write a paragraph with pronouns",
                            generation_instructions=(
                                "Ask the learner to write a 3-4 sentence paragraph about a "
                                "day out with a friend that uses at least one subject "
                                "pronoun, one object pronoun, and one possessive pronoun "
                                "correctly."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, "
                                "grammar_rule, target_words (we, us, our, me, him, her, his, "
                                "hers), minimum_words 20, sample_answer, and answer_hints."
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
                        id="speak_roleplay_pronouns",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Pronoun roleplay scenario",
                            generation_instructions=(
                                "Set up a short ownership roleplay (for example about a book "
                                "on the table) where the learner answers the partner using "
                                "possessive pronouns like mine and object pronouns like him."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_roleplay'. Provide a dialogue_context "
                                "alternating partner and learner turns, target_words (mine, "
                                "yours, she, him, he), and speaking_duration_seconds: 30."
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
                title="Possessives - Nouns, Adjectives, and Pronouns",
                description=(
                    "Learners use possessive 's for nouns, possessive adjectives "
                    "before a noun (my, his, her, our), and possessive pronouns "
                    "that replace a noun (mine, his, hers, ours, theirs)."
                ),
                focus="Possessive 's, possessive adjectives (my, your, his, her, its, our, their), and possessive pronouns (mine, yours, his, hers, ours, theirs).",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach possessive nouns, adjectives, and pronouns.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Teach possessive adjectives and 's.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that we use "
                                "possessive 's for nouns (Maria's bag) and possessive "
                                "adjectives before a noun (my phone, her car). Ask them to "
                                "complete 'This is John's laptop. It is ___ laptop.'"
                            ),
                        ),
                        TeacherStep(
                            id="possessive_pronouns",
                            goal="Teach possessive pronouns that replace a noun.",
                            instruction=(
                                "Confirm 'his laptop'. Explain possessive pronouns (mine, "
                                "yours, his, hers, ours, theirs) replace the noun. Ask them "
                                "to complete 'The car belongs to Mary and Steve. The car is "
                                "___.'"
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a correct possessive form at least "
                                "once, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_possessives",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="Possessives in text",
                            generation_instructions=(
                                "Write a short family description (for example a picnic) rich "
                                "in possessive 's, possessive adjectives, and possessive "
                                "pronouns (his sunglasses, borrowing mine, mother's hat). "
                                "Then give True / False / Not Given statements about who "
                                "owns what."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tfng'. Provide passage_title, passage, "
                                "and 5 items, each with prompt, correct_answer (True, False, "
                                "or Not Given), and explanation."
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
                        id="listen_shadow_possessives",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Repeat possessives in fast speech",
                            generation_instructions=(
                                "Generate a short, fast monologue (about 20 seconds) in which "
                                "possessive pronouns mine, his, and hers are blended into "
                                "fast speech, for the learner to shadow and reproduce "
                                "smoothly."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_shadow'. Provide audio_script, "
                                "text_to_shadow (identical to the script), target_words "
                                "highlighting the reduced possessive chunks, and grammar_rule."
                            ),
                        ),
                        evaluation=EvaluationBlueprint(
                            evaluator="speaking_eval",
                            evaluation_widget="read_aloud_assessment",
                        ),
                        feedback=FeedbackBlueprint(
                            feedback_widget="read_aloud_assessment",
                        ),
                    ),
                    ActivityBlueprint(
                        id="write_email_possessives",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Introduce your family in an email",
                            generation_instructions=(
                                "Ask the learner to write a short email introducing their "
                                "family, using possessive adjectives (my, his, her, our) and "
                                "possessive nouns (brother's, sister's) to introduce family "
                                "members."
                            ),
                            widget_requirements=(
                                "Target widget 'write_email'. Provide prompt, grammar_rule, "
                                "target_words, minimum_words 20, sample_answer (with To and "
                                "Subject lines), and answer_hints."
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
                        id="speak_smalltalk_possessives",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Casual conversation with possessives",
                            generation_instructions=(
                                "Set up casual small talk about whose belongings are whose "
                                "(an umbrella, some keys) where the learner answers using "
                                "possessive pronouns naturally to avoid repeating the noun."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_smalltalk'. Provide a dialogue_context "
                                "alternating partner and learner turns, target_words (yours, "
                                "mine, hers, his, ours), and speaking_duration_seconds: 30."
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
                title="Prepositions - Expressing Place, Time, and Context",
                description=(
                    "Learners choose prepositions of place and common collocations "
                    "in context (in, on, at, next to, between) to describe where "
                    "things are and how ideas connect."
                ),
                focus="Prepositions in context (in, on, at, next to, between) for relationships, space, and confidence.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach prepositions of place and context.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce context-dependent prepositions.",
                            instruction=(
                                "Greet the learner and note this is the final, confidence "
                                "wrap-up day of grammar week. Explain in two sentences that "
                                "prepositions like in, on, at, next to, and between depend on "
                                "context. Ask which preposition describes being inside a room."
                            ),
                        ),
                        TeacherStep(
                            id="surfaces_and_between",
                            goal="Teach on for surfaces and between for the middle.",
                            instruction=(
                                "Confirm 'in the room'. Ask which preposition describes "
                                "something resting on a flat surface like a table, then "
                                "explain between for a position in the middle of two things."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has chosen the correct preposition at least "
                                "once, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_context_mcq_prepositions",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Prepositions in context",
                            generation_instructions=(
                                "Write a short café-scene passage with 4 blanks that each "
                                "need a preposition chosen from context: on for surfaces "
                                "(counter, wall), in for an armchair or room, and between for "
                                "a position in the middle of two places."
                            ),
                            widget_requirements=(
                                "Target widget 'read_context_mcq'. Provide passage_title, "
                                "passage, and 4 MCQ items, each with prompt, options "
                                "(in, on, at, between), correct_index, and explanation."
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
                        id="listen_retell_prepositions",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Listen and summarize",
                            generation_instructions=(
                                "Generate a ~35 second travel monologue describing a place "
                                "using prepositions of place (at the center, next to it, in "
                                "the park, between the two trees). Ask the learner to retell "
                                "the main ideas in their own words, keeping the prepositions "
                                "correct."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_retell'. Provide audio_script, "
                                "passage_to_retell, target_words listing the key preposition "
                                "phrases, and grammar_rule."
                            ),
                        ),
                        evaluation=EvaluationBlueprint(
                            evaluator="speaking_eval",
                            evaluation_widget="read_listen_evaluation",
                        ),
                        feedback=FeedbackBlueprint(
                            feedback_widget="read_listen_feedback",
                        ),
                    ),
                    ActivityBlueprint(
                        id="write_paraphrase_prepositions",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="Correcting preposition mistakes",
                            generation_instructions=(
                                "Give the learner 3 sentences that each use the wrong "
                                "preposition in a common collocation (good in/at, depend "
                                "from/on, arrived at/on Monday) and ask them to rewrite each "
                                "with the correct preposition."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paraphrase'. Provide 3 items, each "
                                "with incorrect_sentence, sample_answer, and watch_hints "
                                "(the target collocation)."
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
                        id="speak_present_prepositions",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Room layout presentation",
                            generation_instructions=(
                                "Ask the learner to describe the objects and their positions "
                                "in a cozy room aloud, using at least three spatial "
                                "prepositions (on the table, next to the sofa, between the "
                                "two windows)."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_present'. Provide "
                                "visual_prompt_description of a cozy room, grammar_rule, "
                                "target_words, and speaking_duration_seconds: 45."
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
        ),
    ),
    WeekSource(
        week_number=2,
        theme_type="communication",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=(
            DaySource(
                title="Greetings & Introductions",
                description=(
                    "Learners greet someone naturally, introduce themselves "
                    "clearly, and keep a first meeting going with one easy "
                    "follow-up question."
                ),
                focus="Greeting someone naturally, introducing yourself, and asking one simple follow-up question.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach natural first-meeting greetings and introductions.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce the first-meeting goal.",
                            instruction=(
                                "Welcome the learner to communication week. Explain in two "
                                "sentences that a first meeting is: say hello, share your "
                                "name, and add one easy question. Ask them to greet you and "
                                "introduce themselves."
                            ),
                        ),
                        TeacherStep(
                            id="follow_up_question",
                            goal="Teach a friendly follow-up question.",
                            instruction=(
                                "Confirm their introduction sounds natural. Explain that "
                                "after introducing yourself you add one friendly question "
                                "like 'Are you new here?' or 'What do you do?'. Ask them to "
                                "introduce themselves again and add one follow-up question."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Remind them to keep the tone warm and sentences short, then "
                                "ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_greetings",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Greetings and introductions",
                            generation_instructions=(
                                "Write a short first-meeting conversation in which two people "
                                "greet each other, share names, and one asks a friendly "
                                "follow-up question. Then ask comprehension questions about "
                                "how each person introduces themselves and why they ask the "
                                "follow-up."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, "
                                "passage, and 3 MCQ items, each with prompt, options, "
                                "correct_index, and explanation."
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
                        id="listen_mcq_greetings",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Listening to a first conversation",
                            generation_instructions=(
                                "Generate a 30-40 word greeting dialogue between two people "
                                "meeting in a class, with names, polite 'nice to meet you' "
                                "exchanges, and one follow-up question. The learner answers "
                                "questions about why they speak, the polite reply, and the "
                                "follow-up question."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ "
                                "items, each with prompt, options, correct_index, and "
                                "explanation."
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
                        id="write_sent_trans_greetings",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Polite self-introductions",
                            generation_instructions=(
                                "Give the learner 3 short, casual self-introduction lines and "
                                "ask them to rewrite each as a more natural, polite "
                                "introduction using forms like 'Hello, my name is...', 'I'm "
                                "a...', and 'Nice to meet you.'"
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 3 items, each "
                                "with source_sentence, sample_answer, and watch_hints."
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
                        id="speak_roleplay_greetings",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Introduce yourself in a new conversation",
                            generation_instructions=(
                                "Set up a friendly first-meeting roleplay where a new person "
                                "introduces themselves. The learner replies with a greeting, "
                                "their name, 'nice to meet you', and one follow-up question "
                                "like 'What about you?'"
                            ),
                            widget_requirements=(
                                "Target widget 'speak_roleplay'. Provide a dialogue_context "
                                "alternating partner and learner turns, target_words (Hi, "
                                "I'm, Nice to meet you, What do you do?), and "
                                "speaking_duration_seconds: 30."
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
                title="Asking & Answering Questions",
                description=(
                    "Learners keep a conversation moving with short clear "
                    "questions, polite requests, and direct answers, then add a "
                    "follow-up so the conversation does not stop."
                ),
                focus="Keeping conversations moving with short questions, polite requests, and clear answers.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach asking and answering short questions to keep a conversation moving.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce short clear questions.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that a good A1 "
                                "conversation uses short clear questions like 'Are you "
                                "free?', 'Can we meet?', and 'What do you like?'. Ask them "
                                "to write one short, polite question."
                            ),
                        ),
                        TeacherStep(
                            id="answer_then_follow_up",
                            goal="Teach the question-answer-follow-up loop.",
                            instruction=(
                                "Confirm their question is clear and polite. Explain that "
                                "when someone answers, you add one simple follow-up question "
                                "so the conversation does not stop. Ask them to answer and "
                                "add a follow-up question."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Remind them to keep words short and answer directly, then "
                                "ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_questions",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="Questions in a short dialogue",
                            generation_instructions=(
                                "Write a short after-class dialogue where two classmates "
                                "arrange to practise English (whether someone is free, where "
                                "to meet, what to bring). Then give True / False / Not Given "
                                "statements based only on the dialogue."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tfng'. Provide passage_title, passage, "
                                "and 4 items, each with prompt, correct_answer (True, False, "
                                "or Not Given), and explanation."
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
                        id="listen_infer_questions",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Inferring intent in a request",
                            generation_instructions=(
                                "Generate a polite request dialogue (about 40 seconds) where "
                                "one person prepares a request, asks for help, limits their "
                                "time, and the other offers to prepare something. Ask the "
                                "learner to infer the intent behind each line, not just the "
                                "literal words."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_infer'. Provide audio_script, "
                                "intent_focus, and 4 MCQ items, each with prompt, options, "
                                "correct_index, and explanation."
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
                        id="write_email_questions",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Ask a simple question by message",
                            generation_instructions=(
                                "Ask the learner to write a short message to a classmate "
                                "asking to meet after class. It must include a greeting, one "
                                "clear question (Can we...? / Could you...?), a time phrase, "
                                "and a polite close."
                            ),
                            widget_requirements=(
                                "Target widget 'write_email'. Provide prompt, grammar_rule, "
                                "target_words, minimum_words 20, sample_answer (with To and "
                                "Subject lines), and answer_hints."
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
                        id="speak_interview_questions",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_INTERVIEW",
                            activity="speak",
                            task_widget="speak_interview",
                            topic_override="Answer simple interview questions",
                            generation_instructions=(
                                "Run a friendly mini interview where the learner answers "
                                "three simple questions (name, what they do, a hobby) in one "
                                "short full sentence each."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_interview'. Provide interview_context, "
                                "grammar_rule, target_words (My name is, I'm a, I like), 3 "
                                "questions each with interviewer_prompt, sample_answer, and "
                                "answer_hint, and speaking_duration_seconds: 30."
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
                title="Talking About Daily Life",
                description=(
                    "Learners speak about routines naturally with clear sequence "
                    "words (first, then, after that, finally) and add a short "
                    "opinion with a reason."
                ),
                focus="Speak about routines naturally with clear sequence words and short opinions.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach describing daily life with sequence words and a short opinion.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce talking about routines.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that a clear "
                                "routine has a beginning, middle, and end. Ask them to tell "
                                "you one thing they do after they wake up."
                            ),
                        ),
                        TeacherStep(
                            id="sequence_words",
                            goal="Teach sequence words.",
                            instruction=(
                                "Confirm their answer. Introduce sequence words (first, "
                                "then, after that, finally) and ask them to write one short "
                                "routine using two sequence words."
                            ),
                        ),
                        TeacherStep(
                            id="add_opinion",
                            goal="Add a short opinion with a reason.",
                            instruction=(
                                "Show how to add a simple opinion (I prefer mornings because "
                                "I feel fresh). Ask them whether they prefer morning or "
                                "evening and why, in one sentence."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a sequence word and a reason at "
                                "least once, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_structure_daily_life",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_STRUCTURE_ID",
                            activity="read",
                            task_widget="read_structure",
                            topic_override="Identify parts of a morning routine",
                            generation_instructions=(
                                "Provide a 3-paragraph morning-routine passage and ask the "
                                "learner to label each paragraph as the intro (main idea), "
                                "body (ordered details with sequence words), or conclusion "
                                "(closing thought)."
                            ),
                            widget_requirements=(
                                "Target widget 'read_structure'. Provide passage_title, "
                                "structure_labels ['Intro', 'Body', 'Conclusion'], and 3 "
                                "items, each with paragraph, correct_answer, and explanation."
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
                        id="listen_retell_daily_life",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Retell a daily routine",
                            generation_instructions=(
                                "Generate a daily-routine monologue (about 50 seconds) with "
                                "ordered actions across morning, afternoon, and evening. Ask "
                                "the learner to retell the key actions in order using "
                                "sequence words."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_retell'. Provide audio_script, "
                                "passage_to_retell, target_words (first, then, after work, "
                                "finally), and grammar_rule."
                            ),
                        ),
                        evaluation=EvaluationBlueprint(
                            evaluator="speaking_eval",
                            evaluation_widget="read_listen_evaluation",
                        ),
                        feedback=FeedbackBlueprint(
                            feedback_widget="read_listen_feedback",
                        ),
                    ),
                    ActivityBlueprint(
                        id="write_para_daily_life",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write your daily routine",
                            generation_instructions=(
                                "Ask the learner to write a 5-7 sentence paragraph about "
                                "their own daily routine, using simple present verbs and at "
                                "least three sequence words, ending with an evening or night "
                                "activity."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, "
                                "grammar_rule, target_words (first, then, after that, "
                                "usually, finally), minimum_words 45, sample_answer, and "
                                "answer_hints."
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
                        id="speak_opinion_daily_life",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_OPINION",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Share a short daily-life opinion",
                            generation_instructions=(
                                "Ask the learner to answer in two or three sentences whether "
                                "they prefer morning or evening, giving their preference and "
                                "one reason with because."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_present'. Provide grammar_rule, "
                                "target_words (I prefer, because, morning, evening), a "
                                "visual_prompt_description or prompt for the opinion, and "
                                "speaking_duration_seconds: 40."
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
                title="Shopping & Ordering",
                description=(
                    "Learners handle real-world shopping and ordering: read a "
                    "shop dialogue, follow a cafe order, turn a shopping list "
                    "into a polite message, and roleplay ordering items."
                ),
                focus="Handle real-world interactions like ordering food and buying items.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach polite shopping and ordering language.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce polite ordering phrases.",
                            instruction=(
                                "Welcome the learner to Day 4. Explain in two sentences that "
                                "ordering should be polite and clear with phrases like "
                                "'Could I have...' or 'I'd like to get...'. Ask for a polite "
                                "way to ask for a coffee."
                            ),
                        ),
                        TeacherStep(
                            id="extend_order",
                            goal="Practise extending an order.",
                            instruction=(
                                "Confirm their polite phrase. Ask them to order one more "
                                "item, such as a slice of cake, in the same polite way, and "
                                "briefly preview that today they will read a shop dialogue, "
                                "follow a cafe order, write from a shopping list, and "
                                "roleplay ordering."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has produced one polite order, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_shopping",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Shopping Dialogue",
                            generation_instructions=(
                                "Write a customer-and-shopkeeper dialogue in which the "
                                "customer asks where to find specific items and the "
                                "shopkeeper gives aisle locations and a delivery time. Then "
                                "ask comprehension questions about what is bought and where "
                                "items are."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, "
                                "passage, and 3 MCQ items, each with prompt, options, "
                                "correct_index, and explanation."
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
                        id="listen_mcq_shopping",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Cafe order details",
                            generation_instructions=(
                                "Generate a cafe order conversation (about 40 seconds) where "
                                "a customer orders a specific drink and a food item and the "
                                "server states the total price. Ask comprehension questions "
                                "about the drink, the food, and the total."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ "
                                "items, each with prompt, options, correct_index, and "
                                "explanation."
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
                        id="write_bullets_to_para_shopping",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_BULLETS_TO_PARA",
                            activity="write",
                            task_widget="write_bullets_to_para",
                            topic_override="Write a message from a shopping list",
                            generation_instructions=(
                                "Give the learner a 4-item shopping list and ask them to "
                                "turn it into a natural, polite chat message to a roommate "
                                "asking them to pick the items up, using complete sentences "
                                "and polite request phrasing."
                            ),
                            widget_requirements=(
                                "Target widget 'write_bullets_to_para'. Provide bullets (4 "
                                "shopping items), prompt, grammar_rule, target_words, "
                                "minimum_words 25, sample_answer, and answer_hints."
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
                        id="speak_roleplay_shopping",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Order items at a grocery shop",
                            generation_instructions=(
                                "Set up a grocery-shop roleplay where a shopkeeper greets "
                                "the learner. The learner says what they are looking for "
                                "using 'I'm looking for...' and answers the shopkeeper's "
                                "questions politely and directly."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_roleplay'. Provide a dialogue_context "
                                "alternating partner and learner turns, target_words (looking "
                                "for, Yes please, also), and speaking_duration_seconds: 30."
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
                title="Asking for Help & Directions",
                description=(
                    "Learners use survival English to ask for help, understand "
                    "simple directions with action words and landmarks, and "
                    "describe locations on a map."
                ),
                focus="Ask for help, understand simple directions, and describe map locations.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach asking for help and understanding directions.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce survival help phrases.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that useful "
                                "survival phrases are 'Excuse me, could you help me?' and "
                                "'Where is the...?', plus directions like go straight, turn "
                                "left, and next to. Ask them to write a polite request for "
                                "help."
                            ),
                        ),
                        TeacherStep(
                            id="add_place_and_landmarks",
                            goal="Add the place and listen for landmarks.",
                            instruction=(
                                "Confirm their request. Ask them to add the place they need "
                                "(for example the station). Explain that when someone gives "
                                "directions you listen for action words and landmarks (go "
                                "straight, turn left, next to the pharmacy), and preview "
                                "today's reading, listening, writing, and map tasks."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has written a clear polite request, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_directions",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="Simple street directions",
                            generation_instructions=(
                                "Write a short set of street directions from a bus stop to a "
                                "station, using direction words and landmarks (go straight, "
                                "turn left at the bakery, next to the pharmacy, on your "
                                "right). Then give True / False / Not Given statements."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tfng'. Provide passage_title, passage, "
                                "and 4 items, each with prompt, correct_answer (True, False, "
                                "or Not Given), and explanation."
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
                        id="listen_infer_directions",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Infer what help someone needs",
                            generation_instructions=(
                                "Generate a help-request dialogue (about 38 seconds) where a "
                                "traveler politely asks for directions to a place, asks about "
                                "distance, and the helper gives directions and a landmark. "
                                "Ask the learner to infer the problem, the place needed, the "
                                "distance question, and the helpful landmark."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_infer'. Provide audio_script, "
                                "intent_focus, and 4 MCQ items, each with prompt, options, "
                                "correct_index, and explanation."
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
                        id="write_idea_para_directions",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_IDEA_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Ask for directions in writing",
                            generation_instructions=(
                                "Ask the learner to write a short polite request for "
                                "directions to a station, including a polite opening, the "
                                "exact place they need, one clear directions question, and a "
                                "thank-you."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, "
                                "grammar_rule, target_words (Excuse me, could you help me, "
                                "station, thank you), minimum_words 24, sample_answer, and "
                                "answer_hints."
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
                        id="speak_pic_desc_directions",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe places on a map",
                            generation_instructions=(
                                "Ask the learner to describe a simple map aloud, saying "
                                "where the station, pharmacy, bakery, and bus stop are using "
                                "place phrases like next to, on the right, and at the bakery."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "a map with a bus stop, bakery, pharmacy, station, and a "
                                "route, grammar_rule, and speaking_duration_seconds: 40."
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
                title="Phone & Online Conversations",
                description=(
                    "Learners identify formal, casual, and urgent tone in "
                    "messages and calls, rewrite messages for a new reader, and "
                    "enjoy relaxed casual small talk."
                ),
                focus="Identify formal, casual, and urgent tone; rewrite messages; and enjoy casual smalltalk.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach recognising and changing tone in messages and calls.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce tone in messages.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that the same "
                                "message can sound formal, casual, or urgent. Read 'Could you "
                                "please call me when you are free?' and ask what tone they "
                                "hear."
                            ),
                        ),
                        TeacherStep(
                            id="make_casual_and_urgent",
                            goal="Change tone and spot urgency.",
                            instruction=(
                                "Confirm it is formal and polite. Ask them to make it casual "
                                "for a friend, and explain that in calls you listen for "
                                "urgency words like now, quickly, or in five minutes. Preview "
                                "that the day ends with relaxed small talk."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has changed the tone correctly at least "
                                "once, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tone_id_messages",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Tone in text messages",
                            generation_instructions=(
                                "Provide two short online messages, one clearly formal and "
                                "one clearly casual, and ask the learner to label each tone "
                                "as Formal, Casual, or Urgent based on word choice and "
                                "punctuation."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tone_id'. Provide passage_title and 2 "
                                "items, each with sender, message, prompt, options (Formal, "
                                "Casual, Urgent), correct_index, and explanation."
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
                        id="listen_tone_phone_call",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Tone in a phone call",
                            generation_instructions=(
                                "Generate a short phone-call clip (about 28 seconds) with "
                                "clear urgency cues (suddenly, now, in the next five "
                                "minutes). Ask the learner to choose the tone that best "
                                "matches the speaker."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_tone'. Provide audio_script and at "
                                "least 1 MCQ item with prompt, options (Formal, Casual, "
                                "Urgent), correct_index, and explanation."
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
                        id="write_paraphrase_register",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="Change message register",
                            generation_instructions=(
                                "Give the learner one formal message to rewrite as a casual "
                                "text and one casual text to rewrite as a polite formal "
                                "message, keeping the meaning the same while changing the "
                                "level of formality."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paraphrase'. Provide 2 items, each "
                                "with incorrect_sentence (the message to convert), "
                                "sample_answer, and watch_hints."
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
                        id="speak_smalltalk_weekend",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Casual weekend chat",
                            generation_instructions=(
                                "Set up relaxed small talk about the weather and weekend "
                                "plans, where the learner answers two turns in a friendly "
                                "casual tone with one simple weekend detail each."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_smalltalk'. Provide a dialogue_context "
                                "alternating partner and learner turns, target_words (That "
                                "sounds fun, I might, usually, weekend), and "
                                "speaking_duration_seconds: 35."
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
                title="Small Talk & Social Interaction",
                description=(
                    "A communication wrap-up: learners build natural fluency by "
                    "connecting ideas with simple connectors, retelling a casual "
                    "chat, writing to a friend, and giving a low-pressure spoken "
                    "summary of their week."
                ),
                focus="Build natural fluency with friendly chat, week review, short messages, and a spoken wrap-up.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach natural small talk that connects ideas and keeps a chat moving.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Reframe fluency as connection.",
                            instruction=(
                                "Greet the learner for the small-talk wrap-up. Explain in "
                                "two sentences that natural fluency is not long sentences; "
                                "it is connecting ideas, responding warmly, and keeping the "
                                "chat moving. Invite a short reaction."
                            ),
                        ),
                        TeacherStep(
                            id="connectors",
                            goal="Teach simple connectors.",
                            instruction=(
                                "Explain that a good chat uses simple connectors (first, "
                                "then, also, but, because). Ask them to tell you one good "
                                "thing and one busy thing from their week, and preview "
                                "today's reading, retell, message, and spoken summary tasks."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has connected two ideas naturally, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_structure_smalltalk",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_STRUCTURE_ID",
                            activity="read",
                            task_widget="read_structure",
                            topic_override="Small-talk chat structure",
                            generation_instructions=(
                                "Provide a short friendly chat thread in 3 parts and ask the "
                                "learner to label each part as the Opening (greeting and "
                                "check-in), Shared Details (connected details about each "
                                "person), or Reflection (closing feelings and next step)."
                            ),
                            widget_requirements=(
                                "Target widget 'read_structure'. Provide passage_title, "
                                "structure_labels ['Opening', 'Shared Details', "
                                "'Reflection'], and 3 items, each with label, paragraph, "
                                "correct_answer, and explanation."
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
                        id="listen_retell_smalltalk",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Retell a casual conversation",
                            generation_instructions=(
                                "Generate a casual conversation (about 55 seconds) where two "
                                "friends compare their busy weeks and agree they want a quiet "
                                "Sunday. Ask the learner to retell the key points in writing "
                                "in their own words (who spoke, key activities, shared "
                                "feeling)."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_retell'. Set response_mode to "
                                "'written'. Provide audio_script, passage_to_retell, "
                                "target_words, and grammar_rule."
                            ),
                        ),
                        evaluation=EvaluationBlueprint(
                            evaluator="llm_writing",
                            evaluation_widget="read_listen_evaluation",
                        ),
                        feedback=FeedbackBlueprint(
                            feedback_widget="read_listen_feedback",
                        ),
                    ),
                    ActivityBlueprint(
                        id="write_email_smalltalk",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Message a friend about your week",
                            generation_instructions=(
                                "Ask the learner to write a short friendly message (45-60 "
                                "words) to a friend about their week, including a friendly "
                                "opening, two activities in simple past, one feeling "
                                "sentence, and a natural closing."
                            ),
                            widget_requirements=(
                                "Target widget 'write_email'. Provide prompt, grammar_rule, "
                                "target_words, minimum_words 45, sample_answer (with To and "
                                "Subject lines), and answer_hints."
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
                        id="speak_present_my_week",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="This is my week",
                            generation_instructions=(
                                "Ask the learner to speak for up to 60 seconds about their "
                                "week using a simple structure: an overall feeling, two "
                                "weekly activities, and one closing plan for next week."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_present'. Provide grammar_rule, "
                                "target_words (This week, I finished, I also, Next week), a "
                                "visual_prompt_description, an optional model_presentation, "
                                "and speaking_duration_seconds: 60."
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
        ),
    ),
    WeekSource(
        week_number=3,
        theme_type="vocabulary",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=(
            DaySource(
                title="People & Relationships - Family, Friends & Roles",
                description=(
                    "Learners build vocabulary for the people in their lives - "
                    "family, friends, colleagues, neighbours, classmates - and "
                    "describe each person's role."
                ),
                focus="Vocabulary for describing family, friends, colleagues, neighbours, and their roles.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach relationship and role vocabulary for people in our lives.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce people and role words.",
                            instruction=(
                                "Welcome the learner to vocabulary week. Explain in two "
                                "sentences that we use words like uncle (a parent's brother) "
                                "and colleague (someone you work with) to describe people. "
                                "Ask who is someone they work with."
                            ),
                        ),
                        TeacherStep(
                            id="role_words",
                            goal="Practise community and family roles.",
                            instruction=(
                                "Confirm 'colleague'. Ask what they call the person who "
                                "lives next door, then summarise the contrast: colleague for "
                                "work, neighbour for where you live, uncle for family, and "
                                "preview today's match, listen, transform, and photo tasks."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has named a role word correctly, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_people",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Family, Friends & Roles",
                            generation_instructions=(
                                "Ask the learner to match relationship and role words "
                                "(uncle, colleague, neighbour, classmate) to short "
                                "definitions describing family, work, community, and school "
                                "roles."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options (the role "
                                "words) and 4 items, each with prompt (the definition), "
                                "correct_answer, and explanation."
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
                        id="listen_mcq_people",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Identifying People in a Dialogue",
                            generation_instructions=(
                                "Generate a short scenario (about 30 seconds) where a host "
                                "introduces several people by their role (an uncle visiting, "
                                "a colleague from the office, a neighbour next door). Ask the "
                                "learner who each person is and how they relate to the "
                                "speaker."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ "
                                "items, each with prompt, options, correct_index, and "
                                "explanation."
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
                        id="write_sent_trans_people",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Vocabulary sentence transformation",
                            generation_instructions=(
                                "Give the learner 2-3 wordy descriptions of people (a person "
                                "I work with, a student in my class) and ask them to rewrite "
                                "each using the precise role word (colleague, classmate)."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 2-3 items, each "
                                "with source_sentence, sample_answer, and watch_hints."
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
                        id="speak_pic_desc_people",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a family photo",
                            generation_instructions=(
                                "Ask the learner to describe a photo of people aloud, naming "
                                "who is who using relationship words such as uncle, "
                                "colleague, and neighbour."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "a small group photo with an uncle, a colleague, and a "
                                "neighbour, grammar_rule, and speaking_duration_seconds: 45."
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
                title="Food & Eating - Meals, Ingredients & Taste",
                description=(
                    "Learners build vocabulary for meals, ingredients, and "
                    "describing taste (delicious, flavourful, bland, savoury) and "
                    "upgrade simple food words to richer ones."
                ),
                focus="Vocabulary for meals, food ingredients, and describing taste (delicious, flavourful, bland, savoury).",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach food, ingredient, and taste vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce taste words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that savoury "
                                "means salty or spicy food and bland means lacking flavour. "
                                "Ask for a word to describe a dish with a rich, pleasant "
                                "taste."
                            ),
                        ),
                        TeacherStep(
                            id="ingredients",
                            goal="Practise ingredient words.",
                            instruction=(
                                "Confirm strong words like delicious or flavourful. Ask for "
                                "two typical ingredients in a fresh salad, then preview "
                                "today's menu reading, cafe-order listening, word-upgrade "
                                "writing, and a timed favourite-meal speech."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has produced a taste or ingredient word, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_context_mcq_food",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Food & Eating",
                            generation_instructions=(
                                "Write a short restaurant menu passage that contrasts "
                                "savoury dishes with sweet desserts, then ask the learner to "
                                "infer the meaning of 'savoury' from context."
                            ),
                            widget_requirements=(
                                "Target widget 'read_context_mcq'. Provide passage_title, "
                                "passage, and at least 1 MCQ item with prompt, options, "
                                "correct_index, and explanation."
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
                        id="listen_dictation_food",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="Ordering Food",
                            generation_instructions=(
                                "Generate a short, polite cafe food order (about 12 seconds) "
                                "with precise ingredient vocabulary, and ask the learner to "
                                "type the exact sentence they hear."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_dictation'. Provide audio_script, "
                                "target_words (the key food items), and 1 dictation item "
                                "with prompt, correct_answer, and explanation."
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
                        id="write_word_upgrade_food",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_WORD_UPGRADE",
                            activity="write",
                            task_widget="write_word_upgrade",
                            topic_override="Vocabulary Word Upgrade",
                            generation_instructions=(
                                "Give the learner 3 plain food sentences (the food is good, "
                                "the soup has no taste, the sauce has nice flavours) and ask "
                                "them to rewrite each using a premium taste word (delicious, "
                                "bland, flavourful)."
                            ),
                            widget_requirements=(
                                "Target widget 'write_word_upgrade'. Provide 3 items, each "
                                "with source_sentence, target_upgrade_word, sample_answer, "
                                "and watch_hints."
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
                        id="speak_timed_food",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Timed Monologue Speech",
                            generation_instructions=(
                                "Ask the learner to describe their favourite meal for up to "
                                "60 seconds, covering its ingredients, how it tastes (using "
                                "taste words), and when they usually eat it."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a "
                                "sample_response, grammar_rule, target_words (delicious, "
                                "ingredients, savoury, taste), and "
                                "speaking_duration_seconds: 60."
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
                title="Places & Locations - City, Home & Directions",
                description=(
                    "Learners build vocabulary for places and city locations "
                    "(market, station, suburb, city) and describe their own "
                    "neighbourhood."
                ),
                focus="Vocabulary for places, city locations, and describing neighbourhoods.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach place and location vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce place words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that a market "
                                "is where you buy fresh food, a station is where you catch a "
                                "train, and a suburb is a quiet area outside the city. Ask "
                                "where they usually buy fresh vegetables."
                            ),
                        ),
                        TeacherStep(
                            id="more_places",
                            goal="Practise more place words.",
                            instruction=(
                                "Confirm 'market'. Ask where they go to travel to another "
                                "city, then preview today's match, neighbourhood listening, "
                                "short paragraph, and city-picture tasks."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a place word correctly, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_places",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Places & Locations",
                            generation_instructions=(
                                "Ask the learner to match place words (market, station, "
                                "suburb, city) to short definitions."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options (the place "
                                "words) and 4 items, each with prompt (the definition), "
                                "correct_answer, and explanation."
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
                        id="listen_mcq_places",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Neighbourhood description",
                            generation_instructions=(
                                "Generate a short monologue (about 25 seconds) where someone "
                                "describes living in a suburb, buying food at a market, and "
                                "walking to a station. Ask comprehension questions about "
                                "where they live, what they buy, and how they travel."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ "
                                "items, each with prompt, options, correct_index, and "
                                "explanation."
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
                        id="write_para_places",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Describe your area",
                            generation_instructions=(
                                "Ask the learner to write 3-4 simple present sentences about "
                                "the area where they live, including the words market and "
                                "station."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, "
                                "grammar_rule, target_words (market, station, live, near), "
                                "minimum_words 20, sample_answer, and answer_hints."
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
                        id="speak_pic_desc_places",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a city map",
                            generation_instructions=(
                                "Ask the learner to describe a simple city map aloud, naming "
                                "the market, station, and suburb using 'There is' or 'I can "
                                "see'."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "a city map with a market, a station, and a suburb, "
                                "grammar_rule, and speaking_duration_seconds: 45."
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
                title="Work & Jobs - Roles, Actions & Workplace",
                description=(
                    "Learners build vocabulary for job roles, workplace actions, "
                    "and describing what people do at work (manager, receptionist, "
                    "responsible for, works in, manages)."
                ),
                focus="Vocabulary for job roles, workplace actions, and describing what people do at work.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach job-role and workplace-action vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce job roles.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that a manager "
                                "leads a team and a receptionist greets visitors and answers "
                                "calls. Ask what they call someone who is responsible for a "
                                "project."
                            ),
                        ),
                        TeacherStep(
                            id="workplace_actions",
                            goal="Practise workplace action verbs.",
                            instruction=(
                                "Confirm and explain that 'responsible for' means in charge "
                                "of, and 'manages' means organises and leads. Ask which verb "
                                "describes a person who works in an office or hospital, then "
                                "preview today's job-ad reading, dictation, rewrite, and "
                                "timed speech."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a work word correctly, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_context_mcq_work",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Job Advertisements",
                            generation_instructions=(
                                "Write a short job advertisement that lists duties (organise "
                                "meetings, manage a small team, keep the office running) and "
                                "ask the learner to infer the meaning of 'responsible for' "
                                "from context."
                            ),
                            widget_requirements=(
                                "Target widget 'read_context_mcq'. Provide passage_title, "
                                "passage, and at least 1 MCQ item with prompt, options, "
                                "correct_index, and explanation."
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
                        id="listen_dictation_work",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="Job Description",
                            generation_instructions=(
                                "Generate a short job description (about 14 seconds) using a "
                                "job-title noun and workplace action verbs (works as, "
                                "manages), and ask the learner to type the exact sentence."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_dictation'. Provide audio_script, "
                                "target_words (the key job nouns and verbs), and 1 dictation "
                                "item with prompt, correct_answer, and explanation."
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
                        id="write_paraphrase_work",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="Rewrite with job vocabulary",
                            generation_instructions=(
                                "Give the learner 2 plain sentences about work (he works in "
                                "an office, she tells people what to do) and ask them to "
                                "rewrite each using more precise job vocabulary (employed "
                                "as, manages a team)."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paraphrase'. Provide 2 items, each "
                                "with incorrect_sentence (the plain sentence), sample_answer, "
                                "and watch_hints."
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
                        id="speak_timed_work",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Timed Job Description Speech",
                            generation_instructions=(
                                "Ask the learner to talk for up to 60 seconds about a job "
                                "they know, describing what the person does, where they "
                                "work, and why the job is important, using workplace "
                                "vocabulary."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a "
                                "sample_response, grammar_rule, target_words (manager, "
                                "responsible for, works in, team), and "
                                "speaking_duration_seconds: 60."
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
                title="Time & Schedules - Days, Months & Routines",
                description=(
                    "Learners build precise time-frequency vocabulary "
                    "(fortnightly, quarterly, deadline, daily, weekly, "
                    "occasionally) and use it to describe schedules."
                ),
                focus="Vocabulary for time expressions: fortnightly, quarterly, deadline, daily, weekly, occasionally.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach precise time and schedule vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce frequency words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that words like "
                                "daily, weekly, and fortnightly tell us how often something "
                                "happens, and a deadline is the latest time to finish. Ask "
                                "what word describes something happening every two weeks."
                            ),
                        ),
                        TeacherStep(
                            id="more_frequency",
                            goal="Practise more frequency words.",
                            instruction=(
                                "Confirm 'fortnightly'. Ask what word fits a meeting held "
                                "four times a year, then preview today's match, week-"
                                "planning listening, time-adverb transform, and planner "
                                "picture tasks."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a time word correctly, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_time",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Time & Schedule Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match time-frequency words "
                                "(fortnightly, quarterly, deadline, occasionally) to their "
                                "meanings."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options (the time "
                                "words) and 4 items, each with prompt (the meaning), "
                                "correct_answer, and explanation."
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
                        id="listen_mcq_time",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Planning the Week",
                            generation_instructions=(
                                "Generate a weekly-planning monologue (about 40 seconds) "
                                "that uses several frequency words (daily emails, fortnightly "
                                "team meeting, a Thursday deadline, occasional gym, quarterly "
                                "strategy meeting). Ask comprehension questions about how "
                                "often things happen and when the deadline is."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ "
                                "items, each with prompt, options, correct_index, and "
                                "explanation."
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
                        id="write_sent_trans_time",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Time expression sentence transformation",
                            generation_instructions=(
                                "Give the learner 3 wordy time phrases (every day, every "
                                "week, sometimes not very often) and ask them to rewrite "
                                "each using a precise time adverb (daily, weekly, "
                                "occasionally)."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 3 items, each "
                                "with source_sentence, sample_answer, and watch_hints."
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
                        id="speak_pic_desc_time",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a weekly planner",
                            generation_instructions=(
                                "Ask the learner to describe a weekly planner aloud, using "
                                "time-frequency words (daily, weekly, quarterly, deadline, "
                                "occasionally) to say how often events happen."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "a Monday-to-Friday planner with daily standups, a Thursday "
                                "deadline, a quarterly review, and occasional gym sessions, "
                                "grammar_rule, and speaking_duration_seconds: 45."
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
                title="Feelings & Emotions - Express inner states",
                description=(
                    "Learners build vocabulary to express feelings precisely "
                    "(overwhelmed, content, devastated, disappointed, "
                    "disheartened) and upgrade plain emotion words."
                ),
                focus="Vocabulary for expressing feelings and emotions: overwhelmed, content, devastated, disappointed, disheartened.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach precise vocabulary for feelings and emotions.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce precise emotion words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that 'content' "
                                "means peaceful and satisfied and 'overwhelmed' means having "
                                "too much to do. Ask what word they would use when stressed "
                                "with too much to do."
                            ),
                        ),
                        TeacherStep(
                            id="stronger_words",
                            goal="Practise stronger emotion words.",
                            instruction=(
                                "Confirm 'overwhelmed'. Explain 'disappointed' (sad it did "
                                "not happen as hoped) and ask for a stronger word for "
                                "extremely sad or shocked, then preview today's diary "
                                "reading, dictation, word-upgrade, and feelings speech."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has produced a precise emotion word, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_context_mcq_feelings",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Infer emotions from context",
                            generation_instructions=(
                                "Write a short diary entry whose mood shifts from content "
                                "(after finishing a stressful project) to disappointed (a "
                                "cancelled plan) to devastated (losing an expensive item). "
                                "Ask the learner to infer the emotion at each point."
                            ),
                            widget_requirements=(
                                "Target widget 'read_context_mcq'. Provide passage_title, "
                                "passage, and 3 MCQ items, each with prompt, options, "
                                "correct_index, and explanation."
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
                        id="listen_dictation_feelings",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="Dictate emotion words",
                            generation_instructions=(
                                "Generate a short personal description (about 45 seconds) in "
                                "which the speaker names feelings (overwhelmed, "
                                "disheartened). Ask the learner to type the exact emotion "
                                "word that completes each blanked sentence."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_dictation'. Provide audio_script, "
                                "target_words (the emotion words), and 2 dictation items, "
                                "each with a prompt sentence containing a blank, "
                                "correct_answer, and explanation."
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
                        id="write_word_upgrade_feelings",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_WORD_UPGRADE",
                            activity="write",
                            task_widget="write_word_upgrade",
                            topic_override="Upgrade emotion vocabulary",
                            generation_instructions=(
                                "Give the learner 3 plain emotion sentences (very sad, "
                                "stressed, sad) and ask them to rewrite each using a stronger "
                                "emotion word (devastated, overwhelmed, disappointed)."
                            ),
                            widget_requirements=(
                                "Target widget 'write_word_upgrade'. Provide 3 items, each "
                                "with source_sentence, target_upgrade_word, sample_answer, "
                                "and watch_hints."
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
                        id="speak_timed_feelings",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Talk about your feelings",
                            generation_instructions=(
                                "Ask the learner to talk about how they felt today or this "
                                "week using at least one strong emotion word and explaining "
                                "why they felt that way."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a "
                                "sample_response, grammar_rule, target_words (content, "
                                "overwhelmed, disappointed, devastated, disheartened), and "
                                "speaking_duration_seconds: 45."
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
                title="Review & Word Building - Consolidate the week's vocab",
                description=(
                    "A vocabulary review day: learners consolidate the week's "
                    "words across People, Food, Places, Work, Time, and Feelings "
                    "through matching, listening, free recall writing, and a "
                    "speaking challenge."
                ),
                focus="Consolidate the week's vocabulary covering People, Food, Places, Work, Time, and Feelings.",
                teacher=TeacherBlueprint(
                    lesson_goal="Consolidate the week's vocabulary across all six topics.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the review day.",
                            instruction=(
                                "Greet the learner for the weekly review. Explain in one "
                                "sentence that today consolidates the week's words across "
                                "People, Food, Places, Work, Time, and Feelings. Ask if they "
                                "are ready for a challenge."
                            ),
                        ),
                        TeacherStep(
                            id="recall_prompt",
                            goal="Prompt active recall.",
                            instruction=(
                                "Explain that reviewing moves words into long-term memory. "
                                "Ask them to recall one strong word from the week (for "
                                "example a word meaning very sad or shocked), then preview "
                                "today's match, story listening, free-recall paragraph, and "
                                "90-second speaking challenge."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has recalled at least one word, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_review",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Weekly Review Match",
                            generation_instructions=(
                                "Ask the learner to match 6 words from across the week (one "
                                "per topic, for example colleague, savoury, suburb, manager, "
                                "deadline, content) to their definitions."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options (the 6 "
                                "words) and 6 items, each with prompt (the definition), "
                                "correct_answer, and explanation."
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
                        id="listen_mcq_review",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Weekend consolidation story",
                            generation_instructions=(
                                "Generate a short personal story (about 28 seconds) that "
                                "weaves in vocabulary from all six topics (colleague, "
                                "savoury, suburb, manager, deadline, overwhelmed, content). "
                                "Ask comprehension questions that depend on those words."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ "
                                "items, each with prompt, options, correct_index, and "
                                "explanation."
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
                        id="write_para_review",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Free recall writing",
                            generation_instructions=(
                                "Ask the learner to write a short paragraph (3-5 sentences) "
                                "on any topic that uses at least 5 words learned this week, "
                                "integrating them smoothly."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, "
                                "grammar_rule, target_words (the week's words), "
                                "minimum_words 25, sample_answer, and answer_hints."
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
                        id="speak_timed_review",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Playful end-of-week recall challenge",
                            generation_instructions=(
                                "Ask the learner to talk for up to 90 seconds on any topic, "
                                "using as many of this week's vocabulary words as they can "
                                "in natural, spontaneous speech."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a "
                                "sample_response, grammar_rule, target_words (the week's "
                                "words), and speaking_duration_seconds: 90."
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
        ),
    ),
    WeekSource(
        week_number=4,
        theme_type="confidence",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=(
            DaySource(
                title="Finding your voice - Start speaking without fear",
                description=(
                    "Learners start speaking without fear: a motivation story, "
                    "shadowing a confident voice, reframing negative self-talk into "
                    "growth language, and a low-stakes read-aloud."
                ),
                focus="Start speaking without fear: simple motivation stories, shadowing practice, low-stakes transforms, and reading aloud.",
                teacher=TeacherBlueprint(
                    lesson_goal="Build a fearless speaking mindset to open confidence week.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Shift the mindset on mistakes.",
                            instruction=(
                                "Welcome the learner to confidence week. Explain in two "
                                "sentences that mistakes are stepping stones to fluency, not "
                                "failures. Ask them to say one positive thing about "
                                "practising English."
                            ),
                        ),
                        TeacherStep(
                            id="preview",
                            goal="Preview the day and reassure.",
                            instruction=(
                                "Affirm their reason warmly. Preview that today they will "
                                "read a short motivational story, shadow a confident voice, "
                                "rewrite a negative sentence into positive self-expression, "
                                "and read a short paragraph aloud."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner sounds ready, ask only: Ready to try the "
                                "practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_finding_voice",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Overcoming fear story",
                            generation_instructions=(
                                "Write a short, encouraging story about a nervous learner "
                                "who takes a deep breath, volunteers to speak, and discovers "
                                "that speaking up is about being heard, not being perfect. "
                                "Then ask comprehension questions about the fear, the "
                                "turning point, and the lesson learned."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, "
                                "passage, and 4 MCQ items, each with prompt, options, "
                                "correct_index, and explanation."
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
                        id="listen_shadow_finding_voice",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Confidence Shadowing",
                            generation_instructions=(
                                "Generate a short, warm motivational monologue (about 15 "
                                "seconds) that reframes speaking as a bridge for sharing "
                                "your voice, for the learner to shadow with natural pacing "
                                "and confidence."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_shadow'. Provide audio_script, "
                                "text_to_shadow (a sentence or two from the script), "
                                "target_words, and grammar_rule."
                            ),
                        ),
                        evaluation=EvaluationBlueprint(
                            evaluator="speaking_eval",
                            evaluation_widget="read_aloud_assessment",
                        ),
                        feedback=FeedbackBlueprint(
                            feedback_widget="read_aloud_assessment",
                        ),
                    ),
                    ActivityBlueprint(
                        id="write_sent_trans_finding_voice",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Low-stakes self-expression reframe",
                            generation_instructions=(
                                "Give the learner 3 self-limiting statements (I am shy, I "
                                "always make mistakes, I cannot speak English) and ask them "
                                "to reframe each into positive growth language using "
                                "proactive verbs (working on, learn from, building)."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 3 items, each "
                                "with source_sentence, sample_answer, and watch_hints."
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
                        id="speak_read_aloud_finding_voice",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_READ_ALOUD",
                            activity="speak",
                            task_widget="read_aloud",
                            topic_override="Motivational paragraph read aloud",
                            generation_instructions=(
                                "Give the learner a short, positive self-affirmation "
                                "paragraph (about 30 words, for example about their voice "
                                "having value and not needing to be perfect) to read aloud "
                                "with clear pronunciation and steady pacing."
                            ),
                            widget_requirements=(
                                "Target widget 'read_aloud'. Provide text_to_read_aloud, "
                                "grammar_rule about clear pronunciation and breathing "
                                "pauses, target_words, and speaking_duration_seconds: 30."
                            ),
                        ),
                        evaluation=EvaluationBlueprint(
                            evaluator="speaking_eval",
                            evaluation_widget="read_aloud_assessment",
                        ),
                        feedback=FeedbackBlueprint(
                            feedback_widget="read_aloud_assessment",
                        ),
                    ),
                ),
            ),
            DaySource(
                title="Sharing opinions - Say what you think clearly",
                description=(
                    "Learners state opinions clearly and confidently, tell "
                    "confident tone from hesitant hedging, and write and speak "
                    "their views under time pressure without overthinking."
                ),
                focus="State your opinion clearly and confidently, notice the difference between confident and uncertain tone, and write/speak under time pressure.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach sharing opinions clearly and confidently.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Contrast confident and hesitant tone.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that sharing "
                                "opinions is about how you say it. Compare a confident line "
                                "(absolutely convinced) with a hesitant one (I guess, I "
                                "don't know) and ask which sounds more confident."
                            ),
                        ),
                        TeacherStep(
                            id="confident_markers",
                            goal="Name confident vs hedging markers.",
                            instruction=(
                                "Confirm the confident one. Explain that strong words "
                                "(convinced, absolutely) sound sure while hedges (guess, "
                                "maybe, I don't know) sound uncertain, and preview that "
                                "today they will distinguish tones and write and speak their "
                                "views clearly under time pressure."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner is ready, ask only: Ready to try the "
                                "practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tone_id_opinions",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Tone awareness in opinions",
                            generation_instructions=(
                                "Provide two short opinions on the same topic, one clearly "
                                "confident (strong words, direct verbs) and one clearly "
                                "hesitant (hedges and fillers), and ask the learner to label "
                                "each as Confident or Hesitant."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tone_id'. Provide passage_title and 2 "
                                "items, each with sender, message, prompt, options "
                                "(Hesitant / Uncertain, Confident / Sure), correct_index, "
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
                        id="listen_mcq_opinions",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Confident Speech Patterns",
                            generation_instructions=(
                                "Generate a clip (about 22 seconds) of two speakers giving "
                                "opinions on the same topic: one hesitant with fillers, one "
                                "confident and structured. Ask the learner which speaker "
                                "sounds more confident."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and at "
                                "least 1 MCQ item with prompt, options, correct_index, and "
                                "explanation."
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
                        id="write_timed_opinions",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Timed Opinion Write",
                            generation_instructions=(
                                "Ask the learner to state their opinion on remote work "
                                "clearly in at least 25 words under a short time limit, "
                                "using strong opinion verbs and markers without "
                                "overthinking."
                            ),
                            widget_requirements=(
                                "Target widget 'write_timed'. Provide prompt, grammar_rule, "
                                "target_words (opinion, remote, productivity, convinced, "
                                "believe), writing_duration_seconds: 180, sample_answer, and "
                                "answer_hints."
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
                        id="speak_timed_opinions",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Timed Improvised Opinion Speech",
                            generation_instructions=(
                                "Ask the learner to speak for up to 60 seconds on whether "
                                "online classes are better than traditional learning, "
                                "stating their view clearly, giving one reason, and "
                                "concluding with conviction."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a "
                                "sample_response, grammar_rule, target_words (opinion, "
                                "online, traditional, confident, prefer), and "
                                "speaking_duration_seconds: 60."
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
                title="Describing yourself - Talk about who you are",
                description=(
                    "Learners build an expressive self-identity, tell formal from "
                    "casual introductions, enrich plain self-descriptions, and "
                    "practise safe self-expression by describing others."
                ),
                focus="Talk about who you are: build expressive self-identity, distinguish formal vs. casual introductions, and practice safe self-expression through describing others.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach describing yourself with richer, register-aware language.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Invite a simple self-introduction.",
                            instruction=(
                                "Greet the learner. Explain in one sentence that expressing "
                                "who you are helps you connect with others. Ask them to "
                                "introduce themselves in one simple sentence."
                            ),
                        ),
                        TeacherStep(
                            id="formal_casual",
                            goal="Contrast formal and casual self-description.",
                            instruction=(
                                "Affirm their start. Explain that descriptions can be formal "
                                "(I am a software engineer) or casual (I build apps), and "
                                "preview today's bio reading, formal-versus-casual "
                                "listening, richer-description writing, and a describe-a-"
                                "person speaking task."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner is ready, ask only: Ready to try the "
                                "practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_describing_self",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="A personal bio",
                            generation_instructions=(
                                "Write a short first-person bio of a professional who links "
                                "their job titles with a personal motivation (for example a "
                                "marine biologist and photographer who wants to inspire "
                                "conservation). Then ask comprehension questions about their "
                                "job, self-description, motivation, and daily work."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, "
                                "passage, and 4 MCQ items, each with prompt, options, "
                                "correct_index, and explanation."
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
                        id="listen_tone_describing_self",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Formal vs. Casual self-description",
                            generation_instructions=(
                                "Generate two versions of the same person introducing "
                                "themselves: a formal version (It is a pleasure to meet you, "
                                "specialize in) and a casual version (Hey there, huge "
                                "bookworm). Ask the learner to label each version's tone."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_tone'. Provide two intros (each with "
                                "id, label, speaker, audio_script) and 2 MCQ items, each "
                                "with prompt, options (Formal / Professional, Casual / "
                                "Informal), correct_index, and explanation."
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
                        id="write_sent_trans_describing_self",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Richer self-description transforms",
                            generation_instructions=(
                                "Give the learner 3 plain self-statements (I like soccer, I "
                                "am a programmer, I live in Berlin) and ask them to rewrite "
                                "each into a richer, more expressive self-description with "
                                "added feeling or detail (passionate about, work as, reside "
                                "in)."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 3 items, each "
                                "with source_sentence, sample_answer, and watch_hints."
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
                        id="speak_pic_desc_describing_self",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe an activity outdoors",
                            generation_instructions=(
                                "Ask the learner to describe a picture of a person doing an "
                                "activity outdoors, saying what they are doing and what kind "
                                "of person they might be, using speculative phrases like "
                                "looks like, seems to be, and might be."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "a person painting a mountain landscape outdoors by a lake, "
                                "grammar_rule about speculative language, and "
                                "speaking_duration_seconds: 45."
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
                title="Handling awkward moments - Recover from mistakes gracefully",
                description=(
                    "Learners learn to recover from mistakes gracefully: spot tone "
                    "shifts after a slip, shadow mid-sentence self-corrections, "
                    "reflect on mistakes under time, and handle unpredictable small "
                    "talk."
                ),
                focus="Recover from mistakes gracefully: short dialogue tone shift identification, mid-sentence self-correction shadowing, timed reflection write, and unpredictable small talk challenge.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach graceful recovery from speaking mistakes.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Normalise mistakes.",
                            instruction=(
                                "Greet the learner. Explain in one sentence that making "
                                "mistakes in a second language is completely normal. Ask "
                                "what their biggest worry is when they slip up while "
                                "speaking."
                            ),
                        ),
                        TeacherStep(
                            id="recover_gracefully",
                            goal="Teach that recovery matters more than the slip.",
                            instruction=(
                                "Reassure them that people notice how you recover, not the "
                                "slip itself, and that a smooth correction makes the mistake "
                                "vanish. Preview today's tone-shift reading, self-correction "
                                "shadowing, timed reflection, and small-talk challenge."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner is ready, ask only: Ready to try the "
                                "practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tone_id_awkward",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Awkward moment tone shift",
                            generation_instructions=(
                                "Provide two short messages where a speaker makes a slip and "
                                "then recovers gracefully, and ask the learner to identify "
                                "the tone shift in each (for example anxious to composed, "
                                "startled to helpful)."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tone_id'. Provide passage_title and 2 "
                                "items, each with sender, message, prompt, options "
                                "describing tone shifts, correct_index, and explanation."
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
                        id="listen_shadow_awkward",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Graceful self-correction",
                            generation_instructions=(
                                "Generate a short clip (about 20 seconds) where a speaker "
                                "self-corrects mid-sentence using markers like 'Oh, wait', "
                                "'I mean', and 'Actually', for the learner to shadow with "
                                "the same natural flow."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_shadow'. Provide audio_script, "
                                "text_to_shadow, target_words (Oh wait, I mean, Actually), "
                                "and grammar_rule."
                            ),
                        ),
                        evaluation=EvaluationBlueprint(
                            evaluator="speaking_eval",
                            evaluation_widget="read_aloud_assessment",
                        ),
                        feedback=FeedbackBlueprint(
                            feedback_widget="read_aloud_assessment",
                        ),
                    ),
                    ActivityBlueprint(
                        id="write_timed_awkward",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Reflecting on mistakes",
                            generation_instructions=(
                                "Ask the learner to write a short personal reflection under "
                                "a short time limit on what they do when they make a mistake "
                                "while speaking, using transition words to organise their "
                                "thoughts."
                            ),
                            widget_requirements=(
                                "Target widget 'write_timed'. Provide prompt, grammar_rule, "
                                "target_words (Usually, Instead of, Simply), "
                                "writing_duration_seconds: 180, sample_answer, and "
                                "answer_hints."
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
                        id="speak_smalltalk_awkward",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Unpredictable small talk",
                            generation_instructions=(
                                "Set up an unpredictable small-talk exchange where the "
                                "partner asks about a recent slip and the learner responds "
                                "gracefully, using transition words to keep the conversation "
                                "flowing."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_smalltalk'. Provide a dialogue_context "
                                "alternating partner and learner turns, target_words "
                                "(Actually, Simply, Instead of), and "
                                "speaking_duration_seconds: 30."
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
                title="Talking about interests - Express hobbies & passions",
                description=(
                    "Learners express their passions and interests with "
                    "confidence: light reading about a hobby, an enthusiastic "
                    "monologue, upgrading plain hobby descriptions, and describing "
                    "a hobby scene."
                ),
                focus="Expressing your passions and interests with confidence: light reading about stargazing, enthusiastic gardening monologues, sentence transformation for premium vocabulary, and describing an outdoor hobby scene.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach expressing interests and passions with enthusiasm.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Invite a real hobby.",
                            instruction=(
                                "Greet the learner. Explain in one sentence that sharing "
                                "what you love builds connection and natural confidence. Ask "
                                "what one hobby they really enjoy in their free time."
                            ),
                        ),
                        TeacherStep(
                            id="express_passion",
                            goal="Model expressive enthusiasm.",
                            instruction=(
                                "React warmly and note that talking about passions makes us "
                                "sound more expressive. Preview today's stargazing reading, "
                                "enthusiastic gardening listening, hobby word-upgrade "
                                "writing, and a hobby-scene speaking task."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner is ready, ask only: Ready to try the "
                                "practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_interests",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Passionate about stargazing",
                            generation_instructions=(
                                "Write a warm first-person passage about a relaxing hobby "
                                "(for example stargazing) covering what sparked it, a proud "
                                "moment, how it affects the narrator's mind, and beginner "
                                "advice. Then ask comprehension questions about each."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, "
                                "passage, and 4 MCQ items, each with prompt, options, "
                                "correct_index, and explanation."
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
                        id="listen_mcq_interests",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Enthusiasm for gardening",
                            generation_instructions=(
                                "Generate an enthusiastic monologue (about 25 seconds) where "
                                "someone describes their indoor gardening hobby (favourite "
                                "plant, how long they have done it, a daily routine). Ask "
                                "comprehension questions about those details."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ "
                                "items, each with prompt, options, correct_index, and "
                                "explanation."
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
                        id="write_sent_trans_interests",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Hobby vocabulary upgrade",
                            generation_instructions=(
                                "Give the learner 3 basic hobby statements (I watch movies, "
                                "I play guitar, I like cooking) and ask them to transform "
                                "each into an expressive, confident description using high-"
                                "enthusiasm patterns (huge fan, passionate about, favourite "
                                "way to unwind)."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 3 items, each "
                                "with source_sentence, sample_answer, and watch_hints."
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
                        id="speak_pic_desc_interests",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Gardening scene description",
                            generation_instructions=(
                                "Ask the learner to describe a hobby scene aloud (the scene, "
                                "the hobby shown) and connect it to their own interests, "
                                "using speculative language and descriptive details."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "a vibrant garden corner with potted plants, blooming "
                                "flowers, and a red watering can, grammar_rule, and "
                                "speaking_duration_seconds: 45."
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
                title="Presenting yourself - Speak with structure and poise",
                description=(
                    "Learners present themselves with poise: tell hesitant from "
                    "polished introductions, train their ear for vocal confidence, "
                    "draft a 3-sentence self-introduction under time, and record a "
                    "structured 90-second presentation."
                ),
                focus="Presenting yourself with poise: identify differences between hesitant and polished introductions, train your ear for vocal confidence tone shifts, timed write a 3-sentence self-introduction, and record a structured 90-second personal presentation.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach presenting yourself with structure and poise.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Surface what a good introduction includes.",
                            instruction=(
                                "Greet the learner. Explain in one sentence that a "
                                "structured, polished introduction makes a strong impression "
                                "in professional or social settings. Ask what they usually "
                                "include when introducing themselves to someone new."
                            ),
                        ),
                        TeacherStep(
                            id="structure_poise",
                            goal="Add structure and poise.",
                            instruction=(
                                "Affirm their foundation and explain that adding structure "
                                "and speaking with poise sounds more confident. Preview "
                                "today's hesitant-versus-polished reading, tone-shift "
                                "listening, timed 3-sentence note, and a 90-second recorded "
                                "self-introduction."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner is ready, ask only: Ready to try the "
                                "practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tone_id_presenting",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Tone identification in introductions",
                            generation_instructions=(
                                "Provide two self-introductions, one confident and polished "
                                "(proactive verbs, strong nouns) and one hesitant (qualifiers "
                                "like maybe, just, hopefully), and ask the learner to label "
                                "each tone."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tone_id'. Provide passage_title and 2 "
                                "items, each with sender, message, prompt, options including "
                                "Confident and polished and Hesitant and uncertain, "
                                "correct_index, and explanation."
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
                        id="listen_tone_presenting",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Audio self-introductions",
                            generation_instructions=(
                                "Generate two spoken self-introductions, one poised and "
                                "evenly paced and one halting with fillers, and ask the "
                                "learner which sounds more poised and what signals "
                                "hesitation."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_tone'. Provide two intros (each with "
                                "id, label, speaker, audio_script) and 2 MCQ items, each "
                                "with prompt, options, correct_index, and explanation."
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
                        id="write_timed_presenting",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="3-sentence introduction",
                            generation_instructions=(
                                "Ask the learner to write a 3-sentence self-introduction "
                                "under a short time limit: sentence 1 their role, sentence 2 "
                                "a key passion, sentence 3 their absolute focus."
                            ),
                            widget_requirements=(
                                "Target widget 'write_timed'. Provide prompt, grammar_rule "
                                "describing the 3-sentence structure, target_words (passion, "
                                "thrilled, focus), writing_duration_seconds: 180, "
                                "sample_answer, and answer_hints."
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
                        id="speak_present_presenting",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Structured self-introduction",
                            generation_instructions=(
                                "Ask the learner to record a 90-second self-introduction in "
                                "three structured parts (background, main passion, key "
                                "focus), speaking with even pacing and poise."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_present'. Provide a "
                                "visual_prompt_description outlining the three parts, an "
                                "optional model_presentation, grammar_rule, target_words "
                                "(thrilled, passion, focus), and speaking_duration_seconds: "
                                "90."
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
                title="Full Confidence Showcase",
                description=(
                    "Cycle 1 wrap-up: learners show their growth with an inspiring "
                    "reading, an energetic shadow, a reflective timed write, and a "
                    "friendly debate with the tutor."
                ),
                focus="Cycle 1 wrap-up: show your growth with inspiring reading, shadowing, reflective writing, and a friendly debate task.",
                teacher=TeacherBlueprint(
                    lesson_goal="Celebrate and showcase Cycle 1 speaking growth.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Invite reflection on growth.",
                            instruction=(
                                "Greet the learner for the final day and Cycle 1 wrap-up. "
                                "Explain in one sentence that today is a confidence showcase. "
                                "Ask how they feel about their speaking confidence now "
                                "compared with Day 1."
                            ),
                        ),
                        TeacherStep(
                            id="showcase_preview",
                            goal="Preview the showcase tasks.",
                            instruction=(
                                "Celebrate their growth warmly. Preview that today they will "
                                "read an inspiring passage about overcoming speaker anxiety, "
                                "shadow a confident speaker, write a timed reflection on "
                                "their growth, and finish with a friendly debate where you "
                                "take the opposite side."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner is ready, ask only: Ready to try the "
                                "practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_showcase",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Overcoming fear of speaking",
                            generation_instructions=(
                                "Write an inspiring first-person passage about someone who "
                                "overcame a fear of speaking English by starting small "
                                "(shadowing, group chats) after a mentor said fluency is "
                                "about connection, not perfection. Then ask comprehension "
                                "questions about the fear, the mentor's advice, the first "
                                "step, and the closing message."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, "
                                "passage, and 4 MCQ items, each with prompt, options, "
                                "correct_index, and explanation."
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
                        id="listen_shadow_showcase",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Fluent and energetic shadow session",
                            generation_instructions=(
                                "Generate a short, energetic motivational line (about 15 "
                                "seconds) about being proud of one's progress and speaking "
                                "with more confidence, for the learner to shadow, matching "
                                "the rising and falling intonation."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_shadow'. Provide audio_script, "
                                "text_to_shadow, target_words (proud of, progress, "
                                "confidence), and grammar_rule about intonation."
                            ),
                        ),
                        evaluation=EvaluationBlueprint(
                            evaluator="speaking_eval",
                            evaluation_widget="read_aloud_assessment",
                        ),
                        feedback=FeedbackBlueprint(
                            feedback_widget="read_aloud_assessment",
                        ),
                    ),
                    ActivityBlueprint(
                        id="write_timed_showcase",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Reflecting on Cycle 1 growth",
                            generation_instructions=(
                                "Ask the learner to write a short personal reflection under "
                                "a short time limit on what they learned about themselves "
                                "this week, using reflective and forward-looking transition "
                                "markers."
                            ),
                            widget_requirements=(
                                "Target widget 'write_timed'. Provide prompt, grammar_rule, "
                                "target_words (discovered, moreover, in the future), "
                                "writing_duration_seconds: 180, sample_answer, and "
                                "answer_hints."
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
                        id="speak_debate_showcase",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_DEBATE",
                            activity="speak",
                            task_widget="speak_debate",
                            topic_override="Debate: Learn alone vs. with others",
                            generation_instructions=(
                                "Set up a friendly debate on whether it is better to learn "
                                "alone or with others. The AI argues for learning alone; the "
                                "learner records a counter-argument using strong opinion "
                                "starters and transition markers."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_debate'. Provide a debate_context with "
                                "an AI moderator turn, an AI opponent turn, and a learner "
                                "turn, target_words (strongly believe, however, on the other "
                                "hand), and speaking_duration_seconds: 60."
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
