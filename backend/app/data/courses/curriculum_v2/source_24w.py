"""24-week curriculum source data.

Content authored from the restructure spec §6. Each `WeekSource` lists 7 day
entries as (topic, explanation_brief) tuples — the loader turns these into
fully-shaped week/day records with stable IDs and archetype suggestions.

When updating content here:
  - Keep the 24 weeks structured as 6 cycles × 4 themes (grammar →
    communication → vocabulary → confidence). Tests enforce this.
  - Keep exactly 7 days per week. Tests enforce this.
  - Use legacy DB sub-skill names ONLY in code; this file is content-facing,
    so theme_type uses the doc names (grammar/communication/vocabulary/
    confidence), which are themes, not sub-skills.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WeekSource:
    week_number: int
    theme_type: str   # grammar | communication | vocabulary | confidence
    title: str
    cefr_level: str   # A1 | A2 | B1 | B1+ | B2 | C1 | C2
    sub_level_min: int
    sub_level_max: int
    learning_goal: str
    days: tuple[tuple[str, str], ...]  # (topic, explanation_brief), len == 7


WEEKS_24: tuple[WeekSource, ...] = (
    # ── Cycle 1 — Foundation (A1) ─────────────────────────────────
    WeekSource(
        week_number=1,
        theme_type="grammar",
        title="Being and Belonging",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        learning_goal="Master 'to be' + possessives + simple present in the affirmative.",
        days=(
            (
                "Simple Present Tense — Subject-Verb Agreement",
                "Using simple present in affirmative sentences: I work, he/she works. "
                "Frequency adverbs: always, usually, often, sometimes, never. "
                "Contrast with 'to be' vs. action verbs.",
            ),
            ("My, your, his, her, our, their", "Possessive adjectives matched to subjects."),
            ("Simple present (positive): I work, she works", "Affirmative simple present with third-person -s."),
            ("This / that / these / those + a / an / the", "Demonstratives and articles in basic sentences."),
            ("Negative present: I don't, she doesn't", "Negation with do/does + base verb."),
            ("Yes/No questions: Do you...? Does she...?", "Question form with do/does."),
            ("Review + light speaking drill", "Mixed practice of the week's structures aloud."),
        ),
    ),
    WeekSource(
        week_number=2,
        theme_type="communication",
        title="Introducing Yourself",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        learning_goal="Comfortably introduce yourself in 4–5 sentences in any setting.",
        days=(
            ("Name + age + country + city", "Saying who you are and where you're from."),
            ("Job / studies / what you do", "Describing your work or studies in one sentence."),
            ("Family — basic mentions", "Saying who you live with in simple terms."),
            ("Hobbies — like / love / enjoy", "Stating preferences with the right verb forms."),
            ("Polite greetings and closings", "Hello, nice to meet you, see you, goodbye."),
            ("Full self-intro practice", "Stringing all pieces into a coherent intro."),
            ("Roleplay: meeting someone new", "Realistic first-meeting exchange."),
        ),
    ),
    WeekSource(
        week_number=3,
        theme_type="vocabulary",
        title="Daily Life Words",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        learning_goal="Acquire 80–100 high-frequency words for daily routines.",
        days=(
            ("Home and rooms", "Names of rooms, furniture, and household items."),
            ("Food and drink basics", "Common foods, drinks, and eating verbs."),
            ("Clothes and colors", "Everyday clothing and basic colour vocabulary."),
            ("Days, times, numbers", "Time-telling, weekdays, numbers up to 100."),
            ("Weather and seasons", "Describing weather and naming the seasons."),
            ("Verbs of daily routine", "Wake, eat, leave, return — core daily-life actions."),
            ("Vocabulary consolidation game", "Mixed retrieval practice of the week's words."),
        ),
    ),
    WeekSource(
        week_number=4,
        theme_type="confidence",
        title="Saying Your First Sentences Out Loud",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        learning_goal="Beat the freeze response — produce simple English aloud without panic.",
        days=(
            ("Reading aloud — short sentences", "Comfortable production of pre-written lines."),
            ("Repeat after audio (shadowing basics)", "Match a native speaker's rhythm at slow pace."),
            ("Answer simple personal questions", "Spontaneous one-sentence answers."),
            ("Describe a photo in 3 sentences", "Picture-prompt speaking without overthinking."),
            ("30-second self-intro recording", "Time-boxed spoken self-introduction."),
            ("Quick small talk: weather, weekend", "Two-line social exchanges."),
            ("Speaking confidence reflection + recap", "Compare today's recording to Day 1's."),
        ),
    ),

    # ── Cycle 2 — Daily Life (A2) ─────────────────────────────────
    WeekSource(
        week_number=5,
        theme_type="grammar",
        title="What I Did and What I'll Do",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        learning_goal="Past simple plus future with will / going to.",
        days=(
            ("Regular past: worked, watched, played", "Forming past simple with -ed endings."),
            ("Irregular past: went, did, saw, had", "High-frequency irregular past forms."),
            ("Past negative and questions", "didn't + base verb; did you / did she."),
            ("Future with 'will'", "Spontaneous decisions and predictions."),
            ("Future with 'going to'", "Planned intentions and clear evidence."),
            ("Mixed time references", "Switching between past and future in one paragraph."),
            ("Past + future review + writing task", "Short bio: yesterday and tomorrow."),
        ),
    ),
    WeekSource(
        week_number=6,
        theme_type="communication",
        title="Asking for Things",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        learning_goal="Ask questions, make requests, and ask for clarification politely.",
        days=(
            ("Information questions", "What, where, when, who, why, how openers."),
            ("Polite requests", "Could you...? Would you mind...? formulas."),
            ("Asking for repetition / clarification", "Sorry, could you say that again? formulas."),
            ("At a shop / cafe / station", "Service-context request patterns."),
            ("Asking a colleague for help", "Workplace-context polite asks."),
            ("Asking on phone / video call", "Audio-only requests and confirmations."),
            ("Mixed roleplay practice", "Multiple scenarios in one speaking session."),
        ),
    ),
    WeekSource(
        week_number=7,
        theme_type="vocabulary",
        title="Workplace Basics",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        learning_goal="Build 100 workplace words usable even outside an office setting.",
        days=(
            ("Office objects and rooms", "Desk, meeting room, kitchen, reception."),
            ("Roles and departments", "Manager, intern, HR, finance, engineering."),
            ("Common workplace verbs", "Attend, schedule, share, send, follow up."),
            ("Email vocabulary", "Subject, attachment, reply, forward, signature."),
            ("Meeting vocabulary", "Agenda, action item, minutes, next steps."),
            ("Time at work", "Deadline, schedule, shift, overtime, break."),
            ("Workplace small talk vocab", "How was your weekend? Got any plans?"),
        ),
    ),
    WeekSource(
        week_number=8,
        theme_type="confidence",
        title="Speaking Without Pausing Too Long",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        learning_goal="Produce 60 seconds of speech without freezing.",
        days=(
            ("30-second timed speaking", "Stretch the comfortable-speech window."),
            ("Picture description timed", "Push past the first-three-sentence wall."),
            ("Recording voice messages", "Audio-only social production."),
            ("Telephoning basics", "Hello, hold on, sorry — could you repeat?"),
            ("Recording a short voice memo summary", "Talk for 45 seconds on a topic."),
            ("Spontaneous topic speaking", "Three random prompts, one minute each."),
            ("Reflection + recording self-comparison", "Compare to Week 4's recordings."),
        ),
    ),

    # ── Cycle 3 — Functioning (B1) ────────────────────────────────
    WeekSource(
        week_number=9,
        theme_type="grammar",
        title="Now, Always, Sometimes",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        learning_goal="Present continuous + present-simple distinction + adverbs of frequency.",
        days=(
            ("Present continuous form", "Be + verb-ing; what is happening right now."),
            ("Present simple vs continuous", "Routine versus current action."),
            ("Adverbs of frequency", "Always, usually, often, sometimes, never."),
            ("Stative verbs", "Know, like, want — not used in continuous."),
            ("Future continuous + future plans", "Will be doing; arrangements with continuous."),
            ("Mixed practice", "Switching tenses to match meaning."),
            ("Review + speaking task", "Talk about a typical day, today, and tomorrow."),
        ),
    ),
    WeekSource(
        week_number=10,
        theme_type="communication",
        title="Describing Routines and Plans",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        learning_goal="Explain what you do, what you're doing now, and what you'll do next.",
        days=(
            ("Describe a typical day", "Morning to night in clear sequence."),
            ("Describe a typical work / study week", "Recurring weekly rhythm."),
            ("Describe today and this week", "Switch into the continuous and specific dates."),
            ("Describe weekend plans", "Going to + scheduling vocabulary."),
            ("Describe a 6-month / 1-year plan", "Longer-arc goals with hedging."),
            ("Compare two routines", "Yours vs a friend's — comparative language."),
            ("Spoken routine description", "Two-minute talk linked together."),
        ),
    ),
    WeekSource(
        week_number=11,
        theme_type="vocabulary",
        title="Emotions and Opinions",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        learning_goal="Build 80+ words for naming feelings and stating thoughts.",
        days=(
            ("Positive emotions", "Happy → thrilled, content, satisfied."),
            ("Negative emotions", "Sad → frustrated, disappointed, anxious."),
            ("Opinion verbs", "Think, believe, feel, suppose."),
            ("Agreeing and disagreeing softly", "I see your point but…; sort of, kind of."),
            ("Strong opinions vs cautious opinions", "I'm convinced that… vs it seems to me."),
            ("Reactions in conversation", "Wow, really, that's interesting — listener cues."),
            ("Mixed emotional + opinion writing", "Short paragraph using new vocabulary."),
        ),
    ),
    WeekSource(
        week_number=12,
        theme_type="confidence",
        title="Expressing What You Think",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        learning_goal="State and defend an opinion in 60 seconds.",
        days=(
            ("I think / I believe / In my opinion", "Standard opinion openers."),
            ("Reasoning connectors", "Because, since, that's why."),
            ("Giving examples", "For example, like, such as."),
            ("Disagreeing politely", "I'd see it differently, actually."),
            ("Opinion + reason + example structure", "OREO-style mini-arguments."),
            ("1-minute opinion speaking", "Time-boxed defended position."),
            ("Reflection + recording review", "Self-critique against the OREO structure."),
        ),
    ),

    # ── Cycle 4 — Connecting (B1+ / B2) ───────────────────────────
    WeekSource(
        week_number=13,
        theme_type="grammar",
        title="Already, Yet, Still",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        learning_goal="Present perfect, past perfect, and the time markers that signal them.",
        days=(
            ("Present perfect form", "Have / has + past participle."),
            ("Present perfect vs past simple", "Choosing based on time relevance."),
            ("Time markers", "Ever, never, already, yet, just, since, for."),
            ("Present perfect continuous", "How long something has been happening."),
            ("Past perfect — narrative use", "Action before another past action."),
            ("All four tenses contrasted", "Past simple / past perfect / present perfect / continuous."),
            ("Tense review + writing task", "Short narrative using all four."),
        ),
    ),
    WeekSource(
        week_number=14,
        theme_type="communication",
        title="Telling Stories",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        learning_goal="Narrate a real or imagined event with clear structure.",
        days=(
            ("Story structure", "Setting → action → result framing."),
            ("Sequence words", "First, then, after that, finally."),
            ("Time descriptions in narrative", "A few minutes later; the next day."),
            ("Adding emotion / reaction", "Surprise, frustration, relief markers."),
            ("A funny / embarrassing story", "Light-stakes narrative practice."),
            ("A challenging school / work moment", "Higher-stakes structured story."),
            ("A 2-minute personal story recording", "Sustained spoken narrative."),
        ),
    ),
    WeekSource(
        week_number=15,
        theme_type="vocabulary",
        title="Travel and Movement",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        learning_goal="Travel, transport, directions, and descriptions of places.",
        days=(
            ("Transport vocabulary", "Train, flight, transfer, gate, platform."),
            ("Accommodation vocabulary", "Booking, check-in, deposit, single room."),
            ("Direction-giving phrases", "Turn left, head straight, opposite the bank."),
            ("City vs countryside descriptors", "Bustling, peaceful, rural, urban, sprawling."),
            ("Tourist + cultural vocabulary", "Heritage, landmark, guided tour, souvenir."),
            ("Travel problems", "Delayed, missed, cancelled, lost luggage."),
            ("Travel story writing + speaking", "Three-paragraph trip recap."),
        ),
    ),
    WeekSource(
        week_number=16,
        theme_type="confidence",
        title="Advanced Small Talk",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        learning_goal="Sustain a 3-minute casual conversation.",
        days=(
            ("Topic-starters", "Weather, weekend, recent news."),
            ("Follow-up questions", "Really? How was that? Did you enjoy it?"),
            ("Active listening sounds", "Mhmm, oh wow, that's interesting, no way."),
            ("Bridging topics", "Speaking of that…; that reminds me of…"),
            ("Polite exits from conversation", "Anyway, I should get going; nice catching up."),
            ("Full simulated small talk", "Three-minute back-and-forth roleplay."),
            ("Conversation reflection", "Where the freeze hit; what to swap next time."),
        ),
    ),

    # ── Cycle 5 — Reasoning (B2) ──────────────────────────────────
    WeekSource(
        week_number=17,
        theme_type="grammar",
        title="If This, Then That",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        learning_goal="All four conditional forms.",
        days=(
            ("Zero conditional", "General truths and laws of nature."),
            ("First conditional", "Real or likely future."),
            ("Second conditional", "Unreal or hypothetical present."),
            ("Third conditional", "Unreal past — regrets and counterfactuals."),
            ("Mixed conditionals", "Past condition with present result, etc."),
            ("Wish + if only", "Wish-clauses across past, present, future."),
            ("Conditional speaking task", "Three what-if prompts with reasoning."),
        ),
    ),
    WeekSource(
        week_number=18,
        theme_type="communication",
        title="Meetings and Disagreement",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        learning_goal="Contribute professionally to meeting conversations.",
        days=(
            ("Meeting language", "Let's start; can I add; to summarize."),
            ("Stating your point clearly", "Concise opener, then the point, then the why."),
            ("Polite disagreement", "I see it slightly differently; my concern is…"),
            ("Building on others' points", "Yes, and…; adding to that…"),
            ("Clarifying and confirming", "Just to make sure I follow; so we agree that…"),
            ("Suggesting and proposing", "What if we…; one option would be…"),
            ("Full simulated meeting roleplay", "Five-minute discussion with two agenda items."),
        ),
    ),
    WeekSource(
        week_number=19,
        theme_type="vocabulary",
        title="Technology and Business",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        learning_goal="100+ words for modern professional contexts.",
        days=(
            ("Tech and software vocab", "Deploy, integrate, debug, ship, rollback."),
            ("AI / data / digital terms", "Model, dataset, inference, latency, embedding."),
            ("Business processes", "Budget, deadline, scope, deliverable, milestone."),
            ("Corporate hierarchy and roles", "Director, VP, individual contributor, lead."),
            ("Numbers in business", "Growth, percent, increase, churn, run-rate."),
            ("Business idioms", "Touch base, ballpark, deep dive, low-hanging fruit."),
            ("Writing a tech-business paragraph", "Mini-update using the week's terms."),
        ),
    ),
    WeekSource(
        week_number=20,
        theme_type="confidence",
        title="Presenting an Idea",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        learning_goal="Deliver a 90-second structured mini-presentation.",
        days=(
            ("Opening lines", "Today I'll talk about…; the goal is to…"),
            ("Signposting", "Firstly; moving on; finally."),
            ("Highlighting key points", "The most important thing here is…"),
            ("Handling a Q&A", "Great question; let me address that in two parts."),
            ("Body language phrasing", "Open with confidence; pause for emphasis."),
            ("Full 90-second presentation recording", "End-to-end timed delivery."),
            ("Self-review + improvement plan", "Identify two things to tighten."),
        ),
    ),

    # ── Cycle 6 — Polishing (C1) ──────────────────────────────────
    WeekSource(
        week_number=21,
        theme_type="grammar",
        title="Can, Should, Must, Be Done",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        learning_goal="Full modal system plus passive voice.",
        days=(
            ("Ability and possibility modals", "Can, could, may, might."),
            ("Advice and obligation", "Should, must, have to, ought to."),
            ("Past modals", "Could have, should have, must have."),
            ("Passive voice — simple tenses", "Form and use across present / past."),
            ("Passive — complex tenses", "Perfect and continuous passives."),
            ("Modal + passive combinations", "It should be done; it might have been lost."),
            ("Formal writing task using modals", "Short policy memo or product brief."),
        ),
    ),
    WeekSource(
        week_number=22,
        theme_type="communication",
        title="Interviews and Negotiation",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        learning_goal="Navigate professional high-stakes conversations.",
        days=(
            ("Standard interview questions", "Tell me about yourself; biggest weakness."),
            ("STAR-method storytelling", "Situation, task, action, result."),
            ("Salary / scope / deadline negotiation", "Anchoring and concession language."),
            ("Diplomatic disagreement", "I hear you; my concern is the timeline."),
            ("Asking strong follow-up questions", "What does success look like in 90 days?"),
            ("Full simulated interview roleplay", "Behavioural + technical mix."),
            ("Negotiation roleplay", "Two-party multi-issue exchange."),
        ),
    ),
    WeekSource(
        week_number=23,
        theme_type="vocabulary",
        title="Abstract and Academic",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        learning_goal="80+ abstract / academic words for nuanced expression.",
        days=(
            ("Linking words", "Moreover, however, nevertheless, consequently."),
            ("Cause-effect vocabulary", "Stems from; gives rise to; attributable to."),
            ("Hedging language", "Tend to; appear to; seem; in some cases."),
            ("Critical thinking vocab", "Assumption, evidence, argument, counterexample."),
            ("Education / research vocab", "Hypothesis, methodology, peer review, citation."),
            ("Abstract concepts", "Justice, freedom, equity, accountability."),
            ("Academic paragraph writing", "Claim → evidence → analysis → restatement."),
        ),
    ),
    WeekSource(
        week_number=24,
        theme_type="confidence",
        title="Debate and Defending an Idea",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        learning_goal="Argue a point under pressure with structure and tone control.",
        days=(
            ("Debate structure", "Claim → evidence → conclusion."),
            ("Rebuttal phrases", "That may be true, but…; on the other hand…"),
            ("Tone control under disagreement", "Stay calm; lower pace; concede small."),
            ("Strong vs reasonable opinions", "Bold claim with caveats vs hedged stance."),
            ("1-minute argument speaking", "Time-boxed single-issue defense."),
            ("Full 2-minute debate roleplay", "Two exchanges with rebuttal."),
            ("Final reflection + course completion", "Compare to Week 4's first recording."),
        ),
    ),
)
