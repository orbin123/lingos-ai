"""Turn recurring feedback themes into qualitative, number-free coaching copy.

The stats page shows strengths and focus areas as plain coaching sentences:
no percentages, no counts, no specific words the learner wrote. This module
templates the recurring themes surfaced by ``FeedbackRAGService`` into that
voice, scrubbing any stray digits, and supplies number-free fallbacks when
there is no feedback history yet.

Pure functions — no DB, no I/O. Tested directly in ``test_progress_stats``.
"""

from __future__ import annotations

import re

# Strip numeric tokens (incl. percentages / decimals) so synthesized copy
# never leaks counts or scores.
_DIGITS = re.compile(r"\d[\d.,%]*")
_WS = re.compile(r"\s{2,}")

STRENGTH_FALLBACK = [
    "Your strongest patterns will appear here as you complete more sessions.",
    "Consistent practice will reveal which sub-skills are leading.",
    "Finish a few more activities to surface your reliable strengths.",
]
FOCUS_FALLBACK = [
    "Recurring focus areas appear here once you have more feedback.",
    "Your most repeated mistakes will be highlighted here.",
    "Keep practising — areas to work on surface after a few sessions.",
]


def _scrub(text: str) -> str:
    cleaned = _DIGITS.sub("", text or "")
    cleaned = _WS.sub(" ", cleaned).strip(" .,;:")
    return cleaned


def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:] if text else text


def _strength_sentence(theme: str) -> str:
    body = _lower_first(_scrub(theme))
    return f"You're showing consistent strength in {body}." if body else ""


def _focus_sentence(theme: str) -> str:
    body = _lower_first(_scrub(theme))
    return f"Keep building accuracy with {body}." if body else ""


def build_insights(themes: dict[str, list[str]]) -> tuple[list[str], list[str]]:
    """Return ``(strengths, focus_areas)`` — qualitative, digit-free, ≤3 each.

    ``themes`` is the ``{"strengths": [...], "focus": [...]}`` shape returned
    by ``FeedbackRAGService.compute_stats_themes``. Empty inputs fall back to
    encouraging, number-free placeholders.
    """
    strengths = [
        s for theme in themes.get("strengths", []) if (s := _strength_sentence(theme))
    ][:3]
    focus = [f for theme in themes.get("focus", []) if (f := _focus_sentence(theme))][
        :3
    ]
    if not strengths:
        strengths = STRENGTH_FALLBACK[:3]
    if not focus:
        focus = FOCUS_FALLBACK[:3]
    return strengths, focus
