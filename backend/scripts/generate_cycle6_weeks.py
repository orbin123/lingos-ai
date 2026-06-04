"""Generate weeks 21-24 (Cycle 6, C1) by mirroring weeks 17-20 structure.

W21..W24 mirror W17..W20 day-for-day (W-4), which mirror W13..W16.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_C4_PATH = Path(__file__).resolve().parent / "generate_cycle4_weeks.py"
_spec = importlib.util.spec_from_file_location("generate_cycle4_weeks", _C4_PATH)
c4 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules["generate_cycle4_weeks"] = c4
_spec.loader.exec_module(c4)

DaySpec = c4.DaySpec
WeekSource = c4.WeekSource
WEEKS_24 = c4.WEEKS_24
_build_day = c4._build_day
_emit_day = c4._emit_day
_week_days = c4._week_days
_vocab_day_spec = c4._vocab_day_spec

STRUCTURAL_MIRROR_OFFSET = 4  # W21 -> W17


ADVANCED_HYP_LISTEN_PAYLOAD: dict[str, Any] = {
    "task_intro": "Listen, then complete the advanced hypothetical notes.",
    "instructions": (
        "Play the audio once, then type the missing formal hypothetical phrases "
        "in the paraphrased notes."
    ),
    "estimated_time_minutes": 3,
    "inner_widget": "fill_in_blanks",
    "audio_genre": "Formal reflective monologue",
    "audio_script": (
        "Were it not for your support, the project would have stalled. But for "
        "the delay, we would have launched in March. Supposing we had accepted "
        "their terms, the partnership might have failed sooner. Had the board "
        "acted earlier, we would have avoided the crisis. If only the data had "
        "been clearer, the decision would have been easier."
    ),
    "passage_title": "Formal Hypotheticals Notes",
    "passage": (
        "___ your support, the project would have stalled. But for the delay, we "
        "___ in March. Supposing we ___ their terms, the partnership might have "
        "failed sooner. Had the board acted earlier, we ___ the crisis."
    ),
    "items": [
        {
            "item_id": "b1",
            "blank_id": "b1",
            "sentence_with_blank": "___ your support, the project would have stalled.",
            "base_verb": "be",
            "correct_answer": "Were it not for",
            "distractors": ["If it was not for", "Without of"],
            "options": ["Were it not for", "If it was not for", "Without of"],
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
            "options": ["would have launched", "will launch", "launched"],
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
            "options": ["had accepted", "accepted", "would accept"],
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
            "options": ["would have avoided", "will avoid", "avoided"],
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
}


def _mirror_day(week: int, day_index: int) -> c4.DaySource:
    return _week_days(week - STRUCTURAL_MIRROR_OFFSET)[day_index]


def _act_ids(mirror_week: int, day_index: int, slug: str) -> tuple[str, ...]:
    mirror = _week_days(mirror_week)[day_index]
    old_ids = tuple(a.id for a in mirror.activities)
    # Replace the middle token cluster with slug (keep archetype prefix)
    out: list[str] = []
    for oid in old_ids:
        parts = oid.split("_")
        # e.g. read_cloze_past_perf_cont -> read_cloze_{slug}
        if len(parts) >= 3:
            out.append(f"{parts[0]}_{parts[1]}_{slug}")
        else:
            out.append(f"{oid}_{slug}")
    return tuple(out)


def _grammar_specs() -> dict[tuple[int, int], DaySpec]:
    """Week 21 — mirrors week 13 grammar layout."""
    specs: dict[tuple[int, int], DaySpec] = {}

    specs[(21, 0)] = DaySpec(
        title="Aspect, Register & Narrative Voice",
        description=(
            "Learners control aspect and register in narrative: subtle time shifts "
            "(had been reflecting, was leaving, has shaped), and a reflective or "
            "literary tone suited to professional storytelling."
        ),
        focus=(
            "Aspect, register, and narrative voice: subtle time shifts and reflective "
            "or literary tone in connected prose."
        ),
        lesson_goal="Teach aspect choice and register in narrative voice.",
        steps=(
            (
                "open",
                "Introduce aspect and narrative register.",
                (
                    "Greet the learner. Explain in two sentences that narrative voice "
                    "combines aspect choices (simple, continuous, perfect) with register "
                    "(neutral, reflective, literary). Ask them to describe a recent "
                    "change at work using one reflective opening line."
                ),
            ),
            (
                "aspect_shifts",
                "Teach subtle time shifts.",
                (
                    "Use their line to show how shifting aspect changes emphasis (I had "
                    "been considering…, I was leaving…, It has shaped…). Ask them to "
                    "rewrite one fact with a different aspect for a more reflective tone."
                ),
            ),
            (
                "register",
                "Teach register in narrative.",
                (
                    "Contrast neutral reporting with literary distance (It seemed that…, "
                    "What followed was…). Ask them to add one literary linker to their "
                    "sentence without changing the fact."
                ),
            ),
            (
                "wrap_up",
                "Move to practice.",
                (
                    "If the learner has shown aspect or register control at least once, "
                    "ask only: Ready to try the practice task?"
                ),
            ),
        ),
        activity_ids=_act_ids(17, 0, "aspect_narrative"),
        topic_overrides=(
            "Aspect and register in narrative",
            "Listening for aspect shifts in narrative",
            "Write narrative sentences with aspect control",
            "Speak a short reflective narrative",
        ),
        generation_instructions=(
            (
                "Write a 4-5 blank connected narrative passage (professional memoir tone) "
                "where aspect and register shift subtly (had been, was, has, seemed). "
                "Blanks test the best aspect or linker for the context."
            ),
            (
                "Generate a 70-100 word spoken reflective narrative using mixed aspects "
                "and one literary distancing phrase. Include 3-4 MCQs on aspect meaning "
                "or register."
            ),
            (
                "Ask for three short narrative sentences at C1 level: one with past perfect "
                "continuous, one with simple past for a punchy fact, one with present perfect "
                "for relevance."
            ),
            (
                "Ask the learner to speak a 45-second reflective narrative about a career "
                "moment using at least two aspect shifts and one literary distancing phrase."
            ),
        ),
        widget_requirements=c4.DAY_SPECS[(13, 0)].widget_requirements,
    )

    specs[(21, 1)] = dataclasses.replace(
        c4.DAY_SPECS[(13, 1)],
        title="Advanced Hypotheticals - Were it not for, But for & Supposing",
        description=(
            "Learners use advanced formal hypotheticals (Were it not for…, But for…, "
            "Supposing…, inverted Had…) for unreal situations in professional speech."
        ),
        focus=(
            "Advanced hypotheticals: Were it not for, But for, Supposing, and inverted "
            "Had-clauses with would-have results."
        ),
        lesson_goal="Teach advanced formal hypothetical patterns.",
        steps=(
            (
                "open",
                "Introduce advanced hypotheticals.",
                (
                    "Greet the learner. Explain in two sentences that formal hypotheticals "
                    "like Were it not for and But for express what would be different if "
                    "something were not true. Ask what would be different in their field "
                    "if one recent trend had not happened."
                ),
            ),
            (
                "were_but_for",
                "Teach Were it not for and But for.",
                (
                    "Use their idea with Were it not for + clause or But for + noun. Ask "
                    "them to finish 'But for the pandemic, …' with a would-have result."
                ),
            ),
            (
                "supposing_had",
                "Teach Supposing and inverted Had.",
                (
                    "Show Supposing + past perfect and Had they acted…, … would have…. Ask "
                    "them to make one Supposing sentence about a decision at work."
                ),
            ),
            (
                "wrap_up",
                "Move to practice.",
                (
                    "If the learner has used an advanced hypothetical at least once, ask "
                    "only: Ready to try the practice task?"
                ),
            ),
        ),
        activity_ids=_act_ids(17, 1, "advanced_hypothetical"),
        topic_overrides=(
            "Spot advanced hypothetical errors",
            "Listen and fill advanced hypothetical forms",
            "Correct advanced hypothetical mistakes",
            "Read advanced hypothetical passage aloud",
        ),
        generation_instructions=(
            (
                "Generate a 5-sentence formal passage with advanced hypotheticals. Each "
                "sentence must contain exactly one error (5 tokens): wrong Were/But for "
                "form, Supposing tense, or would-have mismatch."
            ),
            (
                "Listen to the formal hypotheticals audio, then complete paraphrased "
                "notes with missing Were it not for / But for / Supposing phrases."
            ),
            (
                "Give 3 sentences with one advanced hypothetical error each; ask the "
                "learner to rewrite correctly using Were it not for, But for, or Supposing."
            ),
            (
                "Give a 55-70 word connected passage with Were it not for, But for, and "
                "Supposing for read-aloud practice."
            ),
        ),
        static_payload_index=1,
        static_payload=ADVANCED_HYP_LISTEN_PAYLOAD,
    )

    specs[(21, 2)] = DaySpec(
        title="Nominalisation & Dense Impersonal Style",
        description=(
            "Learners turn verbs into nouns and build dense impersonal sentences "
            "(the implementation of…, a reduction in…, there was an increase in…) "
            "typical of reports and policy writing."
        ),
        focus="Nominalisation and dense impersonal style: verb-to-noun shifts and formal noun phrases.",
        lesson_goal="Teach nominalisation for dense impersonal prose.",
        steps=(
            (
                "open",
                "Introduce nominalisation.",
                (
                    "Greet the learner. Explain in two sentences that nominalisation turns "
                    "verbs into nouns to sound more formal and impersonal (implement → "
                    "implementation). Ask them to name one process their organisation "
                    "improved recently."
                ),
            ),
            (
                "noun_phrases",
                "Teach dense noun phrases.",
                (
                    "Model the implementation of, a reduction in, an increase in using "
                    "their topic. Ask them to rewrite 'We reduced costs' as a nominal "
                    "phrase starting with A reduction in…."
                ),
            ),
            (
                "impersonal",
                "Teach impersonal there was / it is patterns.",
                (
                    "Show There was a decline in… / It is clear that… without naming who "
                    "acted. Ask for one impersonal sentence about their topic."
                ),
            ),
            (
                "wrap_up",
                "Move to practice.",
                (
                    "If the learner has produced a nominal phrase at least once, ask only: "
                    "Ready to try the practice task?"
                ),
            ),
        ),
        activity_ids=_act_ids(17, 2, "nominalisation"),
        topic_overrides=(
            "Nominalisation in policy-style text",
            "Hear nominal phrases in formal speech",
            "Rewrite verbs into nominalisations",
            "Describe outcomes with nominal phrases",
        ),
        generation_instructions=(
            (
                "Write a 60-75 word impersonal report excerpt using nominalisations "
                "(implementation, reduction, assessment). Then comprehension MCQs."
            ),
            (
                "Generate a 35-45 word audio of four formal sentences with nominal "
                "phrases for dictation."
            ),
            (
                "Give 3 active-voice sentences and ask the learner to rewrite each using "
                "nominalisation while keeping meaning."
            ),
            (
                "Ask the learner to speak about a project outcome using at least two "
                "nominal phrases and one impersonal opener."
            ),
        ),
    )

    specs[(21, 3)] = dataclasses.replace(
        c4.DAY_SPECS[(13, 3)],
        title="Complex Embedding & Clarity",
        description=(
            "Learners manage layered subordinate clauses while keeping clarity: "
            "punctuation, relative chains, and when to split long sentences."
        ),
        focus="Complex embedding: layered subordinates with clear punctuation and readable sentence length.",
        lesson_goal="Teach complex embedding without losing clarity.",
        steps=(
            (
                "open",
                "Introduce complex embedding.",
                (
                    "Greet the learner. Explain in two sentences that C1 writers embed "
                    "ideas in layers but must punctuate and break sentences for clarity. "
                    "Ask them to describe a policy they follow using one subordinate clause."
                ),
            ),
            (
                "layers",
                "Teach layered subordinates.",
                (
                    "Build on their sentence with a second layer (which…, where…, although…). "
                    "Ask them to add one more embedded clause without losing the main point."
                ),
            ),
            (
                "clarity",
                "Teach clarity and punctuation.",
                (
                    "Show when to use commas, dashes, or a full stop instead of stacking. "
                    "Ask them to split an over-long example into two clear sentences."
                ),
            ),
            (
                "wrap_up",
                "Move to practice.",
                (
                    "If the learner has embedded and clarified at least once, ask only: "
                    "Ready to try the practice task?"
                ),
            ),
        ),
        activity_ids=_act_ids(17, 3, "complex_embedding"),
        topic_overrides=(
            "Match embedding patterns to punctuation",
            "Hearing layered clauses",
            "Write clearly embedded sentences",
            "Describe a scene with embedded clauses",
        ),
        generation_instructions=(
            (
                "Ask the learner to match sentence stubs to comma rules, dash use, or "
                "need to split for clarity with layered subordinates."
            ),
            (
                "Generate a 35-45 word description with two embedded layers; include "
                "comprehension questions on structure."
            ),
            (
                "Ask for three sentences: one with two embedded clauses punctuated, one "
                "over-long sentence they must split, one reduced for clarity."
            ),
            (
                "Ask the learner to describe a workplace scene aloud using one double-embedded "
                "sentence and one short follow-up for clarity."
            ),
        ),
    )

    specs[(21, 4)] = dataclasses.replace(
        c4.DAY_SPECS[(13, 4)],
        title="Hedging, Boosting & Epistemic Stance",
        description=(
            "Learners signal certainty carefully with hedges (appears to, tends to, "
            "might) and boosters (clearly, undoubtedly) in reporting and analysis."
        ),
        focus="Hedging and boosting: appears to, tends to, arguably, clearly, and epistemic stance.",
        lesson_goal="Teach hedging and boosting for epistemic stance.",
        steps=(
            (
                "open",
                "Introduce hedging and boosting.",
                (
                    "Greet the learner. Explain in two sentences that hedges soften claims "
                    "while boosters strengthen them when evidence supports it. Ask them to "
                    "report one trend they are not fully sure about."
                ),
            ),
            (
                "hedges",
                "Teach hedges.",
                (
                    "Model appears to, tends to, might, and arguably with their topic. Ask "
                    "them to hedge one strong claim they made earlier."
                ),
            ),
            (
                "boosters",
                "Teach boosters carefully.",
                (
                    "Show when clearly or evidently is fair vs overstated. Ask them to add "
                    "one booster only where evidence in their example is strong."
                ),
            ),
            (
                "wrap_up",
                "Move to practice.",
                (
                    "If the learner has hedged or boosted appropriately once, ask only: "
                    "Ready to try the practice task?"
                ),
            ),
        ),
        activity_ids=_act_ids(17, 4, "epistemic_stance"),
        topic_overrides=(
            "Hedges and boosters in analysis",
            "Infer stance from hedged reporting",
            "Write a paragraph with stance markers",
            "Report findings with hedges aloud",
        ),
        generation_instructions=(
            (
                "Write a short analysis passage with blanks for hedges and boosters "
                "(appears to, tends to, arguably, clearly)."
            ),
            (
                "Generate a 35-45 word audio clip reporting data with mixed hedges; ask "
                "the learner to infer certainty level."
            ),
            (
                "Ask for a 3-4 sentence paragraph interpreting results with at least two "
                "hedges and one justified booster."
            ),
            (
                "Set up a roleplay where the learner presents findings to a sceptical "
                "colleague using hedges and one clear booster."
            ),
        ),
    )

    specs[(21, 5)] = dataclasses.replace(
        c4.DAY_SPECS[(13, 5)],
        title="Rhetorical Grammar for Effect",
        description=(
            "Learners use rhetorical grammar for emphasis: fronting, clefts "
            "(What we need is…), parallelism, and inversion for punch."
        ),
        focus="Rhetorical grammar: fronting, cleft sentences, parallelism, and inversion for emphasis.",
        lesson_goal="Teach rhetorical grammar for persuasive effect.",
        steps=(
            (
                "open",
                "Introduce rhetorical grammar.",
                (
                    "Greet the learner. Explain in two sentences that rhetorical grammar "
                    "puts key ideas in focus through fronting, clefts, and parallel structure. "
                    "Ask what message they would emphasise in a leadership talk."
                ),
            ),
            (
                "clefts",
                "Teach cleft and fronting patterns.",
                (
                    "Model What we need is… and Fronting (Especially important is…). Ask "
                    "them to turn their message into one cleft sentence."
                ),
            ),
            (
                "parallelism",
                "Teach parallelism.",
                (
                    "Show parallel verb phrases for rhythm (to build, to test, to launch). Ask "
                    "them to add a three-part parallel list about their topic."
                ),
            ),
            (
                "wrap_up",
                "Move to practice.",
                (
                    "If the learner has used a rhetorical device at least once, ask only: "
                    "Ready to try the practice task?"
                ),
            ),
        ),
        activity_ids=_act_ids(17, 5, "rhetorical_grammar"),
        topic_overrides=(
            "Rhetorical devices in text",
            "Shadow rhetorical emphasis phrases",
            "Email using rhetorical grammar",
            "Casual chat with a rhetorical punch line",
        ),
        generation_instructions=(
            (
                "Write a short persuasive text with fronting, a cleft, and parallel phrases. "
                "Then True/False/Not Given on which device creates emphasis."
            ),
            (
                "Generate a 20-second monologue with a cleft and parallel list for shadowing."
            ),
            (
                "Ask the learner to write a short email using one cleft and one parallel trio."
            ),
            (
                "Set up small talk where the learner closes with one fronted emphasis line."
            ),
        ),
    )

    specs[(21, 6)] = dataclasses.replace(
        c4.DAY_SPECS[(13, 6)],
        title="Metadiscourse & Argument Architecture",
        description=(
            "Learners signpost argument structure with metadiscourse (This section "
            "examines…, To conclude…, Having established…) in essays and briefings."
        ),
        focus="Metadiscourse and argument architecture: section moves, conclusions, and logical signposting.",
        lesson_goal="Teach metadiscourse for argument structure.",
        steps=(
            (
                "open",
                "Introduce metadiscourse.",
                (
                    "Greet the learner and note this is the final grammar day of the cycle. "
                    "Explain in two sentences that metadiscourse guides readers through "
                    "your argument (This section examines…, Having established…). Ask them "
                    "to open a hypothetical report section in one sentence."
                ),
            ),
            (
                "moves",
                "Teach section moves.",
                (
                    "Confirm their opener. Teach To conclude, Conversely, and Having established "
                    "that…. Ask them to link two ideas with Having established…."
                ),
            ),
            (
                "wrap_up",
                "Move to practice.",
                (
                    "If the learner has used metadiscourse correctly at least once, ask "
                    "only: Ready to try the practice task?"
                ),
            ),
        ),
        activity_ids=_act_ids(17, 6, "metadiscourse"),
        topic_overrides=(
            "Metadiscourse in an argument brief",
            "Retell a signposted mini-lecture",
            "Paraphrase with metadiscourse markers",
            "Short talk with argument signposts",
        ),
        generation_instructions=(
            (
                "Write a short argument brief with gaps for metadiscourse (This section "
                "examines, Having established, To conclude). MCQs on best marker."
            ),
            (
                "Generate a 40-50 word signposted audio; ask retell using two metadiscourse "
                "phrases."
            ),
            (
                "Give informal bullet points and ask the learner to join them with "
                "metadiscourse linkers."
            ),
            (
                "Ask for a 45-second mini presentation using at least three metadiscourse "
                "signposts."
            ),
        ),
    )

    return specs


def _communication_specs() -> dict[tuple[int, int], DaySpec]:
    """Week 22 — mirrors week 14 communication layout."""
    topics = [
        (
            "Principled Negotiation",
            "principled negotiation: interests, framing, and durable agreement",
            "negotiation",
            (
                "Welcome the learner to communication week. Explain in two sentences that "
                "principled negotiation focuses on interests, not positions, and seeks "
                "durable agreement. Ask them to describe a negotiation where interests "
                "were hidden."
            ),
            (
                "React warmly. Teach separating interests from positions (What matters is…, "
                "Our underlying need is…). Ask them to reframe one position as an interest."
            ),
        ),
        (
            "Coaching Conversation",
            "coaching conversations: questions, reflection, and ownership instead of directives",
            "coaching",
            (
                "Welcome the learner to Day 2. Explain in two sentences that coaching uses "
                "questions and reflection so the other person owns the solution. Ask about "
                "a time someone told them what to do versus helped them think."
            ),
            (
                "Model What outcome do you want? and What options have you tried? Ask them "
                "to coach you briefly on 'I keep missing deadlines.'"
            ),
        ),
        (
            "Scenario Thinking & Strategic Options",
            "scenario thinking: options, second-order effects, and explicit trade-offs",
            "scenario_thinking",
            (
                "Greet the learner. Explain in two sentences that scenario thinking weighs "
                "options, second-order effects, and trade-offs before recommending. Ask them "
                "to compare two strategic paths they know."
            ),
            (
                "Introduce If we choose X, the knock-on effect is… and On the other hand…. "
                "Ask them to name one second-order effect of their preferred option."
            ),
            (
                "Show how to end with a conditional recommendation. Ask what they would "
                "recommend and which trade-off they accept in one sentence."
            ),
        ),
        (
            "Executive Alignment",
            "executive alignment: vision, priorities, and accountability in tense rooms",
            "exec_alignment",
            (
                "Greet the learner. Explain in two sentences that executive alignment means "
                "locking vision, priorities, and owners when leaders disagree. Ask about "
                "a tense meeting they witnessed or led."
            ),
            (
                "Teach phrases like 'Let's align on the north star' and 'Who owns this by "
                "Friday?'. Ask them to open a one-minute alignment check-in."
            ),
        ),
        (
            "Precision Under Cross-Examination",
            "precision under cross-examination: short exact answers without drift",
            "cross_examination",
            (
                "Greet the learner. Explain in two sentences that cross-examination demands "
                "short, exact answers without volunteering extra detail. Ask when they "
                "have seen a speaker drift off-topic under pressure."
            ),
            (
                "Model Yes, on Tuesday, not Wednesday and That's outside my remit. Ask them "
                "to answer sharply: 'So you approved the budget?'"
            ),
        ),
        (
            "Policy-Style Brief",
            "policy-style briefs: context, issue, options, and ask on one page",
            "policy_brief",
            (
                "Greet the learner. Explain in two sentences that a policy brief moves "
                "context → issue → options → ask in tight prose. Ask which section is "
                "hardest for them to write."
            ),
            (
                "Contrast a fluffy opener with a crisp issue sentence. Ask them to write "
                "one issue sentence about a problem they know."
            ),
        ),
        (
            "Symposium Moderation",
            "symposium moderation: balance experts, synthesise views, neutral close",
            "symposium",
            (
                "Greet the learner. Explain in two sentences that moderating a symposium "
                "means balancing experts, synthesising, and closing neutrally. Ask about "
                "a panel they watched that lacked synthesis."
            ),
            (
                "Teach Let's hear a contrasting view and To synthesise, the shared theme is…. "
                "Ask them to invite one expert and summarise two views in one sentence."
            ),
        ),
    ]

    specs: dict[tuple[int, int], DaySpec] = {}
    for i, row in enumerate(topics):
        title, focus_desc, slug, *step_parts = row
        base = c4.DAY_SPECS[(14, i)]
        steps: list[tuple[str, str, str]] = [
            ("open", f"Introduce {title.lower()}.", step_parts[0]),
        ]
        if len(step_parts) == 2:
            steps.append((slug, f"Teach {title.lower()}.", step_parts[1]))
        else:
            steps.append(("structure", f"Teach {title.lower()}.", step_parts[1]))
            steps.append(("recommend", "Add recommendation or alignment.", step_parts[2]))
        steps.append(
            (
                "wrap_up",
                "Move to practice.",
                (
                    "If the learner has practised the target skill at least once, ask only: "
                    "Ready to try the practice task?"
                ),
            )
        )
        specs[(22, i)] = dataclasses.replace(
            base,
            title=title,
            description=(
                f"Learners practise {focus_desc} at C1 level using the same "
                f"read-listen-write-speak sequence as earlier communication weeks."
            ),
            focus=focus_desc.capitalize() + ".",
            lesson_goal=f"Teach {title.lower()}.",
            steps=tuple(steps),
            activity_ids=_act_ids(18, i, slug),
            topic_overrides=tuple(
                t.replace("conflict", slug)
                .replace("Constructive", title.split()[0])
                .replace("pros", "scenario")
                for t in base.topic_overrides
            ),
        )
        # Tailored overrides per day
        overrides_map = {
            0: (
                "Principled negotiation in messages",
                "Listening to interests-based negotiation",
                "Rewrite positions into interests language",
                "Roleplay principled negotiation",
            ),
            1: (
                "Coaching tone in writing",
                "Infer coaching vs telling in conversation",
                "Write coaching questions",
                "React with coaching questions in chat",
            ),
            2: (
                "Scenario comparison structure",
                "Retell a scenario comparison",
                "Write scenario options with trade-offs",
                "State a conditional recommendation aloud",
            ),
            3: (
                "Executive alignment in writing",
                "Listening to tense leadership alignment",
                "Turn notes into an alignment summary",
                "Roleplay executive alignment",
            ),
            4: (
                "Cross-examination precision in text",
                "Infer pressure questions in dialogue",
                "Write crisp answers to tough questions",
                "Explain precise answers aloud",
            ),
            5: (
                "Policy brief tone and structure",
                "Hear a one-minute policy brief",
                "Rewrite notes into a brief paragraph",
                "Small talk practising a one-line ask",
            ),
            6: (
                "Symposium structure in writing",
                "Retell a moderated panel clip",
                "Email summarising panel synthesis",
                "Present a neutral symposium close",
            ),
        }
        gens_map = {
            0: (
                "Write a negotiation exchange reframing positions as interests and ending "
                "with a durable agreement. Comprehension questions.",
                "Generate a 35-45 word dialogue using interest-based framing. MCQs on each "
                "party's underlying need.",
                "Give 3 positional statements to rewrite using interest language.",
                "Roleplay a principled negotiation with interests, options, and agreement.",
            ),
            1: (
                "Write a manager message: one directive version and one coaching version. "
                "True/False/Not Given on ownership.",
                "Generate a conversation mixing telling and coaching; infer which builds ownership.",
                "Ask the learner to write five coaching questions for a performance issue.",
                "Mini interview: respond with coaching questions, not instructions.",
            ),
            2: (
                "Provide a three-scenario comparison text; label Options, Trade-offs, Recommendation.",
                "Audio comparing strategic options with second-order effects; retell recommendation.",
                "Write a paragraph comparing two scenarios with explicit trade-offs.",
                "Speak for 45 seconds recommending one path and one accepted trade-off.",
            ),
            3: (
                "Write a tense leadership transcript aligning vision, priorities, and owners. MCQs.",
                "Generate a 35-45 word clip aligning executives on one priority and owner.",
                "Turn bullet notes into an alignment summary with owners.",
                "Roleplay opening an executive alignment moment and assigning one owner.",
            ),
            4: (
                "Write a Q&A with probing questions and two precise vs drifting answers. T/F/NG.",
                "Dialogue with cross-examination pressure; inference on evasion.",
                "Write crisp answers to three hostile questions without extra detail.",
                "Describe aloud how to answer under cross-examination in three short lines.",
            ),
            5: (
                "Provide two briefs; identify which follows context→issue→options→ask.",
                "Audio one-minute policy brief; MCQs on issue and ask.",
                "Give bullet notes; write a 4-sentence policy brief with a clear ask.",
                "Small talk practising stating a one-sentence ask to a decision-maker.",
            ),
            6: (
                "Provide a three-part symposium transcript (open, expert turns, synthesis). Label parts.",
                "Audio of a moderator balancing experts; retell synthesis.",
                "Write an email summarising a panel with neutral synthesis and next step.",
                "Deliver a 45-second neutral symposium close synthesising two views.",
            ),
        }
        specs[(22, i)] = dataclasses.replace(
            specs[(22, i)],
            topic_overrides=overrides_map[i],
            generation_instructions=gens_map[i],
        )
    return specs


_VOCAB_TOPICS_C6 = [
    (
        "Philosophy & Ideas (Accessible) - Paradigm, Empirical & Premise",
        "philosophy and ideas at accessible C1 level (paradigm, empirical, existential, premise)",
        "paradigm, empirical, existential, premise, ontology",
        "philosophy and ideas",
        "philosophy_ideas",
        "a seminar or essay discussion",
        "paradigm, empirical, premise",
        "university seminar with students debating ideas on a whiteboard",
    ),
    (
        "Diplomacy & International Relations - Treaty, Sovereignty & Envoy",
        "diplomacy and international relations (treaty, sovereignty, envoy, sanction, bilateral)",
        "treaty, sovereignty, envoy, sanction, bilateral",
        "diplomacy and international relations",
        "diplomacy_ir",
        "a diplomatic briefing",
        "treaty, sovereignty, envoy",
        "diplomats at a treaty signing with flags in the background",
    ),
    (
        "Academic Discourse - Synthesise, Juxtapose & Caveat",
        "academic discourse (synthesise, juxtapose, dichotomy, caveat, corpus)",
        "synthesise, juxtapose, dichotomy, caveat, corpus",
        "academic discourse",
        "academic_discourse",
        "a journal article or lecture",
        "synthesise, juxtapose, caveat",
        "researcher reviewing journal articles in a library",
    ),
    (
        "Corporate Strategy - Merger, Divest & Due Diligence",
        "corporate strategy (merger, divest, due diligence, benchmark, pivot)",
        "merger, divest, due diligence, benchmark, pivot",
        "corporate strategy",
        "corp_strategy",
        "a board strategy session",
        "merger, due diligence, pivot",
        "executives reviewing merger documents in a boardroom",
    ),
    (
        "Discourse & Framing - Subtext, Connotation & Rhetoric",
        "discourse and framing (subtext, connotation, polemic, rhetoric, nuance)",
        "subtext, connotation, polemic, rhetoric, nuance",
        "discourse and framing",
        "discourse_framing",
        "media or political commentary",
        "subtext, connotation, rhetoric",
        "commentator analysing speeches on a news panel",
    ),
    (
        "Precision Meta-Language - Cogent, Succinct & Granular",
        "precision meta-language about language itself (cogent, succinct, equivocate, articulate, granular)",
        "cogent, succinct, equivocate, articulate, granular",
        "precision meta-language",
        "meta_language",
        "an editing or coaching session",
        "cogent, succinct, equivocate",
        "editor marking a draft for cogent and succinct style",
    ),
    (
        "Review & Word Building - Consolidate Week 23",
        "the week's C1 vocabulary across philosophy, diplomacy, academia, strategy, discourse, and meta-language",
        "review words from week 23",
        "review and word building",
        "review_w23",
        "mixed professional and academic contexts",
        "review, prefix, suffix",
        "collage of seminar, diplomacy, boardroom, and editing scenes",
    ),
]


def _vocab_specs() -> dict[tuple[int, int], DaySpec]:
    specs: dict[tuple[int, int], DaySpec] = {}
    for i, topic in enumerate(_VOCAB_TOPICS_C6):
        spec = _vocab_day_spec(*topic, day_index=i)
        spec = dataclasses.replace(
            spec,
            description=spec.description.replace("B1+", "C1"),
            generation_instructions=tuple(
                g.replace("B1+", "C1").replace("at B1+ level", "at C1 level")
                for g in spec.generation_instructions
            ),
        )
        # Use week 15 activity id patterns
        w19 = _week_days(19)[i]
        old_slugs = [
            "innovation_tech",
            "law_justice",
            "politics_governance",
            "finance_markets",
            "psychology_behaviour",
            "rhetoric_argument",
            "review_w19",
        ]
        slug = topic[4]
        spec = dataclasses.replace(
            spec,
            activity_ids=tuple(a.id.replace(old_slugs[i], slug) for a in w19.activities),
        )
        if i == 6:
            spec = dataclasses.replace(
                spec,
                title="Review & Word Building - Consolidate Week 23",
                topic_overrides=(
                    "Week 23 vocabulary review",
                    "Mixed C1 vocabulary listening",
                    "Word-building and precision writing",
                    "Describe a scene using week 23 words",
                ),
                generation_instructions=(
                    "Match week 23 target words to definitions across all domains.",
                    "Short audio using six week-23 words; comprehension questions.",
                    "Ask the learner to build three words with prefixes/suffixes and use each in a sentence.",
                    "Describe a photo collage using at least five week-23 words aloud.",
                ),
            )
        specs[(23, i)] = spec
    return specs


_CONF_SPECS_C6 = [
    (
        "Thought Leadership",
        "state a clear point of view under pushback: claim, reason, and calm restatement",
        "thought_leadership",
        "read_comp_mcq_thought_leadership",
        "listen_shadow_thought_leadership",
        "write_sent_trans_thought_leadership",
        "speak_read_aloud_thought_leadership",
    ),
    (
        "Socratic Persuasion",
        "persuade with questions: draw out assumptions and guide others to your conclusion",
        "socratic_persuasion",
        "read_tone_id_socratic",
        "listen_mcq_socratic",
        "write_timed_socratic",
        "speak_timed_socratic",
    ),
    (
        "Impact & Legacy Narrative",
        "tell an impact and legacy narrative beyond self: why it matters to others",
        "legacy_narrative",
        "read_comp_mcq_legacy",
        "listen_tone_legacy",
        "write_sent_trans_legacy",
        "speak_pic_desc_legacy",
    ),
    (
        "Hostile Interview Recovery",
        "recover in hostile interviews: bridge, redirect, and stay concise",
        "hostile_interview",
        "read_tone_id_hostile_interview",
        "listen_shadow_hostile_interview",
        "write_timed_hostile_interview",
        "speak_smalltalk_hostile_interview",
    ),
    (
        "Senior-Leader Pitch",
        "deliver a ~2-minute senior-leader pitch: stakes, insight, and ask",
        "senior_pitch",
        "read_comp_mcq_senior_pitch",
        "listen_mcq_senior_pitch",
        "write_sent_trans_senior_pitch",
        "speak_pic_desc_senior_pitch",
    ),
    (
        "TED-Style Arc",
        "deliver a TED-style arc: hook, insight, memorable close",
        "ted_arc",
        "read_tone_id_ted_arc",
        "listen_tone_ted_arc",
        "write_timed_ted_arc",
        "speak_present_ted_arc",
    ),
    (
        "Full Confidence Showcase (C1)",
        "integrate C1 confidence skills in one capstone: POV, Socratic move, legacy, and memorable close",
        "showcase_w24",
        "read_comp_mcq_showcase_w24",
        "listen_shadow_showcase_w24",
        "write_timed_showcase_w24",
        "speak_debate_showcase_w24",
    ),
]

_CONF_GEN_C6 = [
    (
        ("POV under pushback", "Pushback listening", "Restate POV in writing", "Read POV passage aloud"),
        (
            "Story where a leader states a POV and faces pushback; MCQs on claim and reason.",
            "15-second clip with polite disagreement for shadowing.",
            "Rewrite defensive lines into calm POV restatements.",
            "55-70 word passage stating a clear POV to read aloud.",
        ),
    ),
    (
        ("Socratic tone in text", "Persuasion by questions", "Timed Socratic writing", "Timed Socratic speaking"),
        (
            "Two persuasion excerpts; identify which uses questions rather than monologue.",
            "Audio using Socratic questions; inference on assumptions drawn out.",
            "Timed paragraph persuading with three questions and a brief conclusion.",
            "Three timed prompts to persuade using questions, not lectures.",
        ),
    ),
    (
        ("Legacy narrative comprehension", "Tone in a legacy talk", "Legacy sentence transforms", "Legacy picture description"),
        (
            "Story about impact beyond self; MCQs on why it matters to others.",
            "Leader describing legacy and community impact; tone questions.",
            "Transform self-focused sentences into legacy-focused statements.",
            "Describe a photo of community impact using legacy vocabulary.",
        ),
    ),
    (
        ("Hostile interview tone", "Recovery shadowing", "Timed bridge-and-redirect writing", "Hostile interview small talk"),
        (
            "Two interview answers; identify which bridges and redirects concisely.",
            "Clip of a tough question answered with bridge and redirect for shadowing.",
            "Timed answers to three hostile questions using bridge + redirect.",
            "Small talk practising one bridge phrase and one redirect.",
        ),
    ),
    (
        ("Senior pitch comprehension", "Stakes and ask listening", "Pitch sentence transforms", "Two-minute pitch speaking"),
        (
            "Short pitch text; questions on stakes, insight, and ask.",
            "Audio of a 90-second senior pitch; MCQs on ask and stakes.",
            "Rewrite a vague pitch into stakes → insight → ask in four sentences.",
            "Describe delivering a two-minute senior-leader pitch aloud.",
        ),
    ),
    (
        ("TED arc comprehension", "Hook and close listening", "TED arc writing", "TED-style presentation"),
        (
            "Identify hook, insight, and memorable close in a short talk transcript.",
            "Audio with clear hook and close; MCQs on structure.",
            "Timed paragraph with hook, one insight, and memorable close.",
            "45-second TED-style segment with hook, insight, close.",
        ),
    ),
]


def _confidence_specs() -> dict[tuple[int, int], DaySpec]:
    specs: dict[tuple[int, int], DaySpec] = {}
    for i, (title, focus_desc, slug, *act_ids) in enumerate(_CONF_SPECS_C6):
        w20 = _week_days(20)[i]
        specs[(24, i)] = DaySpec(
            title=title,
            description=(
                f"Learners build confidence to {focus_desc}, using the same "
                f"read-listen-write-speak sequence at C1 level."
            ),
            focus=focus_desc.capitalize() + ".",
            lesson_goal=f"Build confidence to {focus_desc.split(':')[0]}.",
            steps=(
                (
                    "open",
                    "Frame the skill as small steps.",
                    (
                        "Welcome the learner to confidence week at C1. Explain in two sentences "
                        f"that {focus_desc.split(':')[0]} becomes easier with preparation and "
                        "deliberate structure. Ask them to name one high-stakes situation they "
                        "want to handle better."
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
            activity_ids=tuple(act_ids),
            topic_overrides=tuple(a.task.topic_override for a in w20.activities),
            generation_instructions=tuple(
                a.task.generation_instructions.replace("B2", "C1")
                .replace("B1+", "C1")
                .replace("B1", "C1")
                for a in w20.activities
            ),
        )
    specs[(24, 0)] = dataclasses.replace(
        specs[(24, 0)],
        topic_overrides=_CONF_GEN_C6[0][0],
        generation_instructions=_CONF_GEN_C6[0][1],
    )
    for idx, (topics, gens) in enumerate(_CONF_GEN_C6[1:], start=1):
        specs[(24, idx)] = dataclasses.replace(
            specs[(24, idx)], topic_overrides=topics, generation_instructions=gens
        )
    specs[(24, 6)] = dataclasses.replace(
        specs[(24, 6)],
        title="Full Confidence Showcase (C1)",
        topic_overrides=(
            "C1 confidence integration story",
            "Capstone shadowing clip",
            "Timed integrated C1 confidence writing",
            "Debate-style C1 showcase speaking",
        ),
        generation_instructions=(
            (
                "Write an encouraging story where the speaker holds a POV under pushback, "
                "uses one Socratic question, states legacy impact, and closes memorably. MCQs."
            ),
            (
                "Generate a confident 20-second capstone clip mixing POV, question, and close "
                "for shadowing."
            ),
            (
                "Ask for a timed paragraph integrating POV, one question, legacy, and a memorable close."
            ),
            (
                "Set up a short debate-style showcase: rebut one point, bridge one hostile question, "
                "end with a call to action."
            ),
        ),
    )
    return specs


DAY_SPECS: dict[tuple[int, int], DaySpec] = {}
DAY_SPECS.update(_grammar_specs())
DAY_SPECS.update(_communication_specs())
DAY_SPECS.update(_vocab_specs())
DAY_SPECS.update(_confidence_specs())


def build_week(week: int) -> WeekSource:
    shell = next(w for w in WEEKS_24 if w.week_number == week)
    days = []
    for d in range(7):
        mirror = _mirror_day(week, d)
        spec = DAY_SPECS[(week, d)]
        days.append(_build_day(mirror, spec))
    return dataclasses.replace(shell, days=tuple(days))


def emit_cycle6() -> str:
    lines = [
        "    # ── Cycle 6 — Mastery (C1) ──────────────────────────────────",
    ]
    for week in (21, 22, 23, 24):
        w = build_week(week)
        lines.append("    WeekSource(")
        lines.append(f"        week_number={w.week_number},")
        lines.append(f'        theme_type="{w.theme_type}",')
        lines.append(f'        cefr_level="{w.cefr_level}",')
        lines.append(
            f"        sub_level_min={w.sub_level_min}, sub_level_max={w.sub_level_max},"
        )
        lines.append("        days=(")
        for day in w.days:
            lines.extend(_emit_day(day, "            "))
        lines.append("        ),")
        lines.append("    ),")
    return "\n".join(lines)


def patch_source_file() -> None:
    path = Path(__file__).resolve().parents[1] / "app/modules/curriculum/data/source_L_C1C2.py"
    text = path.read_text()
    start = text.index("    # ── Cycle 6 —")
    new_block = emit_cycle6() + "\n)\n"
    path.write_text(text[:start] + new_block)
    print(f"Patched {path} (weeks 21-24)")


if __name__ == "__main__":
    patch_source_file()
