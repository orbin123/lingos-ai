"use client";

/**
 * Inline progress indicator for a session's activities.
 *
 * Renders a row of dots — one per attempt in the session skeleton — with
 * visual state for past / current / future activities. Lightweight; no
 * navigation behaviour (the shell drives ordering).
 */

import type { AttemptSkeleton } from "@/lib/sessions-api";


interface Props {
  attempts: AttemptSkeleton[];
  currentSequence: number | null;
}

export function SessionActivityNav({ attempts, currentSequence }: Props) {
  return (
    <nav
      aria-label="Session progress"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        flexWrap: "wrap",
      }}
    >
      {attempts.map((attempt) => {
        const isPast = attempt.status === "evaluated";
        const isCurrent = currentSequence === attempt.sequence;
        const isFuture = !isPast && !isCurrent;
        const bg = isPast
          ? "oklch(48% 0.18 155)" // green — done
          : isCurrent
            ? "oklch(52% 0.18 240)" // blue — active
            : "oklch(90% 0.02 240)"; // grey — pending
        const color = isFuture ? "oklch(40% 0.07 240)" : "white";
        return (
          <div
            key={attempt.sequence}
            title={`Activity ${attempt.sequence} — ${attempt.archetype_id}${
              attempt.is_mandatory ? "" : " (optional)"
            }`}
            style={{
              width: 28,
              height: 28,
              borderRadius: 14,
              background: bg,
              color,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 12,
              fontWeight: 700,
              border: isCurrent
                ? "2px solid oklch(35% 0.16 240)"
                : "1px solid oklch(85% 0.04 245)",
            }}
          >
            {attempt.sequence}
          </div>
        );
      })}
    </nav>
  );
}
