"""DaySpec definitions for Cycle 5 (weeks 17–20). See docs/SOURCE_FILE.md."""

from __future__ import annotations

from typing import Any

from generate_cycle4_weeks import DaySpec, _vocab_day_spec

MIXED_COND_LISTEN_PAYLOAD: dict[str, Any] = {
    "task_intro": "Listen, then complete the mixed-conditional notes.",
    "instructions": (
        "Play the audio once, then type the missing mixed-conditional verb phrases "
        "in the paraphrased notes."
    ),
    "estimated_time_minutes": 3,
    "inner_widget": "fill_in_blanks",
    "audio_genre": "Reflective career monologue",
    "audio_script": (
        "Looking back, if I had taken that training course, I would be much more "
        "confident in meetings now. If I were better at delegating, I would have "
        "finished the project on time last month. If she had accepted the offer, "
        "she would still be working here today. If they had invested earlier, they "
        "would not be struggling with cash flow now. If I had known about the "
        "policy change, I would understand the new rules today."
    ),
    "passage_title": "Mixed Time Notes",
    "passage": (
        "If I ___ that training course, I would be much more confident now. If I "
        "___ better at delegating, I would have finished on time last month. If she "
        "___ the offer, she would still be working here today. If they ___ earlier, "
        "they would not be struggling now."
    ),
    "items": [
        {
            "item_id": "b1",
            "blank_id": "b1",
            "sentence_with_blank": (
                "If I ___ that training course, I would be much more confident now."
            ),
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
            "sentence_with_blank": (
                "If I ___ better at delegating, I would have finished on time last month."
            ),
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
            "sentence_with_blank": (
                "If she ___ the offer, she would still be working here today."
            ),
            "base_verb": "accept",
            "correct_answer": "had accepted",
            "distractors": ["accepted", "accepts"],
            "options": ["had accepted", "accepted", "accepts"],
            "grammar_rule": "Past condition with present result.",
            "explanation": "The if-clause needs had accepted.",
        },
        {
            "item_id": "b4",
            "blank_id": "b4",
            "sentence_with_blank": (
                "If they ___ earlier, they would not be struggling now."
            ),
            "base_verb": "invest",
            "correct_answer": "had invested",
            "distractors": ["invested", "invest"],
            "options": ["had invested", "invested", "invest"],
            "grammar_rule": "Past condition with present result.",
            "explanation": "The if-clause needs had invested.",
        },
    ],
    "target_words_in_audio": ["had taken", "were", "had accepted", "had invested"],
}


# Grammar week 17 — activity id patterns match mirror week 13 per archetype
def _grammar_specs() -> dict[tuple[int, int], DaySpec]:
    w = 17
    return {
        (w, 0): DaySpec(
            title="Narrative Tense Control - Mixing Past Forms in One Story",
            description=(
                "Learners control narrative tense at B2: they mix past simple, past "
                "perfect, and past perfect continuous in one coherent story without "
                "losing the timeline."
            ),
            focus="Narrative tense control: past simple, past perfect, and past perfect continuous in one story.",
            lesson_goal="Teach mixing past tenses for clear narrative timeline.",
            steps=(
                ("open", "Introduce narrative tense control.", (
                    "Greet the learner. Explain in two sentences that B2 narratives "
                    "often mix past simple for events, past perfect for earlier background, "
                    "and past perfect continuous for duration before a past moment. Ask them "
                    "to tell you one work story that happened last year."
                )),
                ("mix_tenses", "Teach mixing past forms.", (
                    "Use their story to show when each tense fits (I had been working…, "
                    "I had finished…, then I left). Ask them to add one past perfect "
                    "continuous line to their story."
                )),
                ("timeline", "Keep the timeline clear.", (
                    "Explain that each tense signals a different time layer. Ask them to "
                    "say one past simple sentence for the main event after their background."
                )),
                ("wrap_up", "Move to practice.", (
                    "If the learner has mixed at least two past forms, ask only: "
                    "Ready to try the practice task?"
                )),
            ),
            activity_ids=(
                "read_cloze_narrative_tense",
                "listen_mcq_narrative_tense",
                "write_narrative_tense_sentences",
                "speak_narrative_tense_events",
            ),
            topic_overrides=(
                "Narrative tense in a connected passage",
                "Listening for tense shifts in narrative",
                "Write sentences mixing past forms",
                "Tell a short story with mixed past tenses",
            ),
            generation_instructions=(
                (
                    "Write a 4-5 blank narrative passage mixing past simple, past perfect, "
                    "and past perfect continuous where each blank needs the best tense."
                ),
                (
                    "Generate a 70-100 word spoken story with clear tense shifts; include "
                    "3-4 MCQs on timeline and tense choice."
                ),
                (
                    "Ask for three sentences using past simple, past perfect, and past "
                    "perfect continuous about the same episode."
                ),
                (
                    "Ask the learner to speak a 45-second story mixing all three past forms "
                    "with a clear timeline."
                ),
            ),
            widget_requirements=(
                (
                    "Always include base_verb for verb-form blanks. Do not repeat base_verb "
                    "inline after each ___."
                ),
                "Generate 3-4 MCQ items with prompt, options, correct_index, and explanation.",
                None,
                "Create exactly 3 speaking prompts. Include speaking_duration_seconds: 45.",
            ),
        ),
        (w, 1): DaySpec(
            title="Mixed Conditionals - Past Condition, Present Result",
            description=(
                "Learners use mixed conditionals where a past condition affects the "
                "present (If I had studied harder, I would be more confident now) and "
                "related time mismatches at B2 level."
            ),
            focus="Mixed conditionals: past if-clause with present would result, and related time mismatches.",
            lesson_goal="Teach mixed conditionals linking past conditions to present results.",
            steps=(
                ("open", "Introduce mixed conditionals.", (
                    "Greet the learner. Explain in two sentences that mixed conditionals "
                    "link a past condition to a present result using if + past perfect and "
                    "would + base verb now. Ask what would be different today if they had "
                    "made one different choice last year."
                )),
                ("past_present", "Teach past → present pattern.", (
                    "Model If I had…, I would… now with their idea. Ask them to finish "
                    "'If I had known earlier, I would…' with a present result."
                )),
                ("present_past", "Teach present → past pattern briefly.", (
                    "Show If I were more organised, I would have finished on time. Ask "
                    "them to make one sentence with were and would have."
                )),
                ("wrap_up", "Move to practice.", (
                    "If the learner has shown a mixed conditional at least once, ask only: "
                    "Ready to try the practice task?"
                )),
            ),
            activity_ids=(
                "read_error_spot_mixed_conditional",
                "listen_cloze_mixed_conditional",
                "write_error_corr_mixed_conditional",
                "speak_read_aloud_mixed_conditional",
            ),
            topic_overrides=(
                "Spot mixed conditional errors",
                "Listen and fill mixed conditional forms",
                "Correct mixed conditional mistakes",
                "Read mixed conditional passage aloud",
            ),
            generation_instructions=(
                (
                    "Generate a 5-sentence passage with mixed conditionals. Each sentence "
                    "has exactly one error (5 tokens): wrong tense in if-clause, wrong "
                    "would form, or time mismatch."
                ),
                (
                    "Listen to the career reflection audio, then complete notes with "
                    "missing mixed-conditional phrases."
                ),
                (
                    "Give 3 sentences with one mixed conditional error each; ask the "
                    "learner to rewrite correctly."
                ),
                (
                    "Give a 55-70 word passage with mixed conditionals to read aloud."
                ),
            ),
            static_payload_index=1,
            static_payload=MIXED_COND_LISTEN_PAYLOAD,
        ),
        (w, 2): DaySpec(
            title="Impersonal & Advanced Passive - It Is Said & Is Believed To",
            description=(
                "Learners use impersonal and advanced passive patterns (It is said that…, "
                "He is believed to have…, The decision was made…) typical of news and "
                "reports at B2."
            ),
            focus="Impersonal and advanced passive: It is said/claimed that, is believed to have, and formal passives.",
            lesson_goal="Teach impersonal and advanced passive for formal reporting.",
            steps=(
                ("open", "Introduce impersonal passive.", (
                    "Greet the learner. Explain in two sentences that formal English often "
                    "uses impersonal passives like It is said that or He is believed to "
                    "have to distance the writer from the claim. Ask them to report one "
                    "rumour they heard about their industry."
                )),
                ("it_is_said", "Teach It is said/claimed that.", (
                    "Reframe their rumour as It is said that…. Ask them to add It is "
                    "claimed that with a different verb."
                )),
                ("believed_to", "Teach is believed to have.", (
                    "Show He is believed to have left last week. Ask for one sentence "
                    "about a public figure using is thought to have."
                )),
                ("wrap_up", "Move to practice.", (
                    "If the learner has used an impersonal passive at least once, ask only: "
                    "Ready to try the practice task?"
                )),
            ),
            activity_ids=(
                "read_comp_mcq_impersonal_passive",
                "listen_dictation_impersonal_passive",
                "write_sent_trans_impersonal_passive",
                "speak_timed_impersonal_passive",
            ),
            topic_overrides=(
                "Impersonal passive in a news-style text",
                "Hear impersonal passive chunks",
                "Rewrite active claims into impersonal passive",
                "Report claims with impersonal passive aloud",
            ),
            generation_instructions=(
                (
                    "Write a 60-75 word news-style passage with It is said/claimed that "
                    "and is believed to have. Then comprehension MCQs."
                ),
                (
                    "Generate a 35-45 word audio of four formal passive sentences for "
                    "dictation."
                ),
                (
                    "Give 3 direct claims and ask the learner to rewrite each using "
                    "impersonal or advanced passive."
                ),
                (
                    "Ask the learner to say three impersonal passive sentences about "
                    "recent news in their field."
                ),
            ),
        ),
        (w, 3): DaySpec(
            title="Participle & Adverbial Clauses - Having Finished & Although Tired",
            description=(
                "Learners link ideas with participle clauses (Having finished…, Written "
                "in 2020…) and adverbial clauses (Although tired, …) for denser B2 "
                "sentences."
            ),
            focus="Participle clauses and adverbial clauses: Having + past participle, past participle fronting, Although/While.",
            lesson_goal="Teach participle and adverbial clauses for dense formal sentences.",
            steps=(
                ("open", "Introduce participle and adverbial clauses.", (
                    "Greet the learner. Explain in two sentences that participle clauses "
                    "shorten sentences (Having finished the report, …) and adverbial "
                    "clauses add contrast (Although tired, …). Ask them to describe a busy "
                    "day using Although."
                )),
                ("participle", "Teach participle openers.", (
                    "Model Having completed… and Written in…. Ask them to start one "
                    "sentence with Having + past participle about their work."
                )),
                ("wrap_up", "Move to practice.", (
                    "Confirm with a short example (Although pressed for time, she agreed.) "
                    "then ask only: Ready to try the practice task?"
                )),
            ),
            activity_ids=(
                "read_word_match_participle_clauses",
                "listen_mcq_participle_clauses",
                "write_open_sent_participle_clauses",
                "speak_pic_desc_participle_clauses",
            ),
            topic_overrides=(
                "Match clause types to their function",
                "Hearing participle and adverbial clauses",
                "Write sentences with participle and adverbial clauses",
                "Describe a scene with dense clause openers",
            ),
            generation_instructions=(
                (
                    "Ask the learner to match sentence stubs to participle opener, "
                    "adverbial contrast, or main clause need."
                ),
                (
                    "Generate a 35-45 word description using Having…, Although…, and a "
                    "participle fronting; include comprehension questions."
                ),
                (
                    "Ask for three sentences: one Having-clause, one Although-clause, "
                    "one past participle fronting."
                ),
                (
                    "Ask the learner to describe a workplace scene using at least two "
                    "participle or adverbial openers."
                ),
            ),
        ),
        (w, 4): DaySpec(
            title="Stance & Distancing in Reporting - It Is Argued That",
            description=(
                "Learners report claims with stance and distance (It is argued that…, "
                "According to…, The report suggests that…) without stating opinion as "
                "fact."
            ),
            focus="Stance and distancing: It is argued/claimed/suggested that, According to, and neutral reporting.",
            lesson_goal="Teach stance markers and distancing in reporting.",
            steps=(
                ("open", "Introduce stance in reporting.", (
                    "Greet the learner. Explain in two sentences that B2 reporting uses "
                    "stance phrases like It is argued that or According to to show who "
                    "claims something without endorsing it. Ask them to summarise a debate "
                    "they read recently."
                )),
                ("stance_phrases", "Teach stance phrases.", (
                    "Model It is argued that and The data suggests that. Ask them to "
                    "report one claim using According to a recent study."
                )),
                ("wrap_up", "Move to practice.", (
                    "If the learner has distanced a claim at least once, ask only: "
                    "Ready to try the practice task?"
                )),
            ),
            activity_ids=(
                "read_cloze_stance_reporting",
                "listen_infer_stance_reporting",
                "write_para_stance_reporting",
                "speak_roleplay_stance_reporting",
            ),
            topic_overrides=(
                "Stance markers in reporting blanks",
                "Infer claims behind stance phrases",
                "Write a paragraph with stance and distancing",
                "Pass on a reported claim in roleplay",
            ),
            generation_instructions=(
                (
                    "Write a 4-5 sentence report with blanks for argued, claimed, "
                    "suggested, According to."
                ),
                (
                    "Generate a 35-45 word audio using stance phrases; ask inference "
                    "questions on who claims what."
                ),
                (
                    "Ask for a 3-4 sentence paragraph reporting a topic with at least "
                    "three stance/distancing phrases."
                ),
                (
                    "Set up a roleplay passing on what experts argued using stance phrases "
                    "in 2-3 connected sentences."
                ),
            ),
        ),
        (w, 5): DaySpec(
            title="Inversion for Emphasis - Never Have I & Had I Known",
            description=(
                "Learners use inversion for emphasis (Never have I…, Had I known…, "
                "Not only… but also…) in formal and rhetorical B2 English."
            ),
            focus="Inversion for emphasis: Never have I, Had I known, Not only…but also, and formal negative inversion.",
            lesson_goal="Teach inversion patterns for emphasis and rhetoric.",
            steps=(
                ("open", "Introduce inversion for emphasis.", (
                    "Greet the learner and note this is the rhetoric day of grammar week. "
                    "Explain in two sentences that inversion puts emphasis on an idea "
                    "(Never have I seen…, Had I known…). Ask when they last felt surprised "
                    "at work."
                )),
                ("never_had", "Teach Never have I and Had I.", (
                    "Model Never have I… and Had I known…. Ask them to say one Never "
                    "have I sentence about their field."
                )),
                ("wrap_up", "Move to practice.", (
                    "If the learner has used inversion at least once, ask only: "
                    "Ready to try the practice task?"
                )),
            ),
            activity_ids=(
                "read_tfng_inversion",
                "listen_shadow_inversion",
                "write_email_inversion",
                "speak_smalltalk_inversion",
            ),
            topic_overrides=(
                "Inversion patterns in text",
                "Shadow inverted emphasis phrases",
                "Email using one inversion for emphasis",
                "Casual chat closing with a Not only line",
            ),
            generation_instructions=(
                (
                    "Write a short profile using Never have I, Had I known, and Not only… "
                    "but also. Then True/False/Not Given items."
                ),
                (
                    "Generate a 20-second monologue with inverted phrases for shadowing."
                ),
                (
                    "Ask the learner to write a short email using Had I known and one "
                    "Never have I line."
                ),
                (
                    "Set up small talk where the learner ends with one Not only… but also "
                    "sentence."
                ),
            ),
        ),
        (w, 6): DaySpec(
            title="Academic & Professional Cohesion - Thereby, Thus & In Light Of",
            description=(
                "Learners connect formal arguments with cohesive linkers (thereby, "
                "thus, consequently, in light of, with regard to) at B2 level."
            ),
            focus="Academic and professional cohesion: thereby, thus, consequently, in light of, with regard to.",
            lesson_goal="Teach formal cohesive linkers for B2 argument writing.",
            steps=(
                ("open", "Introduce formal cohesion.", (
                    "Greet the learner and note this is the final grammar day of the cycle. "
                    "Explain in two sentences that formal linkers like thereby and in light "
                    "of connect reasons and conclusions in reports. Ask them to finish "
                    "'In light of recent data, ___.'"
                )),
                ("linkers", "Teach thereby and with regard to.", (
                    "Confirm their sentence. Explain thereby for result and with regard to "
                    "for topic focus. Ask them to use consequently in one sentence."
                )),
                ("wrap_up", "Move to practice.", (
                    "If the learner has used a formal linker at least once, ask only: "
                    "Ready to try the practice task?"
                )),
            ),
            activity_ids=(
                "read_context_mcq_cohesion",
                "listen_retell_cohesion",
                "write_paraphrase_cohesion",
                "speak_present_cohesion",
            ),
            topic_overrides=(
                "Formal cohesion in a report excerpt",
                "Retell a signposted mini-briefing",
                "Paraphrase with cohesive linkers",
                "Short talk using formal linkers",
            ),
            generation_instructions=(
                (
                    "Write a short report excerpt with gaps for thereby, thus, in light of, "
                    "with regard to. MCQs on best linker."
                ),
                (
                    "Generate a 40-50 word formal audio with cohesive linkers; ask retell "
                    "with two linkers."
                ),
                (
                    "Give informal sentences; ask the learner to join them using thereby, "
                    "consequently, or in light of."
                ),
                (
                    "Ask for a 45-second mini presentation using at least two formal "
                    "cohesive linkers."
                ),
            ),
        ),
    }


_COMM = [
    (
        "Diplomatic Mediation - Neutral Language & Workable Outcomes",
        "diplomatic_mediation",
        "diplomatic mediation with neutral language and a workable outcome for both sides",
        "Teach diplomatic mediation between two sides.",
        (
            "Welcome the learner to communication week. Explain in two sentences that "
            "mediation uses neutral language to help two sides reach a workable outcome. "
            "Ask them to describe a disagreement they helped calm."
        ),
        (
            "React warmly. Teach phrases like 'I hear both of you' and 'What would a "
            "workable middle ground look like?'. Ask them to propose one neutral next step."
        ),
    ),
    (
        "Upward & Sensitive Feedback - Managers, Seniors & Clients",
        "upward_feedback",
        "upward and sensitive feedback to a manager, senior peer, or client",
        "Teach upward and sensitive feedback.",
        (
            "Welcome the learner to Day 2. Explain in two sentences that upward feedback "
            "must be respectful, specific, and focused on behaviour not character. Ask "
            "about feedback they need to give upward soon."
        ),
        (
            "Model 'I appreciate… / One concern is… / Could we explore…'. Ask them to "
            "give brief upward feedback on a late decision."
        ),
    ),
    (
        "Strategic Recommendation - Options, Risks & Mitigation",
        "strategic_recommendation",
        "strategic recommendations with options, risks, mitigation, and a clear recommendation",
        "Teach strategic recommendations with risks and mitigation.",
        (
            "Greet the learner. Explain in two sentences that strategic recommendations "
            "present options, risks, mitigation, and a clear preferred choice. Ask them "
            "to compare two options they know at work."
        ),
        (
            "Introduce On balance, I recommend… and The main risk is… with mitigation. "
            "Ask them to recommend one option with one risk and mitigation."
        ),
    ),
    (
        "Chairing with Disagreement - Agenda, Conflict & Actions",
        "chairing_disagreement",
        "chairing meetings when people disagree: agenda, conflict, and clear actions",
        "Teach chairing meetings with disagreement.",
        (
            "Greet the learner. Explain in two sentences that chairing with disagreement "
            "means keeping the agenda, managing conflict fairly, and assigning actions. "
            "Ask about a heated meeting they attended."
        ),
        (
            "Teach 'Let's park that' and 'Who will own this by Friday?'. Ask them to "
            "open a tense meeting in two sentences."
        ),
    ),
    (
        "Formal Advocacy - Defend a Position with Evidence",
        "formal_advocacy",
        "formal advocacy: defend a position with evidence under challenge",
        "Teach formal advocacy under challenge.",
        (
            "Greet the learner. Explain in two sentences that formal advocacy means "
            "stating a position, supporting it with evidence, and responding calmly "
            "to challenges. Ask what position they would defend at work."
        ),
        (
            "Model 'The evidence shows…' and 'That is a fair challenge; however…'. Ask "
            "them to defend one position in two sentences."
        ),
    ),
    (
        "Executive Summary - Compress Complex Information",
        "executive_summary",
        "executive summaries that compress complex information for different seniority levels",
        "Teach executive summaries for senior readers.",
        (
            "Greet the learner. Explain in two sentences that an executive summary gives "
            "senior readers the issue, impact, and ask in a few tight lines. Ask what "
            "report they would summarise for a director."
        ),
        (
            "Contrast detail-heavy vs executive lines. Ask them to write one headline and "
            "one ask for their topic."
        ),
    ),
    (
        "Panel-Style Discussion - Synthesise Multiple Views",
        "panel_discussion",
        "panel-style discussion: balance views, synthesise, and land a shared takeaway",
        "Teach panel-style facilitation and synthesis.",
        (
            "Greet the learner. Explain in two sentences that panel discussions need "
            "balancing voices, synthesising views, and landing one shared takeaway. Ask "
            "about a panel or roundtable they watched."
        ),
        (
            "Teach 'Let's hear a contrasting view' and 'To synthesise, the shared point "
            "is…'. Ask them to summarise two views in one neutral sentence."
        ),
    ),
]

_COMM_OVERRIDES = {
    0: (
        "Mediation in messages",
        "Listening to mediation dialogue",
        "Polite mediation phrases",
        "Roleplay diplomatic mediation",
    ),
    1: (
        "Sensitive feedback in writing",
        "Infer tone in upward feedback",
        "Write upward feedback",
        "React with upward feedback in chat",
    ),
    2: (
        "Strategic recommendation structure",
        "Retell a strategic recommendation",
        "Write recommendation with risks",
        "State a strategic recommendation aloud",
    ),
    3: (
        "Chairing a tense meeting in writing",
        "Listening to chairing under disagreement",
        "Turn notes into a chaired summary",
        "Roleplay chairing with disagreement",
    ),
    4: (
        "Formal advocacy in text",
        "Infer challenges in advocacy dialogue",
        "Write advocacy under challenge",
        "Explain advocacy position aloud",
    ),
    5: (
        "Executive summary tone",
        "Hear a one-minute executive summary",
        "Rewrite detail into executive lines",
        "Small talk practising a one-line ask",
    ),
    6: (
        "Panel discussion structure",
        "Retell a panel synthesis clip",
        "Email summarising panel takeaway",
        "Present a neutral panel close",
    ),
}

_VOCAB_TOPICS = [
    (
        "Innovation & Future Tech - Automation, Algorithm & Ethical AI",
        "innovation and future technology (automation, algorithm, disruption, ethical AI, prototype)",
        "automation, algorithm, disruption, ethical AI",
        "innovation and future tech",
        "innovation_tech",
        "a tech workplace or lab",
        "automation, algorithm, disruption",
        "tech lab with engineers and screens showing automation dashboards",
    ),
    (
        "Law & Justice - Legislation, Verdict & Precedent",
        "law and justice (legislation, verdict, precedent, plaintiff, appeal)",
        "legislation, verdict, precedent, plaintiff, appeal",
        "law and justice",
        "law_justice",
        "a courtroom or legal briefing",
        "legislation, verdict, precedent",
        "courtroom scene with judge and legal counsel at a bench",
    ),
    (
        "Politics & Governance - Coalition, Reform & Mandate",
        "politics and governance (coalition, reform, referendum, mandate, austerity)",
        "coalition, reform, referendum, mandate, austerity",
        "politics and governance",
        "politics_governance",
        "a policy or government context",
        "coalition, mandate, referendum",
        "parliament chamber with politicians debating reforms",
    ),
    (
        "Finance & Markets (Advanced) - Equity, Liability & Volatility",
        "advanced finance and markets (equity, liability, portfolio, volatility, stakeholder)",
        "equity, liability, portfolio, volatility, stakeholder",
        "finance and markets",
        "finance_markets",
        "a trading or board finance scene",
        "equity, volatility, portfolio",
        "trading floor or boardroom reviewing market charts",
    ),
    (
        "Psychology & Behaviour - Cognitive, Implicit & Resilience",
        "psychology and behaviour (cognitive, perception, motivation, implicit, resilience)",
        "cognitive, perception, motivation, implicit, resilience",
        "psychology and behaviour",
        "psychology_behaviour",
        "a coaching or research context",
        "cognitive, implicit, resilience",
        "workshop with facilitator discussing motivation and behaviour",
    ),
    (
        "Rhetoric & Argumentation - Concede, Undermine & Compelling",
        "rhetoric and argumentation (rhetoric, concede, undermine, compelling, nuance)",
        "rhetoric, concede, undermine, compelling, nuance",
        "rhetoric and argumentation",
        "rhetoric_argument",
        "a debate or persuasion setting",
        "rhetoric, concede, compelling",
        "debate stage with speakers and audience",
    ),
    (
        "Review & Word Building - Consolidate Week 19",
        "the week's B2 vocabulary across innovation, law, politics, finance, psychology, and rhetoric",
        "review words from week 19",
        "review and word building",
        "review_w19",
        "mixed professional contexts",
        "review, prefix, suffix",
        "collage of tech, legal, political, and debate scenes",
    ),
]

_CONF = [
    (
        "High-Stakes Conversations - Stay Composed Under Pressure",
        "stay composed in high-stakes conversations when pressure and outcomes matter",
        "high_stakes_conv",
    ),
    (
        "Evidence-Based Debate - Claim, Concession & Rebuttal",
        "debate with evidence: claim, partial concession, and calm rebuttal",
        "evidence_debate",
    ),
    (
        "Professional Brand Story - Past, Present & Direction",
        "tell a professional brand story with past, present, and direction",
        "brand_story",
    ),
    (
        "Public Challenge - Tough Questions Without Defensiveness",
        "handle public challenge: tough questions, stay clear, avoid defensiveness",
        "public_challenge",
    ),
    (
        "Stakeholder Pitch - Problem, Solution, Proof & Ask",
        "deliver a stakeholder pitch with problem, solution, proof point, and ask",
        "stakeholder_pitch",
    ),
    (
        "Keynote-Style Segment - Structured Talk & Hard Question",
        "deliver a keynote-style segment with structure and one hard question",
        "keynote_segment",
    ),
    (
        "Full Confidence Showcase (B2)",
        "integrate B2 confidence skills in one capstone showcase",
        "showcase_w20",
    ),
]

_CONF_ACT = [
    ("read_comp_mcq_high_stakes_conv", "listen_shadow_high_stakes_conv", "write_sent_trans_high_stakes_conv", "speak_read_aloud_high_stakes_conv"),
    ("read_tone_id_evidence_debate", "listen_mcq_evidence_debate", "write_timed_evidence_debate", "speak_timed_evidence_debate"),
    ("read_comp_mcq_brand_story", "listen_tone_brand_story", "write_sent_trans_brand_story", "speak_pic_desc_brand_story"),
    ("read_tone_id_public_challenge", "listen_shadow_public_challenge", "write_timed_public_challenge", "speak_smalltalk_public_challenge"),
    ("read_comp_mcq_stakeholder_pitch", "listen_mcq_stakeholder_pitch", "write_sent_trans_stakeholder_pitch", "speak_pic_desc_stakeholder_pitch"),
    ("read_tone_id_keynote_segment", "listen_tone_keynote_segment", "write_timed_keynote_segment", "speak_present_keynote_segment"),
    ("read_comp_mcq_showcase_w20", "listen_shadow_showcase_w20", "write_timed_showcase_w20", "speak_debate_showcase_w20"),
]


_COMM_GENS = {
    0: (
        "Write a mediation exchange with neutral language and a workable outcome. Comprehension questions.",
        "Generate a 35-45 word mediation dialogue. MCQs on each side's underlying need.",
        "Give 3 positional statements to rewrite using neutral mediation phrases.",
        "Roleplay diplomatic mediation between two colleagues with a shared next step.",
    ),
    1: (
        "Write a message giving upward feedback respectfully. True/False/Not Given on tone.",
        "Generate a conversation with upward feedback; infer whether it builds trust.",
        "Ask the learner to write upward feedback with appreciation, concern, and a request.",
        "Mini interview: respond with upward feedback on a sensitive topic.",
    ),
    2: (
        "Provide a strategic comparison text; label Options, Risks, Mitigation, Recommendation.",
        "Audio comparing options with risks and mitigation; retell the recommendation.",
        "Write a paragraph recommending one option with risks and mitigation.",
        "Speak for 45 seconds with a clear strategic recommendation.",
    ),
    3: (
        "Write a tense meeting transcript with agenda control and action owners. MCQs.",
        "Generate a 35-45 word clip chairing disagreement and assigning an owner.",
        "Turn bullet notes into a chaired summary with actions.",
        "Roleplay chairing a meeting when two people disagree.",
    ),
    4: (
        "Write Q&A with challenges and evidence-based replies. True/False/Not Given.",
        "Dialogue challenging a position; inference on evidence used.",
        "Write crisp advocacy responses to three challenges.",
        "Describe aloud how to defend a position with evidence in three lines.",
    ),
    5: (
        "Provide a detailed update and a 3-line executive summary; compare them.",
        "Audio one-minute executive summary; MCQs on issue and ask.",
        "Rewrite a long update into a 4-sentence executive summary.",
        "Small talk practising a one-sentence ask to a senior stakeholder.",
    ),
    6: (
        "Provide a three-part panel transcript; label open, expert turns, synthesis.",
        "Audio of a moderator synthesising panel views; retell the takeaway.",
        "Write an email summarising a panel with a neutral shared conclusion.",
        "Deliver a 45-second neutral panel close synthesising two views.",
    ),
}

_CONF_GENS = [
    (
        ("High-stakes composure story", "Calm-under-pressure shadowing", "Reframe anxious lines", "Read composure passage aloud"),
        (
            "Write a story about staying composed when stakes are high; MCQs.",
            "Generate a 15-second calm-under-pressure clip for shadowing.",
            "Rewrite three anxious lines into composed professional language.",
            "Give a 55-70 word passage on composure to read aloud.",
        ),
    ),
    (
        ("Evidence-based debate tone", "Debate listening", "Timed debate writing", "Timed debate speaking"),
        (
            "Two argument excerpts; identify which uses evidence and partial concession.",
            "Audio with claim, evidence, and rebuttal; inference questions.",
            "Timed paragraph: claim, evidence, concession, rebuttal.",
            "Three timed speaking prompts to debate with evidence calmly.",
        ),
    ),
    (
        ("Brand story comprehension", "Tone in a brand narrative", "Brand story transforms", "Brand story picture description"),
        (
            "Story with past-present-direction arc; MCQs on brand message.",
            "Audio of a professional brand story; tone and structure questions.",
            "Transform three sentences into a past-present-direction brand arc.",
            "Describe a photo using brand-story vocabulary aloud.",
        ),
    ),
    (
        ("Public challenge tone", "Tough-question shadowing", "Timed bridge-and-redirect writing", "Public challenge small talk"),
        (
            "Two answers to a tough question; identify bridge and redirect.",
            "Clip of a tough question answered calmly for shadowing.",
            "Timed answers to three hostile questions using bridge + redirect.",
            "Small talk practising one bridge phrase and one redirect.",
        ),
    ),
    (
        ("Stakeholder pitch comprehension", "Pitch listening", "Pitch sentence transforms", "Stakeholder pitch speaking"),
        (
            "Short pitch text; questions on problem, solution, proof, and ask.",
            "Audio of a stakeholder pitch; MCQs on ask and proof point.",
            "Rewrite a vague pitch into problem → solution → proof → ask.",
            "Describe delivering a stakeholder pitch aloud.",
        ),
    ),
    (
        ("Keynote structure comprehension", "Hook and close listening", "Keynote writing", "Keynote-style speaking"),
        (
            "Identify hook, two points, and close in a short talk transcript.",
            "Audio with clear structure plus one hard question; MCQs.",
            "Timed paragraph: hook, two points, conclusion.",
            "45-second keynote segment plus brief answer to one hard question.",
        ),
    ),
    (
        (
            "B2 confidence capstone story",
            "Capstone shadowing clip",
            "Timed integrated B2 writing",
            "Debate-style B2 showcase",
        ),
        (
            "Write a capstone story integrating composure, evidence, brand arc, and pitch; MCQs.",
            "Generate a 20-second confident capstone clip for shadowing.",
            "Ask for a timed paragraph integrating claim, story, and ask.",
            "Short showcase: rebut one point and close with a clear ask.",
        ),
    ),
]


def build_day_specs() -> dict[tuple[int, int], DaySpec]:
    import dataclasses
    from generate_cycle4_weeks import DAY_SPECS as C4, WEEKS_24

    specs: dict[tuple[int, int], DaySpec] = {}
    specs.update(_grammar_specs())

    w14 = next(w for w in WEEKS_24 if w.week_number == 14)
    old_comm_slugs = [
        "conflict_resolution",
        "constructive_feedback",
        "pros_cons",
        "leading_meeting",
        "handling_objections",
        "stakeholder_w14",
        "facilitating",
    ]
    for i, row in enumerate(_COMM):
        title, slug, focus_desc, goal, open_i, mid_i = row
        base = C4[(14, i)]
        steps = (
            ("open", f"Introduce {title.split(' - ')[0].lower()}.", open_i),
            (slug, f"Teach {slug.replace('_', ' ')}.", mid_i),
            (
                "wrap_up",
                "Move to practice.",
                (
                    "If the learner has practised the target skill at least once, ask only: "
                    "Ready to try the practice task?"
                ),
            ),
        )
        act_ids = tuple(
            a.id.replace(old_comm_slugs[i], slug) for a in w14.days[i].activities
        )
        specs[(18, i)] = dataclasses.replace(
            base,
            title=title,
            description=(
                f"Learners practise {focus_desc} at B2 level using the same "
                f"read-listen-write-speak sequence as earlier communication weeks."
            ),
            focus=focus_desc.capitalize() + ".",
            lesson_goal=goal,
            steps=steps,
            activity_ids=act_ids,
            topic_overrides=_COMM_OVERRIDES[i],
            generation_instructions=_COMM_GENS[i],
        )

    w15 = next(w for w in WEEKS_24 if w.week_number == 15)
    old_vocab_slugs = [
        "science_research",
        "arts_creativity",
        "ethics_global",
        "business_economics",
        "media_literacy",
        "leadership_influence",
        "review_w15",
    ]
    for i, topic in enumerate(_VOCAB_TOPICS):
        spec = _vocab_day_spec(*topic, day_index=i)
        slug = topic[4]
        act_ids = tuple(
            a.id.replace(old_vocab_slugs[i], slug) for a in w15.days[i].activities
        )
        spec = dataclasses.replace(
            spec,
            description=spec.description.replace("B1+", "B2"),
            generation_instructions=tuple(
                g.replace("B1+", "B2") for g in spec.generation_instructions
            ),
            activity_ids=act_ids,
        )
        if i == 6:
            spec = dataclasses.replace(
                spec,
                title="Review & Word Building - Consolidate Week 19",
                topic_overrides=(
                    "Week 19 vocabulary review",
                    "Mixed B2 vocabulary listening",
                    "Word-building and precision writing",
                    "Describe a scene using week 19 words",
                ),
                generation_instructions=(
                    "Match week 19 target words to definitions across all domains.",
                    "Short audio using six week-19 words; comprehension questions.",
                    "Ask the learner to build three words with prefixes/suffixes and use each in a sentence.",
                    "Describe a photo collage using at least five week-19 words aloud.",
                ),
            )
        specs[(19, i)] = spec

    for i, (title, focus_desc, slug) in enumerate(_CONF):
        topics, gens = _CONF_GENS[i]
        if i == 6:
            title = "Full Confidence Showcase (B2)"
        specs[(20, i)] = DaySpec(
            title=title,
            description=(
                f"Learners build confidence to {focus_desc}, using the same "
                f"read-listen-write-speak sequence at B2 level."
            ),
            focus=focus_desc.capitalize() + ".",
            lesson_goal=f"Build confidence for {title.split(' - ')[0].lower()}.",
            steps=(
                (
                    "open",
                    "Frame the skill as small steps.",
                    (
                        "Welcome the learner to confidence week at B2. Explain in two sentences "
                        f"that {focus_desc} gets easier with preparation. Ask them to name one "
                        "high-stakes situation they want to handle better."
                    ),
                ),
                (
                    "preview",
                    "Preview the day and reassure.",
                    (
                        "Affirm their answer warmly. Preview today's read, listen, write, and "
                        "speak tasks that practise this skill in a supportive way."
                    ),
                ),
                (
                    "wrap_up",
                    "Move to practice.",
                    (
                        "Once the learner sounds ready, ask only: Ready to try the practice task?"
                    ),
                ),
            ),
            activity_ids=_CONF_ACT[i],
            topic_overrides=topics,
            generation_instructions=gens,
        )

    return specs


DAY_SPECS = build_day_specs()
