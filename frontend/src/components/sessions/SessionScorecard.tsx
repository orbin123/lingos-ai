"use client";

/**
 * Terminal scorecard view for a completed session.
 *
 * Two stacked sections:
 *   1. Activity tiles — one per attempt, showing raw_score / 10 + tier
 *      badge + base_reward pts. Order follows the planned sequence.
 *   2. Sub-skill grid — one cell per canonical sub-skill with
 *      per-session points earned + new dashboard value. Iterates over
 *      SKILL_ORDER so every cell renders even when earned is 0.
 */

import type { ActivityBreakdown, SessionScorecardRead } from "@/lib/sessions-api";
import { getSkillLabel, SKILL_ORDER } from "@/lib/skill-labels";


interface Props {
  scorecard: SessionScorecardRead;
  onDone?: () => void;
}

const TIER_COLORS: Record<string, { bg: string; fg: string; label: string }> = {
  excellent: { bg: "oklch(94% 0.06 155)", fg: "oklch(35% 0.18 155)", label: "Excellent" },
  good:      { bg: "oklch(94% 0.06 210)", fg: "oklch(35% 0.18 240)", label: "Good" },
  average:   { bg: "oklch(95% 0.05 90)",  fg: "oklch(40% 0.14 75)",  label: "Average" },
  poor:      { bg: "oklch(94% 0.06 40)",  fg: "oklch(40% 0.16 30)",  label: "Poor" },
  very_poor: { bg: "oklch(94% 0.06 25)",  fg: "oklch(40% 0.16 25)",  label: "Very Poor" },
};

export function SessionScorecard({ scorecard, onDone }: Props) {
  const {
    points_earned,
    dashboard_after,
    skill_labels,
    points_applied,
    activities,
  } = scorecard;

  const orderedActivities = [...(activities ?? [])].sort(
    (a, b) => a.sequence - b.sequence,
  );

  return (
    <section
      style={{
        background: "white",
        borderRadius: 16,
        padding: "clamp(24px, 4vw, 42px)",
        border: "1px solid oklch(88% 0.03 245)",
        display: "flex",
        flexDirection: "column",
        gap: 34,
        width: "100%",
        boxSizing: "border-box",
      }}
    >
      <header style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <h2
          style={{
            margin: 0,
            fontSize: "clamp(30px, 4vw, 42px)",
            lineHeight: 1.05,
            fontWeight: 800,
            color: "oklch(17% 0.08 245)",
          }}
        >
          Session complete
        </h2>
        <p style={{ margin: 0, fontSize: 20, color: "oklch(35% 0.09 240)" }}>
          {points_applied
            ? "Points added to your dashboard."
            : "Practice run — no new points (you already completed today's session)."}
        </p>
      </header>

      {orderedActivities.length > 0 && (
        <ActivitiesRow activities={orderedActivities} />
      )}

      <SubSkillGrid
        pointsEarned={points_earned}
        skillLabels={skill_labels}
      />

      {onDone && (
        <button
          type="button"
          onClick={onDone}
          style={{
            alignSelf: "flex-start",
            background: "oklch(52% 0.18 240)",
            color: "white",
            fontWeight: 700,
            padding: "16px 34px",
            borderRadius: 8,
            border: "none",
            cursor: "pointer",
            fontSize: 21,
            minHeight: 64,
          }}
        >
          Back to dashboard
        </button>
      )}
    </section>
  );
}


function ActivitiesRow({ activities }: { activities: ActivityBreakdown[] }) {
  return (
    <div>
      <div
        style={{
          fontSize: 12,
          textTransform: "uppercase",
          letterSpacing: 0,
          color: "oklch(40% 0.07 240)",
          marginBottom: 18,
        }}
      >
        Activity scores
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
          gap: 18,
        }}
        className="scorecard-activities"
      >
        {activities.map((a) => {
          const tier = TIER_COLORS[a.tier] ?? {
            bg: "oklch(94% 0.02 240)",
            fg: "oklch(40% 0.07 240)",
            label: a.tier,
          };
          return (
            <div
              key={a.attempt_id}
              style={{
                border: "1px solid oklch(92% 0.02 240)",
                borderRadius: 10,
                padding: "24px 18px",
                display: "flex",
                flexDirection: "column",
                gap: 16,
                alignItems: "center",
                justifyContent: "center",
                textAlign: "center",
                background: "oklch(99% 0.005 240)",
                minHeight: 224,
                boxSizing: "border-box",
              }}
            >
              <div
                style={{
                  fontSize: 18,
                  fontWeight: 700,
                  color: "oklch(40% 0.07 240)",
                  minHeight: 46,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  lineHeight: 1.15,
                  overflowWrap: "anywhere",
                  wordBreak: "normal",
                }}
                title={a.archetype_id}
              >
                {a.archetype_label}
              </div>
              <div
                style={{
                  fontSize: 34,
                  fontWeight: 800,
                  color: "oklch(25% 0.07 240)",
                  lineHeight: 1,
                }}
              >
                {a.raw_score.toFixed(1)}
                <span style={{ fontSize: 22, fontWeight: 600, color: "oklch(50% 0.04 240)" }}>
                  {" / 10"}
                </span>
              </div>
              <div
                style={{
                  display: "inline-block",
                  fontSize: 13,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: 0,
                  padding: "7px 13px",
                  borderRadius: 999,
                  background: tier.bg,
                  color: tier.fg,
                }}
              >
                {tier.label}
              </div>
              <div style={{ fontSize: 18, color: "oklch(40% 0.07 240)" }}>
                +{a.base_reward} pts
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}


interface GridProps {
  pointsEarned: Record<string, number>;
  skillLabels: Record<string, string>;
}

function SubSkillGrid({ pointsEarned, skillLabels }: GridProps) {
  return (
    <div>
      <div
        style={{
          fontSize: 12,
          textTransform: "uppercase",
          letterSpacing: 0,
          color: "oklch(40% 0.07 240)",
          marginBottom: 18,
        }}
      >
        Sub-skill points earned
      </div>
      <div
        role="table"
        aria-label="Sub-skill scoreboard"
        className="scorecard-subskill-grid"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
          gap: 16,
        }}
      >
        {SKILL_ORDER.map((skill) => {
          const earned = pointsEarned[skill] ?? 0;
          const hit = earned > 0;
          return (
            <div
              key={skill}
              role="cell"
              style={{
                border: "1px solid oklch(92% 0.02 240)",
                borderRadius: 10,
                padding: "22px 14px",
                display: "flex",
                flexDirection: "column",
                gap: 22,
                alignItems: "center",
                justifyContent: "center",
                textAlign: "center",
                background: hit ? "oklch(98% 0.02 155)" : "oklch(99% 0.005 240)",
                minWidth: 0,
                minHeight: 132,
                boxSizing: "border-box",
              }}
            >
              <div
                style={{
                  fontSize: 15,
                  fontWeight: 700,
                  color: "oklch(40% 0.07 240)",
                  textTransform: "uppercase",
                  letterSpacing: 0,
                  lineHeight: 1.15,
                  minHeight: 38,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  overflowWrap: "anywhere",
                }}
              >
                {getSkillLabel(skill, skillLabels)}
              </div>
              <div
                style={{
                  fontSize: 34,
                  fontWeight: 800,
                  color: hit ? "oklch(35% 0.18 155)" : "oklch(60% 0.03 240)",
                  lineHeight: 1,
                }}
              >
                {hit ? `+${earned}` : "0"}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
