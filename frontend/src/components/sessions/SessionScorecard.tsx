"use client";

/**
 * Terminal scorecard view for a completed session.
 *
 * Renders the spec §14 session-end summary: per-sub-skill earnings,
 * new totals, and dashboard movement. Uses `display_label` shipped with
 * the scorecard (Phase 5) to render friendly labels for the 7 sub-skills.
 */

import type { SessionScorecardRead } from "@/lib/sessions-api";
import { getSkillLabel, SKILL_ORDER } from "@/lib/skill-labels";


interface Props {
  scorecard: SessionScorecardRead;
  onDone?: () => void;
}

export function SessionScorecard({ scorecard, onDone }: Props) {
  const {
    points_earned,
    subskill_totals_after,
    dashboard_after,
    skill_labels,
    points_applied,
  } = scorecard;

  // Render rows in canonical SKILL_ORDER. Skills present in the scorecard
  // but unknown to SKILL_ORDER are tail-appended.
  const known = SKILL_ORDER.filter((k) => k in points_earned);
  const extras = Object.keys(points_earned).filter((k) => !known.includes(k));
  const skillRows = [...known, ...extras];

  return (
    <section
      style={{
        background: "white",
        borderRadius: 12,
        padding: 24,
        border: "1px solid oklch(88% 0.03 245)",
        display: "flex",
        flexDirection: "column",
        gap: 20,
      }}
    >
      <header>
        <h2 style={{ margin: 0, fontSize: 22, fontWeight: 800 }}>Session complete</h2>
        <p style={{ margin: "4px 0 0", fontSize: 14, color: "oklch(40% 0.07 240)" }}>
          {points_applied
            ? "Points added to your dashboard."
            : "Practice run — no new points (you already completed today's session)."}
        </p>
      </header>

      <div role="table" aria-label="Sub-skill scoreboard">
        <div
          role="row"
          style={{
            display: "grid",
            gridTemplateColumns: "1.4fr 1fr 1fr 1fr",
            gap: 12,
            padding: "8px 12px",
            fontSize: 12,
            textTransform: "uppercase",
            letterSpacing: 0.5,
            color: "oklch(40% 0.07 240)",
            borderBottom: "1px solid oklch(92% 0.03 240)",
          }}
        >
          <div>Sub-skill</div>
          <div style={{ textAlign: "right" }}>Earned</div>
          <div style={{ textAlign: "right" }}>Total</div>
          <div style={{ textAlign: "right" }}>Dashboard</div>
        </div>

        {skillRows.map((skill) => {
          const earned = points_earned[skill] ?? 0;
          const total = subskill_totals_after[skill] ?? 0;
          const dash = dashboard_after[skill] ?? 0;
          return (
            <div
              key={skill}
              role="row"
              style={{
                display: "grid",
                gridTemplateColumns: "1.4fr 1fr 1fr 1fr",
                gap: 12,
                padding: "10px 12px",
                alignItems: "center",
                borderBottom: "1px solid oklch(96% 0.02 240)",
                fontSize: 14,
              }}
            >
              <div style={{ fontWeight: 600 }}>
                {getSkillLabel(skill, skill_labels)}
              </div>
              <div
                style={{
                  textAlign: "right",
                  fontWeight: 700,
                  color: earned > 0 ? "oklch(40% 0.16 155)" : "oklch(50% 0.04 240)",
                }}
              >
                {earned > 0 ? `+${earned}` : "0"}
              </div>
              <div style={{ textAlign: "right", color: "oklch(40% 0.07 240)" }}>
                {total}
              </div>
              <div style={{ textAlign: "right", fontWeight: 700 }}>
                {dash.toFixed(1)}
              </div>
            </div>
          );
        })}
      </div>

      {onDone && (
        <button
          type="button"
          onClick={onDone}
          style={{
            alignSelf: "flex-start",
            background: "oklch(52% 0.18 240)",
            color: "white",
            fontWeight: 600,
            padding: "12px 22px",
            borderRadius: 8,
            border: "none",
            cursor: "pointer",
            fontSize: 15,
          }}
        >
          Back to dashboard
        </button>
      )}
    </section>
  );
}
