"use client";

import { useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { authApi } from "@/lib/auth-api";
import { progressApi, type DifficultyDistribution, type RecentActivity, type SkillScoreSnapshot } from "@/lib/progress-api";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { ScoreProgressionChart } from "@/components/stats/ScoreProgressionChart";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useAuthStore } from "@/store/authStore";

// ─── CSS vars / tokens (matching existing app palette) ────────────────────────
const T = {
  navy: "oklch(20% 0.09 245)",
  ink: "oklch(18% 0.06 240)",
  inkMuted: "oklch(45% 0.07 240)",
  line: "oklch(86% 0.025 240)",
  primary: "#0070C4",
  primaryDeep: "#00599e",
  primarySoft: "#d6e8f7",
  green: "oklch(58% 0.16 155)",
  red: "oklch(58% 0.2 25)",
  amber: "oklch(72% 0.16 65)",
  bg: "oklch(91% 0.04 245)",
};

// ─── Mocks for sections with no tracking data yet ─────────────────────────────
const MOCK_TIME_PRACTICED = "–";
const MOCK_PRACTICE = [
  { num: "–",   unit: "",    label: "Most active" },
  { num: "–",   unit: "",    label: "Avg session" },
  { num: "–",   unit: "",    label: "Best day" },
  { num: "–",   unit: "",    label: "Per week" },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────
// Axes use the LEGACY backend sub-skill identifiers as keys. The displayed
// label is the friendlier wording shipped via `display_label` in the API
// (and mirrored in `@/lib/skill-labels` for fallback). See Phase 5 of the
// restructure.
const SKILL_AXES = [
  { key: "grammar",       label: "Grammar" },
  { key: "vocabulary",    label: "Vocabulary" },
  { key: "pronunciation", label: "Pronunciation" },
  { key: "fluency",       label: "Fluency" },
  { key: "expression",    label: "Thought Organization" },
  { key: "comprehension", label: "Listening" },
  { key: "tone",          label: "Tone & Social" },
] as const;

const DEFAULT_SCORES = [6, 5, 4, 5.5, 4.5, 5.8, 4.2];

function normalizeSkillName(n: string) {
  return n.toLowerCase().replace(/[_&.]/g, " ").replace(/\s+/g, " ").trim();
}

function displaySkillName(n: string | null) {
  if (!n) return "No data yet";
  const norm = normalizeSkillName(n);
  // Prefer the LEGACY-keyed fallback in `@/lib/skill-labels` for the three
  // sub-skills whose internal identifier differs from their display label.
  if (norm === "expression") return "Thought Organization";
  if (norm === "comprehension") return "Listening";
  if (norm === "tone") return "Tone & Social";
  return norm.split(" ").map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(" ");
}

function axisScores(scores: SkillScoreSnapshot[]) {
  // Exact key match against LEGACY backend identifiers. Components that
  // need the friendlier label should prefer `s.display_label` when present
  // (Phase 5+), then fall back to `axis.label`.
  return SKILL_AXES.map((axis, i) => {
    const match = scores.find(s => s.skill_name === axis.key);
    return {
      label: (match as { display_label?: string } | undefined)?.display_label ?? axis.label,
      score: match?.score ?? DEFAULT_SCORES[i],
      skill_id: match?.skill_id ?? 0,
    };
  });
}

function formatTimestamp(v: string) {
  return new Intl.DateTimeFormat("en", {
    month: "short", day: "numeric", hour: "numeric", minute: "2-digit",
  }).format(new Date(v));
}

function activityChip(taskType: string) {
  const t = taskType.toLowerCase();
  if (t.includes("speak")) return { emoji: "🗣️", label: "Speak" };
  if (t.includes("listen")) return { emoji: "🎧", label: "Listen" };
  if (t.includes("read")) return { emoji: "📖", label: "Read" };
  return { emoji: "✍️", label: "Write" };
}

function scoreColor(score: number): { color: string; bg: string; cls: string } {
  if (score >= 7) return { color: "oklch(35% 0.14 155)", bg: "oklch(94% 0.07 155)", cls: "high" };
  if (score >= 5) return { color: "oklch(42% 0.1 240)", bg: "#d6e8f7", cls: "" };
  return { color: "oklch(40% 0.18 25)", bg: "oklch(94% 0.06 25)", cls: "low" };
}

// ─── SVG Icons ────────────────────────────────────────────────────────────────
const UpArrow = () => (
  <svg width="11" height="11" viewBox="0 0 12 12" fill="none">
    <path d="M3 7.5L6 4.5L9 7.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);
const DownArrow = () => (
  <svg width="11" height="11" viewBox="0 0 12 12" fill="none">
    <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);
const CheckIcon = () => (
  <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
    <path d="M3.5 7.5L6 10L11 4.5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);
const AlertIcon = () => (
  <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
    <path d="M7 4v3.5M7 9.8v.2" stroke="white" strokeWidth="2" strokeLinecap="round"/>
  </svg>
);
const ArrowRight = () => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
    <path d="M6 4l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);
const ArrowOut = () => (
  <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
    <path d="M5 11L11 5M11 5H6M11 5v5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const PulseIcon = () => (
  <span style={{
    display: "inline-block", width: 6, height: 6, borderRadius: "50%",
    background: T.primary, animation: "pulseDot 2s ease infinite",
  }}/>
);

// ─── Card wrapper ─────────────────────────────────────────────────────────────
function Card({
  children,
  style,
}: {
  children: React.ReactNode;
  style?: React.CSSProperties;
}) {
  return (
    <div style={{
      background: "rgba(255,255,255,0.85)",
      backdropFilter: "blur(18px)",
      border: "1.5px solid rgba(255,255,255,0.92)",
      borderRadius: 22,
      padding: 24,
      boxShadow: "0 4px 24px rgba(80,110,180,0.1)",
      marginBottom: 22,
      ...style,
    }}>
      {children}
    </div>
  );
}

function CardHead({ title, sub, right }: { title: React.ReactNode; sub?: string; right?: React.ReactNode }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 18 }}>
      <div>
        <div style={{ fontSize: 17, fontWeight: 800, color: T.navy, letterSpacing: "-0.01em" }}>{title}</div>
        {sub && <div style={{ fontSize: 12.5, color: T.inkMuted, marginTop: 3 }}>{sub}</div>}
      </div>
      {right}
    </div>
  );
}

function AgentTag({ label, tone = "blue" }: { label: string; tone?: "blue" | "green" | "live" }) {
  const styles: Record<string, React.CSSProperties> = {
    blue: { background: T.primarySoft, color: T.primaryDeep },
    green: { background: "oklch(94% 0.07 155)", color: "oklch(35% 0.14 155)" },
    live: { background: T.primarySoft, color: T.primaryDeep },
  };
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6,
      padding: "5px 11px", borderRadius: 999,
      fontSize: 11.5, fontWeight: 700,
      ...styles[tone],
    }}>
      {tone === "live" && <PulseIcon />}
      {label}
    </span>
  );
}

function CardLink({ children, onClick }: { children: React.ReactNode; onClick?: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        fontSize: 13, fontWeight: 700, color: T.primary,
        display: "inline-flex", alignItems: "center", gap: 4,
        background: "none", border: "none", cursor: "pointer",
        padding: 0, fontFamily: "inherit",
      }}
    >
      {children}
    </button>
  );
}

// ─── Radar chart ──────────────────────────────────────────────────────────────
function Radar({ skills }: { skills: Array<{ label: string; score: number }> }) {
  const cx = 180, cy = 180, R = 130;
  const N = skills.length;
  const angle = (i: number) => (Math.PI * 2 * i) / N - Math.PI / 2;
  const point = (val: number, i: number): [number, number] => {
    const r = (val / 10) * R;
    return [cx + r * Math.cos(angle(i)), cy + r * Math.sin(angle(i))];
  };
  const polyPath = skills.map((s, i) => point(s.score, i)).map(([x, y]) => `${x},${y}`).join(" ");
  const labels = skills.map((s, i) => {
    const [x, y] = [cx + (R + 24) * Math.cos(angle(i)), cy + (R + 24) * Math.sin(angle(i))];
    return { ...s, x, y };
  });

  return (
    <svg width="360" height="360" viewBox="0 0 360 360" overflow="visible" style={{ display: "block", margin: "0 auto" }}>
      {[2, 4, 6, 8, 10].map(v => {
        const pts = Array.from({ length: N }, (_, i) => {
          const r = (v / 10) * R;
          return `${cx + r * Math.cos(angle(i))},${cy + r * Math.sin(angle(i))}`;
        }).join(" ");
        return <polygon key={v} points={pts} fill="none" stroke="oklch(88% 0.02 240)" strokeWidth="1"/>;
      })}
      {skills.map((_, i) => {
        const [x, y] = point(10, i);
        return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="oklch(88% 0.02 240)" strokeWidth="1"/>;
      })}
      <polygon points={polyPath} fill="rgba(0,112,196,0.18)" stroke="#0070C4" strokeWidth="2.5" strokeLinejoin="round"/>
      {skills.map((s, i) => {
        const [x, y] = point(s.score, i);
        return <circle key={i} cx={x} cy={y} r="4" fill="#0070C4" stroke="white" strokeWidth="2"/>;
      })}
      {labels.map((l, i) => (
        <g key={l.label}>
          <text x={l.x} y={l.y - 2} textAnchor="middle" fontSize="11.5" fill={T.navy} fontWeight="700">{l.label}</text>
          <text x={l.x} y={l.y + 12} textAnchor="middle" fontSize="11" fill="#0070C4" fontWeight="800">{l.score.toFixed(1)}</text>
        </g>
      ))}
    </svg>
  );
}

// ─── Sub-skill bars ───────────────────────────────────────────────────────────
function barGradient(score: number) {
  if (score >= 6.5) return `linear-gradient(to right, oklch(55% 0.16 155), oklch(70% 0.13 145))`;
  if (score < 4.0) return `linear-gradient(to right, oklch(60% 0.18 25), oklch(72% 0.16 35))`;
  return `linear-gradient(to right, ${T.primary}, oklch(72% 0.12 220))`;
}

function SkillBars({
  scores,
  weeklyPts = {},
}: {
  scores: Array<{ label: string; score: number; skill_id: number }>;
  weeklyPts?: Record<number, number>;
}) {
  const sorted = [...scores].sort((a, b) => b.score - a.score);

  return (
    <div>
      {sorted.map(s => {
        const pts = weeklyPts[s.skill_id] ?? 0;
        return (
          <div key={s.skill_id || s.label} style={{
            display: "flex", alignItems: "center", gap: 14, padding: "13px 0",
            borderBottom: `1px dashed oklch(88% 0.02 240)`,
          }}>
            <span style={{ fontSize: 13.5, fontWeight: 600, color: T.navy, width: 110, flexShrink: 0 }}>{s.label}</span>
            <div style={{ flex: 1, height: 8, borderRadius: 8, background: "oklch(94% 0.02 240)", overflow: "hidden" }}>
              <div style={{ height: "100%", borderRadius: 8, width: `${s.score * 10}%`, background: barGradient(s.score), transition: "width 0.6s ease" }}/>
            </div>
            <span style={{ fontSize: 13.5, fontWeight: 800, color: T.navy, width: 36, textAlign: "right" }}>{s.score.toFixed(1)}</span>
            <span style={{
              fontSize: 10.5, fontWeight: 700, padding: "3px 6px", borderRadius: 6, minWidth: 64, textAlign: "center",
              background: pts > 0 ? "oklch(94% 0.07 155)" : "oklch(95% 0.015 240)",
              color: pts > 0 ? "oklch(38% 0.14 155)" : T.inkMuted,
            }}>
              {pts > 0 ? `+${pts}` : "—"} pts
            </span>
          </div>
        );
      })}
    </div>
  );
}

// ─── Activity rows ─────────────────────────────────────────────────────────────
function ActivityRow({ activity, onClick }: { activity: RecentActivity; onClick: () => void }) {
  const { color, bg } = scoreColor(activity.score);
  const chip = activityChip(activity.task_type);
  const iconBg: Record<string, string> = {
    "🗣️": "oklch(94% 0.06 240)",
    "🎧": "oklch(94% 0.07 155)",
    "📖": "oklch(94% 0.06 290)",
    "✍️": "oklch(94% 0.07 65)",
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => e.key === "Enter" && onClick()}
      style={{
        display: "flex", alignItems: "center", gap: 14,
        padding: "14px 16px", borderRadius: 14,
        background: "white", border: `1.5px solid ${T.line}`,
        marginBottom: 8, transition: "all 0.15s", cursor: "pointer",
      }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLDivElement).style.borderColor = T.primary;
        (e.currentTarget as HTMLDivElement).style.transform = "translateY(-1px)";
        (e.currentTarget as HTMLDivElement).style.boxShadow = "0 4px 14px rgba(0,112,196,0.1)";
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLDivElement).style.borderColor = T.line;
        (e.currentTarget as HTMLDivElement).style.transform = "";
        (e.currentTarget as HTMLDivElement).style.boxShadow = "";
      }}
    >
      <div style={{
        width: 38, height: 38, borderRadius: 10, flexShrink: 0,
        display: "flex", alignItems: "center", justifyContent: "center",
        background: iconBg[chip.emoji] ?? "oklch(94% 0.025 240)",
        fontSize: 18,
      }}>
        {chip.emoji}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: T.navy }}>{activity.task_name}</div>
        <div style={{ fontSize: 12, color: T.inkMuted, marginTop: 2, display: "flex", gap: 8, flexWrap: "wrap" }}>
          <span>{chip.label}</span>
          <span>·</span>
          <span>{formatTimestamp(activity.completed_at)}</span>
          {activity.mistake_count > 0 && <><span>·</span><span>{activity.mistake_count} mistakes</span></>}
        </div>
      </div>
      <span style={{
        fontSize: 12, fontWeight: 800, padding: "4px 10px", borderRadius: 8,
        background: bg, color, flexShrink: 0,
      }}>
        {activity.score.toFixed(1)}
      </span>
    </div>
  );
}

function MockActivityRow({ title, meta, scoreStr, scoreColor: sc }: {
  title: string; meta: string[]; scoreStr: string; scoreColor: { bg: string; color: string };
}) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 14,
      padding: "14px 16px", borderRadius: 14,
      background: "white", border: `1.5px solid ${T.line}`,
      marginBottom: 8,
    }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: T.navy }}>{title}</div>
        <div style={{ fontSize: 12, color: T.inkMuted, marginTop: 2, display: "flex", gap: 6, flexWrap: "wrap" }}>
          {meta.map((m, j) => <span key={j}>{j > 0 && "· "}{m}</span>)}
        </div>
      </div>
      <span style={{
        fontSize: 12, fontWeight: 800, padding: "4px 10px", borderRadius: 8,
        background: sc.bg, color: sc.color, flexShrink: 0,
      }}>
        {scoreStr}
      </span>
    </div>
  );
}

// ─── Insights (strengths / focus) ─────────────────────────────────────────────
function InsightRow({ text, meta, tone }: { text: React.ReactNode; meta: string; tone: "ok" | "no" }) {
  const isOk = tone === "ok";
  return (
    <div style={{
      display: "flex", alignItems: "flex-start", gap: 8,
      padding: "11px 0", borderBottom: `1px dashed oklch(88% 0.02 240)`,
      fontSize: 13.5,
    }}>
      <div style={{
        flexShrink: 0, width: 22, height: 22, borderRadius: "50%",
        display: "flex", alignItems: "center", justifyContent: "center",
        background: isOk ? T.green : T.red, marginTop: 1,
      }}>
        {isOk ? <CheckIcon/> : <AlertIcon/>}
      </div>
      <div>
        <div style={{ color: T.navy, lineHeight: 1.5 }}>{text}</div>
        <div style={{ fontSize: 11.5, color: T.inkMuted, marginTop: 2 }}>{meta}</div>
      </div>
    </div>
  );
}

// ─── Goal card ────────────────────────────────────────────────────────────────
function GoalCard({ courseLengthStr, currentWeek }: { courseLengthStr?: string, currentWeek?: number }) {
  const totalWeeks = courseLengthStr === "48w" ? 48 : 24;
  const week = currentWeek || 1;
  const stageLength = totalWeeks / 3;

  let targetWeek = stageLength;
  let targetStage = "intermediate";

  if (week <= stageLength) {
    targetWeek = stageLength;
    targetStage = "intermediate";
  } else if (week <= stageLength * 2) {
    targetWeek = stageLength * 2;
    targetStage = "advanced";
  } else {
    targetWeek = totalWeeks;
    targetStage = "completion";
  }

  const titleText = targetStage === "completion" 
    ? `Complete course by Week ${totalWeeks}` 
    : `Reach ${targetStage} by Week ${targetWeek}`;

  const pct = Math.min(100, Math.round((week / targetWeek) * 100));

  return (
    <div style={{
      background: `linear-gradient(135deg, ${T.primary}, oklch(45% 0.2 250))`,
      color: "white", borderRadius: 22, padding: 22,
      position: "relative", overflow: "hidden",
      boxShadow: "0 8px 28px rgba(0,112,196,0.28)",
      marginBottom: 22,
    }}>
      <div style={{
        position: "absolute", top: -40, right: -30,
        width: 160, height: 160, borderRadius: "50%",
        background: "rgba(255,255,255,0.1)",
      }}/>
      <div style={{ fontSize: 12.5, fontWeight: 700, opacity: 0.85, letterSpacing: "0.04em", textTransform: "uppercase" }}>
        {totalWeeks}-week milestone
      </div>
      <div style={{ fontSize: 20, fontWeight: 800, letterSpacing: "-0.02em", margin: "8px 0 14px", lineHeight: 1.25, position: "relative", zIndex: 1 }}>
        {titleText}
      </div>
      <div style={{ position: "relative", zIndex: 1 }}>
        <div style={{ height: 8, background: "rgba(255,255,255,0.25)", borderRadius: 8, overflow: "hidden", margin: "6px 0 10px" }}>
          <div style={{ height: "100%", background: "white", borderRadius: 8, width: `${pct}%`, transition: "width 0.6s ease" }}/>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, opacity: 0.92 }}>
          <span><strong>Week {week}</strong> of {targetWeek}</span>
        </div>
      </div>
    </div>
  );
}

// ─── Donut chart ──────────────────────────────────────────────────────────────
const DIFFICULTY_SLICES = [
  { key: "beginner" as const,     name: "Beginner",     color: "#0070C4" },
  { key: "intermediate" as const, name: "Intermediate", color: "#7c3aed" },
  { key: "advanced" as const,     name: "Advanced",     color: "#f59e0b" },
];

function Donut({ dist }: { dist: DifficultyDistribution | null }) {
  const slices = DIFFICULTY_SLICES.map(s => ({
    ...s,
    count: dist?.[s.key] ?? 0,
    pct: dist && dist.total > 0 ? Math.round((dist[s.key] / dist.total) * 100) : 0,
  }));
  const total = dist?.total ?? 0;
  const r = 52, c = 2 * Math.PI * r;
  let off = 0;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
      <svg width="130" height="130" viewBox="0 0 130 130">
        <circle cx="65" cy="65" r={r} fill="none" stroke="oklch(94% 0.02 240)" strokeWidth="16"/>
        {total > 0 && slices.map((s, i) => {
          const len = (s.count / total) * c;
          const dasharray = `${len} ${c - len}`;
          const dashoffset = -off;
          off += len;
          return (
            <circle key={i} cx="65" cy="65" r={r} fill="none" stroke={s.color} strokeWidth="16"
              strokeDasharray={dasharray} strokeDashoffset={dashoffset}
              transform="rotate(-90 65 65)" strokeLinecap="butt"/>
          );
        })}
        <text x="65" y="62" textAnchor="middle" fontSize="22" fontWeight="800" fill={T.navy} letterSpacing="-1">{total}</text>
        <text x="65" y="78" textAnchor="middle" fontSize="10" fontWeight="700" fill={T.inkMuted}>TASKS</text>
      </svg>
      <div style={{ flex: 1 }}>
        {slices.map(s => (
          <div key={s.name} style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            padding: "7px 0", borderBottom: `1px dashed oklch(88% 0.02 240)`,
            fontSize: 13,
          }}>
            <span style={{ display: "flex", alignItems: "center", gap: 8, color: T.navy, fontWeight: 600 }}>
              <span style={{ width: 10, height: 10, borderRadius: 3, background: s.color, display: "inline-block" }}/>
              {s.name}
            </span>
            <span style={{ fontWeight: 800, color: T.navy }}>{s.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── KPI Tile ─────────────────────────────────────────────────────────────────
function KpiTile({
  label, value, unit, delta, deltaDir,
}: {
  label: string; value: React.ReactNode; unit?: string;
  delta: string; deltaDir: "up" | "down" | "flat";
}) {
  const deltaStyle: Record<string, React.CSSProperties> = {
    up:   { background: "oklch(94% 0.07 155)", color: "oklch(38% 0.14 155)" },
    down: { background: "oklch(94% 0.06 25)",  color: "oklch(40% 0.18 25)" },
    flat: { background: "oklch(95% 0.015 240)",color: T.inkMuted },
  };
  return (
    <div style={{
      background: "rgba(255,255,255,0.85)", backdropFilter: "blur(18px)",
      border: "1.5px solid rgba(255,255,255,0.92)", borderRadius: 18,
      padding: "18px 20px", boxShadow: "0 4px 22px rgba(80,110,180,0.1)",
    }}>
      <div style={{ fontSize: 12.5, fontWeight: 700, color: T.inkMuted, letterSpacing: "0.02em" }}>{label}</div>
      <div style={{
        fontSize: 30, fontWeight: 800, color: T.navy, letterSpacing: "-0.02em",
        lineHeight: 1.1, margin: "6px 0 4px", display: "flex", alignItems: "baseline", gap: 6,
      }}>
        {value}
        {unit && <span style={{ fontSize: 14, fontWeight: 600, color: T.inkMuted }}>{unit}</span>}
      </div>
      <span style={{
        display: "inline-flex", alignItems: "center", gap: 4,
        fontSize: 12, fontWeight: 700, padding: "3px 8px", borderRadius: 6,
        ...deltaStyle[deltaDir],
      }}>
        {deltaDir === "up" && <UpArrow/>}
        {deltaDir === "down" && <DownArrow/>}
        {delta}
      </span>
    </div>
  );
}

// ─── Main page ─────────────────────────────────────────────────────────────────
export default function StatsPage() {
  const router = useRouter();
  const { logout } = useAuthStore();
  const { isReady } = useRequireAuth();

  // Per-attempt detail view is not part of the sessions flow yet. Rows
  // render in read-only mode for now.
  const handleActivityClick = useCallback(() => undefined, []);
  const handleViewAll = useCallback(() => router.push("/stats/activities"), [router]);

  const userQuery = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });

  const statsQuery = useQuery({
    queryKey: ["progress-stats"],
    queryFn: progressApi.getStats,
    enabled: isReady && !!userQuery.data?.diagnosis_completed,
  });

  useEffect(() => {
    if (userQuery.data && !userQuery.data.diagnosis_completed) router.replace("/diagnosis");
  }, [userQuery.data, router]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!isReady) return null;

  const stats = statsQuery.data;
  const weekly = stats?.weekly_snapshot;
  const skillScores = axisScores(stats?.skill_scores ?? []);
  const overallScore = skillScores.length > 0 
    ? skillScores.reduce((sum, s) => sum + s.score, 0) / skillScores.length 
    : 0;
  const change = weekly?.overall_score_change ?? 0;
  const changeUp = change >= 0;
  const strengths = stats?.feedback.strengths ?? [];
  const focusAreas = stats?.feedback.focus_areas ?? [];
  const activities = stats?.recent_activities ?? [];
  const tasksCompleted = weekly?.tasks_completed ?? 0;
  const tasksGoal = weekly?.weekly_task_goal ?? 7;
  const weeklyPts = stats?.weekly_points_by_skill ?? {};
  const historyLabels = stats?.skill_history_labels;
  const skillHistory = stats?.skill_history;
  const difficultyDist = stats?.difficulty_distribution;
  const bestSkill = displaySkillName(weekly?.best_skill_name ?? null);
  const bestScore = weekly?.best_skill_score;

  return (
    <>
      <style>{`
        @keyframes pulseDot { 0%,100% { opacity:1; } 50% { opacity:0.5; } }
        @keyframes fadeIn { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
        .stats-fade { animation: fadeIn 0.4s ease both; }
      `}</style>

      <div style={{
        minHeight: "100vh",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        background: T.bg,
        position: "relative",
      }}>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap"/>
        <div aria-hidden style={{
          position: "fixed", inset: 0, pointerEvents: "none",
          backgroundImage: "radial-gradient(circle, rgba(90,130,210,0.13) 1px, transparent 1px)",
          backgroundSize: "22px 22px", zIndex: 0,
        }}/>

        <div style={{ position: "relative", zIndex: 1 }}>
          <DashboardLayout user={userQuery.data} onSignOut={handleLogout}>
            <main style={{ maxWidth: 1240, margin: "0 auto", padding: "28px 32px 60px" }}>

              {/* ── Page header ── */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 24, flexWrap: "wrap", gap: 16 }}>
                <div>
                  <h1 style={{ fontSize: 28, fontWeight: 800, letterSpacing: "-0.02em", color: T.navy, lineHeight: 1.15, margin: 0 }}>
                    Your stats
                  </h1>
                  <p style={{ fontSize: 14.5, color: T.inkMuted, marginTop: 6 }}>
                    Tracked by the Evaluator Agent · all scores on a 0–10 scale
                  </p>
                </div>

              </div>

              {/* ── KPI row ── */}
              <div className="stats-fade" style={{
                display: "grid",
                gridTemplateColumns: "repeat(4, 1fr)",
                gap: 16, marginBottom: 22,
              }}>
                <KpiTile
                  label="Overall score"
                  value={<>{statsQuery.isLoading ? "…" : overallScore.toFixed(1)}</>}
                  unit="/ 10"
                  delta={change === 0 ? "No change vs last week" : `${changeUp ? "+" : ""}${change.toFixed(1)} vs last week`}
                  deltaDir={change > 0 ? "up" : change < 0 ? "down" : "flat"}
                />
                <KpiTile
                  label="Tasks completed"
                  value={statsQuery.isLoading ? "…" : `${tasksCompleted}`}
                  unit={`/ ${tasksGoal}`}
                  delta={`${tasksGoal > 0 ? Math.round((tasksCompleted / tasksGoal) * 100) : 0}% completion`}
                  deltaDir="up"
                />
                <KpiTile
                  label="Time practiced"
                  value={MOCK_TIME_PRACTICED}
                  delta="+24m vs last week"
                  deltaDir="up"
                />
                <KpiTile
                  label="Best skill"
                  value={<span style={{ fontSize: 24 }}>{statsQuery.isLoading ? "…" : bestSkill}</span>}
                  delta={bestScore != null ? `Scored ${bestScore.toFixed(1)} · highest sub-skill` : "Scored after tasks"}
                  deltaDir="flat"
                />
              </div>

              {/* ── Two-column grid ── */}
              <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 22 }}>

                {/* ── LEFT ── */}
                <div>
                  {/* Score progression */}
                  <Card>
                    <CardHead
                      title="Score progression"
                      sub="Sub-skills tracked daily by Evaluator Agent"
                      right={<AgentTag label="Live" tone="live"/>}
                    />
                    <ScoreProgressionChart labels={historyLabels} series={skillHistory}/>
                  </Card>

                  {/* Sub-skill overview */}
                  <Card>
                    <CardHead
                      title="Sub-skill overview"
                      sub="Updated by Evaluator Agent"
                      right={<CardLink>Drill into a skill <ArrowRight/></CardLink>}
                    />
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, alignItems: "center" }}>
                      <Radar skills={skillScores}/>
                      <SkillBars scores={skillScores} weeklyPts={weeklyPts}/>
                    </div>
                  </Card>

                  {/* Recent activities */}
                  <Card style={{ marginBottom: 0 }}>
                    <CardHead
                      title="Recent activities"
                      sub={`Last ${activities.length || 7} sessions`}
                      right={<CardLink onClick={handleViewAll}>View all <ArrowOut/></CardLink>}
                    />
                    {statsQuery.isLoading ? (
                      <div style={{ padding: 24, color: T.inkMuted, fontSize: 14 }}>Loading activities…</div>
                    ) : activities.length > 0 ? (
                      activities.slice(0, 10).map(a => (
                        <ActivityRow
                          key={a.id}
                          activity={a}
                          onClick={handleActivityClick}
                        />
                      ))
                    ) : (
                      <>
                        <MockActivityRow
                          title="Past simple — chat & drills"
                          meta={["Grammar", "6m 42s", "Today, 9:14 AM"]}
                          scoreStr="6.2"
                          scoreColor={{ bg: "oklch(94% 0.07 155)", color: "oklch(35% 0.14 155)" }}
                        />
                        <MockActivityRow
                          title="Read aloud — workplace email"
                          meta={["Pronunciation", "4m 10s", "Yesterday, 8:02 PM"]}
                          scoreStr="4.0"
                          scoreColor={{ bg: "oklch(94% 0.06 25)", color: "oklch(40% 0.18 25)" }}
                        />
                        <MockActivityRow
                          title="Vocabulary drill — interview verbs"
                          meta={["Vocabulary", "5m 22s", "Yesterday, 7:30 PM"]}
                          scoreStr="5.4"
                          scoreColor={{ bg: T.primarySoft, color: T.primaryDeep }}
                        />
                        <MockActivityRow
                          title="Mock interview — first 3 minutes"
                          meta={["Fluency", "3m 02s", "Wed, 6:48 PM"]}
                          scoreStr="5.5"
                          scoreColor={{ bg: T.primarySoft, color: T.primaryDeep }}
                        />
                      </>
                    )}
                  </Card>
                </div>

                {/* ── RIGHT ── */}
                <div>
                  {/* Strengths */}
                  <Card>
                    <CardHead
                      title={
                        <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <span style={{ width: 8, height: 8, borderRadius: "50%", background: T.green, display: "inline-block" }}/>
                          Your strengths
                        </span>
                      }
                      sub="Where you're outperforming"
                      right={<AgentTag label="Feedback Agent" tone="green"/>}
                    />
                    {strengths.length > 0 ? (
                      strengths.slice(0, 3).map((s, i) => (
                        <InsightRow key={i} text={s} meta="Feedback Agent · sustained" tone="ok"/>
                      ))
                    ) : (
                      <>
                        <InsightRow text={<>Past tense conjugation — <strong>92% accuracy</strong> over 5 sessions.</>} meta="Grammar · sustained" tone="ok"/>
                        <InsightRow text={<>Pronunciation of /θ/ and /ð/ improving — <strong>+12% clarity</strong>.</>} meta="Pronunciation · trending up" tone="ok"/>
                        <InsightRow text={<>Comprehension of formal phrasing tracking at <strong>2.1 above peers</strong>.</>} meta="Listening · benchmark" tone="ok"/>
                      </>
                    )}
                  </Card>

                  {/* Focus areas */}
                  <Card>
                    <CardHead
                      title={
                        <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <span style={{ width: 8, height: 8, borderRadius: "50%", background: T.red, display: "inline-block" }}/>
                          Focus areas
                        </span>
                      }
                      sub="Where extra reps will pay off"
                      right={
                        <span style={{
                          display: "inline-flex", alignItems: "center", gap: 6,
                          padding: "5px 11px", borderRadius: 999,
                          fontSize: 11.5, fontWeight: 700,
                          background: "oklch(94% 0.06 25)", color: "oklch(40% 0.18 25)",
                        }}>
                          Feedback Agent
                        </span>
                      }
                    />
                    {focusAreas.length > 0 ? (
                      focusAreas.slice(0, 3).map((f, i) => (
                        <InsightRow key={i} text={f} meta="Feedback Agent" tone="no"/>
                      ))
                    ) : (
                      <>
                        <InsightRow text={<>Spend extra reps on <strong>tone control</strong> — formal vs casual.</>} meta="Tone & Register · 4.2" tone="no"/>
                        <InsightRow text={<>Fluency dips when sentences exceed <strong>12 words</strong>.</>} meta="Fluency · pause patterns" tone="no"/>
                        <InsightRow text={<>Stress patterns drop on multi-syllable verbs.</>} meta="Pronunciation · 4.0" tone="no"/>
                      </>
                    )}
                  </Card>

                  {/* Goal progress */}
                  <GoalCard 
                    courseLengthStr={userQuery.data?.preference?.course_length}
                    currentWeek={userQuery.data?.preference?.current_week}
                  />

                  {/* Task difficulty */}
                  <Card>
                    <CardHead title="Task difficulty" sub="All sessions so far"/>
                    <Donut dist={difficultyDist ?? null}/>
                  </Card>

                  {/* Practice patterns */}
                  <Card style={{ marginBottom: 0 }}>
                    <CardHead title="Practice patterns" sub="Last 30 days"/>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                      {MOCK_PRACTICE.map(p => (
                        <div key={p.label} style={{ padding: 12, borderRadius: 12, background: "oklch(97% 0.02 240)" }}>
                          <div style={{ fontSize: 22, fontWeight: 800, color: T.navy, letterSpacing: "-0.02em", lineHeight: 1 }}>
                            {p.num}
                            {p.unit && <span style={{ fontSize: 13, color: T.inkMuted, fontWeight: 700 }}> {p.unit}</span>}
                          </div>
                          <div style={{ fontSize: 11.5, color: T.inkMuted, fontWeight: 700, marginTop: 4, letterSpacing: "0.02em" }}>
                            {p.label}
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                </div>
              </div>
            </main>
          </DashboardLayout>
        </div>
      </div>
    </>
  );
}
