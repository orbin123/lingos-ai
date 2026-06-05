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

import { useState } from "react";
import type { ActivityBreakdown, SessionScorecardRead } from "@/lib/sessions-api";
import { getSkillLabel, SKILL_ORDER } from "@/lib/skill-labels";
import { MentorNote } from "./MentorNote";

interface Props {
  scorecard: SessionScorecardRead;
  onGoToDashboard?: () => void;
  /** Chat session id — enables the Coach's Note like/dislike control. */
  sessionId?: string;
}

const TIER_COLORS: Record<string, { bg: string; fg: string; label: string }> = {
  excellent: { bg: "oklch(94% 0.06 155)", fg: "oklch(35% 0.18 155)", label: "Excellent" },
  good:      { bg: "oklch(94% 0.06 210)", fg: "oklch(35% 0.18 240)", label: "Good" },
  average:   { bg: "oklch(95% 0.05 90)",  fg: "oklch(40% 0.14 75)",  label: "Average" },
  poor:      { bg: "oklch(94% 0.06 40)",  fg: "oklch(40% 0.16 30)",  label: "Poor" },
  very_poor: { bg: "oklch(94% 0.06 25)",  fg: "oklch(40% 0.16 25)",  label: "Very Poor" },
};

export function SessionScorecard({ scorecard, onGoToDashboard, sessionId }: Props) {
  const {
    points_earned,
    skill_labels,
    points_applied,
    activities,
    mentor_note,
    rag_rating,
  } = scorecard;

  const orderedActivities = [...(activities ?? [])].sort(
    (a, b) => a.sequence - b.sequence,
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", animation: "fadeIn 0.4s ease both" }}>
      <style>{`
        .subskill-row-1 {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 10px;
        }
        .subskill-row-2 {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 10px;
          max-width: calc(75% - 7.5px);
          margin: 0 auto;
          width: 100%;
        }
        @media (max-width: 600px) {
          .subskill-row-1 {
            grid-template-columns: repeat(2, 1fr);
          }
          .subskill-row-2 {
            grid-template-columns: repeat(2, 1fr);
            max-width: 100%;
            margin: 0;
          }
        }
      `}</style>

      {/* 1. Transparent Header (outside the card container to align with chat flows) */}
      <header
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 6,
          marginBottom: 16,
          textAlign: "center",
        }}
      >
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 7,
            padding: "5px 12px",
            borderRadius: 999,
            background: "white",
            border: "1px solid oklch(85% 0.025 240)",
            fontSize: 12,
            fontWeight: 800,
            letterSpacing: "0.03em",
            color: "oklch(40% 0.16 155)",
            boxShadow: "0 2px 8px rgba(80,110,180,0.06)",
            textTransform: "uppercase",
          }}
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
          <span>Session complete</span>
        </div>
        <p
          style={{
            margin: 0,
            fontSize: 14.5,
            fontWeight: 500,
            color: "oklch(35% 0.09 240)",
          }}
        >
          {points_applied
            ? "Points added to your dashboard."
            : "Practice run — no new points (you already completed today's session)."}
        </p>
      </header>

      {/* 2. Main scorecard card matching chat session card styles */}
      <section
        style={{
          background: "linear-gradient(135deg, oklch(95% 0.05 240) 0%, white 70%)",
          borderRadius: 22,
          padding: "20px 24px",
          border: "1.5px solid rgba(255,255,255,0.92)",
          boxShadow: "0 8px 32px rgba(80,110,180,0.14)",
          display: "flex",
          flexDirection: "column",
          gap: 20,
          width: "100%",
          boxSizing: "border-box",
        }}
      >
        {orderedActivities.length > 0 && (
          <ActivitiesRow activities={orderedActivities} />
        )}

        <SubSkillGrid
          pointsEarned={points_earned}
          skillLabels={skill_labels}
        />
      </section>

      {/* 3. Mentor Note (RAG-powered coaching paragraph) */}
      <div style={{ marginTop: 16 }}>
        <MentorNote
          note={mentor_note}
          sessionId={sessionId}
          initialRating={rag_rating ?? null}
        />
      </div>

      {onGoToDashboard && (
        <button
          type="button"
          onClick={onGoToDashboard}
          style={{
            marginTop: 20,
            width: "100%",
            padding: "13px 18px",
            borderRadius: 14,
            border: "none",
            background: "#0070C4",
            color: "white",
            fontFamily: "inherit",
            fontSize: 14,
            fontWeight: 800,
            cursor: "pointer",
            boxShadow: "0 6px 18px rgba(0,112,196,0.22)",
          }}
        >
          Go to dashboard
        </button>
      )}
    </div>
  );
}

function ActivitiesRow({ activities }: { activities: ActivityBreakdown[] }) {
  return (
    <div>
      <div
        style={{
          fontSize: 11.5,
          fontWeight: 700,
          textTransform: "uppercase",
          letterSpacing: "0.04em",
          color: "oklch(45% 0.07 240)",
          marginBottom: 10,
        }}
      >
        Activity scores
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))",
          gap: 12,
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
            <ActivityCard key={a.attempt_id} activity={a} tier={tier} />
          );
        })}
      </div>
    </div>
  );
}

function ActivityCard({
  activity,
  tier,
}: {
  activity: ActivityBreakdown;
  tier: { bg: string; fg: string; label: string };
}) {
  const [hovered, setHovered] = useState(false);

  // Map archetype_id to core activity label: "Read", "Listen", "Write", "Speak"
  const cleanId = activity.archetype_id.toUpperCase();
  let displayLabel = activity.archetype_label;
  if (cleanId.startsWith("READ_")) displayLabel = "Read";
  else if (cleanId.startsWith("WRITE_")) displayLabel = "Write";
  else if (cleanId.startsWith("LISTEN_")) displayLabel = "Listen";
  else if (cleanId.startsWith("SPEAK_")) displayLabel = "Speak";

  return (
    <div
      style={{
        border: "1px solid oklch(90% 0.03 240)",
        borderRadius: 12,
        padding: "12px 10px",
        display: "flex",
        flexDirection: "column",
        gap: 8,
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        background: hovered ? "oklch(98% 0.01 240)" : "oklch(99% 0.005 240)",
        boxSizing: "border-box",
        boxShadow: hovered ? "0 4px 12px rgba(80,110,180,0.06)" : "0 2px 6px rgba(80,110,180,0.02)",
        transform: hovered ? "translateY(-1px)" : "translateY(0)",
        transition: "all 0.2s ease-in-out",
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div
        style={{
          fontSize: 14,
          fontWeight: 700,
          color: "oklch(35% 0.07 240)",
          minHeight: 20,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          lineHeight: 1.15,
        }}
        title={activity.archetype_label}
      >
        {displayLabel}
      </div>
      <div
        style={{
          fontSize: 22,
          fontWeight: 800,
          color: "oklch(20% 0.08 245)",
          lineHeight: 1,
        }}
      >
        {activity.raw_score.toFixed(1)}
        <span style={{ fontSize: 14, fontWeight: 600, color: "oklch(50% 0.04 240)" }}>
          {"/10"}
        </span>
      </div>
      <div
        style={{
          display: "inline-block",
          fontSize: 10.5,
          fontWeight: 800,
          textTransform: "uppercase",
          letterSpacing: "0.02em",
          padding: "3px 9px",
          borderRadius: 999,
          background: tier.bg,
          color: tier.fg,
        }}
      >
        {tier.label}
      </div>
      <div style={{ fontSize: 13, fontWeight: 600, color: "oklch(40% 0.07 240)" }}>
        +{activity.base_reward} pts
      </div>
    </div>
  );
}

interface GridProps {
  pointsEarned: Record<string, number>;
  skillLabels: Record<string, string>;
}

function SubSkillGrid({ pointsEarned, skillLabels }: GridProps) {
  const row1 = SKILL_ORDER.slice(0, 4);
  const row2 = SKILL_ORDER.slice(4, 7);

  return (
    <div>
      <div
        style={{
          fontSize: 11.5,
          fontWeight: 700,
          textTransform: "uppercase",
          letterSpacing: "0.04em",
          color: "oklch(45% 0.07 240)",
          marginBottom: 10,
        }}
      >
        Sub-skill points earned
      </div>
      
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {/* Row 1: 4 columns */}
        <div className="subskill-row-1">
          {row1.map((skill) => {
            const earned = pointsEarned[skill] ?? 0;
            return (
              <SubSkillCell
                key={skill}
                skill={skill}
                earned={earned}
                skillLabels={skillLabels}
              />
            );
          })}
        </div>

        {/* Row 2: 3 columns, centered */}
        <div className="subskill-row-2">
          {row2.map((skill) => {
            const earned = pointsEarned[skill] ?? 0;
            return (
              <SubSkillCell
                key={skill}
                skill={skill}
                earned={earned}
                skillLabels={skillLabels}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
}

function SubSkillCell({
  skill,
  earned,
  skillLabels,
}: {
  skill: string;
  earned: number;
  skillLabels: Record<string, string>;
}) {
  const [hovered, setHovered] = useState(false);
  const hit = earned > 0;
  return (
    <div
      role="cell"
      style={{
        border: "1px solid oklch(90% 0.03 240)",
        borderRadius: 12,
        padding: "10px 6px",
        display: "flex",
        flexDirection: "column",
        gap: 6,
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        background: hit
          ? hovered
            ? "oklch(96% 0.04 155)"
            : "oklch(97% 0.03 155)"
          : hovered
            ? "oklch(98% 0.01 240)"
            : "oklch(99% 0.005 240)",
        minWidth: 0,
        boxSizing: "border-box",
        boxShadow: hovered ? "0 4px 10px rgba(80,110,180,0.04)" : "0 2px 6px rgba(80,110,180,0.01)",
        transform: hovered ? "translateY(-1px)" : "translateY(0)",
        transition: "all 0.2s ease-in-out",
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div
        style={{
          fontSize: 10,
          fontWeight: 800,
          color: "oklch(45% 0.07 240)",
          textTransform: "uppercase",
          letterSpacing: "0.02em",
          lineHeight: 1.2,
          minHeight: 28,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          overflowWrap: "break-word",
          wordBreak: "keep-all",
        }}
      >
        {getSkillLabel(skill, skillLabels)}
      </div>
      <div
        style={{
          fontSize: 20,
          fontWeight: 800,
          color: hit ? "oklch(35% 0.18 155)" : "oklch(60% 0.03 240)",
          lineHeight: 1,
        }}
      >
        {hit ? `+${earned}` : "0"}
      </div>
    </div>
  );
}
