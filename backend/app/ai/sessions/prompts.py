"""Prompt builders for the sessions-flow LLM agents.

Phase 4 MVP uses ONE parameterized prompt per agent kind instead of the
~160 per-archetype files the doc imagined. The archetype's metadata
(rubric, weight_map, ui_widget) is interpolated into the same template
each call — the LLM adapts.

Phase 5+ can swap individual prompts in if any archetype needs special
handling. Keep this file the only place prompt text lives, so refactors
don't have to chase strings across the codebase.
"""

from __future__ import annotations

import json

from app.scoring import ArchetypeSpec


_EVAL_SYSTEM = """\
You are an expert English tutor scoring one learner activity. You produce
an objective evaluation against the archetype's rubric — no feedback
wording, no encouragement, no rewriting. Another agent handles that.

Hard rules:
  - Output JSON matching the requested schema, nothing else.
  - `raw_score` is a single number in [0.0, 10.0] one-decimal precision.
  - `rubric_scores` has one float per rubric item (same scale).
  - `evaluator_notes` is one short sentence summarising the dominant
    error pattern or strength; leave it empty for perfect responses.
  - Do NOT include feedback to the user. Do NOT include corrections.
"""


_FEEDBACK_SYSTEM = """\
You are a kind, specific English tutor writing feedback for one learner
activity. The Evaluator agent already produced the score; your job is
to turn that score into specific, actionable feedback the learner can
act on.

Hard rules:
  - Output JSON matching the requested schema, nothing else.
  - `summary` is 1–2 sentences. Never generic ("Good job" is banned).
  - `did_well` lists 1–3 specific positives. Empty list is OK for poor work.
  - `mistakes` lists at most 3 items, each with the user's exact wording
    (when relevant), the issue label, the correction, and the rule.
  - `next_tip` is one concrete thing to try next time. May be null.
  - `sub_skill_breakdown` maps each sub-skill in the archetype's weight
    map to a score in [0, 10].
"""


_TASK_GEN_SYSTEM = """\
You are a CEFR-aware curriculum designer generating ONE learning task
for a daily English lesson. The frontend renders your output through a
specific widget, so emit the real payload fields that widget needs.

Hard rules:
  - Output JSON matching the requested schema, nothing else.
  - `topic` repeats or refines the day's topic in one short sentence.
  - `instructions` is ONE imperative sentence telling the learner what
    to do. No greetings, no preamble.
  - `primary_text` is the substantive content the learner reads,
    transforms, listens to, or responds to.
  - `target_words` (optional) lists 0–10 vocabulary items the activity
    centres on. Use for vocabulary-themed archetypes; leave empty otherwise.
  - For fill_in_blanks, include `items` (or `blanks`) with
    sentence_with_blank, correct_answer, explanation, and optional
    distractors/base_verb.
  - For mcq, include `items` with item_id, prompt, options, correct_index,
    and explanation.
  - For listen_and_respond, include `audio_script`, `audio_url: null`,
    `inner_widget`, and the inner widget fields such as `items`.
  - For open_text, include `items` with item_id, prompt, sample_answer,
    and answer_hints.
  - For speak_and_record, include speaking_duration_seconds plus either
    speaking_prompt or speaking_prompts and a sample response/hints.
  - Include answer keys/sample answers inside the payload so the evaluator
    can score the response from this task alone.
"""


# ── User-prompt builders ───────────────────────────────────────────


def build_eval_user_prompt(
    *,
    archetype: ArchetypeSpec,
    task_content: dict,
    user_response: dict | None,
    evaluator_overrides: dict | None = None,
) -> str:
    parts = [
        f"Archetype: {archetype.archetype_id} ({archetype.name})",
        f"Core activity: {archetype.core_activity}",
        f"Rubric criteria: {', '.join(archetype.rubric)}",
        "",
        "Task that was shown to the learner:",
        json.dumps(_compact(task_content), ensure_ascii=False, indent=2),
        "",
        "Learner response:",
        json.dumps(user_response or {}, ensure_ascii=False, indent=2),
    ]
    if evaluator_overrides:
        parts.extend([
            "",
            "Author evaluator overrides:",
            json.dumps(evaluator_overrides, ensure_ascii=False, indent=2),
        ])
    parts.extend([
        "",
        "Score this response. Return JSON for the EvaluationOutput schema.",
    ])
    return "\n".join(parts)


def build_feedback_user_prompt(
    *,
    archetype: ArchetypeSpec,
    raw_score: float,
    rubric_scores: dict[str, float],
    evaluator_notes: str | None,
    task_content: dict,
    user_response: dict | None,
    feedback_overrides: dict | None = None,
) -> str:
    parts = [
        f"Archetype: {archetype.archetype_id} ({archetype.name})",
        f"Sub-skills to comment on: {', '.join(archetype.weight_map)}",
        "",
        f"Evaluator raw_score: {raw_score:.1f}/10",
        f"Per-rubric scores: {json.dumps(rubric_scores)}",
    ]
    if evaluator_notes:
        parts.append(f"Evaluator notes: {evaluator_notes}")
    parts.extend([
        "",
        "Task that was shown to the learner:",
        json.dumps(_compact(task_content), ensure_ascii=False, indent=2),
        "",
        "Learner response:",
        json.dumps(user_response or {}, ensure_ascii=False, indent=2),
    ])
    if feedback_overrides:
        parts.extend([
            "",
            "Author feedback overrides:",
            json.dumps(feedback_overrides, ensure_ascii=False, indent=2),
        ])
    parts.extend([
        "",
        "Write feedback. Return JSON for the FeedbackOutput schema.",
    ])
    return "\n".join(parts)


def build_task_gen_user_prompt(
    *,
    archetype: ArchetypeSpec,
    day_topic: str,
    explanation_brief: str,
    cefr_level: str,
    sub_level: int,
    user_interests: list[str] | None,
    task_spec: dict | None = None,
) -> str:
    interests = ", ".join(user_interests) if user_interests else "general"
    spec = task_spec or {}
    effective_topic = spec.get("topic_override") or day_topic
    parts = [
        f"Archetype: {archetype.archetype_id} ({archetype.name})",
        f"Core activity: {archetype.core_activity}",
        f"Day topic: {effective_topic}",
        f"Day brief: {explanation_brief}",
        f"Target CEFR level: {cefr_level}, sub-level {sub_level} of 10",
        f"Learner interests: {interests}",
    ]
    if spec.get("instructions_override"):
        parts.append(f"Author instructions (use verbatim): {spec['instructions_override']}")
    if spec.get("primary_text_seed"):
        parts.append(f"Primary text seed (build on this): {spec['primary_text_seed']}")
    if spec.get("target_words"):
        words = ", ".join(spec["target_words"])
        parts.append(f"Target words to include: {words}")
    if spec.get("difficulty_note"):
        parts.append(f"Difficulty note: {spec['difficulty_note']}")
    if spec.get("widget_requirements"):
        parts.append(f"Widget requirements: {spec['widget_requirements']}")
    if spec.get("task_intro"):
        parts.append(f"Task intro to use: {spec['task_intro']}")
    if spec.get("estimated_time_minutes"):
        parts.append(f"Estimated time minutes: {spec['estimated_time_minutes']}")
    widget_key = _widget_key(archetype.ui_widget)
    parts.extend([
        "",
        f"Frontend widget key to target: {widget_key}",
        f"Generate one {archetype.core_activity} task on this topic at the "
        f"target level. Return JSON for the TaskGenOutput schema.",
    ])
    return "\n".join(parts)


# ── Helpers ────────────────────────────────────────────────────────


def _compact(content: dict) -> dict:
    """Strip noisy internal keys before embedding in a prompt."""
    drop = {"phase", "archetype_id", "ui_widget", "core_activity", "archetype_name"}
    return {k: v for k, v in content.items() if k not in drop}


def _widget_key(ui_widget: str) -> str:
    mapping = {
        "FillInBlanks": "fill_in_blanks",
        "MCQList": "mcq",
        "ListenAndAnswer+MCQList": "listen_and_respond",
        "ListenAndAnswer+FillInBlanks": "listen_and_respond",
        "ListenAndAnswer+OpenTextList": "listen_and_respond",
        "ListenAndAnswer+SpeakAndRecord": "listen_and_respond",
        "SpeakAndRecord": "speak_and_record",
        "Storyboard": "storyboard",
        "StructuredEssay": "structured_essay",
        "OpenTextList": "open_text",
        "SentenceTransform": "open_text",
        "ErrorCorrection": "open_text",
        "TimedText": "timed_text",
    }
    return mapping.get(ui_widget, ui_widget)


# ── System-prompt accessors ────────────────────────────────────────


def eval_system_prompt() -> str:
    return _EVAL_SYSTEM


def feedback_system_prompt() -> str:
    return _FEEDBACK_SYSTEM


def task_gen_system_prompt() -> str:
    return _TASK_GEN_SYSTEM
