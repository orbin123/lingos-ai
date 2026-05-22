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

from dataclasses import dataclass
from typing import Any, Protocol

from app.modules.sessions.widget_mapping import normalize_widget_key
from app.scoring import ArchetypeSpec


_BASE_FIELDS = ("phase", "archetype_id", "archetype_name", "ui_widget", "core_activity")
_LEGACY_FILL_BLANK_TYPES = {"fill_in_the_blanks", "fill_in_blanks"}
_LISTEN_MCQ_WIDGETS = {"ListenAndAnswer+MCQList", "listen_and_respond"}
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
            else:
                content.update(build_simple_present_fill_in_blanks_content(content["topic"]))
        if archetype.archetype_id == "WRITE_OPEN_SENT":
            content.update(build_simple_present_open_text_content(content["topic"]))
        if archetype.archetype_id == "SPEAK_TIMED" or archetype.ui_widget == "SpeakAndRecord":
            content.update(
                build_simple_present_speak_and_record_content(content["topic"])
            )
        if archetype.core_activity == "listen":
            content.setdefault(
                "audio_script",
                (
                    "Maria wakes up at seven every morning. She always drinks coffee first. "
                    "Then she usually reads the news for ten minutes. She never skips breakfast. "
                    "Her husband often makes eggs on weekdays. They sometimes walk to work together "
                    "when the weather is nice."
                ),
            )
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
        return GeneratedTask(content=content)


def assert_has_base_fields(content: dict) -> None:
    """Validate a content payload carries the keys widgets rely on.

    Used by tests and at production-defensive seams. Raises ValueError
    rather than silently shipping a payload the frontend can't render.
    """
    missing = [f for f in _BASE_FIELDS if f not in content]
    if missing:
        raise ValueError(f"task content missing required base fields: {missing}")


def is_simple_present_fill_in_blanks_task(content: dict) -> bool:
    topic = str(content.get("topic") or content.get("topic_name") or "").lower()
    instructions = str(content.get("instructions") or "").lower()
    archetype_id = str(content.get("archetype_id") or "")
    return (
        archetype_id == "READ_CLOZE"
        and ("simple present" in topic or "simple present" in instructions)
        and ("routine" in topic or "routine" in instructions)
    )


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
        normalized["items"] = items
        normalized.setdefault("blanks", items)
        normalized["total_blanks"] = len(items)

    instruction = normalized.get("instructions") or normalized.get("instruction")
    if not instruction and legacy_activity is not None:
        instruction = legacy_activity.get("instructions") or legacy_activity.get("instruction")
    if isinstance(instruction, str) and instruction.strip():
        normalized["instructions"] = instruction.strip()

    if passage is not None:
        normalized["passage"] = _normalize_blank_markers(passage)

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

    audio_script = normalized.get("audio_script") or normalized.get("primary_text")
    if isinstance(audio_script, str) and audio_script.strip():
        normalized["audio_script"] = audio_script.strip()

    return normalized


def is_valid_listening_mcq_payload(content: dict) -> bool:
    """Return True when a listening MCQ payload is safe to render/score."""
    if normalize_widget_key(str(content.get("widget") or content.get("ui_widget") or "")) != "listen_and_respond":
        return False
    if content.get("inner_widget") != "mcq":
        return False
    if not str(content.get("audio_script") or "").strip():
        return False
    items = content.get("items")
    return isinstance(items, list) and len(items) > 0


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


def build_simple_present_speak_and_record_content(topic: str) -> dict:
    """Deterministic SPEAK_TIMED payload for Day-1/Week-1 (simple present)."""
    return {
        "task_intro": "Record your routine sentences.",
        "instructions": (
            "Tap the mic and say one short routine sentence for each "
            "prompt. Use the correct simple present verb form and one "
            "frequency adverb (always, usually, often, sometimes, never)."
        ),
        "estimated_time_minutes": 3,
        "speaking_duration_seconds": 45,
        "grammar_rule_to_practice": (
            "Use the base verb with I, you, we, and they. Add -s or -es "
            "to the verb with he and she. Place the frequency adverb "
            "before the main verb."
        ),
        "target_words": ["always", "usually", "often", "sometimes", "never"],
        "topic": topic,
        "speaking_prompts": [
            (
                "Say one routine sentence about yourself starting with "
                "'I' and using a frequency adverb."
            ),
            (
                "Say one routine sentence about a friend or family "
                "member using 'he' and a frequency adverb."
            ),
            (
                "Say one routine sentence about a friend or family "
                "member using 'she' and a frequency adverb."
            ),
        ],
        "sample_responses": [
            "I usually drink water in the morning.",
            "He often walks to school.",
            "She always eats breakfast at seven.",
        ],
        "key_points_expected": [
            "Use the base verb after I.",
            "Add -s or -es after he or she.",
            "Place the frequency adverb before the main verb.",
        ],
    }


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


def build_simple_present_fill_in_blanks_content(topic: str) -> dict:
    return {
        "task_intro": "Complete the simple present routine sentences.",
        "instructions": "Fill each blank with the correct simple present verb.",
        "estimated_time_minutes": 4,
        "grammar_rule_explained": (
            "Use the base verb with I, you, we, and they. Add -s or -es with "
            "he and she."
        ),
        "passage_title": topic,
        "items": [
            {
                "item_id": "routine_1",
                "sentence_with_blank": "I always ___ my teeth in the morning.",
                "base_verb": "brush",
                "correct_answer": "brush",
                "distractors": ["brushes", "brushing"],
                "options": ["brush", "brushes", "brushing"],
                "grammar_rule": "Use the base verb form with I.",
                "explanation": "With I, use the base verb: I brush.",
            },
            {
                "item_id": "routine_2",
                "sentence_with_blank": "She usually ___ breakfast at seven.",
                "base_verb": "eat",
                "correct_answer": "eats",
                "distractors": ["eat", "eating"],
                "options": ["eat", "eats", "eating"],
                "grammar_rule": "She adds -s to the verb.",
                "explanation": "With she, add -s: she eats.",
            },
            {
                "item_id": "routine_3",
                "sentence_with_blank": "He sometimes ___ to school.",
                "base_verb": "walk",
                "correct_answer": "walks",
                "distractors": ["walk", "walking"],
                "options": ["walk", "walks", "walking"],
                "grammar_rule": "He adds -s to the verb.",
                "explanation": "With he, add -s: he walks.",
            },
            {
                "item_id": "routine_4",
                "sentence_with_blank": "They never ___ coffee at night.",
                "base_verb": "drink",
                "correct_answer": "drink",
                "distractors": ["drinks", "drinking"],
                "options": ["drink", "drinks", "drinking"],
                "grammar_rule": "Use the base verb form with they.",
                "explanation": "With they, use the base verb: they drink.",
            },
        ],
        "total_blanks": 4,
    }


def build_simple_present_open_text_content(topic: str) -> dict:
    return {
        "task_intro": "Write simple present routine sentences.",
        "instructions": (
            "Write one affirmative routine sentence for each prompt using the "
            "given subject and a frequency adverb."
        ),
        "estimated_time_minutes": 5,
        "grammar_rule_explained": (
            "Use the base verb with I. Add -s or -es to the verb with he and she. "
            "Place frequency adverbs like always, usually, often, sometimes, "
            "or never before the main verb."
        ),
        "common_mistakes": [
            "Missing -s with he or she: she usually walk -> she usually walks.",
            "Adding -s with I: I always drinks -> I always drink.",
            "Putting the frequency adverb in an unnatural place.",
        ],
        "target_words": ["always", "usually", "often", "sometimes", "never"],
        "topic": topic,
        "items": [
            {
                "item_id": "routine_i",
                "prompt": (
                    "Write one affirmative routine sentence with I and one "
                    "frequency adverb."
                ),
                "sample_answer": "I usually drink water in the morning.",
                "answer_hints": [
                    "Start with I.",
                    "Use the base verb.",
                    "Use always, usually, often, sometimes, or never.",
                ],
            },
            {
                "item_id": "routine_he",
                "prompt": (
                    "Write one affirmative routine sentence with he and one "
                    "frequency adverb."
                ),
                "sample_answer": "He often walks to school.",
                "answer_hints": [
                    "Start with He.",
                    "Add -s or -es to the main verb.",
                    "Use a frequency adverb before the verb.",
                ],
            },
            {
                "item_id": "routine_she",
                "prompt": (
                    "Write one affirmative routine sentence with she and one "
                    "frequency adverb."
                ),
                "sample_answer": "She always eats breakfast at seven.",
                "answer_hints": [
                    "Start with She.",
                    "Add -s or -es to the main verb.",
                    "Keep the sentence affirmative.",
                ],
            },
        ],
    }
