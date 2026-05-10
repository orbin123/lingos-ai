"""
Full Tasks Templates — Curriculum-Driven, Widget-First Architecture.

═══════════════════════════════════════════════════════════════════════
WHY THIS FILE EXISTS
═══════════════════════════════════════════════════════════════════════

The original 7 sub-skill template files (grammar_templates.py, etc.) define
~56 task formats. Each format is tightly coupled to a single sub-skill
(e.g. "voice_conversion" only fits grammar). But the LingosAI curriculum
(beginner-24w.json, beginner-48w.json) assigns ONE specific topic per day
that may not fit any of those 56 formats.

Example: Week 1 Day 1 = "Present Simple Tense — Basics" (grammar). The
old `voice_conversion` template can't be used here — Present Simple isn't
about voice. We need a template that adapts to ANY grammar topic.

This file solves that with a 7 × 4 grid: one template per
(sub_skill, activity) pair = 28 templates. Each template is curriculum-
aware: it takes `topic_name` + `topic_id` from the daily plan and
generates content that fits THAT topic, not a fixed format.

═══════════════════════════════════════════════════════════════════════
THE 8 UI WIDGETS (the stable rendering layer)
═══════════════════════════════════════════════════════════════════════

Widget                  │ Input              │ Output                  │ AI Tools
────────────────────────┼────────────────────┼─────────────────────────┼─────────────────────────
1. mcq                  │ text prompt        │ 4-option button choice  │ LLM
2. fill_in_blanks       │ passage with gaps  │ typed blank answers     │ LLM
3. open_text            │ prompt             │ typed answer(s)         │ LLM (gen + eval)
4. timed_text           │ prompt + timer     │ typed answer            │ LLM (gen + eval)
5. structured_essay     │ multi-section      │ multi-section answer    │ LLM (gen + eval)
6. speak_and_record     │ text/audio prompt  │ mic recording           │ LLM + STT (+ Azure opt)
7. listen_and_respond   │ TTS audio          │ any inner output type   │ TTS + LLM (+ STT)
8. storyboard           │ generated images   │ voice narration         │ ImageGen + STT + LLM

Each of the 28 templates below picks ONE widget. The widget is fixed.
What changes is the LLM prompt that produces topic-appropriate content.

═══════════════════════════════════════════════════════════════════════
THE 28 TEMPLATES (7 sub-skills × 4 activities)
═══════════════════════════════════════════════════════════════════════

#   Sub-Skill               Activity   Widget                Template ID
──  ──────────────────────  ─────────  ────────────────────  ────────────────────────────────
01  Grammar                 Read       fill_in_blanks        full_grammar_read_v1
02  Grammar                 Write      open_text             full_grammar_write_v1
03  Grammar                 Listen     listen_and_respond    full_grammar_listen_v1
04  Grammar                 Speak      speak_and_record      full_grammar_speak_v1

05  Vocabulary              Read       mcq                   full_vocabulary_read_v1
06  Vocabulary              Write      open_text             full_vocabulary_write_v1
07  Vocabulary              Listen     listen_and_respond    full_vocabulary_listen_v1
08  Vocabulary              Speak      speak_and_record      full_vocabulary_speak_v1

09  Pronunciation           Read       speak_and_record      full_pronunciation_read_v1
10  Pronunciation           Write      mcq                   full_pronunciation_write_v1
11  Pronunciation           Listen     listen_and_respond    full_pronunciation_listen_v1
12  Pronunciation           Speak      speak_and_record      full_pronunciation_speak_v1

13  Fluency                 Read       speak_and_record      full_fluency_read_v1
14  Fluency                 Write      timed_text            full_fluency_write_v1
15  Fluency                 Listen     listen_and_respond    full_fluency_listen_v1
16  Fluency                 Speak      speak_and_record      full_fluency_speak_v1

17  Thought Organization    Read       open_text             full_expression_read_v1
18  Thought Organization    Write      structured_essay      full_expression_write_v1
19  Thought Organization    Listen     listen_and_respond    full_expression_listen_v1
20  Thought Organization    Speak      storyboard            full_expression_speak_v1

21  Listening/Comprehension Read       mcq                   full_comprehension_read_v1
22  Listening/Comprehension Write      open_text             full_comprehension_write_v1
23  Listening/Comprehension Listen     listen_and_respond    full_comprehension_listen_v1
24  Listening/Comprehension Speak      speak_and_record      full_comprehension_speak_v1

25  Tone & Social Awareness Read       mcq                   full_tone_read_v1
26  Tone & Social Awareness Write      open_text             full_tone_write_v1
27  Tone & Social Awareness Listen     listen_and_respond    full_tone_listen_v1
28  Tone & Social Awareness Speak      speak_and_record      full_tone_speak_v1

═══════════════════════════════════════════════════════════════════════
HOW THE GENERATOR USES THESE TEMPLATES
═══════════════════════════════════════════════════════════════════════

For a given user-day:
  1. Read curriculum entry: { week, day, topic_id, topic_name, sub_skill, sub_level }
  2. Pick the activity (rotate read → write → listen → speak per topic, or via
     user weakness profile)
  3. Look up template: get_full_template(sub_skill, activity)
  4. Fill prompt placeholders:
       {topic_name}, {topic_id}, {week}, {day}, {sub_skill}, {sub_level},
       {tier}, {plan_type}
  5. Send to LLM → validate response against the template's output_model
  6. Frontend renders using the widget name in the response

═══════════════════════════════════════════════════════════════════════
"""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from app.tasks.schemas.base import (
    Activity,
    GeneratedTaskBase,
    ScoringMethod,
    SubSkill,
    TaskTemplate,
)


# ═════════════════════════════════════════════════════════════════════
# WIDGET ENUM — the 8 UI widgets the frontend supports
# ═════════════════════════════════════════════════════════════════════


class UIWidget(str, Enum):
    """The 8 generic UI widgets. Every generated task names one of these."""

    MCQ = "mcq"
    FILL_IN_BLANKS = "fill_in_blanks"
    OPEN_TEXT = "open_text"
    TIMED_TEXT = "timed_text"
    STRUCTURED_ESSAY = "structured_essay"
    SPEAK_AND_RECORD = "speak_and_record"
    LISTEN_AND_RESPOND = "listen_and_respond"
    STORYBOARD = "storyboard"


# Inner widget for listen_and_respond (what comes AFTER the audio plays)
ListenInnerWidget = Literal["mcq", "fill_in_blanks", "open_text", "speak_and_record"]


# ═════════════════════════════════════════════════════════════════════
# SHARED ITEM MODELS — reused across multiple templates
# ═════════════════════════════════════════════════════════════════════


class MCQItem(BaseModel):
    """One question with 4 options. Used by every MCQ-based template."""

    item_id: str
    prompt: str = Field(..., description="The question or sentence with a blank")
    options: list[str] = Field(..., min_length=4, max_length=4)
    correct_index: int = Field(..., ge=0, le=3)
    explanation: str = Field(
        ..., description="Why the correct answer is right (shown after submit)"
    )


class BlankItem(BaseModel):
    """A sentence with one blank to fill. Used by fill_in_blanks widget."""

    item_id: str
    sentence_with_blank: str = Field(..., description="Use ___ to mark the blank")
    base_verb: str | None = Field(
        None,
        description="Base (infinitive) form of the target verb shown as a hint, e.g. 'go'",
    )
    correct_answer: str
    explanation: str


class OpenTextItem(BaseModel):
    """A prompt the learner answers in free-form text."""

    item_id: str
    prompt: str
    sample_answer: str = Field(..., description="Reference answer for the evaluator")
    answer_hints: list[str] = Field(
        default_factory=list,
        description="Hints shown only AFTER submission, never during",
    )


# ═════════════════════════════════════════════════════════════════════
# LAYER 2 — PYDANTIC OUTPUT MODELS (one per template)
#
# Every model carries: widget name, topic context, scoring method
# context, and the actual rendered content for the widget.
# ═════════════════════════════════════════════════════════════════════


# ─── Common base for every full-template output ──────────────────────


class FullTaskBase(GeneratedTaskBase):
    """
    Every generated task carries curriculum + widget metadata so the
    frontend can render it without parsing content.
    """

    widget: UIWidget = Field(..., description="Which of the 8 widgets to render")
    topic_id: str = Field(..., description="e.g. '1:1' — matches curriculum JSON")
    topic_name: str = Field(..., description="e.g. 'Present Simple Tense — Basics'")
    sub_skill: SubSkill
    sub_level: int = Field(..., ge=1, le=10)
    activity: Activity


# ─── #01 Grammar / Read → fill_in_blanks ─────────────────────────────


class GrammarReadTask(FullTaskBase):
    instructions: str
    passage: str = Field(
        ...,
        min_length=40,
        description=(
            "Required 5–6 sentence reading passage containing the same ___ "
            "blank sentences listed in items"
        ),
    )
    items: list[BlankItem] = Field(..., min_length=4, max_length=8)
    grammar_rule_explained: str = Field(
        ..., description="Plain-language explanation of the rule under test"
    )


# ─── #02 Grammar / Write → open_text ─────────────────────────────────


class GrammarWriteTask(FullTaskBase):
    instructions: str
    items: list[OpenTextItem] = Field(..., min_length=3, max_length=6)
    grammar_rule_explained: str
    common_mistakes: list[str] = Field(
        ..., min_length=2,
        description="Typical learner errors for this rule, used by the evaluator",
    )


# ─── #03 Grammar / Listen → listen_and_respond ───────────────────────


class GrammarListenTask(FullTaskBase):
    instructions: str
    audio_script: str = Field(
        ..., min_length=40, max_length=400,
        description="Text the TTS engine will speak (uses the target grammar rule)",
    )
    audio_url: str | None = Field(None, description="Filled by TTS service later")
    inner_widget: ListenInnerWidget = "mcq"
    items: list[MCQItem] = Field(..., min_length=3, max_length=6)


# ─── #04 Grammar / Speak → speak_and_record ──────────────────────────


class GrammarSpeakTask(FullTaskBase):
    instructions: str
    speaking_prompts: list[str] = Field(
        ..., min_length=2, max_length=5,
        description="Each prompt requires the user to USE the target grammar rule",
    )
    sample_responses: list[str] = Field(
        ..., min_length=2,
        description="Reference answers (one per prompt) for evaluation",
    )
    grammar_rule_to_practice: str
    speaking_duration_seconds: int = Field(default=60, ge=20, le=180)


# ─── #05 Vocabulary / Read → mcq ─────────────────────────────────────


class VocabularyReadTask(FullTaskBase):
    instructions: str
    target_words: list[str] = Field(..., min_length=4, max_length=10)
    items: list[MCQItem] = Field(
        ..., min_length=4, max_length=10,
        description="Mix: word→meaning match AND context-fit MCQs",
    )


# ─── #06 Vocabulary / Write → open_text ──────────────────────────────


class VocabularyWriteTask(FullTaskBase):
    instructions: str
    target_words: list[str] = Field(..., min_length=4, max_length=8)
    items: list[OpenTextItem] = Field(
        ..., min_length=3, max_length=6,
        description="Each prompt asks the learner to USE one or more target words",
    )
    minimum_target_words_used: int = Field(
        default=3, description="Evaluator checks how many target words appear"
    )


# ─── #07 Vocabulary / Listen → listen_and_respond ────────────────────


class VocabularyListenTask(FullTaskBase):
    instructions: str
    audio_script: str = Field(..., min_length=60, max_length=400)
    audio_url: str | None = None
    target_words_in_audio: list[str] = Field(..., min_length=3, max_length=8)
    inner_widget: ListenInnerWidget = "mcq"
    items: list[MCQItem] = Field(..., min_length=3, max_length=6)


# ─── #08 Vocabulary / Speak → speak_and_record ───────────────────────


class VocabularySpeakTask(FullTaskBase):
    instructions: str
    target_words: list[str] = Field(..., min_length=3, max_length=6)
    speaking_prompt: str = Field(
        ..., description="Topic the user explains while using all target words"
    )
    sample_response: str
    minimum_words_used: int = Field(
        default=3, description="Required count of target words in the response"
    )
    speaking_duration_seconds: int = Field(default=60, ge=30, le=180)


# ─── #09 Pronunciation / Read → speak_and_record ─────────────────────


class PronunciationReadTask(FullTaskBase):
    instructions: str
    text_to_read_aloud: str = Field(..., min_length=30, max_length=200)
    target_sounds_or_patterns: list[str] = Field(
        ..., min_length=1,
        description="Specific phonemes / stress patterns under test",
    )
    expected_difficult_words: list[str] = Field(default_factory=list)
    use_azure_scoring: bool = Field(
        default=True,
        description="If false, fall back to Whisper-based intelligibility",
    )


# ─── #10 Pronunciation / Write → mcq ─────────────────────────────────


class PronunciationWriteTask(FullTaskBase):
    """
    Pronunciation 'write' = phonetic awareness (no real essay-writing).
    Items are MCQ-style: pick the correct phonetic transcription, identify
    the stressed syllable, etc.
    """

    instructions: str
    items: list[MCQItem] = Field(..., min_length=4, max_length=8)
    pattern_explained: str = Field(
        ..., description="Explanation of the phonetic pattern under test"
    )


# ─── #11 Pronunciation / Listen → listen_and_respond ─────────────────


class PronunciationListenTask(FullTaskBase):
    instructions: str
    audio_script: str = Field(..., min_length=20, max_length=200)
    audio_url: str | None = None
    target_pattern: str = Field(
        ..., description="e.g. 'short /ɪ/ vs long /iː/' or 'stress on 2nd syllable'"
    )
    inner_widget: ListenInnerWidget = "mcq"
    items: list[MCQItem] = Field(..., min_length=3, max_length=6)


# ─── #12 Pronunciation / Speak → speak_and_record ────────────────────


class PronunciationSpeakTask(FullTaskBase):
    instructions: str
    speaking_items: list[str] = Field(
        ..., min_length=3, max_length=8,
        description="Words/phrases/sentences targeting the topic's sound or pattern",
    )
    target_pattern: str
    reference_audio_url: str | None = Field(
        None, description="ElevenLabs reference audio, filled later"
    )
    use_azure_scoring: bool = True


# ─── #13 Fluency / Read → speak_and_record (timed read-aloud) ────────


class FluencyReadTask(FullTaskBase):
    instructions: str
    passage: str = Field(..., min_length=80, max_length=500)
    word_count: int
    target_wpm: int = Field(..., ge=70, le=180)
    time_limit_seconds: int


# ─── #14 Fluency / Write → timed_text ────────────────────────────────


class FluencyWriteTask(FullTaskBase):
    instructions: str
    writing_prompt: str
    time_limit_seconds: int = Field(default=300, ge=60, le=900)
    minimum_word_count: int
    target_word_count: int
    no_editing_allowed: bool = True
    sample_response: str


# ─── #15 Fluency / Listen → listen_and_respond (shadowing) ───────────


class FluencyListenTask(FullTaskBase):
    instructions: str
    text_to_shadow: str = Field(..., min_length=40, max_length=300)
    audio_url: str | None = None
    speed: Literal["slow", "natural", "fast"]
    delay_seconds: float = Field(default=0.8, ge=0, le=3)
    inner_widget: ListenInnerWidget = "speak_and_record"
    minimum_match_percentage: float = Field(default=0.7, ge=0, le=1)


# ─── #16 Fluency / Speak → speak_and_record (free-flow) ──────────────


class FluencySpeakTask(FullTaskBase):
    instructions: str
    speaking_prompt: str
    preparation_seconds: int = Field(default=10, ge=0, le=60)
    speaking_duration_seconds: int = Field(default=60, ge=30, le=180)
    fluency_focus: str = Field(
        ..., description="What the topic targets, e.g. 'self-correction', 'small talk'"
    )
    sample_talking_points: list[str] = Field(..., min_length=2, max_length=5)


# ─── #17 Expression (Thought Org) / Read → open_text ─────────────────


class ExpressionReadTask(FullTaskBase):
    instructions: str
    passage: str = Field(..., min_length=120, max_length=500)
    items: list[OpenTextItem] = Field(
        ..., min_length=2, max_length=4,
        description="Tasks like: summarize main idea, identify structure, paraphrase",
    )
    structure_pattern_taught: str = Field(
        ..., description="The organizational pattern this passage demonstrates"
    )


# ─── #18 Expression / Write → structured_essay ───────────────────────


class EssaySection(BaseModel):
    section_id: str
    section_name: Literal[
        "introduction", "background", "main_point",
        "supporting_detail", "counter_point", "conclusion",
    ]
    section_prompt: str = Field(..., description="What the user should write here")
    minimum_word_count: int
    sample_text: str


class ExpressionWriteTask(FullTaskBase):
    instructions: str
    overall_topic: str
    sections: list[EssaySection] = Field(..., min_length=3, max_length=5)
    structure_pattern: str = Field(
        ..., description="e.g. 'intro-body-conclusion', 'problem-solution', 'pros-cons'"
    )
    total_target_words: int


# ─── #19 Expression / Listen → listen_and_respond ────────────────────


class ExpressionListenTask(FullTaskBase):
    instructions: str
    audio_script: str = Field(..., min_length=120, max_length=600)
    audio_url: str | None = None
    structure_to_identify: str
    inner_widget: ListenInnerWidget = "open_text"
    items: list[OpenTextItem] = Field(..., min_length=2, max_length=4)


# ─── #20 Expression / Speak → storyboard ─────────────────────────────


class StoryboardScene(BaseModel):
    scene_id: str
    scene_number: int = Field(..., ge=1, le=8)
    image_prompt: str = Field(
        ..., description="Prompt sent to ImageGen to create this scene"
    )
    image_url: str | None = None
    narration_focus: str = Field(
        ..., description="What the learner should describe in this scene"
    )


class ExpressionSpeakTask(FullTaskBase):
    instructions: str
    overall_story_premise: str
    scenes: list[StoryboardScene] = Field(..., min_length=3, max_length=6)
    narrative_pattern: str = Field(
        ..., description="e.g. 'beginning-middle-end', 'cause-effect-resolution'"
    )
    speaking_duration_seconds: int = Field(default=120, ge=60, le=300)
    sample_narration: str


# ─── #21 Comprehension / Read → mcq ──────────────────────────────────


class ComprehensionReadTask(FullTaskBase):
    instructions: str
    passage: str = Field(..., min_length=150, max_length=600)
    items: list[MCQItem] = Field(..., min_length=4, max_length=8)
    question_types_used: list[str] = Field(
        ...,
        description="e.g. ['main_idea', 'specific_detail', 'inference', 'vocabulary_in_context']",
    )


# ─── #22 Comprehension / Write → open_text ───────────────────────────


class ComprehensionWriteTask(FullTaskBase):
    instructions: str
    source_audio_script: str | None = Field(
        None, description="If listen-then-write task, the audio text"
    )
    source_audio_url: str | None = None
    source_passage: str | None = Field(
        None, description="If read-then-write task, the passage"
    )
    items: list[OpenTextItem] = Field(..., min_length=3, max_length=6)


# ─── #23 Comprehension / Listen → listen_and_respond ─────────────────


class ComprehensionListenTask(FullTaskBase):
    instructions: str
    audio_script: str = Field(..., min_length=120, max_length=600)
    audio_url: str | None = None
    audio_genre: Literal[
        "conversation", "interview", "lecture", "news", "podcast", "announcement",
    ]
    inner_widget: ListenInnerWidget = "mcq"
    items: list[MCQItem] = Field(..., min_length=4, max_length=8)


# ─── #24 Comprehension / Speak → speak_and_record (retell) ───────────


class ComprehensionSpeakTask(FullTaskBase):
    instructions: str
    source_audio_script: str = Field(..., min_length=80, max_length=400)
    source_audio_url: str | None = None
    retelling_prompt: str = Field(
        ...,
        description="What the learner should retell or answer based on the audio",
    )
    key_points_expected: list[str] = Field(
        ..., min_length=3, max_length=8,
        description="Points the learner's retelling should cover",
    )
    speaking_duration_seconds: int = Field(default=60, ge=30, le=180)


# ─── #25 Tone / Read → mcq ───────────────────────────────────────────


class ToneReadTask(FullTaskBase):
    instructions: str
    items: list[MCQItem] = Field(
        ..., min_length=4, max_length=8,
        description="Each item shows a message; user picks tone/register/audience",
    )
    tone_concepts_taught: list[str] = Field(
        ..., min_length=1,
        description="e.g. ['formal', 'casual', 'neutral', 'assertive']",
    )


# ─── #26 Tone / Write → open_text (rewrite/register conversion) ──────


class ToneWriteTask(FullTaskBase):
    instructions: str
    items: list[OpenTextItem] = Field(
        ..., min_length=3, max_length=6,
        description="Each prompt: rewrite a message in a different tone/register",
    )
    target_register: Literal["formal", "casual", "neutral", "professional", "friendly"]
    common_pitfalls: list[str] = Field(
        ..., min_length=2,
        description="Typical errors when converting register",
    )


# ─── #27 Tone / Listen → listen_and_respond ──────────────────────────


class ToneListenTask(FullTaskBase):
    instructions: str
    audio_script: str = Field(..., min_length=60, max_length=400)
    audio_url: str | None = None
    voice_style_hint: str = Field(
        ...,
        description="Tone the TTS should convey, e.g. 'sarcastic', 'warm', 'firm'",
    )
    inner_widget: ListenInnerWidget = "mcq"
    items: list[MCQItem] = Field(..., min_length=3, max_length=6)


# ─── #28 Tone / Speak → speak_and_record (roleplay) ──────────────────


class RoleplayTurn(BaseModel):
    turn_id: str
    speaker: Literal["ai", "user"]
    ai_line: str | None = None
    expected_user_tone: str | None = Field(
        None, description="Tone the user should adopt for their reply"
    )


class ToneSpeakTask(FullTaskBase):
    instructions: str
    scenario_description: str
    target_tone: str = Field(
        ..., description="The tone the user should consistently use"
    )
    turns: list[RoleplayTurn] = Field(..., min_length=3, max_length=8)
    sample_user_responses: list[str] = Field(..., min_length=2)
    speaking_duration_seconds: int = Field(default=120, ge=60, le=300)


# ═════════════════════════════════════════════════════════════════════
# LAYER 1 — TEMPLATE DEFINITIONS (28 templates)
#
# Every prompt receives the SAME curriculum placeholder set:
#   {topic_name}    e.g. "Present Simple Tense — Basics"
#   {topic_id}      e.g. "1:1"
#   {week}          e.g. 1
#   {day}           e.g. 1
#   {sub_skill}     e.g. "grammar"
#   {sub_level}     1..10
#   {tier}          "beginner" | "intermediate" | "advanced"
#   {plan_type}     "24w" | "48w"
#   {domain}        e.g. "general", "tech", "business"  (from user profile)
# ═════════════════════════════════════════════════════════════════════


# ─── Reusable prompt header injected into every template ─────────────


_CURRICULUM_HEADER = """
CURRICULUM CONTEXT (THE TOPIC IS NON-NEGOTIABLE)
- Plan: {plan_type}
- Week: {week}, Day: {day}
- Topic ID: {topic_id}
- Topic name: "{topic_name}"
- Sub-skill: {sub_skill}
- Sub-level: {sub_level} (tier: {tier})
- Learner domain: {domain}

YOU MUST CENTER EVERY ITEM ON "{topic_name}".
Do NOT drift to a generic {sub_skill} task. The topic is the spine.
""".strip()


# Difficulty modifiers used by ALL templates (per tier)
_TIER_DEFAULTS = {
    "beginner": {
        "item_count": 4,
        "passage_word_count": 80,
        "target_wpm": 90,
        "time_limit": 180,
        "min_words": 60,
        "target_words": 100,
        "speaking_duration": 45,
        "audio_word_count": 60,
    },
    "intermediate": {
        "item_count": 5,
        "passage_word_count": 180,
        "target_wpm": 120,
        "time_limit": 300,
        "min_words": 120,
        "target_words": 200,
        "speaking_duration": 75,
        "audio_word_count": 150,
    },
    "advanced": {
        "item_count": 6,
        "passage_word_count": 280,
        "target_wpm": 150,
        "time_limit": 480,
        "min_words": 200,
        "target_words": 350,
        "speaking_duration": 120,
        "audio_word_count": 280,
    },
}

_GRAMMAR_READ_DEFAULTS = {
    **_TIER_DEFAULTS,
    "beginner": {
        **_TIER_DEFAULTS["beginner"],
        "item_count": 5,
        "passage_word_count": 95,
    },
    "intermediate": {
        **_TIER_DEFAULTS["intermediate"],
        "item_count": 5,
        "passage_word_count": 150,
    },
    "advanced": {
        **_TIER_DEFAULTS["advanced"],
        "item_count": 6,
        "passage_word_count": 220,
    },
}


# ─── #01 Grammar / Read ───────────────────────────────────────────────

FULL_GRAMMAR_READ_V1 = TaskTemplate(
    template_id="full_grammar_read_v1",
    sub_skill=SubSkill.GRAMMAR,
    activity=Activity.READ,
    task_type="curriculum_grammar_fill_blanks",
    difficulty_range=(1, 10),
    estimated_time_minutes=4,
    scoring_method=ScoringMethod.RULE_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: fill_in_blanks
TASK
1. Write ONE coherent reading passage of 5–6 sentences and about
   {passage_word_count} words. The passage is the task, not decoration.
2. Put exactly {item_count} blanks directly INSIDE the passage using "___".
   Each blank must test "{topic_name}" specifically.
3. The passage must use "{topic_name}" naturally from beginning to end.
   Do not add a separate teaching paragraph, rule card, or unrelated
   example paragraph.
4. Generate {item_count} BlankItem objects from that same passage.
   - Each `sentence_with_blank` MUST be copied exactly from one sentence in
     the passage, including the same "___" blank.
   - Do not create any blank item that is not directly present in the passage.
   - Provide ONE correct_answer (lowercase if a verb form, otherwise as written).
   - Set `base_verb` to the base (infinitive) form of the target word shown
     as a learner hint, e.g. "go" when the answer is "goes". Always include it.
   - Do NOT provide distractors, options, choices, or multiple-choice answers.
   - Include a 1-sentence explanation per item.
5. Set `instructions` to tell the learner to read the paragraph and type the
   numbered answers into the blanks.
6. Set `grammar_rule_explained` to a short rule summary for feedback only.
   It must not be a second passage.
7. Sentences must use vocabulary at sub-level {sub_level}.

Output JSON matching GrammarReadTask. Set:
  widget="fill_in_blanks", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="read".
""",
    output_model_name="GrammarReadTask",
    evaluation_logic={
        "method": "exact_match_per_blank",
        "scoring": "passed_blanks / total_blanks",
        "passing_threshold": 0.7,
        "metrics_returned": ["accuracy", "per_item_correctness"],
    },
    difficulty_modifiers=_GRAMMAR_READ_DEFAULTS,
)


# ─── #02 Grammar / Write ──────────────────────────────────────────────

FULL_GRAMMAR_WRITE_V1 = TaskTemplate(
    template_id="full_grammar_write_v1",
    sub_skill=SubSkill.GRAMMAR,
    activity=Activity.WRITE,
    task_type="curriculum_grammar_open_text",
    difficulty_range=(1, 10),
    estimated_time_minutes=8,
    scoring_method=ScoringMethod.AI_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: open_text
TASK
1. Explain the grammar rule from "{topic_name}" in plain language.
2. Generate {item_count} OpenTextItem prompts. Each prompt MUST require the
   learner to PRODUCE sentences using "{topic_name}". Examples by topic type:
   - If topic is a tense: "Write 3 sentences about your weekend using {topic_name}."
   - If topic is articles: "Rewrite this paragraph, fixing every article error."
   - If topic is conditionals: "Finish each conditional sentence."
3. For each item, provide a sample_answer that demonstrates correct usage.
4. List 2–4 common_mistakes the evaluator should watch for.

Output JSON matching GrammarWriteTask. Set:
  widget="open_text", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="write".
""",
    output_model_name="GrammarWriteTask",
    evaluation_logic={
        "method": "ai_evaluator",
        "weights": {
            "rule_correctly_applied": 0.5,
            "sentence_correctness": 0.3,
            "task_completion": 0.2,
        },
        "passing_threshold": 0.65,
        "metrics_returned": ["rule_accuracy", "errors_found", "feedback_per_item"],
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #03 Grammar / Listen ─────────────────────────────────────────────

FULL_GRAMMAR_LISTEN_V1 = TaskTemplate(
    template_id="full_grammar_listen_v1",
    sub_skill=SubSkill.GRAMMAR,
    activity=Activity.LISTEN,
    task_type="curriculum_grammar_listen_mcq",
    difficulty_range=(1, 10),
    estimated_time_minutes=5,
    scoring_method=ScoringMethod.RULE_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: listen_and_respond  (inner: mcq)
TASK
1. Write an audio_script ({audio_word_count} words) that uses "{topic_name}"
   naturally. The script should be conversational and clear.
2. Generate {item_count} MCQ items where each question tests whether the
   learner heard the grammar rule correctly.
   Examples:
   - "Did the speaker use past simple or present perfect?"
   - "Which sentence in the audio had a grammar error?"
   - "How did the speaker form the question?"
3. Each MCQ has 4 options with one correct answer + explanation.
4. Set audio_url to null (TTS service fills it later).

Output JSON matching GrammarListenTask. Set:
  widget="listen_and_respond", inner_widget="mcq",
  topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="listen".
""",
    output_model_name="GrammarListenTask",
    evaluation_logic={
        "method": "exact_match_per_mcq",
        "scoring": "correct_count / total_count",
        "passing_threshold": 0.7,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #04 Grammar / Speak ──────────────────────────────────────────────

FULL_GRAMMAR_SPEAK_V1 = TaskTemplate(
    template_id="full_grammar_speak_v1",
    sub_skill=SubSkill.GRAMMAR,
    activity=Activity.SPEAK,
    task_type="curriculum_grammar_speak",
    difficulty_range=(1, 10),
    estimated_time_minutes=6,
    scoring_method=ScoringMethod.HYBRID,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: speak_and_record
TASK
1. Generate 3 speaking_prompts that FORCE the learner to use "{topic_name}".
   Examples:
   - Past Simple: "Tell me what you did yesterday."
   - Conditionals: "What would you do if you won a million dollars?"
   - Reported speech: "Tell me what your friend said this morning."
2. Provide a sample_response per prompt (3–5 sentences each) showing correct
   usage of the rule.
3. Set grammar_rule_to_practice to a short label (e.g. "past simple regular verbs").
4. Set speaking_duration_seconds to {speaking_duration}.

Output JSON matching GrammarSpeakTask. Set:
  widget="speak_and_record", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="speak".
""",
    output_model_name="GrammarSpeakTask",
    evaluation_logic={
        "method": "stt + ai_grammar_check",
        "weights": {
            "rule_used_correctly": 0.5,
            "fluency_smoothness": 0.2,
            "task_completion": 0.2,
            "intelligibility": 0.1,
        },
        "passing_threshold": 0.6,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #05 Vocabulary / Read ────────────────────────────────────────────

FULL_VOCABULARY_READ_V1 = TaskTemplate(
    template_id="full_vocabulary_read_v1",
    sub_skill=SubSkill.VOCABULARY,
    activity=Activity.READ,
    task_type="curriculum_vocab_mcq",
    difficulty_range=(1, 10),
    estimated_time_minutes=4,
    scoring_method=ScoringMethod.RULE_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: mcq
TASK
1. Pick {item_count} target_words that fit the theme of "{topic_name}".
   E.g. if the topic is "Family Words — Members and Relations", pick words
   like "uncle, niece, cousin, in-law, sibling".
2. Generate {item_count} MCQ items mixing TWO question types:
   - word→meaning: "What does X mean?"
   - context-fit:  "Pick the word that best fits the sentence: ___"
3. Each MCQ has 4 options + correct_index + 1-sentence explanation.
4. All items must use vocabulary appropriate to sub-level {sub_level}.

Output JSON matching VocabularyReadTask. Set:
  widget="mcq", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="read".
""",
    output_model_name="VocabularyReadTask",
    evaluation_logic={
        "method": "exact_match_per_mcq",
        "passing_threshold": 0.7,
        "scoring": "correct_count / total_count",
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #06 Vocabulary / Write ───────────────────────────────────────────

FULL_VOCABULARY_WRITE_V1 = TaskTemplate(
    template_id="full_vocabulary_write_v1",
    sub_skill=SubSkill.VOCABULARY,
    activity=Activity.WRITE,
    task_type="curriculum_vocab_open_text",
    difficulty_range=(1, 10),
    estimated_time_minutes=7,
    scoring_method=ScoringMethod.AI_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: open_text
TASK
1. Pick {item_count} target_words that match the theme of "{topic_name}".
2. Generate {item_count} OpenTextItem prompts. Each prompt requires the
   learner to USE one or more target_words. Examples:
   - "Write a paragraph using these 3 words: X, Y, Z."
   - "Replace 'big' in each sentence with a more advanced synonym."
   - "Paraphrase this sentence using the word 'consequently'."
3. Provide a sample_answer per prompt that demonstrates ideal word usage.
4. Set minimum_target_words_used to 3.

Output JSON matching VocabularyWriteTask. Set:
  widget="open_text", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="write".
""",
    output_model_name="VocabularyWriteTask",
    evaluation_logic={
        "method": "ai_evaluator",
        "weights": {
            "target_words_used": 0.4,
            "correct_word_usage": 0.4,
            "sentence_quality": 0.2,
        },
        "passing_threshold": 0.65,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #07 Vocabulary / Listen ──────────────────────────────────────────

FULL_VOCABULARY_LISTEN_V1 = TaskTemplate(
    template_id="full_vocabulary_listen_v1",
    sub_skill=SubSkill.VOCABULARY,
    activity=Activity.LISTEN,
    task_type="curriculum_vocab_listen_mcq",
    difficulty_range=(1, 10),
    estimated_time_minutes=5,
    scoring_method=ScoringMethod.RULE_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: listen_and_respond  (inner: mcq)
TASK
1. Pick 4–6 target_words_in_audio for the theme "{topic_name}".
2. Write an audio_script ({audio_word_count} words) that uses those words
   naturally in context.
3. Generate {item_count} MCQ items testing:
   - "What word did the speaker use to mean X?"
   - "Which target word did the speaker NOT use?"
   - "From context, what does word X mean?"
4. Set audio_url to null (TTS fills later).

Output JSON matching VocabularyListenTask. Set:
  widget="listen_and_respond", inner_widget="mcq",
  topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="listen".
""",
    output_model_name="VocabularyListenTask",
    evaluation_logic={
        "method": "exact_match_per_mcq",
        "passing_threshold": 0.7,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #08 Vocabulary / Speak ───────────────────────────────────────────

FULL_VOCABULARY_SPEAK_V1 = TaskTemplate(
    template_id="full_vocabulary_speak_v1",
    sub_skill=SubSkill.VOCABULARY,
    activity=Activity.SPEAK,
    task_type="curriculum_vocab_speak",
    difficulty_range=(1, 10),
    estimated_time_minutes=5,
    scoring_method=ScoringMethod.HYBRID,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: speak_and_record
TASK
1. Pick 3–5 target_words from "{topic_name}".
2. Write a speaking_prompt that asks the learner to talk for
   {speaking_duration} seconds while using ALL target_words.
   Example: "Describe your morning routine using these words: alarm,
   commute, breakfast, productive."
3. Provide a sample_response that uses every target word naturally.
4. Set minimum_words_used to 3.

Output JSON matching VocabularySpeakTask. Set:
  widget="speak_and_record", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="speak".
""",
    output_model_name="VocabularySpeakTask",
    evaluation_logic={
        "method": "stt + word_match + ai_evaluator",
        "weights": {
            "target_words_used": 0.4,
            "correct_usage": 0.3,
            "fluency": 0.2,
            "intelligibility": 0.1,
        },
        "passing_threshold": 0.6,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #09 Pronunciation / Read ─────────────────────────────────────────

FULL_PRONUNCIATION_READ_V1 = TaskTemplate(
    template_id="full_pronunciation_read_v1",
    sub_skill=SubSkill.PRONUNCIATION,
    activity=Activity.READ,
    task_type="curriculum_pron_read_aloud",
    difficulty_range=(1, 10),
    estimated_time_minutes=5,
    scoring_method=ScoringMethod.SPEECH_API,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: speak_and_record
TASK
1. Identify the target_sounds_or_patterns covered by "{topic_name}".
   Examples:
   - Topic "Short Vowels — /æ/ and /ɛ/" → ["/æ/", "/ɛ/"]
   - Topic "Word Stress — Two-Syllable Nouns" → ["initial-syllable stress"]
   - Topic "Linking Words — Consonant to Vowel" → ["consonant-to-vowel linking"]
2. Generate text_to_read_aloud (40–120 words) that's PACKED with the
   target sounds/patterns. Mark difficult words inside if helpful.
3. List 2–5 expected_difficult_words.
4. Set use_azure_scoring to true (fall back to Whisper if unavailable).

Output JSON matching PronunciationReadTask. Set:
  widget="speak_and_record", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="read".
""",
    output_model_name="PronunciationReadTask",
    evaluation_logic={
        "method": "azure_speech_pronunciation OR whisper_fallback",
        "metrics_returned": [
            "accuracy_score", "fluency_score",
            "completeness_score", "phoneme_level_errors",
        ],
        "weights": {
            "accuracy": 0.5,
            "fluency": 0.2,
            "completeness": 0.2,
            "intelligibility": 0.1,
        },
        "passing_threshold": 0.65,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #10 Pronunciation / Write ────────────────────────────────────────

FULL_PRONUNCIATION_WRITE_V1 = TaskTemplate(
    template_id="full_pronunciation_write_v1",
    sub_skill=SubSkill.PRONUNCIATION,
    activity=Activity.WRITE,
    task_type="curriculum_pron_phonetic_mcq",
    difficulty_range=(1, 10),
    estimated_time_minutes=4,
    scoring_method=ScoringMethod.RULE_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: mcq
NOTE: Pronunciation is hard to practice through writing alone, so this
template tests PHONETIC AWARENESS — picking the correct stress pattern,
phonetic transcription, or rhyming word.

TASK
1. Briefly explain the pattern from "{topic_name}" in pattern_explained.
2. Generate {item_count} MCQ items using a mix of these question types:
   - "Which word has the /æ/ sound?"
   - "Where is the stress in 'photograph'? (1) PHO-to-graph (2) pho-TO-graph ..."
   - "Which two words rhyme: ship/sheep/shape/shop?"
   - "Which transcription matches 'thought'? /θɔːt/, /tɔːt/, /θaʊt/ ..."
3. Each MCQ has 4 options + correct_index + explanation.

Output JSON matching PronunciationWriteTask. Set:
  widget="mcq", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="write".
""",
    output_model_name="PronunciationWriteTask",
    evaluation_logic={
        "method": "exact_match_per_mcq",
        "passing_threshold": 0.7,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #11 Pronunciation / Listen ───────────────────────────────────────

FULL_PRONUNCIATION_LISTEN_V1 = TaskTemplate(
    template_id="full_pronunciation_listen_v1",
    sub_skill=SubSkill.PRONUNCIATION,
    activity=Activity.LISTEN,
    task_type="curriculum_pron_listen_discriminate",
    difficulty_range=(1, 10),
    estimated_time_minutes=5,
    scoring_method=ScoringMethod.RULE_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: listen_and_respond  (inner: mcq)
TASK
1. Set target_pattern to a phrase describing what the audio demonstrates
   based on "{topic_name}" (e.g. "/ɪ/ vs /iː/ in minimal pairs").
2. Write an audio_script (30–80 words) that contains both correct and
   incorrect or contrasting examples of the pattern.
3. Generate {item_count} MCQ items testing pattern discrimination:
   - "Which word did the speaker mispronounce?"
   - "Which sound did you hear in word 3: /ɪ/ or /iː/?"
   - "Where did the speaker put the stress in 'present'?"
4. Set audio_url to null (TTS fills later).

Output JSON matching PronunciationListenTask. Set:
  widget="listen_and_respond", inner_widget="mcq",
  topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="listen".
""",
    output_model_name="PronunciationListenTask",
    evaluation_logic={
        "method": "exact_match_per_mcq",
        "passing_threshold": 0.7,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #12 Pronunciation / Speak ────────────────────────────────────────

FULL_PRONUNCIATION_SPEAK_V1 = TaskTemplate(
    template_id="full_pronunciation_speak_v1",
    sub_skill=SubSkill.PRONUNCIATION,
    activity=Activity.SPEAK,
    task_type="curriculum_pron_speak_drill",
    difficulty_range=(1, 10),
    estimated_time_minutes=5,
    scoring_method=ScoringMethod.SPEECH_API,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: speak_and_record
TASK
1. Generate 4–8 speaking_items targeting the pattern from "{topic_name}".
   Items can be:
   - Single words (for phoneme drills)
   - Minimal pairs (for sound discrimination)
   - Short sentences (for stress, intonation, linking)
2. Set target_pattern to a clear label (e.g. "long /iː/ sound").
3. Set reference_audio_url to null (ElevenLabs fills it).
4. Set use_azure_scoring to true.

Output JSON matching PronunciationSpeakTask. Set:
  widget="speak_and_record", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="speak".
""",
    output_model_name="PronunciationSpeakTask",
    evaluation_logic={
        "method": "azure_speech_pronunciation OR whisper_fallback",
        "metrics_returned": [
            "phoneme_accuracy", "stress_accuracy",
            "completeness", "per_item_scores",
        ],
        "weights": {
            "phoneme_accuracy": 0.6,
            "stress_pattern": 0.2,
            "intelligibility": 0.2,
        },
        "passing_threshold": 0.65,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #13 Fluency / Read ───────────────────────────────────────────────

FULL_FLUENCY_READ_V1 = TaskTemplate(
    template_id="full_fluency_read_v1",
    sub_skill=SubSkill.FLUENCY,
    activity=Activity.READ,
    task_type="curriculum_fluency_speed_read",
    difficulty_range=(2, 10),
    estimated_time_minutes=4,
    scoring_method=ScoringMethod.SPEECH_API,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: speak_and_record
TASK
1. Write a passage ({passage_word_count} words) about a topic relevant to
   "{topic_name}". The passage should be smooth and conversational —
   this is a SPEED test, not a pronunciation test.
2. Set word_count to the actual count.
3. Set target_wpm to {target_wpm}.
4. Compute time_limit_seconds = ceil(word_count / target_wpm * 60).
5. Use vocabulary appropriate to sub-level {sub_level}.

Output JSON matching FluencyReadTask. Set:
  widget="speak_and_record", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="read".
""",
    output_model_name="FluencyReadTask",
    evaluation_logic={
        "method": "azure_speech + wpm_calculation",
        "weights": {
            "wpm_target_met": 0.5,
            "completeness": 0.3,
            "intelligibility": 0.2,
        },
        "passing_threshold": 0.65,
        "notes": "Forgive minor pronunciation errors — flow matters most.",
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #14 Fluency / Write ──────────────────────────────────────────────

FULL_FLUENCY_WRITE_V1 = TaskTemplate(
    template_id="full_fluency_write_v1",
    sub_skill=SubSkill.FLUENCY,
    activity=Activity.WRITE,
    task_type="curriculum_fluency_timed_write",
    difficulty_range=(2, 10),
    estimated_time_minutes=8,
    scoring_method=ScoringMethod.AI_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: timed_text
TASK
1. Write a writing_prompt connected to "{topic_name}" that the learner can
   answer in {target_words} words within {time_limit} seconds.
   Examples:
   - "Tell a story about a time you took a risk." (fluency-speak narrative)
   - "Describe your weekend in detail." (small-talk fluency)
2. Set time_limit_seconds = {time_limit}.
3. Set minimum_word_count = {min_words}, target_word_count = {target_words}.
4. Set no_editing_allowed to true.
5. Provide a sample_response that hits the target word count.

Output JSON matching FluencyWriteTask. Set:
  widget="timed_text", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="write".
""",
    output_model_name="FluencyWriteTask",
    evaluation_logic={
        "method": "ai_evaluator",
        "weights": {
            "word_count_met": 0.4,
            "idea_flow": 0.3,
            "basic_grammar": 0.2,
            "topic_relevance": 0.1,
        },
        "passing_threshold": 0.6,
        "notes": "Forgive minor errors — measure FLOW.",
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #15 Fluency / Listen ─────────────────────────────────────────────

FULL_FLUENCY_LISTEN_V1 = TaskTemplate(
    template_id="full_fluency_listen_v1",
    sub_skill=SubSkill.FLUENCY,
    activity=Activity.LISTEN,
    task_type="curriculum_fluency_shadow",
    difficulty_range=(3, 10),
    estimated_time_minutes=6,
    scoring_method=ScoringMethod.SPEECH_API,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: listen_and_respond  (inner: speak_and_record — shadowing)
TASK
1. Write text_to_shadow (40–120 words) about a topic relevant to
   "{topic_name}". Use natural conversational rhythm.
2. Set speed: "slow" (beginner), "natural" (intermediate), "fast" (advanced).
3. Set delay_seconds: 1.5 (beginner), 1.0 (intermediate), 0.5 (advanced).
4. Set minimum_match_percentage to 0.7.
5. Set audio_url to null.

Output JSON matching FluencyListenTask. Set:
  widget="listen_and_respond", inner_widget="speak_and_record",
  topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="listen".
""",
    output_model_name="FluencyListenTask",
    evaluation_logic={
        "method": "azure_speech + temporal_alignment",
        "weights": {
            "match_percentage": 0.5,
            "rhythm_sync": 0.3,
            "completeness": 0.2,
        },
        "passing_threshold": 0.6,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #16 Fluency / Speak ──────────────────────────────────────────────

FULL_FLUENCY_SPEAK_V1 = TaskTemplate(
    template_id="full_fluency_speak_v1",
    sub_skill=SubSkill.FLUENCY,
    activity=Activity.SPEAK,
    task_type="curriculum_fluency_speak",
    difficulty_range=(1, 10),
    estimated_time_minutes=5,
    scoring_method=ScoringMethod.HYBRID,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: speak_and_record
TASK
1. Set fluency_focus from "{topic_name}". Examples:
   - "Speaking Without Long Pauses" → focus = "no-pause speaking"
   - "Small Talk — Weather" → focus = "casual workplace small talk"
   - "Self-Correction Without Stopping" → focus = "self-correction phrases"
2. Write a speaking_prompt that targets that focus and lasts
   {speaking_duration} seconds.
3. Set preparation_seconds = 10 (beginner), 5 (intermediate), 0 (advanced).
4. Provide 3–5 sample_talking_points that the learner can use after the task
   (NEVER show during).

Output JSON matching FluencySpeakTask. Set:
  widget="speak_and_record", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="speak".
""",
    output_model_name="FluencySpeakTask",
    evaluation_logic={
        "method": "azure_speech + ai_evaluator",
        "weights": {
            "wpm_naturalness": 0.3,
            "filler_rate_low": 0.2,
            "topic_adherence": 0.25,
            "self_correction_quality": 0.25,
        },
        "passing_threshold": 0.6,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #17 Expression / Read ────────────────────────────────────────────

FULL_EXPRESSION_READ_V1 = TaskTemplate(
    template_id="full_expression_read_v1",
    sub_skill=SubSkill.THOUGHT_ORGANIZATION,
    activity=Activity.READ,
    task_type="curriculum_expression_summarize",
    difficulty_range=(2, 10),
    estimated_time_minutes=7,
    scoring_method=ScoringMethod.AI_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: open_text
TASK
1. Set structure_pattern_taught from "{topic_name}". Examples:
   - "One Idea Per Sentence" → "single-clause sentences"
   - "Beginning, Middle, End" → "narrative arc"
   - "Pros and Cons Structure" → "weighted comparison"
2. Write a passage ({passage_word_count} words) that demonstrates that
   structural pattern clearly.
3. Generate 2–4 OpenTextItem prompts asking the learner to:
   - Summarize the main idea in 2 sentences
   - Identify the structural pattern used
   - Paraphrase a key argument
4. Provide a sample_answer for each prompt.

Output JSON matching ExpressionReadTask. Set:
  widget="open_text", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="read".
""",
    output_model_name="ExpressionReadTask",
    evaluation_logic={
        "method": "ai_evaluator",
        "weights": {
            "main_idea_captured": 0.4,
            "structure_correctly_identified": 0.3,
            "paraphrase_quality": 0.3,
        },
        "passing_threshold": 0.6,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #18 Expression / Write ───────────────────────────────────────────

FULL_EXPRESSION_WRITE_V1 = TaskTemplate(
    template_id="full_expression_write_v1",
    sub_skill=SubSkill.THOUGHT_ORGANIZATION,
    activity=Activity.WRITE,
    task_type="curriculum_expression_essay",
    difficulty_range=(3, 10),
    estimated_time_minutes=15,
    scoring_method=ScoringMethod.AI_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: structured_essay
TASK
1. Set structure_pattern based on "{topic_name}". Examples:
   - "Building a Three-Point Answer" → "intro + 3 points + conclusion"
   - "Persuasive Speaking Structure" → "claim-evidence-reason"
   - "Pros and Cons Structure" → "intro-pros-cons-conclusion"
2. Pick an overall_topic the learner cares about (career, study, life).
3. Generate 3–5 EssaySection objects covering the structure.
   - Each section has: section_id, section_name, section_prompt,
     minimum_word_count, sample_text.
4. Set total_target_words to {target_words}.

Output JSON matching ExpressionWriteTask. Set:
  widget="structured_essay", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="write".
""",
    output_model_name="ExpressionWriteTask",
    evaluation_logic={
        "method": "ai_evaluator",
        "weights": {
            "structure_followed": 0.35,
            "section_word_counts_met": 0.15,
            "argument_clarity": 0.25,
            "cohesion_between_sections": 0.25,
        },
        "passing_threshold": 0.6,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #19 Expression / Listen ──────────────────────────────────────────

FULL_EXPRESSION_LISTEN_V1 = TaskTemplate(
    template_id="full_expression_listen_v1",
    sub_skill=SubSkill.THOUGHT_ORGANIZATION,
    activity=Activity.LISTEN,
    task_type="curriculum_expression_listen_structure",
    difficulty_range=(3, 10),
    estimated_time_minutes=7,
    scoring_method=ScoringMethod.AI_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: listen_and_respond  (inner: open_text)
TASK
1. Set structure_to_identify from "{topic_name}".
2. Write an audio_script ({audio_word_count} words) that uses that
   organizational structure clearly (e.g. a 4-step explanation,
   a problem-solution mini-talk).
3. Generate 2–4 OpenTextItem prompts asking the learner to:
   - List the structural steps in order
   - Summarize the speaker's main argument
   - Identify how the speaker connected ideas
4. Set audio_url to null.

Output JSON matching ExpressionListenTask. Set:
  widget="listen_and_respond", inner_widget="open_text",
  topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="listen".
""",
    output_model_name="ExpressionListenTask",
    evaluation_logic={
        "method": "ai_evaluator",
        "weights": {
            "structure_correctly_identified": 0.5,
            "main_idea_captured": 0.3,
            "transitions_recognized": 0.2,
        },
        "passing_threshold": 0.6,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #20 Expression / Speak ───────────────────────────────────────────

FULL_EXPRESSION_SPEAK_V1 = TaskTemplate(
    template_id="full_expression_speak_v1",
    sub_skill=SubSkill.THOUGHT_ORGANIZATION,
    activity=Activity.SPEAK,
    task_type="curriculum_expression_storyboard",
    difficulty_range=(2, 10),
    estimated_time_minutes=8,
    scoring_method=ScoringMethod.AI_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: storyboard
TASK
1. Set narrative_pattern from "{topic_name}".
   Examples: "beginning-middle-end", "problem-solution", "cause-effect".
2. Pick an overall_story_premise the learner can narrate (work scene,
   travel anecdote, hypothetical situation).
3. Generate 3–6 StoryboardScene objects:
   - Each scene has scene_number, image_prompt (for ImageGen), and
     narration_focus (what the learner should describe).
   - Set image_url to null (ImageGen fills later).
4. Set speaking_duration_seconds based on tier.
5. Provide a sample_narration covering all scenes.

Output JSON matching ExpressionSpeakTask. Set:
  widget="storyboard", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="speak".
""",
    output_model_name="ExpressionSpeakTask",
    evaluation_logic={
        "method": "stt + ai_evaluator",
        "weights": {
            "all_scenes_covered": 0.3,
            "narrative_pattern_followed": 0.3,
            "transitions_smooth": 0.2,
            "fluency": 0.2,
        },
        "passing_threshold": 0.6,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #21 Comprehension / Read ─────────────────────────────────────────

FULL_COMPREHENSION_READ_V1 = TaskTemplate(
    template_id="full_comprehension_read_v1",
    sub_skill=SubSkill.LISTENING,
    activity=Activity.READ,
    task_type="curriculum_comprehension_read_mcq",
    difficulty_range=(1, 10),
    estimated_time_minutes=6,
    scoring_method=ScoringMethod.RULE_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: mcq
TASK
1. Write a passage ({passage_word_count} words) appropriate for
   "{topic_name}". E.g.:
   - "Listening for Numbers and Times" → text with multiple times/dates
   - "Identifying Speaker Emotion" → text with emotional cues
   - "Catching Sarcasm and Irony" → text with ironic tone
2. Generate {item_count} MCQ items mixing question types from
   question_types_used (must include at least 2 of:
   "main_idea", "specific_detail", "inference", "vocabulary_in_context",
   "tone", "speaker_purpose").
3. Each MCQ has 4 options + correct_index + explanation.

Output JSON matching ComprehensionReadTask. Set:
  widget="mcq", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="read".
""",
    output_model_name="ComprehensionReadTask",
    evaluation_logic={
        "method": "exact_match_per_mcq",
        "passing_threshold": 0.7,
        "metrics_returned": ["accuracy", "by_question_type"],
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #22 Comprehension / Write ────────────────────────────────────────

FULL_COMPREHENSION_WRITE_V1 = TaskTemplate(
    template_id="full_comprehension_write_v1",
    sub_skill=SubSkill.LISTENING,
    activity=Activity.WRITE,
    task_type="curriculum_comprehension_write_answers",
    difficulty_range=(1, 10),
    estimated_time_minutes=8,
    scoring_method=ScoringMethod.AI_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: open_text
TASK
1. Decide source: write source_passage (if reading-based topic) OR
   source_audio_script (if listening-based topic). Choose what fits
   "{topic_name}" best. Use {audio_word_count} words.
2. Generate 3–6 OpenTextItem prompts asking the learner to:
   - Write the answer to specific factual questions
   - Fill in missing information from memory
   - Explain something the speaker/author implied
3. Provide sample_answer for each prompt.
4. Set source_audio_url to null if audio (TTS fills later).

Output JSON matching ComprehensionWriteTask. Set:
  widget="open_text", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="write".
""",
    output_model_name="ComprehensionWriteTask",
    evaluation_logic={
        "method": "ai_evaluator + key_phrase_match",
        "weights": {
            "factual_accuracy": 0.5,
            "completeness": 0.3,
            "clarity": 0.2,
        },
        "passing_threshold": 0.65,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #23 Comprehension / Listen ───────────────────────────────────────

FULL_COMPREHENSION_LISTEN_V1 = TaskTemplate(
    template_id="full_comprehension_listen_v1",
    sub_skill=SubSkill.LISTENING,
    activity=Activity.LISTEN,
    task_type="curriculum_comprehension_listen_mcq",
    difficulty_range=(1, 10),
    estimated_time_minutes=7,
    scoring_method=ScoringMethod.RULE_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: listen_and_respond  (inner: mcq)
TASK
1. Pick audio_genre based on "{topic_name}":
   - "Listening to News Headlines" → "news"
   - "Listening to Lectures" → "lecture"
   - "Following Group Discussions" → "conversation"
   - default → "conversation"
2. Write an audio_script ({audio_word_count} words) in that genre that
   tests the topic's specific listening skill.
3. Generate {item_count} MCQ items covering main idea, specific details,
   inference, and tone (mix at least 3 types).
4. Set audio_url to null.

Output JSON matching ComprehensionListenTask. Set:
  widget="listen_and_respond", inner_widget="mcq",
  topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="listen".
""",
    output_model_name="ComprehensionListenTask",
    evaluation_logic={
        "method": "exact_match_per_mcq",
        "passing_threshold": 0.7,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #24 Comprehension / Speak ────────────────────────────────────────

FULL_COMPREHENSION_SPEAK_V1 = TaskTemplate(
    template_id="full_comprehension_speak_v1",
    sub_skill=SubSkill.LISTENING,
    activity=Activity.SPEAK,
    task_type="curriculum_comprehension_retell",
    difficulty_range=(2, 10),
    estimated_time_minutes=7,
    scoring_method=ScoringMethod.HYBRID,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: speak_and_record
TASK
1. Write source_audio_script ({audio_word_count} words) related to
   "{topic_name}".
2. Set retelling_prompt (e.g. "Retell the story in your own words" or
   "Answer: what did the speaker recommend and why?").
3. List 3–8 key_points_expected the retelling should cover.
4. Set speaking_duration_seconds = {speaking_duration}.
5. Set source_audio_url to null.

Output JSON matching ComprehensionSpeakTask. Set:
  widget="speak_and_record", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="speak".
""",
    output_model_name="ComprehensionSpeakTask",
    evaluation_logic={
        "method": "stt + key_point_match + ai_evaluator",
        "weights": {
            "key_points_covered": 0.5,
            "factual_accuracy": 0.2,
            "fluency": 0.2,
            "intelligibility": 0.1,
        },
        "passing_threshold": 0.6,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #25 Tone / Read ──────────────────────────────────────────────────

FULL_TONE_READ_V1 = TaskTemplate(
    template_id="full_tone_read_v1",
    sub_skill=SubSkill.TONE,
    activity=Activity.READ,
    task_type="curriculum_tone_read_mcq",
    difficulty_range=(1, 10),
    estimated_time_minutes=4,
    scoring_method=ScoringMethod.RULE_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: mcq
TASK
1. Set tone_concepts_taught from "{topic_name}".
   E.g. "Greetings — Formal vs Casual" → ["formal", "casual"].
2. Generate {item_count} MCQ items where each item shows a written message
   and asks one of:
   - "What is the tone of this message?"
   - "Which version is more formal?"
   - "Which message would you send to a manager vs a friend?"
   - "Which sentence is too direct/too soft?"
3. Each MCQ has 4 options + correct_index + explanation that teaches
   the tone signal (word choice, structure, politeness markers).

Output JSON matching ToneReadTask. Set:
  widget="mcq", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="read".
""",
    output_model_name="ToneReadTask",
    evaluation_logic={
        "method": "exact_match_per_mcq",
        "passing_threshold": 0.7,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #26 Tone / Write ─────────────────────────────────────────────────

FULL_TONE_WRITE_V1 = TaskTemplate(
    template_id="full_tone_write_v1",
    sub_skill=SubSkill.TONE,
    activity=Activity.WRITE,
    task_type="curriculum_tone_rewrite",
    difficulty_range=(1, 10),
    estimated_time_minutes=7,
    scoring_method=ScoringMethod.AI_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: open_text
TASK
1. Pick target_register from "{topic_name}":
   - "Workplace English" / "Professional Email" → "professional"
   - "Casual vs Workplace English" → "casual" or "professional"
   - "Friendly Email Tone" → "friendly"
   - default → "professional"
2. Generate 3–6 OpenTextItem prompts. Each asks the learner to:
   - Rewrite a casual message in formal tone (or vice versa)
   - Soften a harsh request
   - Make a polite request more direct
3. Provide a sample_answer for each.
4. List 2–4 common_pitfalls (e.g. "over-using 'please'", "starting with 'I want'").

Output JSON matching ToneWriteTask. Set:
  widget="open_text", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="write".
""",
    output_model_name="ToneWriteTask",
    evaluation_logic={
        "method": "ai_evaluator",
        "weights": {
            "register_correctly_applied": 0.5,
            "politeness_markers_used": 0.25,
            "message_intent_preserved": 0.25,
        },
        "passing_threshold": 0.65,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #27 Tone / Listen ────────────────────────────────────────────────

FULL_TONE_LISTEN_V1 = TaskTemplate(
    template_id="full_tone_listen_v1",
    sub_skill=SubSkill.TONE,
    activity=Activity.LISTEN,
    task_type="curriculum_tone_listen_mcq",
    difficulty_range=(1, 10),
    estimated_time_minutes=5,
    scoring_method=ScoringMethod.RULE_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: listen_and_respond  (inner: mcq)
TASK
1. Set voice_style_hint based on "{topic_name}".
   E.g. "Detect Speaker Tone" → "varied — sad / cheerful / sarcastic / firm".
2. Write an audio_script (60–200 words) where the speaker's TONE matters
   more than the literal text (irony, urgency, politeness, anger, warmth).
3. Generate {item_count} MCQ items asking the learner to:
   - Identify the speaker's tone/emotion
   - Detect register mismatch (e.g. too casual for the setting)
   - Choose the appropriate response tone
4. Set audio_url to null.

Output JSON matching ToneListenTask. Set:
  widget="listen_and_respond", inner_widget="mcq",
  topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="listen".
""",
    output_model_name="ToneListenTask",
    evaluation_logic={
        "method": "exact_match_per_mcq",
        "passing_threshold": 0.7,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ─── #28 Tone / Speak ─────────────────────────────────────────────────

FULL_TONE_SPEAK_V1 = TaskTemplate(
    template_id="full_tone_speak_v1",
    sub_skill=SubSkill.TONE,
    activity=Activity.SPEAK,
    task_type="curriculum_tone_roleplay",
    difficulty_range=(2, 10),
    estimated_time_minutes=8,
    scoring_method=ScoringMethod.AI_BASED,
    llm_prompt_template=_CURRICULUM_HEADER + """

WIDGET: speak_and_record  (multi-turn roleplay)
TASK
1. Set scenario_description based on "{topic_name}".
   Examples:
   - "Polite Requests" → asking a colleague for help with a deadline
   - "Disagreeing Politely" → pushing back on a teammate's idea
   - "Diplomatic Disagreement" → declining a manager's plan respectfully
2. Set target_tone (e.g. "polite-but-firm", "warm-professional", "assertive").
3. Generate 3–6 RoleplayTurn objects alternating ai/user.
   - First turn is AI.
   - For each user turn, set expected_user_tone matching target_tone.
4. Provide 2–3 sample_user_responses for the AI's turns (used by evaluator).
5. Set speaking_duration_seconds = {speaking_duration}.

Output JSON matching ToneSpeakTask. Set:
  widget="speak_and_record", topic_id="{topic_id}", topic_name="{topic_name}",
  sub_skill="{sub_skill}", sub_level={sub_level}, activity="speak".
""",
    output_model_name="ToneSpeakTask",
    evaluation_logic={
        "method": "stt + ai_evaluator",
        "weights": {
            "tone_consistency": 0.4,
            "register_appropriateness": 0.25,
            "scenario_fit": 0.2,
            "fluency": 0.15,
        },
        "passing_threshold": 0.6,
    },
    difficulty_modifiers=_TIER_DEFAULTS,
)


# ═════════════════════════════════════════════════════════════════════
# REGISTRIES
# ═════════════════════════════════════════════════════════════════════


FULL_TASK_TEMPLATES: list[TaskTemplate] = [
    # Grammar
    FULL_GRAMMAR_READ_V1,
    FULL_GRAMMAR_WRITE_V1,
    FULL_GRAMMAR_LISTEN_V1,
    FULL_GRAMMAR_SPEAK_V1,
    # Vocabulary
    FULL_VOCABULARY_READ_V1,
    FULL_VOCABULARY_WRITE_V1,
    FULL_VOCABULARY_LISTEN_V1,
    FULL_VOCABULARY_SPEAK_V1,
    # Pronunciation
    FULL_PRONUNCIATION_READ_V1,
    FULL_PRONUNCIATION_WRITE_V1,
    FULL_PRONUNCIATION_LISTEN_V1,
    FULL_PRONUNCIATION_SPEAK_V1,
    # Fluency
    FULL_FLUENCY_READ_V1,
    FULL_FLUENCY_WRITE_V1,
    FULL_FLUENCY_LISTEN_V1,
    FULL_FLUENCY_SPEAK_V1,
    # Expression / Thought Organization
    FULL_EXPRESSION_READ_V1,
    FULL_EXPRESSION_WRITE_V1,
    FULL_EXPRESSION_LISTEN_V1,
    FULL_EXPRESSION_SPEAK_V1,
    # Comprehension / Listening
    FULL_COMPREHENSION_READ_V1,
    FULL_COMPREHENSION_WRITE_V1,
    FULL_COMPREHENSION_LISTEN_V1,
    FULL_COMPREHENSION_SPEAK_V1,
    # Tone & Social Awareness
    FULL_TONE_READ_V1,
    FULL_TONE_WRITE_V1,
    FULL_TONE_LISTEN_V1,
    FULL_TONE_SPEAK_V1,
]


FULL_TASK_OUTPUT_MODELS = {
    "GrammarReadTask": GrammarReadTask,
    "GrammarWriteTask": GrammarWriteTask,
    "GrammarListenTask": GrammarListenTask,
    "GrammarSpeakTask": GrammarSpeakTask,
    "VocabularyReadTask": VocabularyReadTask,
    "VocabularyWriteTask": VocabularyWriteTask,
    "VocabularyListenTask": VocabularyListenTask,
    "VocabularySpeakTask": VocabularySpeakTask,
    "PronunciationReadTask": PronunciationReadTask,
    "PronunciationWriteTask": PronunciationWriteTask,
    "PronunciationListenTask": PronunciationListenTask,
    "PronunciationSpeakTask": PronunciationSpeakTask,
    "FluencyReadTask": FluencyReadTask,
    "FluencyWriteTask": FluencyWriteTask,
    "FluencyListenTask": FluencyListenTask,
    "FluencySpeakTask": FluencySpeakTask,
    "ExpressionReadTask": ExpressionReadTask,
    "ExpressionWriteTask": ExpressionWriteTask,
    "ExpressionListenTask": ExpressionListenTask,
    "ExpressionSpeakTask": ExpressionSpeakTask,
    "ComprehensionReadTask": ComprehensionReadTask,
    "ComprehensionWriteTask": ComprehensionWriteTask,
    "ComprehensionListenTask": ComprehensionListenTask,
    "ComprehensionSpeakTask": ComprehensionSpeakTask,
    "ToneReadTask": ToneReadTask,
    "ToneWriteTask": ToneWriteTask,
    "ToneListenTask": ToneListenTask,
    "ToneSpeakTask": ToneSpeakTask,
}


# ═════════════════════════════════════════════════════════════════════
# LOOKUP HELPERS
# ═════════════════════════════════════════════════════════════════════


# Lookup table: (sub_skill, activity) -> template
_FULL_TEMPLATE_INDEX: dict[tuple[SubSkill, Activity], TaskTemplate] = {
    (t.sub_skill, t.activity): t for t in FULL_TASK_TEMPLATES
}


def get_full_template(sub_skill: SubSkill, activity: Activity) -> TaskTemplate:
    """
    Get the curriculum-driven template for a (sub_skill, activity) pair.

    Used by the Task Generator agent each day:

        from app.tasks.schemas.full_tasks_templates import get_full_template
        from app.tasks.schemas.base import SubSkill, Activity

        template = get_full_template(SubSkill.GRAMMAR, Activity.READ)
        # → FULL_GRAMMAR_READ_V1

    Raises KeyError if no template exists for the pair (shouldn't happen —
    we have all 7 × 4 = 28 combinations covered).
    """
    key = (sub_skill, activity)
    if key not in _FULL_TEMPLATE_INDEX:
        raise KeyError(
            f"No full-task template registered for "
            f"(sub_skill={sub_skill}, activity={activity})"
        )
    return _FULL_TEMPLATE_INDEX[key]


def list_full_templates_by_widget(widget: UIWidget) -> list[TaskTemplate]:
    """Return all templates that render with a given UI widget."""
    return [
        t for t in FULL_TASK_TEMPLATES
        if t.output_model_name in FULL_TASK_OUTPUT_MODELS
        and FULL_TASK_OUTPUT_MODELS[t.output_model_name].model_fields["widget"]
        .default == widget
    ]


# Convenience: which widget does each output_model use?
TEMPLATE_TO_WIDGET: dict[str, UIWidget] = {
    "GrammarReadTask": UIWidget.FILL_IN_BLANKS,
    "GrammarWriteTask": UIWidget.OPEN_TEXT,
    "GrammarListenTask": UIWidget.LISTEN_AND_RESPOND,
    "GrammarSpeakTask": UIWidget.SPEAK_AND_RECORD,
    "VocabularyReadTask": UIWidget.MCQ,
    "VocabularyWriteTask": UIWidget.OPEN_TEXT,
    "VocabularyListenTask": UIWidget.LISTEN_AND_RESPOND,
    "VocabularySpeakTask": UIWidget.SPEAK_AND_RECORD,
    "PronunciationReadTask": UIWidget.SPEAK_AND_RECORD,
    "PronunciationWriteTask": UIWidget.MCQ,
    "PronunciationListenTask": UIWidget.LISTEN_AND_RESPOND,
    "PronunciationSpeakTask": UIWidget.SPEAK_AND_RECORD,
    "FluencyReadTask": UIWidget.SPEAK_AND_RECORD,
    "FluencyWriteTask": UIWidget.TIMED_TEXT,
    "FluencyListenTask": UIWidget.LISTEN_AND_RESPOND,
    "FluencySpeakTask": UIWidget.SPEAK_AND_RECORD,
    "ExpressionReadTask": UIWidget.OPEN_TEXT,
    "ExpressionWriteTask": UIWidget.STRUCTURED_ESSAY,
    "ExpressionListenTask": UIWidget.LISTEN_AND_RESPOND,
    "ExpressionSpeakTask": UIWidget.STORYBOARD,
    "ComprehensionReadTask": UIWidget.MCQ,
    "ComprehensionWriteTask": UIWidget.OPEN_TEXT,
    "ComprehensionListenTask": UIWidget.LISTEN_AND_RESPOND,
    "ComprehensionSpeakTask": UIWidget.SPEAK_AND_RECORD,
    "ToneReadTask": UIWidget.MCQ,
    "ToneWriteTask": UIWidget.OPEN_TEXT,
    "ToneListenTask": UIWidget.LISTEN_AND_RESPOND,
    "ToneSpeakTask": UIWidget.SPEAK_AND_RECORD,
}
