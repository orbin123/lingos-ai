"use client";

/**
 * Coach's Note — personalized RAG-powered mentor feedback.
 *
 * Appears below the session scorecard in the chat flow. Two states:
 *   1. **note provided** → warm-toned card with the coaching paragraph
 *   2. **note missing**  → muted fallback card explaining the note
 *      couldn't be generated (network issue, first run, etc.)
 */

import { useState } from "react";

import { ReactionBar } from "@/components/chat/feedback/ReactionBar";
import type { ReactionValue } from "@/lib/feedback-api";

interface Props {
  /** The mentor note text, or null/undefined when RAG failed. */
  note?: string | null;
  /** Scorecard id — when present, enables the like/dislike control. */
  scorecardId?: number | null;
  /** The viewer's existing reaction, hydrated from the scorecard. */
  userReaction?: ReactionValue | null;
}

/* ── Fallback icon (cloud-off style) ───────────────────────────── */
function UnavailableIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M2 2l20 20" />
      <path d="M9.9 4.24A7.5 7.5 0 0 1 20 10.5c0 1.1-.24 2.14-.67 3.08" />
      <path d="M6.73 6.73A7.5 7.5 0 0 0 5 10.5a5.5 5.5 0 0 0-1.5 10H17" />
    </svg>
  );
}

/* ── Graduation cap icon ───────────────────────────────────────── */
function GradCapIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="oklch(40% 0.14 50)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
      <path d="M6 12v5c3 3 9 3 12 0v-5" />
    </svg>
  );
}

export function MentorNote({ note, scorecardId = null, userReaction = null }: Props) {
  const [hovered, setHovered] = useState(false);

  const hasNote = typeof note === "string" && note.trim().length > 0;

  // ── Fallback state ────────────────────────────────────────────
  if (!hasNote) {
    return (
      <div
        style={{
          animation: "fadeIn 0.5s ease both",
          animationDelay: "0.3s",
        }}
      >
        <section
          style={{
            background:
              "linear-gradient(135deg, oklch(96% 0.01 240) 0%, oklch(99% 0.005 240) 70%)",
            borderRadius: 22,
            padding: "20px 24px",
            border: "1.5px solid oklch(92% 0.015 240)",
            boxShadow: "0 4px 14px rgba(100, 120, 160, 0.06)",
            display: "flex",
            flexDirection: "column",
            gap: 12,
            width: "100%",
            boxSizing: "border-box",
          }}
        >
          {/* Header */}
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div
              style={{
                width: 28,
                height: 28,
                borderRadius: 8,
                background: "oklch(92% 0.015 240)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                color: "oklch(55% 0.04 240)",
              }}
            >
              <UnavailableIcon />
            </div>
            <span
              style={{
                fontSize: 11.5,
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: "0.04em",
                color: "oklch(55% 0.04 240)",
              }}
            >
              Coach&apos;s Note
            </span>
          </div>

          {/* Fallback message */}
          <p
            style={{
              margin: 0,
              fontSize: 13.5,
              lineHeight: 1.6,
              color: "oklch(45% 0.03 240)",
              fontWeight: 400,
              fontStyle: "italic",
            }}
          >
            Your personalized coaching feedback couldn&apos;t be generated right
            now. Don&apos;t worry — your scores and progress are saved.
            Complete your next session to receive tailored mentor notes.
          </p>
        </section>
      </div>
    );
  }

  // ── Normal note state ─────────────────────────────────────────
  return (
    <div
      style={{
        animation: "fadeIn 0.5s ease both",
        animationDelay: "0.3s",
      }}
    >
      <section
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          background: hovered
            ? "linear-gradient(135deg, oklch(94.5% 0.045 50) 0%, oklch(99% 0.01 60) 70%)"
            : "linear-gradient(135deg, oklch(95.5% 0.04 50) 0%, oklch(99.5% 0.005 60) 70%)",
          borderRadius: 22,
          padding: "20px 24px",
          border: "1.5px solid oklch(90% 0.04 50)",
          boxShadow: hovered
            ? "0 8px 28px rgba(180, 140, 60, 0.12)"
            : "0 6px 20px rgba(180, 140, 60, 0.08)",
          display: "flex",
          flexDirection: "column",
          gap: 14,
          width: "100%",
          boxSizing: "border-box",
          transform: hovered ? "translateY(-1px)" : "translateY(0)",
          transition: "all 0.25s ease-in-out",
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: "oklch(90% 0.06 50)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <GradCapIcon />
          </div>
          <span
            style={{
              fontSize: 11.5,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: "0.04em",
              color: "oklch(40% 0.12 50)",
            }}
          >
            Coach&apos;s Note
          </span>
        </div>

        {/* Note content */}
        <p
          style={{
            margin: 0,
            fontSize: 14.5,
            lineHeight: 1.65,
            color: "oklch(22% 0.04 240)",
            fontWeight: 450,
          }}
        >
          {note}
        </p>

        {/* Copy + 👍/👎 reaction on the Coach's Note. */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            paddingTop: 12,
            borderTop: "1px solid oklch(90% 0.04 50)",
          }}
        >
          <span
            style={{
              fontSize: 12,
              fontWeight: 700,
              color: "oklch(45% 0.06 50)",
            }}
          >
            Was this helpful?
          </span>
          <ReactionBar
            feedbackType="COACH_NOTE"
            feedbackId={scorecardId}
            initialReaction={userReaction}
            copyText={note ?? ""}
            align="start"
          />
        </div>
      </section>
    </div>
  );
}
