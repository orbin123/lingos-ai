"""Normalize backend/frontend widget keys.

The scoring registry stores historical UI widget names such as
``FillInBlanks`` and ``ListenAndAnswer+MCQList``. The chat renderer consumes
stable snake_case keys. Keep that translation in one tiny place.
"""

from __future__ import annotations

import re


_ALIASES: dict[str, str] = {
    "FillInBlanks": "fill_in_blanks",
    "MCQList": "mcq",
    "OpenTextList": "open_text",
    "TrueFalseNotGiven": "true_false_not_given",
    "SentenceTransform": "sentence_transform",
    "ErrorCorrection": "error_correction",
    "ErrorSpotting": "error_spotting",
    "SpeakAndRecord": "speak_and_record",
    "StructuredEssay": "structured_essay",
    "ListenAndAnswer+MCQList": "listen_and_respond",
    "ListenAndAnswer+FillInBlanks": "listen_and_respond",
    "ListenAndAnswer+OpenTextList": "listen_and_respond",
    "ListenAndAnswer+SpeakAndRecord": "listen_and_respond",
}


def normalize_widget_key(widget: str | None) -> str:
    """Return the stable frontend widget key for a registry/widget label."""

    if not widget:
        return ""
    raw = str(widget).strip()
    if raw in _ALIASES:
        return _ALIASES[raw]
    lowered = raw.lower().replace("-", "_").replace(" ", "_")
    if lowered in _ALIASES.values():
        return lowered
    return re.sub(r"(?<!^)(?=[A-Z])", "_", raw).lower().replace("+", "_")
