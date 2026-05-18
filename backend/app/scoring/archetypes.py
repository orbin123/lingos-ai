"""Static archetype registry — the one source of truth for archetype IDs,
weight maps, and UI widget bindings.

Each entry is validated at import time by `ArchetypeSpec` (weights sum to 1.0;
sub-skill names match `SUB_SKILLS`). A bad weight crashes the module import —
that's the contract.

Naming: the doc says `thought_org` / `listening` / `tone_social` for three
sub-skills. We store the legacy DB names `expression` / `comprehension` /
`tone` instead. See RESTRUCTURE_DECISIONS.md §2.
"""

from __future__ import annotations

from app.scoring.types import ArchetypeSpec


# ── Reading ────────────────────────────────────────────────────────

_READING: tuple[ArchetypeSpec, ...] = (
    ArchetypeSpec(
        archetype_id="READ_COMP_MCQ",
        name="Reading Comprehension MCQ",
        core_activity="read",
        description="Passage followed by 4–5 multiple-choice questions.",
        ui_widget="MCQList",
        themes_supported=("grammar", "communication", "vocabulary"),
        cefr_min="A1", cefr_max="C2",
        weight_map={"grammar": 0.25, "vocabulary": 0.40, "expression": 0.35},
        rubric=("accuracy", "comprehension_depth", "vocab_inference"),
    ),
    ArchetypeSpec(
        archetype_id="READ_TFNG",
        name="True / False / Not Given",
        core_activity="read",
        description="Passage with statements judged True / False / Not Given.",
        ui_widget="TrueFalseNotGiven",
        themes_supported=("grammar", "communication"),
        cefr_min="A2", cefr_max="C2",
        weight_map={"grammar": 0.20, "vocabulary": 0.30, "expression": 0.50},
        rubric=("accuracy", "inference", "comprehension_depth"),
    ),
    ArchetypeSpec(
        archetype_id="READ_ERROR_SPOT",
        name="Error Spotting",
        core_activity="read",
        description="Sentence list — flag which sentences contain a grammar error.",
        ui_widget="ErrorSpotting",
        themes_supported=("grammar",),
        cefr_min="A1", cefr_max="C2",
        weight_map={"grammar": 0.70, "vocabulary": 0.30},
        rubric=("accuracy", "grammar_recognition"),
    ),
    ArchetypeSpec(
        archetype_id="READ_CLOZE",
        name="Cloze (Fill-in-blanks)",
        core_activity="read",
        description="Paragraph with blanks; pick the correct option per blank.",
        ui_widget="FillInBlanks",
        themes_supported=("grammar", "vocabulary"),
        cefr_min="A1", cefr_max="C2",
        weight_map={"grammar": 0.50, "vocabulary": 0.35, "expression": 0.15},
        rubric=("accuracy", "grammar", "vocabulary_use"),
    ),
    ArchetypeSpec(
        archetype_id="READ_WORD_MATCH",
        name="Word ↔ Meaning Match",
        core_activity="read",
        description="Match each vocabulary item to its meaning.",
        ui_widget="MCQList",
        themes_supported=("vocabulary",),
        cefr_min="A1", cefr_max="C2",
        weight_map={"vocabulary": 1.00},
        rubric=("accuracy",),
    ),
    ArchetypeSpec(
        archetype_id="READ_CONTEXT_MCQ",
        name="Contextual Vocabulary",
        core_activity="read",
        description="Short context + MCQ on what a word means in context.",
        ui_widget="MCQList",
        themes_supported=("vocabulary", "communication"),
        cefr_min="A1", cefr_max="C2",
        weight_map={"grammar": 0.10, "vocabulary": 0.70, "expression": 0.20},
        rubric=("accuracy", "vocab_inference"),
    ),
    ArchetypeSpec(
        archetype_id="READ_TONE_ID",
        name="Tone Identification",
        core_activity="read",
        description="Passage + MCQ on the speaker / writer's tone.",
        ui_widget="MCQList",
        themes_supported=("confidence", "communication"),
        cefr_min="A2", cefr_max="C2",
        weight_map={"vocabulary": 0.30, "tone": 0.70},
        rubric=("accuracy", "tone_recognition"),
    ),
    ArchetypeSpec(
        archetype_id="READ_STRUCTURE_ID",
        name="Structure Identification",
        core_activity="read",
        description="Label intro / body / conclusion sections in a passage.",
        ui_widget="OpenTextList",
        themes_supported=("communication",),
        cefr_min="B1", cefr_max="C2",
        weight_map={"vocabulary": 0.20, "expression": 0.80},
        rubric=("accuracy", "structural_understanding"),
    ),
)


# ── Writing ────────────────────────────────────────────────────────

_WRITING: tuple[ArchetypeSpec, ...] = (
    ArchetypeSpec(
        archetype_id="WRITE_SENT_TRANS",
        name="Sentence Transformation",
        core_activity="write",
        description="Rewrite a sentence to match a target form (tense, voice, …).",
        ui_widget="SentenceTransform",
        themes_supported=("grammar",),
        cefr_min="A1", cefr_max="C2",
        weight_map={"grammar": 0.70, "vocabulary": 0.20, "expression": 0.10},
        rubric=("grammatical_accuracy", "vocabulary", "coherence"),
    ),
    ArchetypeSpec(
        archetype_id="WRITE_ERROR_CORR",
        name="Error Correction",
        core_activity="write",
        description="Rewrite an incorrect sentence so it's grammatically correct.",
        ui_widget="ErrorCorrection",
        themes_supported=("grammar",),
        cefr_min="A1", cefr_max="C2",
        weight_map={"grammar": 0.80, "vocabulary": 0.20},
        rubric=("grammatical_accuracy", "vocabulary"),
    ),
    ArchetypeSpec(
        archetype_id="WRITE_PARA",
        name="Paragraph Writing",
        core_activity="write",
        description="Write a paragraph (80–150 words) on a prompt.",
        ui_widget="OpenTextList",
        themes_supported=("grammar", "communication", "vocabulary"),
        cefr_min="A2", cefr_max="C2",
        weight_map={"grammar": 0.35, "vocabulary": 0.25, "expression": 0.40},
        rubric=("grammatical_accuracy", "vocabulary", "coherence", "task_completion"),
    ),
    ArchetypeSpec(
        archetype_id="WRITE_ESSAY",
        name="Structured Essay",
        core_activity="write",
        description="Multi-section essay (200–400 words).",
        ui_widget="StructuredEssay",
        themes_supported=("communication",),
        cefr_min="B1", cefr_max="C2",
        weight_map={"grammar": 0.25, "vocabulary": 0.30, "expression": 0.45},
        rubric=("grammatical_accuracy", "vocabulary", "coherence", "task_completion"),
    ),
    ArchetypeSpec(
        archetype_id="WRITE_EMAIL",
        name="Email Writing",
        core_activity="write",
        description="Compose a scenario-based email of 80–200 words.",
        ui_widget="OpenTextList",
        themes_supported=("communication",),
        cefr_min="A2", cefr_max="C2",
        weight_map={"grammar": 0.25, "vocabulary": 0.20, "expression": 0.15, "tone": 0.40},
        rubric=("grammatical_accuracy", "vocabulary", "coherence", "task_completion", "register"),
    ),
    ArchetypeSpec(
        archetype_id="WRITE_CONCISE",
        name="Conciseness Rewrite",
        core_activity="write",
        description="Trim a wordy sentence to its tightest correct form.",
        ui_widget="ErrorCorrection",
        themes_supported=("grammar", "communication"),
        cefr_min="A2", cefr_max="C2",
        weight_map={"grammar": 0.30, "vocabulary": 0.40, "expression": 0.30},
        rubric=("conciseness", "grammatical_accuracy", "vocabulary"),
    ),
    ArchetypeSpec(
        archetype_id="WRITE_WORD_UPGRADE",
        name="Word Upgrade",
        core_activity="write",
        description="Replace a simple word with a more precise / advanced one.",
        ui_widget="OpenTextList",
        themes_supported=("vocabulary",),
        cefr_min="A2", cefr_max="C2",
        weight_map={"grammar": 0.20, "vocabulary": 0.80},
        rubric=("vocabulary_range", "appropriateness"),
    ),
    ArchetypeSpec(
        archetype_id="WRITE_PARAPHRASE",
        name="Paraphrasing",
        core_activity="write",
        description="Re-express the same idea in your own words.",
        ui_widget="OpenTextList",
        themes_supported=("communication", "vocabulary"),
        cefr_min="A2", cefr_max="C2",
        weight_map={"grammar": 0.20, "vocabulary": 0.40, "expression": 0.40},
        rubric=("grammatical_accuracy", "vocabulary", "coherence"),
    ),
    ArchetypeSpec(
        archetype_id="WRITE_REGISTER",
        name="Register Conversion",
        core_activity="write",
        description="Rewrite a sentence in a different register (formal ↔ informal).",
        ui_widget="ErrorCorrection",
        themes_supported=("communication", "confidence"),
        cefr_min="B1", cefr_max="C2",
        weight_map={"grammar": 0.15, "vocabulary": 0.25, "tone": 0.60},
        rubric=("register", "vocabulary"),
    ),
    ArchetypeSpec(
        archetype_id="WRITE_IDEA_PARA",
        name="Idea Paraphrasing",
        core_activity="write",
        description="Restate a concept (not just words) in your own framing.",
        ui_widget="OpenTextList",
        themes_supported=("communication",),
        cefr_min="B1", cefr_max="C2",
        weight_map={"grammar": 0.10, "vocabulary": 0.30, "expression": 0.60},
        rubric=("coherence", "task_completion", "vocabulary"),
    ),
    ArchetypeSpec(
        archetype_id="WRITE_SUMMARY",
        name="Passage Summary",
        core_activity="write",
        description="Summarize a passage in N words.",
        ui_widget="PassageSummary",
        themes_supported=("communication",),
        cefr_min="A2", cefr_max="C2",
        weight_map={"grammar": 0.20, "vocabulary": 0.30, "expression": 0.50},
        rubric=("conciseness", "comprehension_depth", "coherence"),
    ),
    ArchetypeSpec(
        archetype_id="WRITE_TIMED",
        name="Timed Writing",
        core_activity="write",
        description="Write quickly against a hard timer.",
        ui_widget="TimedWriting",
        themes_supported=("confidence",),
        cefr_min="A2", cefr_max="C2",
        weight_map={"grammar": 0.20, "vocabulary": 0.25, "fluency": 0.30, "expression": 0.25},
        rubric=("fluency", "grammatical_accuracy", "task_completion"),
    ),
    ArchetypeSpec(
        archetype_id="WRITE_VOICE_CONV",
        name="Active ↔ Passive Voice",
        core_activity="write",
        description="Convert sentence voice while preserving meaning.",
        ui_widget="SentenceTransform",
        themes_supported=("grammar",),
        cefr_min="A2", cefr_max="C2",
        weight_map={"grammar": 0.80, "vocabulary": 0.20},
        rubric=("grammatical_accuracy",),
    ),
    ArchetypeSpec(
        archetype_id="WRITE_BULLETS_TO_PARA",
        name="Bullets → Paragraph",
        core_activity="write",
        description="Convert bullet points into coherent prose.",
        ui_widget="OpenTextList",
        themes_supported=("communication",),
        cefr_min="A2", cefr_max="C2",
        weight_map={"grammar": 0.20, "vocabulary": 0.20, "expression": 0.60},
        rubric=("coherence", "task_completion"),
    ),
)


# ── Listening ──────────────────────────────────────────────────────

_LISTENING: tuple[ArchetypeSpec, ...] = (
    ArchetypeSpec(
        archetype_id="LISTEN_MCQ",
        name="Audio MCQ",
        core_activity="listen",
        description="Audio clip followed by multiple-choice questions.",
        ui_widget="ListenAndAnswer+MCQList",
        themes_supported=("grammar", "communication", "vocabulary"),
        cefr_min="A1", cefr_max="C2",
        weight_map={"vocabulary": 0.25, "expression": 0.15, "comprehension": 0.60},
        rubric=("accuracy", "detail_capture", "main_idea"),
    ),
    ArchetypeSpec(
        archetype_id="LISTEN_CLOZE",
        name="Cloze Listening",
        core_activity="listen",
        description="Fill words from audio into a transcript.",
        ui_widget="ListenAndAnswer+FillInBlanks",
        themes_supported=("grammar", "vocabulary"),
        cefr_min="A1", cefr_max="C2",
        weight_map={"grammar": 0.30, "vocabulary": 0.20, "comprehension": 0.50},
        rubric=("accuracy", "detail_capture"),
    ),
    ArchetypeSpec(
        archetype_id="LISTEN_DICTATION",
        name="Dictation",
        core_activity="listen",
        description="Type what you hear (1–3 sentences).",
        ui_widget="ListenAndAnswer+OpenTextList",
        themes_supported=("grammar", "vocabulary"),
        cefr_min="A1", cefr_max="C2",
        weight_map={"grammar": 0.30, "vocabulary": 0.20, "comprehension": 0.50},
        rubric=("accuracy", "detail_capture"),
    ),
    ArchetypeSpec(
        archetype_id="LISTEN_INFER",
        name="Inference Listening",
        core_activity="listen",
        description="Audio + interpretive (implied-meaning) MCQ.",
        ui_widget="ListenAndAnswer+MCQList",
        themes_supported=("communication",),
        cefr_min="B1", cefr_max="C2",
        weight_map={"vocabulary": 0.15, "expression": 0.35, "comprehension": 0.50},
        rubric=("inference", "comprehension_depth"),
    ),
    ArchetypeSpec(
        archetype_id="LISTEN_RETELL",
        name="Retell What You Heard",
        core_activity="listen",
        description="Speak a summary of an audio clip back.",
        ui_widget="ListenAndAnswer+SpeakAndRecord",
        themes_supported=("communication", "confidence"),
        cefr_min="B1", cefr_max="C2",
        weight_map={"vocabulary": 0.20, "fluency": 0.20, "expression": 0.30, "comprehension": 0.30},
        rubric=("main_idea", "fluency", "vocabulary"),
    ),
    ArchetypeSpec(
        archetype_id="LISTEN_SHADOW",
        name="Shadow Speaking",
        core_activity="listen",
        description="Repeat after audio while it plays.",
        ui_widget="ListenAndAnswer+SpeakAndRecord",
        themes_supported=("confidence",),
        cefr_min="A1", cefr_max="C2",
        weight_map={"pronunciation": 0.45, "fluency": 0.25, "comprehension": 0.30},
        rubric=("pronunciation", "fluency"),
    ),
    ArchetypeSpec(
        archetype_id="LISTEN_TONE",
        name="Detect Speaker Tone",
        core_activity="listen",
        description="Identify emotion / register from an audio clip.",
        ui_widget="ListenAndAnswer+MCQList",
        themes_supported=("confidence", "communication"),
        cefr_min="A2", cefr_max="C2",
        weight_map={"comprehension": 0.45, "tone": 0.55},
        rubric=("tone_recognition", "inference"),
    ),
)


# ── Speaking ───────────────────────────────────────────────────────

_SPEAKING: tuple[ArchetypeSpec, ...] = (
    ArchetypeSpec(
        archetype_id="SPEAK_READ_ALOUD",
        name="Read Aloud",
        core_activity="speak",
        description="Read a passage aloud — focus on pronunciation.",
        ui_widget="SpeakAndRecord",
        themes_supported=("confidence",),
        cefr_min="A1", cefr_max="C2",
        weight_map={"grammar": 0.10, "pronunciation": 0.70, "fluency": 0.20},
        rubric=("pronunciation", "fluency"),
    ),
    ArchetypeSpec(
        archetype_id="SPEAK_PIC_DESC",
        name="Picture Description",
        core_activity="speak",
        description="Describe an image in 3–5 sentences.",
        ui_widget="SpeakAndRecord",
        themes_supported=("confidence", "vocabulary"),
        cefr_min="A1", cefr_max="C2",
        weight_map={"grammar": 0.20, "vocabulary": 0.30, "fluency": 0.30, "expression": 0.20},
        rubric=("fluency", "vocabulary", "task_completion"),
    ),
    ArchetypeSpec(
        archetype_id="SPEAK_TIMED",
        name="Timed Speaking",
        core_activity="speak",
        description="Speak on a prompt without long pauses.",
        ui_widget="SpeakAndRecord",
        themes_supported=("confidence",),
        cefr_min="A1", cefr_max="C2",
        weight_map={"grammar": 0.10, "vocabulary": 0.15, "fluency": 0.50, "expression": 0.25},
        rubric=("fluency", "task_completion"),
    ),
    ArchetypeSpec(
        archetype_id="SPEAK_STORYBOARD",
        name="Storyboard Narration",
        core_activity="speak",
        description="Narrate a sequence of scenes.",
        ui_widget="Storyboard",
        themes_supported=("communication",),
        cefr_min="A2", cefr_max="C2",
        weight_map={"grammar": 0.20, "vocabulary": 0.20, "fluency": 0.25, "expression": 0.35},
        rubric=("coherence", "vocabulary", "fluency"),
    ),
    ArchetypeSpec(
        archetype_id="SPEAK_INTERVIEW",
        name="Interview Response",
        core_activity="speak",
        description="Answer an interview-style question.",
        ui_widget="SpeakAndRecord",
        themes_supported=("communication", "confidence"),
        cefr_min="B1", cefr_max="C2",
        weight_map={"grammar": 0.15, "vocabulary": 0.20, "fluency": 0.30, "expression": 0.25, "tone": 0.10},
        rubric=("fluency", "task_completion", "coherence", "register"),
    ),
    ArchetypeSpec(
        archetype_id="SPEAK_ROLEPLAY",
        name="Roleplay",
        core_activity="speak",
        description="Multi-turn scenario chat with an AI partner.",
        ui_widget="SpeakAndRecord",
        themes_supported=("communication", "confidence"),
        cefr_min="A2", cefr_max="C2",
        weight_map={"grammar": 0.15, "vocabulary": 0.20, "pronunciation": 0.10, "fluency": 0.25, "tone": 0.30},
        rubric=("fluency", "register", "vocabulary"),
    ),
    ArchetypeSpec(
        archetype_id="SPEAK_OPINION",
        name="Opinion Speaking",
        core_activity="speak",
        description="Defend a position spoken.",
        ui_widget="SpeakAndRecord",
        themes_supported=("communication", "confidence"),
        cefr_min="B1", cefr_max="C2",
        weight_map={"grammar": 0.15, "vocabulary": 0.20, "fluency": 0.30, "expression": 0.35},
        rubric=("coherence", "fluency", "task_completion"),
    ),
    ArchetypeSpec(
        archetype_id="SPEAK_SMALLTALK",
        name="Small Talk Simulation",
        core_activity="speak",
        description="Casual back-and-forth with a partner persona.",
        ui_widget="SpeakAndRecord",
        themes_supported=("confidence", "communication"),
        cefr_min="A2", cefr_max="C2",
        weight_map={"grammar": 0.15, "vocabulary": 0.20, "fluency": 0.30, "tone": 0.35},
        rubric=("fluency", "register", "task_completion"),
    ),
    ArchetypeSpec(
        archetype_id="SPEAK_DEBATE",
        name="Debate Response",
        core_activity="speak",
        description="Argue + rebut a stance.",
        ui_widget="SpeakAndRecord",
        themes_supported=("confidence", "communication"),
        cefr_min="B2", cefr_max="C2",
        weight_map={"grammar": 0.15, "vocabulary": 0.20, "fluency": 0.25, "expression": 0.30, "tone": 0.10},
        rubric=("coherence", "fluency", "register"),
    ),
    ArchetypeSpec(
        archetype_id="SPEAK_PRON_DRILL",
        name="Pronunciation Drill",
        core_activity="speak",
        description="Repeat target sounds / words for pronunciation training.",
        ui_widget="SpeakAndRecord",
        themes_supported=("confidence",),
        cefr_min="A1", cefr_max="C2",
        weight_map={"pronunciation": 0.85, "fluency": 0.15},
        rubric=("pronunciation",),
    ),
    ArchetypeSpec(
        archetype_id="SPEAK_PRESENT",
        name="Presentation Practice",
        core_activity="speak",
        description="Deliver a structured mini-presentation.",
        ui_widget="SpeakAndRecord",
        themes_supported=("confidence", "communication"),
        cefr_min="B1", cefr_max="C2",
        weight_map={"vocabulary": 0.20, "pronunciation": 0.15, "fluency": 0.30, "expression": 0.25, "tone": 0.10},
        rubric=("fluency", "coherence", "register"),
    ),
)


# ── Registry assembly ──────────────────────────────────────────────

# Future archetype (doc §9 LISTEN_REG_MIS — Listen for Register Mismatch) is
# intentionally absent from the registry until its UI / evaluator are built.

_ALL: tuple[ArchetypeSpec, ...] = _READING + _WRITING + _LISTENING + _SPEAKING

# Detect accidental duplicate IDs at import time.
_seen_ids: set[str] = set()
for _spec in _ALL:
    if _spec.archetype_id in _seen_ids:
        raise ValueError(f"duplicate archetype_id: {_spec.archetype_id!r}")
    _seen_ids.add(_spec.archetype_id)


ARCHETYPE_REGISTRY: dict[str, ArchetypeSpec] = {
    spec.archetype_id: spec for spec in _ALL
}


def get_archetype(archetype_id: str) -> ArchetypeSpec:
    """Return the spec for `archetype_id`. Raises KeyError if unknown."""
    try:
        return ARCHETYPE_REGISTRY[archetype_id]
    except KeyError:
        raise KeyError(f"unknown archetype_id: {archetype_id!r}") from None


def list_mvp_archetypes() -> tuple[ArchetypeSpec, ...]:
    """Return the subset of archetypes flagged mvp=True. Used by Phase 2 seed."""
    return tuple(spec for spec in _ALL if spec.mvp)
