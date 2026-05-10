"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { tasksApi } from "@/lib/tasks-api";
import type {
  ResponseGraded,
  LearningSessionSnapshot,
  EvaluationQuestionResult,
} from "@/lib/tasks-api";
import { useRequireAuth } from "@/hooks/useRequireAuth";

// ── Tokens ─────────────────────────────────────────────────────
const T = {
  navy: "oklch(20% 0.09 245)",
  inkMuted: "oklch(45% 0.07 240)",
  line: "oklch(86% 0.025 240)",
  primary: "oklch(52% 0.18 240)",
  green: "oklch(55% 0.18 155)",
  amber: "oklch(60% 0.18 70)",
  red: "oklch(50% 0.18 15)",
  bg: "radial-gradient(ellipse 80% 60% at 50% 0%, oklch(86% 0.07 240) 0%, oklch(90% 0.045 245) 50%, oklch(93% 0.025 250) 100%)",
};

function scoreColor(pct: number) {
  if (pct >= 70) return T.green;
  if (pct >= 50) return T.amber;
  return T.red;
}

// ── Shell ───────────────────────────────────────────────────────
function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        minHeight: "100vh",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        background: T.bg,
        position: "relative",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap"
      />
      <div
        aria-hidden
        style={{
          position: "fixed",
          inset: 0,
          pointerEvents: "none",
          backgroundImage: "radial-gradient(circle, rgba(90,130,210,0.18) 1px, transparent 1px)",
          backgroundSize: "22px 22px",
          zIndex: 0,
        }}
      />
      <div style={{ position: "relative", zIndex: 1, maxWidth: 720, margin: "0 auto", padding: "40px 20px 80px" }}>
        <div
          style={{
            background: "rgba(255,255,255,0.88)",
            backdropFilter: "blur(20px)",
            borderRadius: 18,
            border: "1px solid rgba(255,255,255,0.9)",
            padding: "28px 28px 32px",
            boxShadow: "0 4px 32px rgba(80,110,180,0.1)",
          }}
        >
          {children}
        </div>
      </div>
      <style>{`@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}`}</style>
    </div>
  );
}

// ── Back button ─────────────────────────────────────────────────
function BackButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        padding: "8px 14px",
        borderRadius: 10,
        border: `1.5px solid ${T.line}`,
        background: "rgba(255,255,255,0.8)",
        color: T.inkMuted,
        fontSize: 13,
        fontWeight: 600,
        cursor: "pointer",
        marginBottom: 22,
        fontFamily: "inherit",
      }}
    >
      ← Back
    </button>
  );
}

// ── Section card ────────────────────────────────────────────────
function Section({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div
      style={{
        borderRadius: 12,
        background: "oklch(98% 0.008 240)",
        border: `1px solid ${T.line}`,
        padding: "16px 18px",
        marginBottom: 14,
        ...style,
      }}
    >
      {children}
    </div>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <p style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: T.primary, margin: "0 0 10px" }}>
      {children}
    </p>
  );
}

// ── Read-only badge ─────────────────────────────────────────────
function ReadOnlyBadge() {
  return (
    <span
      style={{
        display: "inline-block",
        fontSize: 11,
        fontWeight: 700,
        color: T.inkMuted,
        background: "oklch(92% 0.02 240)",
        border: `1px solid ${T.line}`,
        padding: "3px 9px",
        borderRadius: 20,
        marginLeft: 10,
        verticalAlign: "middle",
      }}
    >
      Read only
    </span>
  );
}

// ════════════════════════════════════════════════════════════════
// STANDARD TASK RESULT VIEW
// ════════════════════════════════════════════════════════════════

function StandardResultView({ result, taskName, taskType }: { result: ResponseGraded; taskName?: string; taskType?: string }) {
  const { evaluation, feedback } = result;
  const report = evaluation.report;
  const fb = feedback.body;
  const percentage = Number(evaluation.percentage ?? fb.score ?? 0);
  const color = scoreColor(percentage);
  const questions = report.questions ?? {};
  const questionEntries = Object.entries(questions);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14, animation: "fadeIn 0.35s ease both" }}>
      {/* Header */}
      <div>
        <p style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: T.primary, margin: "0 0 4px" }}>
          {taskType ? taskType.replace(/_/g, " ") : "Task"} · Completed
        </p>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: T.navy, margin: 0, letterSpacing: "-0.02em" }}>
          {taskName || "Task Result"}
          <ReadOnlyBadge />
        </h1>
      </div>

      {/* Score + feedback */}
      <div style={{ display: "grid", gridTemplateColumns: "minmax(110px, 0.4fr) 1fr", gap: 12 }}>
        <Section style={{ padding: 18, marginBottom: 0 }}>
          <SectionTitle>Score</SectionTitle>
          <p style={{ fontSize: 34, fontWeight: 800, color, margin: 0, lineHeight: 1 }}>
            {Math.round(percentage)}%
          </p>
          <p style={{ fontSize: 12, color: T.inkMuted, margin: "6px 0 0" }}>
            {evaluation.overall_score.toFixed(1)} / 10
          </p>
        </Section>
        <Section style={{ marginBottom: 0 }}>
          <SectionTitle>Feedback</SectionTitle>
          <p style={{ fontSize: 14, color: T.navy, lineHeight: 1.6, margin: "0 0 8px" }}>
            {fb.overall_message}
          </p>
          <p style={{ fontSize: 13, color: T.inkMuted, lineHeight: 1.55, margin: 0 }}>
            <strong>Practice next:</strong> {fb.practice_suggestion}
          </p>
        </Section>
      </div>

      {/* Evaluation rows */}
      {questionEntries.length > 0 && (
        <Section>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <SectionTitle>Evaluation</SectionTitle>
            <span style={{ fontSize: 12, fontWeight: 700, color: T.inkMuted }}>
              {report.correct_count ?? 0} / {report.total ?? questionEntries.length} correct · {Number(report.percentage ?? percentage).toFixed(1)}%
            </span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {questionEntries.map(([id, q]) => (
              <EvalRow key={id} id={id} question={q as EvaluationQuestionResult} />
            ))}
          </div>
        </Section>
      )}

      {/* Errors */}
      {fb.errors && fb.errors.length > 0 && (
        <Section style={{ background: "oklch(98% 0.012 70)", borderColor: "oklch(86% 0.08 70)" }}>
          <SectionTitle>What to fix</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {fb.errors.map((error: { question_id: string; user_answer: string; correct_answer: string; correction?: string | null; why_wrong: string; rule: string; memory_tip: string }) => (
              <div key={error.question_id}>
                <p style={{ fontSize: 13, fontWeight: 700, color: "oklch(25% 0.08 70)", margin: "0 0 3px" }}>
                  {error.question_id}: {error.user_answer || "(blank)"} → {error.correct_answer}
                </p>
                {error.correction && (
                  <p style={{ fontSize: 13, color: "oklch(32% 0.07 70)", margin: "0 0 3px" }}>
                    <strong>Correction:</strong> {error.correction}
                  </p>
                )}
                <p style={{ fontSize: 13, color: "oklch(32% 0.07 70)", margin: "0 0 3px" }}>{error.why_wrong}</p>
                <p style={{ fontSize: 12, color: "oklch(40% 0.07 70)", margin: 0 }}>
                  <strong>Rule:</strong> {error.rule} <strong>Tip:</strong> {error.memory_tip}
                </p>
              </div>
            ))}
          </div>
        </Section>
      )}
    </div>
  );
}

function EvalRow({ id, question }: { id: string; question: EvaluationQuestionResult }) {
  const isCorrect = question.correct === true;
  const score = typeof question.score === "number" ? question.score : null;

  return (
    <div
      style={{
        borderRadius: 9,
        background: isCorrect ? "oklch(97% 0.025 155)" : "white",
        border: `1px solid ${isCorrect ? "oklch(88% 0.08 155)" : T.line}`,
        padding: "10px 12px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
        <span style={{ fontSize: 13, fontWeight: 800, color: T.navy }}>{id}</span>
        <span style={{ fontSize: 12, fontWeight: 800, color: isCorrect ? T.green : T.red }}>
          {score !== null ? `${score.toFixed(1)} / 1` : isCorrect ? "Correct" : "Incorrect"}
        </span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, fontSize: 12, color: T.inkMuted }}>
        <span>Your answer: <strong>{String(question.user_answer || "(blank)")}</strong></span>
        <span>Correct: <strong>{String(question.correct_answer ?? "—")}</strong></span>
      </div>
      {question.correction && (
        <p style={{ fontSize: 12, color: "oklch(34% 0.07 240)", margin: "6px 0 0" }}>
          <strong>Correction:</strong> {question.correction}
        </p>
      )}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════
// CHAT SESSION SNAPSHOT VIEW
// ════════════════════════════════════════════════════════════════

function ChatSessionView({ session }: { session: LearningSessionSnapshot }) {
  const evalData = session.evaluation as Record<string, unknown> | null;
  const feedbackData = session.feedback as Record<string, unknown> | null;
  const percentage = evalData ? Number(evalData.percentage ?? (Number(evalData.overall_score ?? 0) * 10)) : null;
  const overallScore = evalData ? Number(evalData.overall_score ?? 0) : null;

  const completedAt = new Date(session.created_at).toLocaleString("en", {
    month: "short", day: "numeric", hour: "numeric", minute: "2-digit",
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14, animation: "fadeIn 0.35s ease both" }}>
      {/* Header */}
      <div>
        <p style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: T.primary, margin: "0 0 4px" }}>
          Chat session · {session.skill_name} · {completedAt}
        </p>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: T.navy, margin: 0, letterSpacing: "-0.02em" }}>
          {session.topic}
          <ReadOnlyBadge />
        </h1>
      </div>

      {/* Score */}
      {percentage !== null && overallScore !== null && (
        <Section style={{ display: "flex", gap: 20, alignItems: "center", flexWrap: "wrap" }}>
          <div>
            <SectionTitle>Score</SectionTitle>
            <p style={{ fontSize: 34, fontWeight: 800, color: scoreColor(percentage), margin: 0, lineHeight: 1 }}>
              {Math.round(percentage)}%
            </p>
            <p style={{ fontSize: 12, color: T.inkMuted, margin: "4px 0 0" }}>{overallScore.toFixed(1)} / 10</p>
          </div>
          {feedbackData && (
            <div style={{ flex: 1 }}>
              <SectionTitle>Feedback</SectionTitle>
              <p style={{ fontSize: 14, color: T.navy, lineHeight: 1.6, margin: 0 }}>
                {String(feedbackData.overall_message ?? feedbackData.summary ?? "")}
              </p>
            </div>
          )}
        </Section>
      )}

      {/* Conversation */}
      {session.messages.length > 0 && (
        <Section>
          <SectionTitle>Conversation</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {session.messages.map((msg, i) => {
              const isUser = msg.role === "user";
              const content = String(msg.content ?? "");
              if (!content.trim()) return null;
              return (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    justifyContent: isUser ? "flex-end" : "flex-start",
                  }}
                >
                  <div
                    style={{
                      maxWidth: "82%",
                      padding: "10px 14px",
                      borderRadius: isUser ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
                      background: isUser ? T.primary : "oklch(95% 0.02 240)",
                      color: isUser ? "white" : T.navy,
                      fontSize: 13.5,
                      lineHeight: 1.55,
                      fontWeight: isUser ? 500 : 400,
                    }}
                  >
                    {content}
                  </div>
                </div>
              );
            })}
          </div>
        </Section>
      )}

      {/* User submission summary */}
      {session.user_submission && Object.keys(session.user_submission).length > 0 && (
        <Section>
          <SectionTitle>Your answers</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {Object.entries(session.user_submission).map(([k, v]) => (
              <div key={k} style={{ fontSize: 13, color: T.navy }}>
                <strong>{k.replace(/_/g, " ")}:</strong>{" "}
                <span style={{ color: T.inkMuted }}>{String(v)}</span>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Focus areas from feedback */}
      {feedbackData && Array.isArray(feedbackData.errors) && (feedbackData.errors as unknown[]).length > 0 && (
        <Section style={{ background: "oklch(98% 0.012 70)", borderColor: "oklch(86% 0.08 70)" }}>
          <SectionTitle>What to fix</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {(feedbackData.errors as Record<string, unknown>[]).map((err, i) => (
              <div key={i}>
                {Boolean(err.why_wrong) && (
                  <p style={{ fontSize: 13, color: "oklch(32% 0.07 70)", margin: "0 0 3px" }}>
                    {String(err.why_wrong)}
                  </p>
                )}
                {Boolean(err.rule) && (
                  <p style={{ fontSize: 12, color: "oklch(40% 0.07 70)", margin: 0 }}>
                    <strong>Rule:</strong> {String(err.rule)}
                  </p>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════
// MAIN PAGE
// ════════════════════════════════════════════════════════════════

export default function TaskHistoryPage() {
  const params = useParams();
  const router = useRouter();
  const { isReady } = useRequireAuth();

  const userTaskId = Number(params.userTaskId);

  // Try standard task result first
  const standardQuery = useQuery({
    queryKey: ["task-result", userTaskId],
    queryFn: () => tasksApi.getTaskResult(userTaskId),
    enabled: isReady && !isNaN(userTaskId),
    retry: false,
  });

  // Fall back to chat session if standard result returns 404
  const standardFailed =
    standardQuery.isError &&
    (standardQuery.error as AxiosError)?.response?.status === 404;

  const chatQuery = useQuery({
    queryKey: ["session-by-task", userTaskId],
    queryFn: () => tasksApi.getSessionByTask(userTaskId),
    enabled: isReady && standardFailed,
    retry: false,
  });

  if (!isReady) return null;

  if (standardQuery.isLoading || (standardFailed && chatQuery.isLoading)) {
    return (
      <Shell>
        <div style={{ textAlign: "center", padding: "48px 0" }}>
          <div
            style={{
              width: 32,
              height: 32,
              border: "3px solid oklch(88% 0.03 240)",
              borderTopColor: T.primary,
              borderRadius: "50%",
              margin: "0 auto 14px",
              animation: "spin 0.8s linear infinite",
            }}
          />
          <p style={{ fontSize: 14, color: T.inkMuted }}>Loading session…</p>
          <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
        </div>
      </Shell>
    );
  }

  // Both failed
  if (
    (standardQuery.isError && !standardFailed) ||
    (standardFailed && chatQuery.isError)
  ) {
    return (
      <Shell>
        <BackButton onClick={() => router.back()} />
        <p style={{ fontSize: 15, color: T.red }}>
          Could not load this session. It may not exist or has been removed.
        </p>
      </Shell>
    );
  }

  // Standard task result
  if (standardQuery.data) {
    return (
      <Shell>
        <BackButton onClick={() => router.back()} />
        <StandardResultView result={standardQuery.data} />
      </Shell>
    );
  }

  // Chat session snapshot
  if (chatQuery.data) {
    return (
      <Shell>
        <BackButton onClick={() => router.back()} />
        <ChatSessionView session={chatQuery.data} />
      </Shell>
    );
  }

  return null;
}
