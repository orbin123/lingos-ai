"""Frontend widget key normalization for generated session tasks."""

from __future__ import annotations


WIDGET_KEY: dict[str, str] = {
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


def normalize_widget_key(widget: str | None) -> str:
    if not widget:
        return ""
    return WIDGET_KEY.get(widget, widget)
