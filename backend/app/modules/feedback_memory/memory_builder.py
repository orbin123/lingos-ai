"""Build compact text documents from structured feedback data.

These are the texts that get embedded into vectors and stored in Pinecone.
Designed to be:
  - Concise (200-300 tokens) to keep embedding cost low
  - Semantically rich so similar mistakes cluster in vector space
  - Structured enough that the LLM can parse retrieved context easily

No I/O. No DB calls. Pure string formatting.
"""

from __future__ import annotations


def build_activity_memory(
    *,
    archetype_id: str,
    archetype_name: str,
    day_id: str,
    score: int,
    mistakes: list[dict],
    did_well: list[str],
    next_tip: str | None,
    summary: str,
) -> str:
    """Build a compact text document for one activity's feedback.

    Example output::

        Activity: Fill in the Blanks (READ_FIB) | Day: day_24_01_03 | Score: 6/10
        Mistakes: Used 'their' instead of 'there' (spelling);
                  missed article 'the' before noun (grammar)
        Strengths: correct verb tenses; good sentence structure
        Tip: Review homophones (their/there/they're)
    """
    parts: list[str] = []

    # Header line
    parts.append(
        f"Activity: {archetype_name} ({archetype_id}) | Day: {day_id} | Score: {score}/10"
    )

    # Mistakes — compact, semicolon-separated
    if mistakes:
        mistake_strs: list[str] = []
        for m in mistakes[:5]:  # cap to keep embedding size manageable
            issue = m.get("issue", "")
            user_wrote = m.get("user_wrote") or ""
            correction = m.get("correction") or ""
            rule = m.get("rule") or ""
            parts_m = [issue]
            if user_wrote and correction:
                parts_m.append(f"wrote '{user_wrote}' → '{correction}'")
            if rule:
                parts_m.append(f"({rule})")
            mistake_strs.append(" ".join(parts_m))
        parts.append("Mistakes: " + "; ".join(mistake_strs))

    # Strengths
    if did_well:
        parts.append("Strengths: " + "; ".join(did_well[:3]))

    # Tip
    if next_tip:
        parts.append(f"Tip: {next_tip}")

    # Summary — the evaluator's free-text gloss. Included so the day-level
    # note (and per-activity retrieval) has the full narrative, not just the
    # structured mistake list.
    if summary:
        parts.append(f"Summary: {summary.strip()}")

    return "\n".join(parts)


def build_session_memory(
    *,
    day_id: str,
    activities_summary: list[dict],
    points_earned: dict[str, int],
    mentor_note: str,
) -> str:
    """Build a compact text document for a session-level summary.

    Example output::

        Session: day_24_01_03 | Activities: 4
        Scores: Read (8/10), Write (5/10), Listen (7/10), Speak (6/10)
        Points earned: grammar=120, vocabulary=80, fluency=55
        Mentor note: You keep mixing up articles with countable nouns...
    """
    parts: list[str] = []

    parts.append(f"Session: {day_id} | Activities: {len(activities_summary)}")

    # Per-activity scores
    if activities_summary:
        score_strs = [
            f"{a.get('archetype_label', a.get('archetype_id', '?'))} "
            f"({a.get('raw_score', '?')}/10)"
            for a in activities_summary[:6]
        ]
        parts.append("Scores: " + ", ".join(score_strs))

    # Points earned
    if points_earned:
        nonzero = {k: v for k, v in points_earned.items() if v > 0}
        if nonzero:
            pts_strs = [f"{k}={v}" for k, v in sorted(nonzero.items())]
            parts.append("Points earned: " + ", ".join(pts_strs))

    # Mentor note
    if mentor_note:
        # Truncate long notes to keep the embedding focused
        truncated = mentor_note[:500]
        parts.append(f"Mentor note: {truncated}")

    return "\n".join(parts)
