"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { AlertCircle, ArrowUpRight, Check, CheckCircle2 } from "lucide-react";
import { authApi } from "@/lib/auth-api";
import { progressApi, type RecentActivity, type SkillScoreSnapshot } from "@/lib/progress-api";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useAuthStore } from "@/store/authStore";

const SKILL_AXES = [
  { key: "grammar", label: "Grammar" },
  { key: "vocabulary", label: "Vocabulary" },
  { key: "pronunciation", label: "Pronunciation" },
  { key: "fluency", label: "Fluency" },
  { key: "thought", label: "Thought Org." },
  { key: "listening", label: "Listening" },
  { key: "tone", label: "Tone & Register" },
] as const;

const DEFAULT_AXIS_SCORES = [6, 5, 4, 5.5, 4.5, 7, 6.5];

function normalizeSkillName(name: string) {
  return name.toLowerCase().replace(/[_&.]/g, " ").replace(/\s+/g, " ").trim();
}

function displaySkillName(name: string | null) {
  if (!name) return "No data yet";
  const normalized = normalizeSkillName(name);
  if (normalized.includes("thought")) return "Thought Org.";
  if (normalized.includes("tone")) return "Tone & Register";
  return normalized
    .split(" ")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function axisScores(scores: SkillScoreSnapshot[]) {
  return SKILL_AXES.map((axis, index) => {
    const match = scores.find((score) => normalizeSkillName(score.skill_name).includes(axis.key));
    return {
      label: axis.label,
      score: match?.score ?? DEFAULT_AXIS_SCORES[index],
    };
  });
}

function scoreColor(score: number) {
  if (score >= 7) return { color: "oklch(43% 0.16 150)", bg: "oklch(94% 0.055 150)" };
  if (score >= 5) return { color: "oklch(53% 0.14 82)", bg: "oklch(94% 0.07 88)" };
  return { color: "oklch(48% 0.18 28)", bg: "oklch(95% 0.04 28)" };
}

function activityChip(taskType: string) {
  const type = taskType.toLowerCase();
  if (type.includes("speak")) return "🗣️ Speak";
  if (type.includes("listen")) return "🎧 Listen";
  if (type.includes("read")) return "📖 Read";
  return "✍️ Write";
}

function formatTimestamp(value: string) {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export default function StatsPage() {
  const router = useRouter();
  const { logout } = useAuthStore();
  const { isReady } = useRequireAuth();

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
  const change = weekly?.overall_score_change ?? 0;
  const changePositive = change >= 0;

  return (
    <div
      style={{
        minHeight: "100vh",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        background:
          "radial-gradient(ellipse 80% 60% at 50% 0%, oklch(86% 0.07 240) 0%, oklch(90% 0.045 245) 50%, oklch(93% 0.025 250) 100%)",
        position: "relative",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />
      <div
        aria-hidden="true"
        style={{
          position: "fixed",
          inset: 0,
          pointerEvents: "none",
          backgroundImage:
            "radial-gradient(circle, rgba(90,130,210,0.18) 1px, transparent 1px)",
          backgroundSize: "22px 22px",
          zIndex: 0,
        }}
      />

      <div style={{ position: "relative", zIndex: 1 }}>
        <DashboardLayout
          user={userQuery.data}
          onSignOut={handleLogout}
          mainStyle={{
            maxWidth: 1060,
            margin: "0 auto",
            padding: "32px 20px 72px",
          }}
        >
          {userQuery.isLoading || statsQuery.isLoading ? (
            <LoadingCard />
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
              <section
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                  gap: 14,
                  background: "rgba(255,255,255,0.84)",
                  border: "1px solid rgba(255,255,255,0.9)",
                  borderRadius: 8,
                  padding: 16,
                  boxShadow:
                    "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
                }}
              >
                <StatTile
                  title="Overall score change"
                  value={`${changePositive ? "+" : ""}${change.toFixed(1)} ${changePositive ? "↑" : "↓"}`}
                  label="vs last week"
                  note="Evaluator Agent weekly average"
                  valueColor={changePositive ? "oklch(43% 0.16 150)" : "oklch(48% 0.18 28)"}
                />
                <StatTile
                  title="Tasks completed"
                  value={`${weekly?.tasks_completed ?? 0} / ${weekly?.weekly_task_goal ?? 7}`}
                  label="this week"
                  note="completed assigned tasks"
                />
                <StatTile
                  title="Best skill this week"
                  value={displaySkillName(weekly?.best_skill_name ?? null)}
                  label={
                    weekly?.best_skill_score != null
                      ? `scored ${weekly.best_skill_score.toFixed(1)}`
                      : "scored after tasks"
                  }
                  note="highest current sub-skill"
                />
              </section>

              <section
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
                  gap: 20,
                }}
              >
                <RadarCard scores={axisScores(stats?.skill_scores ?? [])} />
                <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                  <FeedbackCard
                    tone="strength"
                    title="Your strengths"
                    pill="Feedback Agent"
                    items={stats?.feedback.strengths ?? []}
                  />
                  <FeedbackCard
                    tone="focus"
                    title="Focus areas"
                    pill="Feedback Agent"
                    items={stats?.feedback.focus_areas ?? []}
                  />
                </div>
              </section>

              <RecentActivities activities={stats?.recent_activities ?? []} />
            </div>
          )}
        </DashboardLayout>
      </div>
    </div>
  );
}

function LoadingCard() {
  return (
    <div
      style={{
        minHeight: 300,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(255,255,255,0.84)",
        border: "1px solid rgba(255,255,255,0.9)",
        borderRadius: 8,
        color: "oklch(45% 0.07 240)",
        fontSize: 15,
      }}
    >
      Loading your stats...
    </div>
  );
}

function StatTile({
  label,
  note,
  title,
  value,
  valueColor = "oklch(18% 0.09 245)",
}: {
  label: string;
  note: string;
  title: string;
  value: string;
  valueColor?: string;
}) {
  return (
    <div
      style={{
        minHeight: 132,
        display: "flex",
        flexDirection: "column",
        borderRadius: 8,
        background: "oklch(94% 0.025 245)",
        border: "1px solid rgba(80,120,200,0.1)",
        padding: "18px 18px 14px",
      }}
    >
      <div style={{ color: "oklch(45% 0.07 240)", fontSize: 12, fontWeight: 700 }}>
        {title}
      </div>
      <div
        style={{
          marginTop: 12,
          color: valueColor,
          fontSize: 30,
          fontWeight: 800,
          letterSpacing: 0,
          lineHeight: 1,
        }}
      >
        {value}
      </div>
      <div style={{ marginTop: 8, color: "oklch(38% 0.08 240)", fontSize: 13 }}>
        {label}
      </div>
      <div style={{ marginTop: "auto", color: "oklch(55% 0.05 240)", fontSize: 11 }}>
        {note}
      </div>
    </div>
  );
}

function RadarCard({
  scores,
}: {
  scores: Array<{ label: string; score: number }>;
}) {
  const size = 500;
  const center = size / 2;
  const radius = 128;
  const labelDistance = radius + 28;
  const levels = [
    { label: "Level 1", score: 3, color: "rgba(71, 149, 232, 0.12)" },
    { label: "Level 2", score: 6, color: "rgba(52, 130, 222, 0.2)" },
    { label: "Level 3", score: 10, color: "rgba(24, 104, 202, 0.32)" },
  ];
  const levelPolygons = levels.map((level) => ({
    ...level,
    points: scores
      .map((_, index) => {
        const angle = -Math.PI / 2 + (index * Math.PI * 2) / scores.length;
        const distance = radius * level.score / 10;
        return `${center + Math.cos(angle) * distance},${center + Math.sin(angle) * distance}`;
      })
      .join(" "),
  }));
  const polygonPointsForScore = (score: number) =>
    scores.map((_, index) => {
      const angle = -Math.PI / 2 + (index * Math.PI * 2) / scores.length;
      const distance = radius * score / 10;
      return {
        x: center + Math.cos(angle) * distance,
        y: center + Math.sin(angle) * distance,
      };
    });
  const polygonPathForScore = (score: number) =>
    polygonPointsForScore(score)
      .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
      .join(" ") + " Z";
  const bandPath = (outerScore: number, innerScore: number) =>
    `${polygonPathForScore(outerScore)} ${polygonPathForScore(innerScore)}`;
  const points = scores.map((score, index) => {
    const angle = -Math.PI / 2 + (index * Math.PI * 2) / scores.length;
    const distance = radius * Math.min(Math.max(score.score, 0), 10) / 10;
    const labelX = center + Math.cos(angle) * labelDistance;
    const labelY = center + Math.sin(angle) * labelDistance;
    const isLeft = labelX < center - 32;
    const isRight = labelX > center + 32;
    const textAnchor: "start" | "end" | "middle" = isLeft
      ? "end"
      : isRight
        ? "start"
        : "middle";
    return {
      ...score,
      x: center + Math.cos(angle) * distance,
      y: center + Math.sin(angle) * distance,
      axisX: center + Math.cos(angle) * radius,
      axisY: center + Math.sin(angle) * radius,
      labelX,
      labelY: Math.min(Math.max(labelY, 30), size - 30),
      textAnchor,
    };
  });
  const polygon = points.map((point) => `${point.x},${point.y}`).join(" ");

  return (
    <section
      style={{
        background: "rgba(255,255,255,0.84)",
        border: "1px solid rgba(255,255,255,0.9)",
        borderRadius: 8,
        padding: 24,
        boxShadow:
          "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          marginBottom: 12,
        }}
      >
        <h2
          style={{
            margin: 0,
            color: "oklch(15% 0.09 245)",
            fontSize: 20,
            fontWeight: 800,
            letterSpacing: 0,
          }}
        >
          Sub-skill overview
        </h2>
        <span
          style={{
            borderRadius: 999,
            background: "oklch(92% 0.035 245)",
            color: "oklch(45% 0.14 240)",
            fontSize: 11,
            fontWeight: 700,
            padding: "6px 10px",
            whiteSpace: "nowrap",
          }}
        >
          Updated by Evaluator Agent
        </span>
      </div>

      <svg viewBox={`0 0 ${size} ${size}`} width="100%" style={{ display: "block" }}>
        <polygon points={levelPolygons[0].points} fill={levelPolygons[0].color} />
        <path
          d={bandPath(levels[1].score, levels[0].score)}
          fill={levels[1].color}
          fillRule="evenodd"
        />
        <path
          d={bandPath(levels[2].score, levels[1].score)}
          fill={levels[2].color}
          fillRule="evenodd"
        />
        {levelPolygons.map((level) => (
          <polygon
            key={level.label}
            points={level.points}
            fill="none"
            stroke="rgba(80,120,200,0.24)"
            strokeWidth="1.2"
          />
        ))}
        {points.map((point) => (
          <line
            key={point.label}
            x1={center}
            y1={center}
            x2={point.axisX}
            y2={point.axisY}
            stroke="rgba(80,120,200,0.16)"
            strokeWidth="1"
          />
        ))}
        <polygon points={polygon} fill="rgba(70,125,220,0.1)" stroke="oklch(52% 0.18 240)" strokeWidth="3" />
        {points.map((point) => (
          <g key={point.label}>
            <circle cx={point.x} cy={point.y} r="4.5" fill="oklch(52% 0.18 240)" />
            <text
              x={point.labelX}
              y={point.labelY}
              textAnchor={point.textAnchor}
              dominantBaseline="middle"
              fill="oklch(35% 0.07 240)"
              fontSize="11"
              fontWeight="700"
            >
              {point.label}
            </text>
          </g>
        ))}
      </svg>
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: 14,
          flexWrap: "wrap",
          marginTop: -12,
        }}
      >
        {levels.map((level) => (
          <div
            key={level.label}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 7,
              color: "oklch(38% 0.07 240)",
              fontSize: 12,
              fontWeight: 700,
            }}
          >
            <span
              style={{
                width: 12,
                height: 12,
                borderRadius: 3,
                background: level.color,
                border: "1px solid rgba(80,120,200,0.24)",
              }}
            />
            {level.label}
          </div>
        ))}
      </div>
    </section>
  );
}

function FeedbackCard({
  items,
  pill,
  title,
  tone,
}: {
  items: string[];
  pill: string;
  title: string;
  tone: "strength" | "focus";
}) {
  const isStrength = tone === "strength";
  const color = isStrength ? "oklch(43% 0.16 150)" : "oklch(48% 0.18 28)";
  const soft = isStrength ? "oklch(94% 0.055 150)" : "oklch(95% 0.04 28)";
  const Icon = isStrength ? Check : AlertCircle;

  return (
    <section
      style={{
        flex: 1,
        background: "rgba(255,255,255,0.84)",
        border: "1px solid rgba(255,255,255,0.9)",
        borderRadius: 8,
        padding: 20,
        boxShadow:
          "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
        <span style={{ width: 9, height: 9, borderRadius: "50%", background: color }} />
        <h2
          style={{
            margin: 0,
            color: "oklch(15% 0.09 245)",
            fontSize: 17,
            fontWeight: 800,
            letterSpacing: 0,
          }}
        >
          {title}
        </h2>
      </div>
      <span
        style={{
          display: "inline-flex",
          marginTop: 12,
          borderRadius: 999,
          background: soft,
          color,
          fontSize: 11,
          fontWeight: 700,
          padding: "5px 9px",
        }}
      >
        {pill}
      </span>
      <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 16 }}>
        {(items.length ? items : ["Complete tasks to generate personalized feedback."]).slice(0, 3).map((item) => (
          <div key={item} style={{ display: "flex", gap: 10, color: "oklch(32% 0.06 240)", fontSize: 13, lineHeight: 1.55 }}>
            <Icon size={16} color={color} style={{ marginTop: 2, flexShrink: 0 }} />
            <span>{item}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function RecentActivities({ activities }: { activities: RecentActivity[] }) {
  return (
    <section
      style={{
        background: "rgba(255,255,255,0.84)",
        border: "1px solid rgba(255,255,255,0.9)",
        borderRadius: 8,
        padding: 20,
        boxShadow:
          "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 14,
          marginBottom: 16,
        }}
      >
        <h2
          style={{
            margin: 0,
            color: "oklch(15% 0.09 245)",
            fontSize: 20,
            fontWeight: 800,
            letterSpacing: 0,
          }}
        >
          Recent activities
        </h2>
        <button
          type="button"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            border: "1px solid rgba(80,120,200,0.16)",
            borderRadius: 8,
            background: "rgba(255,255,255,0.45)",
            color: "oklch(42% 0.1 240)",
            cursor: "pointer",
            fontFamily: "inherit",
            fontSize: 13,
            fontWeight: 700,
            padding: "8px 11px",
          }}
        >
          View all
          <ArrowUpRight size={15} />
        </button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {activities.length === 0 ? (
          <div
            style={{
              borderRadius: 8,
              background: "oklch(94% 0.025 245)",
              border: "1px solid rgba(80,120,200,0.1)",
              padding: 18,
              color: "oklch(45% 0.07 240)",
              fontSize: 14,
            }}
          >
            Completed tasks will appear here after the Evaluator Agent scores your work.
          </div>
        ) : (
          activities.slice(0, 3).map((activity) => <ActivityCard key={activity.id} activity={activity} />)
        )}
      </div>
    </section>
  );
}

function ActivityCard({ activity }: { activity: RecentActivity }) {
  const colors = scoreColor(activity.score);

  return (
    <article
      style={{
        borderRadius: 8,
        background: "oklch(98% 0.008 245)",
        border: "1px solid rgba(80,120,200,0.1)",
        padding: 16,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: 16,
        }}
      >
        <div style={{ minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 9, flexWrap: "wrap" }}>
            <span
              style={{
                borderRadius: 999,
                background: "oklch(92% 0.035 245)",
                color: "oklch(42% 0.1 240)",
                fontSize: 12,
                fontWeight: 800,
                padding: "5px 9px",
              }}
            >
              {activityChip(activity.task_type)}
            </span>
            <strong style={{ color: "oklch(20% 0.08 245)", fontSize: 14 }}>
              {activity.task_name}
            </strong>
            <span style={{ color: "oklch(55% 0.05 240)", fontSize: 12 }}>
              {formatTimestamp(activity.completed_at)}
            </span>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
          <span
            style={{
              borderRadius: 999,
              background: colors.bg,
              color: colors.color,
              fontSize: 12,
              fontWeight: 800,
              padding: "5px 9px",
            }}
          >
            {activity.score.toFixed(1)}
          </span>
          <span style={{ color: "oklch(48% 0.06 240)", fontSize: 12 }}>
            {activity.mistake_count} mistakes
          </span>
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 14 }}>
        {activity.score >= 8 && activity.strength ? (
          <StrengthRow row={activity.strength} />
        ) : activity.mistakes.length > 0 ? (
          activity.mistakes.map((mistake, index) => <MistakeRow key={`${mistake.issue}-${index}`} row={mistake} />)
        ) : (
          <MistakeRow
            row={{
              label: "Mistake:",
              issue: "No detailed mistake rows were returned for this task.",
              correction: "Future Feedback Agent responses will fill this in.",
            }}
          />
        )}
      </div>
    </article>
  );
}

function MistakeRow({ row }: { row: { label: string; issue: string; correction: string | null } }) {
  return (
    <div
      style={{
        borderLeft: "3px solid oklch(55% 0.2 28)",
        borderRadius: 6,
        background: "oklch(96% 0.026 28)",
        padding: "10px 12px",
      }}
    >
      <div style={{ color: "oklch(45% 0.18 28)", fontSize: 13, lineHeight: 1.45 }}>
        <strong>{row.label}</strong> {row.issue}
      </div>
      {row.correction && (
        <div style={{ marginTop: 4, color: "oklch(45% 0.06 240)", fontSize: 12 }}>
          {row.correction}
        </div>
      )}
    </div>
  );
}

function StrengthRow({ row }: { row: { label: string; issue: string; correction: string | null } }) {
  return (
    <div
      style={{
        borderLeft: "3px solid oklch(50% 0.16 150)",
        borderRadius: 6,
        background: "oklch(96% 0.04 150)",
        padding: "10px 12px",
      }}
    >
      <div style={{ display: "flex", gap: 8, color: "oklch(38% 0.15 150)", fontSize: 13, lineHeight: 1.45 }}>
        <CheckCircle2 size={15} style={{ marginTop: 1, flexShrink: 0 }} />
        <span>
          <strong>{row.label}</strong> {row.issue}
        </span>
      </div>
      {row.correction && (
        <div style={{ marginTop: 4, color: "oklch(45% 0.06 240)", fontSize: 12 }}>
          {row.correction}
        </div>
      )}
    </div>
  );
}
