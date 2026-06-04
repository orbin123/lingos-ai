"""Level-band curriculum source data.

Imports blueprint types from ``types.py`` only.
"""

from __future__ import annotations

from .types import (
    ActivityBlueprint,
    DaySource,
    EvaluationBlueprint,
    FeedbackBlueprint,
    TaskBlueprint,
    TeacherBlueprint,
    TeacherStep,
    WeekSource,
)


# ── B1B2 band: source weeks 1-8 (B1 wk 1-4, B2 wk 5-8) ──

WEEKS_B1B2: tuple[WeekSource, ...] = (
    WeekSource(
        week_number=1,
        theme_type="grammar",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=(
            DaySource(
                title="Past Perfect - Actions Before Another Past Event",
                description=(
                    "Learners use the past perfect (had + past participle) to "
                    "show that one past action happened before another past "
                    "action, using time words like already, just, by the time, "
                    "before, and after to order events clearly."
                ),
                focus="Past perfect (had + past participle) for the earlier of two past actions, with already, just, and by the time.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach the past perfect for an action that happened before another past action.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce the past perfect.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that the past "
                                "perfect uses had plus a past participle, and we use it for "
                                "an action that happened before another action in the past. "
                                "Ask for one thing they had already done before they arrived "
                                "at work or class today."
                            ),
                        ),
                        TeacherStep(
                            id="form_had_pp",
                            goal="Teach the had + past participle form.",
                            instruction=(
                                "Use the learner's sentence to explain that had is the same "
                                "for every subject (I, you, he, she, we, they) and is always "
                                "followed by a past participle. Ask them to say one sentence "
                                "about something a friend had finished before a past moment."
                            ),
                        ),
                        TeacherStep(
                            id="signal_words",
                            goal="Teach already, just, by the time, before, and after.",
                            instruction=(
                                "Introduce time words that often go with the past perfect: "
                                "already, just, by the time, before, and after. Ask for one "
                                "sentence using by the time or already and a correct past "
                                "participle."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has shown the pattern at least once, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_cloze_past_perfect",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CLOZE",
                            activity="read",
                            task_widget="fill_blanks",
                            topic_override="Past perfect earlier actions",
                            generation_instructions=(
                                "Write a 4-5 blank connected passage about a person's day "
                                "where several things had already happened before a key "
                                "moment. Focus on the past perfect with had + past participle."
                            ),
                            widget_requirements=(
                                "Always include base_verb for every blank so the learner "
                                "forms had + past participle. Do not repeat base_verb "
                                "inline in the passage after each ___ — the UI shows it "
                                "separately."
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
                        id="listen_mcq_past_perfect",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Listening for past perfect order",
                            generation_instructions=(
                                "Generate a 70-100 word spoken passage about a person "
                                "describing a past situation where earlier actions had "
                                "already happened, using the past perfect with had and time "
                                "words like already, just, and by the time."
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
                        id="write_past_perfect_sentences",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_OPEN_SENT",
                            activity="write",
                            task_widget="open_text",
                            topic_override="Write past perfect sentences",
                            generation_instructions=(
                                "Ask for affirmative past perfect sentences using I, he, and "
                                "she, describing what had happened before another past "
                                "action, with correct past participles and time words like "
                                "already, just, and by the time."
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
                        id="speak_past_perfect_events",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Say what had happened before a past moment",
                            generation_instructions=(
                                "Ask the learner to say short past perfect sentences about "
                                "what had happened before a past moment using correct had and "
                                "a past participle."
                            ),
                            widget_requirements=(
                                "Create exactly 3 speaking prompts: one with I, one with "
                                "he, and one with she. Include speaking_duration_seconds: 45."
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
                title="Second Conditional - Imagining Unreal Situations",
                description=(
                    "Learners use the second conditional (if + past simple, "
                    "would + base verb) to imagine unreal or unlikely present and "
                    "future situations and their results (If I had more time, I "
                    "would travel more)."
                ),
                focus="Second conditional with if + past simple and would + base verb for unreal present and future situations.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach the second conditional for imagining unreal situations.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce the second conditional.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that the second "
                                "conditional imagines an unreal or unlikely present or future "
                                "situation, using if + past simple and would + base verb. Ask "
                                "what they would do if they had a free day tomorrow."
                            ),
                        ),
                        TeacherStep(
                            id="if_clause_form",
                            goal="Teach the past simple in the if-clause.",
                            instruction=(
                                "Use the learner's sentence to explain that the if-clause "
                                "uses the past simple even though we mean now (If I had..., "
                                "If I lived...). Ask them to finish 'If I lived in another "
                                "country, ...' with their own idea."
                            ),
                        ),
                        TeacherStep(
                            id="result_clause",
                            goal="Teach would + base verb in the result clause.",
                            instruction=(
                                "Show that the result clause uses would plus the base verb "
                                "(I would travel, she would study). Ask them to make one "
                                "sentence with would about what they would buy if they won "
                                "some money."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has shown the pattern at least once, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_error_spot_second_conditional",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_ERROR_SPOT",
                            activity="read",
                            task_widget="error_spotting",
                            topic_override="Spot second conditional errors",
                            generation_instructions=(
                                "Generate a 5-sentence passage about imaginary situations and "
                                "their results. Each sentence must contain exactly one "
                                "grammatical error, so there are exactly 5 error tokens for "
                                "the learner to tap. Make the mistakes diverse across "
                                "second-conditional usage: include a present-tense verb where "
                                "the if-clause needs the past simple, a missing would in the "
                                "result clause, will instead of would, a wrong verb form "
                                "after would, and a condition-marker mismatch. Do not make "
                                "all errors the same kind of mistake."
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
                        id="listen_cloze_second_conditional",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_CLOZE",
                            activity="listen",
                            task_widget="listen_cloze",
                            topic_override="Listen and fill second conditional forms",
                            generation_instructions=(
                                "Listen to the short daydream audio, then complete the "
                                "paraphrased notes with the missing second-conditional verbs "
                                "from the clip."
                            ),
                            widget_requirements=(
                                "Set inner_widget to 'fill_in_blanks'. Use the authored "
                                "audio_script, passage, and 5 BlankItems exactly as "
                                "provided so rule-based scoring can compare each typed "
                                "verb phrase with correct_answer."
                            ),
                            static_payload={
                                "task_intro": "Listen, then complete the second-conditional notes.",
                                "instructions": (
                                    "Play the audio once, then type the missing "
                                    "second-conditional verbs in the paraphrased notes."
                                ),
                                "estimated_time_minutes": 3,
                                "inner_widget": "fill_in_blanks",
                                "audio_genre": "Personal daydream monologue",
                                "audio_script": (
                                    "Sometimes I imagine a completely different life. If I "
                                    "had more free time, I would learn the piano. If I lived "
                                    "by the sea, I would swim every single morning. If money "
                                    "were not a problem, I would travel around the world. If "
                                    "I spoke five languages, I would work as a tour guide. "
                                    "Honestly, if I knew then what I know now, I would worry "
                                    "much less."
                                ),
                                "passage_title": "A Different Life Notes",
                                "passage": (
                                    "If I ___ more free time, I would learn the piano. If I "
                                    "lived by the sea, I ___ every morning. If money were not "
                                    "a problem, I ___ around the world. If I ___ five "
                                    "languages, I would work as a guide. If I knew then what "
                                    "I know now, I ___ much less."
                                ),
                                "items": [
                                    {
                                        "item_id": "b1",
                                        "blank_id": "b1",
                                        "sentence_with_blank": "If I ___ more free time, I would learn the piano.",
                                        "base_verb": "have",
                                        "correct_answer": "had",
                                        "distractors": ["have", "would have"],
                                        "options": ["had", "have", "would have"],
                                        "grammar_rule": "Use the past simple in the if-clause of the second conditional.",
                                        "explanation": "The if-clause needs the past simple, so we use had.",
                                    },
                                    {
                                        "item_id": "b2",
                                        "blank_id": "b2",
                                        "sentence_with_blank": "If I lived by the sea, I ___ every morning.",
                                        "base_verb": "swim",
                                        "correct_answer": "would swim",
                                        "distractors": ["will swim", "swam"],
                                        "options": ["would swim", "will swim", "swam"],
                                        "grammar_rule": "Use would + base verb in the result clause of the second conditional.",
                                        "explanation": "The result clause needs would + base verb, so we use would swim.",
                                    },
                                    {
                                        "item_id": "b3",
                                        "blank_id": "b3",
                                        "sentence_with_blank": "If money were not a problem, I ___ around the world.",
                                        "base_verb": "travel",
                                        "correct_answer": "would travel",
                                        "distractors": ["will travel", "travelled"],
                                        "options": ["would travel", "will travel", "travelled"],
                                        "grammar_rule": "Use would + base verb in the result clause of the second conditional.",
                                        "explanation": "The result of an unreal condition uses would travel.",
                                    },
                                    {
                                        "item_id": "b4",
                                        "blank_id": "b4",
                                        "sentence_with_blank": "If I ___ five languages, I would work as a guide.",
                                        "base_verb": "speak",
                                        "correct_answer": "spoke",
                                        "distractors": ["speak", "would speak"],
                                        "options": ["spoke", "speak", "would speak"],
                                        "grammar_rule": "Use the past simple in the if-clause of the second conditional.",
                                        "explanation": "The if-clause needs the past simple, so we use spoke.",
                                    },
                                    {
                                        "item_id": "b5",
                                        "blank_id": "b5",
                                        "sentence_with_blank": (
                                            "If I knew then what I know now, I ___ much less."
                                        ),
                                        "base_verb": "worry",
                                        "correct_answer": "would worry",
                                        "distractors": ["will worry", "worried"],
                                        "options": ["would worry", "will worry", "worried"],
                                        "grammar_rule": "Use would + base verb in the result clause of the second conditional.",
                                        "explanation": "The imagined result uses would worry.",
                                    },
                                ],
                                "target_words_in_audio": [
                                    "had", "would swim", "would travel",
                                    "spoke", "would worry",
                                ],
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
                        id="write_error_corr_second_conditional",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_ERROR_CORR",
                            activity="write",
                            task_widget="error_correction",
                            topic_override="Correct second conditional mistakes",
                            generation_instructions=(
                                "Give the learner 3 sentences that each contain one second "
                                "conditional error — mix wrong tense in the if-clause (e.g. "
                                "'If I have time, I would help') and will/would mistakes "
                                "(e.g. 'If it rained, we will stay home'). Ask the learner to "
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
                        id="speak_read_aloud_second_conditional",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_READ_ALOUD",
                            activity="speak",
                            task_widget="read_aloud",
                            topic_override="Read second conditional passage aloud",
                            generation_instructions=(
                                "Give the learner a connected second conditional narrative "
                                "passage of 55-70 words to read aloud, describing several "
                                "imaginary situations and their results, mixing if-clauses in "
                                "the past simple and result clauses with would."
                            ),
                            widget_requirements=(
                                "Populate `text_to_read_aloud` with a single connected second "
                                "conditional passage (55-70 words) describing imaginary "
                                "situations and their results. Set `task_intro` to 'Read the "
                                "passage above out loud.' Include `grammar_rule_to_practice` "
                                "explaining the second conditional with if + past simple and "
                                "would + base verb, and `speaking_duration_seconds: 45`."
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
                title="The Passive Voice - Focus on the Action",
                description=(
                    "Learners use the passive voice (the right form of be + past "
                    "participle) to put the focus on the action or result rather "
                    "than the doer (is made, was sent), adding by only when the "
                    "doer matters."
                ),
                focus="Passive voice with be + past participle across tenses, focusing on the action rather than the doer.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach the passive voice with be + past participle.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce the passive voice.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that the passive "
                                "voice puts the focus on the action or the result, not the "
                                "doer, using be plus a past participle (is made, was sent). "
                                "Ask them to tell you one thing in their home that was made "
                                "in another country."
                            ),
                        ),
                        TeacherStep(
                            id="form_be_pp",
                            goal="Teach the be + past participle form.",
                            instruction=(
                                "Use the learner's sentence to confirm the form: the right "
                                "form of be plus a past participle. Explain that the tense "
                                "lives in be (is cleaned, was cleaned, will be cleaned). Ask "
                                "them to make one present passive sentence about how a common "
                                "food is made."
                            ),
                        ),
                        TeacherStep(
                            id="when_to_use",
                            goal="Teach when to choose the passive and add by.",
                            instruction=(
                                "Explain that we use the passive when the doer is unknown or "
                                "not important, and we can add by to name the doer (The "
                                "window was broken by the storm). Ask for one past passive "
                                "sentence with by."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has shown the pattern at least once, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_passive",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Understand a process in the passive",
                            generation_instructions=(
                                "Write a 60-75 word passage describing how a product is made "
                                "or how a process works, mixing active and passive sentences "
                                "(the beans are picked, the coffee is shipped). Then ask "
                                "comprehension questions about the steps, and include one "
                                "item asking which sentence uses the correct passive form."
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
                        id="listen_dictation_passive",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="Hear passive-form chunks",
                            generation_instructions=(
                                "Generate a 35-45 word process audio script of 4 short "
                                "sentences with varied passive forms (is made, was sent, are "
                                "delivered, will be repaired). The learner types each "
                                "sentence exactly as heard."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_dictation'. Provide audio_script and "
                                "4 dictation items, each with prompt, correct_answer, and "
                                "explanation. Set target_words to the passive chunks (for "
                                "example 'is made', 'was sent', 'are delivered', 'will be "
                                "repaired')."
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
                        id="write_sent_trans_passive",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Rewrite active into passive",
                            generation_instructions=(
                                "Give the learner 3 active sentences with varied tenses and "
                                "ask them to rewrite each in the passive, keeping the same "
                                "meaning and using by only when the doer matters."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 3 items, each "
                                "with source_sentence, sample_answer, and watch_hints (for "
                                "example 'present -> is/are + past participle', 'past -> "
                                "was/were + past participle')."
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
                        id="speak_timed_passive",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe a process with the passive",
                            generation_instructions=(
                                "Ask the learner to say one passive sentence per prompt, "
                                "choosing the right form of be for the tense and using a "
                                "correct past participle."
                            ),
                            widget_requirements=(
                                "Create exactly 3 speaking prompts: one present passive about "
                                "how something is made, one past passive about something that "
                                "was built or sent, and one about something that will be "
                                "done. Include speaking_duration_seconds: 45."
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
                title="Relative Clauses - Adding Detail with Who, Which & That",
                description=(
                    "Learners add information about a noun using relative clauses "
                    "with who for people, which for things, that for either, and "
                    "where for places, placing the relative pronoun right after "
                    "the noun it describes."
                ),
                focus="Relative clauses with who, which, that, and where to add detail to a noun.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach relative clauses with who, which, that, and where.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce relative clauses.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that relative "
                                "clauses add information about a noun using who for people, "
                                "which for things, and that for either. Ask them to describe "
                                "a person they like using who in a full sentence."
                            ),
                        ),
                        TeacherStep(
                            id="defining_clauses",
                            goal="Teach placement of the relative pronoun.",
                            instruction=(
                                "Confirm their sentence. Explain that the relative pronoun "
                                "comes right after the noun it describes (the man who lives "
                                "next door, the book which I read). Ask them to describe a "
                                "thing they own using which or that."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Confirm the pattern with a short example (She is the friend "
                                "who always helps me. This is the app that I use most.) and "
                                "then ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_relative_clauses",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Match nouns to the right relative pronoun",
                            generation_instructions=(
                                "Ask the learner to match each noun phrase or clue to the "
                                "correct relative pronoun (a person -> who, a thing -> which, "
                                "a place -> where, either person or thing -> that)."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options (the "
                                "relative pronouns who, which, that, where) and 3-4 items, "
                                "each with prompt (a noun phrase with a clue), "
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
                        id="listen_mcq_relative_clauses",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Hearing relative clauses in speech",
                            generation_instructions=(
                                "Generate a 35-45 word short description that uses at least "
                                "two relative clauses (the woman who runs the cafe, the phone "
                                "which broke). Include comprehension questions about which "
                                "person did what and which thing is described."
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
                        id="write_open_sent_relative_clauses",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_OPEN_SENT",
                            activity="write",
                            task_widget="open_text",
                            topic_override="Write sentences with relative clauses",
                            generation_instructions=(
                                "Ask for three short sentences: one describing a person with "
                                "who, one describing a thing with which or that, and one "
                                "describing a place with where. Remind the learner to put the "
                                "relative pronoun right after the noun."
                            ),
                            widget_requirements=(
                                "Target widget 'open_text'. Provide target_words (who, which, "
                                "that, where), common_mistakes, and 3 items, each with "
                                "prompt, sample_answer, and answer_hints."
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
                        id="speak_pic_desc_relative_clauses",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Identify people in a picture with relative clauses",
                            generation_instructions=(
                                "Ask the learner to describe a simple scene aloud, using "
                                "relative clauses to identify the people and things (the man "
                                "who is reading, the bag which is on the table)."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "a busy cafe with several people doing different things, "
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
                title="Reported Speech - Telling What Others Said",
                description=(
                    "Learners report what other people said without their exact "
                    "words, using said that, told me that, and asked if, and "
                    "shifting the verb back one tense (He said he was tired)."
                ),
                focus="Reported speech for statements and questions, with backshift of tense and changes to pronouns and time words.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach reported speech with backshift for statements and questions.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce reported speech.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that reported "
                                "speech tells what someone said without their exact words, "
                                "often using said that or told me that, and that the verb "
                                "usually shifts back one tense. Ask them to tell you one "
                                "thing a friend said to them recently."
                            ),
                        ),
                        TeacherStep(
                            id="backshift",
                            goal="Teach backshift of tense and pronouns.",
                            instruction=(
                                "Confirm their sentence. Explain that present often becomes "
                                "past in reported speech ('I am tired' -> She said she was "
                                "tired) and that pronouns and time words may also change. Ask "
                                "them to report one more thing someone told them, shifting "
                                "the tense back."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has reported a sentence correctly at least "
                                "once, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_cloze_reported_speech",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CLOZE",
                            activity="read",
                            task_widget="fill_blanks",
                            topic_override="Fill reported speech blanks",
                            generation_instructions=(
                                "Write a short 4-5 sentence passage that reports a "
                                "conversation, with blanks that each need the correct "
                                "reported-speech word (said, told, asked, was, had), so the "
                                "learner backshifts by meaning."
                            ),
                            widget_requirements=(
                                "Target widget 'fill_blanks'. Provide passage_title and a passage "
                                "with ___ markers only — no inline hints in parentheses after blanks. "
                                "Provide a BlankItem per blank with correct_answer and explanation. "
                                "Omit base_verb; these are reporting blanks, not verb inflection."
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
                        id="listen_infer_reported_speech",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Infer the original words behind a report",
                            generation_instructions=(
                                "Generate a 35-45 word audio clip where one person reports "
                                "what another said and asked (She said she was busy, he asked "
                                "if I could help). Ask the learner to infer the original "
                                "words and the meaning."
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
                        id="write_para_reported_speech",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write a paragraph in reported speech",
                            generation_instructions=(
                                "Ask the learner to write a 3-4 sentence paragraph reporting "
                                "a short conversation they had, using said that, told me "
                                "that, and asked, with the verbs correctly shifted back."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, "
                                "grammar_rule, target_words (said that, told me, asked if, "
                                "would), minimum_words 25, sample_answer, and answer_hints."
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
                        id="speak_roleplay_reported_speech",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Pass on a message roleplay",
                            generation_instructions=(
                                "Set up a roleplay where the learner passes on a message (for "
                                "example telling a colleague what the manager said). The "
                                "partner's opening should be 2-3 sentences that give the "
                                "original message and ask the learner to report it. The "
                                "learner's spoken response must be 2-3 connected sentences "
                                "using reported speech (he said that, she asked if, they told "
                                "me) — not a one-line answer."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_roleplay'. Provide dialogue_context "
                                "with alternating partner and learner turns (4-6 turns "
                                "total). Partner lines set the scene in 2-3 sentences; "
                                "each learner line is 2-3 connected sentences (roughly "
                                "15-30 words). Include target_words (said that, told me, "
                                "asked if, would), speaking_prompts with one instruction to "
                                "respond aloud, sample_responses with the learner's model "
                                "answer (same text as the learner dialogue turn), "
                                "grammar_rule_to_practice, and speaking_duration_seconds: 45."
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
                title="Used To & Would - Talking About Past Habits",
                description=(
                    "Learners use used to + base verb for past habits and states "
                    "that are no longer true, and would + base verb for repeated "
                    "past actions, to describe how life was different before."
                ),
                focus="Used to and would for past habits and states, and the limits of would with state verbs.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach used to and would for past habits and states.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce used to and would.",
                            instruction=(
                                "Greet the learner and note this is the past-habits day of "
                                "grammar week. Explain in two sentences that used to + base "
                                "verb describes past habits and states that are no longer "
                                "true, and would + base verb describes repeated past actions. "
                                "Ask what they used to do as a child that they no longer do."
                            ),
                        ),
                        TeacherStep(
                            id="used_to_vs_would",
                            goal="Teach used to vs would.",
                            instruction=(
                                "Confirm their answer. Explain that used to works for both "
                                "habits and states (I used to live..., I used to like...), "
                                "but would only works for repeated actions, not states. Ask "
                                "them to say one repeated childhood action using would."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used the pattern at least once, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_used_to_would",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="Past habits in text",
                            generation_instructions=(
                                "Write a short profile of how someone's life used to be "
                                "different (where they used to live, what they would do every "
                                "summer), rich in used to and would for past habits and "
                                "states. Then give True / False / Not Given statements about "
                                "how things used to be."
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
                        id="listen_shadow_used_to_would",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Repeat used to / would phrases in connected speech",
                            generation_instructions=(
                                "Generate a short, natural monologue (about 20 seconds) in "
                                "which used to and would phrases describing past habits are "
                                "blended into connected speech (I used to walk to school, we "
                                "would play outside for hours), for the learner to shadow and "
                                "reproduce smoothly."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_shadow'. Provide audio_script, "
                                "text_to_shadow (identical to the script), target_words "
                                "highlighting the used to / would chunks, and grammar_rule."
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
                        id="write_email_used_to_would",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Tell a friend how life used to be",
                            generation_instructions=(
                                "Ask the learner to write a short email to a friend "
                                "describing how their life or hometown used to be different, "
                                "using used to and would for past habits and states (I used "
                                "to..., we would...)."
                            ),
                            widget_requirements=(
                                "Target widget 'write_email'. Provide prompt, grammar_rule, "
                                "target_words (used to, would, no longer, back then), "
                                "minimum_words 25, sample_answer (with To and Subject "
                                "lines), and answer_hints."
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
                        id="speak_smalltalk_used_to_would",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Casual chat about how things used to be",
                            generation_instructions=(
                                "Set up casual small talk about childhood and the past where "
                                "the learner answers using used to and would naturally to "
                                "describe old habits (I used to..., we would...)."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_smalltalk'. Provide a dialogue_context "
                                "alternating partner and learner turns, target_words (used "
                                "to, would, as a child, back then), and "
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
                title="Concession & Contrast - Despite, In Spite Of, Whereas & However",
                description=(
                    "Learners connect contrasting ideas with advanced linkers: "
                    "despite and in spite of before a noun or -ing, whereas to "
                    "compare two clauses, and however to contrast two sentences."
                ),
                focus="Concession and contrast linkers despite, in spite of, whereas, and however, with the correct grammar after each.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach concession and contrast linkers for connecting opposing ideas.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce concession linkers.",
                            instruction=(
                                "Greet the learner and note this is the final, wrap-up day "
                                "of grammar week. Explain in two sentences that advanced "
                                "linkers connect contrasting ideas: despite and in spite of "
                                "are followed by a noun or -ing, while whereas and however "
                                "contrast two full ideas. Ask them to finish 'Despite the "
                                "rain, ___.'"
                            ),
                        ),
                        TeacherStep(
                            id="contrast_linkers",
                            goal="Teach whereas and however.",
                            instruction=(
                                "Confirm their sentence. Explain that whereas compares two "
                                "ideas inside one sentence and however usually starts a new "
                                "sentence after a full stop or semicolon. Ask them to make "
                                "one sentence with whereas comparing two things."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a contrast linker correctly at least "
                                "once, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_context_mcq_concession",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Contrast linkers in context",
                            generation_instructions=(
                                "Write a short 60-75 word passage about a person's choices or "
                                "a comparison with 4 blanks that each need a contrast linker "
                                "chosen from context: despite or in spite of before a noun or "
                                "-ing, whereas to compare two clauses, and however to "
                                "contrast two sentences."
                            ),
                            widget_requirements=(
                                "Target widget 'read_context_mcq'. Provide passage_title, "
                                "passage, and 4 MCQ items, each with prompt, options "
                                "(despite, in spite of, whereas, however), correct_index, and "
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
                        id="listen_retell_concession",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Listen and summarize with contrast linkers",
                            generation_instructions=(
                                "Generate a ~40 second monologue telling a short story or "
                                "comparison that uses contrast linkers (despite, in spite of, "
                                "whereas, however) to connect opposing ideas. Ask the learner "
                                "to retell the main ideas in their own words, keeping the "
                                "contrast linkers correct."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_retell'. Provide: "
                                "audio_script (the full spoken monologue text), "
                                "passage_to_retell (a 2-3 sentence model retell — shorter "
                                "than the audio, showing how a good student would summarise "
                                "the key points using contrast linkers), "
                                "sample_responses (list containing that same model retell), "
                                "target_words (list of the key contrast linkers from the "
                                "audio), and grammar_rule."
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
                        id="write_paraphrase_concession",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="Joining contrasting ideas with linkers",
                            generation_instructions=(
                                "Give the learner 3 pairs of contrasting sentences and ask "
                                "them to rewrite each pair as one smooth sentence using a "
                                "contrast linker (despite, in spite of, whereas, or however) "
                                "that fits the meaning, with correct grammar after each "
                                "linker."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paraphrase'. Provide 3 items, each "
                                "with incorrect_sentence (the contrasting sentence pair), "
                                "sample_answer, and watch_hints (the target contrast linker)."
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
                        id="speak_present_concession",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Compare two options with contrast linkers",
                            generation_instructions=(
                                "Ask the learner to compare two options or opinions aloud, "
                                "using at least three contrast linkers (despite, in spite of, "
                                "whereas, however) to connect the opposing ideas."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_present'. Provide: "
                                "prompts as a list with one general question asking the learner to "
                                "compare two choices and say which they prefer using contrast "
                                "linkers (e.g. 'Compare living in a city and the countryside, "
                                "and say which you prefer.'); "
                                "visual_prompt_description as a short sample spoken answer that "
                                "uses at least three contrast linkers (e.g. 'A city is "
                                "exciting, whereas the countryside is calm. Despite the noise, "
                                "I prefer the city. However, I visit the countryside often, so "
                                "I get both.'); "
                                "grammar_rule, target_words, and speaking_duration_seconds: 45."
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
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=(
            DaySource(
                title="Negotiating & Reaching Agreement",
                description=(
                    "Learners negotiate to reach an agreement: they propose an "
                    "option, suggest a trade-off or compromise, and confirm what "
                    "both sides agree to (Would you be willing to...? / Let's meet "
                    "halfway)."
                ),
                focus="Negotiating options, suggesting compromises and trade-offs, and confirming a shared agreement.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach negotiating and reaching a shared agreement.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce negotiating.",
                            instruction=(
                                "Welcome the learner to communication week. Explain in two "
                                "sentences that negotiating means proposing an option and "
                                "then finding a compromise both sides can accept. Ask them to "
                                "suggest one thing they would want if they were planning a "
                                "shared project with you."
                            ),
                        ),
                        TeacherStep(
                            id="propose_compromise",
                            goal="Teach proposing a compromise.",
                            instruction=(
                                "React warmly to their suggestion. Explain that we move "
                                "toward agreement with phrases like 'Would you be willing "
                                "to...?' and 'Let's meet halfway.' Ask them to offer one "
                                "compromise on the idea they chose."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has proposed an option and a compromise, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_negotiating",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Negotiating to an agreement",
                            generation_instructions=(
                                "Write a short message exchange in which two people negotiate "
                                "a shared decision, propose trade-offs, and agree on a final "
                                "compromise. Then ask comprehension questions about what each "
                                "side wanted, the trade-off, and the final agreement."
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
                        id="listen_mcq_negotiating",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Listening to a negotiation",
                            generation_instructions=(
                                "Generate a 35-45 word dialogue between two people "
                                "negotiating: one proposes an idea, they discuss two "
                                "trade-offs, and agree on a compromise. The learner answers "
                                "questions about each side's wish, the trade-off, and the "
                                "agreement."
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
                        id="write_sent_trans_negotiating",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Polite negotiation phrases",
                            generation_instructions=(
                                "Give the learner 3 blunt demands (We do it my way. Lower the "
                                "price. Change the date.) and ask them to rewrite each as a "
                                "polite negotiation move using forms like 'Would you be "
                                "willing to...?', 'How about we...?', and 'Could we meet "
                                "halfway on...?'."
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
                        id="speak_roleplay_negotiating",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Negotiate with a colleague",
                            generation_instructions=(
                                "Set up a friendly roleplay where a colleague proposes a plan "
                                "the learner cannot fully accept. The learner reacts, "
                                "proposes a trade-off, and confirms a compromise using "
                                "phrases like 'How about...?' and 'Let's meet halfway.'"
                            ),
                            widget_requirements=(
                                "Target widget 'speak_roleplay'. Provide a dialogue_context "
                                "alternating partner and learner turns, target_words (How "
                                "about, meet halfway, that works, agreed), and "
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
                title="Telling News & Reacting",
                description=(
                    "Learners share recent news and react naturally to others' "
                    "news with surprise, concern, and follow-up questions (Guess "
                    "what! / Oh no, what happened?), keeping a conversation warm "
                    "and two-sided."
                ),
                focus="Share recent news and react with surprise, concern, and follow-up questions.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach sharing news and reacting warmly with follow-ups.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce telling and reacting to news.",
                            instruction=(
                                "Welcome the learner to Day 2 of communication week. Explain "
                                "in two sentences that telling news means sharing something "
                                "recent and reacting warmly to the other person's news with "
                                "surprise or concern. Ask them to tell you one piece of news "
                                "from their week."
                            ),
                        ),
                        TeacherStep(
                            id="react_followup",
                            goal="React and add a follow-up question.",
                            instruction=(
                                "Use the learner's news to show how a good listener reacts "
                                "(Really? That's great!) and asks a follow-up question. Ask "
                                "them to react to this and add a follow-up: 'I just started a "
                                "new job.'"
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has reacted and asked a follow-up, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_telling_news",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="A piece of shared news",
                            generation_instructions=(
                                "Write a short first-person message sharing recent news (a "
                                "new job, a move) together with the warm reactions of a "
                                "friend. Then give True / False / Not Given statements based "
                                "only on the message."
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
                        id="listen_infer_telling_news",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Infer feelings behind news",
                            generation_instructions=(
                                "Generate a conversation (about 45 seconds) where someone "
                                "shares news and a friend reacts with surprise and concern. "
                                "Ask the learner to infer how each speaker feels and what "
                                "they imply, not only what they state."
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
                        id="write_email_telling_news",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Reply to a friend's news",
                            generation_instructions=(
                                "Ask the learner to write a short message to a friend who "
                                "shared some news. It must include a warm greeting, one "
                                "reaction (surprise or congratulations), two follow-up "
                                "questions, and a close."
                            ),
                            widget_requirements=(
                                "Target widget 'write_email'. Provide prompt, grammar_rule, "
                                "target_words, minimum_words 25, sample_answer (with To and "
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
                        id="speak_interview_telling_news",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_INTERVIEW",
                            activity="speak",
                            task_widget="speak_interview",
                            topic_override="React to news in a mini chat",
                            generation_instructions=(
                                "Run a friendly mini interview where the learner reacts to "
                                "three pieces of news (a promotion, a small problem, a "
                                "holiday plan) in one or two full sentences each, with a "
                                "reaction and a follow-up question."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_interview'. Provide interview_context, "
                                "grammar_rule, target_words (That's wonderful, Oh no, How "
                                "did, What about), 3 questions each with interviewer_prompt, "
                                "sample_answer, and answer_hint, and "
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
                title="Explaining a Problem & Solution",
                description=(
                    "Learners explain a problem clearly and propose a solution in "
                    "a logical order — situation, problem, action, result — and add "
                    "a short recommendation with a reason."
                ),
                focus="Explain a problem and solution in order (situation, problem, action, result) with a recommendation.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach explaining a problem and solution in a clear order with a recommendation.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce explaining a problem.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that explaining "
                                "a problem clearly follows an order: the situation, the "
                                "problem, and the action you took or suggest. Ask them to "
                                "tell you about one small problem they solved recently."
                            ),
                        ),
                        TeacherStep(
                            id="structure_order",
                            goal="Teach signposting the order.",
                            instruction=(
                                "Confirm their answer. Introduce signposting words (first, "
                                "the problem was, so, as a result) and ask them to describe "
                                "the situation and the problem in order using two of them."
                            ),
                        ),
                        TeacherStep(
                            id="add_recommendation",
                            goal="Add a recommendation with a reason.",
                            instruction=(
                                "Show how to add a recommendation with a reason (I would "
                                "suggest making backups because they save time). Ask them "
                                "what they would recommend to avoid the problem and why, in "
                                "one sentence."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a signposting word and a reason at "
                                "least once, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_structure_problem_solution",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_STRUCTURE_ID",
                            activity="read",
                            task_widget="read_structure",
                            topic_override="Identify parts of a problem-solution text",
                            generation_instructions=(
                                "Provide a 3-paragraph problem-solution passage and ask the "
                                "learner to label each paragraph as the Situation "
                                "(background), Problem (what went wrong), or Solution (the "
                                "action and result)."
                            ),
                            widget_requirements=(
                                "Target widget 'read_structure'. Provide passage_title, "
                                "structure_labels ['Situation', 'Problem', 'Solution'], and 3 "
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
                        id="listen_retell_problem_solution",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Retell a problem and solution",
                            generation_instructions=(
                                "Generate a problem-solution monologue (about 50 seconds) "
                                "describing a situation, a problem, and how it was solved. "
                                "Ask the learner to retell the key points in order using "
                                "signposting words and the final result."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_retell'. Provide audio_script, "
                                "passage_to_retell, target_words (the situation was, the "
                                "problem, so, as a result), and grammar_rule."
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
                        id="write_para_problem_solution",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write about a problem you solved",
                            generation_instructions=(
                                "Ask the learner to write a 5-7 sentence paragraph about a "
                                "problem they solved, describing the situation, the problem, "
                                "the action, and the result, using at least three signposting "
                                "words and one reason with because."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, "
                                "grammar_rule, target_words (first, the problem was, so, as a "
                                "result, because), minimum_words 45, sample_answer, and "
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
                        id="speak_opinion_problem_solution",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_OPINION",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Recommend the best solution",
                            generation_instructions=(
                                "Ask the learner to answer in two or three sentences what the "
                                "best solution to a common problem is, giving their "
                                "recommendation and one reason with because."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_present'. Provide grammar_rule, "
                                "target_words (I would suggest, because, the best way, "
                                "however), a visual_prompt_description or prompt for the "
                                "recommendation, and speaking_duration_seconds: 40."
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
                title="Workplace Communication - Updates & Tasks",
                description=(
                    "Learners handle everyday workplace English: give a clear "
                    "status update, confirm a deadline, and clarify what a task "
                    "needs, politely and directly."
                ),
                focus="Handle workplace situations like giving updates, confirming deadlines, and clarifying tasks.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach clear workplace language for updates, deadlines, and tasks.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce workplace update phrases.",
                            instruction=(
                                "Welcome the learner to Day 4. Explain in two sentences that "
                                "workplace English means giving clear updates, confirming "
                                "deadlines, and clarifying tasks politely and directly (Just "
                                "to confirm... / Could you clarify...?). Ask for a polite way "
                                "to ask when a task is due."
                            ),
                        ),
                        TeacherStep(
                            id="extend_question",
                            goal="Practise extending a work request.",
                            instruction=(
                                "Confirm their polite phrase. Ask them to ask one more work "
                                "question, such as clarifying who is responsible, in the same "
                                "polite way, and briefly preview that today they will read a "
                                "work email, follow a voicemail update, write from task "
                                "notes, and roleplay a check-in with a manager."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has produced one polite work question, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_workplace",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Workplace Update",
                            generation_instructions=(
                                "Write a short work email or message thread where a colleague "
                                "gives a status update, confirms a deadline, and clarifies a "
                                "task. Then ask comprehension questions about the progress, "
                                "the deadline, and what is still needed."
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
                        id="listen_mcq_workplace",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Voicemail update details",
                            generation_instructions=(
                                "Generate a short workplace voicemail (about 40 seconds) "
                                "about a project update, a changed deadline, and a request. "
                                "Ask comprehension questions about the update, the new "
                                "deadline, and the request."
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
                        id="write_bullets_to_para_workplace",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_BULLETS_TO_PARA",
                            activity="write",
                            task_widget="write_bullets_to_para",
                            topic_override="Write a work update from notes",
                            generation_instructions=(
                                "Give the learner a 4-item task-notes list (task, progress, "
                                "blocker, next step) and ask them to turn it into a clear, "
                                "polite update message to a manager, using complete sentences "
                                "and professional phrasing."
                            ),
                            widget_requirements=(
                                "Target widget 'write_bullets_to_para'. Provide bullets (4 "
                                "work items), prompt, grammar_rule, target_words, "
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
                        id="speak_roleplay_workplace",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Check in with a manager",
                            generation_instructions=(
                                "Set up a check-in roleplay where a manager greets the "
                                "learner and asks for a progress update. The learner gives a "
                                "clear update using 'So far I've...' and answers the "
                                "manager's questions about timing and next steps politely and "
                                "directly."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_roleplay'. Provide a dialogue_context "
                                "alternating partner and learner turns, target_words (so far, "
                                "on track, by Friday, next step), and "
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
                title="Persuading & Making Your Case",
                description=(
                    "Learners make a persuasive case with clear reasons and "
                    "evidence, and push back politely when someone disagrees, so "
                    "they sound convincing without sounding aggressive."
                ),
                focus="Persuade with reasons and evidence, and push back politely while keeping a respectful tone.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach persuading with reasons and evidence and polite pushback.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce the topic and invite the first attempt.",
                            instruction=(
                                "Greet the learner. In one short sentence say that today's "
                                "lesson is about persuading someone and making your case. "
                                "Then ask: 'How would you convince a friend to try a new "
                                "restaurant you love?' Do NOT list phrases or examples before "
                                "they answer — wait for their reply first."
                            ),
                        ),
                        TeacherStep(
                            id="persuade_evidence",
                            goal="Confirm the attempt and add a reason and evidence.",
                            instruction=(
                                "Quote one word from the learner's reply to confirm it sounds "
                                "persuasive. If it is convincing, affirm it briefly; if not, "
                                "give a gentle one-sentence correction. Then explain that a "
                                "strong case adds a reason and a piece of evidence "
                                "(because... / for example...). Ask: 'Now how would you "
                                "persuade a manager to approve one day of remote work?' Stop "
                                "and wait for their answer."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Confirm they have reason and evidence and move to practice.",
                            instruction=(
                                "Quote something from their case to confirm it sounds "
                                "convincing. Tell them in one sentence that they now have a "
                                "clear reason and evidence. Then ask only: Ready to try the "
                                "practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_persuading",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="A persuasive message",
                            generation_instructions=(
                                "Write a short, persuasive message that argues for one idea "
                                "using a clear reason, a piece of evidence, and a polite "
                                "acknowledgement of the other side. Then give True / False / "
                                "Not Given statements based only on the message."
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
                        id="listen_infer_persuading",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Infer the argument behind a pitch",
                            generation_instructions=(
                                "Generate a persuasive dialogue (about 40 seconds) where one "
                                "person makes a case, gives a reason and evidence, and the "
                                "other raises a doubt. Ask the learner to infer the main "
                                "claim, the evidence, and the doubt."
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
                        id="write_idea_para_persuading",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_IDEA_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write a persuasive case",
                            generation_instructions=(
                                "Ask the learner to write a short persuasive paragraph "
                                "arguing for a four-day work week, including a clear claim, "
                                "one reason, one piece of evidence, and a polite "
                                "acknowledgement of the other side."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, "
                                "grammar_rule, target_words (I believe, because, for example, "
                                "admittedly), minimum_words 25, sample_answer, and "
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
                        id="speak_pic_desc_persuading",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe and argue about a scene",
                            generation_instructions=(
                                "Ask the learner to describe a picture of a public choice "
                                "(for example a crowded car park next to an empty bus stop) "
                                "aloud, and make a short case for one solution using a reason "
                                "and evidence."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "a busy car park beside an empty bus lane, grammar_rule, and "
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
                title="Adjusting Your Tone - Professional vs Casual Register",
                description=(
                    "Learners notice how the same message shifts between "
                    "professional and casual register, rewrite messages to fit the "
                    "reader, and switch back into relaxed small talk."
                ),
                focus="Tell professional from casual register, rewrite for the reader, and switch comfortably into casual small talk.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach recognising and changing professional vs casual register.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce register in messages.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that the same "
                                "message can sound professional or casual depending on the "
                                "words we choose. Read 'I would be grateful if you could send "
                                "the report by Friday.' aloud, then ask them how they would "
                                "say the same thing to a close colleague in their own words."
                            ),
                        ),
                        TeacherStep(
                            id="formal_informal",
                            goal="Change register and notice the markers.",
                            instruction=(
                                "Warmly react to their version and name whether it sounds "
                                "professional or casual. Explain that professional messages "
                                "use full forms and polite phrases, while casual ones use "
                                "contractions and relaxed words, and invite them to say the "
                                "same idea in a more professional way. Preview that the day "
                                "ends with relaxed small talk."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has rephrased the message in their own words "
                                "at least once, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tone_id_register_w10",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Professional vs casual in messages",
                            generation_instructions=(
                                "Provide two short messages, one clearly professional and one "
                                "clearly casual, and ask the learner to label each as "
                                "Professional or Casual based on word choice and punctuation."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tone_id'. Provide passage_title and 2 "
                                "items, each with sender, message, prompt, options "
                                "(Professional, Casual), correct_index, and explanation."
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
                        id="listen_tone_register_w10",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Professional vs casual in speech",
                            generation_instructions=(
                                "Generate a short spoken message (about 28 seconds) with "
                                "clear register cues. Ask the learner to choose whether the "
                                "speaker sounds professional or casual and why."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_tone'. Provide audio_script and at "
                                "least 1 MCQ item with prompt, options (Professional, "
                                "Casual), correct_index, and explanation."
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
                        id="write_paraphrase_register_w10",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="Change message register",
                            generation_instructions=(
                                "Give the learner one professional message to rewrite as a "
                                "casual note and one casual note to rewrite as a polite "
                                "professional message, keeping the meaning the same while "
                                "changing the register."
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
                        id="speak_smalltalk_register_w10",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Casual catch-up chat",
                            generation_instructions=(
                                "Set up relaxed small talk about plans for the weekend "
                                "where the learner answers two turns in a friendly casual "
                                "tone with one simple detail each."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_smalltalk'. Provide a dialogue_context "
                                "alternating partner and learner turns, target_words (That "
                                "sounds great, I might, probably, weekend), and "
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
                title="Guided Discussion - Stay on Topic & Build on Others",
                description=(
                    "A communication wrap-up: learners take part in a focused "
                    "discussion, stay on topic, build on others' points, retell a "
                    "discussion, reply to a group thread, and give a short spoken "
                    "summary."
                ),
                focus="Take part in a focused discussion: stay on topic, build on others' points, and summarise the conversation.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach taking part in a focused discussion and building on others' points.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Reframe discussion as building together.",
                            instruction=(
                                "Greet the learner for the discussion wrap-up. Explain in "
                                "two sentences that a good discussion stays on topic and "
                                "builds on what others say with phrases like 'Building on "
                                "that...' and 'That's a good point, and...'. Ask them which "
                                "topic they most enjoy discussing with others."
                            ),
                        ),
                        TeacherStep(
                            id="build_on_points",
                            goal="Teach building on others' points.",
                            instruction=(
                                "Explain that strong contributions connect to the last "
                                "speaker (I agree with that, and...) and add one new idea. "
                                "Ask them to build on this point: 'Remote work saves "
                                "commuting time.' Preview today's reading, retell, message, "
                                "and spoken summary tasks."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has built on a point with a new idea, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_structure_discussion",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_STRUCTURE_ID",
                            activity="read",
                            task_widget="read_structure",
                            topic_override="Discussion structure",
                            generation_instructions=(
                                "Provide a short focused discussion thread in 3 parts and ask "
                                "the learner to label each part as the Opening (topic and "
                                "first view), Building (agreeing, adding, and questioning), "
                                "or Closing (summary and next step)."
                            ),
                            widget_requirements=(
                                "Target widget 'read_structure'. Provide passage_title, "
                                "structure_labels ['Opening', 'Building', 'Closing'], and "
                                "3 items, each with label, paragraph, correct_answer, and "
                                "explanation."
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
                        id="listen_retell_discussion",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Retell a discussion",
                            generation_instructions=(
                                "Generate a focused discussion (about 55 seconds) where two "
                                "people debate a topic, build on each other's points, and "
                                "reach a conclusion. Ask the learner to retell the key points "
                                "in writing in their own words (the topic, each view, the "
                                "conclusion)."
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
                        id="write_email_discussion",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Reply to a group thread",
                            generation_instructions=(
                                "Ask the learner to write a short reply (45-60 words) to a "
                                "group message thread discussing a shared decision, including "
                                "a clear opinion, one point that builds on someone else's, "
                                "one question, and a natural closing."
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
                        id="speak_present_discussion",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Summarise a discussion",
                            generation_instructions=(
                                "Ask the learner to speak for up to 60 seconds summarising a "
                                "recent discussion using a simple structure: the topic, the "
                                "main views, and the conclusion they reached."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_present'. Provide grammar_rule, "
                                "target_words (we discussed, on one hand, on the other hand, "
                                "in the end), a visual_prompt_description, an optional "
                                "model_presentation, and speaking_duration_seconds: 60."
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
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=(
            DaySource(
                title="Environment & Climate - Pollution, Energy & Sustainability",
                description=(
                    "Learners build vocabulary for the environment and climate "
                    "(pollution, renewable, drought, sustainable) and describe "
                    "environmental problems and solutions."
                ),
                focus="Vocabulary for the environment and climate: pollution, renewable, drought, sustainable, emissions.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach environment and climate vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce environment words.",
                            instruction=(
                                "Welcome the learner to vocabulary week. Explain in two "
                                "sentences that we use words like pollution (harmful waste in "
                                "the air or water) and renewable (energy that does not run "
                                "out) to talk about the environment. Ask them what they do to "
                                "reduce pollution."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more environment words.",
                            instruction=(
                                "Confirm 'pollution'. Ask what word means a long period with "
                                "little or no rain (drought), then summarise the contrast: "
                                "pollution is harmful waste, renewable energy does not run "
                                "out, and sustainable means able to continue without harming "
                                "the planet, and preview today's match, listen, transform, "
                                "and photo tasks."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used an environment word correctly, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_environment",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Environment & Climate Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match environment words (pollution, "
                                "renewable, drought, sustainable) to short definitions about "
                                "the planet, energy, and the climate."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options (the "
                                "environment words) and 4 items, each with prompt (the "
                                "definition), correct_answer, and explanation."
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
                        id="listen_mcq_environment",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="A talk about the climate",
                            generation_instructions=(
                                "Generate a short scenario (about 30 seconds) where someone "
                                "describes a local environmental problem, its cause, and one "
                                "sustainable solution. Ask the learner what the problem is, "
                                "the cause, and the solution."
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
                        id="write_sent_trans_environment",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Environment vocabulary sentence transformation",
                            generation_instructions=(
                                "Give the learner 2-3 wordy descriptions of environmental "
                                "ideas (energy that never runs out, a long time without rain, "
                                "harmful waste in the air) and ask them to rewrite each using "
                                "the precise word (renewable, drought, pollution)."
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
                        id="speak_pic_desc_environment",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe an environment scene",
                            generation_instructions=(
                                "Ask the learner to describe a photo of an environmental "
                                "scene aloud (for example a city under smog or a wind farm), "
                                "naming what is happening using environment words such as "
                                "pollution, renewable, and sustainable."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "a wind farm beside a smoggy city skyline, grammar_rule, and "
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
                title="Education & Learning - Courses, Study & Qualifications",
                description=(
                    "Learners build vocabulary for education and learning (enrol, "
                    "assignment, revise, qualification, deadline) and describe how "
                    "they study."
                ),
                focus="Vocabulary for education and learning: enrol, assignment, revise, qualification, deadline.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach education and learning vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce education words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that to enrol "
                                "means to sign up for a course and an assignment is a piece "
                                "of work your teacher sets. Ask them what they are learning "
                                "or studying at the moment."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more education words.",
                            instruction=(
                                "Confirm strong words like enrol. Ask what word means to "
                                "study again before an exam (revise), then preview today's "
                                "education reading, course-announcement dictation, "
                                "word-upgrade writing, and a timed study speech."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has produced an education word, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_context_mcq_education",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Education & Learning",
                            generation_instructions=(
                                "Write a short passage about a student who enrols on a "
                                "course, works on an assignment, and revises for an exam, "
                                "then ask the learner to infer the meaning of 'revise' from "
                                "context."
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
                        id="listen_dictation_education",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="Course Announcement",
                            generation_instructions=(
                                "Generate a short, clear course announcement (about 12 "
                                "seconds) with precise education vocabulary (assignment, "
                                "deadline, qualification), and ask the learner to type the "
                                "exact sentence they hear."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_dictation'. Provide audio_script, "
                                "target_words (the key education words), and 1 dictation "
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
                        id="write_word_upgrade_education",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_WORD_UPGRADE",
                            activity="write",
                            task_widget="write_word_upgrade",
                            topic_override="Vocabulary Word Upgrade",
                            generation_instructions=(
                                "Give the learner 3 plain education sentences (I signed up "
                                "for a class, I will study again before the test, the work is "
                                "due on Friday) and ask them to rewrite each using a precise "
                                "education word (enrolled, revise, deadline)."
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
                        id="speak_timed_education",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Timed Monologue Speech",
                            generation_instructions=(
                                "Ask the learner to describe how they study for an exam for "
                                "up to 60 seconds, covering the course, an assignment, how "
                                "they revise, and the deadline, using education words."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a "
                                "sample_response, grammar_rule, target_words (enrol, "
                                "assignment, revise, qualification), and "
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
                title="Culture & Society - Traditions, Community & Diversity",
                description=(
                    "Learners build vocabulary for culture and society "
                    "(tradition, community, diversity, heritage) and describe "
                    "customs and community life."
                ),
                focus="Vocabulary for culture and society: tradition, community, diversity, heritage.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach culture and society vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce culture words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that a tradition "
                                "is a custom passed down over time and a community is a group "
                                "of people who live together or share something. Ask them "
                                "about one tradition in their culture."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more culture words.",
                            instruction=(
                                "Confirm 'tradition'. Ask what word describes a mix of "
                                "different people and cultures (diversity), then preview "
                                "today's match, culture listening, short paragraph, and "
                                "culture-picture tasks."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a culture word correctly, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_culture",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Culture & Society",
                            generation_instructions=(
                                "Ask the learner to match culture words (tradition, "
                                "community, diversity, heritage) to short definitions."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options (the "
                                "culture words) and 4 items, each with prompt (the "
                                "definition), correct_answer, and explanation."
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
                        id="listen_mcq_culture",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Describing a local festival",
                            generation_instructions=(
                                "Generate a short monologue (about 25 seconds) where someone "
                                "describes a community festival, a tradition, and why it "
                                "matters. Ask comprehension questions about the festival, how "
                                "often it happens, and why people value it."
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
                        id="write_para_culture",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Describe a tradition",
                            generation_instructions=(
                                "Ask the learner to write 3-4 sentences about a tradition or "
                                "community event in their culture, including the words "
                                "tradition and heritage."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, "
                                "grammar_rule, target_words (tradition, community, heritage, "
                                "celebrate), minimum_words 20, sample_answer, and "
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
                        id="speak_pic_desc_culture",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a cultural scene",
                            generation_instructions=(
                                "Ask the learner to describe a cultural scene aloud, naming "
                                "what people are doing using 'There is' or 'I can see' and "
                                "culture words."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "a street festival with people in traditional dress, "
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
                title="Work & Careers - Jobs, Teamwork & Progress",
                description=(
                    "Learners build vocabulary for work and careers (promote, "
                    "resign, collaborate, deadline) and describe working life."
                ),
                focus="Vocabulary for work and careers: promote, resign, collaborate, deadline, colleague.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach work and careers vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce work words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that to promote "
                                "someone means to give them a higher position and to "
                                "collaborate means to work together with others. Ask them "
                                "what kind of work they do or would like to do."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more work words.",
                            instruction=(
                                "React to the work they named and explain that 'resign' "
                                "means to leave a job by choice, while a 'deadline' is the "
                                "time by which work must be finished. Ask which word "
                                "describes the day a report is due, then preview today's work "
                                "reading, dictation, rewrite, and timed speech."
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
                            topic_override="Working Life",
                            generation_instructions=(
                                "Write a short passage describing how a team collaborates on "
                                "a project, meets a deadline, and how one member is promoted, "
                                "and ask the learner to infer the meaning of 'collaborate' "
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
                            topic_override="Talking about a job",
                            generation_instructions=(
                                "Generate a short sentence (about 14 seconds) using work "
                                "vocabulary (promote, collaborate, deadline), and ask the "
                                "learner to type the exact sentence."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_dictation'. Provide audio_script, "
                                "target_words (the key work words), and 1 dictation item "
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
                        id="write_paraphrase_work",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="Rewrite with work vocabulary",
                            generation_instructions=(
                                "Give the learner 2 plain sentences about work (we all worked "
                                "together on the report, she left her job last month) and ask "
                                "them to rewrite each using more precise work vocabulary "
                                "(collaborated, resigned)."
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
                            topic_override="Timed Work Speech",
                            generation_instructions=(
                                "Ask the learner to talk for up to 60 seconds about their "
                                "work or studies, describing what they do, who they "
                                "collaborate with, and an important deadline."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a "
                                "sample_response, grammar_rule, target_words (promote, "
                                "resign, collaborate, deadline), and "
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
                title="News & Current Issues - Headlines, Policy & Debate",
                description=(
                    "Learners build vocabulary for news and current issues "
                    "(headline, policy, debate, impact) and talk about what is "
                    "happening in the world."
                ),
                focus="Vocabulary for news and current issues: headline, policy, debate, impact, coverage.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach news and current-issues vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce news words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that a headline "
                                "is the title of a news story and a policy is a plan or rule "
                                "made by a government or group. Ask them how they usually "
                                "follow the news."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more news words.",
                            instruction=(
                                "Confirm 'headline'. Ask what word means a serious discussion "
                                "where people share different opinions (debate), then preview "
                                "today's match, news listening, sentence transform, and "
                                "news-picture tasks."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a news word correctly, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_news",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="News & Current Issues Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match news words (headline, policy, "
                                "debate, impact) to their meanings."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options (the news "
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
                        id="listen_mcq_news",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="A news report",
                            generation_instructions=(
                                "Generate a monologue (about 40 seconds) where a reporter "
                                "summarises a story, a new policy, and its impact. Ask "
                                "comprehension questions about the story, the policy, and the "
                                "impact."
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
                        id="write_sent_trans_news",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="News vocabulary sentence transformation",
                            generation_instructions=(
                                "Give the learner 3 wordy news phrases (the title of the "
                                "story, a plan made by the government, the effect it had on "
                                "people) and ask them to rewrite each using a precise news "
                                "word (headline, policy, impact)."
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
                        id="speak_pic_desc_news",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a news scene",
                            generation_instructions=(
                                "Ask the learner to describe a news scene aloud, using news "
                                "words (headline, policy, debate, impact) to talk about what "
                                "is happening and why it matters."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "a news studio with a reporter and a headline on the screen, "
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
                title="Abstract Qualities & Values - Integrity, Resilience & Perspective",
                description=(
                    "Learners build precise vocabulary for abstract qualities and "
                    "values (integrity, resilience, perspective, empathy) and "
                    "upgrade plain descriptions of how people think and act."
                ),
                focus="Vocabulary for abstract qualities and values: integrity, resilience, perspective, empathy, ambition.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach precise vocabulary for abstract qualities and values.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce values words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that 'integrity' "
                                "means being honest and having strong principles, and "
                                "'resilience' means the ability to recover after "
                                "difficulties. Ask them to tell you about a person who shows "
                                "real integrity."
                            ),
                        ),
                        TeacherStep(
                            id="stronger_words",
                            goal="Practise stronger values words.",
                            instruction=(
                                "Reflect their answer back and confirm it. Explain "
                                "'perspective' (the particular way someone sees a situation) "
                                "and ask for a word that describes understanding and sharing "
                                "another person's feelings (empathy), then preview today's "
                                "profile reading, dictation, word-upgrade, and values speech."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has produced a precise quality word, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_context_mcq_values",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Infer values from context",
                            generation_instructions=(
                                "Write a short profile of a person whose actions reveal their "
                                "values (keeps promises even when it is hard, recovers after "
                                "setbacks, listens to other views). Ask the learner to infer "
                                "the quality word that best fits at each point."
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
                        id="listen_dictation_values",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="Dictate values words",
                            generation_instructions=(
                                "Generate a short personal description (about 45 seconds) in "
                                "which the speaker names abstract qualities (integrity, "
                                "resilience). Ask the learner to type the exact quality word "
                                "that completes each blanked sentence."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_dictation'. Provide audio_script, "
                                "target_words (the quality words), and 2 dictation items, "
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
                        id="write_word_upgrade_values",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_WORD_UPGRADE",
                            activity="write",
                            task_widget="write_word_upgrade",
                            topic_override="Upgrade values vocabulary",
                            generation_instructions=(
                                "Give the learner 3 plain sentences about values (he is "
                                "always honest and fair, she keeps going after problems, he "
                                "understands how others feel) and ask them to rewrite each "
                                "using a stronger quality word (integrity, resilience, "
                                "empathy)."
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
                        id="speak_timed_values",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Talk about a value you admire",
                            generation_instructions=(
                                "Ask the learner to talk about a person they admire using at "
                                "least one strong quality word and explaining why that value "
                                "matters."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a "
                                "sample_response, grammar_rule, target_words (integrity, "
                                "resilience, perspective, empathy, ambition), and "
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
                    "words across Environment, Education, Culture, Work, News, and "
                    "Values through matching, listening, free recall writing, and "
                    "a speaking challenge."
                ),
                focus="Consolidate the week's vocabulary covering Environment, Education, Culture, Work, News, and Values.",
                teacher=TeacherBlueprint(
                    lesson_goal="Consolidate the week's vocabulary across all six topics.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the review day.",
                            instruction=(
                                "Greet the learner for the weekly review. Explain in one "
                                "sentence that today consolidates the week's words across "
                                "Environment, Education, Culture, Work, News, and Values. Ask "
                                "them to share one word they remember from this week and what "
                                "it means."
                            ),
                        ),
                        TeacherStep(
                            id="recall_prompt",
                            goal="Prompt active recall.",
                            instruction=(
                                "Affirm the word they shared and explain that reviewing "
                                "moves words into long-term memory. Ask them to recall one "
                                "more strong word from the week (for example a word meaning "
                                "energy that never runs out or a word for honest, principled "
                                "behaviour), then preview today's match, story listening, "
                                "free-recall paragraph, and 90-second speaking challenge."
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
                        id="read_word_match_review_w11",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Weekly Review Match",
                            generation_instructions=(
                                "Ask the learner to match 6 words from across the week (one "
                                "per topic, for example sustainable, qualification, heritage, "
                                "collaborate, policy, resilience) to their definitions."
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
                        id="listen_mcq_review_w11",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Weekly consolidation story",
                            generation_instructions=(
                                "Generate a short personal story (about 28 seconds) that "
                                "weaves in vocabulary from all six topics (sustainable, "
                                "qualification, heritage, collaborate, policy, resilience). "
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
                        id="write_para_review_w11",
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
                        id="speak_timed_review_w11",
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
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=(
            DaySource(
                title="Leading Part of a Discussion - Invite Others & Summarise",
                description=(
                    "Learners build the confidence to lead part of a discussion: "
                    "a story about guiding a group, shadowing a clear invitation "
                    "to others, turning passive language into leadership language, "
                    "and reading a short paragraph aloud."
                ),
                focus="Lead part of a discussion: motivation story, shadowing an invitation, reframing into leadership language, and reading aloud.",
                teacher=TeacherBlueprint(
                    lesson_goal="Build the confidence to lead part of a discussion.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame leading as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week. Explain in two "
                                "sentences that leading a discussion means guiding the topic "
                                "and inviting others to speak, and that this gets easier with "
                                "small steps. Ask them to name one situation where they would "
                                "like to lead a conversation more."
                            ),
                        ),
                        TeacherStep(
                            id="preview",
                            goal="Preview the day and reassure.",
                            instruction=(
                                "Affirm their answer warmly. Preview that today they will "
                                "read a short story about leading a group, shadow a confident "
                                "invitation to others, reframe a passive sentence into "
                                "leadership language, and read a short paragraph aloud."
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
                        id="read_comp_mcq_leading",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Leading a group discussion story",
                            generation_instructions=(
                                "Write a short, encouraging story about someone who guides a "
                                "group discussion: they open the topic, invite a quiet member "
                                "to share, and summarise the group's decision. Then ask "
                                "comprehension questions about how they opened, who they "
                                "invited, and the result."
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
                        id="listen_shadow_leading",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Confident invitation shadowing",
                            generation_instructions=(
                                "Generate a short, warm clip (about 15 seconds) of a person "
                                "inviting others into a discussion (What do you think, Priya? "
                                "/ Let's hear another view.), for the learner to shadow with "
                                "natural pacing and confidence."
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
                        id="write_sent_trans_leading",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Reframe passive language into leadership language",
                            generation_instructions=(
                                "Give the learner 3 passive statements (I just follow what "
                                "others decide, I never lead anything, nobody listens to me) "
                                "and ask them to reframe each into confident leadership "
                                "language using verbs like guide, invite, and summarise."
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
                        id="speak_read_aloud_leading",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_READ_ALOUD",
                            activity="speak",
                            task_widget="read_aloud",
                            topic_override="Leadership paragraph read aloud",
                            generation_instructions=(
                                "Give the learner a short, positive paragraph (about 35 "
                                "words) about guiding a group and inviting every voice in, to "
                                "read aloud with clear pronunciation and steady pacing."
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
                title="Building a Clear Argument - Claim, Reason & Example",
                description=(
                    "Learners build a clear argument with a claim, a reason, and "
                    "an example, tell a well-built argument from a weak one, and "
                    "write and speak their case under time pressure."
                ),
                focus="Build an argument with claim, reason, and example; notice strong vs weak structure; and write/speak a case under time pressure.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach building a clear argument with claim, reason, and example.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame a clear argument.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that a clear "
                                "argument has a claim, a reason, and an example, and that "
                                "structure makes you sound convincing. Ask them to tell you "
                                "one opinion they hold, in a single sentence."
                            ),
                        ),
                        TeacherStep(
                            id="argument_markers",
                            goal="Name strong vs weak argument structure.",
                            instruction=(
                                "React warmly to their view. Explain that a strong argument "
                                "adds a reason (because...) and an example (for instance...), "
                                "while a weak one is just an opinion with no support, and "
                                "invite them to add a reason and an example. Preview that "
                                "today they will tell strong from weak arguments and write "
                                "and speak their case clearly under time pressure."
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
                        id="read_tone_id_argument",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Strong vs weak argument",
                            generation_instructions=(
                                "Provide two short responses to the same question, one a "
                                "well-built argument (claim, reason, example) and one a weak "
                                "opinion with no support, and ask the learner to label each "
                                "as Well-built or Weak."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tone_id'. Provide passage_title and 2 "
                                "items, each with sender, message, prompt, options (Weak / "
                                "Unsupported, Well-built / Supported), correct_index, and "
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
                        id="listen_mcq_argument",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Argument structure patterns",
                            generation_instructions=(
                                "Generate a clip (about 22 seconds) of two speakers answering "
                                "the same question: one gives only an opinion, one gives a "
                                "claim with a reason and an example. Ask the learner which "
                                "speaker builds a clearer argument."
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
                        id="write_timed_argument",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Timed Argument Write",
                            generation_instructions=(
                                "Ask the learner to argue in writing whether students should "
                                "learn a second language, in at least 25 words under a short "
                                "time limit, including a claim, a reason, and an example."
                            ),
                            widget_requirements=(
                                "Target widget 'write_timed'. Provide prompt, grammar_rule, "
                                "target_words (I argue that, because, for instance, "
                                "therefore), writing_duration_seconds: 180, sample_answer, "
                                "and answer_hints."
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
                        id="speak_timed_argument",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Timed Improvised Argument Speech",
                            generation_instructions=(
                                "Ask the learner to speak for up to 60 seconds on whether "
                                "technology makes life easier, building a clear argument with "
                                "a claim, a reason, and an example."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a "
                                "sample_response, grammar_rule, target_words (I believe, "
                                "because, for example, overall), and "
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
                title="Goals, Ambitions & Trade-offs - Talk About Your Future Honestly",
                description=(
                    "Learners speak honestly about their goals and ambitions and "
                    "the trade-offs they involve, tell grounded-confident from "
                    "unrealistic or vague tone, enrich plain goal statements, and "
                    "describe ambition through others."
                ),
                focus="Talk about goals, ambitions, and trade-offs: build grounded self-talk, distinguish realistic vs unrealistic tone, and describe ambition.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach describing goals, ambitions, and trade-offs honestly and confidently.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Invite a simple goal.",
                            instruction=(
                                "Greet the learner. Explain in one sentence that knowing your "
                                "goals and the trade-offs they involve helps you plan with "
                                "confidence. Ask them to name one goal they have in one "
                                "simple sentence."
                            ),
                        ),
                        TeacherStep(
                            id="goals_tradeoffs",
                            goal="Contrast confident and grounded goal language.",
                            instruction=(
                                "Affirm their start. Explain that we can describe a goal "
                                "confidently (I'm aiming to...) and name its trade-off "
                                "honestly (it means giving up...), and preview today's "
                                "goal-bio reading, realistic-versus-unrealistic listening, "
                                "richer-description writing, and a describe-a-person speaking "
                                "task."
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
                        id="read_comp_mcq_goals",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="A personal goals bio",
                            generation_instructions=(
                                "Write a short first-person bio of someone who describes a "
                                "clear goal, the trade-off it involves, and their plan to "
                                "reach it. Then ask comprehension questions about their goal, "
                                "the trade-off, their plan, and their motivation."
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
                        id="listen_tone_goals",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Realistic vs unrealistic ambition",
                            generation_instructions=(
                                "Generate two versions of the same person describing their "
                                "goals: a grounded-realistic version (I'm working toward..., "
                                "step by step) and an unrealistic version (I'll be famous "
                                "next month, no effort needed). Ask the learner to label each "
                                "version's tone."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_tone'. Provide two intros (each with "
                                "id, label, speaker, audio_script) and 2 MCQ items, each "
                                "with prompt, options (Unrealistic / Vague, Realistic / "
                                "Grounded), correct_index, and explanation."
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
                        id="write_sent_trans_goals",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Richer goal-statement transforms",
                            generation_instructions=(
                                "Give the learner 3 plain goal statements (I want a better "
                                "job, I hope to travel, I would like to study more) and ask "
                                "them to rewrite each into a clearer, grounded goal with a "
                                "trade-off or step (I'm aiming to..., which means...)."
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
                        id="speak_pic_desc_goals",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a person working toward a goal",
                            generation_instructions=(
                                "Ask the learner to describe a picture of a person working "
                                "toward a goal, saying what they are doing and what ambition "
                                "they might be pursuing, using speculative phrases like looks "
                                "like, seems to be, and might be."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "a person studying late at a desk covered in plans, "
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
                title="Handling Disagreement or Criticism - Stay Calm and Respond",
                description=(
                    "Learners learn to handle disagreement or criticism with "
                    "composure: spot tone shifts from defensive to open, shadow "
                    "calm responding phrases, reflect under time, and handle "
                    "unpredictable pushback."
                ),
                focus="Handle disagreement and criticism: tone-shift identification, calm-response shadowing, timed reflection, and unpredictable pushback.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach staying calm and responding well to disagreement or criticism.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Normalise disagreement.",
                            instruction=(
                                "Greet the learner. Explain in one sentence that receiving "
                                "disagreement or criticism is a normal part of any "
                                "conversation. Ask what they usually do when someone "
                                "disagrees with them."
                            ),
                        ),
                        TeacherStep(
                            id="respond_calmly",
                            goal="Teach calm responding.",
                            instruction=(
                                "Reassure them that staying calm and acknowledging the other "
                                "view keeps the conversation respectful. Preview today's "
                                "tone-shift reading, calm-response shadowing, timed "
                                "reflection, and pushback challenge."
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
                        id="read_tone_id_criticism",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Responding tone shift",
                            generation_instructions=(
                                "Provide two short messages where a speaker first reacts "
                                "defensively and then responds calmly to criticism, and ask "
                                "the learner to identify the tone shift in each (for example "
                                "defensive to open, annoyed to composed)."
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
                        id="listen_shadow_criticism",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Calm response phrases",
                            generation_instructions=(
                                "Generate a short clip (about 20 seconds) where a speaker "
                                "responds calmly to criticism using phrases like 'That's a "
                                "fair point', 'I see what you mean', and 'Let me explain my "
                                "thinking', for the learner to shadow with the same calm "
                                "flow."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_shadow'. Provide audio_script, "
                                "text_to_shadow, target_words (That's a fair point, I see "
                                "what you mean, Let me explain), and grammar_rule."
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
                        id="write_timed_criticism",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Reflecting on criticism",
                            generation_instructions=(
                                "Ask the learner to write a short personal reflection under "
                                "a short time limit on how they respond when someone "
                                "criticises their work, using transition words to organise "
                                "their thoughts."
                            ),
                            widget_requirements=(
                                "Target widget 'write_timed'. Provide prompt, grammar_rule, "
                                "target_words (Usually, Instead of, In future), "
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
                        id="speak_smalltalk_criticism",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Unpredictable pushback",
                            generation_instructions=(
                                "Set up an unpredictable exchange where the partner pushes "
                                "back on the learner's idea and the learner stays calm, "
                                "acknowledges the point, and responds without getting "
                                "defensive."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_smalltalk'. Provide a dialogue_context "
                                "alternating partner and learner turns, target_words (That's "
                                "fair, I understand, even so), and "
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
                title="Pitching an Idea Briefly - Problem, Idea & Benefit",
                description=(
                    "Learners pitch an idea briefly and confidently with a simple "
                    "structure — problem, idea, benefit: a passage about a good "
                    "pitch, an enthusiastic monologue, upgrading plain ideas into "
                    "pitches, and describing a scene that needs a solution."
                ),
                focus="Pitch an idea briefly using problem, idea, and benefit, with confident language.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach pitching an idea briefly with problem, idea, and benefit.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Invite an idea the learner cares about.",
                            instruction=(
                                "Greet the learner. Explain in one sentence that a short, "
                                "clear pitch helps people quickly understand and support your "
                                "idea. Ask them what one idea they would like to suggest to "
                                "improve their workplace or town."
                            ),
                        ),
                        TeacherStep(
                            id="give_reasons",
                            goal="Model a clear pitch structure.",
                            instruction=(
                                "React warmly and note that a strong pitch names the problem, "
                                "the idea, and the benefit clearly and briefly. Preview "
                                "today's pitch reading, enthusiastic listening, idea-upgrade "
                                "writing, and a scene-that-needs-a-solution speaking task."
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
                        id="read_comp_mcq_pitching",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="A short pitch",
                            generation_instructions=(
                                "Write a warm first-person passage where someone pitches an "
                                "idea to improve their community (for example a shared tool "
                                "library), covering the problem, the idea, the benefit, and "
                                "the next step. Then ask comprehension questions about each."
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
                        id="listen_mcq_pitching",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Enthusiasm for an idea",
                            generation_instructions=(
                                "Generate an enthusiastic monologue (about 25 seconds) where "
                                "someone pitches an idea (the problem it solves, the idea "
                                "itself, the benefit). Ask comprehension questions about "
                                "those details."
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
                        id="write_sent_trans_pitching",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Upgrade plain ideas into pitches",
                            generation_instructions=(
                                "Give the learner 3 plain idea statements (we need more bins, "
                                "the app is slow, meetings are too long) and ask them to "
                                "transform each into a brief pitch naming the problem and the "
                                "benefit using patterns like 'The problem is..., so I "
                                "suggest..., which would...'."
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
                        id="speak_pic_desc_pitching",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a scene that needs a solution",
                            generation_instructions=(
                                "Ask the learner to describe a scene that shows a problem "
                                "aloud (the scene, what is wrong) and pitch one idea to "
                                "improve it, using confident problem-idea-benefit language."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing "
                                "an overflowing recycling area outside an office, "
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
                title="Longer Structured Talk - Intro, Two Points & Conclusion",
                description=(
                    "Learners give a longer structured talk with poise: tell a "
                    "well-structured talk from a rambling one, train their ear for "
                    "clear signposting, draft a short structured talk under time, "
                    "and record a structured talk with an intro, two points, and a "
                    "conclusion."
                ),
                focus="Give a longer structured talk: identify structured vs rambling delivery, hear clear signposting, timed structured draft, and a recorded structured talk.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach giving a longer structured talk with poise.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Surface what a structured talk includes.",
                            instruction=(
                                "Greet the learner. Explain in one sentence that a longer "
                                "talk sounds confident when it has a clear intro, two main "
                                "points, and a conclusion. Ask what two points they would "
                                "include if they had to talk about a topic they know well."
                            ),
                        ),
                        TeacherStep(
                            id="structure_poise",
                            goal="Add signposting and poise.",
                            instruction=(
                                "Affirm their foundation and explain that signposting "
                                "(First..., My second point..., To conclude...) plus a steady "
                                "voice keeps a longer talk clear and poised. Preview today's "
                                "structured-versus-rambling reading, signposting listening, "
                                "timed structured note, and a recorded structured talk."
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
                        id="read_tone_id_structured_talk",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Structure in longer talks",
                            generation_instructions=(
                                "Provide two short talks on the same topic, one "
                                "well-structured (clear intro, signposted points, conclusion) "
                                "and one rambling (no order, no signposting), and ask the "
                                "learner to label each."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tone_id'. Provide passage_title and 2 "
                                "items, each with sender, message, prompt, options including "
                                "Well-structured and clear and Rambling and unclear, "
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
                        id="listen_tone_structured_talk",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Audio structured talks",
                            generation_instructions=(
                                "Generate two spoken talks on the same topic, one clearly "
                                "signposted and evenly paced and one rambling with no clear "
                                "order, and ask the learner which sounds more structured and "
                                "what signals the structure."
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
                        id="write_timed_structured_talk",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Structured talk plan",
                            generation_instructions=(
                                "Ask the learner to write a short structured talk plan under "
                                "a short time limit: an intro sentence, two point sentences, "
                                "and a conclusion sentence on a topic they know well."
                            ),
                            widget_requirements=(
                                "Target widget 'write_timed'. Provide prompt, grammar_rule "
                                "describing the intro-points-conclusion structure, "
                                "target_words (To begin, My first point, secondly, to "
                                "conclude), writing_duration_seconds: 180, sample_answer, "
                                "and answer_hints."
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
                        id="speak_present_structured_talk",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Structured talk",
                            generation_instructions=(
                                "Ask the learner to record a 90-second structured talk with a "
                                "clear intro, two main points, and a conclusion, speaking "
                                "with even pacing and clear signposting."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_present'. Provide a "
                                "visual_prompt_description outlining the intro, two points, "
                                "and conclusion, an optional model_presentation, "
                                "grammar_rule, target_words (To begin, firstly, secondly, to "
                                "conclude), and speaking_duration_seconds: 90."
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
                title="Full Confidence Showcase (B1)",
                description=(
                    "Cycle 3 wrap-up: learners show their growth with an inspiring "
                    "reading, an energetic shadow, a reflective timed write, and a "
                    "friendly debate with the tutor."
                ),
                focus="Cycle 3 wrap-up: show your growth with inspiring reading, shadowing, reflective writing, and a friendly debate task.",
                teacher=TeacherBlueprint(
                    lesson_goal="Celebrate and showcase Cycle 3 speaking growth.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Invite reflection on growth.",
                            instruction=(
                                "Greet the learner for the final day and Cycle 3 wrap-up. "
                                "Explain in one sentence that today is a confidence "
                                "showcase. Ask how they feel about their speaking confidence "
                                "now compared with the start of this cycle."
                            ),
                        ),
                        TeacherStep(
                            id="showcase_preview",
                            goal="Preview the showcase tasks.",
                            instruction=(
                                "Celebrate their growth warmly. Preview that today they will "
                                "read an inspiring passage about leading and arguing with "
                                "confidence, shadow a confident speaker, write a timed "
                                "reflection on their growth, and finish with a friendly "
                                "debate where you take the opposite side."
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
                        id="read_comp_mcq_showcase_w12",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Growing in confidence",
                            generation_instructions=(
                                "Write an inspiring first-person passage about someone who "
                                "grew more confident in English by leading discussions and "
                                "making clear arguments after a mentor said confidence grows "
                                "with action, not waiting. Then ask comprehension questions "
                                "about the early struggle, the mentor's advice, the first "
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
                        id="listen_shadow_showcase_w12",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Fluent and energetic shadow session",
                            generation_instructions=(
                                "Generate a short, energetic motivational line (about 15 "
                                "seconds) about being proud of one's growing confidence and "
                                "speaking up with structure and reasons, for the learner to "
                                "shadow, matching the rising and falling intonation."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_shadow'. Provide audio_script, "
                                "text_to_shadow, target_words (proud of, growing, "
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
                        id="write_timed_showcase_w12",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Reflecting on Cycle 3 growth",
                            generation_instructions=(
                                "Ask the learner to write a short personal reflection under "
                                "a short time limit on what they learned about themselves "
                                "this cycle, using reflective and forward-looking transition "
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
                        id="speak_debate_showcase_w12",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_DEBATE",
                            activity="speak",
                            task_widget="speak_debate",
                            topic_override="Debate: Lead firmly vs build consensus first",
                            generation_instructions=(
                                "Set up a friendly debate on whether it is better to lead a "
                                "discussion firmly or build consensus slowly first. The AI "
                                "argues for building consensus first; the learner records a "
                                "counter-argument using strong opinion starters and "
                                "transition markers."
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

    # ── Cycle 4 — Expanding (B1+) ───────────────────────────────
    WeekSource(
        week_number=5,
        theme_type="grammar",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=(
            DaySource(
                title="Past Perfect Continuous - Duration Before a Past Moment",
                description=(
                    "Learners use the past perfect continuous (had been + verb-ing) to "
                    "show that an action had been ongoing for a period before another "
                    "past event, often with for and since."
                ),
                focus=(
                    "Past perfect continuous (had been + -ing) for ongoing actions before "
                    "another past moment, with for and since."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach the past perfect continuous for duration before a past event.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce the past perfect continuous.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that the past perfect "
                                "continuous uses had been plus verb-ing to show something had been "
                                "happening for a while before another past action. Ask how long they had "
                                "been doing their current job or course before a recent change."
                            ),
                        ),
                        TeacherStep(
                            id="had_been_ing",
                            goal="Teach had been + verb-ing.",
                            instruction=(
                                "Use the learner's answer to explain that had been is the same for every "
                                "subject and is followed by verb-ing. Ask them to say one sentence about "
                                "something a colleague had been working on before a deadline last week."
                            ),
                        ),
                        TeacherStep(
                            id="for_since",
                            goal="Teach for and since with the form.",
                            instruction=(
                                "Introduce for with a length of time and since with a starting point with "
                                "the past perfect continuous. Ask for one sentence using since and had "
                                "been plus verb-ing."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has shown the pattern at least once, ask only: Ready to "
                                "try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_cloze_past_perf_cont",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CLOZE",
                            activity="read",
                            task_widget="fill_blanks",
                            topic_override="Past perfect continuous duration",
                            generation_instructions=(
                                "Write a 4-5 blank connected passage about a busy week where several "
                                "actions had been going on for a period before a key moment. Focus on the "
                                "past perfect continuous with had been + verb-ing and for or since."
                            ),
                            widget_requirements=(
                                "Always include base_verb for every blank so the learner forms had been + "
                                "verb-ing. Do not repeat base_verb inline in the passage after each ___ — "
                                "the UI shows it separately."
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
                        id="listen_mcq_past_perf_cont",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Listening for past perfect continuous",
                            generation_instructions=(
                                "Generate a 70-100 word spoken passage about a person describing a past "
                                "situation where longer actions had been in progress, using had been, "
                                "for, and since before another event happened."
                            ),
                            widget_requirements=(
                                "Generate 3-4 MCQ items with prompt, options, correct_index, and "
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
                        id="write_past_perf_cont_sentences",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_OPEN_SENT",
                            activity="write",
                            task_widget="open_text",
                            topic_override="Write past perfect continuous sentences",
                            generation_instructions=(
                                "Ask for affirmative past perfect continuous sentences using I, he, and "
                                "she, describing what had been happening for a period before another past "
                                "action, with for or since."
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
                        id="speak_past_perf_cont_events",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Say what had been happening before a past moment",
                            generation_instructions=(
                                "Ask the learner to say short past perfect continuous sentences about "
                                "what had been happening before a past moment using had been and "
                                "verb-ing."
                            ),
                            widget_requirements=(
                                "Create exactly 3 speaking prompts: one with I, one with he, and one with "
                                "she. Include speaking_duration_seconds: 45."
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
                title="Third Conditional - Regrets About the Past",
                description=(
                    "Learners use the third conditional (if + past perfect, would have + "
                    "past participle) to talk about unreal past situations and their "
                    "results (If I had known, I would have helped)."
                ),
                focus=(
                    "Third conditional with if + past perfect and would have + past "
                    "participle for unreal past situations."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach the third conditional for regrets and unreal past situations.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce the third conditional.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that the third conditional "
                                "talks about an unreal past situation and its imagined result, using if + "
                                "past perfect and would have + past participle. Ask what they would have "
                                "done differently last year if they had had more time."
                            ),
                        ),
                        TeacherStep(
                            id="if_clause_pp",
                            goal="Teach the past perfect in the if-clause.",
                            instruction=(
                                "Use the learner's idea to explain that the if-clause uses had plus a "
                                "past participle (If I had studied..., If we had left...). Ask them to "
                                "finish 'If I had known earlier, ...' with their own result."
                            ),
                        ),
                        TeacherStep(
                            id="would_have",
                            goal="Teach would have + past participle.",
                            instruction=(
                                "Show that the result clause uses would have plus a past participle. Ask "
                                "them to make one sentence with would have about a choice they did not "
                                "make in the past."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has shown the pattern at least once, ask only: Ready to "
                                "try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_error_spot_third_conditional",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_ERROR_SPOT",
                            activity="read",
                            task_widget="error_spotting",
                            topic_override="Spot third conditional errors",
                            generation_instructions=(
                                "Generate a 5-sentence passage about regrets and different past choices. "
                                "Each sentence must contain exactly one grammatical error, so there are "
                                "exactly 5 error tokens. Make mistakes diverse across third-conditional "
                                "usage: wrong tense in the if-clause, missing would have, will instead of "
                                "would have, wrong past participle after would have, and a "
                                "condition-marker mismatch."
                            ),
                            widget_requirements=(
                                "Target widget 'error_spotting'. Return exactly 5 `passage_sentences`. "
                                "Each sentence must include `sentence_id`, `tokens`, and one `error` "
                                "object. Each token needs stable `token_id`, `text`, and `is_error`; "
                                "exactly one token per sentence must have `is_error: true`. Each `error` "
                                "must include token_id, incorrect_phrase, correction, error_type, rule, "
                                "and explanation. Set `total_errors` to 5. Allowed error_type values: "
                                "irregular_past, missing_past_auxiliary, passive_helper_missing, "
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
                        id="listen_cloze_third_conditional",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_CLOZE",
                            activity="listen",
                            task_widget="listen_cloze",
                            topic_override="Listen and fill third conditional forms",
                            generation_instructions=(
                                "Listen to the short regrets audio, then complete the paraphrased notes "
                                "with the missing third-conditional verb phrases from the clip."
                            ),
                            widget_requirements=(
                                "Set inner_widget to 'fill_in_blanks'. Use the authored audio_script, "
                                "passage, and 5 BlankItems exactly as provided so rule-based scoring can "
                                "compare each typed verb phrase with correct_answer."
                            ),
                            static_payload=
                            {'task_intro': 'Listen, then complete the third-conditional notes.',
                             'instructions': 'Play the audio once, then type the missing third-conditional verbs '
                                             'in the paraphrased notes.',
                             'estimated_time_minutes': 3,
                             'inner_widget': 'fill_in_blanks',
                             'audio_genre': 'Reflective regrets monologue',
                             'audio_script': 'Sometimes I think about different choices. If I had studied harder, '
                                             'I would have passed the exam. If we had left earlier, we would have '
                                             'caught the train. If she had known the truth, she would have called '
                                             'me. If they had invited us, we would have come to the party. '
                                             'Honestly, if I had listened to your advice, I would have saved a lot '
                                             'of time.',
                             'passage_title': 'Different Choices Notes',
                             'passage': 'If I ___ harder, I would have passed the exam. If we had left earlier, we '
                                        '___ the train. If she had known the truth, she ___ me. If they ___ us, we '
                                        'would have come. If I had listened to your advice, I ___ a lot of time.',
                             'items': [{'item_id': 'b1',
                                        'blank_id': 'b1',
                                        'sentence_with_blank': 'If I ___ harder, I would have passed the exam.',
                                        'base_verb': 'study',
                                        'correct_answer': 'had studied',
                                        'distractors': ['studied', 'would study'],
                                        'options': ['had studied', 'studied', 'would study'],
                                        'grammar_rule': 'Use the past perfect in the if-clause of the third '
                                                        'conditional.',
                                        'explanation': 'The if-clause needs had + past participle, so we use had '
                                                       'studied.'},
                                       {'item_id': 'b2',
                                        'blank_id': 'b2',
                                        'sentence_with_blank': 'If we had left earlier, we ___ the train.',
                                        'base_verb': 'catch',
                                        'correct_answer': 'would have caught',
                                        'distractors': ['will catch', 'caught'],
                                        'options': ['would have caught', 'will catch', 'caught'],
                                        'grammar_rule': 'Use would have + past participle in the result clause.',
                                        'explanation': 'The unreal past result uses would have caught.'},
                                       {'item_id': 'b3',
                                        'blank_id': 'b3',
                                        'sentence_with_blank': 'If she had known the truth, she ___ me.',
                                        'base_verb': 'call',
                                        'correct_answer': 'would have called',
                                        'distractors': ['will call', 'called'],
                                        'options': ['would have called', 'will call', 'called'],
                                        'grammar_rule': 'Use would have + past participle in the result clause.',
                                        'explanation': 'The imagined past result uses would have called.'},
                                       {'item_id': 'b4',
                                        'blank_id': 'b4',
                                        'sentence_with_blank': 'If they ___ us, we would have come.',
                                        'base_verb': 'invite',
                                        'correct_answer': 'had invited',
                                        'distractors': ['invited', 'would invite'],
                                        'options': ['had invited', 'invited', 'would invite'],
                                        'grammar_rule': 'Use the past perfect in the if-clause of the third '
                                                        'conditional.',
                                        'explanation': 'The if-clause needs had invited.'},
                                       {'item_id': 'b5',
                                        'blank_id': 'b5',
                                        'sentence_with_blank': 'If I had listened to your advice, I ___ a lot of '
                                                               'time.',
                                        'base_verb': 'save',
                                        'correct_answer': 'would have saved',
                                        'distractors': ['will save', 'saved'],
                                        'options': ['would have saved', 'will save', 'saved'],
                                        'grammar_rule': 'Use would have + past participle in the result clause.',
                                        'explanation': 'The imagined past result uses would have saved.'}],
                             'target_words_in_audio': ['had studied',
                                                       'would have caught',
                                                       'would have called',
                                                       'had invited',
                                                       'would have saved']},
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
                        id="write_error_corr_third_conditional",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_ERROR_CORR",
                            activity="write",
                            task_widget="error_correction",
                            topic_override="Correct third conditional mistakes",
                            generation_instructions=(
                                "Give the learner 3 sentences that each contain one third conditional "
                                "error — mix wrong tense in the if-clause and would have mistakes. Ask "
                                "the learner to rewrite each sentence correctly."
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
                        id="speak_read_aloud_third_conditional",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_READ_ALOUD",
                            activity="speak",
                            task_widget="read_aloud",
                            topic_override="Read third conditional passage aloud",
                            generation_instructions=(
                                "Give the learner a connected third conditional narrative passage of "
                                "55-70 words to read aloud, describing several unreal past situations and "
                                "their imagined results."
                            ),
                            widget_requirements=(
                                "Populate `text_to_read_aloud` with a single connected second conditional "
                                "passage (55-70 words) describing imaginary situations and their results. "
                                "Set `task_intro` to 'Read the passage above out loud.' Include "
                                "`grammar_rule_to_practice` explaining the second conditional with if + "
                                "past simple and would + base verb, and `speaking_duration_seconds: 45`."
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
                title="Causative Have & Get - Arranging for Others to Do Things",
                description=(
                    "Learners use causative have and get (have something done, get "
                    "someone to do something) to say they arrange for another person to "
                    "perform an action, not that they do it themselves."
                ),
                focus=(
                    "Causative have/get: have + object + past participle and get + object "
                    "+ to-infinitive for arranged actions."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach causative have and get for arranged actions.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce causative have and get.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that causative have and get "
                                "show you arrange for someone else to do something (I had my hair cut, I "
                                "got him to check it). Ask them to tell you one thing they had done for "
                                "them recently by a professional or service."
                            ),
                        ),
                        TeacherStep(
                            id="have_done",
                            goal="Teach have + object + past participle.",
                            instruction=(
                                "Use the learner's example to confirm have + object + past participle "
                                "(She had her laptop repaired). Ask them to make one present sentence "
                                "about something they need to have done this week."
                            ),
                        ),
                        TeacherStep(
                            id="get_to",
                            goal="Teach get + object + to-infinitive.",
                            instruction=(
                                "Introduce get + someone + to + verb for persuading or arranging (I got "
                                "my colleague to help). Ask for one sentence with got and to about a task "
                                "someone else did for them."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has shown the pattern at least once, ask only: Ready to "
                                "try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_causative",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Understand causative arrangements in context",
                            generation_instructions=(
                                "Write a 60-75 word passage about someone arranging services (repairs, "
                                "deliveries, appointments) using causative have and get naturally. Then "
                                "ask comprehension questions and include one item on the correct "
                                "causative form."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ "
                                "items, each with prompt, options, correct_index, and explanation."
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
                        id="listen_dictation_causative",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="Hear causative have/get chunks",
                            generation_instructions=(
                                "Generate a 35-45 word audio script of 4 short sentences with varied "
                                "causative forms (had my phone fixed, got them to send it, is having the "
                                "report checked). The learner types each sentence exactly as heard."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_dictation'. Provide audio_script and 4 dictation "
                                "items, each with prompt, correct_answer, and explanation. Set "
                                "target_words to the passive chunks (for example 'is made', 'was sent', "
                                "'are delivered', 'will be repaired')."
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
                        id="write_sent_trans_causative",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Rewrite into causative have or get",
                            generation_instructions=(
                                "Give the learner 3 active sentences they did themselves and ask them to "
                                "rewrite each using causative have or get, keeping the same meaning."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 3 items, each with "
                                "source_sentence, sample_answer, and watch_hints (for example 'present -> "
                                "is/are + past participle', 'past -> was/were + past participle')."
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
                        id="speak_timed_causative",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe arranged services with causative forms",
                            generation_instructions=(
                                "Ask the learner to say one causative sentence per prompt about services "
                                "or tasks arranged for them, using have + object + past participle or get "
                                "+ object + to-infinitive."
                            ),
                            widget_requirements=(
                                "Create exactly 3 speaking prompts: one present passive about how "
                                "something is made, one past passive about something that was built or "
                                "sent, and one about something that will be done. Include "
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
                title="Reduced & Non-Defining Relative Clauses",
                description=(
                    "Learners add extra information with non-defining relative clauses "
                    "(commas + who/which) and shorten defining clauses by dropping the "
                    "pronoun or using a participle phrase (the report we sent, the woman "
                    "sitting near the door)."
                ),
                focus=(
                    "Non-defining relative clauses with commas and reduced defining "
                    "clauses (omitted pronoun, participle phrases)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach non-defining and reduced relative clauses.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce non-defining and reduced clauses.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that non-defining clauses "
                                "add extra information with commas, and reduced clauses shorten a "
                                "relative clause by dropping the pronoun or using -ing/-ed. Ask them to "
                                "describe a colleague using a short clause after the noun."
                            ),
                        ),
                        TeacherStep(
                            id="non_defining",
                            goal="Teach commas with extra information.",
                            instruction=(
                                "Confirm their sentence. Explain that non-defining clauses use commas and "
                                "who or which for extra detail (My manager, who lives nearby, ...). Ask "
                                "them to add a non-defining clause about a thing they use every day."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Confirm the pattern with a short example (The app, which I use daily, is "
                                "fast. The person sitting there is new.) and then ask only: Ready to try "
                                "the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_relative_reduced",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Match clause types to their punctuation or form",
                            generation_instructions=(
                                "Ask the learner to match each sentence stub to whether it needs commas "
                                "(non-defining), can drop the pronoun (reduced defining), or uses a "
                                "participle phrase."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options (the relative pronouns "
                                "who, which, that, where) and 3-4 items, each with prompt (a noun phrase "
                                "with a clue), correct_answer, and explanation."
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
                        id="listen_mcq_relative_reduced",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Hearing reduced and non-defining clauses",
                            generation_instructions=(
                                "Generate a 35-45 word description mixing one non-defining clause with "
                                "commas and at least one reduced clause. Include comprehension questions."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 2-3 MCQ items, each "
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
                        id="write_open_sent_relative_reduced",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_OPEN_SENT",
                            activity="write",
                            task_widget="open_text",
                            topic_override="Write sentences with reduced or non-defining clauses",
                            generation_instructions=(
                                "Ask for three short sentences: one non-defining with commas, one reduced "
                                "defining without the pronoun, and one with a participle phrase after the "
                                "noun."
                            ),
                            widget_requirements=(
                                "Target widget 'open_text'. Provide target_words (who, which, that, "
                                "where), common_mistakes, and 3 items, each with prompt, sample_answer, "
                                "and answer_hints."
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
                        id="speak_pic_desc_relative_reduced",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a scene with reduced relative clauses",
                            generation_instructions=(
                                "Ask the learner to describe a simple scene aloud using at least one "
                                "non-defining clause and one reduced clause."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing a busy cafe "
                                "with several people doing different things, grammar_rule, and "
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
                title="Reporting Verbs & Patterns - Admit, Deny, Suggest & More",
                description=(
                    "Learners report what people said using reporting verbs and the right "
                    "pattern after each verb (admit + -ing, suggest + clause, promise + "
                    "to-infinitive), not only said and told."
                ),
                focus=(
                    "Reporting verbs with correct patterns: admit/deny + -ing, suggest + "
                    "clause, promise/refuse + to-infinitive."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach reporting verbs and the patterns that follow them.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce reporting verbs.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that reporting verbs like "
                                "admit, deny, suggest, and promise change the grammar after them (He "
                                "admitted making a mistake, She promised to help). Ask them to tell you "
                                "something a colleague suggested recently."
                            ),
                        ),
                        TeacherStep(
                            id="verb_patterns",
                            goal="Teach verb + pattern combinations.",
                            instruction=(
                                "Confirm their sentence. Explain that admit and deny take -ing, suggest "
                                "often takes a that-clause, and promise takes to + verb. Ask them to "
                                "report one more idea using denied or promised with the correct pattern."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a reporting verb with the right pattern at least "
                                "once, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_cloze_reporting_verbs",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CLOZE",
                            activity="read",
                            task_widget="fill_blanks",
                            topic_override="Fill reporting verb pattern blanks",
                            generation_instructions=(
                                "Write a short 4-5 sentence passage reporting a meeting, with blanks for "
                                "reporting verbs and the correct form after each (admitted, suggested, "
                                "promised to, denied)."
                            ),
                            widget_requirements=(
                                "Target widget 'fill_blanks'. Provide passage_title and a passage with "
                                "___ markers only — no inline hints in parentheses after blanks. Provide "
                                "a BlankItem per blank with correct_answer and explanation. Omit "
                                "base_verb; these are reporting blanks, not verb inflection."
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
                        id="listen_infer_reporting_verbs",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Infer the reporting verb and pattern",
                            generation_instructions=(
                                "Generate a 35-45 word audio clip where someone reports what others said "
                                "using varied reporting verbs and patterns. Ask the learner to infer the "
                                "original meaning and verb choice."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_infer'. Provide audio_script, intent_focus, and 2 "
                                "MCQ items, each with prompt, options, correct_index, and explanation."
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
                        id="write_para_reporting_verbs",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write a paragraph with varied reporting verbs",
                            generation_instructions=(
                                "Ask the learner to write a 3-4 sentence paragraph reporting a short "
                                "discussion using at least three different reporting verbs with correct "
                                "patterns after each."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, grammar_rule, "
                                "target_words (said that, told me, asked if, would), minimum_words 25, "
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
                        id="speak_roleplay_reporting_verbs",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Pass on a message with reporting verbs",
                            generation_instructions=(
                                "Set up a roleplay where the learner passes on what several people said "
                                "using reporting verbs (she suggested that, he promised to, they denied) "
                                "in 2-3 connected sentences."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_roleplay'. Provide dialogue_context with "
                                "alternating partner and learner turns (4-6 turns total). Partner lines "
                                "set the scene in 2-3 sentences; each learner line is 2-3 connected "
                                "sentences (roughly 15-30 words). Include target_words (said that, told "
                                "me, asked if, would), speaking_prompts with one instruction to respond "
                                "aloud, sample_responses with the learner's model answer (same text as "
                                "the learner dialogue turn), grammar_rule_to_practice, and "
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
                title="Wish & Regret - I Wish, If Only & Should Have",
                description=(
                    "Learners express wishes about the present or past and regrets with I "
                    "wish / If only + past simple or past perfect, and should have + past "
                    "participle for things they regret not doing."
                ),
                focus=(
                    "Wish and regret: I wish/If only + past for present regrets; past "
                    "perfect for past regrets; should have for advice regrets."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach wish, if only, and should have for regrets.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce wish and regret forms.",
                            instruction=(
                                "Greet the learner and note this is the regrets day of grammar week. "
                                "Explain in two sentences that I wish plus past simple talks about "
                                "present regrets, and should have plus past participle regrets past "
                                "actions not taken. Ask what they wish were different about their "
                                "routine."
                            ),
                        ),
                        TeacherStep(
                            id="wish_should_have",
                            goal="Teach wish vs should have.",
                            instruction=(
                                "Confirm their answer. Explain that I wish I had... looks back and should "
                                "have shows a past action they regret not doing. Ask them to say one "
                                "should have sentence about a small mistake last month."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used the pattern at least once, ask only: Ready to "
                                "try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_wish_regret",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="Wishes and regrets in text",
                            generation_instructions=(
                                "Write a short profile rich in I wish, If only, and should have sentences "
                                "about present and past regrets. Then give True / False / Not Given "
                                "statements about what the person wishes or regrets."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tfng'. Provide passage_title, passage, and 5 items, "
                                "each with prompt, correct_answer (True, False, or Not Given), and "
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
                        id="listen_shadow_wish_regret",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Repeat wish / should have phrases in speech",
                            generation_instructions=(
                                "Generate a short natural monologue (about 20 seconds) with I wish and "
                                "should have phrases blended into connected speech for shadowing."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_shadow'. Provide audio_script, text_to_shadow "
                                "(identical to the script), target_words highlighting the used to / would "
                                "chunks, and grammar_rule."
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
                        id="write_email_wish_regret",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Email a friend about a wish or regret",
                            generation_instructions=(
                                "Ask the learner to write a short email to a friend expressing one wish "
                                "and one regret using I wish and should have correctly."
                            ),
                            widget_requirements=(
                                "Target widget 'write_email'. Provide prompt, grammar_rule, target_words "
                                "(used to, would, no longer, back then), minimum_words 25, sample_answer "
                                "(with To and Subject lines), and answer_hints."
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
                        id="speak_smalltalk_wish_regret",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Casual chat about wishes and regrets",
                            generation_instructions=(
                                "Set up casual small talk where the learner answers with I wish and "
                                "should have naturally."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_smalltalk'. Provide a dialogue_context alternating "
                                "partner and learner turns, target_words (used to, would, as a child, "
                                "back then), and speaking_duration_seconds: 30."
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
                title="Formal Linkers & Nuance - Moreover, Nevertheless & In Addition",
                description=(
                    "Learners connect ideas in more formal writing and speech with "
                    "linkers such as moreover, nevertheless, in addition, and on the "
                    "other hand, choosing the linker that matches the relationship."
                ),
                focus=(
                    "Formal linkers moreover, nevertheless, in addition, and on the other "
                    "hand for reason, contrast, and addition."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach formal linkers for nuanced connections between ideas.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce formal linkers.",
                            instruction=(
                                "Greet the learner and note this is the final wrap-up day of grammar "
                                "week. Explain in two sentences that formal linkers like moreover and "
                                "nevertheless show addition or contrast in essays and reports. Ask them "
                                "to finish 'Nevertheless, ___.'"
                            ),
                        ),
                        TeacherStep(
                            id="addition_contrast",
                            goal="Teach moreover vs nevertheless.",
                            instruction=(
                                "Confirm their sentence. Explain that moreover and in addition add a "
                                "point, while nevertheless and on the other hand show contrast. Ask them "
                                "to make one sentence with moreover linking two ideas."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a formal linker correctly at least once, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_context_mcq_formal_linkers",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Formal linkers in a short article",
                            generation_instructions=(
                                "Write a short formal paragraph (policy or report style) using moreover, "
                                "nevertheless, and in addition. Then ask MCQ questions about which linker "
                                "fits a gap."
                            ),
                            widget_requirements=(
                                "Target widget 'read_context_mcq'. Provide passage_title, passage, and 4 "
                                "MCQ items, each with prompt, options (despite, in spite of, whereas, "
                                "however), correct_index, and explanation."
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
                        id="listen_retell_formal_linkers",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Retell a formal mini-talk",
                            generation_instructions=(
                                "Generate a 40-50 word formal audio clip with clear linker phrases. Ask "
                                "the learner to retell the main points using at least two formal linkers."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_retell'. Provide: audio_script (the full spoken "
                                "monologue text), passage_to_retell (a 2-3 sentence model retell — "
                                "shorter than the audio, showing how a good student would summarise the "
                                "key points using contrast linkers), sample_responses (list containing "
                                "that same model retell), target_words (list of the key contrast linkers "
                                "from the audio), and grammar_rule."
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
                        id="write_paraphrase_formal_linkers",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="Paraphrase with formal linkers",
                            generation_instructions=(
                                "Give informal sentences and ask the learner to join or rewrite them "
                                "using moreover, nevertheless, or on the other hand."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paraphrase'. Provide 3 items, each with "
                                "incorrect_sentence (the contrasting sentence pair), sample_answer, and "
                                "watch_hints (the target contrast linker)."
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
                        id="speak_present_formal_linkers",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Short talk using formal linkers",
                            generation_instructions=(
                                "Ask the learner to give a 45-second mini presentation on a work or study "
                                "topic using at least two formal linkers naturally."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_present'. Provide: prompts as a list with one "
                                "general question asking the learner to compare two choices and say which "
                                "they prefer using contrast linkers (e.g. 'Compare living in a city and "
                                "the countryside, and say which you prefer.'); visual_prompt_description "
                                "as a short sample spoken answer that uses at least three contrast "
                                "linkers (e.g. 'A city is exciting, whereas the countryside is calm. "
                                "Despite the noise, I prefer the city. However, I visit the countryside "
                                "often, so I get both.'); grammar_rule, target_words, and "
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
        ),
    ),
    WeekSource(
        week_number=6,
        theme_type="communication",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=(
            DaySource(
                title="Conflict Resolution & Middle Ground",
                description=(
                    "Learners resolve disagreements by acknowledging both sides, "
                    "proposing middle-ground options, and confirming what both people can "
                    "accept (I understand your point / Could we try...?)."
                ),
                focus=(
                    "Resolve conflict: acknowledge both sides, propose middle-ground "
                    "options, and confirm shared agreement."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach conflict resolution and finding middle ground.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce conflict resolution.",
                            instruction=(
                                "Welcome the learner to communication week. Explain in two sentences that "
                                "resolving conflict means acknowledging both views and finding a middle "
                                "ground both can accept. Ask them to describe one disagreement they "
                                "handled or want to handle better."
                            ),
                        ),
                        TeacherStep(
                            id="middle_ground",
                            goal="Teach middle-ground phrases.",
                            instruction=(
                                "React warmly. Explain phrases like 'I see your point' and 'Could we meet "
                                "in the middle by...?' Ask them to suggest one compromise for the "
                                "situation they named."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has acknowledged a view and offered a compromise, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_conflict_resolution",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Conflict resolution in messages",
                            generation_instructions=(
                                "Write a short exchange where two people disagree, acknowledge each "
                                "other's points, and agree on middle-ground next steps. Ask comprehension "
                                "questions."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 3 MCQ "
                                "items, each with prompt, options, correct_index, and explanation."
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
                        id="listen_mcq_conflict_resolution",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Listening to a disagreement resolved",
                            generation_instructions=(
                                "Generate a 35-45 word dialogue resolving a conflict with acknowledgement "
                                "and a compromise. Include MCQs on each side's concern and the agreement."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each "
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
                        id="write_sent_trans_conflict_resolution",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Polite conflict-resolution phrases",
                            generation_instructions=(
                                "Give 3 blunt conflicting statements and ask the learner to rewrite each "
                                "using acknowledgement and middle-ground phrases."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 3 items, each with "
                                "source_sentence, sample_answer, and watch_hints."
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
                        id="speak_roleplay_conflict_resolution",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Roleplay resolving a conflict",
                            generation_instructions=(
                                "Set up a roleplay where the learner de-escalates a disagreement and "
                                "proposes a compromise both sides can accept."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_roleplay'. Provide a dialogue_context alternating "
                                "partner and learner turns, target_words (How about, meet halfway, that "
                                "works, agreed), and speaking_duration_seconds: 30."
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
                title="Giving Constructive Feedback",
                description=(
                    "Learners give constructive feedback using a clear structure: "
                    "positive point, specific issue, suggestion, and supportive close (I "
                    "liked... / One thing to improve... / You could try...)."
                ),
                focus=(
                    "Give constructive feedback with positive point, specific issue, "
                    "suggestion, and supportive tone."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach giving constructive feedback in a supportive structure.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce constructive feedback.",
                            instruction=(
                                "Welcome the learner to Day 2 of communication week. Explain in two "
                                "sentences that constructive feedback balances praise with one clear "
                                "suggestion. Ask them to tell you about feedback they found helpful."
                            ),
                        ),
                        TeacherStep(
                            id="feedback_structure",
                            goal="Teach the feedback structure.",
                            instruction=(
                                "Use their example to model 'I liked... / One area to develop is... / You "
                                "could try...'. Ask them to give brief constructive feedback on a sample: "
                                "'A teammate submitted a report late.'"
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has praised and suggested an improvement, ask only: Ready "
                                "to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_constructive_feedback",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="Constructive feedback in writing",
                            generation_instructions=(
                                "Write a short message giving constructive feedback on work quality with "
                                "a positive line, one issue, and a suggestion. Then True/False/Not Given "
                                "items."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tfng'. Provide passage_title, passage, and 4 items, "
                                "each with prompt, correct_answer (True, False, or Not Given), and "
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
                        id="listen_infer_constructive_feedback",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Infer tone in feedback conversations",
                            generation_instructions=(
                                "Generate a conversation where a manager gives constructive feedback. Ask "
                                "the learner to infer tone and the main suggestion."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_infer'. Provide audio_script, intent_focus, and 4 "
                                "MCQ items, each with prompt, options, correct_index, and explanation."
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
                        id="write_email_constructive_feedback",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Write constructive feedback",
                            generation_instructions=(
                                "Ask the learner to write feedback to a colleague with praise, one issue, "
                                "and a concrete suggestion."
                            ),
                            widget_requirements=(
                                "Target widget 'write_email'. Provide prompt, grammar_rule, target_words, "
                                "minimum_words 25, sample_answer (with To and Subject lines), and "
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
                        id="speak_interview_constructive_feedback",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_INTERVIEW",
                            activity="speak",
                            task_widget="speak_interview",
                            topic_override="React with constructive feedback in chat",
                            generation_instructions=(
                                "Run a mini interview where the learner gives constructive feedback on "
                                "three short scenarios in full sentences."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_interview'. Provide interview_context, "
                                "grammar_rule, target_words (That's wonderful, Oh no, How did, What "
                                "about), 3 questions each with interviewer_prompt, sample_answer, and "
                                "answer_hint, and speaking_duration_seconds: 35."
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
                title="Pros, Cons & Recommending an Option",
                description=(
                    "Learners compare options by listing pros and cons, weighing "
                    "trade-offs, and recommending one choice with clear reasons."
                ),
                focus=(
                    "Compare options with pros and cons, weigh trade-offs, and recommend "
                    "one choice with reasons."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach weighing pros and cons and recommending an option.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce pros, cons, and recommendations.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that comparing options means "
                                "listing pros and cons and then recommending the best choice with "
                                "reasons. Ask them to compare two tools or places they know."
                            ),
                        ),
                        TeacherStep(
                            id="structure_order",
                            goal="Teach listing and recommending.",
                            instruction=(
                                "Confirm their answer. Introduce signposting (on the one hand, however, "
                                "overall I would recommend) and ask them to name one pro and one con."
                            ),
                        ),
                        TeacherStep(
                            id="add_recommendation",
                            goal="Add a clear recommendation.",
                            instruction=(
                                "Show how to end with a recommendation and reason (Overall, I would "
                                "choose X because...). Ask what they would recommend and why in one "
                                "sentence."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has listed a pro/con and a recommendation, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_structure_pros_cons",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_STRUCTURE_ID",
                            activity="read",
                            task_widget="read_structure",
                            topic_override="Identify pros, cons, and recommendation sections",
                            generation_instructions=(
                                "Provide a 3-paragraph text comparing two options and ask the learner to "
                                "label paragraphs as Pros, Cons, or Recommendation."
                            ),
                            widget_requirements=(
                                "Target widget 'read_structure'. Provide passage_title, structure_labels "
                                "['Situation', 'Problem', 'Solution'], and 3 items, each with paragraph, "
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
                        id="listen_retell_pros_cons",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Retell an options comparison",
                            generation_instructions=(
                                "Generate a short audio comparing two options with pros, cons, and a "
                                "final recommendation. Ask the learner to retell the recommendation and "
                                "main reason."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_retell'. Provide audio_script, passage_to_retell, "
                                "target_words (the situation was, the problem, so, as a result), and "
                                "grammar_rule."
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
                        id="write_para_pros_cons",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write a pros-cons recommendation paragraph",
                            generation_instructions=(
                                "Ask the learner to write a paragraph comparing two options and "
                                "recommending one with reasons."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, grammar_rule, "
                                "target_words (first, the problem was, so, as a result, because), "
                                "minimum_words 45, sample_answer, and answer_hints."
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
                        id="speak_opinion_pros_cons",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_OPINION",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="State a recommendation aloud",
                            generation_instructions=(
                                "Ask the learner to speak for 45 seconds recommending one option with "
                                "pros, cons, and a clear conclusion."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_present'. Provide grammar_rule, target_words (I "
                                "would suggest, because, the best way, however), a "
                                "visual_prompt_description or prompt for the recommendation, and "
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
                title="Leading a Short Meeting",
                description=(
                    "Learners lead a brief meeting: open with purpose, guide agenda "
                    "items, invite input, and close with actions and owners (Let's start "
                    "with... / Any questions on...? / Next steps are...)."
                ),
                focus=(
                    "Lead a short meeting: purpose, agenda, invitations to speak, and "
                    "action-focused close."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach leading a short meeting with clear structure.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce leading a meeting.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that leading a short meeting "
                                "means stating the purpose, moving through points, and ending with clear "
                                "actions. Ask them to describe a meeting they led or joined recently."
                            ),
                        ),
                        TeacherStep(
                            id="agenda_actions",
                            goal="Teach open and close phrases.",
                            instruction=(
                                "Confirm their answer. Introduce phrases like 'Let's kick off with...' "
                                "and 'The action items are...'. Ask them to open a one-minute project "
                                "check-in."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used an opening or action phrase, ask only: Ready to "
                                "try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_leading_meeting",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Leading a meeting in writing",
                            generation_instructions=(
                                "Write a short meeting transcript with purpose, two agenda items, and "
                                "action owners. Ask comprehension questions."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 3 MCQ "
                                "items, each with prompt, options, correct_index, and explanation."
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
                        id="listen_mcq_leading_meeting",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Listening to a short meeting",
                            generation_instructions=(
                                "Generate a 35-45 word meeting clip with opening, two points, and closing "
                                "actions. Include MCQs on purpose and next steps."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each "
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
                        id="write_bullets_to_para_leading_meeting",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_BULLETS_TO_PARA",
                            activity="write",
                            task_widget="write_bullets_to_para",
                            topic_override="Turn notes into a meeting summary",
                            generation_instructions=(
                                "Give bullet notes from a meeting and ask the learner to write a clear "
                                "summary paragraph with action items."
                            ),
                            widget_requirements=(
                                "Target widget 'write_bullets_to_para'. Provide bullets (4 work items), "
                                "prompt, grammar_rule, target_words, minimum_words 25, sample_answer, and "
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
                        id="speak_roleplay_leading_meeting",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Roleplay leading a meeting",
                            generation_instructions=(
                                "Set up a roleplay where the learner opens a short meeting, invites one "
                                "comment, and closes with next steps."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_roleplay'. Provide a dialogue_context alternating "
                                "partner and learner turns, target_words (so far, on track, by Friday, "
                                "next step), and speaking_duration_seconds: 30."
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
                title="Handling Objections",
                description=(
                    "Learners respond to objections calmly: acknowledge the concern, "
                    "clarify, respond with evidence or benefit, and check agreement (I "
                    "understand why... / That's a fair point / What would help is...)."
                ),
                focus=(
                    "Handle objections by acknowledging, clarifying, responding with "
                    "evidence, and checking agreement."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach handling objections professionally.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce handling objections.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that handling objections "
                                "starts by acknowledging the concern before giving a reasoned response. "
                                "Ask them to recall an objection they heard at work or school."
                            ),
                        ),
                        TeacherStep(
                            id="respond_objection",
                            goal="Teach acknowledge-then-respond.",
                            instruction=(
                                "Model 'That's a fair point' plus a reason or benefit. Ask them to "
                                "respond to: 'It sounds too expensive.'"
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has acknowledged and responded to an objection, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_handling_objections",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="Objection handling in text",
                            generation_instructions=(
                                "Write a short sales or project update with two objections and calm "
                                "responses. Then True/False/Not Given items."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tfng'. Provide passage_title, passage, and 4 items, "
                                "each with prompt, correct_answer (True, False, or Not Given), and "
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
                        id="listen_infer_handling_objections",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Infer concerns behind objections",
                            generation_instructions=(
                                "Generate a dialogue with two objections and nuanced responses. Ask "
                                "inference questions about concerns and agreement."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_infer'. Provide audio_script, intent_focus, and 4 "
                                "MCQ items, each with prompt, options, correct_index, and explanation."
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
                        id="write_idea_para_handling_objections",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_IDEA_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write a response to objections",
                            generation_instructions=(
                                "Ask the learner to write a paragraph responding to two objections about "
                                "an idea."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, grammar_rule, "
                                "target_words (I believe, because, for example, admittedly), "
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
                        id="speak_pic_desc_handling_objections",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Explain handling an objection aloud",
                            generation_instructions=(
                                "Ask the learner to describe aloud how they would handle an objection to "
                                "a proposal, using acknowledge-then-respond language."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing a busy car "
                                "park beside an empty bus lane, grammar_rule, and "
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
                title="Stakeholder Communication",
                description=(
                    "Learners tailor messages for different stakeholders: adjust detail, "
                    "tone, and focus (executive summary vs team detail) while keeping the "
                    "core message consistent."
                ),
                focus=(
                    "Stakeholder communication: adjust detail, tone, and focus for "
                    "different audiences while keeping core facts."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach stakeholder-aware communication.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce stakeholder communication.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that stakeholders need "
                                "different levels of detail and tone — leaders want outcomes, teams want "
                                "steps. Ask which audience is harder for them to write for."
                            ),
                        ),
                        TeacherStep(
                            id="tone_detail",
                            goal="Teach tailoring tone and detail.",
                            instruction=(
                                "Confirm their answer. Contrast a one-line executive update with a fuller "
                                "team message. Ask them to give one headline for a leader and one detail "
                                "for a teammate."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has tailored tone or detail for two audiences, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tone_id_stakeholder_w14",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Identify stakeholder-appropriate tone",
                            generation_instructions=(
                                "Provide two short messages on the same update for different "
                                "stakeholders. Ask which is for a senior leader vs a project team."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tone_id'. Provide passage_title and 2 items, each "
                                "with sender, message, prompt, options (Professional, Casual), "
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
                        id="listen_tone_stakeholder_w14",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Hear tone shifts for stakeholders",
                            generation_instructions=(
                                "Generate audio with two versions of the same news for different "
                                "audiences. Ask tone and detail questions."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_tone'. Provide audio_script and at least 1 MCQ "
                                "item with prompt, options (Professional, Casual), correct_index, and "
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
                        id="write_paraphrase_stakeholder_w14",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="Rewrite for a different stakeholder",
                            generation_instructions=(
                                "Give a detailed team update and ask the learner to rewrite a 2-sentence "
                                "executive version."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paraphrase'. Provide 2 items, each with "
                                "incorrect_sentence (the message to convert), sample_answer, and "
                                "watch_hints."
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
                        id="speak_smalltalk_stakeholder_w14",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Small talk with stakeholder-aware replies",
                            generation_instructions=(
                                "Set up small talk where the learner answers the same news differently "
                                "for a manager vs a peer."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_smalltalk'. Provide a dialogue_context alternating "
                                "partner and learner turns, target_words (That sounds great, I might, "
                                "probably, weekend), and speaking_duration_seconds: 35."
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
                title="Facilitating Discussion",
                description=(
                    "Learners facilitate discussion: set topic, invite quieter voices, "
                    "paraphrase contributions, and summarise before deciding (Let's hear "
                    "from... / So what I'm hearing is... / To sum up...)."
                ),
                focus=(
                    "Facilitate discussion: set topic, invite voices, paraphrase, and "
                    "summarise before a decision."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach facilitating group discussion.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce facilitating discussion.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that facilitating means "
                                "guiding the topic, inviting others, and summarising before deciding. Ask "
                                "when they last joined a group discussion they could have guided more."
                            ),
                        ),
                        TeacherStep(
                            id="invite_summarise",
                            goal="Teach invite and summarise phrases.",
                            instruction=(
                                "Introduce 'Let's hear from...' and 'So what I'm hearing is...'. Ask them "
                                "to invite a quiet member and summarise two ideas in one sentence."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has invited or summarised, ask only: Ready to try the "
                                "practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_structure_facilitating",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_STRUCTURE_ID",
                            activity="read",
                            task_widget="read_structure",
                            topic_override="Structure of a facilitated discussion",
                            generation_instructions=(
                                "Provide a 3-part facilitated discussion transcript (open, contributions, "
                                "summary) and ask the learner to label each part."
                            ),
                            widget_requirements=(
                                "Target widget 'read_structure'. Provide passage_title, structure_labels "
                                "['Opening', 'Building', 'Closing'], and 3 items, each with label, "
                                "paragraph, correct_answer, and explanation."
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
                        id="listen_retell_facilitating",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Retell a facilitated discussion clip",
                            generation_instructions=(
                                "Generate audio of someone facilitating a short discussion. Ask retell of "
                                "invitations and summary."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_retell'. Set response_mode to 'written'. Provide "
                                "audio_script, passage_to_retell, target_words, and grammar_rule."
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
                        id="write_email_facilitating",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Email summarising a discussion",
                            generation_instructions=(
                                "Ask the learner to write an email summarising a discussion with next "
                                "steps."
                            ),
                            widget_requirements=(
                                "Target widget 'write_email'. Provide prompt, grammar_rule, target_words, "
                                "minimum_words 45, sample_answer (with To and Subject lines), and "
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
                        id="speak_present_facilitating",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Present a short facilitated summary",
                            generation_instructions=(
                                "Ask the learner to deliver a 45-second spoken summary after a "
                                "facilitated discussion scenario."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_present'. Provide grammar_rule, target_words (we "
                                "discussed, on one hand, on the other hand, in the end), a "
                                "visual_prompt_description, an optional model_presentation, and "
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
        ),
    ),
    WeekSource(
        week_number=7,
        theme_type="vocabulary",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=(
            DaySource(
                title="Science & Research - Hypothesis, Data & Experiment",
                description=(
                    "Learners build vocabulary for science and research (hypothesis, "
                    "experiment, data, evidence, peer review) and use the words in "
                    "reading, listening, writing, and speaking tasks at B1+ level."
                ),
                focus=(
                    "Vocabulary for science and research (hypothesis, experiment, data, "
                    "evidence, peer review)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach science and research vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce science and research words.",
                            instruction=(
                                "Welcome the learner to vocabulary week. Explain in two sentences that we "
                                "use words like hypothesis and experiment to talk about science and "
                                "research. Ask them to use one of today's words in a sentence."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more science and research words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about science "
                                "and research."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a target word correctly, ask only: Ready to try "
                                "the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_science_research",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Science & Research Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match science and research words (hypothesis, data, "
                                "evidence) to short definitions or context clues."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options (the environment words) "
                                "and 4 items, each with prompt (the definition), correct_answer, and "
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
                        id="listen_mcq_science_research",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="A talk about science and research",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses science and research, "
                                "using at least three target words. Ask comprehension questions."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each "
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
                        id="write_sent_trans_science_research",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="science and research vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of science and research ideas and ask the "
                                "learner to rewrite each using precise vocabulary (hypothesis, data, "
                                "evidence)."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 2-3 items, each with "
                                "source_sentence, sample_answer, and watch_hints."
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
                        id="speak_pic_desc_science_research",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a lab or research setting",
                            generation_instructions=(
                                "Ask the learner to describe a photo of research lab with scientists "
                                "reviewing data on screens aloud using science and research vocabulary "
                                "naturally."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing a wind farm "
                                "beside a smoggy city skyline, grammar_rule, and "
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
                title="Arts & Creativity - Exhibition, Medium & Inspiration",
                description=(
                    "Learners build vocabulary for arts and creativity (exhibition, "
                    "medium, inspiration, curator, portfolio) and use the words in "
                    "reading, listening, writing, and speaking tasks at B1+ level."
                ),
                focus=(
                    "Vocabulary for arts and creativity (exhibition, medium, inspiration, "
                    "curator, portfolio)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach arts and creativity vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce arts and creativity words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that arts and creativity "
                                "vocabulary includes exhibition, medium, inspiration, curator, portfolio. "
                                "Ask them what they have read or heard recently about arts and "
                                "creativity."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more arts and creativity words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about arts and "
                                "creativity."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a target word correctly, ask only: Ready to try "
                                "the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_context_mcq_arts_creativity",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Arts & Creativity Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match arts and creativity words (exhibition, medium, "
                                "inspiration) to short definitions or context clues."
                            ),
                            widget_requirements=(
                                "Target widget 'read_context_mcq'. Provide passage_title, passage, and at "
                                "least 1 MCQ item with prompt, options, correct_index, and explanation."
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
                        id="listen_dictation_arts_creativity",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="A talk about arts and creativity",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses arts and creativity, "
                                "using at least three target words. Ask comprehension questions."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_dictation'. Provide audio_script, target_words "
                                "(the key education words), and 1 dictation item with prompt, "
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
                        id="write_word_upgrade_arts_creativity",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_WORD_UPGRADE",
                            activity="write",
                            task_widget="write_word_upgrade",
                            topic_override="arts and creativity vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of arts and creativity ideas and ask the learner "
                                "to rewrite each using precise vocabulary (exhibition, medium, "
                                "inspiration)."
                            ),
                            widget_requirements=(
                                "Target widget 'write_word_upgrade'. Provide 3 items, each with "
                                "source_sentence, target_upgrade_word, sample_answer, and watch_hints."
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
                        id="speak_timed_arts_creativity",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe a gallery or studio",
                            generation_instructions=(
                                "Ask the learner to describe a photo of art gallery with paintings and a "
                                "sculptor at work aloud using arts and creativity vocabulary naturally."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a sample_response, "
                                "grammar_rule, target_words (enrol, assignment, revise, qualification), "
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
            DaySource(
                title="Ethics & Global Issues - Justice, Rights & Responsibility",
                description=(
                    "Learners build vocabulary for ethics and global issues (justice, "
                    "rights, inequality, responsibility, campaign) and use the words in "
                    "reading, listening, writing, and speaking tasks at B1+ level."
                ),
                focus=(
                    "Vocabulary for ethics and global issues (justice, rights, "
                    "inequality, responsibility, campaign)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach ethics and global issues vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce ethics and global issues words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that ethics and global "
                                "issues vocabulary includes justice, rights, inequality, responsibility, "
                                "campaign. Ask them what they have read or heard recently about ethics "
                                "and global issues."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more ethics and global issues words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about ethics and "
                                "global issues."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a target word correctly, ask only: Ready to try "
                                "the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_ethics_global",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Ethics & Global Issues Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match ethics and global issues words (justice, "
                                "rights, responsibility) to short definitions or context clues."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options (the culture words) and "
                                "4 items, each with prompt (the definition), correct_answer, and "
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
                        id="listen_mcq_ethics_global",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="A talk about ethics and global issues",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses ethics and global "
                                "issues, using at least three target words. Ask comprehension questions."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each "
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
                        id="write_para_ethics_global",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="ethics and global issues vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of ethics and global issues ideas and ask the "
                                "learner to rewrite each using precise vocabulary (justice, rights, "
                                "responsibility)."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, grammar_rule, "
                                "target_words (tradition, community, heritage, celebrate), minimum_words "
                                "20, sample_answer, and answer_hints."
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
                        id="speak_pic_desc_ethics_global",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a community or policy context",
                            generation_instructions=(
                                "Ask the learner to describe a photo of community meeting about a social "
                                "campaign poster aloud using ethics and global issues vocabulary "
                                "naturally."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing a street "
                                "festival with people in traditional dress, grammar_rule, and "
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
                title="Business & Economics - Revenue, Market & Investment",
                description=(
                    "Learners build vocabulary for business and economics (revenue, "
                    "market, investment, budget, profit) and use the words in reading, "
                    "listening, writing, and speaking tasks at B1+ level."
                ),
                focus=(
                    "Vocabulary for business and economics (revenue, market, investment, "
                    "budget, profit)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach business and economics vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce business and economics words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that business and economics "
                                "vocabulary includes revenue, market, investment, budget, profit. Ask "
                                "them what they have read or heard recently about business and economics."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more business and economics words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about business "
                                "and economics."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a target word correctly, ask only: Ready to try "
                                "the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_context_mcq_business_economics",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Business & Economics Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match business and economics words (revenue, market, "
                                "investment) to short definitions or context clues."
                            ),
                            widget_requirements=(
                                "Target widget 'read_context_mcq'. Provide passage_title, passage, and at "
                                "least 1 MCQ item with prompt, options, correct_index, and explanation."
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
                        id="listen_dictation_business_economics",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="A talk about business and economics",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses business and "
                                "economics, using at least three target words. Ask comprehension "
                                "questions."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_dictation'. Provide audio_script, target_words "
                                "(the key work words), and 1 dictation item with prompt, correct_answer, "
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
                        id="write_paraphrase_business_economics",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="business and economics vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of business and economics ideas and ask the "
                                "learner to rewrite each using precise vocabulary (revenue, market, "
                                "investment)."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paraphrase'. Provide 2 items, each with "
                                "incorrect_sentence (the plain sentence), sample_answer, and watch_hints."
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
                        id="speak_timed_business_economics",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe a business or market scene",
                            generation_instructions=(
                                "Ask the learner to describe a photo of office dashboard showing market "
                                "trends and budget charts aloud using business and economics vocabulary "
                                "naturally."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a sample_response, "
                                "grammar_rule, target_words (promote, resign, collaborate, deadline), and "
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
                title="Media Literacy - Source, Bias & Fact-check",
                description=(
                    "Learners build vocabulary for media literacy (source, bias, "
                    "fact-check, headline, credible) and use the words in reading, "
                    "listening, writing, and speaking tasks at B1+ level."
                ),
                focus="Vocabulary for media literacy (source, bias, fact-check, headline, credible).",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach media literacy vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce media literacy words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that media literacy "
                                "vocabulary includes source, bias, fact-check, headline, credible. Ask "
                                "them what they have read or heard recently about media literacy."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more media literacy words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about media "
                                "literacy."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a target word correctly, ask only: Ready to try "
                                "the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_media_literacy",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Media Literacy Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match media literacy words (source, bias, credible) "
                                "to short definitions or context clues."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options (the news words) and 4 "
                                "items, each with prompt (the meaning), correct_answer, and explanation."
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
                        id="listen_mcq_media_literacy",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="A talk about media literacy",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses media literacy, using "
                                "at least three target words. Ask comprehension questions."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each "
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
                        id="write_sent_trans_media_literacy",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="media literacy vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of media literacy ideas and ask the learner to "
                                "rewrite each using precise vocabulary (source, bias, credible)."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 3 items, each with "
                                "source_sentence, sample_answer, and watch_hints."
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
                        id="speak_pic_desc_media_literacy",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe news and online media",
                            generation_instructions=(
                                "Ask the learner to describe a photo of person comparing two news "
                                "headlines on a laptop aloud using media literacy vocabulary naturally."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing a news "
                                "studio with a reporter and a headline on the screen, grammar_rule, and "
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
                title="Leadership & Influence - Vision, Delegate & Motivate",
                description=(
                    "Learners build vocabulary for leadership and influence (vision, "
                    "delegate, motivate, stakeholder, initiative) and use the words in "
                    "reading, listening, writing, and speaking tasks at B1+ level."
                ),
                focus=(
                    "Vocabulary for leadership and influence (vision, delegate, motivate, "
                    "stakeholder, initiative)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach leadership and influence vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce leadership and influence words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that leadership and "
                                "influence vocabulary includes vision, delegate, motivate, stakeholder, "
                                "initiative. Ask them what they have read or heard recently about "
                                "leadership and influence."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more leadership and influence words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about leadership "
                                "and influence."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a target word correctly, ask only: Ready to try "
                                "the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_context_mcq_leadership_influence",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Leadership & Influence Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match leadership and influence words (vision, "
                                "delegate, motivate) to short definitions or context clues."
                            ),
                            widget_requirements=(
                                "Target widget 'read_context_mcq'. Provide passage_title, passage, and 3 "
                                "MCQ items, each with prompt, options, correct_index, and explanation."
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
                        id="listen_dictation_leadership_influence",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="A talk about leadership and influence",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses leadership and "
                                "influence, using at least three target words. Ask comprehension "
                                "questions."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_dictation'. Provide audio_script, target_words "
                                "(the quality words), and 2 dictation items, each with a prompt sentence "
                                "containing a blank, correct_answer, and explanation."
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
                        id="write_word_upgrade_leadership_influence",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_WORD_UPGRADE",
                            activity="write",
                            task_widget="write_word_upgrade",
                            topic_override="leadership and influence vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of leadership and influence ideas and ask the "
                                "learner to rewrite each using precise vocabulary (vision, delegate, "
                                "motivate)."
                            ),
                            widget_requirements=(
                                "Target widget 'write_word_upgrade'. Provide 3 items, each with "
                                "source_sentence, target_upgrade_word, sample_answer, and watch_hints."
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
                        id="speak_timed_leadership_influence",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe a team leadership moment",
                            generation_instructions=(
                                "Ask the learner to describe a photo of team leader motivating colleagues "
                                "around a shared goal board aloud using leadership and influence "
                                "vocabulary naturally."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a sample_response, "
                                "grammar_rule, target_words (integrity, resilience, perspective, empathy, "
                                "ambition), and speaking_duration_seconds: 45."
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
                    "Learners build vocabulary for the week's B1+ vocabulary across "
                    "science, arts, ethics, business, media, and leadership and use the "
                    "words in reading, listening, writing, and speaking tasks at B1+ "
                    "level."
                ),
                focus=(
                    "Vocabulary for the week's B1+ vocabulary across science, arts, "
                    "ethics, business, media, and leadership."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach review and word building vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce review and word building words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that review and word "
                                "building vocabulary includes review words from the week. Ask them what "
                                "they have read or heard recently about review and word building."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more review and word building words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about review and "
                                "word building."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a target word correctly, ask only: Ready to try "
                                "the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_review_w15",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Review & Word Building Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match review and word building words (review, prefix, "
                                "suffix) to short definitions or context clues."
                            ),
                            widget_requirements=(
                                "Target widget 'read_word_match'. Provide options (the 6 words) and 6 "
                                "items, each with prompt (the definition), correct_answer, and "
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
                        id="listen_mcq_review_w15",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="A talk about review and word building",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses review and word "
                                "building, using at least three target words. Ask comprehension "
                                "questions."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each "
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
                        id="write_para_review_w15",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="review and word building vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of review and word building ideas and ask the "
                                "learner to rewrite each using precise vocabulary (review, prefix, "
                                "suffix)."
                            ),
                            widget_requirements=(
                                "Target widget 'write_paragraph'. Provide prompt, grammar_rule, "
                                "target_words (the week's words), minimum_words 25, sample_answer, and "
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
                        id="speak_timed_review_w15",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe mixed professional contexts",
                            generation_instructions=(
                                "Ask the learner to describe a photo of collage of work, lab, gallery, "
                                "and news scenes aloud using review and word building vocabulary "
                                "naturally."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a sample_response, "
                                "grammar_rule, target_words (the week's words), and "
                                "speaking_duration_seconds: 90."
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
        week_number=8,
        theme_type="confidence",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=(
            DaySource(
                title="Facilitating Difficult Conversations",
                description=(
                    "Learners build confidence to facilitate difficult conversations "
                    "calmly: set ground rules, name the issue, and invite respectful "
                    "turns, using the same read-listen-write-speak sequence as earlier "
                    "confidence days at B1+ level."
                ),
                focus=(
                    "Facilitate difficult conversations calmly: set ground rules, name "
                    "the issue, and invite respectful turns."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to facilitate difficult conversations calmly.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week. Explain in two sentences that "
                                "facilitate difficult conversations calmly becomes easier with "
                                "preparation and small steps. Ask them to name one situation where they "
                                "want more confidence."
                            ),
                        ),
                        TeacherStep(
                            id="preview",
                            goal="Preview the day and reassure.",
                            instruction=(
                                "Affirm their answer warmly. Preview today's read, listen, write, and "
                                "speak tasks that practise this skill in a supportive way."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner sounds ready, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_difficult_conv",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Difficult conversation story",
                            generation_instructions=(
                                "Write a short story about someone facilitating a tense conversation: "
                                "they set ground rules, name the issue, and invite respectful turns. Then "
                                "comprehension questions."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ "
                                "items, each with prompt, options, correct_index, and explanation."
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
                        id="listen_shadow_difficult_conv",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Calm facilitation shadowing",
                            generation_instructions=(
                                "Generate a warm 15-second clip inviting respectful turns in a difficult "
                                "conversation for shadowing."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_shadow'. Provide audio_script, text_to_shadow (a "
                                "sentence or two from the script), target_words, and grammar_rule."
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
                        id="write_sent_trans_difficult_conv",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Reframe avoidance into facilitation language",
                            generation_instructions=(
                                "Give 3 avoidance statements and ask the learner to reframe each into "
                                "calm facilitation language."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 3 items, each with "
                                "source_sentence, sample_answer, and watch_hints."
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
                        id="speak_read_aloud_difficult_conv",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_READ_ALOUD",
                            activity="speak",
                            task_widget="read_aloud",
                            topic_override="Read a facilitation passage aloud",
                            generation_instructions=(
                                "Give a 55-70 word passage about facilitating a difficult conversation to "
                                "read aloud."
                            ),
                            widget_requirements=(
                                "Target widget 'read_aloud'. Provide text_to_read_aloud, grammar_rule "
                                "about clear pronunciation and breathing pauses, target_words, and "
                                "speaking_duration_seconds: 30."
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
                title="Counterarguments & Rebuttals",
                description=(
                    "Learners build confidence to respond to counterarguments with calm "
                    "rebuttals: acknowledge, refute with evidence, and restate your "
                    "point, using the same read-listen-write-speak sequence as earlier "
                    "confidence days at B1+ level."
                ),
                focus=(
                    "Respond to counterarguments with calm rebuttals: acknowledge, refute "
                    "with evidence, and restate your point."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to respond to counterarguments with calm rebuttals.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week. Explain in two sentences that "
                                "respond to counterarguments with calm rebuttals becomes easier with "
                                "preparation and small steps. Ask them to name one situation where they "
                                "want more confidence."
                            ),
                        ),
                        TeacherStep(
                            id="preview",
                            goal="Preview the day and reassure.",
                            instruction=(
                                "Affirm their answer warmly. Preview today's read, listen, write, and "
                                "speak tasks that practise this skill in a supportive way."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner sounds ready, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tone_id_counterarguments",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Tone in a rebuttal",
                            generation_instructions=(
                                "Provide two short arguments with counterpoints; ask which rebuttal is "
                                "respectful and evidence-based."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tone_id'. Provide passage_title and 2 items, each "
                                "with sender, message, prompt, options (Weak / Unsupported, Well-built / "
                                "Supported), correct_index, and explanation."
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
                        id="listen_mcq_counterarguments",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Rebuttal listening",
                            generation_instructions=(
                                "Generate audio with a claim and counterargument; ask inference "
                                "questions."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and at least 1 MCQ item "
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
                        id="write_timed_counterarguments",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Timed rebuttal writing",
                            generation_instructions=(
                                "Ask for a timed paragraph acknowledging a counterargument then rebutting "
                                "with one reason."
                            ),
                            widget_requirements=(
                                "Target widget 'write_timed'. Provide prompt, grammar_rule, target_words "
                                "(I argue that, because, for instance, therefore), "
                                "writing_duration_seconds: 180, sample_answer, and answer_hints."
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
                        id="speak_timed_counterarguments",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Timed rebuttal speaking",
                            generation_instructions=(
                                "Three timed speaking prompts to rebut calmly with evidence."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_timed'. Provide a single prompt, a sample_response, "
                                "grammar_rule, target_words (I believe, because, for example, overall), "
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
            DaySource(
                title="Vision & Long-Term Narrative",
                description=(
                    "Learners build confidence to share a vision and long-term narrative "
                    "with clear future focus and realistic trade-offs, using the same "
                    "read-listen-write-speak sequence as earlier confidence days at B1+ "
                    "level."
                ),
                focus=(
                    "Share a vision and long-term narrative with clear future focus and "
                    "realistic trade-offs."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to share a vision and long-term narrative with clear future focus and realistic trade-offs.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week. Explain in two sentences that "
                                "share a vision and long-term narrative with clear future focus and "
                                "realistic trade-offs becomes easier with preparation and small steps. "
                                "Ask them to name one situation where they want more confidence."
                            ),
                        ),
                        TeacherStep(
                            id="preview",
                            goal="Preview the day and reassure.",
                            instruction=(
                                "Affirm their answer warmly. Preview today's read, listen, write, and "
                                "speak tasks that practise this skill in a supportive way."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner sounds ready, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_vision",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Vision narrative comprehension",
                            generation_instructions=(
                                "Write a story about someone explaining a long-term vision with "
                                "trade-offs; comprehension MCQs."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ "
                                "items, each with prompt, options, correct_index, and explanation."
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
                        id="listen_tone_vision",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Tone in a vision talk",
                            generation_instructions=(
                                "Audio of a leader sharing vision; tone and detail questions."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_tone'. Provide two intros (each with id, label, "
                                "speaker, audio_script) and 2 MCQ items, each with prompt, options "
                                "(Unrealistic / Vague, Realistic / Grounded), correct_index, and "
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
                        id="write_sent_trans_vision",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Vision sentence transforms",
                            generation_instructions=(
                                "Transform vague future sentences into a clear vision statement with "
                                "signposting."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 3 items, each with "
                                "source_sentence, sample_answer, and watch_hints."
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
                        id="speak_pic_desc_vision",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Vision picture description",
                            generation_instructions=(
                                "Describe a photo of a team planning a long-term goal using vision "
                                "vocabulary."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing a person "
                                "studying late at a desk covered in plans, grammar_rule about speculative "
                                "language, and speaking_duration_seconds: 45."
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
                title="Giving & Receiving Critical Feedback",
                description=(
                    "Learners build confidence to give and receive critical feedback "
                    "without defensiveness: listen, clarify, and respond constructively, "
                    "using the same read-listen-write-speak sequence as earlier "
                    "confidence days at B1+ level."
                ),
                focus=(
                    "Give and receive critical feedback without defensiveness: listen, "
                    "clarify, and respond constructively."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to give and receive critical feedback without defensiveness.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week. Explain in two sentences that "
                                "give and receive critical feedback without defensiveness becomes easier "
                                "with preparation and small steps. Ask them to name one situation where "
                                "they want more confidence."
                            ),
                        ),
                        TeacherStep(
                            id="preview",
                            goal="Preview the day and reassure.",
                            instruction=(
                                "Affirm their answer warmly. Preview today's read, listen, write, and "
                                "speak tasks that practise this skill in a supportive way."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner sounds ready, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tone_id_critical_feedback",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Critical feedback tone",
                            generation_instructions=(
                                "Two feedback messages; identify which balances honesty and support."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tone_id'. Provide passage_title and 2 items, each "
                                "with sender, message, prompt, options describing tone shifts, "
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
                        id="listen_shadow_critical_feedback",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Receiving feedback shadow",
                            generation_instructions=(
                                "Short clip of receiving criticism calmly for shadowing."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_shadow'. Provide audio_script, text_to_shadow, "
                                "target_words (That's a fair point, I see what you mean, Let me explain), "
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
                        id="write_timed_critical_feedback",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Timed critical feedback writing",
                            generation_instructions=(
                                "Timed response to critical feedback that clarifies and commits to one "
                                "action."
                            ),
                            widget_requirements=(
                                "Target widget 'write_timed'. Provide prompt, grammar_rule, target_words "
                                "(Usually, Instead of, In future), writing_duration_seconds: 180, "
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
                        id="speak_smalltalk_critical_feedback",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Critical feedback small talk",
                            generation_instructions=(
                                "Small talk practicing thanking someone for direct feedback."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_smalltalk'. Provide a dialogue_context alternating "
                                "partner and learner turns, target_words (That's fair, I understand, even "
                                "so), and speaking_duration_seconds: 30."
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
                title="Strong Close & Call to Action",
                description=(
                    "Learners build confidence to close talks with a strong summary and "
                    "call to action that tells the audience what to do next, using the "
                    "same read-listen-write-speak sequence as earlier confidence days at "
                    "B1+ level."
                ),
                focus=(
                    "Close talks with a strong summary and call to action that tells the "
                    "audience what to do next."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to close talks with a strong summary and call to action that tells the audience what to do next.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week. Explain in two sentences that "
                                "close talks with a strong summary and call to action that tells the "
                                "audience what to do next becomes easier with preparation and small "
                                "steps. Ask them to name one situation where they want more confidence."
                            ),
                        ),
                        TeacherStep(
                            id="preview",
                            goal="Preview the day and reassure.",
                            instruction=(
                                "Affirm their answer warmly. Preview today's read, listen, write, and "
                                "speak tasks that practise this skill in a supportive way."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner sounds ready, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_strong_close",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Strong close comprehension",
                            generation_instructions=(
                                "Short talk text; questions about summary and call to action."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ "
                                "items, each with prompt, options, correct_index, and explanation."
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
                        id="listen_mcq_strong_close",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Listening for call to action",
                            generation_instructions=(
                                "Audio ending with summary and clear next step; MCQs."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each "
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
                        id="write_sent_trans_strong_close",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Closing sentence transforms",
                            generation_instructions=(
                                "Rewrite weak endings into strong closes with calls to action."
                            ),
                            widget_requirements=(
                                "Target widget 'sentence_transform'. Provide 3 items, each with "
                                "source_sentence, sample_answer, and watch_hints."
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
                        id="speak_pic_desc_strong_close",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Closing with call to action",
                            generation_instructions=(
                                "Describe persuading an audience to take one specific next step."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_pic_desc'. Provide image_alt describing an "
                                "overflowing recycling area outside an office, grammar_rule, and "
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
                title="Presentation with Brief Q&A",
                description=(
                    "Learners build confidence to deliver a short presentation and handle "
                    "brief Q&A with calm, structured answers, using the same "
                    "read-listen-write-speak sequence as earlier confidence days at B1+ "
                    "level."
                ),
                focus=(
                    "Deliver a short presentation and handle brief q&a with calm, "
                    "structured answers."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to deliver a short presentation and handle brief Q&A with calm, structured answers.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week. Explain in two sentences that "
                                "deliver a short presentation and handle brief Q&A with calm, structured "
                                "answers becomes easier with preparation and small steps. Ask them to "
                                "name one situation where they want more confidence."
                            ),
                        ),
                        TeacherStep(
                            id="preview",
                            goal="Preview the day and reassure.",
                            instruction=(
                                "Affirm their answer warmly. Preview today's read, listen, write, and "
                                "speak tasks that practise this skill in a supportive way."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner sounds ready, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tone_id_presentation_qa",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Presentation with Q&A tone",
                            generation_instructions=(
                                "Identify formal presentation and Q&A tone in two excerpts."
                            ),
                            widget_requirements=(
                                "Target widget 'read_tone_id'. Provide passage_title and 2 items, each "
                                "with sender, message, prompt, options including Well-structured and "
                                "clear and Rambling and unclear, correct_index, and explanation."
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
                        id="listen_tone_presentation_qa",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Q&A tone listening",
                            generation_instructions=(
                                "Audio of presentation plus one question; tone and content MCQs."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_tone'. Provide two intros (each with id, label, "
                                "speaker, audio_script) and 2 MCQ items, each with prompt, options, "
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
                        id="write_timed_presentation_qa",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Timed presentation writing",
                            generation_instructions=(
                                "Timed mini presentation paragraph with intro, two points, conclusion."
                            ),
                            widget_requirements=(
                                "Target widget 'write_timed'. Provide prompt, grammar_rule describing the "
                                "intro-points-conclusion structure, target_words (To begin, My first "
                                "point, secondly, to conclude), writing_duration_seconds: 180, "
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
                        id="speak_present_presentation_qa",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Presentation with Q&A",
                            generation_instructions=(
                                "45-second presentation excerpt plus brief answer to one audience "
                                "question."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_present'. Provide a visual_prompt_description "
                                "outlining the intro, two points, and conclusion, an optional "
                                "model_presentation, grammar_rule, target_words (To begin, firstly, "
                                "secondly, to conclude), and speaking_duration_seconds: 90."
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
                title="Full Confidence Showcase (B1+)",
                description=(
                    "Learners build confidence to integrate B1+ confidence skills in one "
                    "showcase: clear argument, calm rebuttal, vision, and strong close, "
                    "using the same read-listen-write-speak sequence as earlier "
                    "confidence days at B1+ level."
                ),
                focus=(
                    "Integrate b1+ confidence skills in one showcase: clear argument, "
                    "calm rebuttal, vision, and strong close."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to integrate B1+ confidence skills in one showcase.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week. Explain in two sentences that "
                                "integrate B1+ confidence skills in one showcase becomes easier with "
                                "preparation and small steps. Ask them to name one situation where they "
                                "want more confidence."
                            ),
                        ),
                        TeacherStep(
                            id="preview",
                            goal="Preview the day and reassure.",
                            instruction=(
                                "Affirm their answer warmly. Preview today's read, listen, write, and "
                                "speak tasks that practise this skill in a supportive way."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Once the learner sounds ready, ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_showcase_w16",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="B1+ confidence integration story",
                            generation_instructions=(
                                "Write an encouraging story where the speaker handles a counterargument, "
                                "states a vision, and closes with a call to action. Then MCQ "
                                "comprehension."
                            ),
                            widget_requirements=(
                                "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ "
                                "items, each with prompt, options, correct_index, and explanation."
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
                        id="listen_shadow_showcase_w16",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Showcase shadowing clip",
                            generation_instructions=(
                                "Generate a confident 20-second clip mixing summary and call to action "
                                "for shadowing."
                            ),
                            widget_requirements=(
                                "Target widget 'listen_shadow'. Provide audio_script, text_to_shadow, "
                                "target_words (proud of, growing, confidence), and grammar_rule about "
                                "intonation."
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
                        id="write_timed_showcase_w16",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Timed integrated confidence writing",
                            generation_instructions=(
                                "Ask for a timed paragraph integrating argument, rebuttal, and a strong "
                                "close."
                            ),
                            widget_requirements=(
                                "Target widget 'write_timed'. Provide prompt, grammar_rule, target_words "
                                "(discovered, moreover, in the future), writing_duration_seconds: 180, "
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
                        id="speak_debate_showcase_w16",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_DEBATE",
                            activity="speak",
                            task_widget="speak_debate",
                            topic_override="Debate-style showcase speaking",
                            generation_instructions=(
                                "Set up a short debate-style speaking task where the learner rebuts one "
                                "point and ends with a call to action."
                            ),
                            widget_requirements=(
                                "Target widget 'speak_debate'. Provide a debate_context with an AI "
                                "moderator turn, an AI opponent turn, and a learner turn, target_words "
                                "(strongly believe, however, on the other hand), and "
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
        ),
    ),

)
