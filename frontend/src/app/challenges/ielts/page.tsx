"use client";

import type { CSSProperties, ReactNode } from "react";
import { Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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
  ScrollText,
  Trophy,
} from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { authApi } from "@/lib/auth-api";
import {
  challengesApi,
  getChallengesApiError,
} from "@/lib/challenges-api";
import type { ChallengeLevelRead } from "@/lib/challenges-api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useAuthStore } from "@/store/authStore";

function formatMinutes(seconds: number): string {
  return `${Math.round(seconds / 60)} min`;
}

function scoreLabel(score: number | null): string {
  return score == null ? "No band yet" : `Best ${score.toFixed(1)}`;
}

function formatAttemptDate(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

/** Render inline `**bold**` spans inside a line of rule text. */
function renderInline(text: string): ReactNode {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, index) => {
    const bold = /^\*\*([^*]+)\*\*$/.exec(part);
    if (bold) {
      return (
        <strong key={index} style={{ color: "#0f172a", fontWeight: 800 }}>
          {bold[1]}
        </strong>
      );
    }
    return <span key={index}>{part}</span>;
  });
}

/** Turn the challenge's `rules_md` into a numbered list. */
function SprintRules({ rulesMd }: { rulesMd: string }) {
  const rules: string[] = [];
  rulesMd.split("\n").forEach((line) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("# ") || trimmed.startsWith("## ")) return;
    // Extract text from bullet points
    if (trimmed.startsWith("- ")) {
      rules.push(trimmed.slice(2));
      return;
    }
    // Skip bold-only lines and paragraphs that are already covered
    if (!trimmed.startsWith("**")) {
      rules.push(trimmed);
    }
  });

  return (
    <ul style={rulesListStyle}>
      {rules.map((rule, index) => (
        <li key={index} style={rulesListItemStyle}>
          {renderInline(rule)}
        </li>
      ))}
    </ul>
  );
}

// useSearchParams() requires a Suspense boundary for static prerender —
// without this wrapper `next build` fails on this page.
export default function IELTSSprintPage() {
  return (
    <Suspense fallback={null}>
      <IELTSSprintPageInner />
    </Suspense>
  );
}

function IELTSSprintPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [startError, setStartError] = useState<string | null>(null);
  const handledQueryRef = useRef<string | null>(null);
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

  const historyQuery = useQuery({
    queryKey: ["challenge-history", "ielts"],
    queryFn: () => challengesApi.history("ielts"),
    enabled: isReady && !!user?.diagnosis_completed,
  });

  const startMutation = useMutation({
    mutationFn: (level: ChallengeLevelRead) =>
      challengesApi.startAttempt("ielts", level.level_number),
    onMutate: () => {
      setStartError(null);
    },
    onSuccess: (attempt) => {
      router.push(`/challenges/ielts/attempt/${attempt.id}`);
    },
    onError: (error) => {
      const parsed = getChallengesApiError(error);
      if (parsed.status === 409 && parsed.attemptId != null) {
        router.push(`/challenges/ielts/attempt/${parsed.attemptId}`);
        return;
      }
      setStartError(parsed.message);
    },
  });

  useEffect(() => {
    if (user && !user.diagnosis_completed) router.replace("/diagnosis");
  }, [user, router]);

  useEffect(() => {
    const retryLevel = searchParams.get("retry");
    const startLevel = searchParams.get("start");
    const queryKey = `${retryLevel ?? ""}:${startLevel ?? ""}`;
    if (!challengeQuery.data || startMutation.isPending) return;
    if (handledQueryRef.current === queryKey) return;

    const parsedStart = Number(startLevel);
    const parsedRetry = Number(retryLevel);
    const triggerLevelStart = (level: ChallengeLevelRead | undefined) => {
      if (!level?.unlocked) return;
      handledQueryRef.current = queryKey;
      if (level.in_progress_attempt_id != null) {
        router.push(`/challenges/ielts/attempt/${level.in_progress_attempt_id}`);
        return;
      }
      startMutation.mutate(level);
    };

    if (Number.isFinite(parsedStart) && parsedStart >= 1 && parsedStart <= 3) {
      triggerLevelStart(
        challengeQuery.data.levels.find((item) => item.level_number === parsedStart),
      );
    } else if (Number.isFinite(parsedRetry) && parsedRetry >= 1 && parsedRetry <= 3) {
      triggerLevelStart(
        challengeQuery.data.levels.find((item) => item.level_number === parsedRetry),
      );
    }
  }, [
    challengeQuery.data,
    searchParams,
    startMutation.isPending,
    startMutation.mutate,
    router,
  ]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!isReady) return null;

  const loading = userLoading || challengeQuery.isLoading;
  const challenge = challengeQuery.data;
  const history = historyQuery.data?.attempts ?? [];
  const resumeAttempt = challenge?.levels.find(
    (level) => level.in_progress_attempt_id != null,
  );

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

        {resumeAttempt?.in_progress_attempt_id && (
          <div style={{ ...alertStyle, background: "#eef4ff", borderColor: "#bfd7ff", color: "#0f172a", marginBottom: 16 }}>
            <History size={18} aria-hidden />
            <div style={{ flex: 1 }}>
              You have an in-progress attempt on {resumeAttempt.name}. Resume to continue where
              you left off.
            </div>
            <button
              type="button"
              onClick={() =>
                router.push(
                  `/challenges/ielts/attempt/${resumeAttempt.in_progress_attempt_id}`,
                )
              }
              style={{
                border: "none",
                borderRadius: 999,
                padding: "8px 16px",
                background: "#0066cc",
                color: "white",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              Resume sprint
            </button>
          </div>
        )}

        {challenge?.rules_md && (
          <section style={rulesCardStyle}>
            <div style={rulesHeaderStyle}>
              <span style={rulesIconChipStyle}>
                <ScrollText size={20} aria-hidden />
              </span>
              <div>
                <h2 style={rulesTitleStyle}>How the sprint works</h2>
                <p style={rulesSubtitleStyle}>
                  Read this before you start — the timer is strict.
                </p>
              </div>
            </div>
            <div style={rulesBodyStyle}>
              <SprintRules rulesMd={challenge.rules_md} />
            </div>
          </section>
        )}

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

          {startError && (
            <div style={{ ...alertStyle, marginBottom: 14 }}>{startError}</div>
          )}

          {challenge && (
            <>
              {challenge.levels.map((level) => {
                const isStarting =
                  startMutation.isPending &&
                  startMutation.variables?.level_number === level.level_number;
                const resumeId = level.in_progress_attempt_id;
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
                      onClick={() => {
                        if (resumeId) {
                          router.push(`/challenges/ielts/attempt/${resumeId}`);
                          return;
                        }
                        startMutation.mutate(level);
                      }}
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
                      {resumeId ? "Resume" : isStarting ? "Starting" : "Start"}
                      <ChevronRight size={16} />
                    </button>
                  </div>
                );
              })}
            </>
          )}
        </section>

        {history.length > 0 && (
          <section style={{ marginTop: 28 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
              <History size={18} aria-hidden />
              <h2 style={{ margin: 0, fontSize: 20, fontWeight: 800, color: "#0f172a" }}>
                Recent attempts
              </h2>
            </div>
            <div style={{ display: "grid", gap: 10 }}>
              {history.slice(0, 5).map((attempt) => (
                <div
                  key={attempt.id}
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: 12,
                    alignItems: "center",
                    justifyContent: "space-between",
                    background: "white",
                    borderRadius: 16,
                    padding: "16px 18px",
                  }}
                >
                  <div>
                    <strong style={{ color: "#0f172a" }}>{attempt.level_name}</strong>
                    <div style={{ color: "#64748b", fontSize: 13, marginTop: 4 }}>
                      {formatAttemptDate(attempt.created_at)} · {attempt.status.replace("_", " ")}
                      {attempt.overall_score != null
                        ? ` · ${attempt.overall_score.toFixed(1)}`
                        : ""}
                      {attempt.is_best_for_level ? " · best" : ""}
                    </div>
                  </div>
                  {attempt.status === "in_progress" && (
                    <button
                      type="button"
                      onClick={() => router.push(`/challenges/ielts/attempt/${attempt.id}`)}
                      style={{
                        border: "none",
                        borderRadius: 999,
                        padding: "8px 14px",
                        background: "#0066cc",
                        color: "white",
                        fontWeight: 700,
                        cursor: "pointer",
                      }}
                    >
                      Resume
                    </button>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}
      </DashboardLayout>
      </div>
    </div>
  );
}

const alertStyle = {
  display: "flex",
  alignItems: "center",
  gap: 10,
  background: "#fff3e0",
  border: "1px solid #ffd08a",
  color: "#68430a",
  borderRadius: 8,
  padding: "12px 14px",
  fontSize: 14,
  fontWeight: 700,
};

const rulesCardStyle: CSSProperties = {
  marginBottom: 16,
  background: "white",
  borderRadius: 24,
  padding: 28,
  border: "1px solid #eef2f7",
  boxShadow: "0 4px 20px rgba(0,0,0,0.02)",
};

const rulesHeaderStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 14,
  marginBottom: 20,
  paddingBottom: 18,
  borderBottom: "1px solid #eef2f7",
};

const rulesIconChipStyle: CSSProperties = {
  width: 46,
  height: 46,
  borderRadius: 14,
  display: "grid",
  placeItems: "center",
  background: "#eef4ff",
  color: "#0066cc",
  flexShrink: 0,
};

const rulesTitleStyle: CSSProperties = {
  margin: 0,
  fontSize: 19,
  fontWeight: 800,
  color: "#0f172a",
  letterSpacing: "-0.01em",
};

const rulesSubtitleStyle: CSSProperties = {
  margin: "3px 0 0",
  fontSize: 13.5,
  color: "#64748b",
  fontWeight: 500,
};

const rulesBodyStyle: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 12,
};

const rulesParagraphStyle: CSSProperties = {
  margin: 0,
  color: "#475569",
  fontSize: 14.5,
  lineHeight: 1.65,
};

const rulesHeadingStyle: CSSProperties = {
  margin: "4px 0 0",
  fontSize: 15,
  fontWeight: 800,
  color: "#0f172a",
};

const rulesWarningStyle: CSSProperties = {
  display: "flex",
  gap: 10,
  alignItems: "flex-start",
  background: "#fff7ed",
  border: "1px solid #fed7aa",
  color: "#9a3412",
  borderRadius: 14,
  padding: "13px 16px",
  fontSize: 14.5,
  fontWeight: 700,
  lineHeight: 1.55,
};

const rulesBulletStyle: CSSProperties = {
  display: "flex",
  gap: 10,
  alignItems: "flex-start",
  color: "#475569",
  fontSize: 14.5,
  lineHeight: 1.6,
};

const rulesBulletDotStyle: CSSProperties = {
  width: 7,
  height: 7,
  borderRadius: "50%",
  background: "#0066cc",
  marginTop: 8,
  flexShrink: 0,
};

const rulesListStyle: CSSProperties = {
  margin: 0,
  paddingLeft: 24,
  listStyleType: "disc",
};

const rulesListItemStyle: CSSProperties = {
  color: "#475569",
  fontSize: 14.5,
  lineHeight: 1.65,
  fontWeight: 500,
  marginBottom: 8,
};
