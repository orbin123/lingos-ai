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
        sub_level_min=4,
        sub_level_max=5,
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
                depth_day=DaySource(
                    title="Past Perfect in Narratives — Already & Just",
                    description=(
                        "Building on yesterday's past perfect basics, learners order events clearly in short narratives using already, just, and by the time."
                    ),
                    focus="Clear before-ordering in narratives with already and just.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen past perfect with narrative ordering (already, just).",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce the past perfect.",
                                instruction=(
                                    "Greet the learner and note they practised had + past participle yesterday. Explain in two sentences that B2 depth uses already and just to show what had happened just before another past moment. Ask for one sentence with already about something they had finished before a past event."
                                ),
                            ),
                            TeacherStep(
                                id="form_had_pp",
                                goal="Teach the had + past participle form.",
                                instruction=(
                                    "Confirm their sentence. Model just (I had just arrived when…) and by the time in a two-clause narrative. Ask them to add by the time or just to link two past moments."
                                ),
                            ),
                            TeacherStep(
                                id="signal_words",
                                goal="Teach already, just, by the time, before, and after.",
                                instruction=(
                                    "Affirm the time words. Ask for one sentence ordering two past events with already or just."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has ordered events with already or just once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_cloze_past_perfect_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CLOZE",
                                activity="read",
                                task_widget="fill_blanks",
                                topic_override="Past Perfect in Narratives — reading cloze",
                                generation_instructions=(
                                    "Write one connected 4–5-blank passage (a short workplace or travel backstory) where every blank tests Clear before-ordering in narratives with already, just, and by the time. Include at least two distinct facets of the depth angle in the passage. Do not drill only the parent base lesson pattern; the passage must read as a depth task on Past Perfect in Narratives."
                                ),
                                widget_requirements=(
                                    "Always include base_verb for every blank so the learner forms the target form. Do not repeat base_verb inline in the passage after each ___ — the UI shows it separately."
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
                            id="listen_mcq_past_perfect_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Past Perfect in Narratives — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a short workplace or travel backstory) using Clear before-ordering in narratives with already, just, and by the time. Then 3–4 MCQs: at least two must test understanding of Clear before-ordering in narratives with already, just, and by the time (form, stance, or structure), not single-fact recall."
                                ),
                                widget_requirements="Generate 3-4 MCQ items with prompt, options, correct_index, and explanation.",
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
                            id="write_past_perfect_sentences_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_OPEN_SENT",
                                activity="write",
                                task_widget="open_text",
                                topic_override="Past Perfect in Narratives — open sentences",
                                generation_instructions=(
                                    "Ask for exactly 3 learner sentences (a short workplace or travel backstory) that each demonstrate a different facet of Clear before-ordering in narratives with already, just, and by the time. Do not ask for practice that only repeats the parent base lesson focus."
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
                            id="speak_past_perfect_events_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Past Perfect in Narratives — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a short workplace or travel backstory) each forcing production of Clear before-ordering in narratives with already, just, and by the time. Model answers must satisfy the prompt."
                                ),
                                widget_requirements=(
                                    "Create exactly 3 speaking prompts: one with I, one with he, and one with she. Include speaking_duration_seconds: 45."
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
                                        "options": [
                                            "would travel",
                                            "will travel",
                                            "travelled",
                                        ],
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
                                        "options": [
                                            "would worry",
                                            "will worry",
                                            "worried",
                                        ],
                                        "grammar_rule": "Use would + base verb in the result clause of the second conditional.",
                                        "explanation": "The imagined result uses would worry.",
                                    },
                                ],
                                "target_words_in_audio": [
                                    "had",
                                    "would swim",
                                    "would travel",
                                    "spoke",
                                    "would worry",
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
                depth_day=DaySource(
                    title="Second Conditional — Unless, Provided & Tone",
                    description=(
                        "Building on yesterday's second conditional, learners extend if-clauses with unless and provided (that) and soften tone in imaginary scenarios."
                    ),
                    focus="Unless/provided if-clauses; softer tone in unreal scenarios.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Extend second conditional with unless, provided, and tone.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce the second conditional.",
                                instruction=(
                                    "Greet the learner and note they worked on if + past simple, would + base yesterday. Explain in two sentences that B2 depth adds unless (if not) and provided (only if) and softens tone (I would probably…). Ask what they would do unless they had to work this weekend."
                                ),
                            ),
                            TeacherStep(
                                id="if_clause_form",
                                goal="Teach the past simple in the if-clause.",
                                instruction=(
                                    "Use their answer. Show provided (that) with past simple and ask them to rewrite one if-sentence as Unless…"
                                ),
                            ),
                            TeacherStep(
                                id="result_clause",
                                goal="Teach would + base verb in the result clause.",
                                instruction=(
                                    "Model a softer result (I would probably travel). Ask for one full sentence with unless or provided and would."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used unless or provided once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_error_spot_second_conditional_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_ERROR_SPOT",
                                activity="read",
                                task_widget="error_spotting",
                                topic_override="Second Conditional — error spotting",
                                generation_instructions=(
                                    "Write a 5-sentence passage (an imaginary career or lifestyle change) with exactly five single-token errors, all illustrating Unless/provided if-clauses and softer would probably tone in unreal scenarios. Diversify error types across sentences."
                                ),
                                widget_requirements=(
                                    "Target widget 'error_spotting'. Return exactly 5 `passage_sentences`. Each sentence must include `sentence_id`, `tokens`, and one `error` object. Each token needs stable `token_id`, `text`, and `is_error`; exactly one token per sentence must have `is_error: true`. Each `error` must include token_id, incorrect_phrase, correction, error_type, rule, and explanation. Set `total_errors` to 5. Allowed error_type values: irregular_past, missing_past_auxiliary, passive_helper_missing, time_marker_mismatch, object_or_complement_mismatch, past_participle_form, regular_past_ending."
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
                            id="listen_cloze_second_conditional_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_CLOZE",
                                activity="listen",
                                task_widget="listen_cloze",
                                topic_override="Second Conditional — listen and complete",
                                generation_instructions=(
                                    "Create a 40–60 word audio script (an imaginary career or lifestyle change) dense with Unless/provided if-clauses and softer would probably tone in unreal scenarios. Provide a gapped written version; blanks test Unless/provided if-clauses and softer would probably tone in unreal scenarios only."
                                ),
                                widget_requirements=(
                                    "Set inner_widget to 'fill_in_blanks'. Use the authored audio_script, passage, and 5 BlankItems exactly as provided so rule-based scoring can compare each typed verb phrase with correct_answer."
                                ),
                                static_payload={
                                    "task_intro": "Listen, then complete the second-conditional notes.",
                                    "instructions": (
                                        "Play the audio once, then type the missing second-conditional verbs in the paraphrased notes."
                                    ),
                                    "estimated_time_minutes": 3,
                                    "inner_widget": "fill_in_blanks",
                                    "audio_genre": "Personal daydream monologue",
                                    "audio_script": (
                                        "Sometimes I imagine a completely different life. If I had more free time, I would learn the piano. If I lived by the sea, I would swim every single morning. If money were not a problem, I would travel around the world. If I spoke five languages, I would work as a tour guide. Honestly, if I knew then what I know now, I would worry much less."
                                    ),
                                    "passage_title": "A Different Life Notes",
                                    "passage": (
                                        "If I ___ more free time, I would learn the piano. If I lived by the sea, I ___ every morning. If money were not a problem, I ___ around the world. If I ___ five languages, I would work as a guide. If I knew then what I know now, I ___ much less."
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
                                            "options": [
                                                "would swim",
                                                "will swim",
                                                "swam",
                                            ],
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
                                            "options": [
                                                "would travel",
                                                "will travel",
                                                "travelled",
                                            ],
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
                                            "options": [
                                                "spoke",
                                                "speak",
                                                "would speak",
                                            ],
                                            "grammar_rule": "Use the past simple in the if-clause of the second conditional.",
                                            "explanation": "The if-clause needs the past simple, so we use spoke.",
                                        },
                                        {
                                            "item_id": "b5",
                                            "blank_id": "b5",
                                            "sentence_with_blank": "If I knew then what I know now, I ___ much less.",
                                            "base_verb": "worry",
                                            "correct_answer": "would worry",
                                            "distractors": ["will worry", "worried"],
                                            "options": [
                                                "would worry",
                                                "will worry",
                                                "worried",
                                            ],
                                            "grammar_rule": "Use would + base verb in the result clause of the second conditional.",
                                            "explanation": "The imagined result uses would worry.",
                                        },
                                    ],
                                    "target_words_in_audio": [
                                        "had",
                                        "would swim",
                                        "would travel",
                                        "spoke",
                                        "would worry",
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
                            id="write_error_corr_second_conditional_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_ERROR_CORR",
                                activity="write",
                                task_widget="error_correction",
                                topic_override="Second Conditional — error correction",
                                generation_instructions=(
                                    "Provide 3 sentences (an imaginary career or lifestyle change) with one error each, all tied to Unless/provided if-clauses and softer would probably tone in unreal scenarios; the learner rewrites each correctly."
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
                            id="speak_read_aloud_second_conditional_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_READ_ALOUD",
                                activity="speak",
                                task_widget="read_aloud",
                                topic_override="Second Conditional — read aloud",
                                generation_instructions=(
                                    "Write a 50–60 word passage (an imaginary career or lifestyle change) dense with Unless/provided if-clauses and softer would probably tone in unreal scenarios for read-aloud; not an introductory lesson on the parent base form."
                                ),
                                widget_requirements=(
                                    "Populate `text_to_read_aloud` with a single connected second conditional passage (55-70 words) describing imaginary situations and their results. Set `task_intro` to 'Read the passage above out loud.' Include `grammar_rule_to_practice` explaining the second conditional with if + past simple and would + base verb, and `speaking_duration_seconds: 45`."
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
                depth_day=DaySource(
                    title="Passive in Reports — When Agent Matters",
                    description=(
                        "Building on yesterday's passive voice, learners write short news-style passives and decide when to name the agent with by."
                    ),
                    focus="Short report-style passives; when the agent matters.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen passive in reports and agent choice.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce the passive voice.",
                                instruction=(
                                    "Greet the learner and note they practised be + past participle yesterday. Explain in two sentences that report-style English often uses passive when the action matters more than the doer, but adds by when the agent is important. Ask them to report one workplace event passively."
                                ),
                            ),
                            TeacherStep(
                                id="form_be_pp",
                                goal="Teach the be + past participle form.",
                                instruction=(
                                    "Confirm their passive. Give one headline-style sentence (The report was published…) and ask when by is needed."
                                ),
                            ),
                            TeacherStep(
                                id="when_to_use",
                                goal="Teach when to choose the passive and add by.",
                                instruction=(
                                    "Model a passive without by and one with by for contrast. Ask for one past passive in a two-sentence news note."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has written a report-style passive once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_passive_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Passive in Reports — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a brief incident or product launch report) rich in Short news-style passives; when to name the agent with by. Add 3–4 comprehension MCQs where at least two require applying Short news-style passives; when to name the agent with by, not only locating a noun or date."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_dictation_passive_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Passive in Reports — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (a brief incident or product launch report) that exemplify Short news-style passives; when to name the agent with by for exact dictation. Each line should highlight one feature of Short news-style passives; when to name the agent with by."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_dictation'. Provide audio_script and 4 dictation items, each with prompt, correct_answer, and explanation. Set target_words to the passive chunks (for example 'is made', 'was sent', 'are delivered', 'will be repaired')."
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
                            id="write_sent_trans_passive_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Passive in Reports — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a brief incident or product launch report) where source and target practice Short news-style passives; when to name the agent with by (e.g. direct to reported, active to passive, clause reduction)."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 3 items, each with source_sentence, sample_answer, and watch_hints (for example 'present -> is/are + past participle', 'past -> was/were + past participle')."
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
                            id="speak_timed_passive_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Passive in Reports — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a brief incident or product launch report) each forcing production of Short news-style passives; when to name the agent with by. Model answers must satisfy the prompt."
                                ),
                                widget_requirements=(
                                    "Create exactly 3 speaking prompts: one present passive about how something is made, one past passive about something that was built or sent, and one about something that will be done. Include speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Defining vs Non-Defining — Commas & Flow",
                    description=(
                        "Building on yesterday's relative clauses, learners contrast defining and non-defining clauses with commas and reduce repetition in flow."
                    ),
                    focus="Defining vs non-defining relatives; commas and flow.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen relatives with defining vs non-defining and commas.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce relative clauses.",
                                instruction=(
                                    "Greet the learner and note they used who/which/that yesterday. Explain in two sentences that non-defining clauses add extra detail with commas (My manager, who is based in Berlin, …) while defining clauses identify which one (the colleague who leads the project). Ask them to describe a person with a non-defining clause."
                                ),
                            ),
                            TeacherStep(
                                id="defining_clauses",
                                goal="Teach placement of the relative pronoun.",
                                instruction=(
                                    "Confirm commas for non-defining. Contrast with a defining clause without commas and ask them to combine two short sentences using which or who to avoid repetition."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used commas or reduced repetition once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_relative_clauses_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Defining vs Non-Defining — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Defining vs non-defining relative clauses with commas; reduce repetition and short definitions (describing colleagues, projects, or places at work). Learners match each term to the definition that fits the depth collocation or usage."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_word_match'. Provide options (the relative pronouns who, which, that, where) and 3-4 items, each with prompt (a noun phrase with a clue), correct_answer, and explanation."
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
                            id="listen_mcq_relative_clauses_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Defining vs Non-Defining — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (describing colleagues, projects, or places at work) using Defining vs non-defining relative clauses with commas; reduce repetition. Then 3–4 MCQs: at least two must test understanding of Defining vs non-defining relative clauses with commas; reduce repetition (form, stance, or structure), not single-fact recall."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 2-3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_open_sent_relative_clauses_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_OPEN_SENT",
                                activity="write",
                                task_widget="open_text",
                                topic_override="Defining vs Non-Defining — open sentences",
                                generation_instructions=(
                                    "Ask for exactly 3 learner sentences (describing colleagues, projects, or places at work) that each demonstrate a different facet of Defining vs non-defining relative clauses with commas; reduce repetition. Do not ask for practice that only repeats the parent base lesson focus."
                                ),
                                widget_requirements=(
                                    "Target widget 'open_text'. Provide target_words (who, which, that, where), common_mistakes, and 3 items, each with prompt, sample_answer, and answer_hints."
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
                            id="speak_pic_desc_relative_clauses_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Defining vs Non-Defining — picture description",
                                generation_instructions=(
                                    "Describe an image scene (describing colleagues, projects, or places at work) using Defining vs non-defining relative clauses with commas; reduce repetition in 4–5 connected sentences; include at least one depth-specific structure from Defining vs non-defining relative clauses with commas; reduce repetition."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing a busy cafe with several people doing different things, grammar_rule, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Reported Qs, Commands & Time Shifts",
                    description=(
                        "Building on yesterday's reported statements, learners report wh-questions, commands, and time-word shifts accurately."
                    ),
                    focus="Reported questions and commands; time shifts.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen reported speech with questions, commands, and shifts.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce reported speech.",
                                instruction=(
                                    "Greet the learner and note they practised said/told with backshift yesterday. Explain in two sentences that B2 depth adds asked if/whether, told someone to…, and time shifts (today → that day). Ask them to report one question someone asked them."
                                ),
                            ),
                            TeacherStep(
                                id="backshift",
                                goal="Teach backshift of tense and pronouns.",
                                instruction=(
                                    "Model asked if and told me to. Ask them to report a polite command (Please send…) as told me to + infinitive with correct pronoun shift."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has reported a question or command once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_cloze_reported_speech_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CLOZE",
                                activity="read",
                                task_widget="fill_blanks",
                                topic_override="Reported Qs, Commands & Time Shifts — reading cloze",
                                generation_instructions=(
                                    "Write one connected 4–5-blank passage (a manager–team conversation recap) where every blank tests Reported questions, commands, and time-shift patterns. Include at least two distinct facets of the depth angle in the passage. Do not drill only the parent base lesson pattern; the passage must read as a depth task on Reported Qs, Commands & Time Shifts."
                                ),
                                widget_requirements=(
                                    "Omit base_verb on every blank. Do not include base_verb. correct_answer is the word or phrase for the blank (e.g. Unless, doesn't, said, Nevertheless)."
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
                            id="listen_infer_reported_speech_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_INFER",
                                activity="listen",
                                task_widget="listen_infer",
                                topic_override="Reported Qs, Commands & Time Shifts — listening inference",
                                generation_instructions=(
                                    "Generate a 50–70 word spoken exchange (a manager–team conversation recap) where Reported questions, commands, and time-shift patterns is implied. Ask 3 inference questions about stance, intent, or implied meaning tied to Reported questions, commands, and time-shift patterns."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_infer'. Provide audio_script, intent_focus, and 2 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_para_reported_speech_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Reported Qs, Commands & Time Shifts — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (a manager–team conversation recap) that must show Reported questions, commands, and time-shift patterns with clear organisation (topic sentence, support, close)."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paragraph'. Provide prompt, grammar_rule, target_words (said that, told me, asked if, would), minimum_words 25, sample_answer, and answer_hints."
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
                            id="speak_roleplay_reported_speech_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_ROLEPLAY",
                                activity="speak",
                                task_widget="speak_roleplay",
                                topic_override="Reported Qs, Commands & Time Shifts — roleplay",
                                generation_instructions=(
                                    "Roleplay (a manager–team conversation recap) where the learner must use Reported questions, commands, and time-shift patterns in at least two turns; include a partner cue that elicits the depth move."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_roleplay'. Provide dialogue_context with alternating partner and learner turns (4-6 turns total). Partner lines set the scene in 2-3 sentences; each learner line is 2-3 connected sentences (roughly 15-30 words). Include target_words (said that, told me, asked if, would), speaking_prompts with one instruction to respond aloud, sample_responses with the learner's model answer (same text as the learner dialogue turn), grammar_rule_to_practice, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Used To vs Would — Meaning & Negatives",
                    description=(
                        "Building on yesterday's past habits, learners contrast used to and would for past habits, and form clear negatives (didn't use to)."
                    ),
                    focus="Used to vs would for past habits; negatives.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen used to vs would and negative forms.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce used to and would.",
                                instruction=(
                                    "Greet the learner and note they practised used to and would yesterday. Explain in two sentences that used to states a past state or habit, would often describes repeated past actions (not states), and negatives use didn't use to. Ask for one thing they didn't use to do."
                                ),
                            ),
                            TeacherStep(
                                id="used_to_vs_would",
                                goal="Teach used to vs would.",
                                instruction=(
                                    "Confirm didn't use to. Ask when would fits better than used to for a repeated action (Every Sunday we would…) vs a state (I used to live…)."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has contrasted used to and would or used a negative once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tfng_used_to_would_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TFNG",
                                activity="read",
                                task_widget="read_tfng",
                                topic_override="Used To vs Would — true/false/not given",
                                generation_instructions=(
                                    "Write a 100–130 word passage (past habits and routines in personal narrative) about Contrast used to vs would for past habits; negatives and meaning. Provide 4–5 True/False/Not Given statements testing nuanced understanding of Contrast used to vs would for past habits; negatives and meaning, including one subtle distractor."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tfng'. Provide passage_title, passage, and 5 items, each with prompt, correct_answer (True, False, or Not Given), and explanation."
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
                            id="listen_shadow_used_to_would_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Used To vs Would — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (past habits and routines in personal narrative) dense with Contrast used to vs would for past habits; negatives and meaning for shadowing practice. Rhythm and phrasing should model natural B2 delivery."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_shadow'. Provide audio_script, text_to_shadow (identical to the script), target_words highlighting the used to / would chunks, and grammar_rule."
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
                            id="write_email_used_to_would_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_EMAIL",
                                activity="write",
                                task_widget="write_email",
                                topic_override="Used To vs Would — email writing",
                                generation_instructions=(
                                    "Ask for a short professional email (past habits and routines in personal narrative) applying Contrast used to vs would for past habits; negatives and meaning with appropriate opening, body moves, and close."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_email'. Provide prompt, grammar_rule, target_words (used to, would, no longer, back then), minimum_words 25, sample_answer (with To and Subject lines), and answer_hints."
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
                            id="speak_smalltalk_used_to_would_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_SMALLTALK",
                                activity="speak",
                                task_widget="speak_smalltalk",
                                topic_override="Used To vs Would — small talk",
                                generation_instructions=(
                                    "Small-talk prompts (past habits and routines in personal narrative) requiring Contrast used to vs would for past habits; negatives and meaning (echo, register shift, paraphrase, or inclusive invite) in natural replies."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_smalltalk'. Provide a dialogue_context alternating partner and learner turns, target_words (used to, would, as a child, back then), and speaking_duration_seconds: 30."
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
                depth_day=DaySource(
                    title="Although vs However — Placement",
                    description=(
                        "Building on yesterday's contrast linkers, learners place although, however, and whereas correctly in a short four-sentence argument."
                    ),
                    focus="Although vs however placement in a 4-sentence argument.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen concession/contrast with placement control.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce concession linkers.",
                                instruction=(
                                    "Greet the learner and note they used despite/whereas/however yesterday. Explain in two sentences that although joins clauses inside one sentence while However often starts a new sentence after a full stop. Ask them to compare two options they care about."
                                ),
                            ),
                            TeacherStep(
                                id="contrast_linkers",
                                goal="Teach whereas and however.",
                                instruction=(
                                    "Model Although…, … and a second sentence starting However…. Ask for a four-sentence argument with although and however placed correctly."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has placed although or however correctly once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_concession_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Although vs However — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (a balanced opinion on a work or study topic) using Although vs however placement in a four-sentence argument. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Although vs however placement in a four-sentence argument."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_context_mcq'. Provide passage_title, passage, and 4 MCQ items, each with prompt, options (despite, in spite of, whereas, however), correct_index, and explanation."
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
                            id="listen_retell_concession_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_RETELL",
                                activity="listen",
                                task_widget="listen_retell",
                                topic_override="Although vs However — listen and retell",
                                generation_instructions=(
                                    "Generate a 60–80 word monologue (a balanced opinion on a work or study topic) modeling Although vs however placement in a four-sentence argument. Ask the learner to retell including the key depth moves from Although vs however placement in a four-sentence argument."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_retell'. Provide: audio_script (the full spoken monologue text), passage_to_retell (a 2-3 sentence model retell — shorter than the audio, showing how a good student would summarise the key points using contrast linkers), sample_responses (list containing that same model retell), target_words (list of the key contrast linkers from the audio), and grammar_rule."
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
                            id="write_paraphrase_concession_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARAPHRASE",
                                activity="write",
                                task_widget="write_paraphrase",
                                topic_override="Although vs However — paraphrase",
                                generation_instructions=(
                                    "Give 3 source sentences (a balanced opinion on a work or study topic) that are blunt, vague, or off-register; ask the learner to paraphrase for Although vs however placement in a four-sentence argument."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paraphrase'. Provide 3 items, each with incorrect_sentence (the contrasting sentence pair), sample_answer, and watch_hints (the target contrast linker)."
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
                            id="speak_present_concession_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PRESENT",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Although vs However — presentation",
                                generation_instructions=(
                                    "Presentation task (a balanced opinion on a work or study topic): structured spoken segment showing Although vs however placement in a four-sentence argument with signposts and a clear close."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_present'. Provide: prompts as a list with one general question asking the learner to compare two choices and say which they prefer using contrast linkers (e.g. 'Compare living in a city and the countryside, and say which you prefer.'); visual_prompt_description as a short sample spoken answer that uses at least three contrast linkers (e.g. 'A city is exciting, whereas the countryside is calm. Despite the noise, I prefer the city. However, I visit the countryside often, so I get both.'); grammar_rule, target_words, and speaking_duration_seconds: 45."
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
    ),
    WeekSource(
        week_number=2,
        theme_type="communication",
        cefr_level="B1",
        sub_level_min=4,
        sub_level_max=5,
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
                depth_day=DaySource(
                    title="Deadlocks — Trade-offs & Conditional Offers",
                    description=(
                        "Building on yesterday's negotiating basics, learners handle deadlocks with trade-offs and conditional offers (If you…, then we…)."
                    ),
                    focus="Deadlocks; trade-offs; conditional offers.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen negotiating with conditional offers and trade-offs.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce negotiating.",
                                instruction=(
                                    "Welcome the learner and note they practised compromise phrases yesterday. Explain in two sentences that when negotiation stalls, B2 speakers offer conditional trades (If you can…, then we can…). Ask what they would offer if a teammate wanted a different deadline."
                                ),
                            ),
                            TeacherStep(
                                id="propose_compromise",
                                goal="Teach proposing a compromise.",
                                instruction=(
                                    "Affirm their idea. Model If you…, then we… and a trade-off (I can do X if you do Y). Ask them to propose one conditional offer on their scenario."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used an If you…, then we… offer once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_negotiating_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Deadlocks — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a negotiation between two parties) rich in Conditional offers and trade-offs (If you…, then we…). Add 3–4 comprehension MCQs where at least two require applying Conditional offers and trade-offs (If you…, then we…), not only locating a noun or date."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_mcq_negotiating_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Deadlocks — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a negotiation between two parties) using Conditional offers and trade-offs (If you…, then we…). Then 3–4 MCQs: at least two must test understanding of Conditional offers and trade-offs (If you…, then we…) (form, stance, or structure), not single-fact recall."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_sent_trans_negotiating_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Deadlocks — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a negotiation between two parties) where source and target practice Conditional offers and trade-offs (If you…, then we…) (e.g. direct to reported, active to passive, clause reduction)."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 3 items, each with source_sentence, sample_answer, and watch_hints."
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
                            id="speak_roleplay_negotiating_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_ROLEPLAY",
                                activity="speak",
                                task_widget="speak_roleplay",
                                topic_override="Deadlocks — roleplay",
                                generation_instructions=(
                                    "Roleplay (a negotiation between two parties) where the learner must use Conditional offers and trade-offs (If you…, then we…) in at least two turns; include a partner cue that elicits the depth move."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_roleplay'. Provide a dialogue_context alternating partner and learner turns, target_words (How about, meet halfway, that works, agreed), and speaking_duration_seconds: 30."
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
                depth_day=DaySource(
                    title="Breaking News — Stance & Follow-ups",
                    description=(
                        "Building on yesterday's telling news, learners show stance (surprise, concern) and ask two follow-up probes when reacting to news."
                    ),
                    focus="Stance when breaking news; two follow-up probes.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen telling/reacting to news with stance and follow-ups.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce telling and reacting to news.",
                                instruction=(
                                    "Greet the learner and note they shared news reactions yesterday. Explain in two sentences that B2 reactions show stance (That's surprising / I'm concerned that…). Ask how they would react to surprising work news."
                                ),
                            ),
                            TeacherStep(
                                id="react_followup",
                                goal="React and add a follow-up question.",
                                instruction=(
                                    "Model stance + two questions. Ask them to react to: 'Our office is moving next month' with stance and two follow-ups."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has shown stance and one follow-up once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tfng_telling_news_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TFNG",
                                activity="read",
                                task_widget="read_tfng",
                                topic_override="Breaking News — true/false/not given",
                                generation_instructions=(
                                    "Write a 100–130 word passage (sharing unexpected news with a colleague) about Surprise stance plus two follow-up probes. Provide 4–5 True/False/Not Given statements testing nuanced understanding of Surprise stance plus two follow-up probes, including one subtle distractor."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tfng'. Provide passage_title, passage, and 4 items, each with prompt, correct_answer (True, False, or Not Given), and explanation."
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
                            id="listen_infer_telling_news_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_INFER",
                                activity="listen",
                                task_widget="listen_infer",
                                topic_override="Breaking News — listening inference",
                                generation_instructions=(
                                    "Generate a 50–70 word spoken exchange (sharing unexpected news with a colleague) where Surprise stance plus two follow-up probes is implied. Ask 3 inference questions about stance, intent, or implied meaning tied to Surprise stance plus two follow-up probes."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_infer'. Provide audio_script, intent_focus, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_email_telling_news_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_EMAIL",
                                activity="write",
                                task_widget="write_email",
                                topic_override="Breaking News — email writing",
                                generation_instructions=(
                                    "Ask for a short professional email (sharing unexpected news with a colleague) applying Surprise stance plus two follow-up probes with appropriate opening, body moves, and close."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_email'. Provide prompt, grammar_rule, target_words, minimum_words 25, sample_answer (with To and Subject lines), and answer_hints."
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
                            id="speak_interview_telling_news_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_INTERVIEW",
                                activity="speak",
                                task_widget="speak_interview",
                                topic_override="Breaking News — interview",
                                generation_instructions=(
                                    "Interview prompts (sharing unexpected news with a colleague) where answers must demonstrate Surprise stance plus two follow-up probes (stance, follow-ups, or documented feedback moves)."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_interview'. Provide interview_context, grammar_rule, target_words (That's wonderful, Oh no, How did, What about), 3 questions each with interviewer_prompt, sample_answer, and answer_hint, and speaking_duration_seconds: 35."
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
                depth_day=DaySource(
                    title="Root Cause & Measurable Fix",
                    description=(
                        "Building on yesterday's problem-solution order, learners name root cause, impact, and a measurable fix."
                    ),
                    focus="Root cause, impact, and measurable solution.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen problem-solution with cause, impact, and measurable fix.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce explaining a problem.",
                                instruction=(
                                    "Greet the learner and note they used situation–problem–action yesterday. Explain in two sentences that B2 depth adds root cause (The underlying issue was…), impact (As a result, we lost…), and a measurable fix (by Friday / reduce errors by 20%). Ask about a problem they solved recently."
                                ),
                            ),
                            TeacherStep(
                                id="structure_order",
                                goal="Teach signposting the order.",
                                instruction=(
                                    "Affirm their story. Ask them to state the root cause and its impact in one sentence with signposting."
                                ),
                            ),
                            TeacherStep(
                                id="add_recommendation",
                                goal="Add a recommendation with a reason.",
                                instruction=(
                                    "Model a measurable fix (We will… by…). Ask for one recommendation with a number or deadline."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has named cause or a measurable fix once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_structure_problem_solution_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_STRUCTURE_ID",
                                activity="read",
                                task_widget="read_structure",
                                topic_override="Root Cause & Measurable Fix — text structure",
                                generation_instructions=(
                                    "Provide a 4–5 paragraph outline or short text (a workplace problem and proposed fix) about Root cause, impact, and measurable solution. Ask the learner to identify structure elements (problem, cause, solution, recommendation) aligned with Root cause, impact, and measurable solution."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_structure'. Provide passage_title, structure_labels ['Situation', 'Problem', 'Solution'], and 3 items, each with paragraph, correct_answer, and explanation."
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
                            id="listen_retell_problem_solution_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_RETELL",
                                activity="listen",
                                task_widget="listen_retell",
                                topic_override="Root Cause & Measurable Fix — listen and retell",
                                generation_instructions=(
                                    "Generate a 60–80 word monologue (a workplace problem and proposed fix) modeling Root cause, impact, and measurable solution. Ask the learner to retell including the key depth moves from Root cause, impact, and measurable solution."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_retell'. Provide audio_script, passage_to_retell, target_words (the situation was, the problem, so, as a result), and grammar_rule."
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
                            id="write_para_problem_solution_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Root Cause & Measurable Fix — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (a workplace problem and proposed fix) that must show Root cause, impact, and measurable solution with clear organisation (topic sentence, support, close)."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paragraph'. Provide prompt, grammar_rule, target_words (first, the problem was, so, as a result, because), minimum_words 45, sample_answer, and answer_hints."
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
                            id="speak_opinion_problem_solution_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_OPINION",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Root Cause & Measurable Fix — opinion",
                                generation_instructions=(
                                    "Opinion task (a workplace problem and proposed fix): state a position, support with cause→impact→solution or measurable fix aligned with Root cause, impact, and measurable solution."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_present'. Provide grammar_rule, target_words (I would suggest, because, the best way, however), a visual_prompt_description or prompt for the recommendation, and speaking_duration_seconds: 40."
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
                depth_day=DaySource(
                    title="Blockers, Owners & Next Steps",
                    description=(
                        "Building on yesterday's workplace updates, learners give professional status with blockers, owners, and clear next steps."
                    ),
                    focus="Status updates with blockers, owners, and next steps.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen workplace updates with blockers and ownership.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce workplace update phrases.",
                                instruction=(
                                    "Greet the learner and note they practised deadlines and clarifying tasks yesterday. Explain in two sentences that B2 status updates name blockers (We're blocked by…), owners (Alex owns…), and next steps (Next, we will… by…). Ask for a one-sentence status on a task they're doing."
                                ),
                            ),
                            TeacherStep(
                                id="extend_question",
                                goal="Practise extending a work request.",
                                instruction=(
                                    "Add blocker and owner to their update. Ask them to close with one next step and a date."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used blocker, owner, or next step once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_workplace_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Blockers, Owners & Next Steps — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a project stand-up or status update) rich in Professional status: blockers, owners, and next steps. Add 3–4 comprehension MCQs where at least two require applying Professional status: blockers, owners, and next steps, not only locating a noun or date."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_mcq_workplace_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Blockers, Owners & Next Steps — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a project stand-up or status update) using Professional status: blockers, owners, and next steps. Then 3–4 MCQs: at least two must test understanding of Professional status: blockers, owners, and next steps (form, stance, or structure), not single-fact recall."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_bullets_to_para_workplace_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_BULLETS_TO_PARA",
                                activity="write",
                                task_widget="write_bullets_to_para",
                                topic_override="Blockers, Owners & Next Steps — bullets to paragraph",
                                generation_instructions=(
                                    "Provide bullet notes (a project stand-up or status update) about Professional status: blockers, owners, and next steps; ask for one cohesive paragraph with owners, blockers, or next steps as required by the angle."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_bullets_to_para'. Provide bullets (4 work items), prompt, grammar_rule, target_words, minimum_words 25, sample_answer, and answer_hints."
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
                            id="speak_roleplay_workplace_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_ROLEPLAY",
                                activity="speak",
                                task_widget="speak_roleplay",
                                topic_override="Blockers, Owners & Next Steps — roleplay",
                                generation_instructions=(
                                    "Roleplay (a project stand-up or status update) where the learner must use Professional status: blockers, owners, and next steps in at least two turns; include a partner cue that elicits the depth move."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_roleplay'. Provide a dialogue_context alternating partner and learner turns, target_words (so far, on track, by Friday, next step), and speaking_duration_seconds: 30."
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
                depth_day=DaySource(
                    title="Acknowledge Then Refute",
                    description=(
                        "Building on yesterday's persuasive case, learners acknowledge the other side then refute with Yes, but… and evidence."
                    ),
                    focus="Acknowledge then refute with Yes, but… and evidence.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen persuasion with acknowledge-then-refute pattern.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce the topic and invite the first attempt.",
                                instruction=(
                                    "Greet the learner and note they built claim–reason–evidence yesterday. Explain in two sentences that stronger B2 persuasion acknowledges fairly (That's a fair point,) then refutes (Yes, but… / However, the data shows…). Ask how they would push back politely on a weak idea."
                                ),
                            ),
                            TeacherStep(
                                id="persuade_evidence",
                                goal="Confirm the attempt and add a reason and evidence.",
                                instruction=(
                                    "Model That's a fair point; however… with one evidence phrase. Ask them to acknowledge one downside of remote work then refute it."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Confirm they have reason and evidence and move to practice.",
                                instruction=(
                                    "If the learner has used acknowledge + however/but once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tfng_persuading_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TFNG",
                                activity="read",
                                task_widget="read_tfng",
                                topic_override="Acknowledge Then Refute — true/false/not given",
                                generation_instructions=(
                                    "Write a 100–130 word passage (persuading a skeptical stakeholder) about Acknowledge-then-refute with yes-but and evidence. Provide 4–5 True/False/Not Given statements testing nuanced understanding of Acknowledge-then-refute with yes-but and evidence, including one subtle distractor."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tfng'. Provide passage_title, passage, and 4 items, each with prompt, correct_answer (True, False, or Not Given), and explanation."
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
                            id="listen_infer_persuading_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_INFER",
                                activity="listen",
                                task_widget="listen_infer",
                                topic_override="Acknowledge Then Refute — listening inference",
                                generation_instructions=(
                                    "Generate a 50–70 word spoken exchange (persuading a skeptical stakeholder) where Acknowledge-then-refute with yes-but and evidence is implied. Ask 3 inference questions about stance, intent, or implied meaning tied to Acknowledge-then-refute with yes-but and evidence."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_infer'. Provide audio_script, intent_focus, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_idea_para_persuading_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_IDEA_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Acknowledge Then Refute — idea paragraph",
                                generation_instructions=(
                                    "Ask for a 90–120 word paragraph (persuading a skeptical stakeholder) arguing Acknowledge-then-refute with yes-but and evidence with claim, evidence, and explicit recommendation."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paragraph'. Provide prompt, grammar_rule, target_words (I believe, because, for example, admittedly), minimum_words 25, sample_answer, and answer_hints."
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
                            id="speak_pic_desc_persuading_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Acknowledge Then Refute — picture description",
                                generation_instructions=(
                                    "Describe an image scene (persuading a skeptical stakeholder) using Acknowledge-then-refute with yes-but and evidence in 4–5 connected sentences; include at least one depth-specific structure from Acknowledge-then-refute with yes-but and evidence."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing a busy car park beside an empty bus lane, grammar_rule, and speaking_duration_seconds: 40."
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
                depth_day=DaySource(
                    title="Register Repair — Blunt/Vague Fix",
                    description=(
                        "Building on yesterday's register work, learners repair blunt or vague messages for a manager vs a teammate."
                    ),
                    focus="Fix blunt or vague tone for manager vs teammate.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen register with repair for audience.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce register in messages.",
                                instruction=(
                                    "Greet the learner and note they compared professional and casual yesterday. Explain in two sentences that B2 register repair fixes blunt lines (Send it now → Could you send it by…) and vague lines (Sort this out → Please clarify who owns…). Ask them to soften one blunt message to a manager."
                                ),
                            ),
                            TeacherStep(
                                id="formal_informal",
                                goal="Change register and notice the markers.",
                                instruction=(
                                    "Confirm the repair. Ask them to rewrite the same idea for a close teammate in casual register without losing clarity."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has repaired one blunt or vague line once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tone_id_register_w10_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Register Repair — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (the same message rewritten for two audiences) demonstrating Repair blunt or vague messages for manager vs teammate. Ask the learner to identify tone/register problems or best repair choice."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tone_id'. Provide passage_title and 2 items, each with sender, message, prompt, options (Professional, Casual), correct_index, and explanation."
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
                            id="listen_tone_register_w10_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_TONE",
                                activity="listen",
                                task_widget="listen_tone",
                                topic_override="Register Repair — listening for tone",
                                generation_instructions=(
                                    "Generate two 30–40 word clips (the same message rewritten for two audiences) showing contrasting tone for Repair blunt or vague messages for manager vs teammate. Ask which clip fits the required register and why."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_tone'. Provide audio_script and at least 1 MCQ item with prompt, options (Professional, Casual), correct_index, and explanation."
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
                            id="write_paraphrase_register_w10_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARAPHRASE",
                                activity="write",
                                task_widget="write_paraphrase",
                                topic_override="Register Repair — paraphrase",
                                generation_instructions=(
                                    "Give 3 source sentences (the same message rewritten for two audiences) that are blunt, vague, or off-register; ask the learner to paraphrase for Repair blunt or vague messages for manager vs teammate."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paraphrase'. Provide 2 items, each with incorrect_sentence (the message to convert), sample_answer, and watch_hints."
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
                            id="speak_smalltalk_register_w10_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_SMALLTALK",
                                activity="speak",
                                task_widget="speak_smalltalk",
                                topic_override="Register Repair — small talk",
                                generation_instructions=(
                                    "Small-talk prompts (the same message rewritten for two audiences) requiring Repair blunt or vague messages for manager vs teammate (echo, register shift, paraphrase, or inclusive invite) in natural replies."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_smalltalk'. Provide a dialogue_context alternating partner and learner turns, target_words (That sounds great, I might, probably, weekend), and speaking_duration_seconds: 35."
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
                depth_day=DaySource(
                    title="Paraphrase & Invite Quieter Voice",
                    description=(
                        "Building on yesterday's discussion skills, learners paraphrase others' points and invite quieter voices into the conversation."
                    ),
                    focus="Paraphrase others; invite quieter voices.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen facilitation with paraphrase and inclusive invites.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Reframe discussion as building together.",
                                instruction=(
                                    "Greet the learner for communication-week depth and note they built on others' points yesterday. Explain in two sentences that B2 facilitation paraphrases (So you mean…) and invites quieter voices (We haven't heard from… / What do you think, …?). Ask which topic they enjoy discussing."
                                ),
                            ),
                            TeacherStep(
                                id="build_on_points",
                                goal="Teach building on others' points.",
                                instruction=(
                                    "Model paraphrase + invite. Ask them to paraphrase 'Remote work saves time' and invite someone quieter with one inclusive phrase."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has paraphrased or invited once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_structure_discussion_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_STRUCTURE_ID",
                                activity="read",
                                task_widget="read_structure",
                                topic_override="Paraphrase & Invite Quieter Voice — text structure",
                                generation_instructions=(
                                    "Provide a 4–5 paragraph outline or short text (a guided team discussion) about Paraphrase others' points and invite quieter voices. Ask the learner to identify structure elements (problem, cause, solution, recommendation) aligned with Paraphrase others' points and invite quieter voices."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_structure'. Provide passage_title, structure_labels ['Opening', 'Building', 'Closing'], and 3 items, each with label, paragraph, correct_answer, and explanation."
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
                            id="listen_retell_discussion_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_RETELL",
                                activity="listen",
                                task_widget="listen_retell",
                                topic_override="Paraphrase & Invite Quieter Voice — listen and retell",
                                generation_instructions=(
                                    "Generate a 60–80 word monologue (a guided team discussion) modeling Paraphrase others' points and invite quieter voices. Ask the learner to retell including the key depth moves from Paraphrase others' points and invite quieter voices."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_retell'. Set response_mode to 'written'. Provide audio_script, passage_to_retell, target_words, and grammar_rule."
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
                            id="write_email_discussion_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_EMAIL",
                                activity="write",
                                task_widget="write_email",
                                topic_override="Paraphrase & Invite Quieter Voice — email writing",
                                generation_instructions=(
                                    "Ask for a short professional email (a guided team discussion) applying Paraphrase others' points and invite quieter voices with appropriate opening, body moves, and close."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_email'. Provide prompt, grammar_rule, target_words, minimum_words 45, sample_answer (with To and Subject lines), and answer_hints."
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
                            id="speak_present_discussion_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PRESENT",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Paraphrase & Invite Quieter Voice — presentation",
                                generation_instructions=(
                                    "Presentation task (a guided team discussion): structured spoken segment showing Paraphrase others' points and invite quieter voices with signposts and a clear close."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_present'. Provide grammar_rule, target_words (we discussed, on one hand, on the other hand, in the end), a visual_prompt_description, an optional model_presentation, and speaking_duration_seconds: 60."
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
    ),
    WeekSource(
        week_number=3,
        theme_type="vocabulary",
        cefr_level="B1",
        sub_level_min=4,
        sub_level_max=5,
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
                depth_day=DaySource(
                    title="Environment Collocations — Offset, Net Zero",
                    description=(
                        "Building on yesterday's environment vocabulary, learners use policy collocations (carbon offset, net zero, emissions target) in a short policy-style paragraph."
                    ),
                    focus="Environment collocations in a policy mini-paragraph (offset, net zero).",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen environment lexis with policy collocations.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce environment words.",
                                instruction=(
                                    "Welcome the learner and note they practised environment words yesterday. Explain in two sentences that B2 depth uses collocations like carbon offset and net zero in short policy paragraphs. Ask what their city or company is doing about emissions."
                                ),
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more environment words.",
                                instruction=(
                                    "Use their answer to model offset (balance emissions) and net zero (no net emissions). Ask them to add one emissions target phrase to their idea."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used at least one policy collocation, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_environment_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Environment Collocations — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Policy collocations: carbon offset, net zero, emissions target and short definitions (a city or company sustainability policy note). Learners match each term to the definition that fits the depth collocation or usage."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_word_match'. Provide options (the environment words) and 4 items, each with prompt (the definition), correct_answer, and explanation."
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
                            id="listen_mcq_environment_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Environment Collocations — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a city or company sustainability policy note) using Policy collocations: carbon offset, net zero, emissions target. Then 3–4 MCQs: at least two must test understanding of Policy collocations: carbon offset, net zero, emissions target (form, stance, or structure), not single-fact recall."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_sent_trans_environment_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Environment Collocations — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a city or company sustainability policy note) where source and target practice Policy collocations: carbon offset, net zero, emissions target (e.g. direct to reported, active to passive, clause reduction)."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 2-3 items, each with source_sentence, sample_answer, and watch_hints."
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
                            id="speak_pic_desc_environment_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Environment Collocations — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a city or company sustainability policy note) using Policy collocations: carbon offset, net zero, emissions target in 4–5 connected sentences; include at least one depth-specific structure from Policy collocations: carbon offset, net zero, emissions target."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing a wind farm beside a smoggy city skyline, grammar_rule, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Study Journey Verbs — Enrol, Assess",
                    description=(
                        "Building on yesterday's education vocabulary, learners narrate a course journey using study verbs (enrol, assess, submit, graduate) in connected speech and writing."
                    ),
                    focus="Study journey verbs in a course narrative (enrol, assess).",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen education lexis with study-journey verb collocations.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce education words.",
                                instruction=(
                                    "Greet the learner and note they worked on education words yesterday. Explain in two sentences that today they chain study verbs (enrol, assess, resubmit) into a course narrative. Ask them to say one sentence about when they enrolled on a course."
                                ),
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more education words.",
                                instruction=(
                                    "Confirm enrol. Ask what happens after enrolment (assessed, submitted) and have them add assess or deadline in a second sentence."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has linked two study-journey verbs, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_education_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Study Journey Verbs — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (a learner's education path) using Study-journey verbs in a course narrative (enrol, assess, submit). Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Study-journey verbs in a course narrative (enrol, assess, submit)."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_context_mcq'. Provide passage_title, passage, and at least 1 MCQ item with prompt, options, correct_index, and explanation."
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
                            id="listen_dictation_education_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Study Journey Verbs — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (a learner's education path) that exemplify Study-journey verbs in a course narrative (enrol, assess, submit) for exact dictation. Each line should highlight one feature of Study-journey verbs in a course narrative (enrol, assess, submit)."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_dictation'. Provide audio_script, target_words (the key education words), and 1 dictation item with prompt, correct_answer, and explanation."
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
                            id="write_word_upgrade_education_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_WORD_UPGRADE",
                                activity="write",
                                task_widget="write_word_upgrade",
                                topic_override="Study Journey Verbs — word upgrade",
                                generation_instructions=(
                                    "Give 3 informal or vague sentences (a learner's education path); ask the learner to upgrade vocabulary to precise terms that express Study-journey verbs in a course narrative (enrol, assess, submit)."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_word_upgrade'. Provide 3 items, each with source_sentence, target_upgrade_word, sample_answer, and watch_hints."
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
                            id="speak_timed_education_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Study Journey Verbs — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a learner's education path) each forcing production of Study-journey verbs in a course narrative (enrol, assess, submit). Model answers must satisfy the prompt."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_timed'. Provide a single prompt, a sample_response, grammar_rule, target_words (enrol, assignment, revise, qualification), and speaking_duration_seconds: 60."
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
                depth_day=DaySource(
                    title="Respectful Framing & Nuanced Adjectives",
                    description=(
                        "Building on yesterday's culture vocabulary, learners discuss sensitive topics with respectful framing and nuanced adjectives (diverse, inclusive, heritage-rich)."
                    ),
                    focus="Respectful framing and nuanced adjectives on sensitive topics.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen culture lexis with respectful framing and nuance.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce culture words.",
                                instruction=(
                                    "Greet the learner and note they described traditions and community yesterday. Explain in two sentences that B2 depth uses respectful framing (people from…, cultural heritage) and nuanced adjectives on sensitive topics. Ask them to describe a diverse community they know without stereotypes."
                                ),
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more culture words.",
                                instruction=(
                                    "Affirm respectful wording. Model inclusive vs blunt adjectives and ask them to upgrade one plain description (very different people → culturally diverse community)."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used respectful framing once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_culture_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Respectful Framing & Nuanced Adjectives — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Respectful framing and nuanced adjectives on sensitive topics and short definitions (culture and society in a community profile). Learners match each term to the definition that fits the depth collocation or usage."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_word_match'. Provide options (the culture words) and 4 items, each with prompt (the definition), correct_answer, and explanation."
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
                            id="listen_mcq_culture_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Respectful Framing & Nuanced Adjectives — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (culture and society in a community profile) using Respectful framing and nuanced adjectives on sensitive topics. Then 3–4 MCQs: at least two must test understanding of Respectful framing and nuanced adjectives on sensitive topics (form, stance, or structure), not single-fact recall."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_para_culture_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Respectful Framing & Nuanced Adjectives — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (culture and society in a community profile) that must show Respectful framing and nuanced adjectives on sensitive topics with clear organisation (topic sentence, support, close)."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paragraph'. Provide prompt, grammar_rule, target_words (tradition, community, heritage, celebrate), minimum_words 20, sample_answer, and answer_hints."
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
                            id="speak_pic_desc_culture_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Respectful Framing & Nuanced Adjectives — picture description",
                                generation_instructions=(
                                    "Describe an image scene (culture and society in a community profile) using Respectful framing and nuanced adjectives on sensitive topics in 4–5 connected sentences; include at least one depth-specific structure from Respectful framing and nuanced adjectives on sensitive topics."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing a street festival with people in traditional dress, grammar_rule, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Career Move Collocations",
                    description=(
                        "Building on yesterday's work vocabulary, learners use HR-style career collocations (apply for, get promoted, hand in notice) in micro-dialogues."
                    ),
                    focus="Career move collocations in HR-style chat.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen work lexis with career-move collocations.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce work words.",
                                instruction=(
                                    "Greet the learner and note they practised workplace words yesterday. Explain in two sentences that career moves use fixed collocations (apply for a role, hand in your notice, get promoted). Ask what career move they would like next."
                                ),
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more work words.",
                                instruction=(
                                    "React to their goal. Model hand in notice vs resign and ask them to say one HR-style sentence about a colleague who got promoted."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used a career collocation, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_work_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Career Move Collocations — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (a career change conversation) using HR-style career-move collocations. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate HR-style career-move collocations."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_context_mcq'. Provide passage_title, passage, and at least 1 MCQ item with prompt, options, correct_index, and explanation."
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
                            id="listen_dictation_work_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Career Move Collocations — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (a career change conversation) that exemplify HR-style career-move collocations for exact dictation. Each line should highlight one feature of HR-style career-move collocations."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_dictation'. Provide audio_script, target_words (the key work words), and 1 dictation item with prompt, correct_answer, and explanation."
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
                            id="write_paraphrase_work_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARAPHRASE",
                                activity="write",
                                task_widget="write_paraphrase",
                                topic_override="Career Move Collocations — paraphrase",
                                generation_instructions=(
                                    "Give 3 source sentences (a career change conversation) that are blunt, vague, or off-register; ask the learner to paraphrase for HR-style career-move collocations."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paraphrase'. Provide 2 items, each with incorrect_sentence (the plain sentence), sample_answer, and watch_hints."
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
                            id="speak_timed_work_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Career Move Collocations — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a career change conversation) each forcing production of HR-style career-move collocations. Model answers must satisfy the prompt."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_timed'. Provide a single prompt, a sample_response, grammar_rule, target_words (promote, resign, collaborate, deadline), and speaking_duration_seconds: 60."
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
                depth_day=DaySource(
                    title="Claim vs Evidence — Reportedly/Allegedly",
                    description=(
                        "Building on yesterday's news vocabulary, learners separate claims from evidence using hedging language (reportedly, allegedly, according to)."
                    ),
                    focus="Claim vs evidence with reportedly/allegedly; opinion vs fact.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen news lexis with claim vs evidence language.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce news words.",
                                instruction=(
                                    "Greet the learner and note they discussed headlines and policy yesterday. Explain in two sentences that B2 news language distinguishes claims from evidence (reportedly, allegedly, according to sources). Ask them to react to: 'The minister will resign tomorrow' — fact or claim?"
                                ),
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more news words.",
                                instruction=(
                                    "Confirm it is a claim until confirmed. Show reportedly vs allegedly and ask them to rewrite the headline with one hedging phrase."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has hedged a claim at least once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_news_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Claim vs Evidence — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Distinguish claim vs evidence with reportedly/allegedly and short definitions (a news item or opinion piece). Learners match each term to the definition that fits the depth collocation or usage."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_word_match'. Provide options (the news words) and 4 items, each with prompt (the meaning), correct_answer, and explanation."
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
                            id="listen_mcq_news_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Claim vs Evidence — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a news item or opinion piece) using Distinguish claim vs evidence with reportedly/allegedly. Then 3–4 MCQs: at least two must test understanding of Distinguish claim vs evidence with reportedly/allegedly (form, stance, or structure), not single-fact recall."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_sent_trans_news_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Claim vs Evidence — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a news item or opinion piece) where source and target practice Distinguish claim vs evidence with reportedly/allegedly (e.g. direct to reported, active to passive, clause reduction)."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 3 items, each with source_sentence, sample_answer, and watch_hints."
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
                            id="speak_pic_desc_news_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Claim vs Evidence — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a news item or opinion piece) using Distinguish claim vs evidence with reportedly/allegedly in 4–5 connected sentences; include at least one depth-specific structure from Distinguish claim vs evidence with reportedly/allegedly."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing a news studio with a reporter and a headline on the screen, grammar_rule, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Values in Action — Micro-Scenarios",
                    description=(
                        "Building on yesterday's values vocabulary, learners define abstract qualities and illustrate each with a short micro-scenario."
                    ),
                    focus="Define values and show each in a micro-scenario.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen values lexis with define-plus-example micro-scenarios.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce values words.",
                                instruction=(
                                    "Greet the learner and note they upgraded values words yesterday. Explain in two sentences that B2 depth defines a value then shows it in a micro-scenario (Integrity means…; for example, she returned the wallet). Ask them to define resilience in one sentence."
                                ),
                            ),
                            TeacherStep(
                                id="stronger_words",
                                goal="Practise stronger values words.",
                                instruction=(
                                    "Confirm their definition. Ask for a two-sentence micro-scenario showing integrity or empathy in action at work or study."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has given define + example once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_values_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Values in Action — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (workplace or civic values in action) using Define abstract values with micro-scenario examples. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Define abstract values with micro-scenario examples."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_context_mcq'. Provide passage_title, passage, and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_dictation_values_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Values in Action — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (workplace or civic values in action) that exemplify Define abstract values with micro-scenario examples for exact dictation. Each line should highlight one feature of Define abstract values with micro-scenario examples."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_dictation'. Provide audio_script, target_words (the quality words), and 2 dictation items, each with a prompt sentence containing a blank, correct_answer, and explanation."
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
                            id="write_word_upgrade_values_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_WORD_UPGRADE",
                                activity="write",
                                task_widget="write_word_upgrade",
                                topic_override="Values in Action — word upgrade",
                                generation_instructions=(
                                    "Give 3 informal or vague sentences (workplace or civic values in action); ask the learner to upgrade vocabulary to precise terms that express Define abstract values with micro-scenario examples."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_word_upgrade'. Provide 3 items, each with source_sentence, target_upgrade_word, sample_answer, and watch_hints."
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
                            id="speak_timed_values_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Values in Action — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (workplace or civic values in action) each forcing production of Define abstract values with micro-scenario examples. Model answers must satisfy the prompt."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_timed'. Provide a single prompt, a sample_response, grammar_rule, target_words (integrity, resilience, perspective, empathy, ambition), and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Week Review Paragraph",
                    description=(
                        "Building on the week's vocabulary, learners recycle week 3 lexis in one cohesive review paragraph across all six topics."
                    ),
                    focus="Recycle week 3 lexis in one cohesive review paragraph.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Consolidate week 3 vocabulary in a connected paragraph.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the review day.",
                                instruction=(
                                    "Greet the learner for the vocabulary review depth day. Note they built lexis across environment, education, culture, work, news, and values this week. Explain that today they weave those words into one cohesive paragraph. Ask for two words they will definitely include."
                                ),
                            ),
                            TeacherStep(
                                id="recall_prompt",
                                goal="Prompt active recall.",
                                instruction=(
                                    "Affirm their choices. Ask them to link two topics in one sentence (for example sustainable policy and career promotion), then preview match, listening, paragraph, and 90-second recall."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has linked two topics, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_review_w11_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Week Review Paragraph — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Recycle week 3 vocabulary in one cohesive paragraph and short definitions (a week-in-review vocabulary consolidation). Learners match each term to the definition that fits the depth collocation or usage."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_word_match'. Provide options (the 6 words) and 6 items, each with prompt (the definition), correct_answer, and explanation."
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
                            id="listen_mcq_review_w11_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Week Review Paragraph — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a week-in-review vocabulary consolidation) using Recycle week 3 vocabulary in one cohesive paragraph. Then 3–4 MCQs: at least two must test understanding of Recycle week 3 vocabulary in one cohesive paragraph (form, stance, or structure), not single-fact recall."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_para_review_w11_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Week Review Paragraph — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (a week-in-review vocabulary consolidation) that must show Recycle week 3 vocabulary in one cohesive paragraph with clear organisation (topic sentence, support, close)."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paragraph'. Provide prompt, grammar_rule, target_words (the week's words), minimum_words 25, sample_answer, and answer_hints."
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
                            id="speak_timed_review_w11_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Week Review Paragraph — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a week-in-review vocabulary consolidation) each forcing production of Recycle week 3 vocabulary in one cohesive paragraph. Model answers must satisfy the prompt."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_timed'. Provide a single prompt, a sample_response, grammar_rule, target_words (the week's words), and speaking_duration_seconds: 90."
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
    ),
    WeekSource(
        week_number=4,
        theme_type="confidence",
        cefr_level="B1",
        sub_level_min=4,
        sub_level_max=5,
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
                depth_day=DaySource(
                    title="Timebox & Decision Recap",
                    description=(
                        "Building on yesterday's discussion leadership, learners timebox topics, steer the group, and close with a clear decision recap."
                    ),
                    focus="Timebox discussion topics; steer and close with decision recap.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen discussion leadership with timeboxing and decision recap.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame leading as small steps.",
                                instruction=(
                                    "Welcome the learner and note they practised inviting others yesterday. Explain in two sentences that B2 facilitation timeboxes topics (We have five minutes on…) and ends with a decision recap (So we agreed…). Ask how they would open a 10-minute team discussion."
                                ),
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction=(
                                    "Affirm their opener. Model a decision recap with three bullet actions and ask them to timebox one topic and invite one quieter voice."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has timeboxed or recapped a decision once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_leading_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Timebox & Decision Recap — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (leading a short team discussion) rich in Timebox discussion and close with decision recap and actions. Add 3–4 comprehension MCQs where at least two require applying Timebox discussion and close with decision recap and actions, not only locating a noun or date."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_shadow_leading_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Timebox & Decision Recap — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (leading a short team discussion) dense with Timebox discussion and close with decision recap and actions for shadowing practice. Rhythm and phrasing should model natural B2 delivery."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_shadow'. Provide audio_script, text_to_shadow (a sentence or two from the script), target_words, and grammar_rule."
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
                            id="write_sent_trans_leading_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Timebox & Decision Recap — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (leading a short team discussion) where source and target practice Timebox discussion and close with decision recap and actions (e.g. direct to reported, active to passive, clause reduction)."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 3 items, each with source_sentence, sample_answer, and watch_hints."
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
                            id="speak_read_aloud_leading_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_READ_ALOUD",
                                activity="speak",
                                task_widget="read_aloud",
                                topic_override="Timebox & Decision Recap — read aloud",
                                generation_instructions=(
                                    "Write a 50–60 word passage (leading a short team discussion) dense with Timebox discussion and close with decision recap and actions for read-aloud; not an introductory lesson on the parent base form."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_aloud'. Provide text_to_read_aloud, grammar_rule about clear pronunciation and breathing pauses, target_words, and speaking_duration_seconds: 30."
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
                depth_day=DaySource(
                    title="Counterclaim & One Rebuttal",
                    description=(
                        "Building on yesterday's argument structure, learners add a counterclaim and one rebuttal using however / while it's true layers."
                    ),
                    focus="Counterclaim plus one rebuttal with however-layer.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen arguments with counterclaim and rebuttal.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame a clear argument.",
                                instruction=(
                                    "Greet the learner and note they built claim-reason-example yesterday. Explain in two sentences that stronger B2 arguments acknowledge a counterclaim then rebut it (While it's true…, however…). Ask for one opinion they hold about learning English."
                                ),
                            ),
                            TeacherStep(
                                id="argument_markers",
                                goal="Name strong vs weak argument structure.",
                                instruction=(
                                    "Use their opinion. Show counterclaim + one rebuttal and ask them to add However… after a fair point against their view."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used counterclaim and rebuttal once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tone_id_argument_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Counterclaim & One Rebuttal — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (a clear argument on a work topic) demonstrating Counterclaim with however and one rebuttal. Ask the learner to identify tone/register problems or best repair choice."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tone_id'. Provide passage_title and 2 items, each with sender, message, prompt, options (Weak / Unsupported, Well-built / Supported), correct_index, and explanation."
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
                            id="listen_mcq_argument_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Counterclaim & One Rebuttal — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a clear argument on a work topic) using Counterclaim with however and one rebuttal. Then 3–4 MCQs: at least two must test understanding of Counterclaim with however and one rebuttal (form, stance, or structure), not single-fact recall."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and at least 1 MCQ item with prompt, options, correct_index, and explanation."
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
                            id="write_timed_argument_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="Counterclaim & One Rebuttal — timed writing",
                                generation_instructions=(
                                    "Timed writing (a clear argument on a work topic): produce a structured response demonstrating Counterclaim with however and one rebuttal within the time limit; include clear signposts or moves from the depth angle."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_timed'. Provide prompt, grammar_rule, target_words (I argue that, because, for instance, therefore), writing_duration_seconds: 180, sample_answer, and answer_hints."
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
                            id="speak_timed_argument_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Counterclaim & One Rebuttal — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a clear argument on a work topic) each forcing production of Counterclaim with however and one rebuttal. Model answers must satisfy the prompt."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_timed'. Provide a single prompt, a sample_response, grammar_rule, target_words (I believe, because, for example, overall), and speaking_duration_seconds: 60."
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
                depth_day=DaySource(
                    title="Prioritising with Whereas/On the other hand",
                    description=(
                        "Building on yesterday's goals language, learners compare goals and trade-offs with whereas and on the other hand."
                    ),
                    focus="Prioritise goals with whereas / on the other hand trade-offs.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen goal talk with contrasting connectors.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Invite a simple goal.",
                                instruction=(
                                    "Greet the learner and note they discussed goals and trade-offs yesterday. Explain in two sentences that B2 prioritising contrasts goals (I want X, whereas Y means giving up Z). Ask for two goals they are balancing."
                                ),
                            ),
                            TeacherStep(
                                id="goals_tradeoffs",
                                goal="Contrast confident and grounded goal language.",
                                instruction=(
                                    "Affirm both goals. Ask them to link them with whereas or on the other hand and name one trade-off honestly."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has contrasted two goals once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_goals_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Prioritising with Whereas/On the other hand — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (personal or professional goal trade-offs) rich in Compare goals with whereas and on the other hand. Add 3–4 comprehension MCQs where at least two require applying Compare goals with whereas and on the other hand, not only locating a noun or date."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_tone_goals_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_TONE",
                                activity="listen",
                                task_widget="listen_tone",
                                topic_override="Prioritising with Whereas/On the other hand — listening for tone",
                                generation_instructions=(
                                    "Generate two 30–40 word clips (personal or professional goal trade-offs) showing contrasting tone for Compare goals with whereas and on the other hand. Ask which clip fits the required register and why."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_tone'. Provide two intros (each with id, label, speaker, audio_script) and 2 MCQ items, each with prompt, options (Unrealistic / Vague, Realistic / Grounded), correct_index, and explanation."
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
                            id="write_sent_trans_goals_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Prioritising with Whereas/On the other hand — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (personal or professional goal trade-offs) where source and target practice Compare goals with whereas and on the other hand (e.g. direct to reported, active to passive, clause reduction)."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 3 items, each with source_sentence, sample_answer, and watch_hints."
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
                            id="speak_pic_desc_goals_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Prioritising with Whereas/On the other hand — picture description",
                                generation_instructions=(
                                    "Describe an image scene (personal or professional goal trade-offs) using Compare goals with whereas and on the other hand in 4–5 connected sentences; include at least one depth-specific structure from Compare goals with whereas and on the other hand."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing a person studying late at a desk covered in plans, grammar_rule about speculative language, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Clarify, Agree Partly, Plan Fix",
                    description=(
                        "Building on yesterday's calm responses, learners use a non-defensive three-step: clarify, agree partly, plan a fix."
                    ),
                    focus="Non-defensive 3-step: clarify, agree partly, plan fix.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen criticism responses with clarify–partial agree–fix.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Normalise disagreement.",
                                instruction=(
                                    "Greet the learner and note they practised calm responses yesterday. Explain in two sentences that B2 depth uses clarify (Just to confirm…), agree partly (That's fair, and…), then plan a fix (I'll… by Friday). Ask what they do when criticism feels unfair."
                                ),
                            ),
                            TeacherStep(
                                id="respond_calmly",
                                goal="Teach calm responding.",
                                instruction=(
                                    "Reassure them. Model the three-step on sample criticism and ask them to agree partly with one point and offer one concrete fix."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used clarify or partial agree once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tone_id_criticism_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Clarify, Agree Partly, Plan Fix — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (receiving feedback on performance) demonstrating Non-defensive three-step response to criticism. Ask the learner to identify tone/register problems or best repair choice."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tone_id'. Provide passage_title and 2 items, each with sender, message, prompt, options describing tone shifts, correct_index, and explanation."
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
                            id="listen_shadow_criticism_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Clarify, Agree Partly, Plan Fix — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (receiving feedback on performance) dense with Non-defensive three-step response to criticism for shadowing practice. Rhythm and phrasing should model natural B2 delivery."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_shadow'. Provide audio_script, text_to_shadow, target_words (That's a fair point, I see what you mean, Let me explain), and grammar_rule."
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
                            id="write_timed_criticism_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="Clarify, Agree Partly, Plan Fix — timed writing",
                                generation_instructions=(
                                    "Timed writing (receiving feedback on performance): produce a structured response demonstrating Non-defensive three-step response to criticism within the time limit; include clear signposts or moves from the depth angle."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_timed'. Provide prompt, grammar_rule, target_words (Usually, Instead of, In future), writing_duration_seconds: 180, sample_answer, and answer_hints."
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
                            id="speak_smalltalk_criticism_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_SMALLTALK",
                                activity="speak",
                                task_widget="speak_smalltalk",
                                topic_override="Clarify, Agree Partly, Plan Fix — small talk",
                                generation_instructions=(
                                    "Small-talk prompts (receiving feedback on performance) requiring Non-defensive three-step response to criticism (echo, register shift, paraphrase, or inclusive invite) in natural replies."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_smalltalk'. Provide a dialogue_context alternating partner and learner turns, target_words (That's fair, I understand, even so), and speaking_duration_seconds: 30."
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
                depth_day=DaySource(
                    title="Elevator Pitch + One Objection",
                    description=(
                        "Building on yesterday's pitch structure, learners deliver a 60-second elevator pitch and handle one objection briefly."
                    ),
                    focus="60s elevator pitch plus one handled objection.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen pitching with objection handling.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Invite an idea the learner cares about.",
                                instruction=(
                                    "Greet the learner and note they practised problem-idea-benefit yesterday. Explain in two sentences that B2 pitches stay under 60 seconds and answer one objection (I hear your concern; however…). Ask for a one-sentence pitch idea."
                                ),
                            ),
                            TeacherStep(
                                id="give_reasons",
                                goal="Model a clear pitch structure.",
                                instruction=(
                                    "Affirm the idea. Ask them to answer one objection with That's a fair point; however… in one sentence."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has handled one objection, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_pitching_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Elevator Pitch + One Objection — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (pitching an idea to a decision-maker) rich in 60-second pitch plus handling one objection. Add 3–4 comprehension MCQs where at least two require applying 60-second pitch plus handling one objection, not only locating a noun or date."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_mcq_pitching_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Elevator Pitch + One Objection — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (pitching an idea to a decision-maker) using 60-second pitch plus handling one objection. Then 3–4 MCQs: at least two must test understanding of 60-second pitch plus handling one objection (form, stance, or structure), not single-fact recall."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_sent_trans_pitching_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Elevator Pitch + One Objection — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (pitching an idea to a decision-maker) where source and target practice 60-second pitch plus handling one objection (e.g. direct to reported, active to passive, clause reduction)."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 3 items, each with source_sentence, sample_answer, and watch_hints."
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
                            id="speak_pic_desc_pitching_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Elevator Pitch + One Objection — picture description",
                                generation_instructions=(
                                    "Describe an image scene (pitching an idea to a decision-maker) using 60-second pitch plus handling one objection in 4–5 connected sentences; include at least one depth-specific structure from 60-second pitch plus handling one objection."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing an overflowing recycling area outside an office, grammar_rule, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Signposting & Example Handoff",
                    description=(
                        "Building on yesterday's structured talk, learners signpost clearly (Firstly, Secondly, In short) and hand off to examples smoothly."
                    ),
                    focus="Signposting and example handoff (Firstly/Secondly/In short).",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen structured talks with signposts and example handoffs.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Surface what a structured talk includes.",
                                instruction=(
                                    "Greet the learner and note they planned intro-two points-conclusion yesterday. Explain in two sentences that B2 signposting hands off to examples (My first point is…; for instance…; In short…). Ask which topic they could present for 90 seconds."
                                ),
                            ),
                            TeacherStep(
                                id="structure_poise",
                                goal="Add signposting and poise.",
                                instruction=(
                                    "Affirm the topic. Ask them to say Firstly… and For instance… for one point, then preview signposted reading, listening, timed plan, and presentation."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used two signposts once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tone_id_structured_talk_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Signposting & Example Handoff — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (a longer structured talk) demonstrating Firstly/Secondly/In short signposting with example handoff. Ask the learner to identify tone/register problems or best repair choice."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tone_id'. Provide passage_title and 2 items, each with sender, message, prompt, options including Well-structured and clear and Rambling and unclear, correct_index, and explanation."
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
                            id="listen_tone_structured_talk_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_TONE",
                                activity="listen",
                                task_widget="listen_tone",
                                topic_override="Signposting & Example Handoff — listening for tone",
                                generation_instructions=(
                                    "Generate two 30–40 word clips (a longer structured talk) showing contrasting tone for Firstly/Secondly/In short signposting with example handoff. Ask which clip fits the required register and why."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_tone'. Provide two intros (each with id, label, speaker, audio_script) and 2 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_timed_structured_talk_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="Signposting & Example Handoff — timed writing",
                                generation_instructions=(
                                    "Timed writing (a longer structured talk): produce a structured response demonstrating Firstly/Secondly/In short signposting with example handoff within the time limit; include clear signposts or moves from the depth angle."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_timed'. Provide prompt, grammar_rule describing the intro-points-conclusion structure, target_words (To begin, My first point, secondly, to conclude), writing_duration_seconds: 180, sample_answer, and answer_hints."
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
                            id="speak_present_structured_talk_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PRESENT",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Signposting & Example Handoff — presentation",
                                generation_instructions=(
                                    "Presentation task (a longer structured talk): structured spoken segment showing Firstly/Secondly/In short signposting with example handoff with signposts and a clear close."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_present'. Provide a visual_prompt_description outlining the intro, two points, and conclusion, an optional model_presentation, grammar_rule, target_words (To begin, firstly, secondly, to conclude), and speaking_duration_seconds: 90."
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
                depth_day=DaySource(
                    title="B1 Showcase Depth — Integrated",
                    description=(
                        "Cycle 3 confidence showcase depth: learners integrate leading, arguing, pitching, and structured talk with less scaffold than the base day."
                    ),
                    focus="Integrated week 4 confidence skills with less scaffold.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Showcase integrated B1 confidence skills at B2 depth.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Invite reflection on growth.",
                                instruction=(
                                    "Greet the learner for the Cycle 3 showcase depth. Note they built leadership, argument, and pitch skills this week. Explain that today combines those moves with less scaffolding. Ask how their confidence changed since day one of this cycle."
                                ),
                            ),
                            TeacherStep(
                                id="showcase_preview",
                                goal="Preview the showcase tasks.",
                                instruction=(
                                    "Celebrate progress. Preview integrated reading, shadowing, timed reflection, and debate with timebox, counterclaim, and pitch language in one flow."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="Once the learner sounds ready, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_showcase_w12_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="B1 Showcase Depth — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a showcase scenario combining discussion and pitch) rich in Integrated week-4 confidence skills with less scaffold. Add 3–4 comprehension MCQs where at least two require applying Integrated week-4 confidence skills with less scaffold, not only locating a noun or date."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_shadow_showcase_w12_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="B1 Showcase Depth — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (a showcase scenario combining discussion and pitch) dense with Integrated week-4 confidence skills with less scaffold for shadowing practice. Rhythm and phrasing should model natural B2 delivery."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_shadow'. Provide audio_script, text_to_shadow, target_words (proud of, growing, confidence), and grammar_rule about intonation."
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
                            id="write_timed_showcase_w12_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="B1 Showcase Depth — timed writing",
                                generation_instructions=(
                                    "Timed writing (a showcase scenario combining discussion and pitch): produce a structured response demonstrating Integrated week-4 confidence skills with less scaffold within the time limit; include clear signposts or moves from the depth angle."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_timed'. Provide prompt, grammar_rule, target_words (discovered, moreover, in the future), writing_duration_seconds: 180, sample_answer, and answer_hints."
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
                            id="speak_debate_showcase_w12_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_DEBATE",
                                activity="speak",
                                task_widget="speak_debate",
                                topic_override="B1 Showcase Depth — debate",
                                generation_instructions=(
                                    "Debate scenario (a showcase scenario combining discussion and pitch) integrating Integrated week-4 confidence skills with less scaffold: chair briefly, respond to one challenge, then deliver a timed closing statement."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_debate'. Provide a debate_context with an AI moderator turn, an AI opponent turn, and a learner turn, target_words (strongly believe, however, on the other hand), and speaking_duration_seconds: 60."
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
    ),
    # ── Cycle 4 — Expanding (B1+) ───────────────────────────────
    WeekSource(
        week_number=5,
        theme_type="grammar",
        cefr_level="B2",
        sub_level_min=6,
        sub_level_max=7,
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
                depth_day=DaySource(
                    title="PPC — Evidence & Result in Story",
                    description=(
                        "Building on yesterday's past perfect continuous, learners link had been …ing duration to a clear outcome in a short story (evidence → result)."
                    ),
                    focus="Past perfect continuous evidence and result in connected narrative.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen PPC with had been …ing leading to a visible outcome.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce the past perfect continuous.",
                                instruction=(
                                    "Greet the learner and note they practised had been plus verb-ing yesterday. Explain in two sentences that B2+ depth chains duration to a result (I had been working all morning, so the report was ready). Ask what they had been doing before a recent deadline."
                                ),
                            ),
                            TeacherStep(
                                id="had_been_ing",
                                goal="Teach had been + verb-ing.",
                                instruction=(
                                    "Use their answer to show evidence → result with so or therefore. Ask them to add one outcome sentence after a had been …ing line."
                                ),
                            ),
                            TeacherStep(
                                id="for_since",
                                goal="Teach for and since with the form.",
                                instruction=(
                                    "Add for or since to the duration clause, then state the result. Ask for one pair: duration with for/since + clear result."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has linked duration to a result once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_cloze_past_perf_cont_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CLOZE",
                                activity="read",
                                task_widget="fill_blanks",
                                topic_override="PPC — reading cloze",
                                generation_instructions=(
                                    "Write one connected 4–5-blank passage (a story where ongoing past action leads to a visible outcome) where every blank tests Past perfect continuous showing evidence and result in story. Include at least two distinct facets of the depth angle in the passage. Do not drill only the parent base lesson pattern; the passage must read as a depth task on PPC. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Always include base_verb for every blank so the learner forms the target form. Do not repeat base_verb inline in the passage after each ___ — the UI shows it separately."
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
                            id="listen_mcq_past_perf_cont_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="PPC — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a story where ongoing past action leads to a visible outcome) using Past perfect continuous showing evidence and result in story. Then 3–4 MCQs: at least two must test understanding of Past perfect continuous showing evidence and result in story (form, stance, or structure), not single-fact recall. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements="Generate 3-4 MCQ items with prompt, options, correct_index, and explanation.",
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
                            id="write_past_perf_cont_sentences_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_OPEN_SENT",
                                activity="write",
                                task_widget="open_text",
                                topic_override="PPC — open sentences",
                                generation_instructions=(
                                    "Ask for exactly 3 learner sentences (a story where ongoing past action leads to a visible outcome) that each demonstrate a different facet of Past perfect continuous showing evidence and result in story. Do not ask for practice that only repeats the parent base lesson focus. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_past_perf_cont_events_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="PPC — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a story where ongoing past action leads to a visible outcome) each forcing production of Past perfect continuous showing evidence and result in story. Model answers must satisfy the prompt. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Create exactly 3 speaking prompts: one with I, one with he, and one with she. Include speaking_duration_seconds: 45."
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
                            static_payload={
                                "task_intro": "Listen, then complete the third-conditional notes.",
                                "instructions": "Play the audio once, then type the missing third-conditional verbs "
                                "in the paraphrased notes.",
                                "estimated_time_minutes": 3,
                                "inner_widget": "fill_in_blanks",
                                "audio_genre": "Reflective regrets monologue",
                                "audio_script": "Sometimes I think about different choices. If I had studied harder, "
                                "I would have passed the exam. If we had left earlier, we would have "
                                "caught the train. If she had known the truth, she would have called "
                                "me. If they had invited us, we would have come to the party. "
                                "Honestly, if I had listened to your advice, I would have saved a lot "
                                "of time.",
                                "passage_title": "Different Choices Notes",
                                "passage": "If I ___ harder, I would have passed the exam. If we had left earlier, we "
                                "___ the train. If she had known the truth, she ___ me. If they ___ us, we "
                                "would have come. If I had listened to your advice, I ___ a lot of time.",
                                "items": [
                                    {
                                        "item_id": "b1",
                                        "blank_id": "b1",
                                        "sentence_with_blank": "If I ___ harder, I would have passed the exam.",
                                        "base_verb": "study",
                                        "correct_answer": "had studied",
                                        "distractors": ["studied", "would study"],
                                        "options": [
                                            "had studied",
                                            "studied",
                                            "would study",
                                        ],
                                        "grammar_rule": "Use the past perfect in the if-clause of the third "
                                        "conditional.",
                                        "explanation": "The if-clause needs had + past participle, so we use had "
                                        "studied.",
                                    },
                                    {
                                        "item_id": "b2",
                                        "blank_id": "b2",
                                        "sentence_with_blank": "If we had left earlier, we ___ the train.",
                                        "base_verb": "catch",
                                        "correct_answer": "would have caught",
                                        "distractors": ["will catch", "caught"],
                                        "options": [
                                            "would have caught",
                                            "will catch",
                                            "caught",
                                        ],
                                        "grammar_rule": "Use would have + past participle in the result clause.",
                                        "explanation": "The unreal past result uses would have caught.",
                                    },
                                    {
                                        "item_id": "b3",
                                        "blank_id": "b3",
                                        "sentence_with_blank": "If she had known the truth, she ___ me.",
                                        "base_verb": "call",
                                        "correct_answer": "would have called",
                                        "distractors": ["will call", "called"],
                                        "options": [
                                            "would have called",
                                            "will call",
                                            "called",
                                        ],
                                        "grammar_rule": "Use would have + past participle in the result clause.",
                                        "explanation": "The imagined past result uses would have called.",
                                    },
                                    {
                                        "item_id": "b4",
                                        "blank_id": "b4",
                                        "sentence_with_blank": "If they ___ us, we would have come.",
                                        "base_verb": "invite",
                                        "correct_answer": "had invited",
                                        "distractors": ["invited", "would invite"],
                                        "options": [
                                            "had invited",
                                            "invited",
                                            "would invite",
                                        ],
                                        "grammar_rule": "Use the past perfect in the if-clause of the third "
                                        "conditional.",
                                        "explanation": "The if-clause needs had invited.",
                                    },
                                    {
                                        "item_id": "b5",
                                        "blank_id": "b5",
                                        "sentence_with_blank": "If I had listened to your advice, I ___ a lot of "
                                        "time.",
                                        "base_verb": "save",
                                        "correct_answer": "would have saved",
                                        "distractors": ["will save", "saved"],
                                        "options": [
                                            "would have saved",
                                            "will save",
                                            "saved",
                                        ],
                                        "grammar_rule": "Use would have + past participle in the result clause.",
                                        "explanation": "The imagined past result uses would have saved.",
                                    },
                                ],
                                "target_words_in_audio": [
                                    "had studied",
                                    "would have caught",
                                    "would have called",
                                    "had invited",
                                    "would have saved",
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
                depth_day=DaySource(
                    title="Regret Chains — Two If-Clauses",
                    description=(
                        "Building on yesterday's third conditional, learners express two regrets about the same past event using paired if-clauses."
                    ),
                    focus="Two third-conditional regret chains about the same past event.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen third conditional with dual regret chains.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce the third conditional.",
                                instruction=(
                                    "Greet the learner and note they worked on if + past perfect / would have yesterday. Explain in two sentences that B2+ depth stacks two regrets about one event (If I had…, I would have…; If we had…, we would have…). Ask for one choice they regret from last year."
                                ),
                            ),
                            TeacherStep(
                                id="if_clause_pp",
                                goal="Teach the past perfect in the if-clause.",
                                instruction=(
                                    "Model two if-clauses about the same event with different angles. Ask them to finish one if-clause and start a second about the same situation."
                                ),
                            ),
                            TeacherStep(
                                id="would_have",
                                goal="Teach would have + past participle.",
                                instruction=(
                                    "Confirm both result clauses use would have + past participle. Ask for a mini-chain of two complete third-conditional sentences on one topic."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has given two linked regrets once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_error_spot_third_conditional_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_ERROR_SPOT",
                                activity="read",
                                task_widget="error_spotting",
                                topic_override="Regret Chains — error spotting",
                                generation_instructions=(
                                    "Write a 5-sentence passage (professional regret about a past decision) with exactly five single-token errors, all illustrating Two if-clauses expressing regret about the same event. Diversify error types across sentences. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'error_spotting'. Return exactly 5 `passage_sentences`. Each sentence must include `sentence_id`, `tokens`, and one `error` object. Each token needs stable `token_id`, `text`, and `is_error`; exactly one token per sentence must have `is_error: true`. Each `error` must include token_id, incorrect_phrase, correction, error_type, rule, and explanation. Set `total_errors` to 5. Allowed error_type values: irregular_past, missing_past_auxiliary, passive_helper_missing, time_marker_mismatch, object_or_complement_mismatch, past_participle_form, regular_past_ending."
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
                            id="listen_cloze_third_conditional_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_CLOZE",
                                activity="listen",
                                task_widget="listen_cloze",
                                topic_override="Regret Chains — listen and complete",
                                generation_instructions=(
                                    "Create a 40–60 word audio script (professional regret about a past decision) dense with Two if-clauses expressing regret about the same event. Provide a gapped written version; blanks test Two if-clauses expressing regret about the same event only. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Set inner_widget to 'fill_in_blanks'. Use the authored audio_script, passage, and 5 BlankItems exactly as provided so rule-based scoring can compare each typed verb phrase with correct_answer."
                                ),
                                static_payload={
                                    "task_intro": "Listen, then complete the third-conditional notes.",
                                    "instructions": (
                                        "Play the audio once, then type the missing third-conditional verbs in the paraphrased notes."
                                    ),
                                    "estimated_time_minutes": 3,
                                    "inner_widget": "fill_in_blanks",
                                    "audio_genre": "Reflective regrets monologue",
                                    "audio_script": (
                                        "Sometimes I think about different choices. If I had studied harder, I would have passed the exam. If we had left earlier, we would have caught the train. If she had known the truth, she would have called me. If they had invited us, we would have come to the party. Honestly, if I had listened to your advice, I would have saved a lot of time."
                                    ),
                                    "passage_title": "Different Choices Notes",
                                    "passage": (
                                        "If I ___ harder, I would have passed the exam. If we had left earlier, we ___ the train. If she had known the truth, she ___ me. If they ___ us, we would have come. If I had listened to your advice, I ___ a lot of time."
                                    ),
                                    "items": [
                                        {
                                            "item_id": "b1",
                                            "blank_id": "b1",
                                            "sentence_with_blank": "If I ___ harder, I would have passed the exam.",
                                            "base_verb": "study",
                                            "correct_answer": "had studied",
                                            "distractors": ["studied", "would study"],
                                            "options": [
                                                "had studied",
                                                "studied",
                                                "would study",
                                            ],
                                            "grammar_rule": "Use the past perfect in the if-clause of the third conditional.",
                                            "explanation": "The if-clause needs had + past participle, so we use had studied.",
                                        },
                                        {
                                            "item_id": "b2",
                                            "blank_id": "b2",
                                            "sentence_with_blank": "If we had left earlier, we ___ the train.",
                                            "base_verb": "catch",
                                            "correct_answer": "would have caught",
                                            "distractors": ["will catch", "caught"],
                                            "options": [
                                                "would have caught",
                                                "will catch",
                                                "caught",
                                            ],
                                            "grammar_rule": "Use would have + past participle in the result clause.",
                                            "explanation": "The unreal past result uses would have caught.",
                                        },
                                        {
                                            "item_id": "b3",
                                            "blank_id": "b3",
                                            "sentence_with_blank": "If she had known the truth, she ___ me.",
                                            "base_verb": "call",
                                            "correct_answer": "would have called",
                                            "distractors": ["will call", "called"],
                                            "options": [
                                                "would have called",
                                                "will call",
                                                "called",
                                            ],
                                            "grammar_rule": "Use would have + past participle in the result clause.",
                                            "explanation": "The imagined past result uses would have called.",
                                        },
                                        {
                                            "item_id": "b4",
                                            "blank_id": "b4",
                                            "sentence_with_blank": "If they ___ us, we would have come.",
                                            "base_verb": "invite",
                                            "correct_answer": "had invited",
                                            "distractors": ["invited", "would invite"],
                                            "options": [
                                                "had invited",
                                                "invited",
                                                "would invite",
                                            ],
                                            "grammar_rule": "Use the past perfect in the if-clause of the third conditional.",
                                            "explanation": "The if-clause needs had invited.",
                                        },
                                        {
                                            "item_id": "b5",
                                            "blank_id": "b5",
                                            "sentence_with_blank": "If I had listened to your advice, I ___ a lot of time.",
                                            "base_verb": "save",
                                            "correct_answer": "would have saved",
                                            "distractors": ["will save", "saved"],
                                            "options": [
                                                "would have saved",
                                                "will save",
                                                "saved",
                                            ],
                                            "grammar_rule": "Use would have + past participle in the result clause.",
                                            "explanation": "The imagined past result uses would have saved.",
                                        },
                                    ],
                                    "target_words_in_audio": [
                                        "had studied",
                                        "would have caught",
                                        "would have called",
                                        "had invited",
                                        "would have saved",
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
                            id="write_error_corr_third_conditional_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_ERROR_CORR",
                                activity="write",
                                task_widget="error_correction",
                                topic_override="Regret Chains — error correction",
                                generation_instructions=(
                                    "Provide 3 sentences (professional regret about a past decision) with one error each, all tied to Two if-clauses expressing regret about the same event; the learner rewrites each correctly. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_read_aloud_third_conditional_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_READ_ALOUD",
                                activity="speak",
                                task_widget="read_aloud",
                                topic_override="Regret Chains — read aloud",
                                generation_instructions=(
                                    "Write a 50–60 word passage (professional regret about a past decision) dense with Two if-clauses expressing regret about the same event for read-aloud; not an introductory lesson on the parent base form. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Populate `text_to_read_aloud` with a single connected second conditional passage (55-70 words) describing imaginary situations and their results. Set `task_intro` to 'Read the passage above out loud.' Include `grammar_rule_to_practice` explaining the second conditional with if + past simple and would + base verb, and `speaking_duration_seconds: 45`."
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
                depth_day=DaySource(
                    title="Service Contexts — Repairs & Appointments",
                    description=(
                        "Building on yesterday's causative have/get, learners use service contexts (repairs, appointments) and clarify who performs the action."
                    ),
                    focus="Causative have/get in repairs and appointments; who does the action.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen causatives in service and repair scenarios.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce causative have and get.",
                                instruction=(
                                    "Greet the learner and note they practised have something done yesterday. Explain in two sentences that B2+ depth uses repairs and appointments (I'll have the car serviced; I got my laptop fixed). Ask what they last had repaired or arranged for someone else to do."
                                ),
                            ),
                            TeacherStep(
                                id="have_done",
                                goal="Teach have + object + past participle.",
                                instruction=(
                                    "Use their example to contrast who does the work (you vs the technician). Ask for one have + object + past participle in a repair context."
                                ),
                            ),
                            TeacherStep(
                                id="get_to",
                                goal="Teach get + object + to-infinitive.",
                                instruction=(
                                    "Introduce get someone to do something for persuasion or arrangement. Ask them to say one get sentence about booking or chasing a service appointment."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has clarified who acts once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_causative_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Service Contexts — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (arranging repairs or service appointments) rich in Causative have/get in repairs and appointments; who does the action. Add 3–4 comprehension MCQs where at least two require applying Causative have/get in repairs and appointments; who does the action, not only locating a noun or date. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_dictation_causative_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Service Contexts — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (arranging repairs or service appointments) that exemplify Causative have/get in repairs and appointments; who does the action for exact dictation. Each line should highlight one feature of Causative have/get in repairs and appointments; who does the action. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_dictation'. Provide audio_script and 4 dictation items, each with prompt, correct_answer, and explanation. Set target_words to the passive chunks (for example 'is made', 'was sent', 'are delivered', 'will be repaired')."
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
                            id="write_sent_trans_causative_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Service Contexts — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (arranging repairs or service appointments) where source and target practice Causative have/get in repairs and appointments; who does the action (e.g. direct to reported, active to passive, clause reduction). B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 3 items, each with source_sentence, sample_answer, and watch_hints (for example 'present -> is/are + past participle', 'past -> was/were + past participle')."
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
                            id="speak_timed_causative_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Service Contexts — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (arranging repairs or service appointments) each forcing production of Causative have/get in repairs and appointments; who does the action. Model answers must satisfy the prompt. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Create exactly 3 speaking prompts: one present passive about how something is made, one past passive about something that was built or sent, and one about something that will be done. Include speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Formal Description Flow",
                    description=(
                        "Building on yesterday's reduced and non-defining relatives, learners produce formal descriptions with reduced clauses that stay unambiguous."
                    ),
                    focus="Reduced relatives in formal description without ambiguity.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen relative reduction for formal fluent description.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce non-defining and reduced clauses.",
                                instruction=(
                                    "Greet the learner and note they practised non-defining and reduced clauses yesterday. Explain in two sentences that B2+ formal flow reduces clauses only when meaning stays clear. Ask them to describe a colleague or project in one sentence with a comma clause."
                                ),
                            ),
                            TeacherStep(
                                id="non_defining",
                                goal="Teach commas with extra information.",
                                instruction=(
                                    "Affirm their comma clause. Show a safe reduction (who is leading → leading) and ask them to add one reduced phrase to their description."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used a reduced or non-defining clause once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_relative_reduced_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Formal Description Flow — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Reduced relative clauses in formal description without ambiguity and short definitions (a formal profile or role description). Learners match each term to the definition that fits the depth collocation or usage. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_word_match'. Provide options (the relative pronouns who, which, that, where) and 3-4 items, each with prompt (a noun phrase with a clue), correct_answer, and explanation."
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
                            id="listen_mcq_relative_reduced_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Formal Description Flow — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a formal profile or role description) using Reduced relative clauses in formal description without ambiguity. Then 3–4 MCQs: at least two must test understanding of Reduced relative clauses in formal description without ambiguity (form, stance, or structure), not single-fact recall. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 2-3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_open_sent_relative_reduced_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_OPEN_SENT",
                                activity="write",
                                task_widget="open_text",
                                topic_override="Formal Description Flow — open sentences",
                                generation_instructions=(
                                    "Ask for exactly 3 learner sentences (a formal profile or role description) that each demonstrate a different facet of Reduced relative clauses in formal description without ambiguity. Do not ask for practice that only repeats the parent base lesson focus. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'open_text'. Provide target_words (who, which, that, where), common_mistakes, and 3 items, each with prompt, sample_answer, and answer_hints."
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
                            id="speak_pic_desc_relative_reduced_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Formal Description Flow — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a formal profile or role description) using Reduced relative clauses in formal description without ambiguity in 4–5 connected sentences; include at least one depth-specific structure from Reduced relative clauses in formal description without ambiguity. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing a busy cafe with several people doing different things, grammar_rule, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Tone — Deny/Suggest/Claim Patterns",
                    description=(
                        "Building on yesterday's reporting verbs, learners match verb strength to tone (deny, suggest, claim) with correct grammar patterns."
                    ),
                    focus="Reporting verb tone: deny, suggest, claim with correct patterns.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen reporting verbs for tone and grammar control.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce reporting verbs.",
                                instruction=(
                                    "Greet the learner and note they practised reporting verbs yesterday. Explain in two sentences that B2+ depth matches verb strength to tone (deny + gerund, suggest + clause, claim + that). Ask how they would report that a colleague denied a rumour."
                                ),
                            ),
                            TeacherStep(
                                id="verb_patterns",
                                goal="Teach verb + pattern combinations.",
                                instruction=(
                                    "Model deny + gerund vs suggest + should/that. Ask them to say one claim sentence and one softer suggest sentence about the same news item."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has contrasted deny/suggest/claim once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_cloze_reporting_verbs_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CLOZE",
                                activity="read",
                                task_widget="fill_blanks",
                                topic_override="Tone — reading cloze",
                                generation_instructions=(
                                    "Write one connected 4–5-blank passage (a disputed workplace or media account) where every blank tests Reporting verb strength: deny, suggest, claim patterns. Include at least two distinct facets of the depth angle in the passage. Do not drill only the parent base lesson pattern; the passage must read as a depth task on Tone. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Omit base_verb on every blank. Do not include base_verb. correct_answer is the word or phrase for the blank (e.g. Unless, doesn't, said, Nevertheless)."
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
                            id="listen_infer_reporting_verbs_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_INFER",
                                activity="listen",
                                task_widget="listen_infer",
                                topic_override="Tone — listening inference",
                                generation_instructions=(
                                    "Generate a 50–70 word spoken exchange (a disputed workplace or media account) where Reporting verb strength: deny, suggest, claim patterns is implied. Ask 3 inference questions about stance, intent, or implied meaning tied to Reporting verb strength: deny, suggest, claim patterns. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_infer'. Provide audio_script, intent_focus, and 2 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_para_reporting_verbs_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Tone — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (a disputed workplace or media account) that must show Reporting verb strength: deny, suggest, claim patterns with clear organisation (topic sentence, support, close). B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paragraph'. Provide prompt, grammar_rule, target_words (said that, told me, asked if, would), minimum_words 25, sample_answer, and answer_hints."
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
                            id="speak_roleplay_reporting_verbs_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_ROLEPLAY",
                                activity="speak",
                                task_widget="speak_roleplay",
                                topic_override="Tone — roleplay",
                                generation_instructions=(
                                    "Roleplay (a disputed workplace or media account) where the learner must use Reporting verb strength: deny, suggest, claim patterns in at least two turns; include a partner cue that elicits the depth move. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_roleplay'. Provide dialogue_context with alternating partner and learner turns (4-6 turns total). Partner lines set the scene in 2-3 sentences; each learner line is 2-3 connected sentences (roughly 15-30 words). Include target_words (said that, told me, asked if, would), speaking_prompts with one instruction to respond aloud, sample_responses with the learner's model answer (same text as the learner dialogue turn), grammar_rule_to_practice, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Apology Register — Wish/Should Have",
                    description=(
                        "Building on yesterday's wish and regret forms, learners use professional apology register with I wish and should have."
                    ),
                    focus="Professional apology register with wish and should have.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen wish/regret for formal apologies.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce wish and regret forms.",
                                instruction=(
                                    "Greet the learner and note they practised I wish and should have yesterday. Explain in two sentences that B2+ apologies combine regret (I wish I had…) with responsibility (I should have told you sooner). Ask about a small work mistake they would apologise for."
                                ),
                            ),
                            TeacherStep(
                                id="wish_should_have",
                                goal="Teach wish vs should have.",
                                instruction=(
                                    "Use their example to model a brief apology with one wish and one should have. Ask them to say a two-sentence apology to a manager or client."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used wish or should have in apology register once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tfng_wish_regret_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TFNG",
                                activity="read",
                                task_widget="read_tfng",
                                topic_override="Apology Register — true/false/not given",
                                generation_instructions=(
                                    "Write a 100–130 word passage (a formal apology or regret message) about Professional regret with wish and should have. Provide 4–5 True/False/Not Given statements testing nuanced understanding of Professional regret with wish and should have, including one subtle distractor. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tfng'. Provide passage_title, passage, and 5 items, each with prompt, correct_answer (True, False, or Not Given), and explanation."
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
                            id="listen_shadow_wish_regret_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Apology Register — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (a formal apology or regret message) dense with Professional regret with wish and should have for shadowing practice. Rhythm and phrasing should model natural B2+ delivery. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_shadow'. Provide audio_script, text_to_shadow (identical to the script), target_words highlighting the used to / would chunks, and grammar_rule."
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
                            id="write_email_wish_regret_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_EMAIL",
                                activity="write",
                                task_widget="write_email",
                                topic_override="Apology Register — email writing",
                                generation_instructions=(
                                    "Ask for a short professional email (a formal apology or regret message) applying Professional regret with wish and should have with appropriate opening, body moves, and close. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_email'. Provide prompt, grammar_rule, target_words (used to, would, no longer, back then), minimum_words 25, sample_answer (with To and Subject lines), and answer_hints."
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
                            id="speak_smalltalk_wish_regret_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_SMALLTALK",
                                activity="speak",
                                task_widget="speak_smalltalk",
                                topic_override="Apology Register — small talk",
                                generation_instructions=(
                                    "Small-talk prompts (a formal apology or regret message) requiring Professional regret with wish and should have (echo, register shift, paraphrase, or inclusive invite) in natural replies. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_smalltalk'. Provide a dialogue_context alternating partner and learner turns, target_words (used to, would, as a child, back then), and speaking_duration_seconds: 30."
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
                depth_day=DaySource(
                    title="Nevertheless/Moreover in Email",
                    description=(
                        "Building on yesterday's formal linkers, learners control nevertheless and moreover with correct punctuation in email-style paragraphs."
                    ),
                    focus="Nevertheless and moreover in email with punctuation control.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen formal linkers in email paragraphs.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce formal linkers.",
                                instruction=(
                                    "Greet the learner and note they practised moreover and nevertheless yesterday. Explain in two sentences that B2+ emails punctuate linkers clearly (Moreover, …; …, nevertheless, …). Ask them to outline one professional email they need to write."
                                ),
                            ),
                            TeacherStep(
                                id="addition_contrast",
                                goal="Teach moreover vs nevertheless.",
                                instruction=(
                                    "Model moreover for adding a point and nevertheless for contrast with commas. Ask them to say one sentence of each about their email topic."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used moreover or nevertheless once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_formal_linkers_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Nevertheless/Moreover in Email — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (a formal professional email) using Formal linkers nevertheless and moreover with punctuation control. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Formal linkers nevertheless and moreover with punctuation control. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_context_mcq'. Provide passage_title, passage, and 4 MCQ items, each with prompt, options (despite, in spite of, whereas, however), correct_index, and explanation."
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
                            id="listen_retell_formal_linkers_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_RETELL",
                                activity="listen",
                                task_widget="listen_retell",
                                topic_override="Nevertheless/Moreover in Email — listen and retell",
                                generation_instructions=(
                                    "Generate a 60–80 word monologue (a formal professional email) modeling Formal linkers nevertheless and moreover with punctuation control. Ask the learner to retell including the key depth moves from Formal linkers nevertheless and moreover with punctuation control. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_retell'. Provide: audio_script (the full spoken monologue text), passage_to_retell (a 2-3 sentence model retell — shorter than the audio, showing how a good student would summarise the key points using contrast linkers), sample_responses (list containing that same model retell), target_words (list of the key contrast linkers from the audio), and grammar_rule."
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
                            id="write_paraphrase_formal_linkers_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARAPHRASE",
                                activity="write",
                                task_widget="write_paraphrase",
                                topic_override="Nevertheless/Moreover in Email — paraphrase",
                                generation_instructions=(
                                    "Give 3 source sentences (a formal professional email) that are blunt, vague, or off-register; ask the learner to paraphrase for Formal linkers nevertheless and moreover with punctuation control. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paraphrase'. Provide 3 items, each with incorrect_sentence (the contrasting sentence pair), sample_answer, and watch_hints (the target contrast linker)."
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
                            id="speak_present_formal_linkers_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PRESENT",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Nevertheless/Moreover in Email — presentation",
                                generation_instructions=(
                                    "Presentation task (a formal professional email): structured spoken segment showing Formal linkers nevertheless and moreover with punctuation control with signposts and a clear close. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_present'. Provide: prompts as a list with one general question asking the learner to compare two choices and say which they prefer using contrast linkers (e.g. 'Compare living in a city and the countryside, and say which you prefer.'); visual_prompt_description as a short sample spoken answer that uses at least three contrast linkers (e.g. 'A city is exciting, whereas the countryside is calm. Despite the noise, I prefer the city. However, I visit the countryside often, so I get both.'); grammar_rule, target_words, and speaking_duration_seconds: 45."
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
    ),
    WeekSource(
        week_number=6,
        theme_type="communication",
        cefr_level="B2",
        sub_level_min=6,
        sub_level_max=7,
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
                depth_day=DaySource(
                    title="Reframe Positions & Test Agreement",
                    description=(
                        "Building on yesterday's conflict language, learners reframe positions as interests and test agreement with a clear criterion."
                    ),
                    focus="Reframe positions as interests; test agreement with a criterion.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen conflict resolution with interest reframing.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce conflict resolution.",
                                instruction=(
                                    "Welcome the learner and note they practised middle-ground language yesterday. Explain in two sentences that B2+ depth reframes positions (You want X — what you need is…) and tests agreement (Does this meet your main need?). Ask about a recent disagreement at work or study."
                                ),
                            ),
                            TeacherStep(
                                id="middle_ground",
                                goal="Teach middle-ground phrases.",
                                instruction=(
                                    "Use their example to name interests behind positions and propose one objective criterion. Ask them to reframe one side's position as an interest."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has reframed a position or tested agreement once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_conflict_resolution_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Reframe Positions & Test Agreement — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (conflict resolution between two sides) rich in Reframe positions on interests and test agreement. Add 3–4 comprehension MCQs where at least two require applying Reframe positions on interests and test agreement, not only locating a noun or date. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_mcq_conflict_resolution_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Reframe Positions & Test Agreement — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (conflict resolution between two sides) using Reframe positions on interests and test agreement. Then 3–4 MCQs: at least two must test understanding of Reframe positions on interests and test agreement (form, stance, or structure), not single-fact recall. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_sent_trans_conflict_resolution_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Reframe Positions & Test Agreement — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (conflict resolution between two sides) where source and target practice Reframe positions on interests and test agreement (e.g. direct to reported, active to passive, clause reduction). B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 3 items, each with source_sentence, sample_answer, and watch_hints."
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
                            id="speak_roleplay_conflict_resolution_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_ROLEPLAY",
                                activity="speak",
                                task_widget="speak_roleplay",
                                topic_override="Reframe Positions & Test Agreement — roleplay",
                                generation_instructions=(
                                    "Roleplay (conflict resolution between two sides) where the learner must use Reframe positions on interests and test agreement in at least two turns; include a partner cue that elicits the depth move. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_roleplay'. Provide a dialogue_context alternating partner and learner turns, target_words (How about, meet halfway, that works, agreed), and speaking_duration_seconds: 30."
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
                depth_day=DaySource(
                    title="Behaviour, Impact, Request",
                    description=(
                        "Building on yesterday's feedback structure, learners give constructive feedback as behaviour, impact, and a measurable request."
                    ),
                    focus="Constructive feedback: behaviour, impact, measurable request.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen feedback with measurable BIR-style requests.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce constructive feedback.",
                                instruction=(
                                    "Greet the learner and note they structured feedback yesterday. Explain in two sentences that B2+ feedback names behaviour, states impact, and makes a measurable request (by Friday, in the next two meetings). Ask what feedback they would give a teammate about lateness."
                                ),
                            ),
                            TeacherStep(
                                id="feedback_structure",
                                goal="Teach the feedback structure.",
                                instruction=(
                                    "Model When you…, it affects…, so please… with a measurable ask. Ask them to deliver one full behaviour-impact-request line."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has included a measurable request once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tfng_constructive_feedback_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TFNG",
                                activity="read",
                                task_widget="read_tfng",
                                topic_override="Behaviour, Impact, Request — true/false/not given",
                                generation_instructions=(
                                    "Write a 100–130 word passage (giving constructive feedback to a colleague) about Constructive feedback: behaviour, impact, measurable request. Provide 4–5 True/False/Not Given statements testing nuanced understanding of Constructive feedback: behaviour, impact, measurable request, including one subtle distractor. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tfng'. Provide passage_title, passage, and 4 items, each with prompt, correct_answer (True, False, or Not Given), and explanation."
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
                            id="listen_infer_constructive_feedback_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_INFER",
                                activity="listen",
                                task_widget="listen_infer",
                                topic_override="Behaviour, Impact, Request — listening inference",
                                generation_instructions=(
                                    "Generate a 50–70 word spoken exchange (giving constructive feedback to a colleague) where Constructive feedback: behaviour, impact, measurable request is implied. Ask 3 inference questions about stance, intent, or implied meaning tied to Constructive feedback: behaviour, impact, measurable request. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_infer'. Provide audio_script, intent_focus, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_email_constructive_feedback_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_EMAIL",
                                activity="write",
                                task_widget="write_email",
                                topic_override="Behaviour, Impact, Request — email writing",
                                generation_instructions=(
                                    "Ask for a short professional email (giving constructive feedback to a colleague) applying Constructive feedback: behaviour, impact, measurable request with appropriate opening, body moves, and close. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_email'. Provide prompt, grammar_rule, target_words, minimum_words 25, sample_answer (with To and Subject lines), and answer_hints."
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
                            id="speak_interview_constructive_feedback_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_INTERVIEW",
                                activity="speak",
                                task_widget="speak_interview",
                                topic_override="Behaviour, Impact, Request — interview",
                                generation_instructions=(
                                    "Interview prompts (giving constructive feedback to a colleague) where answers must demonstrate Constructive feedback: behaviour, impact, measurable request (stance, follow-ups, or documented feedback moves). B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_interview'. Provide interview_context, grammar_rule, target_words (That's wonderful, Oh no, How did, What about), 3 questions each with interviewer_prompt, sample_answer, and answer_hint, and speaking_duration_seconds: 35."
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
                depth_day=DaySource(
                    title="Risk, Mitigation & Clear Call",
                    description=(
                        "Building on yesterday's pros and cons, learners add risk, mitigation, and an explicit recommendation."
                    ),
                    focus="Pros/cons with risk, mitigation, and explicit recommendation.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen recommendations with risk and mitigation.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce pros, cons, and recommendations.",
                                instruction=(
                                    "Greet the learner and note they ordered pros and cons yesterday. Explain in two sentences that B2+ recommendations name one risk, one mitigation, and a clear call (I recommend X because…). Ask which option they are leaning toward in a current decision."
                                ),
                            ),
                            TeacherStep(
                                id="structure_order",
                                goal="Teach listing and recommending.",
                                instruction=(
                                    "Affirm their option. Ask for one risk and one mitigation before listing pros and cons."
                                ),
                            ),
                            TeacherStep(
                                id="add_recommendation",
                                goal="Add a clear recommendation.",
                                instruction=(
                                    "Ask them to close with an explicit recommendation and one reason in a single sentence."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has stated risk, mitigation, and a clear call once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_structure_pros_cons_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_STRUCTURE_ID",
                                activity="read",
                                task_widget="read_structure",
                                topic_override="Risk, Mitigation & Clear Call — text structure",
                                generation_instructions=(
                                    "Provide a 4–5 paragraph outline or short text (recommending a course of action to a team) about Pros/cons with risk, mitigation, and explicit recommendation. Ask the learner to identify structure elements (problem, cause, solution, recommendation) aligned with Pros/cons with risk, mitigation, and explicit recommendation. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_structure'. Provide passage_title, structure_labels ['Situation', 'Problem', 'Solution'], and 3 items, each with paragraph, correct_answer, and explanation."
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
                            id="listen_retell_pros_cons_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_RETELL",
                                activity="listen",
                                task_widget="listen_retell",
                                topic_override="Risk, Mitigation & Clear Call — listen and retell",
                                generation_instructions=(
                                    "Generate a 60–80 word monologue (recommending a course of action to a team) modeling Pros/cons with risk, mitigation, and explicit recommendation. Ask the learner to retell including the key depth moves from Pros/cons with risk, mitigation, and explicit recommendation. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_retell'. Provide audio_script, passage_to_retell, target_words (the situation was, the problem, so, as a result), and grammar_rule."
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
                            id="write_para_pros_cons_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Risk, Mitigation & Clear Call — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (recommending a course of action to a team) that must show Pros/cons with risk, mitigation, and explicit recommendation with clear organisation (topic sentence, support, close). B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paragraph'. Provide prompt, grammar_rule, target_words (first, the problem was, so, as a result, because), minimum_words 45, sample_answer, and answer_hints."
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
                            id="speak_opinion_pros_cons_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_OPINION",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Risk, Mitigation & Clear Call — opinion",
                                generation_instructions=(
                                    "Opinion task (recommending a course of action to a team): state a position, support with cause→impact→solution or measurable fix aligned with Pros/cons with risk, mitigation, and explicit recommendation. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_present'. Provide grammar_rule, target_words (I would suggest, because, the best way, however), a visual_prompt_description or prompt for the recommendation, and speaking_duration_seconds: 40."
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
                depth_day=DaySource(
                    title="Parking Lot & Action Owners",
                    description=(
                        "Building on yesterday's meeting language, learners use a parking lot for digressions and assign action owners."
                    ),
                    focus="Parking lot for digressions; action owners and next steps.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen meeting leadership with parking lot and owners.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce leading a meeting.",
                                instruction=(
                                    "Welcome the learner and note they practised agendas yesterday. Explain in two sentences that B2+ chairs park tangents (Let's put that in the parking lot) and close with owners (Alex will send… by Wednesday). Ask how they would open a 15-minute stand-up."
                                ),
                            ),
                            TeacherStep(
                                id="agenda_actions",
                                goal="Teach open and close phrases.",
                                instruction=(
                                    "Model parking one tangent and assigning one owner with a deadline. Ask them to park one topic and name who owns the next action."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used parking lot or an action owner once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_leading_meeting_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Parking Lot & Action Owners — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (leading a meeting with tangents) rich in Parking lot digressions and clear action owners. Add 3–4 comprehension MCQs where at least two require applying Parking lot digressions and clear action owners, not only locating a noun or date. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_mcq_leading_meeting_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Parking Lot & Action Owners — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (leading a meeting with tangents) using Parking lot digressions and clear action owners. Then 3–4 MCQs: at least two must test understanding of Parking lot digressions and clear action owners (form, stance, or structure), not single-fact recall. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_bullets_to_para_leading_meeting_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_BULLETS_TO_PARA",
                                activity="write",
                                task_widget="write_bullets_to_para",
                                topic_override="Parking Lot & Action Owners — bullets to paragraph",
                                generation_instructions=(
                                    "Provide bullet notes (leading a meeting with tangents) about Parking lot digressions and clear action owners; ask for one cohesive paragraph with owners, blockers, or next steps as required by the angle. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_bullets_to_para'. Provide bullets (4 work items), prompt, grammar_rule, target_words, minimum_words 25, sample_answer, and answer_hints."
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
                            id="speak_roleplay_leading_meeting_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_ROLEPLAY",
                                activity="speak",
                                task_widget="speak_roleplay",
                                topic_override="Parking Lot & Action Owners — roleplay",
                                generation_instructions=(
                                    "Roleplay (leading a meeting with tangents) where the learner must use Parking lot digressions and clear action owners in at least two turns; include a partner cue that elicits the depth move. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_roleplay'. Provide a dialogue_context alternating partner and learner turns, target_words (so far, on track, by Friday, next step), and speaking_duration_seconds: 30."
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
                depth_day=DaySource(
                    title="Evidence Stack & Concession",
                    description=(
                        "Building on yesterday's objection handling, learners stack evidence and concede fairly before pushing back."
                    ),
                    focus="Evidence stack with concession before rebuttal.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen objections with acknowledge + data + however.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce handling objections.",
                                instruction=(
                                    "Greet the learner and note they responded to objections yesterday. Explain in two sentences that B2+ depth concedes partly (That's fair…) then adds evidence (According to…, our data shows…). Ask what objection they hear often about their ideas."
                                ),
                            ),
                            TeacherStep(
                                id="respond_objection",
                                goal="Teach acknowledge-then-respond.",
                                instruction=(
                                    "Use their objection to model concession + two evidence points + however. Ask them to concede one fair point and cite one piece of evidence."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has conceded and cited evidence once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tfng_handling_objections_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TFNG",
                                activity="read",
                                task_widget="read_tfng",
                                topic_override="Evidence Stack & Concession — true/false/not given",
                                generation_instructions=(
                                    "Write a 100–130 word passage (handling objections in a proposal) about Acknowledge objection then stack evidence with concession. Provide 4–5 True/False/Not Given statements testing nuanced understanding of Acknowledge objection then stack evidence with concession, including one subtle distractor. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tfng'. Provide passage_title, passage, and 4 items, each with prompt, correct_answer (True, False, or Not Given), and explanation."
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
                            id="listen_infer_handling_objections_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_INFER",
                                activity="listen",
                                task_widget="listen_infer",
                                topic_override="Evidence Stack & Concession — listening inference",
                                generation_instructions=(
                                    "Generate a 50–70 word spoken exchange (handling objections in a proposal) where Acknowledge objection then stack evidence with concession is implied. Ask 3 inference questions about stance, intent, or implied meaning tied to Acknowledge objection then stack evidence with concession. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_infer'. Provide audio_script, intent_focus, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_idea_para_handling_objections_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_IDEA_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Evidence Stack & Concession — idea paragraph",
                                generation_instructions=(
                                    "Ask for a 90–120 word paragraph (handling objections in a proposal) arguing Acknowledge objection then stack evidence with concession with claim, evidence, and explicit recommendation. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paragraph'. Provide prompt, grammar_rule, target_words (I believe, because, for example, admittedly), minimum_words 25, sample_answer, and answer_hints."
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
                            id="speak_pic_desc_handling_objections_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Evidence Stack & Concession — picture description",
                                generation_instructions=(
                                    "Describe an image scene (handling objections in a proposal) using Acknowledge objection then stack evidence with concession in 4–5 connected sentences; include at least one depth-specific structure from Acknowledge objection then stack evidence with concession. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing a busy car park beside an empty bus lane, grammar_rule, and speaking_duration_seconds: 40."
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
                depth_day=DaySource(
                    title="Same Update, Two Audiences",
                    description=(
                        "Building on yesterday's stakeholder tone, learners deliver the same update for executive vs team audiences."
                    ),
                    focus="Same update rewritten for executive vs team tone.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen stakeholder communication with audience shift.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce stakeholder communication.",
                                instruction=(
                                    "Greet the learner and note they adjusted tone for stakeholders yesterday. Explain in two sentences that B2+ depth delivers one update twice: concise and outcome-focused for executives, collaborative detail for the team. Ask what project update they would share this week."
                                ),
                            ),
                            TeacherStep(
                                id="tone_detail",
                                goal="Teach tailoring tone and detail.",
                                instruction=(
                                    "Have them sketch one sentence for an executive (headline + impact) and one for the team (next steps + support needed). Ask them to contrast formality."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has contrasted two audience versions once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tone_id_stakeholder_w14_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Same Update, Two Audiences — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (a stakeholder update) demonstrating Same update rewritten for executive vs team tone. Ask the learner to identify tone/register problems or best repair choice. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tone_id'. Provide passage_title and 2 items, each with sender, message, prompt, options (Professional, Casual), correct_index, and explanation."
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
                            id="listen_tone_stakeholder_w14_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_TONE",
                                activity="listen",
                                task_widget="listen_tone",
                                topic_override="Same Update, Two Audiences — listening for tone",
                                generation_instructions=(
                                    "Generate two 30–40 word clips (a stakeholder update) showing contrasting tone for Same update rewritten for executive vs team tone. Ask which clip fits the required register and why. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_tone'. Provide audio_script and at least 1 MCQ item with prompt, options (Professional, Casual), correct_index, and explanation."
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
                            id="write_paraphrase_stakeholder_w14_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARAPHRASE",
                                activity="write",
                                task_widget="write_paraphrase",
                                topic_override="Same Update, Two Audiences — paraphrase",
                                generation_instructions=(
                                    "Give 3 source sentences (a stakeholder update) that are blunt, vague, or off-register; ask the learner to paraphrase for Same update rewritten for executive vs team tone. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paraphrase'. Provide 2 items, each with incorrect_sentence (the message to convert), sample_answer, and watch_hints."
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
                            id="speak_smalltalk_stakeholder_w14_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_SMALLTALK",
                                activity="speak",
                                task_widget="speak_smalltalk",
                                topic_override="Same Update, Two Audiences — small talk",
                                generation_instructions=(
                                    "Small-talk prompts (a stakeholder update) requiring Same update rewritten for executive vs team tone (echo, register shift, paraphrase, or inclusive invite) in natural replies. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_smalltalk'. Provide a dialogue_context alternating partner and learner turns, target_words (That sounds great, I might, probably, weekend), and speaking_duration_seconds: 35."
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
                depth_day=DaySource(
                    title="Synthesis Question & Decision Check",
                    description=(
                        "Building on yesterday's facilitation, learners synthesise three views with one question and confirm the decision."
                    ),
                    focus="Synthesis question after three views; explicit decision check.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen facilitation with synthesis and decision check.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce facilitating discussion.",
                                instruction=(
                                    "Welcome the learner and note they invited and summarised voices yesterday. Explain in two sentences that B2+ facilitation names three views, asks one synthesis question (What do we all agree is the main risk?), and checks the decision (So we're choosing X — does everyone commit?). Ask about a discussion they might chair soon."
                                ),
                            ),
                            TeacherStep(
                                id="invite_summarise",
                                goal="Teach invite and summarise phrases.",
                                instruction=(
                                    "Model summarising three positions briefly, then one synthesis question. Ask them to paraphrase two views and pose one synthesis question."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has synthesised or checked a decision once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_structure_facilitating_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_STRUCTURE_ID",
                                activity="read",
                                task_widget="read_structure",
                                topic_override="Synthesis Question & Decision Check — text structure",
                                generation_instructions=(
                                    "Provide a 4–5 paragraph outline or short text (facilitating a decision after multiple opinions) about Synthesize three views into a decision-check question. Ask the learner to identify structure elements (problem, cause, solution, recommendation) aligned with Synthesize three views into a decision-check question. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_structure'. Provide passage_title, structure_labels ['Opening', 'Building', 'Closing'], and 3 items, each with label, paragraph, correct_answer, and explanation."
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
                            id="listen_retell_facilitating_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_RETELL",
                                activity="listen",
                                task_widget="listen_retell",
                                topic_override="Synthesis Question & Decision Check — listen and retell",
                                generation_instructions=(
                                    "Generate a 60–80 word monologue (facilitating a decision after multiple opinions) modeling Synthesize three views into a decision-check question. Ask the learner to retell including the key depth moves from Synthesize three views into a decision-check question. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_retell'. Set response_mode to 'written'. Provide audio_script, passage_to_retell, target_words, and grammar_rule."
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
                            id="write_email_facilitating_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_EMAIL",
                                activity="write",
                                task_widget="write_email",
                                topic_override="Synthesis Question & Decision Check — email writing",
                                generation_instructions=(
                                    "Ask for a short professional email (facilitating a decision after multiple opinions) applying Synthesize three views into a decision-check question with appropriate opening, body moves, and close. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_email'. Provide prompt, grammar_rule, target_words, minimum_words 45, sample_answer (with To and Subject lines), and answer_hints."
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
                            id="speak_present_facilitating_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PRESENT",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Synthesis Question & Decision Check — presentation",
                                generation_instructions=(
                                    "Presentation task (facilitating a decision after multiple opinions): structured spoken segment showing Synthesize three views into a decision-check question with signposts and a clear close. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_present'. Provide grammar_rule, target_words (we discussed, on one hand, on the other hand, in the end), a visual_prompt_description, an optional model_presentation, and speaking_duration_seconds: 60."
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
    ),
    WeekSource(
        week_number=7,
        theme_type="vocabulary",
        cefr_level="B2",
        sub_level_min=6,
        sub_level_max=7,
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
                depth_day=DaySource(
                    title="Method & Limitation Phrases",
                    description=(
                        "Building on yesterday's science and research vocabulary, learners use method and limitation phrases (hypothesis, data, limitation) in a short research-style paragraph."
                    ),
                    focus="Method and limitation phrases in a research mini-paragraph.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen science lexis with method and limitation collocations.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce science and research words.",
                                instruction=(
                                    "Welcome the learner and note they practised hypothesis and experiment yesterday. Explain in two sentences that B2+ depth adds limitation phrases (the data suggest…, one limitation is…) in formal research tone. Ask what topic they would research."
                                ),
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more science and research words.",
                                instruction=(
                                    "Use their topic to model hypothesis → data → limitation in one chain. Ask them to add one limitation phrase to their idea."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used a limitation phrase once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_science_research_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Method & Limitation Phrases — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Hypothesis, data, and limitation phrases in research discourse and short definitions (a short research summary). Learners match each term to the definition that fits the depth collocation or usage. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_word_match'. Provide options (the environment words) and 4 items, each with prompt (the definition), correct_answer, and explanation."
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
                            id="listen_mcq_science_research_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Method & Limitation Phrases — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a short research summary) using Hypothesis, data, and limitation phrases in research discourse. Then 3–4 MCQs: at least two must test understanding of Hypothesis, data, and limitation phrases in research discourse (form, stance, or structure), not single-fact recall. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_sent_trans_science_research_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Method & Limitation Phrases — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a short research summary) where source and target practice Hypothesis, data, and limitation phrases in research discourse (e.g. direct to reported, active to passive, clause reduction). B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 2-3 items, each with source_sentence, sample_answer, and watch_hints."
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
                            id="speak_pic_desc_science_research_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Method & Limitation Phrases — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a short research summary) using Hypothesis, data, and limitation phrases in research discourse in 4–5 connected sentences; include at least one depth-specific structure from Hypothesis, data, and limitation phrases in research discourse. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing a wind farm beside a smoggy city skyline, grammar_rule, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Critique & Interpretation Chunks",
                    description=(
                        "Building on yesterday's arts vocabulary, learners use critique and interpretation chunks (exhibition, medium, curator) in evaluative speech."
                    ),
                    focus="Critique and interpretation chunks for exhibitions and media.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen arts lexis with critique and interpretation language.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce arts and creativity words.",
                                instruction=(
                                    "Greet the learner and note they worked on exhibition and medium yesterday. Explain in two sentences that B2+ critique uses interpretation chunks (the curator argues…, the medium suggests…). Ask about a recent exhibition or artwork."
                                ),
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more arts and creativity words.",
                                instruction=(
                                    "Affirm their example. Model one critique sentence with interpretation chunk and ask them to evaluate one design choice using medium or curator."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used a critique or interpretation chunk once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_arts_creativity_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Critique & Interpretation Chunks — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (reviewing an exhibition or creative work) using Arts critique and interpretation collocations. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Arts critique and interpretation collocations. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_context_mcq'. Provide passage_title, passage, and at least 1 MCQ item with prompt, options, correct_index, and explanation."
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
                            id="listen_dictation_arts_creativity_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Critique & Interpretation Chunks — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (reviewing an exhibition or creative work) that exemplify Arts critique and interpretation collocations for exact dictation. Each line should highlight one feature of Arts critique and interpretation collocations. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_dictation'. Provide audio_script, target_words (the key education words), and 1 dictation item with prompt, correct_answer, and explanation."
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
                            id="write_word_upgrade_arts_creativity_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_WORD_UPGRADE",
                                activity="write",
                                task_widget="write_word_upgrade",
                                topic_override="Critique & Interpretation Chunks — word upgrade",
                                generation_instructions=(
                                    "Give 3 informal or vague sentences (reviewing an exhibition or creative work); ask the learner to upgrade vocabulary to precise terms that express Arts critique and interpretation collocations. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_word_upgrade'. Provide 3 items, each with source_sentence, target_upgrade_word, sample_answer, and watch_hints."
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
                            id="speak_timed_arts_creativity_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Critique & Interpretation Chunks — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (reviewing an exhibition or creative work) each forcing production of Arts critique and interpretation collocations. Model answers must satisfy the prompt. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_timed'. Provide a single prompt, a sample_response, grammar_rule, target_words (enrol, assignment, revise, qualification), and speaking_duration_seconds: 60."
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
                depth_day=DaySource(
                    title="Stakeholder & Principle Language",
                    description=(
                        "Building on yesterday's ethics vocabulary, learners discuss global issues with stakeholder and principle language (rights, responsibility, equity)."
                    ),
                    focus="Stakeholder and principle language on ethics topics.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen ethics lexis with stakeholders and principles.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce ethics and global issues words.",
                                instruction=(
                                    "Greet the learner and note they discussed ethics and global issues yesterday. Explain in two sentences that B2+ depth names stakeholders and principles (stakeholders expect…, the principle of fairness…). Ask which global issue they care about."
                                ),
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more ethics and global issues words.",
                                instruction=(
                                    "Use their issue to model stakeholder + principle in one sentence. Ask them to name two stakeholders and one principle for that issue."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has named a stakeholder and principle once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_ethics_global_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Stakeholder & Principle Language — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Ethics and global issues: stakeholder and principle language and short definitions (an ethical dilemma or policy debate). Learners match each term to the definition that fits the depth collocation or usage. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_word_match'. Provide options (the culture words) and 4 items, each with prompt (the definition), correct_answer, and explanation."
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
                            id="listen_mcq_ethics_global_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Stakeholder & Principle Language — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (an ethical dilemma or policy debate) using Ethics and global issues: stakeholder and principle language. Then 3–4 MCQs: at least two must test understanding of Ethics and global issues: stakeholder and principle language (form, stance, or structure), not single-fact recall. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_para_ethics_global_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Stakeholder & Principle Language — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (an ethical dilemma or policy debate) that must show Ethics and global issues: stakeholder and principle language with clear organisation (topic sentence, support, close). B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paragraph'. Provide prompt, grammar_rule, target_words (tradition, community, heritage, celebrate), minimum_words 20, sample_answer, and answer_hints."
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
                            id="speak_pic_desc_ethics_global_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Stakeholder & Principle Language — picture description",
                                generation_instructions=(
                                    "Describe an image scene (an ethical dilemma or policy debate) using Ethics and global issues: stakeholder and principle language in 4–5 connected sentences; include at least one depth-specific structure from Ethics and global issues: stakeholder and principle language. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing a street festival with people in traditional dress, grammar_rule, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Forecast & Risk Brief",
                    description=(
                        "Building on yesterday's business vocabulary, learners deliver a short forecast and risk brief using revenue, volatility, and mitigation language."
                    ),
                    focus="Forecast and risk brief with revenue and volatility language.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen business lexis with forecast and risk framing.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce business and economics words.",
                                instruction=(
                                    "Greet the learner and note they practised business and economics words yesterday. Explain in two sentences that B2+ briefs pair forecasts (revenue is projected to…) with risks (volatility, downside). Ask what market or product they follow."
                                ),
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more business and economics words.",
                                instruction=(
                                    "React to their choice. Model one forecast line and one risk line with mitigation (we could hedge / diversify). Ask for a two-sentence mini-brief."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has given forecast and risk once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_business_economics_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Forecast & Risk Brief — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (an investor or board risk note) using Business forecast and risk brief vocabulary. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Business forecast and risk brief vocabulary. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_context_mcq'. Provide passage_title, passage, and at least 1 MCQ item with prompt, options, correct_index, and explanation."
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
                            id="listen_dictation_business_economics_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Forecast & Risk Brief — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (an investor or board risk note) that exemplify Business forecast and risk brief vocabulary for exact dictation. Each line should highlight one feature of Business forecast and risk brief vocabulary. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_dictation'. Provide audio_script, target_words (the key work words), and 1 dictation item with prompt, correct_answer, and explanation."
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
                            id="write_paraphrase_business_economics_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARAPHRASE",
                                activity="write",
                                task_widget="write_paraphrase",
                                topic_override="Forecast & Risk Brief — paraphrase",
                                generation_instructions=(
                                    "Give 3 source sentences (an investor or board risk note) that are blunt, vague, or off-register; ask the learner to paraphrase for Business forecast and risk brief vocabulary. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paraphrase'. Provide 2 items, each with incorrect_sentence (the plain sentence), sample_answer, and watch_hints."
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
                            id="speak_timed_business_economics_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Forecast & Risk Brief — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (an investor or board risk note) each forcing production of Business forecast and risk brief vocabulary. Model answers must satisfy the prompt. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_timed'. Provide a single prompt, a sample_response, grammar_rule, target_words (promote, resign, collaborate, deadline), and speaking_duration_seconds: 60."
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
                depth_day=DaySource(
                    title="Bias & Verification Steps",
                    description=(
                        "Building on yesterday's media literacy vocabulary, learners separate bias from fact with verification steps (source, corroborate, primary)."
                    ),
                    focus="Bias labels and verification steps for media claims.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen media literacy with bias and verification language.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce media literacy words.",
                                instruction=(
                                    "Greet the learner and note they worked on media and sources yesterday. Explain in two sentences that B2+ depth types sources and lists verification steps (check the primary source, corroborate with…). Ask about a headline they doubted."
                                ),
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more media literacy words.",
                                instruction=(
                                    "Use their headline to model bias label plus two verification steps. Ask them to say what they would check first and second."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has named bias or a verification step once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_media_literacy_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Bias & Verification Steps — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Media literacy: bias labels and verification steps and short definitions (evaluating an online news source). Learners match each term to the definition that fits the depth collocation or usage. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_word_match'. Provide options (the news words) and 4 items, each with prompt (the meaning), correct_answer, and explanation."
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
                            id="listen_mcq_media_literacy_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Bias & Verification Steps — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (evaluating an online news source) using Media literacy: bias labels and verification steps. Then 3–4 MCQs: at least two must test understanding of Media literacy: bias labels and verification steps (form, stance, or structure), not single-fact recall. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_sent_trans_media_literacy_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Bias & Verification Steps — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (evaluating an online news source) where source and target practice Media literacy: bias labels and verification steps (e.g. direct to reported, active to passive, clause reduction). B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 3 items, each with source_sentence, sample_answer, and watch_hints."
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
                            id="speak_pic_desc_media_literacy_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Bias & Verification Steps — picture description",
                                generation_instructions=(
                                    "Describe an image scene (evaluating an online news source) using Media literacy: bias labels and verification steps in 4–5 connected sentences; include at least one depth-specific structure from Media literacy: bias labels and verification steps. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing a news studio with a reporter and a headline on the screen, grammar_rule, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Delegate & Motivate in Message",
                    description=(
                        "Building on yesterday's leadership vocabulary, learners write a short message that delegates clearly and motivates the team."
                    ),
                    focus="Delegate and motivate in a leadership message.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen leadership lexis with delegate and motivate chunks.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce leadership and influence words.",
                                instruction=(
                                    "Greet the learner and note they practised vision and delegate yesterday. Explain in two sentences that B2+ messages assign owners (I'll delegate X to…) and motivate (thanks for…, this matters because…). Ask about a team task they lead."
                                ),
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more leadership and influence words.",
                                instruction=(
                                    "Use their task to model delegate + motivate in two sentences. Ask them to delegate one action with a deadline and add one motivating line."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has delegated and motivated once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_leadership_influence_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Delegate & Motivate in Message — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (a team note from a leader) using Leadership message: delegate and motivate with vision. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Leadership message: delegate and motivate with vision. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_context_mcq'. Provide passage_title, passage, and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_dictation_leadership_influence_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Delegate & Motivate in Message — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (a team note from a leader) that exemplify Leadership message: delegate and motivate with vision for exact dictation. Each line should highlight one feature of Leadership message: delegate and motivate with vision. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_dictation'. Provide audio_script, target_words (the quality words), and 2 dictation items, each with a prompt sentence containing a blank, correct_answer, and explanation."
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
                            id="write_word_upgrade_leadership_influence_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_WORD_UPGRADE",
                                activity="write",
                                task_widget="write_word_upgrade",
                                topic_override="Delegate & Motivate in Message — word upgrade",
                                generation_instructions=(
                                    "Give 3 informal or vague sentences (a team note from a leader); ask the learner to upgrade vocabulary to precise terms that express Leadership message: delegate and motivate with vision. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_word_upgrade'. Provide 3 items, each with source_sentence, target_upgrade_word, sample_answer, and watch_hints."
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
                            id="speak_timed_leadership_influence_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Delegate & Motivate in Message — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a team note from a leader) each forcing production of Leadership message: delegate and motivate with vision. Model answers must satisfy the prompt. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_timed'. Provide a single prompt, a sample_response, grammar_rule, target_words (integrity, resilience, perspective, empathy, ambition), and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Formal Argument Paragraph",
                    description=(
                        "Building on the week's vocabulary, learners recycle week 7 lexis in one formal argument paragraph across science, arts, ethics, business, media, and leadership topics."
                    ),
                    focus="Recycle week 7 lexis in one formal argument paragraph.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Consolidate week 7 vocabulary in a formal argument paragraph.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce review and word building words.",
                                instruction=(
                                    "Greet the learner for the vocabulary review depth day. Note they built lexis across science, arts, ethics, business, media, and leadership this week. Explain that today they weave those words into one formal argument paragraph. Ask for two words they will definitely include."
                                ),
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more review and word building words.",
                                instruction=(
                                    "Affirm their choices. Ask them to link two topics in one sentence (for example data limitation and stakeholder responsibility), then preview match, listening, paragraph, and timed recall."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has linked two topics once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_review_w15_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Formal Argument Paragraph — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Week 7 lexis in one formal argument paragraph and short definitions (a formal argument using week 7 vocabulary). Learners match each term to the definition that fits the depth collocation or usage. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_word_match'. Provide options (the 6 words) and 6 items, each with prompt (the definition), correct_answer, and explanation."
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
                            id="listen_mcq_review_w15_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Formal Argument Paragraph — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a formal argument using week 7 vocabulary) using Week 7 lexis in one formal argument paragraph. Then 3–4 MCQs: at least two must test understanding of Week 7 lexis in one formal argument paragraph (form, stance, or structure), not single-fact recall. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_para_review_w15_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Formal Argument Paragraph — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (a formal argument using week 7 vocabulary) that must show Week 7 lexis in one formal argument paragraph with clear organisation (topic sentence, support, close). B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_paragraph'. Provide prompt, grammar_rule, target_words (the week's words), minimum_words 25, sample_answer, and answer_hints."
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
                            id="speak_timed_review_w15_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Formal Argument Paragraph — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a formal argument using week 7 vocabulary) each forcing production of Week 7 lexis in one formal argument paragraph. Model answers must satisfy the prompt. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_timed'. Provide a single prompt, a sample_response, grammar_rule, target_words (the week's words), and speaking_duration_seconds: 90."
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
    ),
    WeekSource(
        week_number=8,
        theme_type="confidence",
        cefr_level="B2",
        sub_level_min=6,
        sub_level_max=7,
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
                depth_day=DaySource(
                    title="Stakes & Boundary Setting",
                    description=(
                        "Building on yesterday's difficult-conversation practice, learners set stakes and time boundaries before facilitating tense talks."
                    ),
                    focus="Name stakes and set time boundaries in difficult conversations.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen facilitation with purpose and boundary language.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction=(
                                    "Welcome the learner and note they practised ground rules yesterday. Explain in two sentences that B2+ depth names stakes (what matters here) and boundaries (we have 20 minutes; let's focus on X). Ask one situation where they must facilitate tension."
                                ),
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction=(
                                    "Affirm their situation. Model opening with purpose + time boundary and ask them to invite one respectful turn after naming the issue."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has set a boundary or named stakes once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_difficult_conv_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Stakes & Boundary Setting — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a high-stakes one-to-one conversation) rich in State stakes and set a time boundary in a difficult talk. Add 3–4 comprehension MCQs where at least two require applying State stakes and set a time boundary in a difficult talk, not only locating a noun or date. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_shadow_difficult_conv_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Stakes & Boundary Setting — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (a high-stakes one-to-one conversation) dense with State stakes and set a time boundary in a difficult talk for shadowing practice. Rhythm and phrasing should model natural B2+ delivery. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_shadow'. Provide audio_script, text_to_shadow (a sentence or two from the script), target_words, and grammar_rule."
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
                            id="write_sent_trans_difficult_conv_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Stakes & Boundary Setting — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a high-stakes one-to-one conversation) where source and target practice State stakes and set a time boundary in a difficult talk (e.g. direct to reported, active to passive, clause reduction). B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 3 items, each with source_sentence, sample_answer, and watch_hints."
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
                            id="speak_read_aloud_difficult_conv_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_READ_ALOUD",
                                activity="speak",
                                task_widget="read_aloud",
                                topic_override="Stakes & Boundary Setting — read aloud",
                                generation_instructions=(
                                    "Write a 50–60 word passage (a high-stakes one-to-one conversation) dense with State stakes and set a time boundary in a difficult talk for read-aloud; not an introductory lesson on the parent base form. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_aloud'. Provide text_to_read_aloud, grammar_rule about clear pronunciation and breathing pauses, target_words, and speaking_duration_seconds: 30."
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
                depth_day=DaySource(
                    title="Concede Partially Then Undermine",
                    description=(
                        "Building on yesterday's rebuttal work, learners concede partially (While it's true…) then undermine with however and evidence."
                    ),
                    focus="Partial concession then undermine with however-layer.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen rebuttals with concede-then-undermine structure.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction=(
                                    "Greet the learner and note they practised acknowledge-refute yesterday. Explain in two sentences that B2+ depth concedes fairly (While it's true…) then undermines with however and one evidence point. Ask for an opinion they defend at work."
                                ),
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction=(
                                    "Use their opinion. Model partial concession + however + evidence and ask them to concede one fair point then push back once."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has conceded partially and used however once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tone_id_counterarguments_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Concede Partially Then Undermine — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (responding to a strong counterargument) demonstrating While it's true…, however… partial concession then undermine. Ask the learner to identify tone/register problems or best repair choice. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tone_id'. Provide passage_title and 2 items, each with sender, message, prompt, options (Weak / Unsupported, Well-built / Supported), correct_index, and explanation."
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
                            id="listen_mcq_counterarguments_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Concede Partially Then Undermine — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (responding to a strong counterargument) using While it's true…, however… partial concession then undermine. Then 3–4 MCQs: at least two must test understanding of While it's true…, however… partial concession then undermine (form, stance, or structure), not single-fact recall. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and at least 1 MCQ item with prompt, options, correct_index, and explanation."
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
                            id="write_timed_counterarguments_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="Concede Partially Then Undermine — timed writing",
                                generation_instructions=(
                                    "Timed writing (responding to a strong counterargument): produce a structured response demonstrating While it's true…, however… partial concession then undermine within the time limit; include clear signposts or moves from the depth angle. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_timed'. Provide prompt, grammar_rule, target_words (I argue that, because, for instance, therefore), writing_duration_seconds: 180, sample_answer, and answer_hints."
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
                            id="speak_timed_counterarguments_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Concede Partially Then Undermine — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (responding to a strong counterargument) each forcing production of While it's true…, however… partial concession then undermine. Model answers must satisfy the prompt. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_timed'. Provide a single prompt, a sample_response, grammar_rule, target_words (I believe, because, for example, overall), and speaking_duration_seconds: 60."
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
                depth_day=DaySource(
                    title="Milestones & Metrics",
                    description=(
                        "Building on yesterday's vision language, learners narrate past milestones and future metrics in a vision story."
                    ),
                    focus="Past milestones and future metrics in a vision narrative.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen vision talks with measurable milestones.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction=(
                                    "Greet the learner and note they described vision yesterday. Explain in two sentences that B2+ vision stories anchor past milestones (By Q2 we had…) and future metrics (we aim to reach…). Ask for a goal they are pursuing."
                                ),
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction=(
                                    "Affirm the goal. Ask for one past milestone and one measurable metric with a timeframe, then preview today's integrated tasks."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has named a milestone and metric once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_vision_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Vision Narrative — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a vision narrative for a team or project) rich in Past-to-future vision with milestones and measurable metrics. Add 3–4 comprehension MCQs where at least two require applying Past-to-future vision with milestones and measurable metrics, not only locating a noun or date. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_tone_vision_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_TONE",
                                activity="listen",
                                task_widget="listen_tone",
                                topic_override="Vision Narrative — listening for tone",
                                generation_instructions=(
                                    "Generate two 30–40 word clips (a vision narrative for a team or project) showing contrasting tone for Past-to-future vision with milestones and measurable metrics. Ask which clip fits the required register and why. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_tone'. Provide two intros (each with id, label, speaker, audio_script) and 2 MCQ items, each with prompt, options (Unrealistic / Vague, Realistic / Grounded), correct_index, and explanation."
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
                            id="write_sent_trans_vision_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Vision Narrative — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a vision narrative for a team or project) where source and target practice Past-to-future vision with milestones and measurable metrics (e.g. direct to reported, active to passive, clause reduction). B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 3 items, each with source_sentence, sample_answer, and watch_hints."
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
                            id="speak_pic_desc_vision_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Vision Narrative — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a vision narrative for a team or project) using Past-to-future vision with milestones and measurable metrics in 4–5 connected sentences; include at least one depth-specific structure from Past-to-future vision with milestones and measurable metrics. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing a person studying late at a desk covered in plans, grammar_rule about speculative language, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Clarify & Paraphrase Under Challenge",
                    description=(
                        "Building on yesterday's critical feedback practice, learners clarify and paraphrase under challenge before responding."
                    ),
                    focus="Clarify and paraphrase before responding under challenge.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen critical feedback exchanges with clarify–paraphrase–respond.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction=(
                                    "Greet the learner and note they reframed avoidance language yesterday. Explain in two sentences that B2+ depth clarifies (Just to confirm…) and paraphrases (So you're saying…) before answering criticism. Ask what feedback feels hardest to hear."
                                ),
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction=(
                                    "Reassure them. Model clarify + paraphrase on sample criticism and ask them to paraphrase one point before giving a brief response."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has clarified or paraphrased once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tone_id_critical_feedback_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Clarify & Paraphrase Under Challenge — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (critical feedback exchange) demonstrating Structured clarify-and-paraphrase under challenge. Ask the learner to identify tone/register problems or best repair choice. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tone_id'. Provide passage_title and 2 items, each with sender, message, prompt, options describing tone shifts, correct_index, and explanation."
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
                            id="listen_shadow_critical_feedback_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Clarify & Paraphrase Under Challenge — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (critical feedback exchange) dense with Structured clarify-and-paraphrase under challenge for shadowing practice. Rhythm and phrasing should model natural B2+ delivery. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_shadow'. Provide audio_script, text_to_shadow, target_words (That's a fair point, I see what you mean, Let me explain), and grammar_rule."
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
                            id="write_timed_critical_feedback_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="Clarify & Paraphrase Under Challenge — timed writing",
                                generation_instructions=(
                                    "Timed writing (critical feedback exchange): produce a structured response demonstrating Structured clarify-and-paraphrase under challenge within the time limit; include clear signposts or moves from the depth angle. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_timed'. Provide prompt, grammar_rule, target_words (Usually, Instead of, In future), writing_duration_seconds: 180, sample_answer, and answer_hints."
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
                            id="speak_smalltalk_critical_feedback_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_SMALLTALK",
                                activity="speak",
                                task_widget="speak_smalltalk",
                                topic_override="Clarify & Paraphrase Under Challenge — small talk",
                                generation_instructions=(
                                    "Small-talk prompts (critical feedback exchange) requiring Structured clarify-and-paraphrase under challenge (echo, register shift, paraphrase, or inclusive invite) in natural replies. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_smalltalk'. Provide a dialogue_context alternating partner and learner turns, target_words (That's fair, I understand, even so), and speaking_duration_seconds: 30."
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
                depth_day=DaySource(
                    title="Urgency Without Pressure",
                    description=(
                        "Building on yesterday's strong-close practice, learners close with urgency that respects the listener (timeline + benefit, not pressure)."
                    ),
                    focus="Urgent close with timeline and benefit, without pressure.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen closes with urgency without aggressive pressure.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction=(
                                    "Greet the learner and note they practised call-to-action language yesterday. Explain in two sentences that B2+ closes add urgency with timeline and benefit (If we decide by Friday, we gain…) without pushy tone. Ask what they want someone to decide."
                                ),
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction=(
                                    "Use their decision. Model one urgent-but-respectful close, then ask them to add a timeline and one benefit in one sentence."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has used timeline and benefit once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_strong_close_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Strong Close & CTA — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (closing a pitch or proposal) rich in Urgency without pressure: timeline plus benefit. Add 3–4 comprehension MCQs where at least two require applying Urgency without pressure: timeline plus benefit, not only locating a noun or date. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_mcq_strong_close_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Strong Close & CTA — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (closing a pitch or proposal) using Urgency without pressure: timeline plus benefit. Then 3–4 MCQs: at least two must test understanding of Urgency without pressure: timeline plus benefit (form, stance, or structure), not single-fact recall. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_mcq'. Provide audio_script and 3 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_sent_trans_strong_close_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Strong Close & CTA — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (closing a pitch or proposal) where source and target practice Urgency without pressure: timeline plus benefit (e.g. direct to reported, active to passive, clause reduction). B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'sentence_transform'. Provide 3 items, each with source_sentence, sample_answer, and watch_hints."
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
                            id="speak_pic_desc_strong_close_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Strong Close & CTA — picture description",
                                generation_instructions=(
                                    "Describe an image scene (closing a pitch or proposal) using Urgency without pressure: timeline plus benefit in 4–5 connected sentences; include at least one depth-specific structure from Urgency without pressure: timeline plus benefit. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_pic_desc'. Provide image_alt describing an overflowing recycling area outside an office, grammar_rule, and speaking_duration_seconds: 45."
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
                depth_day=DaySource(
                    title="Bridge & Buy-Time Phrases",
                    description=(
                        "Building on yesterday's presentation Q&A, learners bridge tough questions to key messages and buy time politely."
                    ),
                    focus="Bridge and buy-time phrases in presentation Q&A.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Deepen Q&A with bridge and buy-time language.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction=(
                                    "Greet the learner and note they practised presentation Q&A yesterday. Explain in two sentences that B2+ Q&A bridges (That's an important question — the core issue is…) and buys time (Let me think for a moment…). Ask what hard question they fear in presentations."
                                ),
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction=(
                                    "Use their question. Model bridge + buy-time + short answer and ask them to try one bridge phrase toward their main message."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction=(
                                    "If the learner has bridged or bought time once, ask only: Ready to try the practice task?"
                                ),
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tone_id_presentation_qa_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Presentation Q&A — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (presentation Q&A after a talk) demonstrating Bridge and buy-time phrases for hard questions. Ask the learner to identify tone/register problems or best repair choice. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_tone_id'. Provide passage_title and 2 items, each with sender, message, prompt, options including Well-structured and clear and Rambling and unclear, correct_index, and explanation."
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
                            id="listen_tone_presentation_qa_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_TONE",
                                activity="listen",
                                task_widget="listen_tone",
                                topic_override="Presentation Q&A — listening for tone",
                                generation_instructions=(
                                    "Generate two 30–40 word clips (presentation Q&A after a talk) showing contrasting tone for Bridge and buy-time phrases for hard questions. Ask which clip fits the required register and why. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_tone'. Provide two intros (each with id, label, speaker, audio_script) and 2 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="write_timed_presentation_qa_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="Presentation Q&A — timed writing",
                                generation_instructions=(
                                    "Timed writing (presentation Q&A after a talk): produce a structured response demonstrating Bridge and buy-time phrases for hard questions within the time limit; include clear signposts or moves from the depth angle. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_timed'. Provide prompt, grammar_rule describing the intro-points-conclusion structure, target_words (To begin, My first point, secondly, to conclude), writing_duration_seconds: 180, sample_answer, and answer_hints."
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
                            id="speak_present_presentation_qa_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PRESENT",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Presentation Q&A — presentation",
                                generation_instructions=(
                                    "Presentation task (presentation Q&A after a talk): structured spoken segment showing Bridge and buy-time phrases for hard questions with signposts and a clear close. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_present'. Provide a visual_prompt_description outlining the intro, two points, and conclusion, an optional model_presentation, grammar_rule, target_words (To begin, firstly, secondly, to conclude), and speaking_duration_seconds: 90."
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
                depth_day=DaySource(
                    title="Chair + Pitch Combined",
                    description=(
                        "B2 confidence showcase depth: learners chair a short discussion and deliver a 45-second pitch close with less scaffold than the base day."
                    ),
                    focus="Integrated chairing plus pitch close with less scaffold.",
                    teacher=TeacherBlueprint(
                        lesson_goal="Showcase integrated B2 confidence: facilitate and pitch.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction=(
                                    "Greet the learner for the B2 showcase depth. Note they built difficult conversations, rebuttals, vision, and Q&A skills this week. Explain that today combines chairing with a 45-second pitch close and less scaffolding. Ask how their confidence changed this cycle."
                                ),
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction=(
                                    "Celebrate progress. Preview integrated reading, shadowing, timed writing, and debate with synthesis question, partial concession, and pitch close in one flow."
                                ),
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="Once the learner sounds ready, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_showcase_w16_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="B2 Showcase Depth — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (B2 showcase combining chairing and pitch) rich in Facilitate discussion then deliver a 45-second close. Add 3–4 comprehension MCQs where at least two require applying Facilitate discussion then deliver a 45-second close, not only locating a noun or date. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'read_comp_mcq'. Provide passage_title, passage, and 4 MCQ items, each with prompt, options, correct_index, and explanation."
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
                            id="listen_shadow_showcase_w16_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="B2 Showcase Depth — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (B2 showcase combining chairing and pitch) dense with Facilitate discussion then deliver a 45-second close for shadowing practice. Rhythm and phrasing should model natural B2+ delivery. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'listen_shadow'. Provide audio_script, text_to_shadow, target_words (proud of, growing, confidence), and grammar_rule about intonation."
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
                            id="write_timed_showcase_w16_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="B2 Showcase Depth — timed writing",
                                generation_instructions=(
                                    "Timed writing (B2 showcase combining chairing and pitch): produce a structured response demonstrating Facilitate discussion then deliver a 45-second close within the time limit; include clear signposts or moves from the depth angle. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'write_timed'. Provide prompt, grammar_rule, target_words (discovered, moreover, in the future), writing_duration_seconds: 180, sample_answer, and answer_hints."
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
                            id="speak_debate_showcase_w16_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_DEBATE",
                                activity="speak",
                                task_widget="speak_debate",
                                topic_override="B2 Showcase Depth — debate",
                                generation_instructions=(
                                    "Debate scenario (B2 showcase combining chairing and pitch) integrating Facilitate discussion then deliver a 45-second close: chair briefly, respond to one challenge, then deliver a timed closing statement. B2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Target widget 'speak_debate'. Provide a debate_context with an AI moderator turn, an AI opponent turn, and a learner turn, target_words (strongly believe, however, on the other hand), and speaking_duration_seconds: 60."
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
    ),
)
