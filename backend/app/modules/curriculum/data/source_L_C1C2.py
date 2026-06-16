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


# ── C1C2 band: source weeks 1-8 (C1 wk 1-4, C2 wk 5-8) ──

WEEKS_C1C2: tuple[WeekSource, ...] = (
    WeekSource(
        week_number=1,
        theme_type="grammar",
        cefr_level="C1",
        sub_level_min=8,
        sub_level_max=8,
        days=(
            DaySource(
                title="Narrative Tense Control - Mixing Past Forms in One Story",
                description=(
                    "Learners control narrative tense at B2: they mix past simple, past "
                    "perfect, and past perfect continuous in one coherent story without "
                    "losing the timeline."
                ),
                focus=(
                    "Narrative tense control: past simple, past perfect, and past perfect "
                    "continuous in one story."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach mixing past tenses for clear narrative timeline.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce narrative tense control.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that B2 narratives often mix "
                                "past simple for events, past perfect for earlier background, and past "
                                "perfect continuous for duration before a past moment. Ask them to tell "
                                "you one thing that happened at work last year."
                            ),
                        ),
                        TeacherStep(
                            id="mix_tenses",
                            goal="Teach mixing past forms.",
                            instruction=(
                                "Use their story to show when each tense fits (I had been working…, I had "
                                "finished…, then I left). Ask them to add one past perfect continuous "
                                "line to their story."
                            ),
                        ),
                        TeacherStep(
                            id="timeline",
                            goal="Keep the timeline clear.",
                            instruction=(
                                "Explain that each tense signals a different time layer. Ask them to say "
                                "one past simple sentence for the main event after their background."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has mixed at least two past forms, ask only: Ready to try "
                                "the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_cloze_narrative_tense",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CLOZE",
                            activity="read",
                            task_widget="fill_blanks",
                            topic_override="Narrative tense in a connected passage",
                            generation_instructions=(
                                "Write a 4-5 blank narrative passage mixing past simple, past perfect, "
                                "and past perfect continuous where each blank needs the best tense."
                            ),
                            widget_requirements=(
                                "Always include base_verb for verb-form blanks. Do not repeat base_verb "
                                "inline after each ___."
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
                        id="listen_mcq_narrative_tense",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Listening for tense shifts in narrative",
                            generation_instructions=(
                                "Generate a 70-100 word spoken story with clear tense shifts; include 3-4 "
                                "MCQs on timeline and tense choice."
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
                        id="write_narrative_tense_sentences",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_OPEN_SENT",
                            activity="write",
                            task_widget="open_text",
                            topic_override="Write sentences mixing past forms",
                            generation_instructions=(
                                "Ask for three sentences using past simple, past perfect, and past "
                                "perfect continuous about the same episode."
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
                        id="speak_narrative_tense_events",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Tell a short story with mixed past tenses",
                            generation_instructions=(
                                "Ask the learner to speak a 45-second story mixing all three past forms "
                                "with a clear timeline."
                            ),
                            widget_requirements=(
                                "Create exactly 3 speaking prompts. Include speaking_duration_seconds: "
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
                depth_day=DaySource(
                    title="Tense Shifts — Flashback & Commentary",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Controlled backstory shifts. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Controlled backstory shifts.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Tense Shifts — Flashback & Commentary: Controlled backstory shifts.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce narrative tense control.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that B2 narratives often mix past simple for events, past perfect for earlier background, and past perfect continuous for duration before a past moment. Ask them to say one sentence about something that happened at work last year.",
                            ),
                            TeacherStep(
                                id="mix_tenses",
                                goal="Teach mixing past forms.",
                                instruction="At C2 depth, push Controlled backstory shifts: Use their story to show when each tense fits (I had been working…, I had finished…, then I left). Ask them to add one past perfect continuous line to their story.",
                            ),
                            TeacherStep(
                                id="timeline",
                                goal="Keep the timeline clear.",
                                instruction="At C2 depth, push Controlled backstory shifts: Explain that each tense signals a different time layer. Ask them to say one past simple sentence for the main event after their background.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has mixed at least two past forms, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_cloze_narrative_tense_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CLOZE",
                                activity="read",
                                task_widget="fill_blanks",
                                topic_override="Tense Shifts — reading cloze",
                                generation_instructions=(
                                    "Write one connected 4–5-blank passage (a professional narrative with flashback layers) where every blank tests Controlled backstory tense shifts with brief commentary lines. Include at least two distinct facets of the depth angle in the passage. Do not drill only the parent base lesson pattern; the passage must read as a depth task on Tense Shifts. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_mcq_narrative_tense_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Tense Shifts — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a professional narrative with flashback layers) using Controlled backstory tense shifts with brief commentary lines. Then 3–4 MCQs: at least two must test understanding of Controlled backstory tense shifts with brief commentary lines (form, stance, or structure), not single-fact recall. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_narrative_tense_sentences_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_OPEN_SENT",
                                activity="write",
                                task_widget="open_text",
                                topic_override="Tense Shifts — open sentences",
                                generation_instructions=(
                                    "Ask for exactly 3 learner sentences (a professional narrative with flashback layers) that each demonstrate a different facet of Controlled backstory tense shifts with brief commentary lines. Do not ask for practice that only repeats the parent base lesson focus. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_narrative_tense_events_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Tense Shifts — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a professional narrative with flashback layers) each forcing production of Controlled backstory tense shifts with brief commentary lines. Model answers must satisfy the prompt. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
                                ),
                                widget_requirements="Create exactly 3 speaking prompts. Include speaking_duration_seconds: 45.",
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
                title="Mixed Conditionals - Past Condition, Present Result",
                description=(
                    "Learners use mixed conditionals where a past condition affects the "
                    "present (If I had studied harder, I would be more confident now) and "
                    "related time mismatches at B2 level."
                ),
                focus=(
                    "Mixed conditionals: past if-clause with present would result, and "
                    "related time mismatches."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach mixed conditionals linking past conditions to present results.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce mixed conditionals.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that mixed conditionals link "
                                "a past condition to a present result using if + past perfect and would + "
                                "base verb now. Ask what would be different today if they had made one "
                                "different choice last year."
                            ),
                        ),
                        TeacherStep(
                            id="past_present",
                            goal="Teach past → present pattern.",
                            instruction=(
                                "Model If I had…, I would… now with their idea. Ask them to finish 'If I "
                                "had known earlier, I would…' with a present result."
                            ),
                        ),
                        TeacherStep(
                            id="present_past",
                            goal="Teach present → past pattern briefly.",
                            instruction=(
                                "Show If I were more organised, I would have finished on time. Ask them "
                                "to make one sentence with were and would have."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has shown a mixed conditional at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_error_spot_mixed_conditional",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_ERROR_SPOT",
                            activity="read",
                            task_widget="error_spotting",
                            topic_override="Spot mixed conditional errors",
                            generation_instructions=(
                                "Generate a 5-sentence passage with mixed conditionals. Each sentence has "
                                "exactly one error (5 tokens): wrong tense in if-clause, wrong would "
                                "form, or time mismatch."
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
                        id="listen_cloze_mixed_conditional",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_CLOZE",
                            activity="listen",
                            task_widget="listen_cloze",
                            topic_override="Listen and fill mixed conditional forms",
                            generation_instructions=(
                                "Listen to the career reflection audio, then complete notes with missing "
                                "mixed-conditional phrases."
                            ),
                            widget_requirements=(
                                "Set inner_widget to 'fill_in_blanks'. Use the authored audio_script, "
                                "passage, and 5 BlankItems exactly as provided so rule-based scoring can "
                                "compare each typed verb phrase with correct_answer."
                            ),
                            static_payload={
                                "task_intro": "Listen, then complete the mixed-conditional notes.",
                                "instructions": "Play the audio once, then type the missing mixed-conditional verb "
                                "phrases in the paraphrased notes.",
                                "estimated_time_minutes": 3,
                                "inner_widget": "fill_in_blanks",
                                "audio_genre": "Reflective career monologue",
                                "audio_script": "Looking back, if I had taken that training course, I would be much "
                                "more confident in meetings now. If I were better at delegating, I "
                                "would have finished the project on time last month. If she had "
                                "accepted the offer, she would still be working here today. If they "
                                "had invested earlier, they would not be struggling with cash flow "
                                "now. If I had known about the policy change, I would understand the "
                                "new rules today.",
                                "passage_title": "Mixed Time Notes",
                                "passage": "If I ___ that training course, I would be much more confident now. If I "
                                "___ better at delegating, I would have finished on time last month. If "
                                "she ___ the offer, she would still be working here today. If they ___ "
                                "earlier, they would not be struggling now.",
                                "items": [
                                    {
                                        "item_id": "b1",
                                        "blank_id": "b1",
                                        "sentence_with_blank": "If I ___ that training course, I would be much "
                                        "more confident now.",
                                        "base_verb": "take",
                                        "correct_answer": "had taken",
                                        "distractors": ["took", "would take"],
                                        "options": ["had taken", "took", "would take"],
                                        "grammar_rule": "Past condition with present result: if + past perfect.",
                                        "explanation": "The past condition uses had taken.",
                                    },
                                    {
                                        "item_id": "b2",
                                        "blank_id": "b2",
                                        "sentence_with_blank": "If I ___ better at delegating, I would have "
                                        "finished on time last month.",
                                        "base_verb": "be",
                                        "correct_answer": "were",
                                        "distractors": ["was", "am"],
                                        "options": ["were", "was", "am"],
                                        "grammar_rule": "Present hypothetical with past result: if + past simple.",
                                        "explanation": "The if-clause uses were for a present hypothetical.",
                                    },
                                    {
                                        "item_id": "b3",
                                        "blank_id": "b3",
                                        "sentence_with_blank": "If she ___ the offer, she would still be working "
                                        "here today.",
                                        "base_verb": "accept",
                                        "correct_answer": "had accepted",
                                        "distractors": ["accepted", "accepts"],
                                        "options": [
                                            "had accepted",
                                            "accepted",
                                            "accepts",
                                        ],
                                        "grammar_rule": "Past condition with present result.",
                                        "explanation": "The if-clause needs had accepted.",
                                    },
                                    {
                                        "item_id": "b4",
                                        "blank_id": "b4",
                                        "sentence_with_blank": "If they ___ earlier, they would not be struggling "
                                        "now.",
                                        "base_verb": "invest",
                                        "correct_answer": "had invested",
                                        "distractors": ["invested", "invest"],
                                        "options": [
                                            "had invested",
                                            "invested",
                                            "invest",
                                        ],
                                        "grammar_rule": "Past condition with present result.",
                                        "explanation": "The if-clause needs had invested.",
                                    },
                                ],
                                "target_words_in_audio": [
                                    "had taken",
                                    "were",
                                    "had accepted",
                                    "had invested",
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
                        id="write_error_corr_mixed_conditional",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_ERROR_CORR",
                            activity="write",
                            task_widget="error_correction",
                            topic_override="Correct mixed conditional mistakes",
                            generation_instructions=(
                                "Give 3 sentences with one mixed conditional error each; ask the learner "
                                "to rewrite correctly."
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
                        id="speak_read_aloud_mixed_conditional",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_READ_ALOUD",
                            activity="speak",
                            task_widget="read_aloud",
                            topic_override="Read mixed conditional passage aloud",
                            generation_instructions=(
                                "Give a 55-70 word passage with mixed conditionals to read aloud."
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
                    title="Mixed Conditionals in Professional Advice",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: If I had…, I would… now. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: If I had…, I would… now.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Mixed Conditionals in Professional Advice: If I had…, I would… now.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce mixed conditionals.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that mixed conditionals link a past condition to a present result using if + past perfect and would + base verb now. Ask what would be different today if they had made one different choice last year.",
                            ),
                            TeacherStep(
                                id="past_present",
                                goal="Teach past → present pattern.",
                                instruction="At C2 depth, push If I had…, I would… now: Model If I had…, I would… now with their idea. Ask them to finish 'If I had known earlier, I would…' with a present result.",
                            ),
                            TeacherStep(
                                id="present_past",
                                goal="Teach present → past pattern briefly.",
                                instruction="At C2 depth, push If I had…, I would… now: Show If I were more organised, I would have finished on time. Ask them to make one sentence with were and would have.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has shown a mixed conditional at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_error_spot_mixed_conditional_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_ERROR_SPOT",
                                activity="read",
                                task_widget="error_spotting",
                                topic_override="Mixed Conditionals in Professional Advice — error spotting",
                                generation_instructions=(
                                    "Write a 5-sentence passage (a mentor advising a colleague on a past decision) with exactly five single-token errors, all illustrating If I had…, I would… now in professional advice. Diversify error types across sentences. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_cloze_mixed_conditional_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_CLOZE",
                                activity="listen",
                                task_widget="listen_cloze",
                                topic_override="Mixed Conditionals in Professional Advice — listen and complete",
                                generation_instructions=(
                                    "Create a 40–60 word audio script (a mentor advising a colleague on a past decision) dense with If I had…, I would… now in professional advice. Provide a gapped written version; blanks test If I had…, I would… now in professional advice only. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
                                ),
                                widget_requirements=(
                                    "Set inner_widget to 'fill_in_blanks'. Use the authored audio_script, passage, and 5 BlankItems exactly as provided so rule-based scoring can compare each typed verb phrase with correct_answer."
                                ),
                                static_payload={
                                    "task_intro": "Listen, then complete the mixed-conditional notes.",
                                    "instructions": "Play the audio once, then type the missing mixed-conditional verb phrases in the paraphrased notes.",
                                    "estimated_time_minutes": 3,
                                    "inner_widget": "fill_in_blanks",
                                    "audio_genre": "Reflective career monologue",
                                    "audio_script": "Looking back, if I had taken that training course, I would be much more confident in meetings now. If I were better at delegating, I would have finished the project on time last month. If she had accepted the offer, she would still be working here today. If they had invested earlier, they would not be struggling with cash flow now. If I had known about the policy change, I would understand the new rules today.",
                                    "passage_title": "Mixed Time Notes",
                                    "passage": "If I ___ that training course, I would be much more confident now. If I ___ better at delegating, I would have finished on time last month. If she ___ the offer, she would still be working here today. If they ___ earlier, they would not be struggling now.",
                                    "items": [
                                        {
                                            "item_id": "b1",
                                            "blank_id": "b1",
                                            "sentence_with_blank": "If I ___ that training course, I would be much more confident now.",
                                            "base_verb": "take",
                                            "correct_answer": "had taken",
                                            "distractors": ["took", "would take"],
                                            "options": [
                                                "had taken",
                                                "took",
                                                "would take",
                                            ],
                                            "grammar_rule": "Past condition with present result: if + past perfect.",
                                            "explanation": "The past condition uses had taken.",
                                        },
                                        {
                                            "item_id": "b2",
                                            "blank_id": "b2",
                                            "sentence_with_blank": "If I ___ better at delegating, I would have finished on time last month.",
                                            "base_verb": "be",
                                            "correct_answer": "were",
                                            "distractors": ["was", "am"],
                                            "options": ["were", "was", "am"],
                                            "grammar_rule": "Present hypothetical with past result: if + past simple.",
                                            "explanation": "The if-clause uses were for a present hypothetical.",
                                        },
                                        {
                                            "item_id": "b3",
                                            "blank_id": "b3",
                                            "sentence_with_blank": "If she ___ the offer, she would still be working here today.",
                                            "base_verb": "accept",
                                            "correct_answer": "had accepted",
                                            "distractors": ["accepted", "accepts"],
                                            "options": [
                                                "had accepted",
                                                "accepted",
                                                "accepts",
                                            ],
                                            "grammar_rule": "Past condition with present result.",
                                            "explanation": "The if-clause needs had accepted.",
                                        },
                                        {
                                            "item_id": "b4",
                                            "blank_id": "b4",
                                            "sentence_with_blank": "If they ___ earlier, they would not be struggling now.",
                                            "base_verb": "invest",
                                            "correct_answer": "had invested",
                                            "distractors": ["invested", "invest"],
                                            "options": [
                                                "had invested",
                                                "invested",
                                                "invest",
                                            ],
                                            "grammar_rule": "Past condition with present result.",
                                            "explanation": "The if-clause needs had invested.",
                                        },
                                    ],
                                    "target_words_in_audio": [
                                        "had taken",
                                        "were",
                                        "had accepted",
                                        "had invested",
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
                            id="write_error_corr_mixed_conditional_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_ERROR_CORR",
                                activity="write",
                                task_widget="error_correction",
                                topic_override="Mixed Conditionals in Professional Advice — error correction",
                                generation_instructions=(
                                    "Provide 3 sentences (a mentor advising a colleague on a past decision) with one error each, all tied to If I had…, I would… now in professional advice; the learner rewrites each correctly. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_read_aloud_mixed_conditional_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_READ_ALOUD",
                                activity="speak",
                                task_widget="read_aloud",
                                topic_override="Mixed Conditionals in Professional Advice — read aloud",
                                generation_instructions=(
                                    "Write a 50–60 word passage (a mentor advising a colleague on a past decision) dense with If I had…, I would… now in professional advice for read-aloud; not an introductory lesson on the parent base form. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Impersonal & Advanced Passive - It Is Said & Is Believed To",
                description=(
                    "Learners use impersonal and advanced passive patterns (It is said "
                    "that…, He is believed to have…, The decision was made…) typical of "
                    "news and reports at B2."
                ),
                focus=(
                    "Impersonal and advanced passive: It is said/claimed that, is "
                    "believed to have, and formal passives."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach impersonal and advanced passive for formal reporting.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce impersonal passive.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that formal English often "
                                "uses impersonal passives like It is said that or He is believed to have "
                                "to distance the writer from the claim. Ask them to report one rumour "
                                "they heard about their industry."
                            ),
                        ),
                        TeacherStep(
                            id="it_is_said",
                            goal="Teach It is said/claimed that.",
                            instruction=(
                                "Reframe their rumour as It is said that…. Ask them to add It is claimed "
                                "that with a different verb."
                            ),
                        ),
                        TeacherStep(
                            id="believed_to",
                            goal="Teach is believed to have.",
                            instruction=(
                                "Show He is believed to have left last week. Ask for one sentence about a "
                                "public figure using is thought to have."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used an impersonal passive at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_impersonal_passive",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Impersonal passive in a news-style text",
                            generation_instructions=(
                                "Write a 60-75 word news-style passage with It is said/claimed that and "
                                "is believed to have. Then comprehension MCQs."
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
                        id="listen_dictation_impersonal_passive",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="Hear impersonal passive chunks",
                            generation_instructions=(
                                "Generate a 35-45 word audio of four formal passive sentences for "
                                "dictation."
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
                        id="write_sent_trans_impersonal_passive",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Rewrite active claims into impersonal passive",
                            generation_instructions=(
                                "Give 3 direct claims and ask the learner to rewrite each using "
                                "impersonal or advanced passive."
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
                        id="speak_timed_impersonal_passive",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Report claims with impersonal passive aloud",
                            generation_instructions=(
                                "Ask the learner to say three impersonal passive sentences about recent "
                                "news in their field."
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
                    title="Reporting Chains — Said/Believed + Hedge",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Distance + stance. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Distance + stance.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Reporting Chains — Said/Believed + Hedge: Distance + stance.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce impersonal passive.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that formal English often uses impersonal passives like It is said that or He is believed to have to distance the writer from the claim. Ask them to report one rumour they heard about their industry.",
                            ),
                            TeacherStep(
                                id="it_is_said",
                                goal="Teach It is said/claimed that.",
                                instruction="At C2 depth, push Distance + stance: Reframe their rumour as It is said that…. Ask them to add It is claimed that with a different verb.",
                            ),
                            TeacherStep(
                                id="believed_to",
                                goal="Teach is believed to have.",
                                instruction="At C2 depth, push Distance + stance: Show He is believed to have left last week. Ask for one sentence about a public figure using is thought to have.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used an impersonal passive at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_impersonal_passive_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Reporting Chains — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a news-style report on contested findings) rich in Impersonal reporting chains with distance and hedging (said/believed). Add 3–4 comprehension MCQs where at least two require applying Impersonal reporting chains with distance and hedging (said/believed), not only locating a noun or date. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_dictation_impersonal_passive_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Reporting Chains — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (a news-style report on contested findings) that exemplify Impersonal reporting chains with distance and hedging (said/believed) for exact dictation. Each line should highlight one feature of Impersonal reporting chains with distance and hedging (said/believed). C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_sent_trans_impersonal_passive_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Reporting Chains — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a news-style report on contested findings) where source and target practice Impersonal reporting chains with distance and hedging (said/believed) (e.g. direct to reported, active to passive, clause reduction). C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_timed_impersonal_passive_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Reporting Chains — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a news-style report on contested findings) each forcing production of Impersonal reporting chains with distance and hedging (said/believed). Model answers must satisfy the prompt. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Participle & Adverbial Clauses - Having Finished & Although Tired",
                description=(
                    "Learners link ideas with participle clauses (Having finished…, "
                    "Written in 2020…) and adverbial clauses (Although tired, …) for "
                    "denser B2 sentences."
                ),
                focus=(
                    "Participle clauses and adverbial clauses: Having + past participle, "
                    "past participle fronting, Although/While."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach participle and adverbial clauses for dense formal sentences.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce participle and adverbial clauses.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that participle clauses "
                                "shorten sentences (Having finished the report, …) and adverbial clauses "
                                "add contrast (Although tired, …). Ask them to describe a busy day using "
                                "Although."
                            ),
                        ),
                        TeacherStep(
                            id="participle",
                            goal="Teach participle openers.",
                            instruction=(
                                "Model Having completed… and Written in…. Ask them to start one sentence "
                                "with Having + past participle about their work."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "Confirm with a short example (Although pressed for time, she agreed.) "
                                "then ask only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_match_participle_clauses",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Match clause types to their function",
                            generation_instructions=(
                                "Ask the learner to match sentence stubs to participle opener, adverbial "
                                "contrast, or main clause need."
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
                        id="listen_mcq_participle_clauses",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Hearing participle and adverbial clauses",
                            generation_instructions=(
                                "Generate a 35-45 word description using Having…, Although…, and a "
                                "participle fronting; include comprehension questions."
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
                        id="write_open_sent_participle_clauses",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_OPEN_SENT",
                            activity="write",
                            task_widget="open_text",
                            topic_override="Write sentences with participle and adverbial clauses",
                            generation_instructions=(
                                "Ask for three sentences: one Having-clause, one Although-clause, one "
                                "past participle fronting."
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
                        id="speak_pic_desc_participle_clauses",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a scene with dense clause openers",
                            generation_instructions=(
                                "Ask the learner to describe a workplace scene using at least two "
                                "participle or adverbial openers."
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
                    title="Combine Clauses Without Ambiguity",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Having/although density. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Having/although density.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Combine Clauses Without Ambiguity: Having/although density.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce participle and adverbial clauses.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that participle clauses shorten sentences (Having finished the report, …) and adverbial clauses add contrast (Although tired, …). Ask them to describe a busy day using Although.",
                            ),
                            TeacherStep(
                                id="participle",
                                goal="Teach participle openers.",
                                instruction="At C2 depth, push Having/although density: Model Having completed… and Written in…. Ask them to start one sentence with Having + past participle about their work.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="Confirm with a short example (Although pressed for time, she agreed.) then ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_participle_clauses_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Combine Clauses Without Ambiguity — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Having/although participle density without referent ambiguity and short definitions (a formal policy excerpt with dense clause combining). Learners match each term to the definition that fits the depth collocation or usage. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_mcq_participle_clauses_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Combine Clauses Without Ambiguity — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a formal policy excerpt with dense clause combining) using Having/although participle density without referent ambiguity. Then 3–4 MCQs: at least two must test understanding of Having/although participle density without referent ambiguity (form, stance, or structure), not single-fact recall. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_open_sent_participle_clauses_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_OPEN_SENT",
                                activity="write",
                                task_widget="open_text",
                                topic_override="Combine Clauses Without Ambiguity — open sentences",
                                generation_instructions=(
                                    "Ask for exactly 3 learner sentences (a formal policy excerpt with dense clause combining) that each demonstrate a different facet of Having/although participle density without referent ambiguity. Do not ask for practice that only repeats the parent base lesson focus. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_pic_desc_participle_clauses_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Combine Clauses Without Ambiguity — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a formal policy excerpt with dense clause combining) using Having/although participle density without referent ambiguity in 4–5 connected sentences; include at least one depth-specific structure from Having/although participle density without referent ambiguity. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Stance & Distancing in Reporting - It Is Argued That",
                description=(
                    "Learners report claims with stance and distance (It is argued that…, "
                    "According to…, The report suggests that…) without stating opinion as "
                    "fact."
                ),
                focus=(
                    "Stance and distancing: It is argued/claimed/suggested that, "
                    "According to, and neutral reporting."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach stance markers and distancing in reporting.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce stance in reporting.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that B2 reporting uses "
                                "stance phrases like It is argued that or According to to show who claims "
                                "something without endorsing it. Ask them to summarise a debate they read "
                                "recently."
                            ),
                        ),
                        TeacherStep(
                            id="stance_phrases",
                            goal="Teach stance phrases.",
                            instruction=(
                                "Model It is argued that and The data suggests that. Ask them to report "
                                "one claim using According to a recent study."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has distanced a claim at least once, ask only: Ready to "
                                "try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_cloze_stance_reporting",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CLOZE",
                            activity="read",
                            task_widget="fill_blanks",
                            topic_override="Stance markers in reporting blanks",
                            generation_instructions=(
                                "Write a 4-5 sentence report with blanks for argued, claimed, suggested, "
                                "According to."
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
                        id="listen_infer_stance_reporting",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Infer claims behind stance phrases",
                            generation_instructions=(
                                "Generate a 35-45 word audio using stance phrases; ask inference "
                                "questions on who claims what."
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
                        id="write_para_stance_reporting",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write a paragraph with stance and distancing",
                            generation_instructions=(
                                "Ask for a 3-4 sentence paragraph reporting a topic with at least three "
                                "stance/distancing phrases."
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
                        id="speak_roleplay_stance_reporting",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Pass on a reported claim in roleplay",
                            generation_instructions=(
                                "Set up a roleplay passing on what experts argued using stance phrases in "
                                "2-3 connected sentences."
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
                    title="Weak vs Strong Reporting Verbs",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: argue/claim/suggest. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: argue/claim/suggest.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Weak vs Strong Reporting Verbs: argue/claim/suggest.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce stance in reporting.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that B2 reporting uses stance phrases like It is argued that or According to to show who claims something without endorsing it. Ask them to summarise a debate they read recently.",
                            ),
                            TeacherStep(
                                id="stance_phrases",
                                goal="Teach stance phrases.",
                                instruction="At C2 depth, push argue/claim/suggest: Model It is argued that and The data suggests that. Ask them to report one claim using According to a recent study.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has distanced a claim at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_cloze_stance_reporting_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CLOZE",
                                activity="read",
                                task_widget="fill_blanks",
                                topic_override="Weak vs Strong Reporting Verbs — reading cloze",
                                generation_instructions=(
                                    "Write one connected 4–5-blank passage (a disputed workplace or media account) where every blank tests Weak vs strong reporting verbs (argue/claim/suggest) and distancing phrases. Include at least two distinct facets of the depth angle in the passage. Do not drill only the parent base lesson pattern; the passage must read as a depth task on Weak vs Strong Reporting Verbs. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_infer_stance_reporting_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_INFER",
                                activity="listen",
                                task_widget="listen_infer",
                                topic_override="Weak vs Strong Reporting Verbs — listening inference",
                                generation_instructions=(
                                    "Generate a 50–70 word spoken exchange (a disputed workplace or media account) where Weak vs strong reporting verbs (argue/claim/suggest) and distancing phrases is implied. Ask 3 inference questions about stance, intent, or implied meaning tied to Weak vs strong reporting verbs (argue/claim/suggest) and distancing phrases. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_para_stance_reporting_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Weak vs Strong Reporting Verbs — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (a disputed workplace or media account) that must show Weak vs strong reporting verbs (argue/claim/suggest) and distancing phrases with clear organisation (topic sentence, support, close). C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_roleplay_stance_reporting_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_ROLEPLAY",
                                activity="speak",
                                task_widget="speak_roleplay",
                                topic_override="Weak vs Strong Reporting Verbs — roleplay",
                                generation_instructions=(
                                    "Roleplay (a disputed workplace or media account) where the learner must use Weak vs strong reporting verbs (argue/claim/suggest) and distancing phrases in at least two turns; include a partner cue that elicits the depth move. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Inversion for Emphasis - Never Have I & Had I Known",
                description=(
                    "Learners use inversion for emphasis (Never have I…, Had I known…, "
                    "Not only… but also…) in formal and rhetorical B2 English."
                ),
                focus=(
                    "Inversion for emphasis: Never have I, Had I known, Not only…but "
                    "also, and formal negative inversion."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach inversion patterns for emphasis and rhetoric.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce inversion for emphasis.",
                            instruction=(
                                "Greet the learner and note this is the rhetoric day of grammar week. "
                                "Explain in two sentences that inversion puts emphasis on an idea (Never "
                                "have I seen…, Had I known…). Ask when they last felt surprised at work."
                            ),
                        ),
                        TeacherStep(
                            id="never_had",
                            goal="Teach Never have I and Had I.",
                            instruction=(
                                "Model Never have I… and Had I known…. Ask them to say one Never have I "
                                "sentence about their field."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used inversion at least once, ask only: Ready to try "
                                "the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_inversion",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="Inversion patterns in text",
                            generation_instructions=(
                                "Write a short profile using Never have I, Had I known, and Not only… but "
                                "also. Then True/False/Not Given items."
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
                        id="listen_shadow_inversion",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Shadow inverted emphasis phrases",
                            generation_instructions=(
                                "Generate a 20-second monologue with inverted phrases for shadowing."
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
                        id="write_email_inversion",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Email using one inversion for emphasis",
                            generation_instructions=(
                                "Ask the learner to write a short email using Had I known and one Never "
                                "have I line."
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
                        id="speak_smalltalk_inversion",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Casual chat closing with a Not only line",
                            generation_instructions=(
                                "Set up small talk where the learner ends with one Not only… but also "
                                "sentence."
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
                    title="Formal Emphasis — Never/Had I",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Rhetoric lines. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Rhetoric lines.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Formal Emphasis — Never/Had I: Rhetoric lines.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce inversion for emphasis.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner and note this is the rhetoric day of grammar week. Explain in two sentences that inversion puts emphasis on an idea (Never have I seen…, Had I known…). Ask when they last felt surprised at work.",
                            ),
                            TeacherStep(
                                id="never_had",
                                goal="Teach Never have I and Had I.",
                                instruction="At C2 depth, push Rhetoric lines: Model Never have I… and Had I known…. Ask them to say one Never have I sentence about their field.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used inversion at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tfng_inversion_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TFNG",
                                activity="read",
                                task_widget="read_tfng",
                                topic_override="Formal Emphasis — true/false/not given",
                                generation_instructions=(
                                    "Write a 100–130 word passage (a formal speech or editorial opening) about Never/Had I formal inversion for rhetorical emphasis. Provide 4–5 True/False/Not Given statements testing nuanced understanding of Never/Had I formal inversion for rhetorical emphasis, including one subtle distractor. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_shadow_inversion_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Formal Emphasis — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (a formal speech or editorial opening) dense with Never/Had I formal inversion for rhetorical emphasis for shadowing practice. Rhythm and phrasing should model natural C2 delivery. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_email_inversion_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_EMAIL",
                                activity="write",
                                task_widget="write_email",
                                topic_override="Formal Emphasis — email writing",
                                generation_instructions=(
                                    "Ask for a short professional email (a formal speech or editorial opening) applying Never/Had I formal inversion for rhetorical emphasis with appropriate opening, body moves, and close. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_smalltalk_inversion_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_SMALLTALK",
                                activity="speak",
                                task_widget="speak_smalltalk",
                                topic_override="Formal Emphasis — small talk",
                                generation_instructions=(
                                    "Small-talk prompts (a formal speech or editorial opening) requiring Never/Had I formal inversion for rhetorical emphasis (echo, register shift, paraphrase, or inclusive invite) in natural replies. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Academic & Professional Cohesion - Thereby, Thus & In Light Of",
                description=(
                    "Learners connect formal arguments with cohesive linkers (thereby, "
                    "thus, consequently, in light of, with regard to) at B2 level."
                ),
                focus=(
                    "Academic and professional cohesion: thereby, thus, consequently, in "
                    "light of, with regard to."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach formal cohesive linkers for B2 argument writing.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce formal cohesion.",
                            instruction=(
                                "Greet the learner and note this is the final grammar day of the cycle. "
                                "Explain in two sentences that formal linkers like thereby and in light "
                                "of connect reasons and conclusions in reports. Ask them to finish 'In "
                                "light of recent data, ___.'"
                            ),
                        ),
                        TeacherStep(
                            id="linkers",
                            goal="Teach thereby and with regard to.",
                            instruction=(
                                "Confirm their sentence. Explain thereby for result and with regard to "
                                "for topic focus. Ask them to use consequently in one sentence."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a formal linker at least once, ask only: Ready "
                                "to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_context_mcq_cohesion",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Formal cohesion in a report excerpt",
                            generation_instructions=(
                                "Write a short report excerpt with gaps for thereby, thus, in light of, "
                                "with regard to. MCQs on best linker."
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
                        id="listen_retell_cohesion",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Retell a signposted mini-briefing",
                            generation_instructions=(
                                "Generate a 40-50 word formal audio with cohesive linkers; ask retell "
                                "with two linkers."
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
                        id="write_paraphrase_cohesion",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="Paraphrase with cohesive linkers",
                            generation_instructions=(
                                "Give informal sentences; ask the learner to join them using thereby, "
                                "consequently, or in light of."
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
                        id="speak_present_cohesion",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Short talk using formal linkers",
                            generation_instructions=(
                                "Ask for a 45-second mini presentation using at least two formal cohesive "
                                "linkers."
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
                    title="Thereby / In Light Of in Proposal",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: 6-sentence proposal. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: 6-sentence proposal.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Thereby / In Light Of in Proposal: 6-sentence proposal.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce formal cohesion.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner and note this is the final grammar day of the cycle. Explain in two sentences that formal linkers like thereby and in light of connect reasons and conclusions in reports. Ask them to finish 'In light of recent data, ___.'",
                            ),
                            TeacherStep(
                                id="linkers",
                                goal="Teach thereby and with regard to.",
                                instruction="At C2 depth, push 6-sentence proposal: Confirm their sentence. Explain thereby for result and with regard to for topic focus. Ask them to use consequently in one sentence.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a formal linker at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_cohesion_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Thereby / In Light Of in Proposal — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (a short academic or business proposal) using Thereby / in light of cohesion in a six-sentence proposal. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Thereby / in light of cohesion in a six-sentence proposal. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_retell_cohesion_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_RETELL",
                                activity="listen",
                                task_widget="listen_retell",
                                topic_override="Thereby / In Light Of in Proposal — listen and retell",
                                generation_instructions=(
                                    "Generate a 60–80 word monologue (a short academic or business proposal) modeling Thereby / in light of cohesion in a six-sentence proposal. Ask the learner to retell including the key depth moves from Thereby / in light of cohesion in a six-sentence proposal. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_paraphrase_cohesion_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARAPHRASE",
                                activity="write",
                                task_widget="write_paraphrase",
                                topic_override="Thereby / In Light Of in Proposal — paraphrase",
                                generation_instructions=(
                                    "Give 3 source sentences (a short academic or business proposal) that are blunt, vague, or off-register; ask the learner to paraphrase for Thereby / in light of cohesion in a six-sentence proposal. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_present_cohesion_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PRESENT",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Thereby / In Light Of in Proposal — presentation",
                                generation_instructions=(
                                    "Presentation task (a short academic or business proposal): structured spoken segment showing Thereby / in light of cohesion in a six-sentence proposal with signposts and a clear close. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
        cefr_level="C1",
        sub_level_min=8,
        sub_level_max=8,
        days=(
            DaySource(
                title="Diplomatic Mediation - Neutral Language & Workable Outcomes",
                description=(
                    "Learners practise diplomatic mediation with neutral language and a "
                    "workable outcome for both sides at B2 level using the same "
                    "read-listen-write-speak sequence as earlier communication weeks."
                ),
                focus=(
                    "Diplomatic mediation with neutral language and a workable outcome "
                    "for both sides."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach diplomatic mediation between two sides.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce diplomatic mediation.",
                            instruction=(
                                "Welcome the learner to communication week. Explain in two sentences that "
                                "mediation uses neutral language to help two sides reach a workable "
                                "outcome. Ask them to describe a disagreement they helped calm."
                            ),
                        ),
                        TeacherStep(
                            id="diplomatic_mediation",
                            goal="Teach diplomatic mediation.",
                            instruction=(
                                "React warmly. Teach phrases like 'I hear both of you' and 'What would a "
                                "workable middle ground look like?'. Ask them to propose one neutral next "
                                "step."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_diplomatic_mediation",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Mediation in messages",
                            generation_instructions=(
                                "Write a mediation exchange with neutral language and a workable outcome. "
                                "Comprehension questions."
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
                        id="listen_mcq_diplomatic_mediation",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Listening to mediation dialogue",
                            generation_instructions=(
                                "Generate a 35-45 word mediation dialogue. MCQs on each side's underlying "
                                "need."
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
                        id="write_sent_trans_diplomatic_mediation",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Polite mediation phrases",
                            generation_instructions=(
                                "Give 3 positional statements to rewrite using neutral mediation phrases."
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
                        id="speak_roleplay_diplomatic_mediation",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Roleplay diplomatic mediation",
                            generation_instructions=(
                                "Roleplay diplomatic mediation between two colleagues with a shared next "
                                "step."
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
                    title="Interests, Options & Face-Saving",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Behind positions. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Behind positions.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Interests, Options & Face-Saving: Behind positions.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce diplomatic mediation.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to communication week. Explain in two sentences that mediation uses neutral language to help two sides reach a workable outcome. Ask them to describe a disagreement they helped calm.",
                            ),
                            TeacherStep(
                                id="diplomatic_mediation",
                                goal="Teach diplomatic mediation.",
                                instruction="At C2 depth, push Behind positions: React warmly. Teach phrases like 'I hear both of you' and 'What would a workable middle ground look like?'. Ask them to propose one neutral next step.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_diplomatic_mediation_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Interests, Options & Face-Saving — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a diplomatic mediation between two parties) rich in Interests and options behind positions with face-saving language. Add 3–4 comprehension MCQs where at least two require applying Interests and options behind positions with face-saving language, not only locating a noun or date. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_mcq_diplomatic_mediation_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Interests, Options & Face-Saving — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a diplomatic mediation between two parties) using Interests and options behind positions with face-saving language. Then 3–4 MCQs: at least two must test understanding of Interests and options behind positions with face-saving language (form, stance, or structure), not single-fact recall. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_sent_trans_diplomatic_mediation_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Interests, Options & Face-Saving — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a diplomatic mediation between two parties) where source and target practice Interests and options behind positions with face-saving language (e.g. direct to reported, active to passive, clause reduction). C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_roleplay_diplomatic_mediation_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_ROLEPLAY",
                                activity="speak",
                                task_widget="speak_roleplay",
                                topic_override="Interests, Options & Face-Saving — roleplay",
                                generation_instructions=(
                                    "Roleplay (a diplomatic mediation between two parties) where the learner must use Interests and options behind positions with face-saving language in at least two turns; include a partner cue that elicits the depth move. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Upward & Sensitive Feedback - Managers, Seniors & Clients",
                description=(
                    "Learners practise upward and sensitive feedback to a manager, senior "
                    "peer, or client at B2 level using the same read-listen-write-speak "
                    "sequence as earlier communication weeks."
                ),
                focus="Upward and sensitive feedback to a manager, senior peer, or client.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach upward and sensitive feedback.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce upward & sensitive feedback.",
                            instruction=(
                                "Welcome the learner to Day 2. Explain in two sentences that upward "
                                "feedback must be respectful, specific, and focused on behaviour not "
                                "character. Ask about feedback they need to give upward soon."
                            ),
                        ),
                        TeacherStep(
                            id="upward_feedback",
                            goal="Teach upward feedback.",
                            instruction=(
                                "Model 'I appreciate… / One concern is… / Could we explore…'. Ask them to "
                                "give brief upward feedback on a late decision."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_upward_feedback",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="Sensitive feedback in writing",
                            generation_instructions=(
                                "Write a message giving upward feedback respectfully. True/False/Not "
                                "Given on tone."
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
                        id="listen_infer_upward_feedback",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Infer tone in upward feedback",
                            generation_instructions=(
                                "Generate a conversation with upward feedback; infer whether it builds "
                                "trust."
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
                        id="write_email_upward_feedback",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Write upward feedback",
                            generation_instructions=(
                                "Ask the learner to write upward feedback with appreciation, concern, and "
                                "a request."
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
                        id="speak_interview_upward_feedback",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_INTERVIEW",
                            activity="speak",
                            task_widget="speak_interview",
                            topic_override="React with upward feedback in chat",
                            generation_instructions=(
                                "Mini interview: respond with upward feedback on a sensitive topic."
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
                    title="Request, Deliver, Document",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Sensitive upward msg. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Sensitive upward msg.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Request, Deliver, Document: Sensitive upward msg.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce upward & sensitive feedback.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to Day 2. Explain in two sentences that upward feedback must be respectful, specific, and focused on behaviour not character. Ask about feedback they need to give upward soon.",
                            ),
                            TeacherStep(
                                id="upward_feedback",
                                goal="Teach upward feedback.",
                                instruction="At C2 depth, push Sensitive upward msg: Model 'I appreciate… / One concern is… / Could we explore…'. Ask them to give brief upward feedback on a late decision.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tfng_upward_feedback_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TFNG",
                                activity="read",
                                task_widget="read_tfng",
                                topic_override="Request, Deliver, Document — true/false/not given",
                                generation_instructions=(
                                    "Write a 100–130 word passage (an upward feedback exchange with a senior manager) about Request, deliver, and document structure for sensitive upward messages. Provide 4–5 True/False/Not Given statements testing nuanced understanding of Request, deliver, and document structure for sensitive upward messages, including one subtle distractor. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_infer_upward_feedback_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_INFER",
                                activity="listen",
                                task_widget="listen_infer",
                                topic_override="Request, Deliver, Document — listening inference",
                                generation_instructions=(
                                    "Generate a 50–70 word spoken exchange (an upward feedback exchange with a senior manager) where Request, deliver, and document structure for sensitive upward messages is implied. Ask 3 inference questions about stance, intent, or implied meaning tied to Request, deliver, and document structure for sensitive upward messages. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_email_upward_feedback_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_EMAIL",
                                activity="write",
                                task_widget="write_email",
                                topic_override="Request, Deliver, Document — email writing",
                                generation_instructions=(
                                    "Ask for a short professional email (an upward feedback exchange with a senior manager) applying Request, deliver, and document structure for sensitive upward messages with appropriate opening, body moves, and close. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_interview_upward_feedback_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_INTERVIEW",
                                activity="speak",
                                task_widget="speak_interview",
                                topic_override="Request, Deliver, Document — interview",
                                generation_instructions=(
                                    "Interview prompts (an upward feedback exchange with a senior manager) where answers must demonstrate Request, deliver, and document structure for sensitive upward messages (stance, follow-ups, or documented feedback moves). C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Strategic Recommendation - Options, Risks & Mitigation",
                description=(
                    "Learners practise strategic recommendations with options, risks, "
                    "mitigation, and a clear recommendation at B2 level using the same "
                    "read-listen-write-speak sequence as earlier communication weeks."
                ),
                focus=(
                    "Strategic recommendations with options, risks, mitigation, and a "
                    "clear recommendation."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach strategic recommendations with risks and mitigation.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce strategic recommendation.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that strategic "
                                "recommendations present options, risks, mitigation, and a clear "
                                "preferred choice. Ask them to compare two options they know at work."
                            ),
                        ),
                        TeacherStep(
                            id="strategic_recommendation",
                            goal="Teach strategic recommendation.",
                            instruction=(
                                "Introduce On balance, I recommend… and The main risk is… with "
                                "mitigation. Ask them to recommend one option with one risk and "
                                "mitigation."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_structure_strategic_recommendation",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_STRUCTURE_ID",
                            activity="read",
                            task_widget="read_structure",
                            topic_override="Strategic recommendation structure",
                            generation_instructions=(
                                "Provide a strategic comparison text; label Options, Risks, Mitigation, "
                                "Recommendation."
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
                        id="listen_retell_strategic_recommendation",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Retell a strategic recommendation",
                            generation_instructions=(
                                "Audio comparing options with risks and mitigation; retell the "
                                "recommendation."
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
                        id="write_para_strategic_recommendation",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write recommendation with risks",
                            generation_instructions=(
                                "Write a paragraph recommending one option with risks and mitigation."
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
                        id="speak_opinion_strategic_recommendation",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_OPINION",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="State a strategic recommendation aloud",
                            generation_instructions=(
                                "Speak for 45 seconds with a clear strategic recommendation."
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
                    title="Scenario Tree & Residual Risk",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Options + risk language. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Options + risk language.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Scenario Tree & Residual Risk: Options + risk language.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce strategic recommendation.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that strategic recommendations present options, risks, mitigation, and a clear preferred choice. Ask them to compare two options they know at work.",
                            ),
                            TeacherStep(
                                id="strategic_recommendation",
                                goal="Teach strategic recommendation.",
                                instruction="At C2 depth, push Options + risk language: Introduce On balance, I recommend… and The main risk is… with mitigation. Ask them to recommend one option with one risk and mitigation.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_structure_strategic_recommendation_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_STRUCTURE_ID",
                                activity="read",
                                task_widget="read_structure",
                                topic_override="Scenario Tree & Residual Risk — text structure",
                                generation_instructions=(
                                    "Provide a 4–5 paragraph outline or short text (a strategic recommendation to leadership) about Scenario tree with options and residual risk language. Ask the learner to identify structure elements (problem, cause, solution, recommendation) aligned with Scenario tree with options and residual risk language. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_retell_strategic_recommendation_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_RETELL",
                                activity="listen",
                                task_widget="listen_retell",
                                topic_override="Scenario Tree & Residual Risk — listen and retell",
                                generation_instructions=(
                                    "Generate a 60–80 word monologue (a strategic recommendation to leadership) modeling Scenario tree with options and residual risk language. Ask the learner to retell including the key depth moves from Scenario tree with options and residual risk language. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_para_strategic_recommendation_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Scenario Tree & Residual Risk — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (a strategic recommendation to leadership) that must show Scenario tree with options and residual risk language with clear organisation (topic sentence, support, close). C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_opinion_strategic_recommendation_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_OPINION",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Scenario Tree & Residual Risk — opinion",
                                generation_instructions=(
                                    "Opinion task (a strategic recommendation to leadership): state a position, support with cause→impact→solution or measurable fix aligned with Scenario tree with options and residual risk language. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Chairing with Disagreement - Agenda, Conflict & Actions",
                description=(
                    "Learners practise chairing meetings when people disagree: agenda, "
                    "conflict, and clear actions at B2 level using the same "
                    "read-listen-write-speak sequence as earlier communication weeks."
                ),
                focus="Chairing meetings when people disagree: agenda, conflict, and clear actions.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach chairing meetings with disagreement.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce chairing with disagreement.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that chairing with "
                                "disagreement means keeping the agenda, managing conflict fairly, and "
                                "assigning actions. Ask about a heated meeting they attended."
                            ),
                        ),
                        TeacherStep(
                            id="chairing_disagreement",
                            goal="Teach chairing disagreement.",
                            instruction=(
                                "Teach 'Let's park that' and 'Who will own this by Friday?'. Ask them to "
                                "open a tense meeting in one sentence."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_mcq_chairing_disagreement",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Chairing a tense meeting in writing",
                            generation_instructions=(
                                "Write a tense meeting transcript with agenda control and action owners. "
                                "MCQs."
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
                        id="listen_mcq_chairing_disagreement",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Listening to chairing under disagreement",
                            generation_instructions=(
                                "Generate a 35-45 word clip chairing disagreement and assigning an owner."
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
                        id="write_bullets_to_para_chairing_disagreement",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_BULLETS_TO_PARA",
                            activity="write",
                            task_widget="write_bullets_to_para",
                            topic_override="Turn notes into a chaired summary",
                            generation_instructions=(
                                "Turn bullet notes into a chaired summary with actions."
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
                        id="speak_roleplay_chairing_disagreement",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Roleplay chairing with disagreement",
                            generation_instructions=(
                                "Roleplay chairing a meeting when two people disagree."
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
                    title="Escalation & Minute Recap",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: De-escalate + log. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: De-escalate + log.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Escalation & Minute Recap: De-escalate + log.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce chairing with disagreement.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that chairing with disagreement means keeping the agenda, managing conflict fairly, and assigning actions. Ask about a heated meeting they attended.",
                            ),
                            TeacherStep(
                                id="chairing_disagreement",
                                goal="Teach chairing disagreement.",
                                instruction="At C2 depth, push De-escalate + log: Teach 'Let's park that' and 'Who will own this by Friday?'. Ask them to open a tense meeting in one sentence.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_mcq_chairing_disagreement_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Escalation & Minute Recap — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a heated meeting the learner is chairing) rich in De-escalation and minute-style recap when chairing disagreement. Add 3–4 comprehension MCQs where at least two require applying De-escalation and minute-style recap when chairing disagreement, not only locating a noun or date. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_mcq_chairing_disagreement_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Escalation & Minute Recap — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a heated meeting the learner is chairing) using De-escalation and minute-style recap when chairing disagreement. Then 3–4 MCQs: at least two must test understanding of De-escalation and minute-style recap when chairing disagreement (form, stance, or structure), not single-fact recall. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_bullets_to_para_chairing_disagreement_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_BULLETS_TO_PARA",
                                activity="write",
                                task_widget="write_bullets_to_para",
                                topic_override="Escalation & Minute Recap — bullets to paragraph",
                                generation_instructions=(
                                    "Provide bullet notes (a heated meeting the learner is chairing) about De-escalation and minute-style recap when chairing disagreement; ask for one cohesive paragraph with owners, blockers, or next steps as required by the angle. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_roleplay_chairing_disagreement_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_ROLEPLAY",
                                activity="speak",
                                task_widget="speak_roleplay",
                                topic_override="Escalation & Minute Recap — roleplay",
                                generation_instructions=(
                                    "Roleplay (a heated meeting the learner is chairing) where the learner must use De-escalation and minute-style recap when chairing disagreement in at least two turns; include a partner cue that elicits the depth move. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Formal Advocacy - Defend a Position with Evidence",
                description=(
                    "Learners practise formal advocacy: defend a position with evidence "
                    "under challenge at B2 level using the same read-listen-write-speak "
                    "sequence as earlier communication weeks."
                ),
                focus="Formal advocacy: defend a position with evidence under challenge.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach formal advocacy under challenge.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce formal advocacy.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that formal advocacy means "
                                "stating a position, supporting it with evidence, and responding calmly "
                                "to challenges. Ask what position they would defend at work."
                            ),
                        ),
                        TeacherStep(
                            id="formal_advocacy",
                            goal="Teach formal advocacy.",
                            instruction=(
                                "Model 'The evidence shows…' and 'That is a fair challenge; however…'. "
                                "Ask them to defend one position in one sentence."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_formal_advocacy",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="Formal advocacy in text",
                            generation_instructions=(
                                "Write Q&A with challenges and evidence-based replies. True/False/Not "
                                "Given."
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
                        id="listen_infer_formal_advocacy",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Infer challenges in advocacy dialogue",
                            generation_instructions=(
                                "Dialogue challenging a position; inference on evidence used."
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
                        id="write_idea_para_formal_advocacy",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_IDEA_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write advocacy under challenge",
                            generation_instructions=(
                                "Write crisp advocacy responses to three challenges."
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
                        id="speak_pic_desc_formal_advocacy",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Explain advocacy position aloud",
                            generation_instructions=(
                                "Describe aloud how to defend a position with evidence in three lines."
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
                    title="Pre-empt Objection & Warrant",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Claim→warrant→evidence. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Claim→warrant→evidence.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Pre-empt Objection & Warrant: Claim→warrant→evidence.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce formal advocacy.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that formal advocacy means stating a position, supporting it with evidence, and responding calmly to challenges. Ask what position they would defend at work.",
                            ),
                            TeacherStep(
                                id="formal_advocacy",
                                goal="Teach formal advocacy.",
                                instruction="At C2 depth, push Claim→warrant→evidence: Model 'The evidence shows…' and 'That is a fair challenge; however…'. Ask them to defend one position in one sentence.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tfng_formal_advocacy_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TFNG",
                                activity="read",
                                task_widget="read_tfng",
                                topic_override="Pre-empt Objection & Warrant — true/false/not given",
                                generation_instructions=(
                                    "Write a 100–130 word passage (formal advocacy before a decision panel) about Pre-empt objection with claim→warrant→evidence. Provide 4–5 True/False/Not Given statements testing nuanced understanding of Pre-empt objection with claim→warrant→evidence, including one subtle distractor. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_infer_formal_advocacy_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_INFER",
                                activity="listen",
                                task_widget="listen_infer",
                                topic_override="Pre-empt Objection & Warrant — listening inference",
                                generation_instructions=(
                                    "Generate a 50–70 word spoken exchange (formal advocacy before a decision panel) where Pre-empt objection with claim→warrant→evidence is implied. Ask 3 inference questions about stance, intent, or implied meaning tied to Pre-empt objection with claim→warrant→evidence. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_idea_para_formal_advocacy_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_IDEA_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Pre-empt Objection & Warrant — idea paragraph",
                                generation_instructions=(
                                    "Ask for a 90–120 word paragraph (formal advocacy before a decision panel) arguing Pre-empt objection with claim→warrant→evidence with claim, evidence, and explicit recommendation. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_pic_desc_formal_advocacy_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Pre-empt Objection & Warrant — picture description",
                                generation_instructions=(
                                    "Describe an image scene (formal advocacy before a decision panel) using Pre-empt objection with claim→warrant→evidence in 4–5 connected sentences; include at least one depth-specific structure from Pre-empt objection with claim→warrant→evidence. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Executive Summary - Compress Complex Information",
                description=(
                    "Learners practise executive summaries that compress complex "
                    "information for different seniority levels at B2 level using the "
                    "same read-listen-write-speak sequence as earlier communication "
                    "weeks."
                ),
                focus=(
                    "Executive summaries that compress complex information for different "
                    "seniority levels."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach executive summaries for senior readers.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce executive summary.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that an executive summary "
                                "gives senior readers the issue, impact, and ask in a few tight lines. "
                                "Ask what report they would summarise for a director."
                            ),
                        ),
                        TeacherStep(
                            id="executive_summary",
                            goal="Teach executive summary.",
                            instruction=(
                                "Contrast detail-heavy vs executive lines. Ask them to write one headline "
                                "and one ask for their topic."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tone_id_executive_summary",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Executive summary tone",
                            generation_instructions=(
                                "Provide a detailed update and a 3-line executive summary; compare them."
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
                        id="listen_tone_executive_summary",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Hear a one-minute executive summary",
                            generation_instructions=(
                                "Audio one-minute executive summary; MCQs on issue and ask."
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
                        id="write_paraphrase_executive_summary",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="Rewrite detail into executive lines",
                            generation_instructions=(
                                "Rewrite a long update into a 4-sentence executive summary."
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
                        id="speak_smalltalk_executive_summary",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Small talk practising a one-line ask",
                            generation_instructions=(
                                "Small talk practising a one-sentence ask to a senior stakeholder."
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
                    title="Pyramid Principle & Scannability",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Answer-first bullets. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Answer-first bullets.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Pyramid Principle & Scannability: Answer-first bullets.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce executive summary.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that an executive summary gives senior readers the issue, impact, and ask in a few tight lines. Ask what report they would summarise for a director.",
                            ),
                            TeacherStep(
                                id="executive_summary",
                                goal="Teach executive summary.",
                                instruction="At C2 depth, push Answer-first bullets: Contrast detail-heavy vs executive lines. Ask them to write one headline and one ask for their topic.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tone_id_executive_summary_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Pyramid Principle & Scannability — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (an executive summary for senior readers) demonstrating Pyramid principle with answer-first scannable bullets. Ask the learner to identify tone/register problems or best repair choice. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_tone_executive_summary_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_TONE",
                                activity="listen",
                                task_widget="listen_tone",
                                topic_override="Pyramid Principle & Scannability — listening for tone",
                                generation_instructions=(
                                    "Generate two 30–40 word clips (an executive summary for senior readers) showing contrasting tone for Pyramid principle with answer-first scannable bullets. Ask which clip fits the required register and why. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_paraphrase_executive_summary_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARAPHRASE",
                                activity="write",
                                task_widget="write_paraphrase",
                                topic_override="Pyramid Principle & Scannability — paraphrase",
                                generation_instructions=(
                                    "Give 3 source sentences (an executive summary for senior readers) that are blunt, vague, or off-register; ask the learner to paraphrase for Pyramid principle with answer-first scannable bullets. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_smalltalk_executive_summary_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_SMALLTALK",
                                activity="speak",
                                task_widget="speak_smalltalk",
                                topic_override="Pyramid Principle & Scannability — small talk",
                                generation_instructions=(
                                    "Small-talk prompts (an executive summary for senior readers) requiring Pyramid principle with answer-first scannable bullets (echo, register shift, paraphrase, or inclusive invite) in natural replies. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Panel-Style Discussion - Synthesise Multiple Views",
                description=(
                    "Learners practise panel-style discussion: balance views, synthesise, "
                    "and land a shared takeaway at B2 level using the same "
                    "read-listen-write-speak sequence as earlier communication weeks."
                ),
                focus="Panel-style discussion: balance views, synthesise, and land a shared takeaway.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach panel-style facilitation and synthesis.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce panel-style discussion.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that panel discussions need "
                                "balancing voices, synthesising views, and landing one shared takeaway. "
                                "Ask about a panel or roundtable they watched."
                            ),
                        ),
                        TeacherStep(
                            id="panel_discussion",
                            goal="Teach panel discussion.",
                            instruction=(
                                "Teach 'Let's hear a contrasting view' and 'To synthesise, the shared "
                                "point is…'. Ask them to summarise two views in one neutral sentence."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_structure_panel_discussion",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_STRUCTURE_ID",
                            activity="read",
                            task_widget="read_structure",
                            topic_override="Panel discussion structure",
                            generation_instructions=(
                                "Provide a three-part panel transcript; label open, expert turns, "
                                "synthesis."
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
                        id="listen_retell_panel_discussion",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Retell a panel synthesis clip",
                            generation_instructions=(
                                "Audio of a moderator synthesising panel views; retell the takeaway."
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
                        id="write_email_panel_discussion",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Email summarising panel takeaway",
                            generation_instructions=(
                                "Write an email summarising a panel with a neutral shared conclusion."
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
                        id="speak_present_panel_discussion",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Present a neutral panel close",
                            generation_instructions=(
                                "Deliver a 45-second neutral panel close synthesising two views."
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
                    title="Name Tension & Propose Hybrid",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: 3 views → synthesis. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: 3 views → synthesis.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Name Tension & Propose Hybrid: 3 views → synthesis.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce panel-style discussion.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that panel discussions need balancing voices, synthesising views, and landing one shared takeaway. Ask about a panel or roundtable they watched.",
                            ),
                            TeacherStep(
                                id="panel_discussion",
                                goal="Teach panel discussion.",
                                instruction="At C2 depth, push 3 views → synthesis: Teach 'Let's hear a contrasting view' and 'To synthesise, the shared point is…'. Ask them to summarise two views in one neutral sentence.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_structure_panel_discussion_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_STRUCTURE_ID",
                                activity="read",
                                task_widget="read_structure",
                                topic_override="Name Tension & Propose Hybrid — text structure",
                                generation_instructions=(
                                    "Provide a 4–5 paragraph outline or short text (a panel discussion with conflicting experts) about Name tension across three views and propose a hybrid. Ask the learner to identify structure elements (problem, cause, solution, recommendation) aligned with Name tension across three views and propose a hybrid. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_retell_panel_discussion_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_RETELL",
                                activity="listen",
                                task_widget="listen_retell",
                                topic_override="Name Tension & Propose Hybrid — listen and retell",
                                generation_instructions=(
                                    "Generate a 60–80 word monologue (a panel discussion with conflicting experts) modeling Name tension across three views and propose a hybrid. Ask the learner to retell including the key depth moves from Name tension across three views and propose a hybrid. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_email_panel_discussion_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_EMAIL",
                                activity="write",
                                task_widget="write_email",
                                topic_override="Name Tension & Propose Hybrid — email writing",
                                generation_instructions=(
                                    "Ask for a short professional email (a panel discussion with conflicting experts) applying Name tension across three views and propose a hybrid with appropriate opening, body moves, and close. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_present_panel_discussion_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PRESENT",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Name Tension & Propose Hybrid — presentation",
                                generation_instructions=(
                                    "Presentation task (a panel discussion with conflicting experts): structured spoken segment showing Name tension across three views and propose a hybrid with signposts and a clear close. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
        cefr_level="C1",
        sub_level_min=8,
        sub_level_max=8,
        days=(
            DaySource(
                title="Innovation & Future Tech - Automation, Algorithm & Ethical AI",
                description=(
                    "Learners build vocabulary for innovation and future technology "
                    "(automation, algorithm, disruption, ethical AI, prototype) and use "
                    "the words in reading, listening, writing, and speaking tasks at B2 "
                    "level."
                ),
                focus=(
                    "Vocabulary for innovation and future technology (automation, "
                    "algorithm, disruption, ethical AI, prototype)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach innovation and future tech vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce innovation and future tech words.",
                            instruction=(
                                "Welcome the learner to vocabulary week. Explain in two sentences that we "
                                "use words like automation and algorithm to talk about innovation and "
                                "future tech. Ask them to use one of today's words in a sentence."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more innovation and future tech words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about innovation "
                                "and future tech."
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
                        id="read_word_match_innovation_tech",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Innovation & Future Tech Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match innovation and future tech words (automation, "
                                "algorithm, disruption) to short definitions or context clues."
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
                        id="listen_mcq_innovation_tech",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="A talk about innovation and future tech",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses innovation and future "
                                "tech, using at least three target words. Ask comprehension questions."
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
                        id="write_sent_trans_innovation_tech",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="innovation and future tech vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of innovation and future tech ideas and ask the "
                                "learner to rewrite each using precise vocabulary (automation, algorithm, "
                                "disruption)."
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
                        id="speak_pic_desc_innovation_tech",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a tech workplace or lab",
                            generation_instructions=(
                                "Ask the learner to describe a photo of tech lab with engineers and "
                                "screens showing automation dashboards aloud using innovation and future "
                                "tech vocabulary naturally."
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
                    title="Tech Ethics — Trade-off Debate",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: automation/algorithm argue. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: automation/algorithm argue.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Tech Ethics — Trade-off Debate: automation/algorithm argue.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce innovation and future tech words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to vocabulary week. Explain in two sentences that we use words like automation and algorithm to talk about innovation and future tech. Ask them to use one of today's words in a sentence.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more innovation and future tech words.",
                                instruction="At C2 depth, push automation/algorithm argue: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about innovation and future tech.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_innovation_tech_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Tech Ethics — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Automation/algorithm trade-offs in tech ethics debate and short definitions (a tech ethics panel on automation). Learners match each term to the definition that fits the depth collocation or usage. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_mcq_innovation_tech_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Tech Ethics — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a tech ethics panel on automation) using Automation/algorithm trade-offs in tech ethics debate. Then 3–4 MCQs: at least two must test understanding of Automation/algorithm trade-offs in tech ethics debate (form, stance, or structure), not single-fact recall. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_sent_trans_innovation_tech_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Tech Ethics — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a tech ethics panel on automation) where source and target practice Automation/algorithm trade-offs in tech ethics debate (e.g. direct to reported, active to passive, clause reduction). C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_pic_desc_innovation_tech_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Tech Ethics — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a tech ethics panel on automation) using Automation/algorithm trade-offs in tech ethics debate in 4–5 connected sentences; include at least one depth-specific structure from Automation/algorithm trade-offs in tech ethics debate. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Law & Justice - Legislation, Verdict & Precedent",
                description=(
                    "Learners build vocabulary for law and justice (legislation, verdict, "
                    "precedent, plaintiff, appeal) and use the words in reading, "
                    "listening, writing, and speaking tasks at B2 level."
                ),
                focus=(
                    "Vocabulary for law and justice (legislation, verdict, precedent, "
                    "plaintiff, appeal)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach law and justice vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce law and justice words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that law and justice "
                                "vocabulary includes legislation, verdict, precedent, plaintiff, appeal. "
                                "Ask them what they have read or heard recently about law and justice."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more law and justice words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about law and "
                                "justice."
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
                        id="read_context_mcq_law_justice",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Law & Justice Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match law and justice words (legislation, verdict, "
                                "precedent) to short definitions or context clues."
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
                        id="listen_dictation_law_justice",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="A talk about law and justice",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses law and justice, using "
                                "at least three target words. Ask comprehension questions."
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
                        id="write_word_upgrade_law_justice",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_WORD_UPGRADE",
                            activity="write",
                            task_widget="write_word_upgrade",
                            topic_override="law and justice vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of law and justice ideas and ask the learner to "
                                "rewrite each using precise vocabulary (legislation, verdict, precedent)."
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
                        id="speak_timed_law_justice",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe a courtroom or legal briefing",
                            generation_instructions=(
                                "Ask the learner to describe a photo of courtroom scene with judge and "
                                "legal counsel at a bench aloud using law and justice vocabulary "
                                "naturally."
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
                    title="Procedure vs Outcome Lexis",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: legislation/verdict case. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: legislation/verdict case.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Procedure vs Outcome Lexis: legislation/verdict case.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce law and justice words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that law and justice vocabulary includes legislation, verdict, precedent, plaintiff, appeal. Ask them what they have read or heard recently about law and justice.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more law and justice words.",
                                instruction="At C2 depth, push legislation/verdict case: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about law and justice.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_law_justice_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Procedure vs Outcome Lexis — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (a court or legislative case summary) using Procedure vs outcome lexis in a legal case narrative. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Procedure vs outcome lexis in a legal case narrative. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_dictation_law_justice_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Procedure vs Outcome Lexis — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (a court or legislative case summary) that exemplify Procedure vs outcome lexis in a legal case narrative for exact dictation. Each line should highlight one feature of Procedure vs outcome lexis in a legal case narrative. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_word_upgrade_law_justice_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_WORD_UPGRADE",
                                activity="write",
                                task_widget="write_word_upgrade",
                                topic_override="Procedure vs Outcome Lexis — word upgrade",
                                generation_instructions=(
                                    "Give 3 informal or vague sentences (a court or legislative case summary); ask the learner to upgrade vocabulary to precise terms that express Procedure vs outcome lexis in a legal case narrative. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_timed_law_justice_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Procedure vs Outcome Lexis — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a court or legislative case summary) each forcing production of Procedure vs outcome lexis in a legal case narrative. Model answers must satisfy the prompt. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Politics & Governance - Coalition, Reform & Mandate",
                description=(
                    "Learners build vocabulary for politics and governance (coalition, "
                    "reform, referendum, mandate, austerity) and use the words in "
                    "reading, listening, writing, and speaking tasks at B2 level."
                ),
                focus=(
                    "Vocabulary for politics and governance (coalition, reform, "
                    "referendum, mandate, austerity)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach politics and governance vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce politics and governance words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that politics and governance "
                                "vocabulary includes coalition, reform, referendum, mandate, austerity. "
                                "Ask them what they have read or heard recently about politics and "
                                "governance."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more politics and governance words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about politics "
                                "and governance."
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
                        id="read_word_match_politics_governance",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Politics & Governance Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match politics and governance words (coalition, "
                                "mandate, referendum) to short definitions or context clues."
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
                        id="listen_mcq_politics_governance",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="A talk about politics and governance",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses politics and "
                                "governance, using at least three target words. Ask comprehension "
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
                        id="write_para_politics_governance",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="politics and governance vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of politics and governance ideas and ask the "
                                "learner to rewrite each using precise vocabulary (coalition, mandate, "
                                "referendum)."
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
                        id="speak_pic_desc_politics_governance",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a policy or government context",
                            generation_instructions=(
                                "Ask the learner to describe a photo of parliament chamber with "
                                "politicians debating reforms aloud using politics and governance "
                                "vocabulary naturally."
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
                    title="Coalition & Policy Verbs",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: reform/mandate process. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: reform/mandate process.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Coalition & Policy Verbs: reform/mandate process.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce politics and governance words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that politics and governance vocabulary includes coalition, reform, referendum, mandate, austerity. Ask them what they have read or heard recently about politics and governance.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more politics and governance words.",
                                instruction="At C2 depth, push reform/mandate process: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about politics and governance.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_politics_governance_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Coalition & Policy Verbs — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Coalition and policy verbs (reform/mandate) in governance and short definitions (a coalition-building policy brief). Learners match each term to the definition that fits the depth collocation or usage. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_mcq_politics_governance_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Coalition & Policy Verbs — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a coalition-building policy brief) using Coalition and policy verbs (reform/mandate) in governance. Then 3–4 MCQs: at least two must test understanding of Coalition and policy verbs (reform/mandate) in governance (form, stance, or structure), not single-fact recall. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_para_politics_governance_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Coalition & Policy Verbs — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (a coalition-building policy brief) that must show Coalition and policy verbs (reform/mandate) in governance with clear organisation (topic sentence, support, close). C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_pic_desc_politics_governance_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Coalition & Policy Verbs — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a coalition-building policy brief) using Coalition and policy verbs (reform/mandate) in governance in 4–5 connected sentences; include at least one depth-specific structure from Coalition and policy verbs (reform/mandate) in governance. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Finance & Markets (Advanced) - Equity, Liability & Volatility",
                description=(
                    "Learners build vocabulary for advanced finance and markets (equity, "
                    "liability, portfolio, volatility, stakeholder) and use the words in "
                    "reading, listening, writing, and speaking tasks at B2 level."
                ),
                focus=(
                    "Vocabulary for advanced finance and markets (equity, liability, "
                    "portfolio, volatility, stakeholder)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach finance and markets vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce finance and markets words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that finance and markets "
                                "vocabulary includes equity, liability, portfolio, volatility, "
                                "stakeholder. Ask them what they have read or heard recently about "
                                "finance and markets."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more finance and markets words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about finance "
                                "and markets."
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
                        id="read_context_mcq_finance_markets",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Finance & Markets (Advanced) Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match finance and markets words (equity, volatility, "
                                "portfolio) to short definitions or context clues."
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
                        id="listen_dictation_finance_markets",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="A talk about finance and markets",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses finance and markets, "
                                "using at least three target words. Ask comprehension questions."
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
                        id="write_paraphrase_finance_markets",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="finance and markets vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of finance and markets ideas and ask the learner "
                                "to rewrite each using precise vocabulary (equity, volatility, "
                                "portfolio)."
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
                        id="speak_timed_finance_markets",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe a trading or board finance scene",
                            generation_instructions=(
                                "Ask the learner to describe a photo of trading floor or boardroom "
                                "reviewing market charts aloud using finance and markets vocabulary "
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
                    title="Risk-Return Investor Note",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: equity/volatility brief. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: equity/volatility brief.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Risk-Return Investor Note: equity/volatility brief.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce finance and markets words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that finance and markets vocabulary includes equity, liability, portfolio, volatility, stakeholder. Ask them what they have read or heard recently about finance and markets.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more finance and markets words.",
                                instruction="At C2 depth, push equity/volatility brief: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about finance and markets.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_finance_markets_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Risk-Return Investor Note — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (a concise investor note on equity risk) using Risk-return framing in an investor note. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Risk-return framing in an investor note. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_dictation_finance_markets_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Risk-Return Investor Note — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (a concise investor note on equity risk) that exemplify Risk-return framing in an investor note for exact dictation. Each line should highlight one feature of Risk-return framing in an investor note. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_paraphrase_finance_markets_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARAPHRASE",
                                activity="write",
                                task_widget="write_paraphrase",
                                topic_override="Risk-Return Investor Note — paraphrase",
                                generation_instructions=(
                                    "Give 3 source sentences (a concise investor note on equity risk) that are blunt, vague, or off-register; ask the learner to paraphrase for Risk-return framing in an investor note. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_timed_finance_markets_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Risk-Return Investor Note — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a concise investor note on equity risk) each forcing production of Risk-return framing in an investor note. Model answers must satisfy the prompt. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Psychology & Behaviour - Cognitive, Implicit & Resilience",
                description=(
                    "Learners build vocabulary for psychology and behaviour (cognitive, "
                    "perception, motivation, implicit, resilience) and use the words in "
                    "reading, listening, writing, and speaking tasks at B2 level."
                ),
                focus=(
                    "Vocabulary for psychology and behaviour (cognitive, perception, "
                    "motivation, implicit, resilience)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach psychology and behaviour vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce psychology and behaviour words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that psychology and "
                                "behaviour vocabulary includes cognitive, perception, motivation, "
                                "implicit, resilience. Ask them what they have read or heard recently "
                                "about psychology and behaviour."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more psychology and behaviour words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about psychology "
                                "and behaviour."
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
                        id="read_word_match_psychology_behaviour",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Psychology & Behaviour Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match psychology and behaviour words (cognitive, "
                                "implicit, resilience) to short definitions or context clues."
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
                        id="listen_mcq_psychology_behaviour",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="A talk about psychology and behaviour",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses psychology and "
                                "behaviour, using at least three target words. Ask comprehension "
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
                        id="write_sent_trans_psychology_behaviour",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="psychology and behaviour vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of psychology and behaviour ideas and ask the "
                                "learner to rewrite each using precise vocabulary (cognitive, implicit, "
                                "resilience)."
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
                        id="speak_pic_desc_psychology_behaviour",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a coaching or research context",
                            generation_instructions=(
                                "Ask the learner to describe a photo of workshop with facilitator "
                                "discussing motivation and behaviour aloud using psychology and behaviour "
                                "vocabulary naturally."
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
                    title="Bias Labels in Explanation",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: cognitive/implicit precise. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: cognitive/implicit precise.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Bias Labels in Explanation: cognitive/implicit precise.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce psychology and behaviour words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that psychology and behaviour vocabulary includes cognitive, perception, motivation, implicit, resilience. Ask them what they have read or heard recently about psychology and behaviour.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more psychology and behaviour words.",
                                instruction="At C2 depth, push cognitive/implicit precise: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about psychology and behaviour.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_psychology_behaviour_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Bias Labels in Explanation — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Precise cognitive/implicit bias labels in explanation and short definitions (explaining behaviour in a workplace study). Learners match each term to the definition that fits the depth collocation or usage. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_mcq_psychology_behaviour_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Bias Labels in Explanation — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (explaining behaviour in a workplace study) using Precise cognitive/implicit bias labels in explanation. Then 3–4 MCQs: at least two must test understanding of Precise cognitive/implicit bias labels in explanation (form, stance, or structure), not single-fact recall. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_sent_trans_psychology_behaviour_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Bias Labels in Explanation — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (explaining behaviour in a workplace study) where source and target practice Precise cognitive/implicit bias labels in explanation (e.g. direct to reported, active to passive, clause reduction). C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_pic_desc_psychology_behaviour_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Bias Labels in Explanation — picture description",
                                generation_instructions=(
                                    "Describe an image scene (explaining behaviour in a workplace study) using Precise cognitive/implicit bias labels in explanation in 4–5 connected sentences; include at least one depth-specific structure from Precise cognitive/implicit bias labels in explanation. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Rhetoric & Argumentation - Concede, Undermine & Compelling",
                description=(
                    "Learners build vocabulary for rhetoric and argumentation (rhetoric, "
                    "concede, undermine, compelling, nuance) and use the words in "
                    "reading, listening, writing, and speaking tasks at B2 level."
                ),
                focus=(
                    "Vocabulary for rhetoric and argumentation (rhetoric, concede, "
                    "undermine, compelling, nuance)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach rhetoric and argumentation vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce rhetoric and argumentation words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that rhetoric and "
                                "argumentation vocabulary includes rhetoric, concede, undermine, "
                                "compelling, nuance. Ask them what they have read or heard recently about "
                                "rhetoric and argumentation."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more rhetoric and argumentation words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about rhetoric "
                                "and argumentation."
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
                        id="read_context_mcq_rhetoric_argument",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Rhetoric & Argumentation Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match rhetoric and argumentation words (rhetoric, "
                                "concede, compelling) to short definitions or context clues."
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
                        id="listen_dictation_rhetoric_argument",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="A talk about rhetoric and argumentation",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses rhetoric and "
                                "argumentation, using at least three target words. Ask comprehension "
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
                        id="write_word_upgrade_rhetoric_argument",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_WORD_UPGRADE",
                            activity="write",
                            task_widget="write_word_upgrade",
                            topic_override="rhetoric and argumentation vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of rhetoric and argumentation ideas and ask the "
                                "learner to rewrite each using precise vocabulary (rhetoric, concede, "
                                "compelling)."
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
                        id="speak_timed_rhetoric_argument",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe a debate or persuasion setting",
                            generation_instructions=(
                                "Ask the learner to describe a photo of debate stage with speakers and "
                                "audience aloud using rhetoric and argumentation vocabulary naturally."
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
                    title="Concede–Undermine Paragraph",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: concede then undermine. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: concede then undermine.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Concede–Undermine Paragraph: concede then undermine.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce rhetoric and argumentation words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that rhetoric and argumentation vocabulary includes rhetoric, concede, undermine, compelling, nuance. Ask them what they have read or heard recently about rhetoric and argumentation.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more rhetoric and argumentation words.",
                                instruction="At C2 depth, push concede then undermine: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about rhetoric and argumentation.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_rhetoric_argument_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Concede–Undermine Paragraph — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (an opinion piece on a contested issue) using Concede-then-undermine rhetorical structure. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Concede-then-undermine rhetorical structure. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_dictation_rhetoric_argument_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Concede–Undermine Paragraph — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (an opinion piece on a contested issue) that exemplify Concede-then-undermine rhetorical structure for exact dictation. Each line should highlight one feature of Concede-then-undermine rhetorical structure. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_word_upgrade_rhetoric_argument_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_WORD_UPGRADE",
                                activity="write",
                                task_widget="write_word_upgrade",
                                topic_override="Concede–Undermine Paragraph — word upgrade",
                                generation_instructions=(
                                    "Give 3 informal or vague sentences (an opinion piece on a contested issue); ask the learner to upgrade vocabulary to precise terms that express Concede-then-undermine rhetorical structure. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_timed_rhetoric_argument_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Concede–Undermine Paragraph — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (an opinion piece on a contested issue) each forcing production of Concede-then-undermine rhetorical structure. Model answers must satisfy the prompt. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Review & Word Building - Consolidate Week 19",
                description=(
                    "Learners build vocabulary for the week's B2 vocabulary across "
                    "innovation, law, politics, finance, psychology, and rhetoric and use "
                    "the words in reading, listening, writing, and speaking tasks at B2 "
                    "level."
                ),
                focus=(
                    "Vocabulary for the week's B2 vocabulary across innovation, law, "
                    "politics, finance, psychology, and rhetoric."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach review and word building vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce review and word building words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that review and word "
                                "building vocabulary includes review words from week 19. Ask them what "
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
                        id="read_word_match_review_w19",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Week 19 vocabulary review",
                            generation_instructions=(
                                "Match week 19 target words to definitions across all domains."
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
                        id="listen_mcq_review_w19",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Mixed B2 vocabulary listening",
                            generation_instructions=(
                                "Short audio using six week-19 words; comprehension questions."
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
                        id="write_para_review_w19",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Word-building and precision writing",
                            generation_instructions=(
                                "Ask the learner to build three words with prefixes/suffixes and use each "
                                "in a sentence."
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
                        id="speak_timed_review_w19",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe a scene using week 19 words",
                            generation_instructions=(
                                "Describe a photo collage using at least five week-19 words aloud."
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
                    title="C1 Argument Fragment (120w)",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Recycle week 3 lexis. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Recycle week 3 lexis.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — C1 Argument Fragment (120w): Recycle week 3 lexis.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce review and word building words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that review and word building vocabulary includes review words from week 19. Ask them what they have read or heard recently about review and word building.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more review and word building words.",
                                instruction="At C2 depth, push Recycle week 3 lexis: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about review and word building.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_review_w19_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="C1 Argument Fragment (120w) — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Week 3 vocabulary in a 120-word formal argument fragment and short definitions (a formal argument recycling week 3 lexis). Learners match each term to the definition that fits the depth collocation or usage. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_mcq_review_w19_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="C1 Argument Fragment (120w) — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a formal argument recycling week 3 lexis) using Week 3 vocabulary in a 120-word formal argument fragment. Then 3–4 MCQs: at least two must test understanding of Week 3 vocabulary in a 120-word formal argument fragment (form, stance, or structure), not single-fact recall. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_para_review_w19_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="C1 Argument Fragment (120w) — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (a formal argument recycling week 3 lexis) that must show Week 3 vocabulary in a 120-word formal argument fragment with clear organisation (topic sentence, support, close). C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_timed_review_w19_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="C1 Argument Fragment (120w) — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a formal argument recycling week 3 lexis) each forcing production of Week 3 vocabulary in a 120-word formal argument fragment. Model answers must satisfy the prompt. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
        cefr_level="C1",
        sub_level_min=8,
        sub_level_max=8,
        days=(
            DaySource(
                title="High-Stakes Conversations - Stay Composed Under Pressure",
                description=(
                    "Learners build confidence to stay composed in high-stakes "
                    "conversations when pressure and outcomes matter, using the same "
                    "read-listen-write-speak sequence at B2 level."
                ),
                focus="Stay composed in high-stakes conversations when pressure and outcomes matter.",
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence for high-stakes conversations.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at B2. Explain in two sentences "
                                "that stay composed in high-stakes conversations when pressure and "
                                "outcomes matter gets easier with preparation. Ask them to name one "
                                "high-stakes situation they want to handle better."
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
                        id="read_comp_mcq_high_stakes_conv",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="High-stakes composure story",
                            generation_instructions=(
                                "Write a story about staying composed when stakes are high; MCQs."
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
                        id="listen_shadow_high_stakes_conv",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Calm-under-pressure shadowing",
                            generation_instructions=(
                                "Generate a 15-second calm-under-pressure clip for shadowing."
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
                        id="write_sent_trans_high_stakes_conv",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Reframe anxious lines",
                            generation_instructions=(
                                "Rewrite three anxious lines into composed professional language."
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
                        id="speak_read_aloud_high_stakes_conv",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_READ_ALOUD",
                            activity="speak",
                            task_widget="read_aloud",
                            topic_override="Read composure passage aloud",
                            generation_instructions=(
                                "Give a 55-70 word passage on composure to read aloud."
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
                    title="Reframe & Bounded 3-Part Answer",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Pressure + structure. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Pressure + structure.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Reframe & Bounded 3-Part Answer: Pressure + structure.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at B2. Explain in two sentences that stay composed in high-stakes conversations when pressure and outcomes matter gets easier with preparation. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push Pressure + structure: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_comp_mcq_high_stakes_conv_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Reframe & Bounded 3-Part Answer — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a high-stakes stakeholder conversation) rich in Reframe under pressure with a bounded three-part answer. Add 3–4 comprehension MCQs where at least two require applying Reframe under pressure with a bounded three-part answer, not only locating a noun or date. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_shadow_high_stakes_conv_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Reframe & Bounded 3-Part Answer — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (a high-stakes stakeholder conversation) dense with Reframe under pressure with a bounded three-part answer for shadowing practice. Rhythm and phrasing should model natural C2 delivery. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_sent_trans_high_stakes_conv_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Reframe & Bounded 3-Part Answer — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a high-stakes stakeholder conversation) where source and target practice Reframe under pressure with a bounded three-part answer (e.g. direct to reported, active to passive, clause reduction). C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_read_aloud_high_stakes_conv_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_READ_ALOUD",
                                activity="speak",
                                task_widget="read_aloud",
                                topic_override="Reframe & Bounded 3-Part Answer — read aloud",
                                generation_instructions=(
                                    "Write a 50–60 word passage (a high-stakes stakeholder conversation) dense with Reframe under pressure with a bounded three-part answer for read-aloud; not an introductory lesson on the parent base form. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Evidence-Based Debate - Claim, Concession & Rebuttal",
                description=(
                    "Learners build confidence to debate with evidence: claim, partial "
                    "concession, and calm rebuttal, using the same "
                    "read-listen-write-speak sequence at B2 level."
                ),
                focus="Debate with evidence: claim, partial concession, and calm rebuttal.",
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence for evidence-based debate.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at B2. Explain in two sentences "
                                "that debate with evidence: claim, partial concession, and calm rebuttal "
                                "gets easier with preparation. Ask them to name one high-stakes situation "
                                "they want to handle better."
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
                        id="read_tone_id_evidence_debate",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Evidence-based debate tone",
                            generation_instructions=(
                                "Two argument excerpts; identify which uses evidence and partial "
                                "concession."
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
                        id="listen_mcq_evidence_debate",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Debate listening",
                            generation_instructions=(
                                "Audio with claim, evidence, and rebuttal; inference questions."
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
                        id="write_timed_evidence_debate",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Timed debate writing",
                            generation_instructions=(
                                "Timed paragraph: claim, evidence, concession, rebuttal."
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
                        id="speak_timed_evidence_debate",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Timed debate speaking",
                            generation_instructions=(
                                "Three timed speaking prompts to debate with evidence calmly."
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
                    title="Weigh Evidence & Partial Concession",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Quality of proof. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Quality of proof.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Weigh Evidence & Partial Concession: Quality of proof.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at B2. Explain in two sentences that debate with evidence: claim, partial concession, and calm rebuttal gets easier with preparation. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push Quality of proof: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_tone_id_evidence_debate_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Weigh Evidence & Partial Concession — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (an evidence-based debate on a policy) demonstrating Weigh evidence quality with partial concession. Ask the learner to identify tone/register problems or best repair choice. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_mcq_evidence_debate_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Weigh Evidence & Partial Concession — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (an evidence-based debate on a policy) using Weigh evidence quality with partial concession. Then 3–4 MCQs: at least two must test understanding of Weigh evidence quality with partial concession (form, stance, or structure), not single-fact recall. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_timed_evidence_debate_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="Weigh Evidence & Partial Concession — timed writing",
                                generation_instructions=(
                                    "Timed writing (an evidence-based debate on a policy): produce a structured response demonstrating Weigh evidence quality with partial concession within the time limit; include clear signposts or moves from the depth angle. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_timed_evidence_debate_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Weigh Evidence & Partial Concession — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (an evidence-based debate on a policy) each forcing production of Weigh evidence quality with partial concession. Model answers must satisfy the prompt. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Professional Brand Story - Past, Present & Direction",
                description=(
                    "Learners build confidence to tell a professional brand story with "
                    "past, present, and direction, using the same read-listen-write-speak "
                    "sequence at B2 level."
                ),
                focus="Tell a professional brand story with past, present, and direction.",
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence for professional brand story.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at B2. Explain in two sentences "
                                "that tell a professional brand story with past, present, and direction "
                                "gets easier with preparation. Ask them to name one high-stakes situation "
                                "they want to handle better."
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
                        id="read_comp_mcq_brand_story",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Brand story comprehension",
                            generation_instructions=(
                                "Story with past-present-direction arc; MCQs on brand message."
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
                        id="listen_tone_brand_story",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Tone in a brand narrative",
                            generation_instructions=(
                                "Audio of a professional brand story; tone and structure questions."
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
                        id="write_sent_trans_brand_story",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Brand story transforms",
                            generation_instructions=(
                                "Transform three sentences into a past-present-direction brand arc."
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
                        id="speak_pic_desc_brand_story",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Brand story picture description",
                            generation_instructions=(
                                "Describe a photo using brand-story vocabulary aloud."
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
                    title="Tension–Turn–Proof Arc",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Turning point narrative. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Turning point narrative.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Tension–Turn–Proof Arc: Turning point narrative.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at B2. Explain in two sentences that tell a professional brand story with past, present, and direction gets easier with preparation. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push Turning point narrative: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_comp_mcq_brand_story_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Tension–Turn–Proof Arc — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a brand story with a turning point) rich in Tension–turn–proof brand narrative arc. Add 3–4 comprehension MCQs where at least two require applying Tension–turn–proof brand narrative arc, not only locating a noun or date. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_tone_brand_story_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_TONE",
                                activity="listen",
                                task_widget="listen_tone",
                                topic_override="Tension–Turn–Proof Arc — listening for tone",
                                generation_instructions=(
                                    "Generate two 30–40 word clips (a brand story with a turning point) showing contrasting tone for Tension–turn–proof brand narrative arc. Ask which clip fits the required register and why. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_sent_trans_brand_story_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Tension–Turn–Proof Arc — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a brand story with a turning point) where source and target practice Tension–turn–proof brand narrative arc (e.g. direct to reported, active to passive, clause reduction). C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_pic_desc_brand_story_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Tension–Turn–Proof Arc — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a brand story with a turning point) using Tension–turn–proof brand narrative arc in 4–5 connected sentences; include at least one depth-specific structure from Tension–turn–proof brand narrative arc. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Public Challenge - Tough Questions Without Defensiveness",
                description=(
                    "Learners build confidence to handle public challenge: tough "
                    "questions, stay clear, avoid defensiveness, using the same "
                    "read-listen-write-speak sequence at B2 level."
                ),
                focus="Handle public challenge: tough questions, stay clear, avoid defensiveness.",
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence for public challenge.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at B2. Explain in two sentences "
                                "that handle public challenge: tough questions, stay clear, avoid "
                                "defensiveness gets easier with preparation. Ask them to name one "
                                "high-stakes situation they want to handle better."
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
                        id="read_tone_id_public_challenge",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Public challenge tone",
                            generation_instructions=(
                                "Two answers to a tough question; identify bridge and redirect."
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
                        id="listen_shadow_public_challenge",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Tough-question shadowing",
                            generation_instructions=(
                                "Clip of a tough question answered calmly for shadowing."
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
                        id="write_timed_public_challenge",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Timed bridge-and-redirect writing",
                            generation_instructions=(
                                "Timed answers to three hostile questions using bridge + redirect."
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
                        id="speak_smalltalk_public_challenge",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Public challenge small talk",
                            generation_instructions=(
                                "Small talk practising one bridge phrase and one redirect."
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
                    title="Non-Defensive Bridge",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Acknowledge→core message. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Acknowledge→core message.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Non-Defensive Bridge: Acknowledge→core message.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at B2. Explain in two sentences that handle public challenge: tough questions, stay clear, avoid defensiveness gets easier with preparation. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push Acknowledge→core message: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_tone_id_public_challenge_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Non-Defensive Bridge — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (responding to public challenge or criticism) demonstrating Non-defensive bridge from acknowledge to core message. Ask the learner to identify tone/register problems or best repair choice. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_shadow_public_challenge_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Non-Defensive Bridge — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (responding to public challenge or criticism) dense with Non-defensive bridge from acknowledge to core message for shadowing practice. Rhythm and phrasing should model natural C2 delivery. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_timed_public_challenge_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="Non-Defensive Bridge — timed writing",
                                generation_instructions=(
                                    "Timed writing (responding to public challenge or criticism): produce a structured response demonstrating Non-defensive bridge from acknowledge to core message within the time limit; include clear signposts or moves from the depth angle. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_smalltalk_public_challenge_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_SMALLTALK",
                                activity="speak",
                                task_widget="speak_smalltalk",
                                topic_override="Non-Defensive Bridge — small talk",
                                generation_instructions=(
                                    "Small-talk prompts (responding to public challenge or criticism) requiring Non-defensive bridge from acknowledge to core message (echo, register shift, paraphrase, or inclusive invite) in natural replies. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Stakeholder Pitch - Problem, Solution, Proof & Ask",
                description=(
                    "Learners build confidence to deliver a stakeholder pitch with "
                    "problem, solution, proof point, and ask, using the same "
                    "read-listen-write-speak sequence at B2 level."
                ),
                focus="Deliver a stakeholder pitch with problem, solution, proof point, and ask.",
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence for stakeholder pitch.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at B2. Explain in two sentences "
                                "that deliver a stakeholder pitch with problem, solution, proof point, "
                                "and ask gets easier with preparation. Ask them to name one high-stakes "
                                "situation they want to handle better."
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
                        id="read_comp_mcq_stakeholder_pitch",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Stakeholder pitch comprehension",
                            generation_instructions=(
                                "Short pitch text; questions on problem, solution, proof, and ask."
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
                        id="listen_mcq_stakeholder_pitch",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Pitch listening",
                            generation_instructions=(
                                "Audio of a stakeholder pitch; MCQs on ask and proof point."
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
                        id="write_sent_trans_stakeholder_pitch",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Pitch sentence transforms",
                            generation_instructions=(
                                "Rewrite a vague pitch into problem → solution → proof → ask."
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
                        id="speak_pic_desc_stakeholder_pitch",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Stakeholder pitch speaking",
                            generation_instructions=(
                                "Describe delivering a stakeholder pitch aloud."
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
                    title="Proof Point + Risk Mitigant",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Data + acknowledged risk. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Data + acknowledged risk.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Proof Point + Risk Mitigant: Data + acknowledged risk.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at B2. Explain in two sentences that deliver a stakeholder pitch with problem, solution, proof point, and ask gets easier with preparation. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push Data + acknowledged risk: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_comp_mcq_stakeholder_pitch_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Proof Point + Risk Mitigant — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a stakeholder pitch with data and risk) rich in Proof point plus acknowledged risk mitigant in a pitch. Add 3–4 comprehension MCQs where at least two require applying Proof point plus acknowledged risk mitigant in a pitch, not only locating a noun or date. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_mcq_stakeholder_pitch_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Proof Point + Risk Mitigant — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a stakeholder pitch with data and risk) using Proof point plus acknowledged risk mitigant in a pitch. Then 3–4 MCQs: at least two must test understanding of Proof point plus acknowledged risk mitigant in a pitch (form, stance, or structure), not single-fact recall. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_sent_trans_stakeholder_pitch_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Proof Point + Risk Mitigant — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a stakeholder pitch with data and risk) where source and target practice Proof point plus acknowledged risk mitigant in a pitch (e.g. direct to reported, active to passive, clause reduction). C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_pic_desc_stakeholder_pitch_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Proof Point + Risk Mitigant — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a stakeholder pitch with data and risk) using Proof point plus acknowledged risk mitigant in a pitch in 4–5 connected sentences; include at least one depth-specific structure from Proof point plus acknowledged risk mitigant in a pitch. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Keynote-Style Segment - Structured Talk & Hard Question",
                description=(
                    "Learners build confidence to deliver a keynote-style segment with "
                    "structure and one hard question, using the same "
                    "read-listen-write-speak sequence at B2 level."
                ),
                focus="Deliver a keynote-style segment with structure and one hard question.",
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence for keynote-style segment.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at B2. Explain in two sentences "
                                "that deliver a keynote-style segment with structure and one hard "
                                "question gets easier with preparation. Ask them to name one high-stakes "
                                "situation they want to handle better."
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
                        id="read_tone_id_keynote_segment",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Keynote structure comprehension",
                            generation_instructions=(
                                "Identify hook, two points, and close in a short talk transcript."
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
                        id="listen_tone_keynote_segment",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Hook and close listening",
                            generation_instructions=(
                                "Audio with clear structure plus one hard question; MCQs."
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
                        id="write_timed_keynote_segment",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Keynote writing",
                            generation_instructions=(
                                "Timed paragraph: hook, two points, conclusion."
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
                        id="speak_present_keynote_segment",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Keynote-style speaking",
                            generation_instructions=(
                                "45-second keynote segment plus brief answer to one hard question."
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
                    title="90s Segment + Hostile Follow-up",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Structure + hard Q. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Structure + hard Q.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — 90s Segment + Hostile Follow-up: Structure + hard Q.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at B2. Explain in two sentences that deliver a keynote-style segment with structure and one hard question gets easier with preparation. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push Structure + hard Q: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_tone_id_keynote_segment_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="90s Segment + Hostile Follow-up — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (a keynote segment with a tough follow-up question) demonstrating 90-second structured segment plus hostile follow-up. Ask the learner to identify tone/register problems or best repair choice. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_tone_keynote_segment_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_TONE",
                                activity="listen",
                                task_widget="listen_tone",
                                topic_override="90s Segment + Hostile Follow-up — listening for tone",
                                generation_instructions=(
                                    "Generate two 30–40 word clips (a keynote segment with a tough follow-up question) showing contrasting tone for 90-second structured segment plus hostile follow-up. Ask which clip fits the required register and why. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_timed_keynote_segment_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="90s Segment + Hostile Follow-up — timed writing",
                                generation_instructions=(
                                    "Timed writing (a keynote segment with a tough follow-up question): produce a structured response demonstrating 90-second structured segment plus hostile follow-up within the time limit; include clear signposts or moves from the depth angle. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_present_keynote_segment_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PRESENT",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="90s Segment + Hostile Follow-up — presentation",
                                generation_instructions=(
                                    "Presentation task (a keynote segment with a tough follow-up question): structured spoken segment showing 90-second structured segment plus hostile follow-up with signposts and a clear close. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                title="Full Confidence Showcase (B2)",
                description=(
                    "Learners build confidence to integrate B2 confidence skills in one "
                    "capstone showcase, using the same read-listen-write-speak sequence "
                    "at B2 level."
                ),
                focus="Integrate b2 confidence skills in one capstone showcase.",
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence for full confidence showcase (b2).",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at B2. Explain in two sentences "
                                "that integrate B2 confidence skills in one capstone showcase gets easier "
                                "with preparation. Ask them to name one high-stakes situation they want "
                                "to handle better."
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
                        id="read_comp_mcq_showcase_w20",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="B2 confidence capstone story",
                            generation_instructions=(
                                "Write a capstone story integrating composure, evidence, brand arc, and "
                                "pitch; MCQs."
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
                        id="listen_shadow_showcase_w20",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Capstone shadowing clip",
                            generation_instructions=(
                                "Generate a 20-second confident capstone clip for shadowing."
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
                        id="write_timed_showcase_w20",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Timed integrated B2 writing",
                            generation_instructions=(
                                "Ask for a timed paragraph integrating claim, story, and ask."
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
                        id="speak_debate_showcase_w20",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_DEBATE",
                            activity="speak",
                            task_widget="speak_debate",
                            topic_override="Debate-style B2 showcase",
                            generation_instructions=(
                                "Short showcase: rebut one point and close with a clear ask."
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
                    title="Mediation + Exec Summary Close",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Combined scenario. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Combined scenario.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Mediation + Exec Summary Close: Combined scenario.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at B2. Explain in two sentences that integrate B2 confidence skills in one capstone showcase gets easier with preparation. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push Combined scenario: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_comp_mcq_showcase_w20_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Mediation + Exec Summary Close — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a showcase combining mediation and exec close) rich in Combined mediation and executive-summary close. Add 3–4 comprehension MCQs where at least two require applying Combined mediation and executive-summary close, not only locating a noun or date. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="listen_shadow_showcase_w20_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Mediation + Exec Summary Close — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (a showcase combining mediation and exec close) dense with Combined mediation and executive-summary close for shadowing practice. Rhythm and phrasing should model natural C2 delivery. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="write_timed_showcase_w20_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="Mediation + Exec Summary Close — timed writing",
                                generation_instructions=(
                                    "Timed writing (a showcase combining mediation and exec close): produce a structured response demonstrating Combined mediation and executive-summary close within the time limit; include clear signposts or moves from the depth angle. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
                            id="speak_debate_showcase_w20_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_DEBATE",
                                activity="speak",
                                task_widget="speak_debate",
                                topic_override="Mediation + Exec Summary Close — debate",
                                generation_instructions=(
                                    "Debate scenario (a showcase combining mediation and exec close) integrating Combined mediation and executive-summary close: chair briefly, respond to one challenge, then deliver a timed closing statement. C2 level: longer passages, contrast, and error-spotting or nuanced distractors where the archetype allows."
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
    # ── Cycle 6 — Mastery (C1) ──────────────────────────────────
    WeekSource(
        week_number=5,
        theme_type="grammar",
        cefr_level="C2",
        sub_level_min=8,
        sub_level_max=8,
        days=(
            DaySource(
                title="Aspect, Register & Narrative Voice",
                description=(
                    "Learners control aspect and register in narrative: subtle time "
                    "shifts (had been reflecting, was leaving, has shaped), and a "
                    "reflective or literary tone suited to professional storytelling."
                ),
                focus=(
                    "Aspect, register, and narrative voice: subtle time shifts and "
                    "reflective or literary tone in connected prose."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach aspect choice and register in narrative voice.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce aspect and narrative register.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that narrative voice "
                                "combines aspect choices (simple, continuous, perfect) with register "
                                "(neutral, reflective, literary). Ask them to describe a recent change at "
                                "work using one reflective opening line."
                            ),
                        ),
                        TeacherStep(
                            id="aspect_shifts",
                            goal="Teach subtle time shifts.",
                            instruction=(
                                "Use their line to show how shifting aspect changes emphasis (I had been "
                                "considering…, I was leaving…, It has shaped…). Ask them to rewrite one "
                                "fact with a different aspect for a more reflective tone."
                            ),
                        ),
                        TeacherStep(
                            id="register",
                            goal="Teach register in narrative.",
                            instruction=(
                                "Contrast neutral reporting with literary distance (It seemed that…, What "
                                "followed was…). Ask them to add one literary linker to their sentence "
                                "without changing the fact."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has shown aspect or register control at least once, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_cloze_aspect_narrative",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CLOZE",
                            activity="read",
                            task_widget="fill_blanks",
                            topic_override="Aspect and register in narrative",
                            generation_instructions=(
                                "Write a 4-5 blank connected narrative passage (professional memoir tone) "
                                "where aspect and register shift subtly (had been, was, has, seemed). "
                                "Blanks test the best aspect or linker for the context."
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
                        id="listen_mcq_aspect_narrative",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Listening for aspect shifts in narrative",
                            generation_instructions=(
                                "Generate a 70-100 word spoken reflective narrative using mixed aspects "
                                "and one literary distancing phrase. Include 3-4 MCQs on aspect meaning "
                                "or register."
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
                        id="write_narrative_aspect_narrative",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_OPEN_SENT",
                            activity="write",
                            task_widget="open_text",
                            topic_override="Write narrative sentences with aspect control",
                            generation_instructions=(
                                "Ask for three short narrative sentences at C1 level: one with past "
                                "perfect continuous, one with simple past for a punchy fact, one with "
                                "present perfect for relevance."
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
                        id="speak_narrative_aspect_narrative",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Speak a short reflective narrative",
                            generation_instructions=(
                                "Ask the learner to speak a 45-second reflective narrative about a career "
                                "moment using at least two aspect shifts and one literary distancing "
                                "phrase."
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
                    title="Irony & Distance via Voice/Aspect",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Subtle stance shift. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Subtle stance shift.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Irony & Distance via Voice/Aspect: Subtle stance shift.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce aspect and narrative register.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that narrative voice combines aspect choices (simple, continuous, perfect) with register (neutral, reflective, literary). Ask them to describe a recent change at work using one reflective opening line.",
                            ),
                            TeacherStep(
                                id="aspect_shifts",
                                goal="Teach subtle time shifts.",
                                instruction="At C2 depth, push Subtle stance shift: Use their line to show how shifting aspect changes emphasis (I had been considering…, I was leaving…, It has shaped…). Ask them to rewrite one fact with a different aspect for a more reflective tone.",
                            ),
                            TeacherStep(
                                id="register",
                                goal="Teach register in narrative.",
                                instruction="At C2 depth, push Subtle stance shift: Contrast neutral reporting with literary distance (It seemed that…, What followed was…). Ask them to add one literary linker to their sentence without changing the fact.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has shown aspect or register control at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_cloze_aspect_narrative_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CLOZE",
                                activity="read",
                                task_widget="fill_blanks",
                                topic_override="Irony & Distance via Voice/Aspect — reading cloze",
                                generation_instructions=(
                                    "Write one connected 4–5-blank passage (a professional memoir-style narrative) where every blank tests Subtle stance shift through voice and aspect (irony and distance). Include at least two distinct facets of the depth angle in the passage. Do not drill only the parent base lesson pattern; the passage must read as a depth task on Irony & Distance via Voice/Aspect. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_mcq_aspect_narrative_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Irony & Distance via Voice/Aspect — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a professional memoir-style narrative) using Subtle stance shift through voice and aspect (irony and distance). Then 3–4 MCQs: at least two must test understanding of Subtle stance shift through voice and aspect (irony and distance) (form, stance, or structure), not single-fact recall. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_narrative_aspect_narrative_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_OPEN_SENT",
                                activity="write",
                                task_widget="open_text",
                                topic_override="Irony & Distance via Voice/Aspect — open sentences",
                                generation_instructions=(
                                    "Ask for exactly 3 learner sentences (a professional memoir-style narrative) that each demonstrate a different facet of Subtle stance shift through voice and aspect (irony and distance). Do not ask for practice that only repeats the parent base lesson focus. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_narrative_aspect_narrative_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Irony & Distance via Voice/Aspect — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a professional memoir-style narrative) each forcing production of Subtle stance shift through voice and aspect (irony and distance). Model answers must satisfy the prompt. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Advanced Hypotheticals - Were it not for, But for & Supposing",
                description=(
                    "Learners use advanced formal hypotheticals (Were it not for…, But "
                    "for…, Supposing…, inverted Had…) for unreal situations in "
                    "professional speech."
                ),
                focus=(
                    "Advanced hypotheticals: Were it not for, But for, Supposing, and "
                    "inverted Had-clauses with would-have results."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach advanced formal hypothetical patterns.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce advanced hypotheticals.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that formal hypotheticals "
                                "like Were it not for and But for express what would be different if "
                                "something were not true. Ask what would be different in their field if "
                                "one recent trend had not happened."
                            ),
                        ),
                        TeacherStep(
                            id="were_but_for",
                            goal="Teach Were it not for and But for.",
                            instruction=(
                                "Use their idea with Were it not for + clause or But for + noun. Ask them "
                                "to finish 'But for the pandemic, …' with a would-have result."
                            ),
                        ),
                        TeacherStep(
                            id="supposing_had",
                            goal="Teach Supposing and inverted Had.",
                            instruction=(
                                "Show Supposing + past perfect and Had they acted…, … would have…. Ask "
                                "them to make one Supposing sentence about a decision at work."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used an advanced hypothetical at least once, ask "
                                "only: Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_error_advanced_hypothetical",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_ERROR_SPOT",
                            activity="read",
                            task_widget="error_spotting",
                            topic_override="Spot advanced hypothetical errors",
                            generation_instructions=(
                                "Generate a 5-sentence formal passage with advanced hypotheticals. Each "
                                "sentence must contain exactly one error (5 tokens): wrong Were/But for "
                                "form, Supposing tense, or would-have mismatch."
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
                        id="listen_cloze_advanced_hypothetical",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_CLOZE",
                            activity="listen",
                            task_widget="listen_cloze",
                            topic_override="Listen and fill advanced hypothetical forms",
                            generation_instructions=(
                                "Listen to the formal hypotheticals audio, then complete paraphrased "
                                "notes with missing Were it not for / But for / Supposing phrases."
                            ),
                            widget_requirements=(
                                "Set inner_widget to 'fill_in_blanks'. Use the authored audio_script, "
                                "passage, and 5 BlankItems exactly as provided so rule-based scoring can "
                                "compare each typed verb phrase with correct_answer."
                            ),
                            static_payload={
                                "task_intro": "Listen, then complete the advanced hypothetical notes.",
                                "instructions": "Play the audio once, then type the missing formal hypothetical "
                                "phrases in the paraphrased notes.",
                                "estimated_time_minutes": 3,
                                "inner_widget": "fill_in_blanks",
                                "audio_genre": "Formal reflective monologue",
                                "audio_script": "Were it not for your support, the project would have stalled. But "
                                "for the delay, we would have launched in March. Supposing we had "
                                "accepted their terms, the partnership might have failed sooner. Had "
                                "the board acted earlier, we would have avoided the crisis. If only "
                                "the data had been clearer, the decision would have been easier.",
                                "passage_title": "Formal Hypotheticals Notes",
                                "passage": "___ your support, the project would have stalled. But for the delay, we "
                                "___ in March. Supposing we ___ their terms, the partnership might have "
                                "failed sooner. Had the board acted earlier, we ___ the crisis.",
                                "items": [
                                    {
                                        "item_id": "b1",
                                        "blank_id": "b1",
                                        "sentence_with_blank": "___ your support, the project would have stalled.",
                                        "base_verb": "be",
                                        "correct_answer": "Were it not for",
                                        "distractors": [
                                            "If it was not for",
                                            "Without of",
                                        ],
                                        "options": [
                                            "Were it not for",
                                            "If it was not for",
                                            "Without of",
                                        ],
                                        "grammar_rule": "Use Were it not for in formal unreal present/past "
                                        "hypotheticals.",
                                        "explanation": "Were it not for is the formal inverted hypothetical "
                                        "opener.",
                                    },
                                    {
                                        "item_id": "b2",
                                        "blank_id": "b2",
                                        "sentence_with_blank": "But for the delay, we ___ in March.",
                                        "base_verb": "launch",
                                        "correct_answer": "would have launched",
                                        "distractors": ["will launch", "launched"],
                                        "options": [
                                            "would have launched",
                                            "will launch",
                                            "launched",
                                        ],
                                        "grammar_rule": "But for + noun takes a would-have result clause.",
                                        "explanation": "The unreal past result uses would have launched.",
                                    },
                                    {
                                        "item_id": "b3",
                                        "blank_id": "b3",
                                        "sentence_with_blank": "Supposing we ___ their terms, the partnership "
                                        "might have failed sooner.",
                                        "base_verb": "accept",
                                        "correct_answer": "had accepted",
                                        "distractors": ["accepted", "would accept"],
                                        "options": [
                                            "had accepted",
                                            "accepted",
                                            "would accept",
                                        ],
                                        "grammar_rule": "Supposing often takes past perfect for unreal past.",
                                        "explanation": "Supposing we had accepted fits a formal unreal past.",
                                    },
                                    {
                                        "item_id": "b4",
                                        "blank_id": "b4",
                                        "sentence_with_blank": "Had the board acted earlier, we ___ the crisis.",
                                        "base_verb": "avoid",
                                        "correct_answer": "would have avoided",
                                        "distractors": ["will avoid", "avoided"],
                                        "options": [
                                            "would have avoided",
                                            "will avoid",
                                            "avoided",
                                        ],
                                        "grammar_rule": "Inverted Had-clause pairs with would have + past "
                                        "participle.",
                                        "explanation": "The imagined past result uses would have avoided.",
                                    },
                                ],
                                "target_words_in_audio": [
                                    "Were it not for",
                                    "would have launched",
                                    "had accepted",
                                    "would have avoided",
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
                        id="write_error_advanced_hypothetical",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_ERROR_CORR",
                            activity="write",
                            task_widget="error_correction",
                            topic_override="Correct advanced hypothetical mistakes",
                            generation_instructions=(
                                "Give 3 sentences with one advanced hypothetical error each; ask the "
                                "learner to rewrite correctly using Were it not for, But for, or "
                                "Supposing."
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
                        id="speak_read_advanced_hypothetical",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_READ_ALOUD",
                            activity="speak",
                            task_widget="read_aloud",
                            topic_override="Read advanced hypothetical passage aloud",
                            generation_instructions=(
                                "Give a 55-70 word connected passage with Were it not for, But for, and "
                                "Supposing for read-aloud practice."
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
                    title="Were it not for / But for Chains",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Policy counterfactual. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Policy counterfactual.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Were it not for / But for Chains: Policy counterfactual.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce advanced hypotheticals.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that formal hypotheticals like Were it not for and But for express what would be different if something were not true. Ask what would be different in their field if one recent trend had not happened.",
                            ),
                            TeacherStep(
                                id="were_but_for",
                                goal="Teach Were it not for and But for.",
                                instruction="At C2 depth, push Policy counterfactual: Use their idea with Were it not for + clause or But for + noun. Ask them to finish 'But for the pandemic, …' with a would-have result.",
                            ),
                            TeacherStep(
                                id="supposing_had",
                                goal="Teach Supposing and inverted Had.",
                                instruction="At C2 depth, push Policy counterfactual: Show Supposing + past perfect and Had they acted…, … would have…. Ask them to make one Supposing sentence about a decision at work.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used an advanced hypothetical at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_error_advanced_hypothetical_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_ERROR_SPOT",
                                activity="read",
                                task_widget="error_spotting",
                                topic_override="Were it not for / But for Chains — error spotting",
                                generation_instructions=(
                                    "Write a 5-sentence passage (a policy counterfactual on a past decision) with exactly five single-token errors, all illustrating Were it not for / But for counterfactual chains in policy. Diversify error types across sentences. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_cloze_advanced_hypothetical_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_CLOZE",
                                activity="listen",
                                task_widget="listen_cloze",
                                topic_override="Were it not for / But for Chains — listen and complete",
                                generation_instructions=(
                                    "Create a 40–60 word audio script (a policy counterfactual on a past decision) dense with Were it not for / But for counterfactual chains in policy. Provide a gapped written version; blanks test Were it not for / But for counterfactual chains in policy only. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
                                ),
                                widget_requirements=(
                                    "Set inner_widget to 'fill_in_blanks'. Use the authored audio_script, passage, and 5 BlankItems exactly as provided so rule-based scoring can compare each typed verb phrase with correct_answer."
                                ),
                                static_payload={
                                    "task_intro": "Listen, then complete the advanced hypothetical notes.",
                                    "instructions": "Play the audio once, then type the missing formal hypothetical phrases in the paraphrased notes.",
                                    "estimated_time_minutes": 3,
                                    "inner_widget": "fill_in_blanks",
                                    "audio_genre": "Formal reflective monologue",
                                    "audio_script": "Were it not for your support, the project would have stalled. But for the delay, we would have launched in March. Supposing we had accepted their terms, the partnership might have failed sooner. Had the board acted earlier, we would have avoided the crisis. If only the data had been clearer, the decision would have been easier.",
                                    "passage_title": "Formal Hypotheticals Notes",
                                    "passage": "___ your support, the project would have stalled. But for the delay, we ___ in March. Supposing we ___ their terms, the partnership might have failed sooner. Had the board acted earlier, we ___ the crisis.",
                                    "items": [
                                        {
                                            "item_id": "b1",
                                            "blank_id": "b1",
                                            "sentence_with_blank": "___ your support, the project would have stalled.",
                                            "base_verb": "be",
                                            "correct_answer": "Were it not for",
                                            "distractors": [
                                                "If it was not for",
                                                "Without of",
                                            ],
                                            "options": [
                                                "Were it not for",
                                                "If it was not for",
                                                "Without of",
                                            ],
                                            "grammar_rule": "Use Were it not for in formal unreal present/past hypotheticals.",
                                            "explanation": "Were it not for is the formal inverted hypothetical opener.",
                                        },
                                        {
                                            "item_id": "b2",
                                            "blank_id": "b2",
                                            "sentence_with_blank": "But for the delay, we ___ in March.",
                                            "base_verb": "launch",
                                            "correct_answer": "would have launched",
                                            "distractors": ["will launch", "launched"],
                                            "options": [
                                                "would have launched",
                                                "will launch",
                                                "launched",
                                            ],
                                            "grammar_rule": "But for + noun takes a would-have result clause.",
                                            "explanation": "The unreal past result uses would have launched.",
                                        },
                                        {
                                            "item_id": "b3",
                                            "blank_id": "b3",
                                            "sentence_with_blank": "Supposing we ___ their terms, the partnership might have failed sooner.",
                                            "base_verb": "accept",
                                            "correct_answer": "had accepted",
                                            "distractors": ["accepted", "would accept"],
                                            "options": [
                                                "had accepted",
                                                "accepted",
                                                "would accept",
                                            ],
                                            "grammar_rule": "Supposing often takes past perfect for unreal past.",
                                            "explanation": "Supposing we had accepted fits a formal unreal past.",
                                        },
                                        {
                                            "item_id": "b4",
                                            "blank_id": "b4",
                                            "sentence_with_blank": "Had the board acted earlier, we ___ the crisis.",
                                            "base_verb": "avoid",
                                            "correct_answer": "would have avoided",
                                            "distractors": ["will avoid", "avoided"],
                                            "options": [
                                                "would have avoided",
                                                "will avoid",
                                                "avoided",
                                            ],
                                            "grammar_rule": "Inverted Had-clause pairs with would have + past participle.",
                                            "explanation": "The imagined past result uses would have avoided.",
                                        },
                                    ],
                                    "target_words_in_audio": [
                                        "Were it not for",
                                        "would have launched",
                                        "had accepted",
                                        "would have avoided",
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
                            id="write_error_advanced_hypothetical_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_ERROR_CORR",
                                activity="write",
                                task_widget="error_correction",
                                topic_override="Were it not for / But for Chains — error correction",
                                generation_instructions=(
                                    "Provide 3 sentences (a policy counterfactual on a past decision) with one error each, all tied to Were it not for / But for counterfactual chains in policy; the learner rewrites each correctly. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_read_advanced_hypothetical_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_READ_ALOUD",
                                activity="speak",
                                task_widget="read_aloud",
                                topic_override="Were it not for / But for Chains — read aloud",
                                generation_instructions=(
                                    "Write a 50–60 word passage (a policy counterfactual on a past decision) dense with Were it not for / But for counterfactual chains in policy for read-aloud; not an introductory lesson on the parent base form. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Nominalisation & Dense Impersonal Style",
                description=(
                    "Learners turn verbs into nouns and build dense impersonal sentences "
                    "(the implementation of…, a reduction in…, there was an increase in…) "
                    "typical of reports and policy writing."
                ),
                focus=(
                    "Nominalisation and dense impersonal style: verb-to-noun shifts and "
                    "formal noun phrases."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach nominalisation for dense impersonal prose.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce nominalisation.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that nominalisation turns "
                                "verbs into nouns to sound more formal and impersonal (implement → "
                                "implementation). Ask them to name one process their organisation "
                                "improved recently."
                            ),
                        ),
                        TeacherStep(
                            id="noun_phrases",
                            goal="Teach dense noun phrases.",
                            instruction=(
                                "Model the implementation of, a reduction in, an increase in using their "
                                "topic. Ask them to rewrite 'We reduced costs' as a nominal phrase "
                                "starting with A reduction in…."
                            ),
                        ),
                        TeacherStep(
                            id="impersonal",
                            goal="Teach impersonal there was / it is patterns.",
                            instruction=(
                                "Show There was a decline in… / It is clear that… without naming who "
                                "acted. Ask for one impersonal sentence about their topic."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has produced a nominal phrase at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_nominalisation",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Nominalisation in policy-style text",
                            generation_instructions=(
                                "Write a 60-75 word impersonal report excerpt using nominalisations "
                                "(implementation, reduction, assessment). Then comprehension MCQs."
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
                        id="listen_dictation_nominalisation",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="Hear nominal phrases in formal speech",
                            generation_instructions=(
                                "Generate a 35-45 word audio of four formal sentences with nominal "
                                "phrases for dictation."
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
                        id="write_sent_nominalisation",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Rewrite verbs into nominalisations",
                            generation_instructions=(
                                "Give 3 active-voice sentences and ask the learner to rewrite each using "
                                "nominalisation while keeping meaning."
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
                        id="speak_timed_nominalisation",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe outcomes with nominal phrases",
                            generation_instructions=(
                                "Ask the learner to speak about a project outcome using at least two "
                                "nominal phrases and one impersonal opener."
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
                    title="Dense Then One Clarity Unpack",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Nominalise + clarify. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Nominalise + clarify.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Dense Then One Clarity Unpack: Nominalise + clarify.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce nominalisation.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that nominalisation turns verbs into nouns to sound more formal and impersonal (implement → implementation). Ask them to name one process their organisation improved recently.",
                            ),
                            TeacherStep(
                                id="noun_phrases",
                                goal="Teach dense noun phrases.",
                                instruction="At C2 depth, push Nominalise + clarify: Model the implementation of, a reduction in, an increase in using their topic. Ask them to rewrite 'We reduced costs' as a nominal phrase starting with A reduction in….",
                            ),
                            TeacherStep(
                                id="impersonal",
                                goal="Teach impersonal there was / it is patterns.",
                                instruction="At C2 depth, push Nominalise + clarify: Show There was a decline in… / It is clear that… without naming who acted. Ask for one impersonal sentence about their topic.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has produced a nominal phrase at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_nominalisation_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Dense Then One Clarity Unpack — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a dense executive brief then a plain summary) rich in Dense nominalisation followed by one plain-language unpack. Add 3–4 comprehension MCQs where at least two require applying Dense nominalisation followed by one plain-language unpack, not only locating a noun or date. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_dictation_nominalisation_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Dense Then One Clarity Unpack — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (a dense executive brief then a plain summary) that exemplify Dense nominalisation followed by one plain-language unpack for exact dictation. Each line should highlight one feature of Dense nominalisation followed by one plain-language unpack. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_sent_nominalisation_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Dense Then One Clarity Unpack — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a dense executive brief then a plain summary) where source and target practice Dense nominalisation followed by one plain-language unpack (e.g. direct to reported, active to passive, clause reduction). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_timed_nominalisation_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Dense Then One Clarity Unpack — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a dense executive brief then a plain summary) each forcing production of Dense nominalisation followed by one plain-language unpack. Model answers must satisfy the prompt. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Complex Embedding & Clarity",
                description=(
                    "Learners manage layered subordinate clauses while keeping clarity: "
                    "punctuation, relative chains, and when to split long sentences."
                ),
                focus=(
                    "Complex embedding: layered subordinates with clear punctuation and "
                    "readable sentence length."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach complex embedding without losing clarity.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce complex embedding.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that C1 writers embed ideas "
                                "in layers but must punctuate and break sentences for clarity. Ask them "
                                "to describe a policy they follow using one subordinate clause."
                            ),
                        ),
                        TeacherStep(
                            id="layers",
                            goal="Teach layered subordinates.",
                            instruction=(
                                "Build on their sentence with a second layer (which…, where…, although…). "
                                "Ask them to add one more embedded clause without losing the main point."
                            ),
                        ),
                        TeacherStep(
                            id="clarity",
                            goal="Teach clarity and punctuation.",
                            instruction=(
                                "Show when to use commas, dashes, or a full stop instead of stacking. Ask "
                                "them to split an over-long example into two clear sentences."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has embedded and clarified at least once, ask only: Ready "
                                "to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_word_complex_embedding",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Match embedding patterns to punctuation",
                            generation_instructions=(
                                "Ask the learner to match sentence stubs to comma rules, dash use, or "
                                "need to split for clarity with layered subordinates."
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
                        id="listen_mcq_complex_embedding",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Hearing layered clauses",
                            generation_instructions=(
                                "Generate a 35-45 word description with two embedded layers; include "
                                "comprehension questions on structure."
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
                        id="write_open_complex_embedding",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_OPEN_SENT",
                            activity="write",
                            task_widget="open_text",
                            topic_override="Write clearly embedded sentences",
                            generation_instructions=(
                                "Ask for three sentences: one with two embedded clauses punctuated, one "
                                "over-long sentence they must split, one reduced for clarity."
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
                        id="speak_pic_complex_embedding",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a scene with embedded clauses",
                            generation_instructions=(
                                "Ask the learner to describe a workplace scene aloud using one "
                                "double-embedded sentence and one short follow-up for clarity."
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
                    title="Parenthetical Control",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Clear referents. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Clear referents.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Parenthetical Control: Clear referents.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce complex embedding.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that C1 writers embed ideas in layers but must punctuate and break sentences for clarity. Ask them to describe a policy they follow using one subordinate clause.",
                            ),
                            TeacherStep(
                                id="layers",
                                goal="Teach layered subordinates.",
                                instruction="At C2 depth, push Clear referents: Build on their sentence with a second layer (which…, where…, although…). Ask them to add one more embedded clause without losing the main point.",
                            ),
                            TeacherStep(
                                id="clarity",
                                goal="Teach clarity and punctuation.",
                                instruction="At C2 depth, push Clear referents: Show when to use commas, dashes, or a full stop instead of stacking. Ask them to split an over-long example into two clear sentences.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has embedded and clarified at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_complex_embedding_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Parenthetical Control — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Parenthetical embedding with clear referents and short definitions (a complex report with embedded clauses). Learners match each term to the definition that fits the depth collocation or usage. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_mcq_complex_embedding_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Parenthetical Control — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a complex report with embedded clauses) using Parenthetical embedding with clear referents. Then 3–4 MCQs: at least two must test understanding of Parenthetical embedding with clear referents (form, stance, or structure), not single-fact recall. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_open_complex_embedding_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_OPEN_SENT",
                                activity="write",
                                task_widget="open_text",
                                topic_override="Parenthetical Control — open sentences",
                                generation_instructions=(
                                    "Ask for exactly 3 learner sentences (a complex report with embedded clauses) that each demonstrate a different facet of Parenthetical embedding with clear referents. Do not ask for practice that only repeats the parent base lesson focus. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_pic_complex_embedding_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Parenthetical Control — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a complex report with embedded clauses) using Parenthetical embedding with clear referents in 4–5 connected sentences; include at least one depth-specific structure from Parenthetical embedding with clear referents. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Hedging, Boosting & Epistemic Stance",
                description=(
                    "Learners signal certainty carefully with hedges (appears to, tends "
                    "to, might) and boosters (clearly, undoubtedly) in reporting and "
                    "analysis."
                ),
                focus=(
                    "Hedging and boosting: appears to, tends to, arguably, clearly, and "
                    "epistemic stance."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach hedging and boosting for epistemic stance.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce hedging and boosting.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that hedges soften claims "
                                "while boosters strengthen them when evidence supports it. Ask them to "
                                "report one trend they are not fully sure about."
                            ),
                        ),
                        TeacherStep(
                            id="hedges",
                            goal="Teach hedges.",
                            instruction=(
                                "Model appears to, tends to, might, and arguably with their topic. Ask "
                                "them to hedge one strong claim they made earlier."
                            ),
                        ),
                        TeacherStep(
                            id="boosters",
                            goal="Teach boosters carefully.",
                            instruction=(
                                "Show when clearly or evidently is fair vs overstated. Ask them to add "
                                "one booster only where evidence in their example is strong."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has hedged or boosted appropriately once, ask only: Ready "
                                "to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_cloze_epistemic_stance",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CLOZE",
                            activity="read",
                            task_widget="fill_blanks",
                            topic_override="Hedges and boosters in analysis",
                            generation_instructions=(
                                "Write a short analysis passage with blanks for hedges and boosters "
                                "(appears to, tends to, arguably, clearly)."
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
                        id="listen_infer_epistemic_stance",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Infer stance from hedged reporting",
                            generation_instructions=(
                                "Generate a 35-45 word audio clip reporting data with mixed hedges; ask "
                                "the learner to infer certainty level."
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
                        id="write_para_epistemic_stance",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write a paragraph with stance markers",
                            generation_instructions=(
                                "Ask for a 3-4 sentence paragraph interpreting results with at least two "
                                "hedges and one justified booster."
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
                        id="speak_roleplay_epistemic_stance",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Report findings with hedges aloud",
                            generation_instructions=(
                                "Set up a roleplay where the learner presents findings to a sceptical "
                                "colleague using hedges and one clear booster."
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
                    title="Calibrate Commitment Grid",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: hedge/boost per claim. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: hedge/boost per claim.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Calibrate Commitment Grid: hedge/boost per claim.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce hedging and boosting.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that hedges soften claims while boosters strengthen them when evidence supports it. Ask them to report one trend they are not fully sure about.",
                            ),
                            TeacherStep(
                                id="hedges",
                                goal="Teach hedges.",
                                instruction="At C2 depth, push hedge/boost per claim: Model appears to, tends to, might, and arguably with their topic. Ask them to hedge one strong claim they made earlier.",
                            ),
                            TeacherStep(
                                id="boosters",
                                goal="Teach boosters carefully.",
                                instruction="At C2 depth, push hedge/boost per claim: Show when clearly or evidently is fair vs overstated. Ask them to add one booster only where evidence in their example is strong.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has hedged or boosted appropriately once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_cloze_epistemic_stance_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CLOZE",
                                activity="read",
                                task_widget="fill_blanks",
                                topic_override="Calibrate Commitment Grid — reading cloze",
                                generation_instructions=(
                                    "Write one connected 4–5-blank passage (an analyst note with graded certainty) where every blank tests Hedge and boost commitment calibrated per claim. Include at least two distinct facets of the depth angle in the passage. Do not drill only the parent base lesson pattern; the passage must read as a depth task on Calibrate Commitment Grid. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_infer_epistemic_stance_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_INFER",
                                activity="listen",
                                task_widget="listen_infer",
                                topic_override="Calibrate Commitment Grid — listening inference",
                                generation_instructions=(
                                    "Generate a 50–70 word spoken exchange (an analyst note with graded certainty) where Hedge and boost commitment calibrated per claim is implied. Ask 3 inference questions about stance, intent, or implied meaning tied to Hedge and boost commitment calibrated per claim. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_para_epistemic_stance_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Calibrate Commitment Grid — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (an analyst note with graded certainty) that must show Hedge and boost commitment calibrated per claim with clear organisation (topic sentence, support, close). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_roleplay_epistemic_stance_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_ROLEPLAY",
                                activity="speak",
                                task_widget="speak_roleplay",
                                topic_override="Calibrate Commitment Grid — roleplay",
                                generation_instructions=(
                                    "Roleplay (an analyst note with graded certainty) where the learner must use Hedge and boost commitment calibrated per claim in at least two turns; include a partner cue that elicits the depth move. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Rhetorical Grammar for Effect",
                description=(
                    "Learners use rhetorical grammar for emphasis: fronting, clefts (What "
                    "we need is…), parallelism, and inversion for punch."
                ),
                focus=(
                    "Rhetorical grammar: fronting, cleft sentences, parallelism, and "
                    "inversion for emphasis."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach rhetorical grammar for persuasive effect.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce rhetorical grammar.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that rhetorical grammar puts "
                                "key ideas in focus through fronting, clefts, and parallel structure. Ask "
                                "what message they would emphasise in a leadership talk."
                            ),
                        ),
                        TeacherStep(
                            id="clefts",
                            goal="Teach cleft and fronting patterns.",
                            instruction=(
                                "Model What we need is… and Fronting (Especially important is…). Ask them "
                                "to turn their message into one cleft sentence."
                            ),
                        ),
                        TeacherStep(
                            id="parallelism",
                            goal="Teach parallelism.",
                            instruction=(
                                "Show parallel verb phrases for rhythm (to build, to test, to launch). "
                                "Ask them to add a three-part parallel list about their topic."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used a rhetorical device at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_rhetorical_grammar",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="Rhetorical devices in text",
                            generation_instructions=(
                                "Write a short persuasive text with fronting, a cleft, and parallel "
                                "phrases. Then True/False/Not Given on which device creates emphasis."
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
                        id="listen_shadow_rhetorical_grammar",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Shadow rhetorical emphasis phrases",
                            generation_instructions=(
                                "Generate a 20-second monologue with a cleft and parallel list for "
                                "shadowing."
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
                        id="write_email_rhetorical_grammar",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Email using rhetorical grammar",
                            generation_instructions=(
                                "Ask the learner to write a short email using one cleft and one parallel "
                                "trio."
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
                        id="speak_smalltalk_rhetorical_grammar",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Casual chat with a rhetorical punch line",
                            generation_instructions=(
                                "Set up small talk where the learner closes with one fronted emphasis "
                                "line."
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
                    title="Parallelism & Antithesis",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Memorable lines. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Memorable lines.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Parallelism & Antithesis: Memorable lines.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce rhetorical grammar.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that rhetorical grammar puts key ideas in focus through fronting, clefts, and parallel structure. Ask what message they would emphasise in a leadership talk.",
                            ),
                            TeacherStep(
                                id="clefts",
                                goal="Teach cleft and fronting patterns.",
                                instruction="At C2 depth, push Memorable lines: Model What we need is… and Fronting (Especially important is…). Ask them to turn their message into one cleft sentence.",
                            ),
                            TeacherStep(
                                id="parallelism",
                                goal="Teach parallelism.",
                                instruction="At C2 depth, push Memorable lines: Show parallel verb phrases for rhythm (to build, to test, to launch). Ask them to add a three-part parallel list about their topic.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a rhetorical device at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tfng_rhetorical_grammar_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TFNG",
                                activity="read",
                                task_widget="read_tfng",
                                topic_override="Parallelism & Antithesis — true/false/not given",
                                generation_instructions=(
                                    "Write a 100–130 word passage (a rhetorical address or campaign message) about Parallelism and antithesis in memorable rhetoric lines. Provide 4–5 True/False/Not Given statements testing nuanced understanding of Parallelism and antithesis in memorable rhetoric lines, including one subtle distractor. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_shadow_rhetorical_grammar_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Parallelism & Antithesis — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (a rhetorical address or campaign message) dense with Parallelism and antithesis in memorable rhetoric lines for shadowing practice. Rhythm and phrasing should model natural C2+ delivery. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_email_rhetorical_grammar_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_EMAIL",
                                activity="write",
                                task_widget="write_email",
                                topic_override="Parallelism & Antithesis — email writing",
                                generation_instructions=(
                                    "Ask for a short professional email (a rhetorical address or campaign message) applying Parallelism and antithesis in memorable rhetoric lines with appropriate opening, body moves, and close. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_smalltalk_rhetorical_grammar_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_SMALLTALK",
                                activity="speak",
                                task_widget="speak_smalltalk",
                                topic_override="Parallelism & Antithesis — small talk",
                                generation_instructions=(
                                    "Small-talk prompts (a rhetorical address or campaign message) requiring Parallelism and antithesis in memorable rhetoric lines (echo, register shift, paraphrase, or inclusive invite) in natural replies. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Metadiscourse & Argument Architecture",
                description=(
                    "Learners signpost argument structure with metadiscourse (This "
                    "section examines…, To conclude…, Having established…) in essays and "
                    "briefings."
                ),
                focus=(
                    "Metadiscourse and argument architecture: section moves, conclusions, "
                    "and logical signposting."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach metadiscourse for argument structure.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce metadiscourse.",
                            instruction=(
                                "Greet the learner and note this is the final grammar day of the cycle. "
                                "Explain in two sentences that metadiscourse guides readers through your "
                                "argument (This section examines…, Having established…). Ask them to open "
                                "a hypothetical report section in one sentence."
                            ),
                        ),
                        TeacherStep(
                            id="moves",
                            goal="Teach section moves.",
                            instruction=(
                                "Confirm their opener. Teach To conclude, Conversely, and Having "
                                "established that…. Ask them to link two ideas with Having established…."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has used metadiscourse correctly at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_context_metadiscourse",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Metadiscourse in an argument brief",
                            generation_instructions=(
                                "Write a short argument brief with gaps for metadiscourse (This section "
                                "examines, Having established, To conclude). MCQs on best marker."
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
                        id="listen_retell_metadiscourse",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Retell a signposted mini-lecture",
                            generation_instructions=(
                                "Generate a 40-50 word signposted audio; ask retell using two "
                                "metadiscourse phrases."
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
                        id="write_paraphrase_metadiscourse",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="Paraphrase with metadiscourse markers",
                            generation_instructions=(
                                "Give informal bullet points and ask the learner to join them with "
                                "metadiscourse linkers."
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
                        id="speak_present_metadiscourse",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Short talk with argument signposts",
                            generation_instructions=(
                                "Ask for a 45-second mini presentation using at least three metadiscourse "
                                "signposts."
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
                    title="Signpost Complex Argument",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Reader guidance. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Reader guidance.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Signpost Complex Argument: Reader guidance.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce metadiscourse.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner and note this is the final grammar day of the cycle. Explain in two sentences that metadiscourse guides readers through your argument (This section examines…, Having established…). Ask them to open a hypothetical report section in one sentence.",
                            ),
                            TeacherStep(
                                id="moves",
                                goal="Teach section moves.",
                                instruction="At C2 depth, push Reader guidance: Confirm their opener. Teach To conclude, Conversely, and Having established that…. Ask them to link two ideas with Having established….",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used metadiscourse correctly at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_metadiscourse_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Signpost Complex Argument — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (a long-form argument with reader guidance) using Metadiscourse signposting through a complex argument. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Metadiscourse signposting through a complex argument. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_retell_metadiscourse_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_RETELL",
                                activity="listen",
                                task_widget="listen_retell",
                                topic_override="Signpost Complex Argument — listen and retell",
                                generation_instructions=(
                                    "Generate a 60–80 word monologue (a long-form argument with reader guidance) modeling Metadiscourse signposting through a complex argument. Ask the learner to retell including the key depth moves from Metadiscourse signposting through a complex argument. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_paraphrase_metadiscourse_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARAPHRASE",
                                activity="write",
                                task_widget="write_paraphrase",
                                topic_override="Signpost Complex Argument — paraphrase",
                                generation_instructions=(
                                    "Give 3 source sentences (a long-form argument with reader guidance) that are blunt, vague, or off-register; ask the learner to paraphrase for Metadiscourse signposting through a complex argument. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_present_metadiscourse_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PRESENT",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Signpost Complex Argument — presentation",
                                generation_instructions=(
                                    "Presentation task (a long-form argument with reader guidance): structured spoken segment showing Metadiscourse signposting through a complex argument with signposts and a clear close. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
        cefr_level="C2",
        sub_level_min=8,
        sub_level_max=8,
        days=(
            DaySource(
                title="Principled Negotiation",
                description=(
                    "Learners practise principled negotiation: interests, framing, and "
                    "durable agreement at C1 level using the same read-listen-write-speak "
                    "sequence as earlier communication weeks."
                ),
                focus="Principled negotiation: interests, framing, and durable agreement.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach principled negotiation.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce principled negotiation.",
                            instruction=(
                                "Welcome the learner to communication week. Explain in two sentences that "
                                "principled negotiation focuses on interests, not positions, and seeks "
                                "durable agreement. Ask them to describe a negotiation where interests "
                                "were hidden."
                            ),
                        ),
                        TeacherStep(
                            id="negotiation",
                            goal="Teach principled negotiation.",
                            instruction=(
                                "React warmly. Teach separating interests from positions (What matters "
                                "is…, Our underlying need is…). Ask them to reframe one position as an "
                                "interest."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_negotiation",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Principled negotiation in messages",
                            generation_instructions=(
                                "Write a negotiation exchange reframing positions as interests and ending "
                                "with a durable agreement. Comprehension questions."
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
                        id="listen_mcq_negotiation",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Listening to interests-based negotiation",
                            generation_instructions=(
                                "Generate a 35-45 word dialogue using interest-based framing. MCQs on "
                                "each party's underlying need."
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
                        id="write_sent_negotiation",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Rewrite positions into interests language",
                            generation_instructions=(
                                "Give 3 positional statements to rewrite using interest language."
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
                        id="speak_roleplay_negotiation",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Roleplay principled negotiation",
                            generation_instructions=(
                                "Roleplay a principled negotiation with interests, options, and "
                                "agreement."
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
                    title="BATNA & Objective Criteria",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Named BATNA. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Named BATNA.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — BATNA & Objective Criteria: Named BATNA.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce principled negotiation.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to communication week. Explain in two sentences that principled negotiation focuses on interests, not positions, and seeks durable agreement. Ask them to describe a negotiation where interests were hidden.",
                            ),
                            TeacherStep(
                                id="negotiation",
                                goal="Teach principled negotiation.",
                                instruction="At C2 depth, push Named BATNA: React warmly. Teach separating interests from positions (What matters is…, Our underlying need is…). Ask them to reframe one position as an interest.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_negotiation_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="BATNA & Objective Criteria — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a negotiation with explicit BATNA language) rich in Named BATNA and objective criteria in principled negotiation. Add 3–4 comprehension MCQs where at least two require applying Named BATNA and objective criteria in principled negotiation, not only locating a noun or date. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_mcq_negotiation_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="BATNA & Objective Criteria — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a negotiation with explicit BATNA language) using Named BATNA and objective criteria in principled negotiation. Then 3–4 MCQs: at least two must test understanding of Named BATNA and objective criteria in principled negotiation (form, stance, or structure), not single-fact recall. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_sent_negotiation_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="BATNA & Objective Criteria — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a negotiation with explicit BATNA language) where source and target practice Named BATNA and objective criteria in principled negotiation (e.g. direct to reported, active to passive, clause reduction). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_roleplay_negotiation_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_ROLEPLAY",
                                activity="speak",
                                task_widget="speak_roleplay",
                                topic_override="BATNA & Objective Criteria — roleplay",
                                generation_instructions=(
                                    "Roleplay (a negotiation with explicit BATNA language) where the learner must use Named BATNA and objective criteria in principled negotiation in at least two turns; include a partner cue that elicits the depth move. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Coaching Conversation",
                description=(
                    "Learners practise coaching conversations: questions, reflection, and "
                    "ownership instead of directives at C1 level using the same "
                    "read-listen-write-speak sequence as earlier communication weeks."
                ),
                focus=(
                    "Coaching conversations: questions, reflection, and ownership instead "
                    "of directives."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach coaching conversation.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce coaching conversation.",
                            instruction=(
                                "Welcome the learner to Day 2. Explain in two sentences that coaching "
                                "uses questions and reflection so the other person owns the solution. Ask "
                                "about a time someone told them what to do versus helped them think."
                            ),
                        ),
                        TeacherStep(
                            id="coaching",
                            goal="Teach coaching conversation.",
                            instruction=(
                                "Model What outcome do you want? and What options have you tried? Ask "
                                "them to coach you briefly on 'I keep missing deadlines.'"
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_coaching",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="Coaching tone in writing",
                            generation_instructions=(
                                "Write a manager message: one directive version and one coaching version. "
                                "True/False/Not Given on ownership."
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
                        id="listen_infer_coaching",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Infer coaching vs telling in conversation",
                            generation_instructions=(
                                "Generate a conversation mixing telling and coaching; infer which builds "
                                "ownership."
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
                        id="write_email_coaching",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Write coaching questions",
                            generation_instructions=(
                                "Ask the learner to write five coaching questions for a performance "
                                "issue."
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
                        id="speak_interview_coaching",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_INTERVIEW",
                            activity="speak",
                            task_widget="speak_interview",
                            topic_override="React with coaching questions in chat",
                            generation_instructions=(
                                "Mini interview: respond with coaching questions, not instructions."
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
                    title="Powerful Questions & Summary",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: No advice dump. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: No advice dump.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Powerful Questions & Summary: No advice dump.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce coaching conversation.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to Day 2. Explain in two sentences that coaching uses questions and reflection so the other person owns the solution. Ask about a time someone told them what to do versus helped them think.",
                            ),
                            TeacherStep(
                                id="coaching",
                                goal="Teach coaching conversation.",
                                instruction="At C2 depth, push No advice dump: Model What outcome do you want? and What options have you tried? Ask them to coach you briefly on 'I keep missing deadlines.'",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tfng_coaching_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TFNG",
                                activity="read",
                                task_widget="read_tfng",
                                topic_override="Powerful Questions & Summary — true/false/not given",
                                generation_instructions=(
                                    "Write a 100–130 word passage (a coaching conversation with a direct report) about Powerful coaching questions and summary without advice-dump. Provide 4–5 True/False/Not Given statements testing nuanced understanding of Powerful coaching questions and summary without advice-dump, including one subtle distractor. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_infer_coaching_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_INFER",
                                activity="listen",
                                task_widget="listen_infer",
                                topic_override="Powerful Questions & Summary — listening inference",
                                generation_instructions=(
                                    "Generate a 50–70 word spoken exchange (a coaching conversation with a direct report) where Powerful coaching questions and summary without advice-dump is implied. Ask 3 inference questions about stance, intent, or implied meaning tied to Powerful coaching questions and summary without advice-dump. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_email_coaching_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_EMAIL",
                                activity="write",
                                task_widget="write_email",
                                topic_override="Powerful Questions & Summary — email writing",
                                generation_instructions=(
                                    "Ask for a short professional email (a coaching conversation with a direct report) applying Powerful coaching questions and summary without advice-dump with appropriate opening, body moves, and close. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_interview_coaching_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_INTERVIEW",
                                activity="speak",
                                task_widget="speak_interview",
                                topic_override="Powerful Questions & Summary — interview",
                                generation_instructions=(
                                    "Interview prompts (a coaching conversation with a direct report) where answers must demonstrate Powerful coaching questions and summary without advice-dump (stance, follow-ups, or documented feedback moves). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Scenario Thinking & Strategic Options",
                description=(
                    "Learners practise scenario thinking: options, second-order effects, "
                    "and explicit trade-offs at C1 level using the same "
                    "read-listen-write-speak sequence as earlier communication weeks."
                ),
                focus="Scenario thinking: options, second-order effects, and explicit trade-offs.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach scenario thinking & strategic options.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce scenario thinking & strategic options.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that scenario thinking "
                                "weighs options, second-order effects, and trade-offs before "
                                "recommending. Ask them to compare two strategic paths they know."
                            ),
                        ),
                        TeacherStep(
                            id="structure",
                            goal="Teach scenario thinking & strategic options.",
                            instruction=(
                                "Introduce If we choose X, the knock-on effect is… and On the other "
                                "hand…. Ask them to name one second-order effect of their preferred "
                                "option."
                            ),
                        ),
                        TeacherStep(
                            id="recommend",
                            goal="Add recommendation or alignment.",
                            instruction=(
                                "Show how to end with a conditional recommendation. Ask what they would "
                                "recommend and which trade-off they accept in one sentence."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_structure_scenario_thinking",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_STRUCTURE_ID",
                            activity="read",
                            task_widget="read_structure",
                            topic_override="Scenario comparison structure",
                            generation_instructions=(
                                "Provide a three-scenario comparison text; label Options, Trade-offs, "
                                "Recommendation."
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
                        id="listen_retell_scenario_thinking",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Retell a scenario comparison",
                            generation_instructions=(
                                "Audio comparing strategic options with second-order effects; retell "
                                "recommendation."
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
                        id="write_para_scenario_thinking",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write scenario options with trade-offs",
                            generation_instructions=(
                                "Write a paragraph comparing two scenarios with explicit trade-offs."
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
                        id="speak_opinion_scenario_thinking",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_OPINION",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="State a conditional recommendation aloud",
                            generation_instructions=(
                                "Speak for 45 seconds recommending one path and one accepted trade-off."
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
                    title="Triggers & No-Regret Moves",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Scenario outline. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Scenario outline.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Triggers & No-Regret Moves: Scenario outline.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce scenario thinking & strategic options.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that scenario thinking weighs options, second-order effects, and trade-offs before recommending. Ask them to compare two strategic paths they know.",
                            ),
                            TeacherStep(
                                id="structure",
                                goal="Teach scenario thinking & strategic options.",
                                instruction="At C2 depth, push Scenario outline: Introduce If we choose X, the knock-on effect is… and On the other hand…. Ask them to name one second-order effect of their preferred option.",
                            ),
                            TeacherStep(
                                id="recommend",
                                goal="Add recommendation or alignment.",
                                instruction="At C2 depth, push Scenario outline: Show how to end with a conditional recommendation. Ask what they would recommend and which trade-off they accept in one sentence.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_structure_scenario_thinking_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_STRUCTURE_ID",
                                activity="read",
                                task_widget="read_structure",
                                topic_override="Triggers & No-Regret Moves — text structure",
                                generation_instructions=(
                                    "Provide a 4–5 paragraph outline or short text (a strategic scenario outline for leadership) about Scenario triggers and no-regret moves in scenario thinking. Ask the learner to identify structure elements (problem, cause, solution, recommendation) aligned with Scenario triggers and no-regret moves in scenario thinking. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_retell_scenario_thinking_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_RETELL",
                                activity="listen",
                                task_widget="listen_retell",
                                topic_override="Triggers & No-Regret Moves — listen and retell",
                                generation_instructions=(
                                    "Generate a 60–80 word monologue (a strategic scenario outline for leadership) modeling Scenario triggers and no-regret moves in scenario thinking. Ask the learner to retell including the key depth moves from Scenario triggers and no-regret moves in scenario thinking. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_para_scenario_thinking_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Triggers & No-Regret Moves — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (a strategic scenario outline for leadership) that must show Scenario triggers and no-regret moves in scenario thinking with clear organisation (topic sentence, support, close). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_opinion_scenario_thinking_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_OPINION",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Triggers & No-Regret Moves — opinion",
                                generation_instructions=(
                                    "Opinion task (a strategic scenario outline for leadership): state a position, support with cause→impact→solution or measurable fix aligned with Scenario triggers and no-regret moves in scenario thinking. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Executive Alignment",
                description=(
                    "Learners practise executive alignment: vision, priorities, and "
                    "accountability in tense rooms at C1 level using the same "
                    "read-listen-write-speak sequence as earlier communication weeks."
                ),
                focus="Executive alignment: vision, priorities, and accountability in tense rooms.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach executive alignment.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce executive alignment.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that executive alignment "
                                "means locking vision, priorities, and owners when leaders disagree. Ask "
                                "about a tense meeting they witnessed or led."
                            ),
                        ),
                        TeacherStep(
                            id="exec_alignment",
                            goal="Teach executive alignment.",
                            instruction=(
                                "Teach phrases like 'Let's align on the north star' and 'Who owns this by "
                                "Friday?'. Ask them to open a one-minute alignment check-in."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_comp_exec_alignment",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Executive alignment in writing",
                            generation_instructions=(
                                "Write a tense leadership transcript aligning vision, priorities, and "
                                "owners. MCQs."
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
                        id="listen_mcq_exec_alignment",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Listening to tense leadership alignment",
                            generation_instructions=(
                                "Generate a 35-45 word clip aligning executives on one priority and "
                                "owner."
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
                        id="write_bullets_exec_alignment",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_BULLETS_TO_PARA",
                            activity="write",
                            task_widget="write_bullets_to_para",
                            topic_override="Turn notes into an alignment summary",
                            generation_instructions=(
                                "Turn bullet notes into an alignment summary with owners."
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
                        id="speak_roleplay_exec_alignment",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_ROLEPLAY",
                            activity="speak",
                            task_widget="speak_roleplay",
                            topic_override="Roleplay executive alignment",
                            generation_instructions=(
                                "Roleplay opening an executive alignment moment and assigning one owner."
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
                    title="Disagree and Commit Language",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Leadership memo. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Leadership memo.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Disagree and Commit Language: Leadership memo.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce executive alignment.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that executive alignment means locking vision, priorities, and owners when leaders disagree. Ask about a tense meeting they witnessed or led.",
                            ),
                            TeacherStep(
                                id="exec_alignment",
                                goal="Teach executive alignment.",
                                instruction="At C2 depth, push Leadership memo: Teach phrases like 'Let's align on the north star' and 'Who owns this by Friday?'. Ask them to open a one-minute alignment check-in.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_comp_exec_alignment_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Disagree and Commit Language — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a leadership memo after executive disagreement) rich in Disagree-and-commit language in an executive alignment memo. Add 3–4 comprehension MCQs where at least two require applying Disagree-and-commit language in an executive alignment memo, not only locating a noun or date. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_mcq_exec_alignment_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Disagree and Commit Language — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a leadership memo after executive disagreement) using Disagree-and-commit language in an executive alignment memo. Then 3–4 MCQs: at least two must test understanding of Disagree-and-commit language in an executive alignment memo (form, stance, or structure), not single-fact recall. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_bullets_exec_alignment_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_BULLETS_TO_PARA",
                                activity="write",
                                task_widget="write_bullets_to_para",
                                topic_override="Disagree and Commit Language — bullets to paragraph",
                                generation_instructions=(
                                    "Provide bullet notes (a leadership memo after executive disagreement) about Disagree-and-commit language in an executive alignment memo; ask for one cohesive paragraph with owners, blockers, or next steps as required by the angle. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_roleplay_exec_alignment_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_ROLEPLAY",
                                activity="speak",
                                task_widget="speak_roleplay",
                                topic_override="Disagree and Commit Language — roleplay",
                                generation_instructions=(
                                    "Roleplay (a leadership memo after executive disagreement) where the learner must use Disagree-and-commit language in an executive alignment memo in at least two turns; include a partner cue that elicits the depth move. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Precision Under Cross-Examination",
                description=(
                    "Learners practise precision under cross-examination: short exact "
                    "answers without drift at C1 level using the same "
                    "read-listen-write-speak sequence as earlier communication weeks."
                ),
                focus="Precision under cross-examination: short exact answers without drift.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach precision under cross-examination.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce precision under cross-examination.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that cross-examination "
                                "demands short, exact answers without volunteering extra detail. Ask when "
                                "they have seen a speaker drift off-topic under pressure."
                            ),
                        ),
                        TeacherStep(
                            id="cross_examination",
                            goal="Teach precision under cross-examination.",
                            instruction=(
                                "Model Yes, on Tuesday, not Wednesday and That's outside my remit. Ask "
                                "them to answer sharply: 'So you approved the budget?'"
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tfng_cross_examination",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TFNG",
                            activity="read",
                            task_widget="read_tfng",
                            topic_override="Cross-examination precision in text",
                            generation_instructions=(
                                "Write a Q&A with probing questions and two precise vs drifting answers. "
                                "T/F/NG."
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
                        id="listen_infer_cross_examination",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_INFER",
                            activity="listen",
                            task_widget="listen_infer",
                            topic_override="Infer pressure questions in dialogue",
                            generation_instructions=(
                                "Dialogue with cross-examination pressure; inference on evasion."
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
                        id="write_idea_cross_examination",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_IDEA_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Write crisp answers to tough questions",
                            generation_instructions=(
                                "Write crisp answers to three hostile questions without extra detail."
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
                        id="speak_pic_cross_examination",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Explain precise answers aloud",
                            generation_instructions=(
                                "Describe aloud how to answer under cross-examination in three short "
                                "lines."
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
                    title="Scope & Non-Answer Repair",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Narrow claim. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Narrow claim.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Scope & Non-Answer Repair: Narrow claim.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce precision under cross-examination.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that cross-examination demands short, exact answers without volunteering extra detail. Ask when they have seen a speaker drift off-topic under pressure.",
                            ),
                            TeacherStep(
                                id="cross_examination",
                                goal="Teach precision under cross-examination.",
                                instruction="At C2 depth, push Narrow claim: Model Yes, on Tuesday, not Wednesday and That's outside my remit. Ask them to answer sharply: 'So you approved the budget?'",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tfng_cross_examination_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TFNG",
                                activity="read",
                                task_widget="read_tfng",
                                topic_override="Scope & Non-Answer Repair — true/false/not given",
                                generation_instructions=(
                                    "Write a 100–130 word passage (a cross-examination of a senior spokesperson) about Narrow claims and non-answer repair under cross-examination. Provide 4–5 True/False/Not Given statements testing nuanced understanding of Narrow claims and non-answer repair under cross-examination, including one subtle distractor. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_infer_cross_examination_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_INFER",
                                activity="listen",
                                task_widget="listen_infer",
                                topic_override="Scope & Non-Answer Repair — listening inference",
                                generation_instructions=(
                                    "Generate a 50–70 word spoken exchange (a cross-examination of a senior spokesperson) where Narrow claims and non-answer repair under cross-examination is implied. Ask 3 inference questions about stance, intent, or implied meaning tied to Narrow claims and non-answer repair under cross-examination. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_idea_cross_examination_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_IDEA_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Scope & Non-Answer Repair — idea paragraph",
                                generation_instructions=(
                                    "Ask for a 90–120 word paragraph (a cross-examination of a senior spokesperson) arguing Narrow claims and non-answer repair under cross-examination with claim, evidence, and explicit recommendation. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_pic_cross_examination_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Scope & Non-Answer Repair — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a cross-examination of a senior spokesperson) using Narrow claims and non-answer repair under cross-examination in 4–5 connected sentences; include at least one depth-specific structure from Narrow claims and non-answer repair under cross-examination. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Policy-Style Brief",
                description=(
                    "Learners practise policy-style briefs: context, issue, options, and "
                    "ask on one page at C1 level using the same read-listen-write-speak "
                    "sequence as earlier communication weeks."
                ),
                focus="Policy-style briefs: context, issue, options, and ask on one page.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach policy-style brief.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce policy-style brief.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that a policy brief moves "
                                "context → issue → options → ask in tight prose. Ask which section is "
                                "hardest for them to write."
                            ),
                        ),
                        TeacherStep(
                            id="policy_brief",
                            goal="Teach policy-style brief.",
                            instruction=(
                                "Contrast a fluffy opener with a crisp issue sentence. Ask them to write "
                                "one issue sentence about a problem they know."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_tone_policy_brief",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Policy brief tone and structure",
                            generation_instructions=(
                                "Provide two briefs; identify which follows context→issue→options→ask."
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
                        id="listen_tone_policy_brief",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Hear a one-minute policy brief",
                            generation_instructions=(
                                "Audio one-minute policy brief; MCQs on issue and ask."
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
                        id="write_paraphrase_policy_brief",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="Rewrite notes into a brief paragraph",
                            generation_instructions=(
                                "Give bullet notes; write a 4-sentence policy brief with a clear ask."
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
                        id="speak_smalltalk_policy_brief",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Small talk practising a one-line ask",
                            generation_instructions=(
                                "Small talk practising stating a one-sentence ask to a decision-maker."
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
                    title="Recommendation Up Front",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Option table tone. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Option table tone.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Recommendation Up Front: Option table tone.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce policy-style brief.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that a policy brief moves context → issue → options → ask in tight prose. Ask which section is hardest for them to write.",
                            ),
                            TeacherStep(
                                id="policy_brief",
                                goal="Teach policy-style brief.",
                                instruction="At C2 depth, push Option table tone: Contrast a fluffy opener with a crisp issue sentence. Ask them to write one issue sentence about a problem they know.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_tone_policy_brief_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Recommendation Up Front — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (a policy brief with options and a clear call) demonstrating Upfront recommendation with option-table tone in a policy brief. Ask the learner to identify tone/register problems or best repair choice. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_tone_policy_brief_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_TONE",
                                activity="listen",
                                task_widget="listen_tone",
                                topic_override="Recommendation Up Front — listening for tone",
                                generation_instructions=(
                                    "Generate two 30–40 word clips (a policy brief with options and a clear call) showing contrasting tone for Upfront recommendation with option-table tone in a policy brief. Ask which clip fits the required register and why. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_paraphrase_policy_brief_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARAPHRASE",
                                activity="write",
                                task_widget="write_paraphrase",
                                topic_override="Recommendation Up Front — paraphrase",
                                generation_instructions=(
                                    "Give 3 source sentences (a policy brief with options and a clear call) that are blunt, vague, or off-register; ask the learner to paraphrase for Upfront recommendation with option-table tone in a policy brief. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_smalltalk_policy_brief_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_SMALLTALK",
                                activity="speak",
                                task_widget="speak_smalltalk",
                                topic_override="Recommendation Up Front — small talk",
                                generation_instructions=(
                                    "Small-talk prompts (a policy brief with options and a clear call) requiring Upfront recommendation with option-table tone in a policy brief (echo, register shift, paraphrase, or inclusive invite) in natural replies. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Symposium Moderation",
                description=(
                    "Learners practise symposium moderation: balance experts, synthesise "
                    "views, neutral close at C1 level using the same "
                    "read-listen-write-speak sequence as earlier communication weeks."
                ),
                focus="Symposium moderation: balance experts, synthesise views, neutral close.",
                teacher=TeacherBlueprint(
                    lesson_goal="Teach symposium moderation.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce symposium moderation.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that moderating a symposium "
                                "means balancing experts, synthesising, and closing neutrally. Ask about "
                                "a panel they watched that lacked synthesis."
                            ),
                        ),
                        TeacherStep(
                            id="symposium",
                            goal="Teach symposium moderation.",
                            instruction=(
                                "Teach Let's hear a contrasting view and To synthesise, the shared theme "
                                "is…. Ask them to invite one expert and summarise two views in one "
                                "sentence."
                            ),
                        ),
                        TeacherStep(
                            id="wrap_up",
                            goal="Move to practice.",
                            instruction=(
                                "If the learner has practised the target skill at least once, ask only: "
                                "Ready to try the practice task?"
                            ),
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read_structure_symposium",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_STRUCTURE_ID",
                            activity="read",
                            task_widget="read_structure",
                            topic_override="Symposium structure in writing",
                            generation_instructions=(
                                "Provide a three-part symposium transcript (open, expert turns, "
                                "synthesis). Label parts."
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
                        id="listen_retell_symposium",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_RETELL",
                            activity="listen",
                            task_widget="listen_retell",
                            topic_override="Retell a moderated panel clip",
                            generation_instructions=(
                                "Audio of a moderator balancing experts; retell synthesis."
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
                        id="write_email_symposium",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_EMAIL",
                            activity="write",
                            task_widget="write_email",
                            topic_override="Email summarising panel synthesis",
                            generation_instructions=(
                                "Write an email summarising a panel with neutral synthesis and next step."
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
                        id="speak_present_symposium",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="Present a neutral symposium close",
                            generation_instructions=(
                                "Deliver a 45-second neutral symposium close synthesising two views."
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
                    title="Equal Voice & Thematic Close",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Multi-speaker synthesis. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Multi-speaker synthesis.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Equal Voice & Thematic Close: Multi-speaker synthesis.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce symposium moderation.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that moderating a symposium means balancing experts, synthesising, and closing neutrally. Ask about a panel they watched that lacked synthesis.",
                            ),
                            TeacherStep(
                                id="symposium",
                                goal="Teach symposium moderation.",
                                instruction="At C2 depth, push Multi-speaker synthesis: Teach Let's hear a contrasting view and To synthesise, the shared theme is…. Ask them to invite one expert and summarise two views in one sentence.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has practised the target skill at least once, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_structure_symposium_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_STRUCTURE_ID",
                                activity="read",
                                task_widget="read_structure",
                                topic_override="Equal Voice & Thematic Close — text structure",
                                generation_instructions=(
                                    "Provide a 4–5 paragraph outline or short text (moderating a multi-speaker symposium) about Equal voice and thematic synthesis in symposium moderation. Ask the learner to identify structure elements (problem, cause, solution, recommendation) aligned with Equal voice and thematic synthesis in symposium moderation. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_retell_symposium_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_RETELL",
                                activity="listen",
                                task_widget="listen_retell",
                                topic_override="Equal Voice & Thematic Close — listen and retell",
                                generation_instructions=(
                                    "Generate a 60–80 word monologue (moderating a multi-speaker symposium) modeling Equal voice and thematic synthesis in symposium moderation. Ask the learner to retell including the key depth moves from Equal voice and thematic synthesis in symposium moderation. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_email_symposium_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_EMAIL",
                                activity="write",
                                task_widget="write_email",
                                topic_override="Equal Voice & Thematic Close — email writing",
                                generation_instructions=(
                                    "Ask for a short professional email (moderating a multi-speaker symposium) applying Equal voice and thematic synthesis in symposium moderation with appropriate opening, body moves, and close. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_present_symposium_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PRESENT",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Equal Voice & Thematic Close — presentation",
                                generation_instructions=(
                                    "Presentation task (moderating a multi-speaker symposium): structured spoken segment showing Equal voice and thematic synthesis in symposium moderation with signposts and a clear close. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
        cefr_level="C2",
        sub_level_min=8,
        sub_level_max=8,
        days=(
            DaySource(
                title="Philosophy & Ideas (Accessible) - Paradigm, Empirical & Premise",
                description=(
                    "Learners build vocabulary for philosophy and ideas at accessible C1 "
                    "level (paradigm, empirical, existential, premise) and use the words "
                    "in reading, listening, writing, and speaking tasks at C1 level."
                ),
                focus=(
                    "Vocabulary for philosophy and ideas at accessible C1 level "
                    "(paradigm, empirical, existential, premise)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach philosophy and ideas vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce philosophy and ideas words.",
                            instruction=(
                                "Welcome the learner to vocabulary week. Explain in two sentences that we "
                                "use words like paradigm and empirical to talk about philosophy and "
                                "ideas. Ask them to use one of today's words in a sentence."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more philosophy and ideas words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about philosophy "
                                "and ideas."
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
                        id="read_word_match_philosophy_ideas",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Philosophy & Ideas (Accessible) Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match philosophy and ideas words (paradigm, "
                                "empirical, premise) to short definitions or context clues."
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
                        id="listen_mcq_philosophy_ideas",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="A talk about philosophy and ideas",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses philosophy and ideas, "
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
                        id="write_sent_trans_philosophy_ideas",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="philosophy and ideas vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of philosophy and ideas ideas and ask the "
                                "learner to rewrite each using precise vocabulary (paradigm, empirical, "
                                "premise)."
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
                        id="speak_pic_desc_philosophy_ideas",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a seminar or essay discussion",
                            generation_instructions=(
                                "Ask the learner to describe a photo of university seminar with students "
                                "debating ideas on a whiteboard aloud using philosophy and ideas "
                                "vocabulary naturally."
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
                    title="Define Term & Apply in Argument",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: paradigm/premise. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: paradigm/premise.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Define Term & Apply in Argument: paradigm/premise.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce philosophy and ideas words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to vocabulary week. Explain in two sentences that we use words like paradigm and empirical to talk about philosophy and ideas. Ask them to use one of today's words in a sentence.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more philosophy and ideas words.",
                                instruction="At C2 depth, push paradigm/premise: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about philosophy and ideas.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_philosophy_ideas_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Define Term & Apply in Argument — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Define a term (paradigm/premise) then apply it in argument and short definitions (a philosophy-of-ideas discussion). Learners match each term to the definition that fits the depth collocation or usage. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_mcq_philosophy_ideas_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Define Term & Apply in Argument — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a philosophy-of-ideas discussion) using Define a term (paradigm/premise) then apply it in argument. Then 3–4 MCQs: at least two must test understanding of Define a term (paradigm/premise) then apply it in argument (form, stance, or structure), not single-fact recall. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_sent_trans_philosophy_ideas_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Define Term & Apply in Argument — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a philosophy-of-ideas discussion) where source and target practice Define a term (paradigm/premise) then apply it in argument (e.g. direct to reported, active to passive, clause reduction). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_pic_desc_philosophy_ideas_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Define Term & Apply in Argument — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a philosophy-of-ideas discussion) using Define a term (paradigm/premise) then apply it in argument in 4–5 connected sentences; include at least one depth-specific structure from Define a term (paradigm/premise) then apply it in argument. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Diplomacy & International Relations - Treaty, Sovereignty & Envoy",
                description=(
                    "Learners build vocabulary for diplomacy and international relations "
                    "(treaty, sovereignty, envoy, sanction, bilateral) and use the words "
                    "in reading, listening, writing, and speaking tasks at C1 level."
                ),
                focus=(
                    "Vocabulary for diplomacy and international relations (treaty, "
                    "sovereignty, envoy, sanction, bilateral)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach diplomacy and international relations vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce diplomacy and international relations words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that diplomacy and "
                                "international relations vocabulary includes treaty, sovereignty, envoy, "
                                "sanction, bilateral. Ask them what they have read or heard recently "
                                "about diplomacy and international relations."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more diplomacy and international relations words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about diplomacy "
                                "and international relations."
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
                        id="read_context_mcq_diplomacy_ir",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Diplomacy & International Relations Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match diplomacy and international relations words "
                                "(treaty, sovereignty, envoy) to short definitions or context clues."
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
                        id="listen_dictation_diplomacy_ir",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="A talk about diplomacy and international relations",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses diplomacy and "
                                "international relations, using at least three target words. Ask "
                                "comprehension questions."
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
                        id="write_word_upgrade_diplomacy_ir",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_WORD_UPGRADE",
                            activity="write",
                            task_widget="write_word_upgrade",
                            topic_override="diplomacy and international relations vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of diplomacy and international relations ideas "
                                "and ask the learner to rewrite each using precise vocabulary (treaty, "
                                "sovereignty, envoy)."
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
                        id="speak_timed_diplomacy_ir",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe a diplomatic briefing",
                            generation_instructions=(
                                "Ask the learner to describe a photo of diplomats at a treaty signing "
                                "with flags in the background aloud using diplomacy and international "
                                "relations vocabulary naturally."
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
                    title="Treaty Language & Face-Saving",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: sovereignty/envoy. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: sovereignty/envoy.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Treaty Language & Face-Saving: sovereignty/envoy.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce diplomacy and international relations words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that diplomacy and international relations vocabulary includes treaty, sovereignty, envoy, sanction, bilateral. Ask them what they have read or heard recently about diplomacy and international relations.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more diplomacy and international relations words.",
                                instruction="At C2 depth, push sovereignty/envoy: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about diplomacy and international relations.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_diplomacy_ir_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Treaty Language & Face-Saving — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (a diplomacy or international-relations exchange) using Treaty register and face-saving (sovereignty/envoy). Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Treaty register and face-saving (sovereignty/envoy). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_dictation_diplomacy_ir_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Treaty Language & Face-Saving — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (a diplomacy or international-relations exchange) that exemplify Treaty register and face-saving (sovereignty/envoy) for exact dictation. Each line should highlight one feature of Treaty register and face-saving (sovereignty/envoy). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_word_upgrade_diplomacy_ir_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_WORD_UPGRADE",
                                activity="write",
                                task_widget="write_word_upgrade",
                                topic_override="Treaty Language & Face-Saving — word upgrade",
                                generation_instructions=(
                                    "Give 3 informal or vague sentences (a diplomacy or international-relations exchange); ask the learner to upgrade vocabulary to precise terms that express Treaty register and face-saving (sovereignty/envoy). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_timed_diplomacy_ir_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Treaty Language & Face-Saving — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a diplomacy or international-relations exchange) each forcing production of Treaty register and face-saving (sovereignty/envoy). Model answers must satisfy the prompt. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Academic Discourse - Synthesise, Juxtapose & Caveat",
                description=(
                    "Learners build vocabulary for academic discourse (synthesise, "
                    "juxtapose, dichotomy, caveat, corpus) and use the words in reading, "
                    "listening, writing, and speaking tasks at C1 level."
                ),
                focus=(
                    "Vocabulary for academic discourse (synthesise, juxtapose, dichotomy, "
                    "caveat, corpus)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach academic discourse vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce academic discourse words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that academic discourse "
                                "vocabulary includes synthesise, juxtapose, dichotomy, caveat, corpus. "
                                "Ask them what they have read or heard recently about academic discourse."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more academic discourse words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about academic "
                                "discourse."
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
                        id="read_word_match_academic_discourse",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Academic Discourse Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match academic discourse words (synthesise, "
                                "juxtapose, caveat) to short definitions or context clues."
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
                        id="listen_mcq_academic_discourse",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="A talk about academic discourse",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses academic discourse, "
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
                        id="write_para_academic_discourse",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="academic discourse vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of academic discourse ideas and ask the learner "
                                "to rewrite each using precise vocabulary (synthesise, juxtapose, "
                                "caveat)."
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
                        id="speak_pic_desc_academic_discourse",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe a journal article or lecture",
                            generation_instructions=(
                                "Ask the learner to describe a photo of researcher reviewing journal "
                                "articles in a library aloud using academic discourse vocabulary "
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
                    title="Synthesis Across Two Sources",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: synthesise/juxtapose/caveat. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: synthesise/juxtapose/caveat.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Synthesis Across Two Sources: synthesise/juxtapose/caveat.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce academic discourse words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that academic discourse vocabulary includes synthesise, juxtapose, dichotomy, caveat, corpus. Ask them what they have read or heard recently about academic discourse.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more academic discourse words.",
                                instruction="At C2 depth, push synthesise/juxtapose/caveat: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about academic discourse.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_academic_discourse_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Synthesis Across Two Sources — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Synthesise/juxtapose/caveat across two academic sources and short definitions (comparing two academic abstracts). Learners match each term to the definition that fits the depth collocation or usage. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_mcq_academic_discourse_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Synthesis Across Two Sources — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (comparing two academic abstracts) using Synthesise/juxtapose/caveat across two academic sources. Then 3–4 MCQs: at least two must test understanding of Synthesise/juxtapose/caveat across two academic sources (form, stance, or structure), not single-fact recall. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_para_academic_discourse_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Synthesis Across Two Sources — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (comparing two academic abstracts) that must show Synthesise/juxtapose/caveat across two academic sources with clear organisation (topic sentence, support, close). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_pic_desc_academic_discourse_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Synthesis Across Two Sources — picture description",
                                generation_instructions=(
                                    "Describe an image scene (comparing two academic abstracts) using Synthesise/juxtapose/caveat across two academic sources in 4–5 connected sentences; include at least one depth-specific structure from Synthesise/juxtapose/caveat across two academic sources. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Corporate Strategy - Merger, Divest & Due Diligence",
                description=(
                    "Learners build vocabulary for corporate strategy (merger, divest, "
                    "due diligence, benchmark, pivot) and use the words in reading, "
                    "listening, writing, and speaking tasks at C1 level."
                ),
                focus=(
                    "Vocabulary for corporate strategy (merger, divest, due diligence, "
                    "benchmark, pivot)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach corporate strategy vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce corporate strategy words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that corporate strategy "
                                "vocabulary includes merger, divest, due diligence, benchmark, pivot. Ask "
                                "them what they have read or heard recently about corporate strategy."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more corporate strategy words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about corporate "
                                "strategy."
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
                        id="read_context_mcq_corp_strategy",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Corporate Strategy Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match corporate strategy words (merger, due "
                                "diligence, pivot) to short definitions or context clues."
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
                        id="listen_dictation_corp_strategy",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="A talk about corporate strategy",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses corporate strategy, "
                                "using at least three target words. Ask comprehension questions."
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
                        id="write_paraphrase_corp_strategy",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARAPHRASE",
                            activity="write",
                            task_widget="write_paraphrase",
                            topic_override="corporate strategy vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of corporate strategy ideas and ask the learner "
                                "to rewrite each using precise vocabulary (merger, due diligence, pivot)."
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
                        id="speak_timed_corp_strategy",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe a board strategy session",
                            generation_instructions=(
                                "Ask the learner to describe a photo of executives reviewing merger "
                                "documents in a boardroom aloud using corporate strategy vocabulary "
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
                    title="M&A Rationale & Diligence Questions",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: merger/divest. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: merger/divest.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — M&A Rationale & Diligence Questions: merger/divest.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce corporate strategy words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that corporate strategy vocabulary includes merger, divest, due diligence, benchmark, pivot. Ask them what they have read or heard recently about corporate strategy.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more corporate strategy words.",
                                instruction="At C2 depth, push merger/divest: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about corporate strategy.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_corp_strategy_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="M&A Rationale & Diligence Questions — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (a corporate strategy M&A review) using M&A rationale with merger/divest diligence questions. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate M&A rationale with merger/divest diligence questions. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_dictation_corp_strategy_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="M&A Rationale & Diligence Questions — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (a corporate strategy M&A review) that exemplify M&A rationale with merger/divest diligence questions for exact dictation. Each line should highlight one feature of M&A rationale with merger/divest diligence questions. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_paraphrase_corp_strategy_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARAPHRASE",
                                activity="write",
                                task_widget="write_paraphrase",
                                topic_override="M&A Rationale & Diligence Questions — paraphrase",
                                generation_instructions=(
                                    "Give 3 source sentences (a corporate strategy M&A review) that are blunt, vague, or off-register; ask the learner to paraphrase for M&A rationale with merger/divest diligence questions. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_timed_corp_strategy_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="M&A Rationale & Diligence Questions — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a corporate strategy M&A review) each forcing production of M&A rationale with merger/divest diligence questions. Model answers must satisfy the prompt. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Discourse & Framing - Subtext, Connotation & Rhetoric",
                description=(
                    "Learners build vocabulary for discourse and framing (subtext, "
                    "connotation, polemic, rhetoric, nuance) and use the words in "
                    "reading, listening, writing, and speaking tasks at C1 level."
                ),
                focus=(
                    "Vocabulary for discourse and framing (subtext, connotation, polemic, "
                    "rhetoric, nuance)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach discourse and framing vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce discourse and framing words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that discourse and framing "
                                "vocabulary includes subtext, connotation, polemic, rhetoric, nuance. Ask "
                                "them what they have read or heard recently about discourse and framing."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more discourse and framing words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about discourse "
                                "and framing."
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
                        id="read_word_match_discourse_framing",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Discourse & Framing Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match discourse and framing words (subtext, "
                                "connotation, rhetoric) to short definitions or context clues."
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
                        id="listen_mcq_discourse_framing",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="A talk about discourse and framing",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses discourse and framing, "
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
                        id="write_sent_trans_discourse_framing",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="discourse and framing vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of discourse and framing ideas and ask the "
                                "learner to rewrite each using precise vocabulary (subtext, connotation, "
                                "rhetoric)."
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
                        id="speak_pic_desc_discourse_framing",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Describe media or political commentary",
                            generation_instructions=(
                                "Ask the learner to describe a photo of commentator analysing speeches on "
                                "a news panel aloud using discourse and framing vocabulary naturally."
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
                    title="Reframe Opponent's Metaphor",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Respectful reframe. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Respectful reframe.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Reframe Opponent's Metaphor: Respectful reframe.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce discourse and framing words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that discourse and framing vocabulary includes subtext, connotation, polemic, rhetoric, nuance. Ask them what they have read or heard recently about discourse and framing.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more discourse and framing words.",
                                instruction="At C2 depth, push Respectful reframe: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about discourse and framing.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_discourse_framing_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Reframe Opponent's Metaphor — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Respectful reframe of an opponent's metaphor or framing and short definitions (a discourse debate on framing). Learners match each term to the definition that fits the depth collocation or usage. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_mcq_discourse_framing_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Reframe Opponent's Metaphor — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a discourse debate on framing) using Respectful reframe of an opponent's metaphor or framing. Then 3–4 MCQs: at least two must test understanding of Respectful reframe of an opponent's metaphor or framing (form, stance, or structure), not single-fact recall. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_sent_trans_discourse_framing_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Reframe Opponent's Metaphor — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a discourse debate on framing) where source and target practice Respectful reframe of an opponent's metaphor or framing (e.g. direct to reported, active to passive, clause reduction). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_pic_desc_discourse_framing_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Reframe Opponent's Metaphor — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a discourse debate on framing) using Respectful reframe of an opponent's metaphor or framing in 4–5 connected sentences; include at least one depth-specific structure from Respectful reframe of an opponent's metaphor or framing. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Precision Meta-Language - Cogent, Succinct & Granular",
                description=(
                    "Learners build vocabulary for precision meta-language about language "
                    "itself (cogent, succinct, equivocate, articulate, granular) and use "
                    "the words in reading, listening, writing, and speaking tasks at C1 "
                    "level."
                ),
                focus=(
                    "Vocabulary for precision meta-language about language itself "
                    "(cogent, succinct, equivocate, articulate, granular)."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach precision meta-language vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce precision meta-language words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that precision meta-language "
                                "vocabulary includes cogent, succinct, equivocate, articulate, granular. "
                                "Ask them what they have read or heard recently about precision "
                                "meta-language."
                            ),
                        ),
                        TeacherStep(
                            id="more_words",
                            goal="Practise more precision meta-language words.",
                            instruction=(
                                "Confirm strong words. Ask what another key word means, then preview "
                                "today's reading, listening, writing, and speaking tasks about precision "
                                "meta-language."
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
                        id="read_context_mcq_meta_language",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CONTEXT_MCQ",
                            activity="read",
                            task_widget="read_context_mcq",
                            topic_override="Precision Meta-Language Vocabulary",
                            generation_instructions=(
                                "Ask the learner to match precision meta-language words (cogent, "
                                "succinct, equivocate) to short definitions or context clues."
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
                        id="listen_dictation_meta_language",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_DICTATION",
                            activity="listen",
                            task_widget="listen_dictation",
                            topic_override="A talk about precision meta-language",
                            generation_instructions=(
                                "Generate a short scenario where someone discusses precision "
                                "meta-language, using at least three target words. Ask comprehension "
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
                        id="write_word_upgrade_meta_language",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_WORD_UPGRADE",
                            activity="write",
                            task_widget="write_word_upgrade",
                            topic_override="precision meta-language vocabulary in writing",
                            generation_instructions=(
                                "Give wordy descriptions of precision meta-language ideas and ask the "
                                "learner to rewrite each using precise vocabulary (cogent, succinct, "
                                "equivocate)."
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
                        id="speak_timed_meta_language",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe an editing or coaching session",
                            generation_instructions=(
                                "Ask the learner to describe a photo of editor marking a draft for cogent "
                                "and succinct style aloud using precision meta-language vocabulary "
                                "naturally."
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
                    title="Edit for Cogency & Granularity",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Revise vague text. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Revise vague text.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Edit for Cogency & Granularity: Revise vague text.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce precision meta-language words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that precision meta-language vocabulary includes cogent, succinct, equivocate, articulate, granular. Ask them what they have read or heard recently about precision meta-language.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more precision meta-language words.",
                                instruction="At C2 depth, push Revise vague text: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about precision meta-language.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_context_mcq_meta_language_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_CONTEXT_MCQ",
                                activity="read",
                                task_widget="read_context_mcq",
                                topic_override="Edit for Cogency & Granularity — vocabulary in context",
                                generation_instructions=(
                                    "Write a 80–110 word passage (editing an imprecise executive draft) using Revise vague text for cogency and granularity. Create 4 MCQs choosing the best word/phrase for each gap to demonstrate Revise vague text for cogency and granularity. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_dictation_meta_language_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_DICTATION",
                                activity="listen",
                                task_widget="listen_dictation",
                                topic_override="Edit for Cogency & Granularity — dictation",
                                generation_instructions=(
                                    "Generate 4 short audio lines (editing an imprecise executive draft) that exemplify Revise vague text for cogency and granularity for exact dictation. Each line should highlight one feature of Revise vague text for cogency and granularity. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_word_upgrade_meta_language_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_WORD_UPGRADE",
                                activity="write",
                                task_widget="write_word_upgrade",
                                topic_override="Edit for Cogency & Granularity — word upgrade",
                                generation_instructions=(
                                    "Give 3 informal or vague sentences (editing an imprecise executive draft); ask the learner to upgrade vocabulary to precise terms that express Revise vague text for cogency and granularity. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_timed_meta_language_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Edit for Cogency & Granularity — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (editing an imprecise executive draft) each forcing production of Revise vague text for cogency and granularity. Model answers must satisfy the prompt. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Review & Word Building - Consolidate Week 23",
                description=(
                    "Learners build vocabulary for the week's C1 vocabulary across "
                    "philosophy, diplomacy, academia, strategy, discourse, and "
                    "meta-language and use the words in reading, listening, writing, and "
                    "speaking tasks at C1 level."
                ),
                focus=(
                    "Vocabulary for the week's C1 vocabulary across philosophy, "
                    "diplomacy, academia, strategy, discourse, and meta-language."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Teach review and word building vocabulary.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce review and word building words.",
                            instruction=(
                                "Greet the learner. Explain in two sentences that review and word "
                                "building vocabulary includes review words from week 23. Ask them what "
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
                        id="read_word_match_review_w23",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_WORD_MATCH",
                            activity="read",
                            task_widget="read_word_match",
                            topic_override="Week 23 vocabulary review",
                            generation_instructions=(
                                "Match week 23 target words to definitions across all domains."
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
                        id="listen_mcq_review_w23",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Mixed C1 vocabulary listening",
                            generation_instructions=(
                                "Short audio using six week-23 words; comprehension questions."
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
                        id="write_para_review_w23",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_PARA",
                            activity="write",
                            task_widget="write_paragraph",
                            topic_override="Word-building and precision writing",
                            generation_instructions=(
                                "Ask the learner to build three words with prefixes/suffixes and use each "
                                "in a sentence."
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
                        id="speak_timed_review_w23",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Describe a scene using week 23 words",
                            generation_instructions=(
                                "Describe a photo collage using at least five week-23 words aloud."
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
                    title="Discipline-Spanning Collage",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Formal integration. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Formal integration.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Discipline-Spanning Collage: Formal integration.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Introduce review and word building words.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Greet the learner. Explain in two sentences that review and word building vocabulary includes review words from week 23. Ask them what they have read or heard recently about review and word building.",
                            ),
                            TeacherStep(
                                id="more_words",
                                goal="Practise more review and word building words.",
                                instruction="At C2 depth, push Formal integration: Confirm strong words. Ask what another key word means, then preview today's reading, listening, writing, and speaking tasks about review and word building.",
                            ),
                            TeacherStep(
                                id="wrap_up",
                                goal="Move to practice.",
                                instruction="If the learner has used a target word correctly, ask only: Ready to try the practice task?",
                            ),
                        ),
                    ),
                    activities=(
                        ActivityBlueprint(
                            id="read_word_match_review_w23_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_WORD_MATCH",
                                activity="read",
                                task_widget="read_word_match",
                                topic_override="Discipline-Spanning Collage — word–definition match",
                                generation_instructions=(
                                    "Create 6–8 target words/phrases for Formal integration collage across week 7 lexis and short definitions (a discipline-spanning formal paragraph). Learners match each term to the definition that fits the depth collocation or usage. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_mcq_review_w23_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Discipline-Spanning Collage — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a discipline-spanning formal paragraph) using Formal integration collage across week 7 lexis. Then 3–4 MCQs: at least two must test understanding of Formal integration collage across week 7 lexis (form, stance, or structure), not single-fact recall. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_para_review_w23_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_PARA",
                                activity="write",
                                task_widget="write_paragraph",
                                topic_override="Discipline-Spanning Collage — paragraph writing",
                                generation_instructions=(
                                    "Ask for one 80–110 word paragraph (a discipline-spanning formal paragraph) that must show Formal integration collage across week 7 lexis with clear organisation (topic sentence, support, close). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_timed_review_w23_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Discipline-Spanning Collage — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (a discipline-spanning formal paragraph) each forcing production of Formal integration collage across week 7 lexis. Model answers must satisfy the prompt. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
        cefr_level="C2",
        sub_level_min=8,
        sub_level_max=8,
        days=(
            DaySource(
                title="Thought Leadership",
                description=(
                    "Learners build confidence to state a clear point of view under "
                    "pushback: claim, reason, and calm restatement, using the same "
                    "read-listen-write-speak sequence at C1 level."
                ),
                focus=(
                    "State a clear point of view under pushback: claim, reason, and calm "
                    "restatement."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to state a clear point of view under pushback.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at C1. Explain in two sentences "
                                "that state a clear point of view under pushback becomes easier with "
                                "preparation and deliberate structure. Ask them to name one high-stakes "
                                "situation they want to handle better."
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
                        id="read_comp_mcq_thought_leadership",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="POV under pushback",
                            generation_instructions=(
                                "Story where a leader states a POV and faces pushback; MCQs on claim and "
                                "reason."
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
                        id="listen_shadow_thought_leadership",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Pushback listening",
                            generation_instructions=(
                                "15-second clip with polite disagreement for shadowing."
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
                        id="write_sent_trans_thought_leadership",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Restate POV in writing",
                            generation_instructions=(
                                "Rewrite defensive lines into calm POV restatements."
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
                        id="speak_read_aloud_thought_leadership",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_READ_ALOUD",
                            activity="speak",
                            task_widget="read_aloud",
                            topic_override="Read POV passage aloud",
                            generation_instructions=(
                                "55-70 word passage stating a clear POV to read aloud."
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
                    title="Thesis, Objection, Response",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Publishable spoken essay. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Publishable spoken essay.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Thesis, Objection, Response: Publishable spoken essay.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at C1. Explain in two sentences that state a clear point of view under pushback becomes easier with preparation and deliberate structure. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push Publishable spoken essay: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_comp_mcq_thought_leadership_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Thesis, Objection, Response — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (thought leadership on a contested idea) rich in Thesis, objection, and response in a publishable spoken essay. Add 3–4 comprehension MCQs where at least two require applying Thesis, objection, and response in a publishable spoken essay, not only locating a noun or date. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_shadow_thought_leadership_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Thesis, Objection, Response — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (thought leadership on a contested idea) dense with Thesis, objection, and response in a publishable spoken essay for shadowing practice. Rhythm and phrasing should model natural C2+ delivery. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_sent_trans_thought_leadership_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Thesis, Objection, Response — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (thought leadership on a contested idea) where source and target practice Thesis, objection, and response in a publishable spoken essay (e.g. direct to reported, active to passive, clause reduction). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_read_aloud_thought_leadership_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_READ_ALOUD",
                                activity="speak",
                                task_widget="read_aloud",
                                topic_override="Thesis, Objection, Response — read aloud",
                                generation_instructions=(
                                    "Write a 50–60 word passage (thought leadership on a contested idea) dense with Thesis, objection, and response in a publishable spoken essay for read-aloud; not an introductory lesson on the parent base form. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Socratic Persuasion",
                description=(
                    "Learners build confidence to persuade with questions: draw out "
                    "assumptions and guide others to your conclusion, using the same "
                    "read-listen-write-speak sequence at C1 level."
                ),
                focus=(
                    "Persuade with questions: draw out assumptions and guide others to "
                    "your conclusion."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to persuade with questions.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at C1. Explain in two sentences "
                                "that persuade with questions becomes easier with preparation and "
                                "deliberate structure. Ask them to name one high-stakes situation they "
                                "want to handle better."
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
                        id="read_tone_id_socratic",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Socratic tone in text",
                            generation_instructions=(
                                "Two persuasion excerpts; identify which uses questions rather than "
                                "monologue."
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
                        id="listen_mcq_socratic",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Persuasion by questions",
                            generation_instructions=(
                                "Audio using Socratic questions; inference on assumptions drawn out."
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
                        id="write_timed_socratic",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Timed Socratic writing",
                            generation_instructions=(
                                "Timed paragraph persuading with three questions and a brief conclusion."
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
                        id="speak_timed_socratic",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_TIMED",
                            activity="speak",
                            task_widget="speak_timed",
                            topic_override="Timed Socratic speaking",
                            generation_instructions=(
                                "Three timed prompts to persuade using questions, not lectures."
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
                    title="Question Ladder to Assumption",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: 3 non-hostile Qs. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: 3 non-hostile Qs.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Question Ladder to Assumption: 3 non-hostile Qs.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at C1. Explain in two sentences that persuade with questions becomes easier with preparation and deliberate structure. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push 3 non-hostile Qs: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_tone_id_socratic_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Question Ladder to Assumption — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (Socratic persuasion in a professional setting) demonstrating A ladder of three non-hostile questions to surface assumptions. Ask the learner to identify tone/register problems or best repair choice. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_mcq_socratic_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Question Ladder to Assumption — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (Socratic persuasion in a professional setting) using A ladder of three non-hostile questions to surface assumptions. Then 3–4 MCQs: at least two must test understanding of A ladder of three non-hostile questions to surface assumptions (form, stance, or structure), not single-fact recall. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_timed_socratic_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="Question Ladder to Assumption — timed writing",
                                generation_instructions=(
                                    "Timed writing (Socratic persuasion in a professional setting): produce a structured response demonstrating A ladder of three non-hostile questions to surface assumptions within the time limit; include clear signposts or moves from the depth angle. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_timed_socratic_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_TIMED",
                                activity="speak",
                                task_widget="speak_timed",
                                topic_override="Question Ladder to Assumption — timed speaking",
                                generation_instructions=(
                                    "Create exactly 3 speaking prompts (Socratic persuasion in a professional setting) each forcing production of A ladder of three non-hostile questions to surface assumptions. Model answers must satisfy the prompt. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Impact & Legacy Narrative",
                description=(
                    "Learners build confidence to tell an impact and legacy narrative "
                    "beyond self: why it matters to others, using the same "
                    "read-listen-write-speak sequence at C1 level."
                ),
                focus="Tell an impact and legacy narrative beyond self: why it matters to others.",
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to tell an impact and legacy narrative beyond self.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at C1. Explain in two sentences "
                                "that tell an impact and legacy narrative beyond self becomes easier with "
                                "preparation and deliberate structure. Ask them to name one high-stakes "
                                "situation they want to handle better."
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
                        id="read_comp_mcq_legacy",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Legacy narrative comprehension",
                            generation_instructions=(
                                "Story about impact beyond self; MCQs on why it matters to others."
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
                        id="listen_tone_legacy",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Tone in a legacy talk",
                            generation_instructions=(
                                "Leader describing legacy and community impact; tone questions."
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
                        id="write_sent_trans_legacy",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Legacy sentence transforms",
                            generation_instructions=(
                                "Transform self-focused sentences into legacy-focused statements."
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
                        id="speak_pic_desc_legacy",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Legacy picture description",
                            generation_instructions=(
                                "Describe a photo of community impact using legacy vocabulary."
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
                    title="Values & Impact Evidence",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Legacy arc. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Legacy arc.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Values & Impact Evidence: Legacy arc.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at C1. Explain in two sentences that tell an impact and legacy narrative beyond self becomes easier with preparation and deliberate structure. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push Legacy arc: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_comp_mcq_legacy_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Values & Impact Evidence — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a legacy or impact story for an organisation) rich in Legacy narrative with values and impact evidence. Add 3–4 comprehension MCQs where at least two require applying Legacy narrative with values and impact evidence, not only locating a noun or date. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_tone_legacy_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_TONE",
                                activity="listen",
                                task_widget="listen_tone",
                                topic_override="Values & Impact Evidence — listening for tone",
                                generation_instructions=(
                                    "Generate two 30–40 word clips (a legacy or impact story for an organisation) showing contrasting tone for Legacy narrative with values and impact evidence. Ask which clip fits the required register and why. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_sent_trans_legacy_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Values & Impact Evidence — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a legacy or impact story for an organisation) where source and target practice Legacy narrative with values and impact evidence (e.g. direct to reported, active to passive, clause reduction). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_pic_desc_legacy_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Values & Impact Evidence — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a legacy or impact story for an organisation) using Legacy narrative with values and impact evidence in 4–5 connected sentences; include at least one depth-specific structure from Legacy narrative with values and impact evidence. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Hostile Interview Recovery",
                description=(
                    "Learners build confidence to recover in hostile interviews: bridge, "
                    "redirect, and stay concise, using the same read-listen-write-speak "
                    "sequence at C1 level."
                ),
                focus="Recover in hostile interviews: bridge, redirect, and stay concise.",
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to recover in hostile interviews.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at C1. Explain in two sentences "
                                "that recover in hostile interviews becomes easier with preparation and "
                                "deliberate structure. Ask them to name one high-stakes situation they "
                                "want to handle better."
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
                        id="read_tone_id_hostile_interview",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="Hostile interview tone",
                            generation_instructions=(
                                "Two interview answers; identify which bridges and redirects concisely."
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
                        id="listen_shadow_hostile_interview",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Recovery shadowing",
                            generation_instructions=(
                                "Clip of a tough question answered with bridge and redirect for "
                                "shadowing."
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
                        id="write_timed_hostile_interview",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Timed bridge-and-redirect writing",
                            generation_instructions=(
                                "Timed answers to three hostile questions using bridge + redirect."
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
                        id="speak_smalltalk_hostile_interview",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_SMALLTALK",
                            activity="speak",
                            task_widget="speak_smalltalk",
                            topic_override="Hostile interview small talk",
                            generation_instructions=(
                                "Small talk practising one bridge phrase and one redirect."
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
                    title="Bridge, Clarify, Bounded Answer",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Trap question recovery. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Trap question recovery.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Bridge, Clarify, Bounded Answer: Trap question recovery.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at C1. Explain in two sentences that recover in hostile interviews becomes easier with preparation and deliberate structure. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push Trap question recovery: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_tone_id_hostile_interview_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Bridge, Clarify, Bounded Answer — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (recovery from a trap question in media interview) demonstrating Bridge, clarify, and bounded answer under hostile interview. Ask the learner to identify tone/register problems or best repair choice. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_shadow_hostile_interview_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Bridge, Clarify, Bounded Answer — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (recovery from a trap question in media interview) dense with Bridge, clarify, and bounded answer under hostile interview for shadowing practice. Rhythm and phrasing should model natural C2+ delivery. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_timed_hostile_interview_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="Bridge, Clarify, Bounded Answer — timed writing",
                                generation_instructions=(
                                    "Timed writing (recovery from a trap question in media interview): produce a structured response demonstrating Bridge, clarify, and bounded answer under hostile interview within the time limit; include clear signposts or moves from the depth angle. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_smalltalk_hostile_interview_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_SMALLTALK",
                                activity="speak",
                                task_widget="speak_smalltalk",
                                topic_override="Bridge, Clarify, Bounded Answer — small talk",
                                generation_instructions=(
                                    "Small-talk prompts (recovery from a trap question in media interview) requiring Bridge, clarify, and bounded answer under hostile interview (echo, register shift, paraphrase, or inclusive invite) in natural replies. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Senior-Leader Pitch",
                description=(
                    "Learners build confidence to deliver a ~2-minute senior-leader "
                    "pitch: stakes, insight, and ask, using the same "
                    "read-listen-write-speak sequence at C1 level."
                ),
                focus="Deliver a ~2-minute senior-leader pitch: stakes, insight, and ask.",
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to deliver a ~2-minute senior-leader pitch.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at C1. Explain in two sentences "
                                "that deliver a ~2-minute senior-leader pitch becomes easier with "
                                "preparation and deliberate structure. Ask them to name one high-stakes "
                                "situation they want to handle better."
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
                        id="read_comp_mcq_senior_pitch",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="Senior pitch comprehension",
                            generation_instructions=(
                                "Short pitch text; questions on stakes, insight, and ask."
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
                        id="listen_mcq_senior_pitch",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_MCQ",
                            activity="listen",
                            task_widget="listen_mcq",
                            topic_override="Stakes and ask listening",
                            generation_instructions=(
                                "Audio of a 90-second senior pitch; MCQs on ask and stakes."
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
                        id="write_sent_trans_senior_pitch",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_SENT_TRANS",
                            activity="write",
                            task_widget="sentence_transform",
                            topic_override="Pitch sentence transforms",
                            generation_instructions=(
                                "Rewrite a vague pitch into stakes → insight → ask in four sentences."
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
                        id="speak_pic_desc_senior_pitch",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PIC_DESC",
                            activity="speak",
                            task_widget="speak_pic_desc",
                            topic_override="Two-minute pitch speaking",
                            generation_instructions=(
                                "Describe delivering a two-minute senior-leader pitch aloud."
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
                    title="Strategic Fit & Governance",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: C-suite ask. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: C-suite ask.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Strategic Fit & Governance: C-suite ask.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at C1. Explain in two sentences that deliver a ~2-minute senior-leader pitch becomes easier with preparation and deliberate structure. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push C-suite ask: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_comp_mcq_senior_pitch_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Strategic Fit & Governance — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (a senior-leader pitch with governance asks) rich in Strategic fit and governance language in a C-suite pitch. Add 3–4 comprehension MCQs where at least two require applying Strategic fit and governance language in a C-suite pitch, not only locating a noun or date. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_mcq_senior_pitch_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_MCQ",
                                activity="listen",
                                task_widget="listen_mcq",
                                topic_override="Strategic Fit & Governance — listening MCQ",
                                generation_instructions=(
                                    "Generate a 70–100 word spoken script (a senior-leader pitch with governance asks) using Strategic fit and governance language in a C-suite pitch. Then 3–4 MCQs: at least two must test understanding of Strategic fit and governance language in a C-suite pitch (form, stance, or structure), not single-fact recall. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_sent_trans_senior_pitch_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_SENT_TRANS",
                                activity="write",
                                task_widget="sentence_transform",
                                topic_override="Strategic Fit & Governance — sentence transformation",
                                generation_instructions=(
                                    "Provide 3 transform items (a senior-leader pitch with governance asks) where source and target practice Strategic fit and governance language in a C-suite pitch (e.g. direct to reported, active to passive, clause reduction). C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_pic_desc_senior_pitch_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PIC_DESC",
                                activity="speak",
                                task_widget="speak_pic_desc",
                                topic_override="Strategic Fit & Governance — picture description",
                                generation_instructions=(
                                    "Describe an image scene (a senior-leader pitch with governance asks) using Strategic fit and governance language in a C-suite pitch in 4–5 connected sentences; include at least one depth-specific structure from Strategic fit and governance language in a C-suite pitch. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="TED-Style Arc",
                description=(
                    "Learners build confidence to deliver a TED-style arc: hook, insight, "
                    "memorable close, using the same read-listen-write-speak sequence at "
                    "C1 level."
                ),
                focus="Deliver a ted-style arc: hook, insight, memorable close.",
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to deliver a TED-style arc.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at C1. Explain in two sentences "
                                "that deliver a TED-style arc becomes easier with preparation and "
                                "deliberate structure. Ask them to name one high-stakes situation they "
                                "want to handle better."
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
                        id="read_tone_id_ted_arc",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_TONE_ID",
                            activity="read",
                            task_widget="read_tone_id",
                            topic_override="TED arc comprehension",
                            generation_instructions=(
                                "Identify hook, insight, and memorable close in a short talk transcript."
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
                        id="listen_tone_ted_arc",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_TONE",
                            activity="listen",
                            task_widget="listen_tone",
                            topic_override="Hook and close listening",
                            generation_instructions=(
                                "Audio with clear hook and close; MCQs on structure."
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
                        id="write_timed_ted_arc",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="TED arc writing",
                            generation_instructions=(
                                "Timed paragraph with hook, one insight, and memorable close."
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
                        id="speak_present_ted_arc",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_PRESENT",
                            activity="speak",
                            task_widget="speak_present",
                            topic_override="TED-style presentation",
                            generation_instructions=(
                                "45-second TED-style segment with hook, insight, close."
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
                    title="Hook, Idea, CTA + Pauses",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Deliberate rhythm. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Deliberate rhythm.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Hook, Idea, CTA + Pauses: Deliberate rhythm.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at C1. Explain in two sentences that deliver a TED-style arc becomes easier with preparation and deliberate structure. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push Deliberate rhythm: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_tone_id_ted_arc_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_TONE_ID",
                                activity="read",
                                task_widget="read_tone_id",
                                topic_override="Hook, Idea, CTA + Pauses — tone identification",
                                generation_instructions=(
                                    "Provide 3 short messages (a TED-style talk segment) demonstrating Hook–idea–CTA with deliberate rhythm and pauses. Ask the learner to identify tone/register problems or best repair choice. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_tone_ted_arc_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_TONE",
                                activity="listen",
                                task_widget="listen_tone",
                                topic_override="Hook, Idea, CTA + Pauses — listening for tone",
                                generation_instructions=(
                                    "Generate two 30–40 word clips (a TED-style talk segment) showing contrasting tone for Hook–idea–CTA with deliberate rhythm and pauses. Ask which clip fits the required register and why. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_timed_ted_arc_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="Hook, Idea, CTA + Pauses — timed writing",
                                generation_instructions=(
                                    "Timed writing (a TED-style talk segment): produce a structured response demonstrating Hook–idea–CTA with deliberate rhythm and pauses within the time limit; include clear signposts or moves from the depth angle. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_present_ted_arc_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_PRESENT",
                                activity="speak",
                                task_widget="speak_present",
                                topic_override="Hook, Idea, CTA + Pauses — presentation",
                                generation_instructions=(
                                    "Presentation task (a TED-style talk segment): structured spoken segment showing Hook–idea–CTA with deliberate rhythm and pauses with signposts and a clear close. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                title="Full Confidence Showcase (C1)",
                description=(
                    "Learners build confidence to integrate C1 confidence skills in one "
                    "capstone: POV, Socratic move, legacy, and memorable close, using the "
                    "same read-listen-write-speak sequence at C1 level."
                ),
                focus=(
                    "Integrate c1 confidence skills in one capstone: pov, socratic move, "
                    "legacy, and memorable close."
                ),
                teacher=TeacherBlueprint(
                    lesson_goal="Build confidence to integrate C1 confidence skills in one capstone.",
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Frame the skill as small steps.",
                            instruction=(
                                "Welcome the learner to confidence week at C1. Explain in two sentences "
                                "that integrate C1 confidence skills in one capstone becomes easier with "
                                "preparation and deliberate structure. Ask them to name one high-stakes "
                                "situation they want to handle better."
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
                        id="read_comp_mcq_showcase_w24",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_COMP_MCQ",
                            activity="read",
                            task_widget="read_comp_mcq",
                            topic_override="C1 confidence integration story",
                            generation_instructions=(
                                "Write an encouraging story where the speaker holds a POV under pushback, "
                                "uses one Socratic question, states legacy impact, and closes memorably. "
                                "MCQs."
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
                        id="listen_shadow_showcase_w24",
                        sequence=2,
                        task=TaskBlueprint(
                            archetype_id="LISTEN_SHADOW",
                            activity="listen",
                            task_widget="listen_shadow",
                            topic_override="Capstone shadowing clip",
                            generation_instructions=(
                                "Generate a confident 20-second capstone clip mixing POV, question, and "
                                "close for shadowing."
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
                        id="write_timed_showcase_w24",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_TIMED",
                            activity="write",
                            task_widget="write_timed",
                            topic_override="Timed integrated C1 confidence writing",
                            generation_instructions=(
                                "Ask for a timed paragraph integrating POV, one question, legacy, and a "
                                "memorable close."
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
                        id="speak_debate_showcase_w24",
                        sequence=4,
                        task=TaskBlueprint(
                            archetype_id="SPEAK_DEBATE",
                            activity="speak",
                            task_widget="speak_debate",
                            topic_override="Debate-style C1 showcase speaking",
                            generation_instructions=(
                                "Set up a short debate-style showcase: rebut one point, bridge one "
                                "hostile question, end with a call to action."
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
                    title="Symposium + Thesis Close",
                    description="Building on yesterday's lesson, learners go deeper at C2 level: Time-capped integration. They refine control, nuance, and extended discourse on the same skill family.",
                    focus="C2 depth: Time-capped integration.",
                    teacher=TeacherBlueprint(
                        lesson_goal="C2 depth — Symposium + Thesis Close: Time-capped integration.",
                        steps=(
                            TeacherStep(
                                id="open",
                                goal="Frame the skill as small steps.",
                                instruction="Welcome back. Briefly note they practised this yesterday on the base day. Welcome the learner to confidence week at C1. Explain in two sentences that integrate C1 confidence skills in one capstone becomes easier with preparation and deliberate structure. Ask them to name one high-stakes situation they want to handle better.",
                            ),
                            TeacherStep(
                                id="preview",
                                goal="Preview the day and reassure.",
                                instruction="At C2 depth, push Time-capped integration: Affirm their answer warmly. Preview today's read, listen, write, and speak tasks that practise this skill in a supportive way.",
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
                            id="read_comp_mcq_showcase_w24_depth",
                            sequence=1,
                            task=TaskBlueprint(
                                archetype_id="READ_COMP_MCQ",
                                activity="read",
                                task_widget="read_comp_mcq",
                                topic_override="Symposium + Thesis Close — reading comprehension",
                                generation_instructions=(
                                    "Write a 120–150 word passage (C2 showcase integrating symposium and thesis) rich in Time-capped symposium moderation plus thesis close. Add 3–4 comprehension MCQs where at least two require applying Time-capped symposium moderation plus thesis close, not only locating a noun or date. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="listen_shadow_showcase_w24_depth",
                            sequence=2,
                            task=TaskBlueprint(
                                archetype_id="LISTEN_SHADOW",
                                activity="listen",
                                task_widget="listen_shadow",
                                topic_override="Symposium + Thesis Close — shadowing",
                                generation_instructions=(
                                    "Provide a 50–60 word script (C2 showcase integrating symposium and thesis) dense with Time-capped symposium moderation plus thesis close for shadowing practice. Rhythm and phrasing should model natural C2+ delivery. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="write_timed_showcase_w24_depth",
                            sequence=3,
                            task=TaskBlueprint(
                                archetype_id="WRITE_TIMED",
                                activity="write",
                                task_widget="write_timed",
                                topic_override="Symposium + Thesis Close — timed writing",
                                generation_instructions=(
                                    "Timed writing (C2 showcase integrating symposium and thesis): produce a structured response demonstrating Time-capped symposium moderation plus thesis close within the time limit; include clear signposts or moves from the depth angle. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
                            id="speak_debate_showcase_w24_depth",
                            sequence=4,
                            task=TaskBlueprint(
                                archetype_id="SPEAK_DEBATE",
                                activity="speak",
                                task_widget="speak_debate",
                                topic_override="Symposium + Thesis Close — debate",
                                generation_instructions=(
                                    "Debate scenario (C2 showcase integrating symposium and thesis) integrating Time-capped symposium moderation plus thesis close: chair briefly, respond to one challenge, then deliver a timed closing statement. C2+ level: denser discourse, subtler distractors, and less explicit scaffolding."
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
