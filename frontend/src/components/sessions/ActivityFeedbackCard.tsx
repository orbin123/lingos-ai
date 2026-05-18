"use client";

/**
 * Inline feedback card shown after the user submits an activity.
 *
 * Renders the structured feedback shape from the spec §14:
 *   summary, did_well[], mistakes[], next_tip, sub_skill_breakdown.
 *
 * Uses `display_label` (Phase 5) when available — falls back to the
 * shared client-side label map otherwise.
 */

import type { FeedbackRead } from "@/lib/sessions-api";
import { getSkillLabel } from "@/lib/skill-labels";


interface Props {
  feedback: FeedbackRead;
  /**
   * Optional `{skill_name: display_label}` map. Pass scorecard.skill_labels
   * if you have it; otherwise the fallback in `@/lib/skill-labels` is used.
   */
  skillLabels?: Record<string, string>;
  onContinue?: () => void;
}

export function ActivityFeedbackCard({ feedback, skillLabels, onContinue }: Props) {
  const { score, summary, did_well, mistakes, next_tip, sub_skill_breakdown } = feedback;

  return (
    <section
      style={{
        background: "white",
        borderRadius: 12,
        padding: 20,
        border: "1px solid oklch(88% 0.03 245)",
        display: "flex",
        flexDirection: "column",
        gap: 16,
      }}
    >
      <header style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <ScoreBadge score={score} />
        <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0 }}>{summary}</h3>
      </header>

      {did_well.length > 0 && (
        <div>
          <h4 style={sectionHeaderStyle}>What worked</h4>
          <ul style={listStyle}>
            {did_well.map((line, i) => (
              <li key={i} style={lineStyle}>{line}</li>
            ))}
          </ul>
        </div>
      )}

      {mistakes.length > 0 && (
        <div>
          <h4 style={sectionHeaderStyle}>To fix</h4>
          <ul style={{ ...listStyle, gap: 12 }}>
            {mistakes.map((m, i) => (
              <li
                key={i}
                style={{
                  ...lineStyle,
                  background: "oklch(96% 0.03 25)",
                  borderRadius: 8,
                  padding: 12,
                  border: "1px solid oklch(88% 0.06 25)",
                }}
              >
                {m.user_wrote && (
                  <div style={{ fontSize: 13, marginBottom: 4 }}>
                    <em>You wrote:</em> &quot;{m.user_wrote}&quot;
                  </div>
                )}
                <div style={{ fontWeight: 600 }}>{m.issue}</div>
                {m.correction && (
                  <div style={{ fontSize: 13, marginTop: 4 }}>
                    <em>Better:</em> &quot;{m.correction}&quot;
                  </div>
                )}
                {m.rule && (
                  <div style={{ fontSize: 13, marginTop: 4, color: "oklch(40% 0.06 240)" }}>
                    {m.rule}
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {next_tip && (
        <div
          style={{
            background: "oklch(96% 0.04 240)",
            padding: 12,
            borderRadius: 8,
            fontSize: 14,
          }}
        >
          <strong>Next: </strong>{next_tip}
        </div>
      )}

      {Object.keys(sub_skill_breakdown).length > 0 && (
        <div>
          <h4 style={sectionHeaderStyle}>Sub-skill scores</h4>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {Object.entries(sub_skill_breakdown).map(([skill, value]) => (
              <span
                key={skill}
                style={{
                  background: "oklch(94% 0.03 240)",
                  padding: "4px 10px",
                  borderRadius: 999,
                  fontSize: 13,
                  fontWeight: 600,
                }}
              >
                {getSkillLabel(skill, skillLabels)}: {value}/10
              </span>
            ))}
          </div>
        </div>
      )}

      {onContinue && (
        <button
          type="button"
          onClick={onContinue}
          style={{
            alignSelf: "flex-start",
            background: "oklch(52% 0.18 240)",
            color: "white",
            fontWeight: 600,
            padding: "10px 18px",
            borderRadius: 8,
            border: "none",
            cursor: "pointer",
          }}
        >
          Continue
        </button>
      )}
    </section>
  );
}


function ScoreBadge({ score }: { score: number }) {
  const bg =
    score >= 8 ? "oklch(48% 0.18 155)" :
    score >= 6 ? "oklch(52% 0.18 240)" :
    score >= 4 ? "oklch(60% 0.13 80)"  :
                 "oklch(58% 0.2 15)";
  return (
    <div
      style={{
        background: bg,
        color: "white",
        borderRadius: 8,
        padding: "6px 10px",
        fontWeight: 800,
        minWidth: 48,
        textAlign: "center",
      }}
    >
      {score}/10
    </div>
  );
}


const sectionHeaderStyle: React.CSSProperties = {
  fontSize: 13,
  textTransform: "uppercase",
  letterSpacing: 0.5,
  color: "oklch(40% 0.07 240)",
  margin: "0 0 8px 0",
};

const listStyle: React.CSSProperties = {
  listStyle: "none",
  padding: 0,
  margin: 0,
  display: "flex",
  flexDirection: "column",
  gap: 6,
};

const lineStyle: React.CSSProperties = {
  fontSize: 14,
  lineHeight: 1.5,
};
