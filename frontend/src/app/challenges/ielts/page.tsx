"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  ChevronLeft,
  ChevronRight,
  Check,
  Clock3,
  History,
  Lock,
  Medal,
  Play,
  RefreshCw,
  Trophy,
} from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { authApi } from "@/lib/auth-api";
import { challengesApi } from "@/lib/challenges-api";
import type { ChallengeLevelRead } from "@/lib/challenges-api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useAuthStore } from "@/store/authStore";

function formatMinutes(seconds: number): string {
  return `${Math.round(seconds / 60)} min`;
}

function scoreLabel(score: number | null): string {
  return score == null ? "No band yet" : `Best ${score.toFixed(1)}`;
}

export default function IELTSSprintPage() {
  const router = useRouter();
  const { logout } = useAuthStore();
  const { isReady } = useRequireAuth();

  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });

  const challengeQuery = useQuery({
    queryKey: ["challenge", "ielts"],
    queryFn: () => challengesApi.detail("ielts"),
    enabled: isReady && !!user?.diagnosis_completed,
  });

  const startMutation = useMutation({
    mutationFn: (level: ChallengeLevelRead) =>
      challengesApi.startAttempt("ielts", level.level_number),
    onSuccess: (attempt) => {
      router.push(`/challenges/ielts/attempt/${attempt.id}`);
    },
  });

  useEffect(() => {
    if (user && !user.diagnosis_completed) router.replace("/diagnosis");
  }, [user, router]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!isReady) return null;

  const loading = userLoading || challengeQuery.isLoading;
  const challenge = challengeQuery.data;

  return (
    <div
      style={{
        minHeight: "100vh",
        fontFamily: "var(--font-geist-sans), Arial, sans-serif",
        background: "#eef2f6",
        backgroundImage: "radial-gradient(rgba(15, 23, 42, 0.08) 1px, transparent 1px)",
        backgroundSize: "20px 20px",
      }}
    >
      <DashboardLayout
        user={user}
        onSignOut={handleLogout}
        mainStyle={{
          maxWidth: 1080,
          margin: "0 auto",
          padding: "40px 20px 76px",
        }}
      >
        <button
          onClick={() => router.push("/challenges")}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            background: "none",
            border: "none",
            color: "#0f172a",
            fontSize: 14,
            fontWeight: 600,
            cursor: "pointer",
            padding: 0,
            marginBottom: 24,
          }}
        >
          <ChevronLeft size={18} />
          Challenges
        </button>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 320px), 1fr))",
            gap: 24,
            alignItems: "stretch",
            marginBottom: 24,
          }}
        >
          <div
            style={{
              background: "#ffffff",
              borderRadius: 24,
              padding: 32,
              minHeight: 220,
              boxShadow: "0 4px 20px rgba(0, 0, 0, 0.02)",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
            }}
          >
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                color: "#0066cc",
                background: "#eef4ff",
                padding: "6px 12px",
                borderRadius: 100,
                fontSize: 13,
                fontWeight: 700,
                marginBottom: 20,
                alignSelf: "flex-start",
              }}
            >
              <Trophy size={16} aria-hidden />
              Challenges
            </div>
            <h1
              style={{
                margin: 0,
                color: "#0f172a",
                fontSize: 36,
                lineHeight: 1.15,
                fontWeight: 800,
                letterSpacing: "-0.02em",
              }}
            >
              {challenge?.name ?? "IELTS Sprint"}
            </h1>
            <p
              style={{
                margin: "12px 0 0",
                color: "#64748b",
                fontSize: 16,
                lineHeight: 1.5,
                maxWidth: 640,
              }}
            >
              {challenge?.short_description ??
                "Timed IELTS-flavored practice across all four sections."}
            </p>
          </div>

          <div
            style={{
              background: "#0b132b",
              color: "#f8fafc",
              borderRadius: 24,
              padding: 32,
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              minHeight: 220,
            }}
          >
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  fontSize: 15,
                  fontWeight: 700,
                  color: "#ffffff",
                  marginBottom: 12,
                }}
              >
                <Clock3 size={18} aria-hidden />
                Strict timer
              </div>
              <p style={{ margin: 0, fontSize: 15, lineHeight: 1.6, color: "#94a3b8" }}>
                No pause. Submit before the server deadline. Reading and Writing
                responses are saved for this phase.
              </p>
            </div>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                gap: 12,
                marginTop: 24,
              }}
            >
              {["20", "30", "40"].map((minute, index) => (
                <div
                  key={minute}
                  style={{
                    borderRadius: 16,
                    padding: "16px 12px",
                    textAlign: "center",
                    background: "#162032",
                  }}
                >
                  <div style={{ fontSize: 24, fontWeight: 800, color: "#ffffff" }}>{minute}</div>
                  <div style={{ fontSize: 13, color: "#64748b", marginTop: 4, fontWeight: 500 }}>L{index + 1} min</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section
          style={{
            display: "grid",
            gap: 16,
          }}
        >
          {loading && (
            <p style={{ margin: 0, color: "#64748b", fontSize: 14 }}>
              Loading challenges...
            </p>
          )}

          {challengeQuery.isError && (
            <div style={alertStyle}>
              Could not load IELTS Sprint. Seed the challenge and try again.
            </div>
          )}

          {startMutation.isError && (
            <div style={{ ...alertStyle, marginBottom: 14 }}>
              Could not start this level. Check that it is unlocked.
            </div>
          )}

          {challenge && (
            <>
              {challenge.levels.map((level) => {
                const isStarting =
                  startMutation.isPending &&
                  startMutation.variables?.level_number === level.level_number;
                return (
                  <div
                    key={level.id}
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: 20,
                      alignItems: "center",
                      borderRadius: 20,
                      padding: "24px 32px",
                      background: "#ffffff",
                      boxShadow: "0 4px 20px rgba(0, 0, 0, 0.02)",
                    }}
                  >
                    <div
                      style={{
                        width: 48,
                        height: 48,
                        display: "grid",
                        placeItems: "center",
                        borderRadius: 16,
                        background: level.unlocked ? "#dcfce7" : "transparent",
                        color: level.unlocked ? "#16a34a" : "#94a3b8",
                        flexShrink: 0,
                      }}
                    >
                      {level.unlocked ? <Check size={24} strokeWidth={3} /> : <Lock size={20} />}
                    </div>
                    <div style={{ minWidth: 220, flex: "1 1 300px" }}>
                      <h2
                        style={{
                          margin: 0,
                          color: level.unlocked ? "#0f172a" : "#64748b",
                          fontSize: 18,
                          fontWeight: 800,
                          letterSpacing: "-0.01em",
                        }}
                      >
                        {level.name}
                      </h2>
                      <div
                        style={{
                          display: "flex",
                          gap: 24,
                          flexWrap: "wrap",
                          marginTop: 10,
                          color: "#64748b",
                          fontSize: 14,
                          fontWeight: 500,
                        }}
                      >
                        <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <Clock3 size={16} />{" "}
                          {formatMinutes(level.time_limit_seconds)}
                        </span>
                        <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <Medal size={16} /> pass{" "}
                          {level.pass_threshold.toFixed(1)}
                        </span>
                        <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <RefreshCw size={16} />{" "}
                          {level.attempt_count} attempt{level.attempt_count !== 1 ? "s" : ""}
                        </span>
                        <span style={{ fontWeight: 600, color: level.best_score ? "#0f172a" : "#94a3b8" }}>{scoreLabel(level.best_score)}</span>
                      </div>
                    </div>
                    <button
                      type="button"
                      disabled={!level.unlocked || isStarting}
                      onClick={() => startMutation.mutate(level)}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: 8,
                        minWidth: 120,
                        border: "none",
                        borderRadius: 100,
                        padding: "12px 24px",
                        background: level.unlocked ? "#0066cc" : "#f1f5f9",
                        color: level.unlocked ? "#ffffff" : "#94a3b8",
                        fontSize: 15,
                        fontWeight: 700,
                        cursor: level.unlocked ? "pointer" : "not-allowed",
                        transition: "background 0.2s",
                      }}
                    >
                      <Play size={14} fill="currentColor" />
                      {isStarting ? "Starting" : "Start"}
                      <ChevronRight size={16} />
                    </button>
                  </div>
                );
              })}
            </>
          )}
        </section>
      </DashboardLayout>
    </div>
  );
}

const alertStyle = {
  background: "#fff3e0",
  border: "1px solid #ffd08a",
  color: "#68430a",
  borderRadius: 8,
  padding: "12px 14px",
  fontSize: 14,
  fontWeight: 700,
};
