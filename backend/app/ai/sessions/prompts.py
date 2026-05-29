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

from app.modules.sessions.widget_mapping import normalize_widget_key
from app.scoring import ArchetypeSpec

_OPEN_ENDED_FEEDBACK_WIDGETS = {
    "open_text",
    "timed_text",
    "structured_essay",
    "speak_and_record",
    "storyboard",
}


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
  - Only add a `mistakes` item when the learner's actual submitted wording
    contains a concrete error. If the wording is already acceptable, put the
    point in `did_well` instead.
  - For open-ended writing/speaking tasks, there is no binary right/wrong
    answer. Use `correction` as an improved version of the learner's wording:
    same idea, but with spelling, grammar, word choice, and clarity improved.
    The improved version must never introduce a new grammar error.
  - CRITICAL: When `confirmed_wrong_answers` appears in the prompt it is the
    ONLY authoritative source for mistakes. Generate `mistakes` entries for
    EXACTLY those items — no more, no fewer. NEVER infer, guess, or add any
    mistake that is not explicitly listed there, even if you believe the learner
    made one.
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
  - For error_correction, include `items` with item_id, incorrect_sentence,
    sample_answer, and watch_hints.
  - For error_spotting, include `passage_sentences`: exactly 5 sentence
    objects. Each sentence must include tokenized `tokens` and exactly one
    `error` object whose token_id points at the single token where the
    learner should tap. Set `total_errors: 5`.
  - For speak_and_record, REQUIRED top-level fields are:
      * `task_intro` — short imperative line (e.g. "Record your routine
        sentences.").
      * `instructions` — one sentence telling the learner what to do.
      * `speaking_prompts` — a list of 2–3 short prompts. Each must be a
        complete instruction the learner can act on (e.g. "Say one
        routine sentence using 'he' and a frequency adverb.").
      * `sample_responses` — same length as `speaking_prompts`. Each is
        a model spoken answer that satisfies the prompt.
      * `speaking_duration_seconds` — integer, typically 30–60.
      * `target_words` — list of 3–10 vocabulary items the learner
        should try to use, when relevant.
      * `grammar_rule_to_practice` — one short sentence describing the
        rule under test.
    Do NOT emit a bare `speaking_prompt` (singular) — always use the
    list form so the widget renders one item per prompt.
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


def build_speak_eval_user_prompt(
    *,
    archetype: ArchetypeSpec,
    task_content: dict,
    speaking_items: list[dict],
    evaluator_overrides: dict | None = None,
) -> str:
    """Structured speaking evaluation prompt with prompt/transcript alignment."""
    parts = [
        f"Archetype: {archetype.archetype_id} ({archetype.name})",
        f"Core activity: {archetype.core_activity}",
        f"Rubric criteria: {', '.join(archetype.rubric)}",
        "",
        "Speaking task context:",
        json.dumps(_compact(task_content), ensure_ascii=False, indent=2),
        "",
        "Learner spoken responses (score each transcript against its prompt):",
        json.dumps(speaking_items, ensure_ascii=False, indent=2),
        "",
        "Score the learner's spoken performance. Use grammar_rule_to_practice, "
        "target_words, and sample_response fields when present. Return JSON for "
        "the EvaluationOutput schema.",
    ]
    if evaluator_overrides:
        parts.extend([
            "",
            "Author evaluator overrides:",
            json.dumps(evaluator_overrides, ensure_ascii=False, indent=2),
        ])
    return "\n".join(parts)


def compute_wrong_items(task_content: dict, user_response: dict) -> list[dict]:
    """Deterministically find which items the learner answered incorrectly.

    Compares case-insensitively, matching the frontend isCorrect() logic.
    Only items the learner actually answered are checked — blank/missing
    answers are excluded so unanswered items don't appear as mistakes.
    """
    wrong: list[dict] = []
    for item in task_content.get("items", []):
        item_id = item.get("item_id", "")
        correct = str(item.get("correct_answer", "")).strip().lower()
        user_val = str(user_response.get(item_id, "")).strip().lower()
        if user_val and user_val != correct:
            wrong.append({
                "item_id": item_id,
                "user_wrote": user_response.get(item_id),
                "correct_answer": item.get("correct_answer"),
                "explanation": item.get("explanation", ""),
            })
    return wrong


def compute_mcq_wrong_items(task_content: dict, user_response: dict) -> list[dict]:
    """Deterministically find wrong MCQ answers from a listen_and_respond submission.

    Response format: inner_response.answers = [{item_id, selected_index}, ...]
    Task format: items[].correct_index (0-based int), items[].options (list of str)
    """
    wrong: list[dict] = []
    submitted = _mcq_submitted_answer_map(user_response)
    for item in task_content.get("items", []):
        item_id = item.get("item_id", "")
        correct_idx = item.get("correct_index")
        selected_idx = submitted.get(item_id)
        if selected_idx is None or correct_idx is None:
            continue
        if selected_idx != correct_idx:
            options = item.get("options") or []
            wrong.append({
                "item_id": item_id,
                "user_selected": options[selected_idx] if selected_idx < len(options) else str(selected_idx),
                "correct_answer": options[correct_idx] if correct_idx < len(options) else str(correct_idx),
                "explanation": item.get("explanation", ""),
            })
    return wrong


def _mcq_submitted_answer_map(user_response: dict) -> dict[str, int]:
    inner = user_response.get("inner_response") or {}
    rows = inner.get("answers") if isinstance(inner, dict) else None
    if not isinstance(rows, list):
        rows = user_response.get("answers")

    submitted: dict[str, int] = {}
    if isinstance(rows, list):
        for answer in rows:
            if not isinstance(answer, dict) or "item_id" not in answer:
                continue
            try:
                submitted[str(answer["item_id"])] = int(answer.get("selected_index"))
            except (TypeError, ValueError):
                continue

    for key, value in user_response.items():
        if key in {"inner_response", "listen_analytics", "time_spent_seconds", "answers"}:
            continue
        try:
            submitted.setdefault(str(key), int(value))
        except (TypeError, ValueError):
            continue

    return submitted


def compute_listen_cloze_wrong_items(task_content: dict, user_response: dict) -> list[dict]:
    """Find wrong fill-in-blank answers inside a listen_and_respond submission."""
    wrong: list[dict] = []
    inner = user_response.get("inner_response") or {}
    submitted = {
        str(a.get("item_id") or a.get("blank_id") or ""): a.get("user_answer")
        for a in (inner.get("answers") or [])
        if isinstance(a, dict) and (a.get("item_id") or a.get("blank_id"))
    }
    for item in task_content.get("items", []) or task_content.get("blanks", []):
        item_id = str(item.get("item_id") or item.get("blank_id") or "")
        correct = str(item.get("correct_answer", "")).strip().lower()
        user_val_raw = submitted.get(item_id)
        user_val = str(user_val_raw or "").strip().lower()
        if user_val and user_val != correct:
            wrong.append({
                "item_id": item_id,
                "user_wrote": user_val_raw,
                "correct_answer": item.get("correct_answer"),
                "explanation": item.get("explanation", ""),
                "rule": item.get("grammar_rule", ""),
            })
    return wrong


def compute_error_spotting_wrong_items(task_content: dict, user_response: dict) -> list[dict]:
    """Find missed and falsely selected word-level error-spotting items."""
    selected_ids = {
        str(token_id)
        for token_id in (user_response.get("selected_token_ids") or [])
    }
    correct_errors: list[dict] = []
    token_lookup: dict[str, dict] = {}
    for sentence in task_content.get("passage_sentences") or []:
        if not isinstance(sentence, dict):
            continue
        for token in sentence.get("tokens") or []:
            if isinstance(token, dict) and token.get("token_id"):
                token_lookup[str(token["token_id"])] = {
                    **token,
                    "sentence_id": sentence.get("sentence_id"),
                }
        error = sentence.get("error")
        if isinstance(error, dict) and error.get("token_id"):
            correct_errors.append({
                **error,
                "sentence_id": sentence.get("sentence_id"),
            })

    wrong: list[dict] = []
    for error in correct_errors:
        if str(error["token_id"]) not in selected_ids:
            incorrect_phrase = error.get("incorrect_phrase") or error.get("token_id")
            wrong.append({
                "item_id": error.get("token_id"),
                "user_wrote": incorrect_phrase,
                "correct_answer": error.get("correction"),
                "explanation": error.get("explanation") or error.get("rule") or "",
                "error_type": "missed_error",
                "incorrect_phrase": incorrect_phrase,
                "rule": error.get("rule") or "",
            })
    correct_ids = {str(error["token_id"]) for error in correct_errors}
    for token_id in sorted(selected_ids - correct_ids):
        token = token_lookup.get(token_id) or {}
        wrong.append({
            "item_id": token_id,
            "user_wrote": token.get("text") or token_id,
            "correct_answer": "Do not flag this word",
            "explanation": "This selected word was not one of the passage errors.",
            "error_type": "false_positive",
        })
    return wrong


def build_feedback_user_prompt(
    *,
    archetype: ArchetypeSpec,
    raw_score: float,
    rubric_scores: dict[str, float],
    evaluator_notes: str | None,
    task_content: dict,
    user_response: dict | None,
    feedback_overrides: dict | None = None,
    confirmed_mistakes: list[dict] | None = None,
) -> str:
    widget_key = _widget_key(archetype.ui_widget)
    parts = [
        f"Archetype: {archetype.archetype_id} ({archetype.name})",
        f"Widget: {widget_key}",
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
    if confirmed_mistakes is not None:
        parts.extend([
            "",
            "Confirmed wrong answers (ground truth — do NOT infer additional mistakes):",
            json.dumps(confirmed_mistakes, ensure_ascii=False, indent=2),
        ])
    elif widget_key in _OPEN_ENDED_FEEDBACK_WIDGETS:
        parts.extend([
            "",
            "Open-ended feedback mode:",
            "- Treat the learner's answer as a scored performance on a spectrum, not as right/wrong.",
            "- First decide which submitted answers actually contain errors; do not create one feedback item per submitted answer.",
            "- For each `mistakes` item, set `user_wrote` to the exact learner wording or sentence being improved.",
            "- Set `correction` to an improved version that preserves the same idea while fixing spelling, grammar, word choice, and clarity.",
            "- If `user_wrote` is already grammatical and clear, do not include it in `mistakes`; mention it in `did_well` if useful.",
            "- Do not invent a different answer, and do not label the learner's wording as a wrong answer.",
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
    ])
    if widget_key == "fill_in_blanks":
        parts.extend([
            "FillInBlanks requirements:",
            "- Create 5–7 sentences that form a SHORT connected narrative about a routine or daily activity.",
            "- Base the story's topic and characters on the learner's interests listed above.",
            "  Example: learner loves football → write about a footballer's morning routine;",
            "  learner loves movies → write about a film director's day.",
            "  If no specific interests are given, use a relatable everyday routine.",
            "- EVERY BlankItem MUST include `base_verb` (the bare infinitive, e.g. 'wake', 'prepare', 'eat').",
            "- Mix subjects deliberately: include at least one each of I / he or she / a proper name / they.",
            "- `correct_answer` is the correctly inflected simple-present form (base verb or +s/+es).",
            "- Include exactly 2 distractors per item (wrong inflections, e.g. 'wakes'/'waking' when correct is 'wake').",
            "- Items must read sequentially — together they tell one coherent story.",
        ])
    if widget_key == "listen_and_respond":
        parts.extend([
            "ListenAndRespond requirements:",
            "- `audio_script` must be a natural-sounding spoken passage (60-120 words) at the target CEFR level.",
            "- `inner_widget` must be 'mcq' unless widget_requirements specifies otherwise.",
            "- For MCQ: `items` list with item_id (q1, q2…), prompt, options (list of 4 strings), correct_index (0-based int), explanation.",
            "- For fill_in_blanks: include a `passage` with ___ markers and `items` with item_id, sentence_with_blank, base_verb, correct_answer, grammar_rule, and explanation.",
            "- Set `audio_url: null` — the backend synthesizes the audio from audio_script.",
        ])
    if archetype.archetype_id == "WRITE_OPEN_SENT":
        parts.extend([
            "OpenText writing requirements:",
            "- Generate exactly 3 items.",
            "- Item 1 asks for one affirmative routine sentence with I and a frequency adverb.",
            "- Item 2 asks for one affirmative routine sentence with he and a frequency adverb.",
            "- Item 3 asks for one affirmative routine sentence with she and a frequency adverb.",
            "- Each item must include item_id, prompt, sample_answer, and answer_hints.",
            "- Include grammar_rule_explained, common_mistakes, and target_words with frequency adverbs.",
        ])
    if archetype.archetype_id == "WRITE_ERROR_CORR" or archetype.ui_widget == "ErrorCorrection":
        parts.extend([
            "ErrorCorrection writing requirements:",
            "- Generate exactly 3 items.",
            "- Each item MUST contain item_id, incorrect_sentence, sample_answer, and watch_hints (a list of 1-4 short error labels like 'tense', 'agreement', 'infinitive form', 'double negatives').",
            "- Focus on the day's grammar topic (simple past tense regular/irregular verbs).",
            "- Set `task_intro` to a short imperative like 'Correct past tense mistakes.'",
        ])
    if archetype.archetype_id == "READ_ERROR_SPOT":
        parts.extend([
            "ErrorSpotting requirements:",
            "- Generate exactly 5 passage_sentences.",
            "- Each sentence must contain exactly 1 grammatical error token, so total_errors is exactly 5.",
            "- Tokenize every sentence into words/chunks with stable token_id values like s1_t1, s1_t2.",
            "- Mark only the clickable incorrect word/token with is_error: true; all other tokens use is_error: false.",
            "- Each sentence must include error.token_id, incorrect_phrase, correction, error_type, rule, and explanation.",
            "- Use at least four different error_type values from: irregular_past, missing_past_auxiliary, passive_helper_missing, time_marker_mismatch, object_or_complement_mismatch, past_participle_form, regular_past_ending.",
            "- Keep all mistakes connected to simple past meaning, but do not make them all regular verb + -ed errors.",
            "- Include diverse mistakes such as irregular past forms, did + base verb, passive helper missing, past time marker mismatch, and object/complement mismatch.",
        ])
    if archetype.archetype_id == "SPEAK_READ_ALOUD":
        parts.extend([
            "ReadAloud speaking requirements:",
            "- Generate a single connected narrative passage of 50-60 words in simple past tense (focusing on regular -ed verbs and irregular verbs).",
            "- Do NOT generate separate sentences or multiple items.",
            "- Populate `text_to_read_aloud` with this connected passage.",
            "- Set `task_intro` to 'Read the passage above out loud.'",
            "- Set `instructions` to 'Read the connected passage aloud clearly.'",
            "- Set `speaking_duration_seconds` to 45.",
            "- Do NOT generate `speaking_prompts` or multiple items - only use `text_to_read_aloud` for the passage.",
        ])
    parts.extend([
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
    return normalize_widget_key(ui_widget)


# ── System-prompt accessors ────────────────────────────────────────


def eval_system_prompt() -> str:
    return _EVAL_SYSTEM


def feedback_system_prompt() -> str:
    return _FEEDBACK_SYSTEM


def task_gen_system_prompt() -> str:
    return _TASK_GEN_SYSTEM
