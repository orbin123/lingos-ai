"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { useRequireAuth } from "@/hooks/useRequireAuth";
import { authApi } from "@/lib/auth-api";
import { progressApi } from "@/lib/progress-api";
import { CourseCertificate } from "@/components/completion/CourseCertificate";

const PAGE_BG = "oklch(91% 0.04 245)";

function RecapStat({ value, label }: { value: string; label: string }) {
  return (
    <div
      style={{
        flex: "1 1 0",
        minWidth: 120,
        background: "white",
        border: "1.5px solid oklch(88% 0.025 240)",
        borderRadius: 14,
        padding: "16px 18px",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: 26, fontWeight: 800, color: "#0070C4" }}>{value}</div>
      <div
        style={{
          fontSize: 12.5,
          fontWeight: 600,
          color: "oklch(45% 0.07 240)",
          marginTop: 4,
        }}
      >
        {label}
      </div>
    </div>
  );
}

export default function CourseCompletePage() {
  const router = useRouter();
  const { isReady } = useRequireAuth();

  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });

  const completedAt = user?.preference?.course_completed_at ?? null;

  // Guard: this page only exists for learners who have finished the course.
  useEffect(() => {
    if (user && !completedAt) router.replace("/dashboard");
  }, [user, completedAt, router]);

  const { data: skillScores } = useQuery({
    queryKey: ["progress", "scores"],
    queryFn: progressApi.getScores,
    enabled: isReady && !!completedAt,
  });

  if (!isReady || isLoading || !user) return null;
  if (!completedAt || !user.preference) return null; // redirecting

  const courseLength = user.preference.course_length;
  const totalWeeks = courseLength === "48w" ? 48 : 24;
  const learnerName = user.display_name || user.name || "Learner";
  const avgScore =
    skillScores && skillScores.length > 0
      ? skillScores.reduce((sum, s) => sum + s.score, 0) / skillScores.length
      : null;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: PAGE_BG,
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        padding: "48px 20px 72px",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />
      <style>{`
        @media print {
          .cc-noprint { display: none !important; }
          body { background: #fff !important; }
        }
      `}</style>

      <div style={{ maxWidth: 760, margin: "0 auto" }}>
        {/* Congratulations hero */}
        <div className="cc-noprint" style={{ textAlign: "center", marginBottom: 28 }}>
          <div style={{ fontSize: 46, lineHeight: 1 }}>🎉</div>
          <h1
            style={{
              fontSize: 30,
              fontWeight: 800,
              color: "oklch(20% 0.09 245)",
              margin: "14px 0 6px",
              letterSpacing: "-0.01em",
            }}
          >
            Congratulations, {learnerName}!
          </h1>
          <p
            style={{
              fontSize: 15,
              color: "oklch(45% 0.07 240)",
              margin: 0,
              lineHeight: 1.6,
            }}
          >
            You&apos;ve completed every lesson of your course. Here&apos;s your
            certificate — and the whole curriculum stays open for review.
          </p>
        </div>

        {/* Recap stats */}
        <div
          className="cc-noprint"
          style={{
            display: "flex",
            gap: 12,
            flexWrap: "wrap",
            marginBottom: 28,
          }}
        >
          <RecapStat value={`${totalWeeks}`} label="weeks completed" />
          <RecapStat value="100%" label="course progress" />
          {avgScore !== null && (
            <RecapStat value={avgScore.toFixed(1)} label="avg. skill score" />
          )}
        </div>

        {/* Certificate */}
        <CourseCertificate
          name={learnerName}
          courseLength={courseLength}
          completedAt={completedAt}
        />

        {/* Actions */}
        <div
          className="cc-noprint"
          style={{
            display: "flex",
            gap: 12,
            justifyContent: "center",
            flexWrap: "wrap",
            marginTop: 28,
          }}
        >
          <button
            type="button"
            onClick={() => window.print()}
            style={{
              padding: "13px 22px",
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
            Download certificate
          </button>
          <button
            type="button"
            onClick={() => router.push("/dashboard")}
            style={{
              padding: "13px 22px",
              borderRadius: 14,
              border: "1.5px solid oklch(85% 0.03 240)",
              background: "white",
              color: "oklch(28% 0.08 245)",
              fontFamily: "inherit",
              fontSize: 14,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Back to dashboard
          </button>
        </div>
      </div>
    </div>
  );
}
