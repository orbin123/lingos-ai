"""TaskGenerator interface + Phase 3 deterministic stub.

Mirrors the Evaluator / FeedbackGenerator pattern. The session shell pulls
`task_content` from whichever generator is wired in; Phase 4 swaps the
default to the LLM-driven implementation.

`task_content` is the JSONB blob the frontend renders. Shape varies by
archetype (passages for read, prompts for write, audio for listen, …) but
every payload carries the common keys defined in `_BASE_FIELDS` below so
the widget shell can render a minimal view even when the archetype-specific
fields are missing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Protocol

from app.modules.sessions.widget_mapping import normalize_widget_key
from app.scoring import ArchetypeSpec


_BASE_FIELDS = ("phase", "archetype_id", "archetype_name", "ui_widget", "core_activity")
_LEGACY_FILL_BLANK_TYPES = {"fill_in_the_blanks", "fill_in_blanks"}
_LISTEN_WIDGETS = {
    "ListenAndAnswer+MCQList",
    "ListenAndAnswer+FillInBlanks",
    "ListenAndAnswer+OpenTextList",
    "ListenAndAnswer+SpeakAndRecord",
    "listen_and_respond",
}
_LISTEN_MCQ_WIDGETS = {"ListenAndAnswer+MCQList", "listen_and_respond"}
_ERROR_SPOTTING_TYPES = {"READ_ERROR_SPOT", "ErrorSpotting", "error_spotting"}
_INNER_WIDGET_ALIASES = {
    "mcq": "mcq",
    "mcqlist": "mcq",
    "mcq_list": "mcq",
    "multiplechoice": "mcq",
    "multiple_choice": "mcq",
    "multiple-choice": "mcq",
    "quiz": "mcq",
    "open_text": "open_text",
    "opentext": "open_text",
    "opentextlist": "open_text",
    "open_text_list": "open_text",
    "fill_in_blanks": "fill_in_blanks",
    "fillinblanks": "fill_in_blanks",
    "fillblanks": "fill_in_blanks",
    "speak_and_record": "speak_and_record",
    "speakandrecord": "speak_and_record",
}

@dataclass(frozen=True)
class GeneratedTask:
    """Wrapper that distinguishes the rendered content from optional notes.

    `content` is what gets stored in `activity_attempts.task_content` and
    shipped to the frontend. `evaluator_notes` is optional internal context
    the Evaluator may consult (e.g. "expected key points: …") and is NOT
    surfaced through the next-activity API. Phase 4 MVP leaves it empty.
    """

    content: dict
    evaluator_notes: str | None = None


class TaskGenerator(Protocol):
    """Produce the `task_content` JSON for one activity in a session."""

    async def generate(
        self,
        *,
        archetype: ArchetypeSpec,
        day_topic: str,
        explanation_brief: str,
        cefr_level: str,
        sub_level: int,
        user_interests: list[str] | None = None,
        task_spec: dict | None = None,
    ) -> GeneratedTask: ...


class StubTaskGenerator:
    """Deterministic offline TaskGenerator. Used in tests and as fallback.

    Returns the same shape as the Phase 3 `_stub_task_content` helper so
    existing widget code keeps working without an LLM call.
    """

    async def generate(
        self,
        *,
        archetype: ArchetypeSpec,
        day_topic: str,
        explanation_brief: str,
        cefr_level: str,
        sub_level: int,
        user_interests: list[str] | None = None,
        task_spec: dict | None = None,
    ) -> GeneratedTask:
        spec_dict = task_spec or {}
        content = {
            "phase": "stub",
            "archetype_id": archetype.archetype_id,
            "archetype_name": archetype.name,
            "ui_widget": archetype.ui_widget,
            "widget": normalize_widget_key(archetype.ui_widget),
            "core_activity": archetype.core_activity,
            "topic": spec_dict.get("topic_override") or day_topic,
            "explanation_brief": explanation_brief,
            "instructions": spec_dict.get("instructions_override") or (
                f"Practice {archetype.name.lower()} on the topic '{day_topic}'."
            ),
            "primary_text": spec_dict.get("primary_text_seed", ""),
            "target_words": list(spec_dict.get("target_words", [])),
            "cefr_level": cefr_level,
            "sub_level": sub_level,
        }
        if spec_dict.get("task_intro"):
            content["task_intro"] = spec_dict["task_intro"]
        if spec_dict.get("estimated_time_minutes"):
            content["estimated_time_minutes"] = spec_dict["estimated_time_minutes"]
        if archetype.ui_widget == "FillInBlanks":
            authored = authored_fill_in_blanks_content(spec_dict)
            if authored is not None:
                content.update(authored)
        if archetype.core_activity == "listen":
            authored = authored_listen_and_respond_content(spec_dict)
            if authored is not None:
                content.update(authored)
                content = normalize_listen_and_respond_payload(content)
                return GeneratedTask(content=content)
            content.setdefault(
                "audio_script",
                (
                    "Maria wakes up at seven every morning. She always drinks coffee first. "
                    "Then she usually reads the news for ten minutes. She never skips breakfast. "
                    "Her husband often makes eggs on weekdays. They sometimes walk to work together "
                    "when the weather is nice."
                ),
            )
            # Cloze listening renders blanks (inner_widget="fill_in_blanks"); every
            # other listening archetype renders MCQ. Generic, theme-neutral stub
            # content — the live LLM generator produces the real payload.
            if archetype.archetype_id == "LISTEN_CLOZE":
                content.setdefault("inner_widget", "fill_in_blanks")
                content.setdefault(
                    "passage",
                    "Maria ___ up at seven. She always ___ coffee first.",
                )
                content.setdefault("items", [
                    {
                        "item_id": "b1",
                        "blank_id": "b1",
                        "sentence_with_blank": "Maria ___ up at seven.",
                        "base_verb": "wake",
                        "correct_answer": "wakes",
                        "options": ["wakes", "wake", "waking"],
                        "explanation": "Third person singular adds -s: she wakes.",
                    },
                    {
                        "item_id": "b2",
                        "blank_id": "b2",
                        "sentence_with_blank": "She always ___ coffee first.",
                        "base_verb": "drink",
                        "correct_answer": "drinks",
                        "options": ["drinks", "drink", "drinking"],
                        "explanation": "Third person singular adds -s: she drinks.",
                    },
                ])
            else:
                content.setdefault("inner_widget", "mcq")
                content.setdefault("items", [
                    {
                        "item_id": "q1",
                        "prompt": "What time does Maria wake up?",
                        "options": ["Six o'clock", "Seven o'clock", "Eight o'clock", "Nine o'clock"],
                        "correct_index": 1,
                        "explanation": "The script says she wakes up at seven every morning.",
                    },
                    {
                        "item_id": "q2",
                        "prompt": "What does Maria always do first?",
                        "options": ["Eat breakfast", "Read the news", "Drink coffee", "Walk to work"],
                        "correct_index": 2,
                        "explanation": "She always drinks coffee first.",
                    },
                    {
                        "item_id": "q3",
                        "prompt": "How long does Maria usually read the news?",
                        "options": ["Five minutes", "Ten minutes", "Fifteen minutes", "Twenty minutes"],
                        "correct_index": 1,
                        "explanation": "She reads for ten minutes.",
                    },
                    {
                        "item_id": "q4",
                        "prompt": "When do Maria and her husband sometimes walk to work?",
                        "options": [
                            "Every day",
                            "When it is cold",
                            "When the weather is nice",
                            "On weekends only",
                        ],
                        "correct_index": 2,
                        "explanation": "They walk together when the weather is nice.",
                    },
                ])
            content = normalize_listen_and_respond_payload(content)
        if archetype.archetype_id == "SPEAK_READ_ALOUD":
            content = normalize_read_aloud_payload({
                **content,
                "text_to_read_aloud": (
                    "Last Saturday, Maria visited her grandparents in the countryside. "
                    "They played cards and talked about school. She ate homemade soup, "
                    "watched an old film, and laughed with her cousins. Maria enjoyed "
                    "the quiet evening and went home feeling happy. She told her parents "
                    "about the trip before she fell asleep."
                ),
                "grammar_rule_to_practice": (
                    "Use the simple past tense to describe completed actions. "
                    "Regular verbs typically end in -ed; irregular verbs change form."
                ),
                "target_words": [
                    "visited", "played", "talked", "ate", "watched",
                    "laughed", "enjoyed", "went", "told",
                ],
                "task_intro": "Read the passage above out loud.",
                "instructions": "Read the connected passage aloud clearly.",
                "speaking_duration_seconds": 45,
            })
        return GeneratedTask(content=content)


def assert_has_base_fields(content: dict) -> None:
    """Validate a content payload carries the keys widgets rely on.

    Used by tests and at production-defensive seams. Raises ValueError
    rather than silently shipping a payload the frontend can't render.
    """
    missing = [f for f in _BASE_FIELDS if f not in content]
    if missing:
        raise ValueError(f"task content missing required base fields: {missing}")


def authored_fill_in_blanks_content(task_spec: dict | None) -> dict | None:
    """Return source-authored fill-in-blanks content from a task spec, if any."""
    spec = task_spec or {}
    for key in ("fill_in_blanks", "payload", "content"):
        candidate = spec.get(key)
        if isinstance(candidate, dict):
            normalized = normalize_fill_in_blanks_payload(candidate)
            if normalized.get("items") or normalized.get("blanks"):
                return normalized

    has_direct_payload = any(
        key in spec
        for key in ("items", "blanks", "activities", "source", "passage", "primary_text")
    )
    if not has_direct_payload:
        return None
    normalized = normalize_fill_in_blanks_payload(spec)
    return normalized if normalized.get("items") or normalized.get("blanks") else None


def authored_listen_and_respond_content(task_spec: dict | None) -> dict | None:
    """Return source-authored listening content from a task spec, if present."""
    spec = task_spec or {}
    for key in ("listen_and_respond", "payload", "content"):
        candidate = spec.get(key)
        if isinstance(candidate, dict):
            normalized = normalize_listen_and_respond_payload(candidate)
            if is_valid_listening_payload(normalized):
                return normalized

    if not isinstance(spec.get("audio_script"), str):
        return None
    normalized = normalize_listen_and_respond_payload(spec)
    return normalized if is_valid_listening_payload(normalized) else None


def _strip_inline_verb_hint(text: str, base_verb: str) -> str:
    """Remove `(base_verb)` hints from passage text; the UI shows them from `base_verb`."""
    verb = base_verb.strip()
    if not verb:
        return text
    cleaned = re.sub(
        rf"\(\s*{re.escape(verb)}\s*\)",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return re.sub(r"  +", " ", cleaned)


def _strip_passage_verb_hints(passage: str, items: list[dict]) -> str:
    result = passage
    for item in items:
        base_verb = str(item.get("base_verb") or "").strip()
        if base_verb:
            result = _strip_inline_verb_hint(result, base_verb)
    return re.sub(r"  +", " ", result)


def normalize_fill_in_blanks_payload(content: dict) -> dict:
    """Derive widget-native fields from native or legacy cloze payloads.

    The chat UI renders `items` / `blanks`, while older seeded tasks used
    `activities[].questions` plus `activities[].answers`. This function keeps
    the original payload intact and only adds/fills derived widget fields.
    """
    normalized = dict(content or {})
    items = _native_blank_items(normalized)
    legacy_activity = _legacy_fill_blanks_activity(normalized)

    passage = _first_text(
        normalized.get("passage"),
        _source_text(normalized.get("source")),
        normalized.get("primary_text"),
    )
    if passage is None and legacy_activity is not None:
        passage = _first_text(
            legacy_activity.get("passage"),
            _source_text(legacy_activity.get("source")),
            legacy_activity.get("primary_text"),
        )

    if not items and legacy_activity is not None:
        items = _items_from_legacy_activity(legacy_activity)
    if not items and passage is not None:
        items = _items_from_passage(passage, normalized)

    if items:
        for item in items:
            base_verb = str(item.get("base_verb") or "").strip()
            sentence = item.get("sentence_with_blank")
            if base_verb and isinstance(sentence, str):
                item["sentence_with_blank"] = _strip_inline_verb_hint(sentence, base_verb)
        normalized["items"] = items
        normalized.setdefault("blanks", items)
        normalized["total_blanks"] = len(items)

    instruction = normalized.get("instructions") or normalized.get("instruction")
    if not instruction and legacy_activity is not None:
        instruction = legacy_activity.get("instructions") or legacy_activity.get("instruction")
    if isinstance(instruction, str) and instruction.strip():
        normalized["instructions"] = instruction.strip()

    if passage is not None:
        passage = _normalize_blank_markers(passage)
        if items:
            passage = _strip_passage_verb_hints(passage, items)
        normalized["passage"] = passage

    if "widget" in normalized:
        normalized["widget"] = normalize_widget_key(str(normalized["widget"]))

    return normalized


def normalize_listen_and_respond_payload(content: dict) -> dict:
    """Normalize generated listening payloads into the frontend contract.

    The LLM occasionally emits friendly aliases such as ``MCQList`` or
    one-based/capitalized answer keys. This keeps the wire shape stable:
    ``inner_widget: "mcq"`` plus ``items[].correct_index`` as a zero-based int.
    Invalid MCQ rows are dropped so callers can reliably detect malformed
    payloads and fall back before delivery.
    """
    normalized = dict(content or {})
    normalized["widget"] = "listen_and_respond"
    inner = _normalize_inner_widget(normalized.get("inner_widget"))
    if not inner and (
        str(normalized.get("archetype_id") or "") == "LISTEN_MCQ"
        or str(normalized.get("ui_widget") or "") in _LISTEN_MCQ_WIDGETS
    ):
        inner = "mcq"
    if inner:
        normalized["inner_widget"] = inner

    if normalized.get("inner_widget") == "mcq":
        normalized["items"] = _normalize_mcq_items(normalized.get("items"))
    elif normalized.get("inner_widget") == "fill_in_blanks":
        fill_payload = normalize_fill_in_blanks_payload(normalized)
        normalized.update({
            key: value
            for key, value in fill_payload.items()
            if key in {"items", "blanks", "total_blanks", "passage", "instructions"}
        })

    audio_script = normalized.get("audio_script") or normalized.get("primary_text")
    if isinstance(audio_script, str) and audio_script.strip():
        normalized["audio_script"] = audio_script.strip()

    return normalized


def is_valid_listening_payload(content: dict) -> bool:
    """Return True when a listening payload is safe to render and score."""
    if normalize_widget_key(str(content.get("widget") or content.get("ui_widget") or "")) != "listen_and_respond":
        return False
    if not str(content.get("audio_script") or "").strip():
        return False

    inner_widget = content.get("inner_widget")
    items = content.get("items")
    if inner_widget == "mcq":
        return isinstance(items, list) and len(items) > 0
    if inner_widget == "fill_in_blanks":
        if not isinstance(items, list) or not items:
            return False
        return all(
            isinstance(item, dict)
            and str(item.get("item_id") or item.get("blank_id") or "").strip()
            and "___" in str(item.get("sentence_with_blank") or "")
            and str(item.get("correct_answer") or "").strip()
            for item in items
        )
    if inner_widget == "open_text":
        return is_valid_open_text_payload(content)
    if inner_widget == "speak_and_record":
        return bool(str(content.get("text_to_shadow") or content.get("audio_script") or "").strip())
    return False


def is_valid_listening_mcq_payload(content: dict) -> bool:
    """Return True when a listening MCQ payload is safe to render/score."""
    return is_valid_listening_payload(content) and content.get("inner_widget") == "mcq"


def normalize_open_text_payload(content: dict) -> dict:
    """Normalize generated open-text writing payloads for the chat widget."""
    normalized = dict(content or {})
    normalized["widget"] = "open_text"
    normalized["items"] = _normalize_open_text_items(normalized.get("items"))

    instructions = normalized.get("instructions") or normalized.get("instruction")
    if isinstance(instructions, str) and instructions.strip():
        normalized["instructions"] = instructions.strip()

    target_words = normalized.get("target_words")
    if isinstance(target_words, list):
        normalized["target_words"] = [
            str(word).strip() for word in target_words if str(word).strip()
        ]

    return normalized


def is_valid_open_text_payload(content: dict, *, expected_items: int | None = None) -> bool:
    """Return True when an open-text payload is safe to render/evaluate."""
    if normalize_widget_key(str(content.get("widget") or content.get("ui_widget") or "")) != "open_text":
        return False
    items = content.get("items")
    if not isinstance(items, list) or not items:
        return False
    if expected_items is not None and len(items) != expected_items:
        return False
    return all(
        isinstance(item, dict)
        and str(item.get("item_id") or "").strip()
        and str(item.get("prompt") or "").strip()
        and str(item.get("sample_answer") or "").strip()
        and isinstance(item.get("answer_hints"), list)
        for item in items
    )


def normalize_error_correction_payload(content: dict) -> dict:
    """Normalize generated error-correction writing payloads for the chat widget."""
    normalized = dict(content or {})
    normalized["widget"] = "error_correction"
    normalized["items"] = _normalize_error_correction_items(normalized.get("items"))

    instructions = normalized.get("instructions") or normalized.get("instruction")
    if isinstance(instructions, str) and instructions.strip():
        normalized["instructions"] = instructions.strip()

    return normalized


def normalize_sentence_transform_payload(content: dict) -> dict:
    """Normalize generated sentence-transformation writing payloads for the chat widget."""
    normalized = dict(content or {})
    normalized["widget"] = "sentence_transform"
    normalized["items"] = _normalize_sentence_transform_items(normalized.get("items"))

    instructions = normalized.get("instructions") or normalized.get("instruction")
    if isinstance(instructions, str) and instructions.strip():
        normalized["instructions"] = instructions.strip()

    return normalized


def is_valid_sentence_transform_payload(content: dict, *, expected_items: int | None = None) -> bool:
    """Return True when a sentence-transform payload is safe to render/evaluate."""
    if normalize_widget_key(str(content.get("widget") or content.get("ui_widget") or "")) != "sentence_transform":
        return False
    items = content.get("items")
    if not isinstance(items, list) or not items:
        return False
    if expected_items is not None and len(items) != expected_items:
        return False
    return all(
        isinstance(item, dict)
        and str(item.get("item_id") or "").strip()
        and str(item.get("source_sentence") or "").strip()
        and str(item.get("sample_answer") or "").strip()
        and isinstance(item.get("watch_hints"), list)
        for item in items
    )


def is_valid_error_correction_payload(content: dict, *, expected_items: int | None = None) -> bool:
    """Return True when an error-correction payload is safe to render/evaluate."""
    if normalize_widget_key(str(content.get("widget") or content.get("ui_widget") or "")) != "error_correction":
        return False
    items = content.get("items")
    if not isinstance(items, list) or not items:
        return False
    if expected_items is not None and len(items) != expected_items:
        return False
    return all(
        isinstance(item, dict)
        and str(item.get("item_id") or "").strip()
        and str(item.get("incorrect_sentence") or "").strip()
        and str(item.get("sample_answer") or "").strip()
        and isinstance(item.get("watch_hints"), list)
        for item in items
    )


def normalize_error_spotting_payload(content: dict) -> dict:
    """Normalize word-level error-spotting payloads for the chat widget."""
    normalized = dict(content or {})
    normalized["widget"] = "error_spotting"
    sentences = normalized.get("passage_sentences")
    if not isinstance(sentences, list) or not sentences:
        sentences = _legacy_error_sentences(normalized.get("sentences"))
    normalized["passage_sentences"] = [
        _normalize_error_sentence(sentence, s_idx)
        for s_idx, sentence in enumerate(sentences or [], start=1)
        if isinstance(sentence, dict)
    ]
    normalized["total_errors"] = sum(
        1
        for sentence in normalized["passage_sentences"]
        if isinstance(sentence.get("error"), dict)
    )
    if not str(normalized.get("instructions") or "").strip():
        normalized["instructions"] = (
            "Tap each word in the passage that contains a grammatical error."
        )
    if not str(normalized.get("task_intro") or "").strip():
        normalized["task_intro"] = "Tap each word that has a grammatical error."
    if not normalized.get("estimated_time_minutes"):
        normalized["estimated_time_minutes"] = 3
    return normalized


def is_valid_error_spotting_payload(content: dict) -> bool:
    """Return True when an error-spotting payload is safe to render/score."""
    if normalize_widget_key(
        str(content.get("widget") or content.get("ui_widget") or "")
    ) != "error_spotting":
        return False
    sentences = content.get("passage_sentences")
    if not isinstance(sentences, list) or len(sentences) != 5:
        return False
    token_ids: set[str] = set()
    error_types: set[str] = set()
    for sentence in sentences:
        if not isinstance(sentence, dict):
            return False
        tokens = sentence.get("tokens")
        error = sentence.get("error")
        if not isinstance(tokens, list) or not tokens or not isinstance(error, dict):
            return False
        sentence_error_ids = {
            str(token.get("token_id") or "")
            for token in tokens
            if isinstance(token, dict) and token.get("is_error") is True
        }
        if len(sentence_error_ids) != 1:
            return False
        error_token_id = str(error.get("token_id") or "")
        if error_token_id not in sentence_error_ids:
            return False
        token_ids.update(
            str(token.get("token_id") or "")
            for token in tokens
            if isinstance(token, dict)
        )
        if not str(error.get("correction") or "").strip():
            return False
        error_types.add(str(error.get("error_type") or ""))
    return (
        int(content.get("total_errors") or 0) == 5
        and len(token_ids) >= 10
        and len(error_types) >= 4
    )


def _normalize_error_sentence(sentence: dict, sentence_index: int) -> dict:
    sentence_id = str(sentence.get("sentence_id") or f"s{sentence_index}")
    raw_tokens = sentence.get("tokens")
    if not isinstance(raw_tokens, list) or not raw_tokens:
        raw_text = str(sentence.get("sentence") or sentence.get("text") or "")
        raw_tokens = [
            {"text": part}
            for part in raw_text.split()
            if part.strip()
        ]

    error = dict(sentence.get("error") or {})
    legacy_error_text = str(
        sentence.get("incorrect_phrase")
        or error.get("incorrect_phrase")
        or ""
    ).strip()
    tokens: list[dict] = []
    error_token_id = str(error.get("token_id") or "")
    for token_index, raw in enumerate(raw_tokens, start=1):
        if not isinstance(raw, dict):
            raw = {"text": str(raw)}
        text = str(raw.get("text") or "").strip()
        token_id = str(raw.get("token_id") or f"{sentence_id}_t{token_index}")
        is_error = bool(raw.get("is_error"))
        if not error_token_id and legacy_error_text and text.strip(".,!?;:\"'").lower() == legacy_error_text.lower():
            is_error = True
            error_token_id = token_id
        if error_token_id and token_id == error_token_id:
            is_error = True
        tokens.append({
            "token_id": token_id,
            "text": text,
            "is_error": is_error,
        })

    if not error_token_id:
        for token in tokens:
            if token["is_error"]:
                error_token_id = token["token_id"]
                break

    if error_token_id:
        for token in tokens:
            token["is_error"] = token["token_id"] == error_token_id

    error.setdefault("token_id", error_token_id)
    error.setdefault("incorrect_phrase", legacy_error_text)
    error.setdefault("correction", sentence.get("correction") or "")
    error.setdefault("error_type", sentence.get("error_type") or "unknown")
    error.setdefault("rule", sentence.get("rule") or sentence.get("explanation") or "")
    error.setdefault("explanation", sentence.get("explanation") or "")

    return {
        "sentence_id": sentence_id,
        "tokens": tokens,
        "error": error,
    }


def _legacy_error_sentences(sentences: object) -> list[dict]:
    if not isinstance(sentences, list):
        return []
    out: list[dict] = []
    for idx, sentence in enumerate(sentences, start=1):
        if not isinstance(sentence, dict):
            continue
        if not sentence.get("has_error", True):
            continue
        sentence_id = str(sentence.get("sentence_id") or f"s{idx}")
        incorrect = str(sentence.get("incorrect_phrase") or "").strip()
        tokens = []
        for token_idx, text in enumerate(str(sentence.get("sentence") or "").split(), start=1):
            clean = text.strip(".,!?;:\"'")
            tokens.append({
                "token_id": f"{sentence_id}_t{token_idx}",
                "text": text,
                "is_error": bool(incorrect and clean.lower() == incorrect.lower()),
            })
        out.append({
            "sentence_id": sentence_id,
            "tokens": tokens,
            "error": {
                "token_id": next(
                    (
                        token["token_id"]
                        for token in tokens
                        if token.get("is_error")
                    ),
                    "",
                ),
                "incorrect_phrase": incorrect,
                "correction": sentence.get("correction") or "",
                "error_type": sentence.get("error_type") or "unknown",
                "rule": sentence.get("explanation") or "",
                "explanation": sentence.get("explanation") or "",
            },
        })
    return out


def normalize_read_aloud_payload(content: dict) -> dict:
    """Normalize read-aloud payloads so the passage is always in ``text_to_read_aloud``.

    The LLM task schema exposes ``primary_text`` and ``passage``; curriculum copy
    asks for ``text_to_read_aloud``. Coerce any of those into the canonical field.
    """
    normalized = dict(content or {})
    passage = _first_text(
        normalized.get("text_to_read_aloud"),
        normalized.get("passage"),
        normalized.get("primary_text"),
        normalized.get("speaking_prompt"),
    )
    if passage:
        normalized["text_to_read_aloud"] = passage

    for key in ("instructions", "task_intro", "grammar_rule_to_practice"):
        value = normalized.get(key)
        if isinstance(value, str):
            normalized[key] = value.strip()

    if not str(normalized.get("task_intro") or "").strip():
        normalized["task_intro"] = "Read the passage above out loud."
    if not str(normalized.get("instructions") or "").strip():
        normalized["instructions"] = "Read the connected passage aloud clearly."

    duration = normalized.get("speaking_duration_seconds")
    try:
        duration_int = int(duration) if duration is not None else 0
    except (TypeError, ValueError):
        duration_int = 0
    if duration_int <= 0:
        duration_int = 45
    normalized["speaking_duration_seconds"] = duration_int

    target_words = normalized.get("target_words")
    if isinstance(target_words, list):
        normalized["target_words"] = [
            str(w).strip() for w in target_words if str(w).strip()
        ]

    if not normalized.get("estimated_time_minutes"):
        normalized["estimated_time_minutes"] = 1

    return normalized


def is_valid_read_aloud_payload(content: dict) -> bool:
    """Return True when a read-aloud payload includes a passage to speak."""
    passage = _first_text(
        content.get("text_to_read_aloud"),
        content.get("passage"),
        content.get("primary_text"),
    )
    if not passage:
        return False
    word_count = len(passage.split())
    return 30 <= word_count <= 80


def normalize_speak_and_record_payload(content: dict) -> dict:
    """Normalize generated speaking payloads for the SpeakRecordWidget.

    The widget expects `speaking_prompts: list[str]` with a matching
    `sample_responses: list[str]`. The LLM frequently emits aliases
    (`prompt`, `speaking_prompt`, `prompts`, `sample_response`) — this
    helper coerces those into the canonical shape so the widget receives
    real prompts instead of falling back to its "Speak your response"
    placeholder.
    """
    normalized = dict(content or {})
    normalized["widget"] = "speak_and_record"

    prompts_raw: Any = (
        normalized.get("speaking_prompts")
        or normalized.get("prompts")
        or normalized.get("speaking_items")
    )
    prompts: list[str] = []
    if isinstance(prompts_raw, list):
        prompts = [str(p).strip() for p in prompts_raw if str(p).strip()]

    if not prompts:
        single = (
            normalized.get("speaking_prompt")
            or normalized.get("prompt")
            or normalized.get("primary_text")
        )
        if isinstance(single, str) and single.strip():
            prompts = [single.strip()]

    if prompts:
        normalized["speaking_prompts"] = prompts

    samples_raw: Any = (
        normalized.get("sample_responses") or normalized.get("sample_answers")
    )
    samples: list[str] = []
    if isinstance(samples_raw, list):
        samples = [str(s).strip() for s in samples_raw]
    if not samples:
        single_sample = (
            normalized.get("sample_response") or normalized.get("sample_answer")
        )
        if isinstance(single_sample, str) and single_sample.strip():
            samples = [single_sample.strip()]
    if prompts:
        if len(samples) < len(prompts):
            samples = samples + [""] * (len(prompts) - len(samples))
        else:
            samples = samples[: len(prompts)]
        normalized["sample_responses"] = samples

    for key in ("instructions", "task_intro", "grammar_rule_to_practice"):
        value = normalized.get(key)
        if isinstance(value, str):
            normalized[key] = value.strip()

    target_words = normalized.get("target_words")
    if isinstance(target_words, list):
        normalized["target_words"] = [
            str(w).strip() for w in target_words if str(w).strip()
        ]

    duration = normalized.get("speaking_duration_seconds")
    try:
        duration_int = int(duration) if duration is not None else 0
    except (TypeError, ValueError):
        duration_int = 0
    if duration_int <= 0:
        duration_int = 45
    normalized["speaking_duration_seconds"] = duration_int

    if not normalized.get("estimated_time_minutes"):
        normalized["estimated_time_minutes"] = 3

    return normalized


def normalize_speak_pic_desc_payload(content: dict) -> dict:
    """Normalize generated picture-description payloads for speak_pic_desc.

    Coerces speaking prompt aliases into a single prompt list and preserves
    ``image_alt`` for downstream image generation. Does not overwrite ``widget``.
    """
    normalized = dict(content or {})

    prompts_raw: Any = (
        normalized.get("speaking_prompts")
        or normalized.get("prompts")
        or normalized.get("speaking_items")
    )
    prompts: list[str] = []
    if isinstance(prompts_raw, list):
        prompts = [str(p).strip() for p in prompts_raw if str(p).strip()]

    if not prompts:
        single = (
            normalized.get("speaking_prompt")
            or normalized.get("prompt")
            or normalized.get("primary_text")
        )
        if isinstance(single, str) and single.strip():
            prompts = [single.strip()]

    if prompts:
        normalized["speaking_prompts"] = prompts[:1]

    samples_raw: Any = (
        normalized.get("sample_responses") or normalized.get("sample_answers")
    )
    samples: list[str] = []
    if isinstance(samples_raw, list):
        samples = [str(s).strip() for s in samples_raw if str(s).strip()]
    if not samples:
        single_sample = (
            normalized.get("sample_response") or normalized.get("sample_answer")
        )
        if isinstance(single_sample, str) and single_sample.strip():
            samples = [single_sample.strip()]
    if samples:
        normalized["sample_responses"] = samples[:1]
    elif normalized.get("speaking_prompts"):
        normalized["sample_responses"] = [""]

    image_alt = normalized.get("image_alt")
    if isinstance(image_alt, str):
        normalized["image_alt"] = image_alt.strip()

    for key in ("instructions", "task_intro", "grammar_rule_to_practice"):
        value = normalized.get(key)
        if isinstance(value, str):
            normalized[key] = value.strip()

    duration = normalized.get("speaking_duration_seconds")
    try:
        duration_int = int(duration) if duration is not None else 0
    except (TypeError, ValueError):
        duration_int = 0
    if duration_int <= 0:
        duration_int = 45
    normalized["speaking_duration_seconds"] = duration_int

    if not normalized.get("estimated_time_minutes"):
        normalized["estimated_time_minutes"] = 1

    return normalized


def is_valid_speak_pic_desc_payload(content: dict) -> bool:
    """Return True when a picture-description payload can be shown to the learner."""
    prompts = content.get("speaking_prompts")
    if not isinstance(prompts, list) or not prompts:
        return False
    if not all(isinstance(p, str) and p.strip() for p in prompts):
        return False
    if not str(content.get("image_alt") or "").strip():
        return False
    image_url = str(content.get("image_url") or "").strip()
    image_error = str(content.get("image_error") or "").strip()
    return bool(image_url or image_error)


def is_valid_speak_and_record_payload(content: dict) -> bool:
    """Return True when a speaking payload is safe to render/evaluate."""
    if normalize_widget_key(
        str(content.get("widget") or content.get("ui_widget") or "")
    ) != "speak_and_record":
        return False
    prompts = content.get("speaking_prompts")
    if not isinstance(prompts, list) or not prompts:
        return False
    if not all(isinstance(p, str) and p.strip() for p in prompts):
        return False
    samples = content.get("sample_responses")
    if not isinstance(samples, list) or len(samples) != len(prompts):
        return False
    if not str(content.get("instructions") or "").strip():
        return False
    if not str(content.get("task_intro") or "").strip():
        return False
    return True


def _normalize_inner_widget(raw: Any) -> str:
    key = str(raw or "").strip()
    if not key:
        return ""
    compact = key.replace(" ", "_").replace("-", "_")
    return _INNER_WIDGET_ALIASES.get(compact.lower(), key)


def _normalize_mcq_items(raw_items: Any) -> list[dict]:
    if not isinstance(raw_items, list):
        return []
    items: list[dict] = []
    for index, raw in enumerate(raw_items, start=1):
        if not isinstance(raw, dict):
            continue
        prompt = str(raw.get("prompt") or raw.get("question") or "").strip()
        options = raw.get("options") or raw.get("choices") or []
        if not isinstance(options, list):
            continue
        clean_options = [str(option).strip() for option in options if str(option).strip()]
        correct_index = _coerce_correct_index(raw, clean_options)
        if not prompt or len(clean_options) != 4 or correct_index is None:
            continue
        item_id = str(raw.get("item_id") or raw.get("id") or f"q{index}").strip()
        items.append({
            "item_id": item_id or f"q{index}",
            "prompt": prompt,
            "options": clean_options,
            "correct_index": correct_index,
            "explanation": str(raw.get("explanation") or "").strip(),
        })
    return items


def _coerce_correct_index(raw: dict, options: list[str]) -> int | None:
    value_source = "correct_index"
    value = raw.get("correct_index")
    if value is None:
        value_source = "answer_index"
        value = raw.get("answer_index")
    if value is None:
        answer = raw.get("correct_answer") or raw.get("answer")
        if answer is not None:
            answer_text = str(answer).strip()
            for idx, option in enumerate(options):
                if option.lower() == answer_text.lower():
                    return idx
            if len(answer_text) == 1 and answer_text.upper() in "ABCD":
                return ord(answer_text.upper()) - ord("A")
    try:
        idx = int(value)
    except (TypeError, ValueError):
        return None
    if value_source == "answer_index" and 1 <= idx <= len(options):
        idx -= 1
    if 0 <= idx < len(options):
        return idx
    return None


def _normalize_open_text_items(raw_items: Any) -> list[dict]:
    if not isinstance(raw_items, list):
        return []
    items: list[dict] = []
    for index, raw in enumerate(raw_items, start=1):
        if not isinstance(raw, dict):
            continue
        prompt = str(raw.get("prompt") or raw.get("question") or "").strip()
        sample = str(
            raw.get("sample_answer")
            or raw.get("reference_answer")
            or raw.get("example_answer")
            or ""
        ).strip()
        if not prompt or not sample:
            continue
        hints = raw.get("answer_hints") or raw.get("hints") or []
        if not isinstance(hints, list):
            hints = [str(hints)] if str(hints).strip() else []
        clean_hints = [str(hint).strip() for hint in hints if str(hint).strip()]
        if not clean_hints:
            clean_hints = ["Use one clear sentence.", "Include a frequency adverb."]
        item_id = str(raw.get("item_id") or raw.get("id") or f"routine_{index}").strip()
        items.append(
            {
                "item_id": item_id or f"routine_{index}",
                "prompt": prompt,
                "sample_answer": sample,
                "answer_hints": clean_hints,
            }
        )
    return items


def _normalize_error_correction_items(raw_items: Any) -> list[dict]:
    if not isinstance(raw_items, list):
        return []
    items: list[dict] = []
    for index, raw in enumerate(raw_items, start=1):
        if not isinstance(raw, dict):
            continue
        incorrect = str(
            raw.get("incorrect_sentence")
            or raw.get("incorrect")
            or raw.get("sentence")
            or ""
        ).strip()
        sample = str(
            raw.get("sample_answer")
            or raw.get("correct_answer")
            or raw.get("correction")
            or raw.get("reference_answer")
            or ""
        ).strip()
        if not incorrect or not sample:
            continue
        hints = raw.get("watch_hints") or raw.get("hints") or []
        if not isinstance(hints, list):
            hints = [str(hints)] if str(hints).strip() else []
        clean_hints = [str(hint).strip() for hint in hints if str(hint).strip()]
        item_id = str(raw.get("item_id") or raw.get("id") or f"ec_{index}").strip()
        items.append(
            {
                "item_id": item_id,
                "incorrect_sentence": incorrect,
                "sample_answer": sample,
                "watch_hints": clean_hints,
            }
        )
    return items


def _normalize_sentence_transform_items(raw_items: Any) -> list[dict]:
    if not isinstance(raw_items, list):
        return []
    items: list[dict] = []
    for index, raw in enumerate(raw_items, start=1):
        if not isinstance(raw, dict):
            continue
        source = str(
            raw.get("source_sentence")
            or raw.get("source")
            or raw.get("prompt")
            or raw.get("original_sentence")
            or raw.get("sentence")
            or ""
        ).strip()
        sample = str(
            raw.get("sample_answer")
            or raw.get("correct_answer")
            or raw.get("reference_answer")
            or ""
        ).strip()
        if not source or not sample:
            continue
        hints = raw.get("watch_hints") or raw.get("hints") or []
        if not isinstance(hints, list):
            hints = [str(hints)] if str(hints).strip() else []
        clean_hints = [str(hint).strip() for hint in hints if str(hint).strip()]
        item_id = str(raw.get("item_id") or raw.get("id") or f"st_{index}").strip()
        items.append(
            {
                "item_id": item_id or f"st_{index}",
                "source_sentence": source,
                "sample_answer": sample,
                "watch_hints": clean_hints,
            }
        )
    return items


def _native_blank_items(content: dict) -> list[dict]:
    raw_items = content.get("items") or content.get("blanks") or []
    if not isinstance(raw_items, list):
        return []
    items: list[dict] = []
    for index, raw in enumerate(raw_items, start=1):
        if not isinstance(raw, dict):
            continue
        sentence = _blank_sentence(raw.get("sentence_with_blank"))
        if sentence is None:
            continue
        item = dict(raw)
        item.setdefault("item_id", item.get("blank_id") or f"blank_{index}")
        item.setdefault("blank_id", item.get("item_id"))
        item["sentence_with_blank"] = sentence
        item.setdefault("correct_answer", "")
        item.setdefault("explanation", "")
        items.append(item)
    return items


def _legacy_fill_blanks_activity(content: dict) -> dict | None:
    activities = content.get("activities")
    if not isinstance(activities, list):
        return None
    for activity in activities:
        if not isinstance(activity, dict):
            continue
        if str(activity.get("activity_type") or "") in _LEGACY_FILL_BLANK_TYPES:
            return activity
    return None


def _items_from_legacy_activity(activity: dict) -> list[dict]:
    questions = activity.get("questions")
    if not isinstance(questions, dict):
        return []
    answers = activity.get("answers") if isinstance(activity.get("answers"), dict) else {}
    explanations = (
        activity.get("explanations")
        if isinstance(activity.get("explanations"), dict)
        else {}
    )
    items: list[dict] = []
    for index, (qid, raw_sentence) in enumerate(questions.items(), start=1):
        sentence = _blank_sentence(raw_sentence)
        if sentence is None:
            continue
        item_id = str(qid) if str(qid).strip() else f"blank_{index}"
        items.append(
            {
                "item_id": item_id,
                "blank_id": item_id,
                "sentence_with_blank": sentence,
                "correct_answer": str(answers.get(qid) or answers.get(item_id) or ""),
                "explanation": str(
                    explanations.get(qid)
                    or explanations.get(item_id)
                    or "Review the target grammar for this blank."
                ),
            }
        )
    return items


def _items_from_passage(passage: str, content: dict) -> list[dict]:
    total = len(_blank_markers(passage))
    if total == 0:
        return []
    answers = _answer_lookup(content)
    return [
        {
            "item_id": f"blank_{index}",
            "blank_id": f"blank_{index}",
            "sentence_with_blank": f"Blank {index}: ___",
            "correct_answer": str(
                answers.get(f"blank_{index}")
                or answers.get(f"Q{index}")
                or answers.get(index)
                or ""
            ),
            "explanation": "Review the target grammar for this blank.",
        }
        for index in range(1, total + 1)
    ]


def _answer_lookup(content: dict) -> dict:
    raw = (
        content.get("answers")
        or content.get("answer_key")
        or content.get("correct_answers")
        or {}
    )
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list):
        return {index: value for index, value in enumerate(raw, start=1)}
    return {}


def _blank_sentence(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    sentence = value.strip()
    if not sentence:
        return None
    return _normalize_blank_markers(sentence)


def _blank_markers(value: str) -> list[str]:
    import re

    return re.findall(r"_{3,}", value)


def _normalize_blank_markers(value: str) -> str:
    import re

    return re.sub(r"_{3,}", "___", value)


def _source_text(value: object) -> str | None:
    if isinstance(value, dict):
        text = value.get("text")
        return text.strip() if isinstance(text, str) and text.strip() else None
    return None


def _first_text(*values: object) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None



