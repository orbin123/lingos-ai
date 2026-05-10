"use client";

import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { authApi } from "@/lib/auth-api";
import { progressApi, type RecentActivity } from "@/lib/progress-api";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useAuthStore } from "@/store/authStore";

const T = {
  navy: "oklch(20% 0.09 245)",
  inkMuted: "oklch(45% 0.07 240)",
  line: "oklch(86% 0.025 240)",
  primary: "#0070C4",
  green: "oklch(58% 0.16 155)",
  red: "oklch(58% 0.2 25)",
  bg: "oklch(91% 0.04 245)",
};

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

function scoreColor(score: number) {
  if (score >= 7) return { color: "oklch(35% 0.14 155)", bg: "oklch(94% 0.07 155)" };
  if (score >= 5) return { color: T.primary, bg: "#d6e8f7" };
  return { color: "oklch(40% 0.18 25)", bg: "oklch(94% 0.06 25)" };
}

const iconBg: Record<string, string> = {
  "🗣️": "oklch(94% 0.06 240)",
  "🎧": "oklch(94% 0.07 155)",
  "📖": "oklch(94% 0.06 290)",
  "✍️": "oklch(94% 0.07 65)",
};

function ActivityRow({ activity, onClick }: { activity: RecentActivity; onClick: () => void }) {
  const { color, bg } = scoreColor(activity.score);
  const chip = activityChip(activity.task_type);

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
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLDivElement).style.borderColor = T.primary;
        (e.currentTarget as HTMLDivElement).style.transform = "translateY(-1px)";
        (e.currentTarget as HTMLDivElement).style.boxShadow = "0 4px 14px rgba(0,112,196,0.1)";
      }}
      onMouseLeave={(e) => {
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

export default function AllActivitiesPage() {
  const router = useRouter();
  const { logout } = useAuthStore();
  const { isReady } = useRequireAuth();

  const userQuery = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });

  const activitiesQuery = useQuery({
    queryKey: ["all-activities"],
    queryFn: () => progressApi.getActivities(100),
    enabled: isReady,
  });

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!isReady) return null;

  const activities = activitiesQuery.data ?? [];

  return (
    <div style={{ minHeight: "100vh", fontFamily: "'Plus Jakarta Sans', sans-serif", background: T.bg, position: "relative" }}>
      <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" />
      <div aria-hidden style={{
        position: "fixed", inset: 0, pointerEvents: "none",
        backgroundImage: "radial-gradient(circle, rgba(90,130,210,0.13) 1px, transparent 1px)",
        backgroundSize: "22px 22px", zIndex: 0,
      }} />
      <div style={{ position: "relative", zIndex: 1 }}>
        <DashboardLayout user={userQuery.data} onSignOut={handleLogout}>
          <main style={{ maxWidth: 800, margin: "0 auto", padding: "28px 32px 60px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 28 }}>
              <button
                onClick={() => router.back()}
                style={{
                  padding: "8px 14px", borderRadius: 10, border: `1.5px solid ${T.line}`,
                  background: "white", color: T.inkMuted, fontSize: 13, fontWeight: 600,
                  cursor: "pointer", fontFamily: "inherit",
                }}
              >
                ← Back
              </button>
              <div>
                <h1 style={{ fontSize: 24, fontWeight: 800, color: T.navy, margin: 0, letterSpacing: "-0.02em" }}>
                  All activities
                </h1>
                <p style={{ fontSize: 13, color: T.inkMuted, margin: "4px 0 0" }}>
                  {activitiesQuery.isLoading ? "Loading…" : `${activities.length} completed sessions`}
                </p>
              </div>
            </div>

            {activitiesQuery.isLoading ? (
              <div style={{ padding: "40px 0", textAlign: "center", color: T.inkMuted, fontSize: 14 }}>
                Loading activities…
              </div>
            ) : activities.length === 0 ? (
              <div style={{ padding: "40px 0", textAlign: "center", color: T.inkMuted, fontSize: 14 }}>
                No completed activities yet. Complete some tasks to see them here!
              </div>
            ) : (
              <div>
                {activities.map((a) => (
                  <ActivityRow
                    key={a.id}
                    activity={a}
                    onClick={() => router.push(`/task/history/${a.user_task_id}`)}
                  />
                ))}
              </div>
            )}
          </main>
        </DashboardLayout>
      </div>
    </div>
  );
}
