"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/lib/auth-api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { DailyTaskPanel } from "@/components/dashboard/DailyTaskPanel";
import { SkillScorePreview } from "@/components/dashboard/SkillScorePreview";

const DEFAULT_SCORES: Record<string, number> = {
  grammar: 6.0,
  vocabulary: 5.0,
  pronunciation: 4.0,
  fluency: 5.5,
  thought_org: 4.5,
  listening: 7.0,
  tone: 6.5,
};

function getGreeting(name: string | undefined): string {
  const hour = new Date().getHours();
  const first = name?.trim().split(/\s+/)[0] ?? "there";
  if (hour < 12) return `Good morning, ${first}`;
  if (hour < 17) return `Good afternoon, ${first}`;
  return `Good evening, ${first}`;
}

function getInitialPurchaseToast() {
  if (typeof window === "undefined") return null;
  const params = new URLSearchParams(window.location.search);
  if (params.get("purchase") !== "success") return null;
  const plan = params.get("plan") || "selected";
  return `You're now on the ${plan} plan. Let's go! 🎉`;
}

/* ── Mock data for right-column widgets ── */

function GoalRing({ pct }: { pct: number }) {
  const r = 28;
  const c = 2 * Math.PI * r;
  return (
    <div style={{ width: 72, height: 72, position: "relative", flexShrink: 0 }}>
      <svg width="72" height="72" viewBox="0 0 72 72">
        <circle
          cx="36"
          cy="36"
          r={r}
          stroke="rgba(255,255,255,0.25)"
          strokeWidth="6"
          fill="none"
        />
        <circle
          cx="36"
          cy="36"
          r={r}
          stroke="white"
          strokeWidth="6"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c - (pct / 100) * c}
          transform="rotate(-90 36 36)"
          style={{ transition: "stroke-dashoffset 1s" }}
        />
      </svg>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <span
          style={{ fontSize: 20, fontWeight: 800, lineHeight: 1, color: "white" }}
        >
          {pct}
          <span style={{ fontSize: 10, opacity: 0.8 }}>%</span>
        </span>
        <span
          style={{
            fontSize: 8,
            opacity: 0.85,
            fontWeight: 700,
            letterSpacing: "0.06em",
            color: "white",
            marginTop: 2,
          }}
        >
          DONE
        </span>
      </div>
    </div>
  );
}

function ActivityHeatmap() {
  const [cells] = useState(() =>
    Array.from({ length: 91 }, () => {
      const r = Math.random();
      return r < 0.25 ? 0 : r < 0.5 ? 1 : r < 0.75 ? 2 : r < 0.92 ? 3 : 4;
    }),
  );

  function cellColor(lvl: number) {
    if (lvl === 0) return "oklch(94% 0.02 240)";
    if (lvl === 1) return "oklch(88% 0.06 240)";
    if (lvl === 2) return "oklch(78% 0.1 230)";
    if (lvl === 3) return "oklch(62% 0.14 230)";
    return "#0070C4";
  }

  return (
    <>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(13, 1fr)",
          gap: 4,
          marginTop: 10,
        }}
      >
        {cells.map((lvl, i) => (
          <div
            key={i}
            style={{
              aspectRatio: "1",
              borderRadius: 4,
              background: cellColor(lvl),
            }}
          />
        ))}
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          marginTop: 12,
          fontSize: 11,
          color: "oklch(45% 0.07 240)",
          fontWeight: 600,
        }}
      >
        <span>Less</span>
        {[0, 1, 2, 3, 4].map((lvl) => (
          <div
            key={lvl}
            style={{
              width: 10,
              height: 10,
              borderRadius: 3,
              background: cellColor(lvl),
            }}
          />
        ))}
        <span>More</span>
        <span style={{ marginLeft: "auto" }}>Last 13 weeks</span>
      </div>
    </>
  );
}

const YESTERDAY_WINS = [
  { badge: "+5", badgeColor: "#0070C4", text: "Grammar score climbed from 5.5 → 6.0" },
  { badge: "★", badgeColor: "oklch(45% 0.16 60)", text: 'Fixed "go" → "went" pattern in 3 sentences' },
  { badge: "14", badgeColor: "oklch(45% 0.16 290)", text: "New verbs added to your vocabulary deck" },
] as const;

/* ── Card wrapper ── */
function Card({
  children,
  style,
}: {
  children: React.ReactNode;
  style?: React.CSSProperties;
}) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.85)",
        backdropFilter: "blur(18px)",
        WebkitBackdropFilter: "blur(18px)",
        border: "1.5px solid rgba(255,255,255,0.92)",
        borderRadius: 22,
        padding: 24,
        boxShadow: "0 4px 24px rgba(80,110,180,0.1)",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

function CardHead({
  title,
  sub,
  link,
  onLinkClick,
}: {
  title: string;
  sub?: string;
  link?: string;
  onLinkClick?: () => void;
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-end",
        marginBottom: 18,
      }}
    >
      <div>
        <div
          style={{
            fontSize: 17,
            fontWeight: 800,
            color: "oklch(20% 0.09 245)",
            letterSpacing: "-0.01em",
          }}
        >
          {title}
        </div>
        {sub && (
          <div style={{ fontSize: 12.5, color: "oklch(45% 0.07 240)", marginTop: 3 }}>
            {sub}
          </div>
        )}
      </div>
      {link && (
        <button
          type="button"
          onClick={onLinkClick}
          style={{
            fontSize: 13,
            fontWeight: 700,
            color: "#0070C4",
            background: "none",
            border: "none",
            cursor: onLinkClick ? "pointer" : "default",
            display: "flex",
            alignItems: "center",
            gap: 4,
            padding: 0,
            fontFamily: "inherit",
          }}
        >
          {link}{" "}
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path d="M6 4l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      )}
    </div>
  );
}

/* ── Page component ── */

export default function DashboardPage() {
  const router = useRouter();
  const { logout } = useAuthStore();
  const { isReady } = useRequireAuth();
  const [toast, setToast] = useState<string | null>(getInitialPurchaseToast);

  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });

  useEffect(() => {
    if (user && !user.diagnosis_completed) router.replace("/diagnosis");
  }, [user, router]);

  useEffect(() => {
    if (!toast) return;
    const timeout = window.setTimeout(() => setToast(null), 4200);
    if (window.location.search.includes("purchase=success")) {
      router.replace("/dashboard");
    }
    return () => window.clearTimeout(timeout);
  }, [router, toast]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!isReady) return null;

  if (isLoading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "'Plus Jakarta Sans', sans-serif",
          background: "oklch(91% 0.04 245)",
        }}
      >
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
        />
        <p style={{ color: "oklch(45% 0.07 240)", fontSize: 15 }}>
          Loading your dashboard...
        </p>
      </div>
    );
  }

  const enrollment = user?.enrollment;
  const userRecord = user as unknown as Record<string, unknown> | undefined;
  const rawScores = userRecord?.skill_scores;
  const scores =
    rawScores && typeof rawScores === "object" && !Array.isArray(rawScores)
      ? (rawScores as Record<string, number>)
      : DEFAULT_SCORES;

  return (
    <div
      style={{
        minHeight: "100vh",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        background: "oklch(91% 0.04 245)",
        position: "relative",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />

      {/* Dot grid overlay */}
      <div
        aria-hidden="true"
        style={{
          position: "fixed",
          inset: 0,
          pointerEvents: "none",
          backgroundImage:
            "radial-gradient(circle, rgba(90,130,210,0.13) 1px, transparent 1px)",
          backgroundSize: "22px 22px",
          zIndex: 0,
        }}
      />

      <div style={{ position: "relative", zIndex: 1 }}>
        {toast && (
          <div
            role="status"
            style={{
              position: "fixed",
              top: 88,
              left: "50%",
              transform: "translateX(-50%)",
              zIndex: 40,
              background: "oklch(28% 0.1 240)",
              color: "white",
              borderRadius: 8,
              padding: "12px 16px",
              fontSize: 14,
              fontWeight: 700,
              boxShadow: "0 14px 38px rgba(20,35,70,0.2)",
            }}
          >
            {toast}
          </div>
        )}

        <DashboardLayout user={user} onSignOut={handleLogout}>
          {enrollment ? (
            <EnrolledView
              enrollment={enrollment}
              scores={scores}
              onViewStats={() => router.push("/stats")}
              userName={user?.name}
            />
          ) : (
            <NoEnrollmentView
              scores={scores}
              onChoosePlan={() => router.push("/pricing")}
              onViewStats={() => router.push("/stats")}
              userName={user?.name}
            />
          )}
        </DashboardLayout>
      </div>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════════════
   Enrolled view — 2-column layout
   ════════════════════════════════════════════════════════════════════ */

interface EnrolledViewProps {
  enrollment: NonNullable<
    ReturnType<typeof import("@/lib/auth-api").authApi.me> extends Promise<
      infer U
    >
      ? U extends { enrollment: infer E }
        ? E
        : never
      : never
  >;
  scores: Record<string, number>;
  onViewStats: () => void;
  userName: string | undefined;
}

function EnrolledView({ enrollment, scores, onViewStats, userName }: EnrolledViewProps) {
  return (
    <div
      style={{
        maxWidth: 1240,
        margin: "0 auto",
        padding: "28px 32px 60px",
        animation: "fadeSlideUp 0.4s ease both",
      }}
    >
      {/* Page header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-end",
          marginBottom: 24,
        }}
      >
        <div>
          <h1
            style={{
              fontSize: 28,
              fontWeight: 800,
              letterSpacing: "-0.02em",
              color: "oklch(20% 0.09 245)",
              lineHeight: 1.15,
              margin: 0,
            }}
          >
            {getGreeting(userName)} 👋
          </h1>
          <p
            style={{
              fontSize: 14.5,
              color: "oklch(45% 0.07 240)",
              marginTop: 6,
              marginBottom: 0,
            }}
          >
            Week {enrollment.current_week}, Day {enrollment.current_day_in_week} — keep the momentum going.
          </p>
        </div>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "8px 14px",
            borderRadius: 12,
            background: "white",
            border: "1.5px solid oklch(88% 0.025 240)",
            fontSize: 13,
            fontWeight: 600,
            color: "oklch(20% 0.09 245)",
            flexShrink: 0,
          }}
        >
          <span style={{ color: "oklch(45% 0.07 240)" }}>Week</span>
          <span style={{ color: "#0070C4", fontWeight: 800 }}>
            {enrollment.current_week}
          </span>
          <span style={{ color: "oklch(45% 0.07 240)" }}>of</span>
          <span style={{ fontWeight: 700 }}>{enrollment.course.duration_weeks}</span>
        </div>
      </div>

      {/* 2-column grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: 22,
        }}
      >
        {/* LEFT COLUMN */}
        <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>
          <DailyTaskPanel
            key={`${enrollment.current_week}-${enrollment.current_day_in_week}`}
            enrollment={enrollment}
          />

          {/* Skill scores */}
          <Card>
            <CardHead
              title="Your skill scores"
              sub="Updated after every session · scale 0–10"
              link="View full stats"
              onLinkClick={onViewStats}
            />
            <SkillScorePreview scores={scores} />
          </Card>
        </div>

        {/* RIGHT COLUMN */}
        <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>
          {/* Weekly goal — gradient card */}
          <div
            style={{
              background: "linear-gradient(135deg, #0070C4, oklch(45% 0.2 250))",
              borderRadius: 22,
              padding: 22,
              position: "relative",
              overflow: "hidden",
              boxShadow: "0 8px 28px rgba(0,112,196,0.28)",
            }}
          >
            <div
              aria-hidden="true"
              style={{
                position: "absolute",
                top: -40,
                right: -30,
                width: 160,
                height: 160,
                borderRadius: "50%",
                background: "rgba(255,255,255,0.1)",
              }}
            />
            <div
              aria-hidden="true"
              style={{
                position: "absolute",
                bottom: -50,
                left: -30,
                width: 130,
                height: 130,
                borderRadius: "50%",
                background: "rgba(255,255,255,0.06)",
              }}
            />
            <div
              style={{
                fontSize: 12.5,
                fontWeight: 700,
                opacity: 0.85,
                letterSpacing: "0.04em",
                textTransform: "uppercase",
                color: "white",
              }}
            >
              Weekly goal
            </div>
            <div
              style={{
                fontSize: 20,
                fontWeight: 800,
                letterSpacing: "-0.02em",
                margin: "8px 0 14px",
                lineHeight: 1.2,
                position: "relative",
                zIndex: 1,
                color: "white",
              }}
            >
              Reach {enrollment.course.target_level} by Friday
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 14,
                position: "relative",
                zIndex: 1,
              }}
            >
              <GoalRing pct={42} />
              <div style={{ fontSize: 13, lineHeight: 1.5, color: "white" }}>
                <div>
                  <strong style={{ fontSize: 16, fontWeight: 800 }}>3</strong> of 7 sessions
                </div>
                <div style={{ opacity: 0.85 }}>4 more this week</div>
              </div>
            </div>
          </div>

          {/* Activity heatmap */}
          <Card>
            <div style={{ marginBottom: 6 }}>
              <div
                style={{
                  fontSize: 17,
                  fontWeight: 800,
                  color: "oklch(20% 0.09 245)",
                  letterSpacing: "-0.01em",
                }}
              >
                Activity
              </div>
              <div style={{ fontSize: 12.5, color: "oklch(45% 0.07 240)", marginTop: 3 }}>
                Sessions per day
              </div>
            </div>
            <ActivityHeatmap />
          </Card>

          {/* Yesterday's wins */}
          <Card>
            <div
              style={{
                fontSize: 17,
                fontWeight: 800,
                color: "oklch(20% 0.09 245)",
                letterSpacing: "-0.01em",
                marginBottom: 12,
              }}
            >
              Yesterday&apos;s wins
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {YESTERDAY_WINS.map((item, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    padding: "9px 10px",
                    borderRadius: 10,
                    background: "oklch(97% 0.02 240)",
                    fontSize: 12.5,
                  }}
                >
                  <div
                    style={{
                      width: 26,
                      height: 26,
                      borderRadius: 8,
                      background: "white",
                      border: "1px solid oklch(88% 0.025 240)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                      fontWeight: 800,
                      fontSize: 11,
                      color: item.badgeColor,
                    }}
                  >
                    {item.badge}
                  </div>
                  <span
                    style={{
                      color: "oklch(20% 0.09 245)",
                      fontWeight: 600,
                      flex: 1,
                      lineHeight: 1.4,
                    }}
                  >
                    {item.text}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════════════
   No enrollment view
   ════════════════════════════════════════════════════════════════════ */

interface NoEnrollmentViewProps {
  scores: Record<string, number>;
  onChoosePlan: () => void;
  onViewStats: () => void;
  userName: string | undefined;
}

function NoEnrollmentView({ scores, onChoosePlan, onViewStats, userName }: NoEnrollmentViewProps) {
  return (
    <div
      style={{
        maxWidth: 1240,
        margin: "0 auto",
        padding: "28px 32px 60px",
        animation: "fadeSlideUp 0.4s ease both",
      }}
    >
      {/* Page header */}
      <div style={{ marginBottom: 24 }}>
        <h1
          style={{
            fontSize: 28,
            fontWeight: 800,
            letterSpacing: "-0.02em",
            color: "oklch(20% 0.09 245)",
            lineHeight: 1.15,
            margin: 0,
          }}
        >
          {getGreeting(userName)} 👋
        </h1>
        <p
          style={{
            fontSize: 14.5,
            color: "oklch(45% 0.07 240)",
            marginTop: 6,
            marginBottom: 0,
          }}
        >
          Your diagnosis is complete — choose a plan to unlock your daily tasks.
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: 22,
        }}
      >
        {/* Left column */}
        <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>
          {/* Plan picker card */}
          <Card>
            <CardHead title="Choose your learning plan" />
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(2, 1fr)",
                gap: 14,
              }}
            >
              <PlanCard
                weeks={24}
                label="Accelerated plan"
                taskFrequency="5 tasks / week"
                onClick={onChoosePlan}
              />
              <PlanCard
                weeks={48}
                label="Steady plan"
                taskFrequency="3 tasks / week"
                onClick={onChoosePlan}
              />
            </div>
          </Card>

          {/* Locked tasks preview */}
          <Card>
            <CardHead title="Today's tasks" sub="Unlock by enrolling in a plan" />
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {[
                { type: "Speaking task", skill: "Grammar & Fluency" },
                { type: "Writing task", skill: "Sentence structure" },
              ].map((task, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 14,
                    padding: "16px 18px",
                    borderRadius: 16,
                    border: "1.5px solid oklch(88% 0.025 240)",
                    background: "oklch(97% 0.02 240)",
                    opacity: 0.65,
                  }}
                >
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: 12,
                      background: "oklch(94% 0.02 240)",
                      color: "oklch(55% 0.04 240)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                    }}
                  >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <rect x="4" y="7" width="8" height="6" rx="1.2" stroke="currentColor" strokeWidth="1.5" />
                      <path d="M5.8 7V5a2.2 2.2 0 0 1 4.4 0v2" stroke="currentColor" strokeWidth="1.5" />
                    </svg>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        fontSize: 15,
                        fontWeight: 700,
                        color: "oklch(45% 0.07 240)",
                        filter: "blur(0.4px)",
                      }}
                    >
                      {task.type}
                    </div>
                    <div style={{ fontSize: 12.5, color: "oklch(55% 0.05 240)" }}>
                      {task.skill}
                    </div>
                  </div>
                  <span style={{ fontSize: 13, fontWeight: 700, color: "oklch(55% 0.04 240)" }}>
                    Locked
                  </span>
                </div>
              ))}
            </div>
          </Card>

          {/* Skill scores */}
          <Card>
            <CardHead
              title="Your skill scores"
              sub="From your diagnosis · scale 0–10"
              link="View full stats"
              onLinkClick={onViewStats}
            />
            <SkillScorePreview scores={scores} />
          </Card>
        </div>

        {/* Right column — same mock widgets */}
        <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>
          {/* Teaser goal card */}
          <div
            style={{
              background: "linear-gradient(135deg, #0070C4, oklch(45% 0.2 250))",
              borderRadius: 22,
              padding: 22,
              position: "relative",
              overflow: "hidden",
              boxShadow: "0 8px 28px rgba(0,112,196,0.28)",
            }}
          >
            <div
              aria-hidden="true"
              style={{
                position: "absolute",
                top: -40,
                right: -30,
                width: 160,
                height: 160,
                borderRadius: "50%",
                background: "rgba(255,255,255,0.1)",
              }}
            />
            <div
              style={{
                fontSize: 12.5,
                fontWeight: 700,
                opacity: 0.85,
                letterSpacing: "0.04em",
                textTransform: "uppercase",
                color: "white",
              }}
            >
              Weekly goal
            </div>
            <div
              style={{
                fontSize: 20,
                fontWeight: 800,
                letterSpacing: "-0.02em",
                margin: "8px 0 14px",
                lineHeight: 1.2,
                color: "white",
                opacity: 0.75,
              }}
            >
              Enroll to set your first goal
            </div>
            <button
              onClick={onChoosePlan}
              style={{
                padding: "10px 20px",
                borderRadius: 10,
                border: "none",
                background: "rgba(255,255,255,0.2)",
                color: "white",
                fontSize: 13,
                fontWeight: 700,
                cursor: "pointer",
                fontFamily: "inherit",
              }}
            >
              Choose a plan →
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}

/* ── Plan card ── */

function PlanCard({
  weeks,
  label,
  taskFrequency,
  onClick,
}: {
  weeks: number;
  label: string;
  taskFrequency: string;
  onClick: () => void;
}) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.7)",
        borderRadius: 12,
        border: "1px solid rgba(80,120,200,0.12)",
        padding: "20px 18px",
        display: "flex",
        flexDirection: "column",
        gap: 10,
        cursor: "pointer",
        transition: "transform 0.2s ease, box-shadow 0.2s ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-3px)";
        e.currentTarget.style.boxShadow = "0 8px 28px rgba(80,130,220,0.14)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      <span
        style={{
          fontSize: 28,
          fontWeight: 800,
          color: "oklch(15% 0.09 245)",
          letterSpacing: "-0.03em",
        }}
      >
        {weeks} weeks
      </span>
      <span style={{ fontSize: 14, fontWeight: 600, color: "oklch(40% 0.07 240)" }}>
        {label}
      </span>
      <span
        style={{
          display: "inline-block",
          fontSize: 12,
          fontWeight: 600,
          color: "#0070C4",
          background: "oklch(95% 0.02 240)",
          padding: "3px 10px",
          borderRadius: 20,
          width: "fit-content",
        }}
      >
        {taskFrequency}
      </span>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onClick();
        }}
        style={{
          marginTop: 6,
          width: "100%",
          padding: "10px 0",
          borderRadius: 10,
          border: "none",
          background: "#0070C4",
          color: "white",
          fontSize: 13,
          fontWeight: 700,
          cursor: "pointer",
          fontFamily: "inherit",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = "#00599e";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = "#0070C4";
        }}
      >
        Choose this plan
      </button>
    </div>
  );
}
