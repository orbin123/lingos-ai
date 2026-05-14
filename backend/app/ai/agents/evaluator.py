"""Agent 2 — Evaluator Agent.

Scores a user's answer against an answer key. Returns a structured
evaluation report with per-question correctness and an overall score.

Rule-based for discrete tasks (fill-in-blanks, MCQ, etc.).
LLM-backed for open-ended writing tasks where correctness isn't binary.

This module is PURE: data in, data out. No DB, no commits.
Persistence happens in the service layer (responses/service.py).
"""

import json
import logging
from typing import Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Error taxonomy — keep it tiny for MVP.
# Add fancier labels (wrong_tense, subject_verb_disagreement, ...) later
# when we have grammar logic to detect them.
# ---------------------------------------------------------------------------
ErrorType = Literal[
    "correct",
    "missing_answer",
    "wrong_answer",
    "too_short",          # paraphrasing: answer is shorter than min_words
    "too_similar",        # paraphrasing: user copied the original
    "needs_review",       # paraphrasing: passed rule checks, needs LLM later
    "needs_ai_review",    # speaking: passed basic checks, needs LLM tense/grammar grading
    "false_positive",     # error_spotting: user flagged a correct sentence as wrong
    "false_negative",     # error_spotting: user marked an erroneous sentence as correct
    "wrong_error_type",   # error_spotting: verdict correct but error category wrong
]


# Activity types this evaluator knows how to score.
# Keep this list in sync with the dispatcher (`evaluate`) below.
SupportedActivity = Literal[
    "fill_in_the_blanks",
    "fill_in_blanks",
    "error_spotting",
    "sentence_transformation",
    "voice_conversion",
    "sentence_engineering",
    "paraphrasing",
    "error_correction",
    "speak_with_tense",
    "curriculum_grammar_listen_mcq",
    "curriculum_grammar_speak",
]


# ---------------------------------------------------------------------------
# Internal helpers (pure functions, no side effects)
# ---------------------------------------------------------------------------
def _normalize(text: str) -> str:
    """Lowercase + strip. The minimum needed so 'Went ' == 'went'.

    We intentionally do NOT strip punctuation or collapse spaces yet —
    FIB answers are short single words/phrases; over-normalizing would
    hide real errors (e.g. user writes 'is not' as 'isnt').
    """
    return text.strip().lower()


def _normalize_sentence(text: str) -> str:
    """Normalize a full sentence for comparison.

    Stronger than `_normalize` because for sentence engineering we want
    'She went to the market yesterday' to match 'she went to the market
    yesterday.' — same word order is what matters, NOT capitalization or
    a missing period (we still flag those in feedback later).

    Steps:
      1. lowercase + strip
      2. remove trailing punctuation (. ! ?)
      3. collapse multiple spaces into one
    """
    s = text.strip().lower()
    # Remove trailing sentence-ending punctuation
    while s.endswith((".", "!", "?")):
        s = s[:-1].rstrip()
    # Collapse internal whitespace
    return " ".join(s.split())


def _check_one(user_answer: str, correct_answer: str) -> dict:
    """Score ONE question. Returns the per-question dict.

    Shape matches what the Feedback Agent expects:
        {
          "correct": bool,
          "user_answer": str,        # original, NOT normalized — for display
          "correct_answer": str,
          "error_type": ErrorType,
        }
    """
    # Empty / whitespace-only → missing, not wrong.
    # Feedback should differ: "you didn't answer" vs "you answered, but wrong".
    if not user_answer.strip():
        return {
            "correct": False,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "error_type": "missing_answer",
        }

    is_correct = _normalize(user_answer) == _normalize(correct_answer)

    return {
        "correct": is_correct,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "error_type": "correct" if is_correct else "wrong_answer",
    }


def _score_paraphrase(
    *,
    user_answer: str,
    original: str,
    reference: str | None,
    min_words: int,
) -> dict:
    """Cheap rule-based paraphrase scoring.

    Returns a dict with the same fields as `_check_one` PLUS a numeric
    `score` in [0.0, 1.0]. The dispatcher uses `score` to compute the
    overall percentage; per-question display still uses `error_type`.

    Rules (in order):
      1. Empty            → missing_answer        score=0.0
      2. < min_words      → too_short             score=0.0
      3. Identical to src → too_similar           score=0.0
      4. Otherwise        → needs_review          score=0.7

    The 0.7 placeholder reflects "this passed cheap checks but a real
    grader has not seen it yet." When we add the LLM evaluator, this
    function is the ONLY thing that changes.
    """
    # `correct_answer` field shows the user a sample paraphrase if we have
    # one, otherwise the original sentence (less useful but never None).
    sample = reference or original

    # Rule 1: empty
    if not user_answer.strip():
        return {
            "correct": False,
            "user_answer": user_answer,
            "correct_answer": sample,
            "error_type": "missing_answer",
            "score": 0.0,
        }

    word_count = len(user_answer.strip().split())

    # Rule 2: too short
    if word_count < min_words:
        return {
            "correct": False,
            "user_answer": user_answer,
            "correct_answer": sample,
            "error_type": "too_short",
            "score": 0.0,
        }

    # Rule 3: copied the original (after light normalization)
    if _normalize_sentence(user_answer) == _normalize_sentence(original):
        return {
            "correct": False,
            "user_answer": user_answer,
            "correct_answer": sample,
            "error_type": "too_similar",
            "score": 0.0,
        }

    # Passed rule checks — needs a real grader to confirm semantic match.
    return {
        "correct": True,         # True = "accepted", not "perfect"
        "user_answer": user_answer,
        "correct_answer": sample,
        "error_type": "needs_review",
        "score": 0.7,
    }


# ---------------------------------------------------------------------------
# LLM output schemas — used ONLY by evaluate_open_text_writing
# ---------------------------------------------------------------------------

class _ItemWritingEval(BaseModel):
    """Per-item result from the LLM writing evaluator."""
    item_id: str
    mistakes: list[str] = Field(
        default_factory=list,
        description="Specific grammar mistakes found in this answer",
    )
    score: float = Field(..., ge=0.0, le=1.0, description="Item score 0-1")


class _OpenTextWritingEval(BaseModel):
    """Full LLM evaluation of a writing task."""
    subskill_score: int = Field(
        ..., ge=0, le=10,
        description="Grammar sub-skill score 0-10, calibrated to the learner's level",
    )
    items: list[_ItemWritingEval]
    main_mistakes: list[str] = Field(
        ...,
        description=(
            "Top 3-5 specific grammar mistakes across all answers. "
            "Each entry should quote the learner's phrase and name the rule violated. "
            "These are passed directly to the feedback agent."
        ),
    )
    overall_level: Literal["needs_work", "okay", "good", "excellent"]


class _GrammarSpeakingItemEval(BaseModel):
    """Per-prompt result from the LLM speaking evaluator."""

    item_id: str
    mistakes: list[str] = Field(
        default_factory=list,
        description="Specific grammar mistakes found in the transcript",
    )
    score: float = Field(..., ge=0.0, le=1.0, description="Prompt score 0-1")
    grammar_rule_used: bool = Field(
        ..., description="Whether the target grammar rule was used meaningfully"
    )


class _GrammarSpeakingEval(BaseModel):
    """Full LLM evaluation of a grammar speaking task."""

    subskill_score: int = Field(
        ..., ge=0, le=10,
        description="Grammar speaking score 0-10, calibrated to the learner's level",
    )
    items: list[_GrammarSpeakingItemEval]
    main_mistakes: list[str] = Field(
        ...,
        description="Top 3-5 specific grammar mistakes across all transcripts",
    )
    overall_level: Literal["needs_work", "okay", "good", "excellent"]


_OPEN_TEXT_EVAL_SYSTEM = """\
You are an expert English grammar evaluator assessing a non-native learner's writing.

EVALUATION RULES
1. Focus exclusively on whether the learner correctly applied the grammar rule being practiced.
2. Calibrate grading to the learner's level (provided as X/10):
   - Beginner (1-3): be lenient with style and vocabulary; grade primarily on core rule application.
   - Intermediate (4-6): grade on rule accuracy + sentence structure.
   - Advanced (7-10): grade on rule accuracy + structure + naturalness.
3. subskill_score (0-10) must reflect: accuracy of grammar rule application × level expectations.
   A beginner making 1 mistake on a 3-item task might score 6/10; an advanced learner the same score 4/10.
4. main_mistakes: list 3-5 SPECIFIC mistakes, quoting the learner's exact phrase.
   Example: "Missing -s on third-person verb: 'he go' → should be 'he goes'"
5. Per item: list concrete mistakes only for that answer; empty list if the answer is correct.
6. Never penalize for spelling errors unless they change meaning.

Return JSON matching the schema. Nothing else.
"""


_GRAMMAR_SPEAKING_EVAL_SYSTEM = """\
You are an expert English grammar speaking evaluator.

Evaluate the learner's speech transcripts for the target grammar rule only.
Do not grade accent harshly. Do grade whether the learner actually used the
requested grammar structure, whether forms are correct, and whether the answer
completed the prompt.

Return JSON matching the schema. Nothing else.
"""


def _format_evaluation_focus_block(
    evaluation_focus: dict | None,
) -> str:
    """Render the Planner's evaluation_focus as a prompt block, or empty."""
    if not evaluation_focus:
        return ""
    lines = [
        "PLANNER EVALUATION FOCUS (apply over the generic level rules above):",
    ]
    focus_areas = evaluation_focus.get("focus_areas")
    if isinstance(focus_areas, list) and focus_areas:
        lines.append(
            "- focus_areas: " + ", ".join(str(f) for f in focus_areas if str(f).strip())
        )
    for key in ("level_note", "scoring_instruction"):
        value = evaluation_focus.get(key)
        if isinstance(value, str) and value.strip():
            lines.append(f"- {key}: {value.strip()}")
    return "\n".join(lines)


def _build_open_text_user_message(
    *,
    task_content: dict,
    user_answers: dict,
    user_level: int,
    learner_profile: dict,
    evaluation_focus: dict | None = None,
) -> str:
    """Format the writing task evaluation prompt."""
    tier = (
        "Beginner (1-3)" if user_level <= 3
        else "Intermediate (4-6)" if user_level <= 6
        else "Advanced (7-10)"
    )
    self_assessed = learner_profile.get("self_assessed_level", "unknown")

    grammar_rule = task_content.get("grammar_rule_explained", "See task instructions")
    common_mistakes = task_content.get("common_mistakes") or []
    common_text = (
        "\n".join(f"- {m}" for m in common_mistakes)
        if common_mistakes
        else "None specified"
    )

    items = task_content.get("items") or []
    items_lines: list[str] = []
    for idx, item in enumerate(items, 1):
        item_id = item.get("item_id", f"item_{idx}")
        prompt = item.get("prompt", "")
        sample = item.get("sample_answer", "")
        user_ans = user_answers.get(item_id, "").strip()
        items_lines.append(
            f"Item {idx} (id={item_id})\n"
            f"  Prompt: {prompt}\n"
            f"  Sample answer: {sample}\n"
            f"  Learner's answer: {user_ans if user_ans else '[no answer]'}"
        )
    items_text = "\n\n".join(items_lines)

    focus_block = _format_evaluation_focus_block(evaluation_focus)
    focus_section = f"{focus_block}\n\n" if focus_block else ""
    return (
        f"LEARNER LEVEL: {user_level}/10 ({tier})\n"
        f"SELF-ASSESSED: {self_assessed}\n\n"
        f"{focus_section}"
        f"GRAMMAR RULE BEING PRACTICED:\n{grammar_rule}\n\n"
        f"COMMON MISTAKES TO WATCH FOR:\n{common_text}\n\n"
        f"TASK ITEMS AND ANSWERS:\n{items_text}\n\n"
        "Evaluate the learner's writing. Return your assessment."
    )


def _prompt_id(index: int) -> str:
    return f"prompt_{index}"


def _grammar_speaking_recordings_by_id(user_answers: dict) -> dict[str, dict]:
    recordings = user_answers.get("recordings") or []
    if not isinstance(recordings, list):
        return {}

    by_id: dict[str, dict] = {}
    for idx, recording in enumerate(recordings, 1):
        if not isinstance(recording, dict):
            continue
        item_id = str(recording.get("item_id") or _prompt_id(idx))
        by_id[item_id] = recording
    return by_id


def _build_grammar_speaking_user_message(
    *,
    task_content: dict,
    user_answers: dict,
    user_level: int,
    learner_profile: dict,
    evaluation_focus: dict | None = None,
) -> str:
    """Format the grammar speaking task evaluation prompt."""
    tier = (
        "Beginner (1-3)" if user_level <= 3
        else "Intermediate (4-6)" if user_level <= 6
        else "Advanced (7-10)"
    )
    recordings_by_id = _grammar_speaking_recordings_by_id(user_answers)
    prompts = task_content.get("speaking_prompts") or []
    samples = task_content.get("sample_responses") or []

    items: list[dict] = []
    for idx, prompt in enumerate(prompts, 1):
        item_id = _prompt_id(idx)
        recording = recordings_by_id.get(item_id, {})
        items.append(
            {
                "item_id": item_id,
                "prompt": prompt,
                "sample_response": samples[idx - 1] if idx - 1 < len(samples) else "",
                "transcript": recording.get("transcript", ""),
                "duration_seconds": recording.get("duration_seconds"),
            }
        )

    focus_block = _format_evaluation_focus_block(evaluation_focus)
    focus_section = f"{focus_block}\n\n" if focus_block else ""
    return f"""\
LEARNER LEVEL: {user_level}/10 ({tier})
SELF-ASSESSED: {learner_profile.get("self_assessed_level", "unknown")}

{focus_section}TARGET GRAMMAR RULE:
{task_content.get("grammar_rule_to_practice") or task_content.get("topic_name") or "See task topic"}

TASK INSTRUCTIONS:
{task_content.get("instructions", "")}

PROMPTS, SAMPLE RESPONSES, AND TRANSCRIPTS:
{json.dumps(items, indent=2)}

Evaluate each transcript. Penalize missing transcripts, not using the target
grammar rule, incorrect forms, and answers that do not address the prompt.
Return your assessment.
"""


# ---------------------------------------------------------------------------
# Public agent class
# ---------------------------------------------------------------------------
class EvaluationService:
    """Rule-based evaluator for fill-in-the-blanks tasks.

    Pure logic, no DB. The service layer (responses/service.py) calls
    `evaluate_fill_in_blanks(...)` and persists the returned dict into
    the Evaluation row.

    Why a class (not plain functions)? Future evaluators (writing,
    speaking) may need shared state — e.g. a cached LLM client, an
    Azure Speech client, prompt templates. Keeping the class form now
    means we can add `evaluate_writing(...)`, `evaluate_speaking(...)`
    methods alongside without changing existing callers.
    """

    def evaluate_fill_in_blanks(
        self,
        *,
        task_content: dict,
        user_answers: dict,
    ) -> dict:
        """Score a fill-in-the-blanks submission.

        Args:
            task_content: The Task.content JSONB. Expected to contain an
                `activities` list with at least one fill_in_the_blanks
                activity that has an `answers` key.
            user_answers: Flat dict {"Q1": "went", "Q2": "has", ...}
                — same shape as UserResponse.content.

        Returns:
            Evaluation report dict — see shape at end of method.
        """
        answer_key = self._extract_answer_key(task_content)

        per_question: dict[str, dict] = {}
        correct_count = 0

        # Loop over the ANSWER KEY, not user_answers.
        # Why? If the user skipped Q3 entirely, we still want it in the
        # report as 'missing_answer'. Looping over user_answers would
        # silently drop unanswered questions.
        for qid, correct in answer_key.items():
            user_ans = user_answers.get(qid, "")  # missing → empty string
            result = _check_one(user_ans, correct)
            per_question[qid] = result
            if result["correct"]:
                correct_count += 1

        total = len(answer_key)
        # Guard against divide-by-zero on a malformed task with 0 questions
        percentage = round((correct_count / total) * 100, 2) if total else 0.0

        return {
            "task_type": "fill_in_the_blanks",
            "total": total,
            "correct_count": correct_count,
            "percentage": percentage,
            "questions": per_question,
        }

    @staticmethod
    def _extract_answer_key(task_content: dict) -> dict[str, str]:
        """Find the FIB activity in task_content and return its answers.

        Task content shape (from seed files):
            {
              "activities": [
                {"activity_type": "fill_in_the_blanks", "answers": {...}, ...},
                {"activity_type": "mcq", ...},
              ]
            }

        Raises:
            ValueError: if no fill_in_the_blanks activity is found.
        """
        for activity in task_content.get("activities", []):
            if activity.get("activity_type") == "fill_in_the_blanks":
                return activity["answers"]
        raise ValueError(
            "task_content has no fill_in_the_blanks activity"
        )

    # ------------------------------------------------------------------
    # Sentence engineering — string match against the canonical answer.
    # ------------------------------------------------------------------
    def evaluate_sentence_engineering(
        self,
        *,
        task_content: dict,
        user_answers: dict,
    ) -> dict:
        """Score a sentence-engineering submission.

        Same pattern as FIB but uses `_normalize_sentence` so a missing
        period or wrong capitalization does not count as wrong — the
        user got the WORD ORDER right, which is what this activity
        teaches.

        Returns the same report shape as FIB so the Feedback Agent and
        the score updater don't need a special branch.
        """
        activity = self._find_activity(task_content, "sentence_engineering")
        answer_key: dict[str, str] = activity["answers"]

        per_question: dict[str, dict] = {}
        correct_count = 0

        for qid, correct in answer_key.items():
            user_ans = user_answers.get(qid, "")

            if not user_ans.strip():
                per_question[qid] = {
                    "correct": False,
                    "user_answer": user_ans,
                    "correct_answer": correct,
                    "error_type": "missing_answer",
                }
                continue

            is_correct = (
                _normalize_sentence(user_ans) == _normalize_sentence(correct)
            )
            per_question[qid] = {
                "correct": is_correct,
                "user_answer": user_ans,
                "correct_answer": correct,
                "error_type": "correct" if is_correct else "wrong_answer",
            }
            if is_correct:
                correct_count += 1

        total = len(answer_key)
        percentage = round((correct_count / total) * 100, 2) if total else 0.0

        return {
            "task_type": "sentence_engineering",
            "total": total,
            "correct_count": correct_count,
            "percentage": percentage,
            "questions": per_question,
        }

    # ------------------------------------------------------------------
    # Paraphrasing — STUB grader.
    #
    # No single correct answer exists for paraphrasing. A real grader
    # would call an LLM to score semantic similarity + grammar. Today we
    # ship cheap rule-based checks so the loop works end-to-end:
    #
    #   - empty            → missing_answer        (0%)
    #   - too short        → too_short             (0%)
    #   - identical to src → too_similar           (0%)
    #   - otherwise        → needs_review          (70% placeholder)
    #
    # TODO(post-MVP): replace `_score_paraphrase` with an LLM call.
    # The dispatcher signature stays the same so callers don't change.
    # ------------------------------------------------------------------
    def evaluate_paraphrasing(
        self,
        *,
        task_content: dict,
        user_answers: dict,
    ) -> dict:
        """Score a paraphrasing submission with rule-based heuristics."""
        activity = self._find_activity(task_content, "paraphrasing")
        originals: dict[str, str] = activity["questions"]
        references: dict[str, str] = activity.get("reference_answers", {})
        min_words: int = int(activity.get("min_words", 4))

        per_question: dict[str, dict] = {}
        score_sum = 0.0

        for qid, original in originals.items():
            user_ans = user_answers.get(qid, "")
            result = _score_paraphrase(
                user_answer=user_ans,
                original=original,
                reference=references.get(qid),
                min_words=min_words,
            )
            per_question[qid] = result
            score_sum += result["score"]

        total = len(originals)
        # `score` is 0.0..1.0 per question. Average → percentage.
        percentage = round((score_sum / total) * 100, 2) if total else 0.0
        # `correct_count` for paraphrasing means "passed all rule checks"
        correct_count = sum(
            1 for r in per_question.values() if r["score"] >= 0.7
        )

        return {
            "task_type": "paraphrasing",
            "total": total,
            "correct_count": correct_count,
            "percentage": percentage,
            "questions": per_question,
        }

    # ------------------------------------------------------------------
    # Generated fill-in-blanks — reads content.blanks[], not activities[]
    # ------------------------------------------------------------------
    def evaluate_generated_fill_in_blanks(
        self,
        *,
        task_content: dict,
        user_answers: dict,
    ) -> dict:
        """Score an LLM-generated fill-in-blanks task.

        Generated tasks have a different content shape from seeded tasks:

            SEEDED:    content["activities"][0]["answers"] = {"Q1": "went", ...}
            GENERATED: content["blanks"] = [
                           {"blank_id": "b1", "correct_answer": "went", ...},
                           ...
                       ]

        The user submits answers keyed by blank_id:
            user_answers = {"b1": "went", "b2": "has"}
        """
        blanks: list[dict] = task_content.get("blanks") or task_content.get("items", [])
        if not blanks:
            raise ValueError(
                "Generated fill_in_blanks task has no 'blanks' or 'items' in content"
            )

        per_question: dict[str, dict] = {}
        correct_count = 0

        for blank in blanks:
            bid = blank.get("blank_id") or blank["item_id"]
            correct = blank["correct_answer"]
            user_ans = user_answers.get(bid, "")
            result = _check_one(user_ans, correct)
            # Also store the grammar_rule so the feedback agent can use it
            result["grammar_rule"] = (
                blank.get("grammar_rule")
                or task_content.get("grammar_rule_explained")
                or ""
            )
            result["sentence"] = blank.get("sentence_with_blank", "")
            per_question[bid] = result
            if result["correct"]:
                correct_count += 1

        total = len(blanks)
        percentage = round((correct_count / total) * 100, 2) if total else 0.0

        return {
            "task_type": "fill_in_blanks",
            "total": total,
            "correct_count": correct_count,
            "percentage": percentage,
            "questions": per_question,
        }

    # ------------------------------------------------------------------
    # Sentence transformation — stub grader (open-ended writing)
    #
    # Real grading needs an LLM to check structure match + grammar.
    # Today we ship the same cheap rule-based checks as paraphrasing so
    # the full loop works end-to-end without blocking on the LLM evaluator:
    #
    #   - empty                    → missing_answer        (0%)
    #   - too short (< 4 words)    → too_short             (0%)
    #   - identical to original    → too_similar           (0%)
    #   - otherwise                → needs_review          (70% placeholder)
    #
    # TODO(post-MVP): replace the stub with an LLM evaluator that checks:
    #   - transformation_target was applied (make_complex, add_relative_clause, etc.)
    #   - expected_pattern was followed
    #   - grammar is correct
    # The dispatcher signature stays the same so callers don't change.
    # ------------------------------------------------------------------
    def evaluate_sentence_transformation(
        self,
        *,
        task_content: dict,
        user_answers: dict,
    ) -> dict:
        """Score a generated sentence-transformation task.

        Content shape (from SentenceTransformationTask Pydantic model):
            {
              "items": [
                {
                  "item_id": "item_1",
                  "original_sentence": "He was tired.",
                  "transformation_target": "make_complex",
                  "expected_pattern": "Although/Because + clause",
                  "sample_correct_answer": "Although he was tired, he finished the work.",
                  "grading_criteria": [...]
                },
                ...
              ]
            }

        User answer shape (from GeneratedSentenceTransformation.tsx):
            { "item_1": "Although he was tired, he finished the work.", ... }

        Scoring per item (max 1.0 point each):
            - Empty                      → 0.0  (missing_answer)
            - Fewer than 4 words         → 0.0  (too_short)
            - Identical to original      → 0.0  (too_similar)
            - Otherwise                  → 0.7  (needs_review)
        """
        items: list[dict] = task_content.get("items", [])
        if not items:
            raise ValueError(
                "Generated sentence_transformation task has no 'items' in content"
            )

        per_question: dict[str, dict] = {}
        score_sum = 0.0

        for item in items:
            iid = item["item_id"]
            original = item.get("original_sentence", "")
            sample = item.get("sample_correct_answer", original)
            user_ans = user_answers.get(iid, "")

            result = _score_paraphrase(
                user_answer=user_ans,
                original=original,
                reference=sample,
                min_words=4,
            )
            # Attach transformation metadata so the feedback agent can
            # reference the target and expected pattern.
            result["transformation_target"] = item.get("transformation_target", "")
            result["expected_pattern"] = item.get("expected_pattern", "")
            result["grading_criteria"] = item.get("grading_criteria", [])
            result["original_sentence"] = original

            per_question[iid] = result
            score_sum += result["score"]

        total = len(items)
        percentage = round((score_sum / total) * 100, 2) if total else 0.0
        correct_count = sum(
            1 for r in per_question.values() if r["score"] >= 0.7
        )

        return {
            "task_type": "sentence_transformation",
            "total": total,
            "correct_count": correct_count,
            "percentage": percentage,
            "questions": per_question,
        }

    # ------------------------------------------------------------------
    # Voice conversion — exact match with sentence normalization
    #
    # Each item has a `correct_answer` field, so we can do a real
    # deterministic check — no stub needed. We use `_normalize_sentence`
    # (strip trailing punctuation + lowercase + collapse spaces) so that
    # "The letter was written by John" matches "the letter was written by john."
    # ------------------------------------------------------------------
    def evaluate_voice_conversion(
        self,
        *,
        task_content: dict,
        user_answers: dict,
    ) -> dict:
        """Score a generated voice-conversion task.

        Content shape (from VoiceConversionTask Pydantic model):
            {
              "items": [
                {
                  "item_id": "item_1",
                  "original_sentence": "John wrote the letter.",
                  "direction": "active_to_passive",
                  "correct_answer": "The letter was written by John.",
                  "common_mistake": "..."
                },
                ...
              ]
            }

        User answer shape (from GeneratedVoiceConversion.tsx):
            { "item_1": "The letter was written by John.", ... }

        Scoring per item (max 1.0 each):
            - Empty                                         → 0.0  (missing_answer)
            - Normalised match with correct_answer          → 1.0  (correct)
            - Non-empty but doesn’t match                  → 0.0  (wrong_answer)
        """
        items: list[dict] = task_content.get("items", [])
        if not items:
            raise ValueError(
                "Generated voice_conversion task has no 'items' in content"
            )

        per_question: dict[str, dict] = {}
        correct_count = 0

        for item in items:
            iid = item["item_id"]
            correct = item.get("correct_answer", "")
            user_ans = user_answers.get(iid, "")

            if not user_ans.strip():
                per_question[iid] = {
                    "correct": False,
                    "user_answer": user_ans,
                    "correct_answer": correct,
                    "error_type": "missing_answer",
                    "score": 0.0,
                    "direction": item.get("direction", ""),
                    "original_sentence": item.get("original_sentence", ""),
                    "common_mistake": item.get("common_mistake"),
                }
                continue

            is_correct = (
                _normalize_sentence(user_ans) == _normalize_sentence(correct)
            )
            per_question[iid] = {
                "correct": is_correct,
                "user_answer": user_ans,
                "correct_answer": correct,
                "error_type": "correct" if is_correct else "wrong_answer",
                "score": 1.0 if is_correct else 0.0,
                "direction": item.get("direction", ""),
                "original_sentence": item.get("original_sentence", ""),
                "common_mistake": item.get("common_mistake"),
            }
            if is_correct:
                correct_count += 1

        total = len(items)
        percentage = round((correct_count / total) * 100, 2) if total else 0.0

        return {
            "task_type": "voice_conversion",
            "total": total,
            "correct_count": correct_count,
            "percentage": percentage,
            "questions": per_question,
        }

    # ------------------------------------------------------------------
    # Error correction — exact match with sentence normalization
    #
    # Each item provides an `incorrect_sentence` the learner must fix
    # and a `correct_sentence` as the answer key. We use
    # `_normalize_sentence` so differences in capitalization and trailing
    # punctuation (., !, ?) don't count against the learner.
    #
    # Note: `error_type` in the result dict is the standard evaluation
    # verdict ("correct" / "missing_answer" / "wrong_answer"). The
    # grammar category from the item is stored under `item_error_type`
    # to avoid a name clash.
    # ------------------------------------------------------------------
    def evaluate_error_correction(
        self,
        *,
        task_content: dict,
        user_answers: dict,
    ) -> dict:
        """Score a generated error-correction task.

        Content shape (from ErrorCorrectionTask Pydantic model):
            {
              "items": [
                {
                  "item_id": "item_1",
                  "incorrect_sentence": "She don't likes apples.",
                  "correct_sentence": "She doesn't like apples.",
                  "error_type": "subject_verb_agreement",
                  "explanation": "After 'doesn't', the verb stays in base form."
                },
                ...
              ]
            }

        User answer shape (from GeneratedErrorCorrection.tsx):
            { "item_1": "She doesn't like apples.", ... }

        Scoring per item (max 1.0 each):
            - Empty answer                              → 0.0  (missing_answer)
            - Normalised match with correct_sentence    → 1.0  (correct)
            - Non-empty but doesn't match               → 0.0  (wrong_answer)
        """
        items: list[dict] = task_content.get("items", [])
        if not items:
            raise ValueError(
                "Generated error_correction task has no 'items' in content"
            )

        per_question: dict[str, dict] = {}
        correct_count = 0

        for item in items:
            iid = item["item_id"]
            correct = item.get("correct_sentence", "")
            user_ans = user_answers.get(iid, "")

            if not user_ans.strip():
                per_question[iid] = {
                    "correct": False,
                    "user_answer": user_ans,
                    "correct_answer": correct,
                    "error_type": "missing_answer",
                    "score": 0.0,
                    "incorrect_sentence": item.get("incorrect_sentence", ""),
                    "item_error_type": item.get("error_type", ""),
                    "explanation": item.get("explanation", ""),
                }
                continue

            is_correct = (
                _normalize_sentence(user_ans) == _normalize_sentence(correct)
            )
            per_question[iid] = {
                "correct": is_correct,
                "user_answer": user_ans,
                "correct_answer": correct,
                "error_type": "correct" if is_correct else "wrong_answer",
                "score": 1.0 if is_correct else 0.0,
                "incorrect_sentence": item.get("incorrect_sentence", ""),
                "item_error_type": item.get("error_type", ""),
                "explanation": item.get("explanation", ""),
            }
            if is_correct:
                correct_count += 1

        total = len(items)
        percentage = round((correct_count / total) * 100, 2) if total else 0.0

        return {
            "task_type": "error_correction",
            "total": total,
            "correct_count": correct_count,
            "percentage": percentage,
            "questions": per_question,
        }

    # ------------------------------------------------------------------
    # Error spotting — 0.5 pts for verdict + 0.5 pts for error_type
    # ------------------------------------------------------------------
    def evaluate_error_spotting(
        self,
        *,
        task_content: dict,
        user_answers: dict,
    ) -> dict:
        """Score a generated error-spotting task.

        Content shape (from ErrorSpottingTask Pydantic model):
            {
              "sentences": [
                {
                  "sentence_id": "s1",
                  "sentence": "She go to school every day.",
                  "has_error": true,
                  "error_type": "present_simple",
                  "incorrect_phrase": "go",
                  "correction": "goes",
                  "explanation": "..."
                },
                ...
              ],
              "total_with_errors": 4,
              ...
            }

        User answer shape (from GeneratedErrorSpotting.tsx):
            {
              "s1": "present_simple",   # user said has_error + picked type
              "s2": "correct",          # user said this sentence is correct
              ...
            }

        Scoring per sentence (max 1.0 point each):
            - Sentence has no error AND user says "correct"      → 1.0
            - Sentence has error  AND user picks correct type    → 1.0
            - Sentence has error  AND user picks wrong type      → 0.5
              (got the verdict right, missed the category)
            - Any other mismatch (false positive / false negative) → 0.0
        """
        sentences: list[dict] = task_content.get("sentences", [])
        if not sentences:
            raise ValueError(
                "Generated error_spotting task has no 'sentences' in content"
            )

        per_question: dict[str, dict] = {}
        score_sum = 0.0

        for sent in sentences:
            sid = sent["sentence_id"]
            has_error: bool = sent.get("has_error", False)
            correct_type: str | None = sent.get("error_type")  # None when has_error=False
            user_ans: str = user_answers.get(sid, "").strip()

            # Build the canonical "correct answer" label shown in feedback.
            # For error-free sentences, "correct" is the right answer.
            # For erroneous sentences, the right answer is the error type.
            expected_label = "correct" if not has_error else (correct_type or "unknown")

            if not user_ans:
                # User did not answer this sentence at all
                per_question[sid] = {
                    "correct": False,
                    "user_answer": user_ans,
                    "correct_answer": expected_label,
                    "grammar_rule": correct_type,
                    "error_type": "missing_answer",
                    "error_classification": "missing_answer",
                    "score": 0.0,
                    # Pass through the sentence data so the feedback agent
                    # can reference the original text and explanation.
                    "sentence": sent.get("sentence", ""),
                    "incorrect_phrase": sent.get("incorrect_phrase"),
                    "correction": sent.get("correction"),
                    "explanation": sent.get("explanation"),
                }
                continue

            user_said_correct = (user_ans == "correct")

            if not has_error:
                # Sentence is actually correct
                if user_said_correct:
                    q_score = 1.0
                    q_correct = True
                    q_error_type = "correct"
                else:
                    # False positive — user flagged an error that doesn't exist
                    q_score = 0.0
                    q_correct = False
                    q_error_type = "false_positive"
            else:
                # Sentence has a real error
                if user_said_correct:
                    # False negative — user missed the error entirely
                    q_score = 0.0
                    q_correct = False
                    q_error_type = "false_negative"
                elif user_ans == correct_type:
                    # Correct verdict AND correct error type → full marks
                    q_score = 1.0
                    q_correct = True
                    q_error_type = "correct"
                else:
                    # Correct verdict but wrong error type → half marks
                    q_score = 0.5
                    q_correct = False
                    q_error_type = "wrong_error_type"

            per_question[sid] = {
                "correct": q_correct,
                "user_answer": user_ans,
                "correct_answer": expected_label,
                "grammar_rule": correct_type,
                "error_type": q_error_type,
                "error_classification": q_error_type,
                "score": q_score,
                "sentence": sent.get("sentence", ""),
                "incorrect_phrase": sent.get("incorrect_phrase"),
                "correction": sent.get("correction"),
                "explanation": sent.get("explanation"),
            }
            score_sum += q_score

        total = len(sentences)
        # Each sentence is worth 1.0 max, so percentage = (sum / total) * 100
        percentage = round((score_sum / total) * 100, 2) if total else 0.0
        # "correct" means full marks on that sentence (score == 1.0)
        correct_count = sum(
            1 for r in per_question.values() if r["score"] == 1.0
        )

        return {
            "task_type": "error_spotting",
            "total": total,
            "correct_count": correct_count,
            "percentage": percentage,
            "questions": per_question,
        }

    # ------------------------------------------------------------------
    # Speak with tense — stub evaluator (sentence-count heuristic)
    #
    # A real tense-usage grader needs an LLM to check whether the learner
    # actually used the target tense and whether the grammar is correct.
    # Today we ship cheap rule-based sentence counting so the full loop
    # works end-to-end without blocking on the LLM evaluator:
    #
    #   - empty transcript          → missing_answer        (0.0)
    #   - < minimum_sentences       → too_short             (0.3)
    #   - >= minimum_sentences      → needs_ai_review       (0.7)
    #
    # TODO(post-MVP): replace stub with an LLM call that checks:
    #   - target tense was used correctly
    #   - grammar accuracy and fluency
    # The dispatcher signature stays the same so callers don't change.
    # ------------------------------------------------------------------
    def evaluate_speak_with_tense(
        self,
        *,
        task_content: dict,
        user_answers: dict,
    ) -> dict:
        """Score a generated speak-with-tense submission.

        Content shape (from SpeakWithTenseTask Pydantic model):
            {
              "target_tense": "past_simple",
              "speaking_prompt": "Tell me about your last weekend.",
              "minimum_duration_seconds": 60,
              "minimum_sentences": 4,
              "grading_criteria": ["uses past simple", ...],
              "sample_response": "Last weekend I visited..."
            }

        User answer shape (from SpeakAndRecord component):
            {
              "transcript": "Last weekend I visited my grandmother...",
              "duration_seconds": 65,
              "audio_url": "/audio/user-recordings/abc123.webm"
            }

        Scoring:
            - Empty transcript         → 0.0  (missing_answer)
            - < minimum_sentences      → 0.3  (too_short)
            - >= minimum_sentences     → 0.7  (needs_ai_review)
        """
        transcript: str = str(user_answers.get("transcript", "")).strip()
        duration: float | None = user_answers.get("duration_seconds")
        minimum_sentences: int = int(task_content.get("minimum_sentences", 4))

        # Count sentences by splitting on terminal punctuation.
        # Filter fragments shorter than 3 chars (catch "..." or lone "?").
        if transcript:
            import re
            raw_fragments = re.split(r"[.!?]+", transcript)
            sentence_count = sum(
                1 for f in raw_fragments if f.strip() and len(f.strip()) >= 3
            )
        else:
            sentence_count = 0

        base = {
            "user_answer": transcript,
            "correct_answer": None,
            "target_tense": task_content.get("target_tense", ""),
            "speaking_prompt": task_content.get("speaking_prompt", ""),
            "minimum_sentences": minimum_sentences,
            "sentence_count": sentence_count,
            "duration_seconds": duration,
            "grading_criteria": task_content.get("grading_criteria", []),
            "sample_response": task_content.get("sample_response", ""),
        }

        if not transcript:
            result = {
                **base,
                "correct": False,
                "score": 0.0,
                "error_type": "missing_answer",
            }
            percentage = 0.0
            correct_count = 0
        elif sentence_count < minimum_sentences:
            result = {
                **base,
                "correct": False,
                "score": 0.3,
                "error_type": "too_short",
            }
            percentage = 30.0
            correct_count = 0
        else:
            result = {
                **base,
                "correct": True,
                "score": 0.7,
                "error_type": "needs_ai_review",
            }
            percentage = 70.0
            correct_count = 1

        return {
            "task_type": "speak_with_tense",
            "total": 1,
            "correct_count": correct_count,
            "percentage": percentage,
            "questions": {"speaking_response": result},
        }

    # ------------------------------------------------------------------
    # Curriculum grammar listen — listen_and_respond with inner MCQ.
    # ------------------------------------------------------------------
    def evaluate_curriculum_grammar_listen_mcq(
        self,
        *,
        task_content: dict,
        user_answers: dict,
    ) -> dict:
        """Score the MCQ response inside a grammar listening task."""
        items: list[dict] = task_content.get("items") or []
        if not items:
            raise ValueError("Grammar listen task has no MCQ items")

        inner_response = user_answers.get("inner_response") or {}
        if not isinstance(inner_response, dict):
            inner_response = {}
        answer_rows = inner_response.get("answers") or user_answers.get("answers") or []
        selected_by_id: dict[str, int] = {}
        if isinstance(answer_rows, list):
            for row in answer_rows:
                if not isinstance(row, dict):
                    continue
                item_id = str(row.get("item_id") or "")
                try:
                    selected_by_id[item_id] = int(row.get("selected_index"))
                except (TypeError, ValueError):
                    continue

        per_question: dict[str, dict] = {}
        correct_count = 0

        for idx, item in enumerate(items, 1):
            item_id = str(item.get("item_id") or f"item_{idx}")
            options = item.get("options") or []
            correct_index = int(item.get("correct_index", -1))
            selected_index = selected_by_id.get(item_id)
            selected_valid = (
                selected_index is not None
                and 0 <= selected_index < len(options)
            )
            correct_valid = 0 <= correct_index < len(options)
            is_correct = (
                selected_valid
                and correct_valid
                and selected_index == correct_index
            )
            if is_correct:
                correct_count += 1

            per_question[item_id] = {
                "correct": is_correct,
                "user_answer": options[selected_index] if selected_valid else "",
                "correct_answer": options[correct_index] if correct_valid else "",
                "selected_index": selected_index,
                "correct_index": correct_index,
                "prompt": item.get("prompt", ""),
                "explanation": item.get("explanation", ""),
                "error_type": (
                    "correct"
                    if is_correct
                    else "wrong_answer"
                    if selected_valid
                    else "missing_answer"
                ),
            }

        total = len(items)
        percentage = round((correct_count / total) * 100, 2) if total else 0.0
        return {
            "task_type": "curriculum_grammar_listen_mcq",
            "total": total,
            "correct_count": correct_count,
            "percentage": percentage,
            "listen_analytics": user_answers.get("listen_analytics") or {},
            "questions": per_question,
        }

    # ------------------------------------------------------------------
    # Curriculum grammar speak — LLM-backed transcript evaluation.
    # ------------------------------------------------------------------
    async def evaluate_grammar_speaking(
        self,
        *,
        task_content: dict,
        user_answers: dict,
        user_level: int = 5,
        learner_profile: dict | None = None,
        evaluation_focus: dict | None = None,
    ) -> dict:
        """Evaluate grammar speaking transcripts with the LLM."""
        prompts = task_content.get("speaking_prompts") or []
        if not prompts:
            raise ValueError("Grammar speak task has no speaking prompts")

        recordings_by_id = _grammar_speaking_recordings_by_id(user_answers)
        has_any_transcript = any(
            str(recording.get("transcript") or "").strip()
            for recording in recordings_by_id.values()
        )

        if not has_any_transcript:
            questions = {
                _prompt_id(idx): {
                    "correct": False,
                    "user_answer": "",
                    "correct_answer": "",
                    "prompt": prompt,
                    "grammar_rule_to_practice": task_content.get(
                        "grammar_rule_to_practice", ""
                    ),
                    "duration_seconds": 0,
                    "mistakes": ["No speech transcript was submitted."],
                    "score": 0.0,
                    "error_type": "missing_answer",
                }
                for idx, prompt in enumerate(prompts, 1)
            }
            return {
                "task_type": "curriculum_grammar_speak",
                "total": len(prompts),
                "correct_count": 0,
                "percentage": 0.0,
                "subskill_score": 0,
                "main_mistakes": ["No speech transcript was submitted."],
                "overall_level": "needs_work",
                "questions": questions,
            }

        from app.ai.llm import get_default_llm_client

        client = get_default_llm_client()
        llm_result = await client.generate_structured(
            system_prompt=_GRAMMAR_SPEAKING_EVAL_SYSTEM,
            user_prompt=_build_grammar_speaking_user_message(
                task_content=task_content,
                user_answers=user_answers,
                user_level=user_level,
                learner_profile=learner_profile or {},
                evaluation_focus=evaluation_focus,
            ),
            output_model=_GrammarSpeakingEval,
            temperature=0.2,
        )

        item_eval_by_id = {item.item_id: item for item in llm_result.items}
        samples = task_content.get("sample_responses") or []
        questions: dict[str, dict] = {}
        correct_count = 0

        for idx, prompt in enumerate(prompts, 1):
            item_id = _prompt_id(idx)
            recording = recordings_by_id.get(item_id, {})
            transcript = str(recording.get("transcript") or "").strip()
            ev = item_eval_by_id.get(item_id)
            score = ev.score if ev is not None else (0.0 if not transcript else 0.5)
            mistakes = ev.mistakes if ev is not None else []
            is_correct = bool(transcript) and score >= 0.6
            if is_correct:
                correct_count += 1

            questions[item_id] = {
                "correct": is_correct,
                "user_answer": transcript,
                "correct_answer": samples[idx - 1] if idx - 1 < len(samples) else "",
                "prompt": prompt,
                "grammar_rule_to_practice": task_content.get(
                    "grammar_rule_to_practice", ""
                ),
                "duration_seconds": recording.get("duration_seconds"),
                "audio_url": recording.get("audio_blob_url"),
                "mistakes": mistakes,
                "grammar_rule_used": ev.grammar_rule_used if ev is not None else False,
                "score": score,
                "error_type": "correct" if is_correct else "needs_review",
            }

        return {
            "task_type": "curriculum_grammar_speak",
            "total": len(prompts),
            "correct_count": correct_count,
            "percentage": llm_result.subskill_score * 10.0,
            "subskill_score": llm_result.subskill_score,
            "main_mistakes": llm_result.main_mistakes,
            "overall_level": llm_result.overall_level,
            "questions": questions,
        }

    # ------------------------------------------------------------------
    # Open-text writing evaluator — LLM-backed, async.
    #
    # Used for curriculum_grammar_open_text (and future open_text tasks).
    # Returns the same report envelope as the rule-based methods so
    # evaluation_node + feedback_node need no special-casing.
    # ------------------------------------------------------------------
    async def evaluate_open_text_writing(
        self,
        *,
        task_content: dict,
        user_answers: dict,
        user_level: int = 5,
        learner_profile: dict | None = None,
        evaluation_focus: dict | None = None,
    ) -> dict:
        """LLM-based evaluation for open_text writing tasks.

        Calls the LLM with the task prompts, user answers, and learner
        profile (level, self-assessed tier) to get:
          - subskill_score (0-10, level-calibrated)
          - per-item mistakes
          - main_mistakes list (fed straight to the feedback agent)

        Falls back to a safe structural stub if the LLM call fails, so
        the session flow never breaks.
        """
        from app.ai.llm import get_default_llm_client

        profile = learner_profile or {}
        items = task_content.get("items") or []

        user_message = _build_open_text_user_message(
            task_content=task_content,
            user_answers=user_answers,
            user_level=user_level,
            learner_profile=profile,
            evaluation_focus=evaluation_focus,
        )

        llm_result: _OpenTextWritingEval | None = None
        try:
            client = get_default_llm_client()
            llm_result = await client.generate_structured(
                system_prompt=_OPEN_TEXT_EVAL_SYSTEM,
                user_prompt=user_message,
                output_model=_OpenTextWritingEval,
                temperature=0.2,
            )
        except Exception:
            logger.exception(
                "evaluate_open_text_writing LLM call failed; using fallback"
            )

        if llm_result is None:
            # Structural fallback: answered = 1.0, empty = 0.0
            answered = sum(
                1 for it in items
                if user_answers.get(it.get("item_id", ""), "").strip()
            )
            total = len(items) or 1
            subskill_score = round((answered / total) * 7)  # max 7 for fallback
            per_item = {
                it.get("item_id", f"item_{idx}"): {
                    "correct": bool(user_answers.get(it.get("item_id", ""), "").strip()),
                    "user_answer": user_answers.get(it.get("item_id", ""), ""),
                    "mistakes": [],
                    "score": 1.0 if user_answers.get(it.get("item_id", ""), "").strip() else 0.0,
                    "error_type": (
                        "needs_ai_review"
                        if user_answers.get(it.get("item_id", ""), "").strip()
                        else "missing_answer"
                    ),
                }
                for idx, it in enumerate(items, 1)
            }
            return {
                "task_type": "curriculum_grammar_open_text",
                "total": total,
                "correct_count": answered,
                "answered_count": answered,
                "percentage": subskill_score * 10.0,
                "subskill_score": subskill_score,
                "main_mistakes": ["Evaluation service temporarily unavailable."],
                "questions": per_item,
            }

        # Build the standard per-question dict from LLM result
        item_eval_by_id = {ev.item_id: ev for ev in llm_result.items}
        per_question: dict[str, dict] = {}
        correct_count = 0
        answered_count = 0

        for idx, item in enumerate(items, 1):
            item_id = item.get("item_id", f"item_{idx}")
            user_ans = user_answers.get(item_id, "")
            ev = item_eval_by_id.get(item_id)
            score = ev.score if ev else (0.0 if not user_ans.strip() else 0.7)
            mistakes = ev.mistakes if ev else []
            is_correct = score >= 0.6
            is_answered = bool(user_ans.strip())

            per_question[item_id] = {
                "correct": is_correct,
                "user_answer": user_ans,
                "correct_answer": item.get("sample_answer", ""),
                "mistakes": mistakes,
                "score": score,
                "error_type": "correct" if is_correct else "needs_review",
                "prompt": item.get("prompt", ""),
            }
            if is_correct:
                correct_count += 1
            if is_answered:
                answered_count += 1

        total = len(items) or 1
        percentage = llm_result.subskill_score * 10.0

        return {
            "task_type": "curriculum_grammar_open_text",
            "total": total,
            "correct_count": correct_count,
            "answered_count": answered_count,
            "percentage": percentage,
            "subskill_score": llm_result.subskill_score,
            "main_mistakes": llm_result.main_mistakes,
            "overall_level": llm_result.overall_level,
            "questions": per_question,
        }

    # ------------------------------------------------------------------
    # Strategy dispatcher — dispatches on ScoringMethod, not task_type.
    # ------------------------------------------------------------------
    async def score(
        self,
        *,
        scoring_method: "ScoringMethod",
        task_content: dict,
        user_answers: dict,
        user_level: int = 5,
        learner_profile: dict | None = None,
        evaluation_focus: dict | None = None,
        activity_type: str | None = None,
    ) -> dict:
        """Single entry point. Dispatches on scoring_method, not task_type strings."""
        from app.tasks.schemas.base import ScoringMethod

        if scoring_method == ScoringMethod.LLM_OPEN_WRITING:
            return await self.evaluate_open_text_writing(
                task_content=task_content,
                user_answers=user_answers,
                user_level=user_level,
                learner_profile=learner_profile or {},
                evaluation_focus=evaluation_focus,
            )
        # TODO(migration): add LLM_SPEAKING_GRAMMAR, RULE_* branches one PR at a time
        if activity_type is None:
            raise ValueError(
                f"score() needs activity_type for legacy scoring_method={scoring_method}"
            )
        return self.evaluate(
            activity_type=activity_type,
            task_content=task_content,
            user_answers=user_answers,
        )

    # ------------------------------------------------------------------
    # Legacy dispatcher — routes on activity_type strings.
    # ------------------------------------------------------------------
    def evaluate(
        self,
        *,
        activity_type: str,
        task_content: dict,
        user_answers: dict,
    ) -> dict:
        """Route to the right evaluator based on activity_type.

        This is the single entry point for the responses service. Adding
        a new activity later means: write `evaluate_xxx`, add one line
        here. Callers don't change.

        Raises:
            ValueError: unsupported activity_type.
        """
        if activity_type == "fill_in_the_blanks":
            return self.evaluate_fill_in_blanks(
                task_content=task_content, user_answers=user_answers
            )
        if activity_type in ("fill_in_blanks", "curriculum_grammar_fill_blanks"):
            # Generated task shape — blanks[] not activities[]
            return self.evaluate_generated_fill_in_blanks(
                task_content=task_content, user_answers=user_answers
            )
        if activity_type == "error_spotting":
            return self.evaluate_error_spotting(
                task_content=task_content, user_answers=user_answers
            )
        if activity_type == "sentence_transformation":
            return self.evaluate_sentence_transformation(
                task_content=task_content, user_answers=user_answers
            )
        if activity_type == "voice_conversion":
            return self.evaluate_voice_conversion(
                task_content=task_content, user_answers=user_answers
            )
        if activity_type == "sentence_engineering":
            return self.evaluate_sentence_engineering(
                task_content=task_content, user_answers=user_answers
            )
        if activity_type == "paraphrasing":
            return self.evaluate_paraphrasing(
                task_content=task_content, user_answers=user_answers
            )
        if activity_type == "error_correction":
            return self.evaluate_error_correction(
                task_content=task_content, user_answers=user_answers
            )
        if activity_type == "speak_with_tense":
            return self.evaluate_speak_with_tense(
                task_content=task_content, user_answers=user_answers
            )
        if activity_type == "curriculum_grammar_listen_mcq":
            return self.evaluate_curriculum_grammar_listen_mcq(
                task_content=task_content, user_answers=user_answers
            )
        raise ValueError(
            f"Unsupported activity_type: {activity_type!r}. "
            f"Supported: fill_in_the_blanks, fill_in_blanks, error_spotting, "
            f"sentence_transformation, voice_conversion, sentence_engineering, "
            f"paraphrasing, error_correction, speak_with_tense, "
            f"curriculum_grammar_listen_mcq."
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _find_activity(task_content: dict, activity_type: str) -> dict:
        """Return the first activity dict matching `activity_type`.

        Generic version of `_extract_answer_key` — works for any
        activity, returns the whole activity dict (not just answers).
        """
        for activity in task_content.get("activities", []):
            if activity.get("activity_type") == activity_type:
                return activity
        raise ValueError(
            f"task_content has no {activity_type!r} activity"
        )
