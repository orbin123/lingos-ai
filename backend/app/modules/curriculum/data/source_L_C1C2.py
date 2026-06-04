"""Level-band curriculum source data.

Imports blueprint types from ``types.py`` only.
"""

from __future__ import annotations

from .types import DaySource, WeekSource


# ── C1C2 band: source weeks 1-8 (C1 wk 1-4, C2 wk 5-8) ──

WEEKS_C1C2: tuple[WeekSource, ...] = (
    WeekSource(
        week_number=1,
        theme_type="grammar",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
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
                                "you one work story that happened last year."
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
                            static_payload=
                            {'task_intro': 'Listen, then complete the mixed-conditional notes.',
                             'instructions': 'Play the audio once, then type the missing mixed-conditional verb '
                                             'phrases in the paraphrased notes.',
                             'estimated_time_minutes': 3,
                             'inner_widget': 'fill_in_blanks',
                             'audio_genre': 'Reflective career monologue',
                             'audio_script': 'Looking back, if I had taken that training course, I would be much '
                                             'more confident in meetings now. If I were better at delegating, I '
                                             'would have finished the project on time last month. If she had '
                                             'accepted the offer, she would still be working here today. If they '
                                             'had invested earlier, they would not be struggling with cash flow '
                                             'now. If I had known about the policy change, I would understand the '
                                             'new rules today.',
                             'passage_title': 'Mixed Time Notes',
                             'passage': 'If I ___ that training course, I would be much more confident now. If I '
                                        '___ better at delegating, I would have finished on time last month. If '
                                        'she ___ the offer, she would still be working here today. If they ___ '
                                        'earlier, they would not be struggling now.',
                             'items': [{'item_id': 'b1',
                                        'blank_id': 'b1',
                                        'sentence_with_blank': 'If I ___ that training course, I would be much '
                                                               'more confident now.',
                                        'base_verb': 'take',
                                        'correct_answer': 'had taken',
                                        'distractors': ['took', 'would take'],
                                        'options': ['had taken', 'took', 'would take'],
                                        'grammar_rule': 'Past condition with present result: if + past perfect.',
                                        'explanation': 'The past condition uses had taken.'},
                                       {'item_id': 'b2',
                                        'blank_id': 'b2',
                                        'sentence_with_blank': 'If I ___ better at delegating, I would have '
                                                               'finished on time last month.',
                                        'base_verb': 'be',
                                        'correct_answer': 'were',
                                        'distractors': ['was', 'am'],
                                        'options': ['were', 'was', 'am'],
                                        'grammar_rule': 'Present hypothetical with past result: if + past simple.',
                                        'explanation': 'The if-clause uses were for a present hypothetical.'},
                                       {'item_id': 'b3',
                                        'blank_id': 'b3',
                                        'sentence_with_blank': 'If she ___ the offer, she would still be working '
                                                               'here today.',
                                        'base_verb': 'accept',
                                        'correct_answer': 'had accepted',
                                        'distractors': ['accepted', 'accepts'],
                                        'options': ['had accepted', 'accepted', 'accepts'],
                                        'grammar_rule': 'Past condition with present result.',
                                        'explanation': 'The if-clause needs had accepted.'},
                                       {'item_id': 'b4',
                                        'blank_id': 'b4',
                                        'sentence_with_blank': 'If they ___ earlier, they would not be struggling '
                                                               'now.',
                                        'base_verb': 'invest',
                                        'correct_answer': 'had invested',
                                        'distractors': ['invested', 'invest'],
                                        'options': ['had invested', 'invested', 'invest'],
                                        'grammar_rule': 'Past condition with present result.',
                                        'explanation': 'The if-clause needs had invested.'}],
                             'target_words_in_audio': ['had taken', 'were', 'had accepted', 'had invested']},
                        ),
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
            ),
        ),
    ),
    WeekSource(
        week_number=2,
        theme_type="communication",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
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
                                "open a tense meeting in two sentences."
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
                                "Ask them to defend one position in two sentences."
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
            ),
        ),
    ),
    WeekSource(
        week_number=3,
        theme_type="vocabulary",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
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
            ),
        ),
    ),
    WeekSource(
        week_number=4,
        theme_type="confidence",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
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
            ),
        ),
    ),

    # ── Cycle 6 — Mastery (C1) ──────────────────────────────────
    WeekSource(
        week_number=5,
        theme_type="grammar",
        cefr_level="C2",
        sub_level_min=8, sub_level_max=8,
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
                            static_payload=
                            {'task_intro': 'Listen, then complete the advanced hypothetical notes.',
                             'instructions': 'Play the audio once, then type the missing formal hypothetical '
                                             'phrases in the paraphrased notes.',
                             'estimated_time_minutes': 3,
                             'inner_widget': 'fill_in_blanks',
                             'audio_genre': 'Formal reflective monologue',
                             'audio_script': 'Were it not for your support, the project would have stalled. But '
                                             'for the delay, we would have launched in March. Supposing we had '
                                             'accepted their terms, the partnership might have failed sooner. Had '
                                             'the board acted earlier, we would have avoided the crisis. If only '
                                             'the data had been clearer, the decision would have been easier.',
                             'passage_title': 'Formal Hypotheticals Notes',
                             'passage': '___ your support, the project would have stalled. But for the delay, we '
                                        '___ in March. Supposing we ___ their terms, the partnership might have '
                                        'failed sooner. Had the board acted earlier, we ___ the crisis.',
                             'items': [{'item_id': 'b1',
                                        'blank_id': 'b1',
                                        'sentence_with_blank': '___ your support, the project would have stalled.',
                                        'base_verb': 'be',
                                        'correct_answer': 'Were it not for',
                                        'distractors': ['If it was not for', 'Without of'],
                                        'options': ['Were it not for', 'If it was not for', 'Without of'],
                                        'grammar_rule': 'Use Were it not for in formal unreal present/past '
                                                        'hypotheticals.',
                                        'explanation': 'Were it not for is the formal inverted hypothetical '
                                                       'opener.'},
                                       {'item_id': 'b2',
                                        'blank_id': 'b2',
                                        'sentence_with_blank': 'But for the delay, we ___ in March.',
                                        'base_verb': 'launch',
                                        'correct_answer': 'would have launched',
                                        'distractors': ['will launch', 'launched'],
                                        'options': ['would have launched', 'will launch', 'launched'],
                                        'grammar_rule': 'But for + noun takes a would-have result clause.',
                                        'explanation': 'The unreal past result uses would have launched.'},
                                       {'item_id': 'b3',
                                        'blank_id': 'b3',
                                        'sentence_with_blank': 'Supposing we ___ their terms, the partnership '
                                                               'might have failed sooner.',
                                        'base_verb': 'accept',
                                        'correct_answer': 'had accepted',
                                        'distractors': ['accepted', 'would accept'],
                                        'options': ['had accepted', 'accepted', 'would accept'],
                                        'grammar_rule': 'Supposing often takes past perfect for unreal past.',
                                        'explanation': 'Supposing we had accepted fits a formal unreal past.'},
                                       {'item_id': 'b4',
                                        'blank_id': 'b4',
                                        'sentence_with_blank': 'Had the board acted earlier, we ___ the crisis.',
                                        'base_verb': 'avoid',
                                        'correct_answer': 'would have avoided',
                                        'distractors': ['will avoid', 'avoided'],
                                        'options': ['would have avoided', 'will avoid', 'avoided'],
                                        'grammar_rule': 'Inverted Had-clause pairs with would have + past '
                                                        'participle.',
                                        'explanation': 'The imagined past result uses would have avoided.'}],
                             'target_words_in_audio': ['Were it not for',
                                                       'would have launched',
                                                       'had accepted',
                                                       'would have avoided']},
                        ),
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
            ),
        ),
    ),
    WeekSource(
        week_number=6,
        theme_type="communication",
        cefr_level="C2",
        sub_level_min=8, sub_level_max=8,
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
            ),
        ),
    ),
    WeekSource(
        week_number=7,
        theme_type="vocabulary",
        cefr_level="C2",
        sub_level_min=8, sub_level_max=8,
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
            ),
        ),
    ),
    WeekSource(
        week_number=8,
        theme_type="confidence",
        cefr_level="C2",
        sub_level_min=8, sub_level_max=8,
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
            ),
        ),
    ),
)
