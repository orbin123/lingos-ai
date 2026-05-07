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

/* ── Inline SVG icons (no emoji, no external libs) ── */

function LockIcon() {
  return (
    <svg
      width="28"
      height="28"
      viewBox="0 0 24 24"
      fill="none"
      style={{ flexShrink: 0 }}
    >
      <rect
        x="5"
        y="11"
        width="14"
        height="10"
        rx="2"
        stroke="oklch(45% 0.07 240)"
        strokeWidth="1.6"
        fill="none"
      />
      <path
        d="M8 11V7a4 4 0 1 1 8 0v4"
        stroke="oklch(45% 0.07 240)"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

function FireIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
      <path
        d="M12 2c.5 3.5-1.5 6-1.5 6s2 1 3 4c1 3-1 5.5-3.5 6.5C8 19.5 6.5 17 7 14c.5-3 2-4.5 2-4.5S8 7 12 2z"
        fill="oklch(65% 0.2 55)"
        stroke="oklch(55% 0.2 40)"
        strokeWidth="1"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/* ── Locked task card data ── */

const LOCKED_TASKS = [
  { type: "Writing task", skill: "Grammar & Sentence" },
  { type: "Listening task", skill: "Comprehension & Tone" },
] as const;

function getInitialPurchaseToast() {
  if (typeof window === "undefined") return null;
  const params = new URLSearchParams(window.location.search);
  if (params.get("purchase") !== "success") return null;
  const plan = params.get("plan") || "selected";
  return `You're now on the ${plan} plan. Let's go! 🎉`;
}

/* ── Page component ── */

export default function DashboardPage() {
  const router = useRouter();
  const { logout } = useAuthStore();
  const { isReady } = useRequireAuth();
  const [toast, setToast] = useState<string | null>(getInitialPurchaseToast);

  // Fetch user info using the token (proves token works)
  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });
  // If diagnosis not done, redirect to diagnosis flow
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
          background:
            "radial-gradient(ellipse 80% 60% at 50% 0%, oklch(86% 0.07 240) 0%, oklch(90% 0.045 245) 50%, oklch(93% 0.025 250) 100%)",
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

  // Use scores from user if available, fallback to demo values
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
        background:
          "radial-gradient(ellipse 80% 60% at 50% 0%, oklch(86% 0.07 240) 0%, oklch(90% 0.045 245) 50%, oklch(93% 0.025 250) 100%)",
        position: "relative",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />

      {/* Dotted pattern overlay */}
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
        <DashboardLayout
          user={user}
          onSignOut={handleLogout}
          mainStyle={{
            maxWidth: 780,
            margin: "0 auto",
            padding: "32px 20px 64px",
          }}
        >
          <div
            style={{
              animation: "fadeSlideUp 0.4s ease both",
            }}
          >
            {enrollment ? (
              <EnrolledView
                enrollment={enrollment}
                scores={scores}
                onViewStats={() => router.push("/stats")}
              />
            ) : (
              <NoEnrollmentView
                scores={scores}
                onChoosePlan={() => router.push("/pricing")}
                onViewStats={() => router.push("/stats")}
              />
            )}
          </div>
        </DashboardLayout>
      </div>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════════════
   State A — No enrollment
   ════════════════════════════════════════════════════════════════════ */

interface NoEnrollmentViewProps {
  scores: Record<string, number>;
  onChoosePlan: () => void;
  onViewStats: () => void;
}

function NoEnrollmentView({
  scores,
  onChoosePlan,
  onViewStats,
}: NoEnrollmentViewProps) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
      {/* ── Section 1: Plan banner ── */}
      <section
        style={{
          background: "rgba(255,255,255,0.85)",
          backdropFilter: "blur(20px)",
          WebkitBackdropFilter: "blur(20px)",
          borderRadius: 16,
          border: "1px solid rgba(255,255,255,0.9)",
          borderLeft: "4px solid oklch(52% 0.18 240)",
          padding: "28px 28px 24px",
          boxShadow:
            "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
          animation: "fadeSlideUp 0.4s ease 0.2s both",
        }}
      >
        {/* Badge */}
        <span
          style={{
            display: "inline-block",
            fontSize: 12,
            fontWeight: 700,
            color: "oklch(45% 0.16 70)",
            background: "oklch(92% 0.06 80)",
            padding: "3px 10px",
            borderRadius: 20,
            marginBottom: 12,
            letterSpacing: "0.3px",
          }}
        >
          Next step
        </span>

        <h2
          style={{
            fontSize: 22,
            fontWeight: 800,
            color: "oklch(15% 0.09 245)",
            margin: "0 0 6px",
            letterSpacing: "-0.02em",
          }}
        >
          Choose your learning plan
        </h2>
        <p
          style={{
            fontSize: 14,
            color: "oklch(45% 0.07 240)",
            margin: "0 0 20px",
            lineHeight: 1.5,
          }}
        >
          Your diagnosis is complete. Pick a plan to start your personalized
          tasks.
        </p>

        {/* Plan cards */}
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
      </section>

      {/* ── Section 2: Locked tasks ── */}
      <section>
        <h3
          style={{
            fontSize: 16,
            fontWeight: 700,
            color: "oklch(18% 0.09 245)",
            margin: "0 0 14px",
          }}
        >
          Today&apos;s tasks
        </h3>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(2, 1fr)",
            gap: 14,
          }}
        >
          {LOCKED_TASKS.map((task, i) => (
            <div
              key={i}
              style={{
                border: "1.5px dashed rgba(80,120,200,0.25)",
                borderRadius: 14,
                padding: "22px 20px",
                opacity: 0.65,
                animation: "pulse-soft 2.5s ease-in-out infinite",
                animationDelay: `${i * 0.3}s`,
                display: "flex",
                flexDirection: "column",
                gap: 10,
              }}
            >
              <LockIcon />
              <span
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: "oklch(45% 0.07 240)",
                  filter: "blur(0.4px)",
                }}
              >
                {task.type}
              </span>
              <span
                style={{
                  fontSize: 12,
                  fontWeight: 500,
                  color: "oklch(50% 0.05 240)",
                }}
              >
                {task.skill}
              </span>
            </div>
          ))}
        </div>

        <p
          style={{
            textAlign: "center",
            fontSize: 13,
            color: "oklch(45% 0.07 240)",
            marginTop: 14,
          }}
        >
          Enroll in a plan to unlock your personalized daily tasks
        </p>
      </section>

      {/* ── Section 3: Skill scores ── */}
      <section
        style={{
          background: "rgba(255,255,255,0.85)",
          backdropFilter: "blur(20px)",
          WebkitBackdropFilter: "blur(20px)",
          borderRadius: 16,
          border: "1px solid rgba(255,255,255,0.9)",
          padding: 24,
          boxShadow:
            "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
        }}
      >
        <SkillScorePreview scores={scores} onViewAll={onViewStats} />
      </section>
    </div>
  );
}

/* ── Plan card ── */

interface PlanCardProps {
  weeks: number;
  label: string;
  taskFrequency: string;
  onClick: () => void;
}

function PlanCard({ weeks, label, taskFrequency, onClick }: PlanCardProps) {
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
        transition: "transform 0.2s ease, box-shadow 0.2s ease",
        cursor: "pointer",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-3px)";
        e.currentTarget.style.boxShadow =
          "0 8px 28px rgba(80,130,220,0.14), 0 2px 8px rgba(80,120,200,0.08)";
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
      <span
        style={{
          fontSize: 14,
          fontWeight: 600,
          color: "oklch(40% 0.07 240)",
        }}
      >
        {label}
      </span>
      <span
        style={{
          display: "inline-block",
          fontSize: 12,
          fontWeight: 600,
          color: "oklch(52% 0.18 240)",
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
          background: "oklch(52% 0.18 240)",
          color: "white",
          fontSize: 13,
          fontWeight: 700,
          cursor: "pointer",
          transition:
            "background 0.15s ease, transform 0.1s ease",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = "oklch(46% 0.18 240)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = "oklch(52% 0.18 240)";
        }}
        onMouseDown={(e) => {
          e.currentTarget.style.transform = "scale(0.97)";
        }}
        onMouseUp={(e) => {
          e.currentTarget.style.transform = "scale(1)";
        }}
      >
        Choose this plan
      </button>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════════════
   State B — Enrolled
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
}

function EnrolledView({
  enrollment,
  scores,
  onViewStats,
}: EnrolledViewProps) {
  const streakDays =
    (enrollment.current_week - 1) * 7 + enrollment.current_day_in_week;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
      {/* ── Top row: streak + plan info ── */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 10,
        }}
      >
        {/* Streak chip */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            background: "oklch(92% 0.06 80)",
            padding: "6px 14px",
            borderRadius: 20,
          }}
        >
          <span
            style={{
              display: "inline-block",
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "oklch(65% 0.2 55)",
              animation: "pulse-soft 2s ease-in-out infinite",
            }}
          />
          <FireIcon />
          <span
            style={{
              fontSize: 13,
              fontWeight: 700,
              color: "oklch(40% 0.15 60)",
            }}
          >
            Day {streakDays} streak
          </span>
        </div>

        {/* Week / plan label */}
        <span
          style={{
            fontSize: 13,
            fontWeight: 500,
            color: "oklch(45% 0.07 240)",
          }}
        >
          Week {enrollment.current_week} &middot;{" "}
          {enrollment.course.duration_weeks}-week plan
        </span>
      </div>

      <DailyTaskPanel
        key={`${enrollment.current_week}-${enrollment.current_day_in_week}`}
        enrollment={enrollment}
      />

      {/* ── Skill scores ── */}
      <section
        style={{
          background: "rgba(255,255,255,0.85)",
          backdropFilter: "blur(20px)",
          WebkitBackdropFilter: "blur(20px)",
          borderRadius: 16,
          border: "1px solid rgba(255,255,255,0.9)",
          padding: 24,
          boxShadow:
            "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
        }}
      >
        <SkillScorePreview scores={scores} onViewAll={onViewStats} />
      </section>
    </div>
  );
}
