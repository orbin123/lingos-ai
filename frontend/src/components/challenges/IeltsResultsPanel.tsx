"use client";

import type { CSSProperties } from "react";
import { useRouter } from "next/navigation";
import { RotateCcw, Trophy } from "lucide-react";
import type { ChallengeAttemptRead } from "@/lib/challenges-api";

type SectionKey = "listening" | "reading" | "writing" | "speaking";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/**
 * The IELTS sprint scorecard. Lives on its own (`/attempt/[id]/result`) so
 * results are a destination rather than an inline footnote under the task.
 * Self-contained styling — does not depend on the attempt page's style consts.
 */
export function IeltsResultsPanel({ attempt }: { attempt: ChallengeAttemptRead }) {
  const router = useRouter();
  const passThreshold = attempt.pass_threshold ?? 6.0;
  const passed = attempt.passed === true;
  const levelNumber = attempt.level_number ?? 1;
  const scores = attempt.section_scores ?? {};
  // Average of the section bands (falls back to the stored overall band).
  const sectionValues = (["listening", "reading", "writing", "speaking"] as SectionKey[])
    .map((section) => scores[section])
    .filter((value): value is number => typeof value === "number");
  const averageScore =
    sectionValues.length > 0
      ? sectionValues.reduce((sum, value) => sum + value, 0) / sectionValues.length
      : attempt.overall_score ?? null;
  const feedbackReport = isRecord(attempt.feedback_report) ? attempt.feedback_report : {};
  const feedbackSummary =
    typeof feedbackReport.overall_summary === "string"
      ? feedbackReport.overall_summary
      : null;
  const feedbackSections = isRecord(feedbackReport.sections)
    ? feedbackReport.sections
    : {};
  const nextTips = (["listening", "reading", "writing", "speaking"] as SectionKey[])
    .map((section) => {
      const sectionFeedback = feedbackSections[section];
      if (!isRecord(sectionFeedback) || typeof sectionFeedback.next_tip !== "string") {
        return null;
      }
      return { section, tip: sectionFeedback.next_tip };
    })
    .filter((tip): tip is { section: SectionKey; tip: string } => tip !== null);

  const evaluationReport = isRecord(attempt.evaluation_report)
    ? attempt.evaluation_report
    : {};
  const readingReview = isRecord(evaluationReport.reading) ? evaluationReport.reading : null;
  const listeningReview = isRecord(evaluationReport.listening)
    ? evaluationReport.listening
    : null;
  const writingReview = isRecord(evaluationReport.writing) ? evaluationReport.writing : null;
  const readingQuestions = Array.isArray(readingReview?.questions)
    ? readingReview.questions.filter(isRecord)
    : [];
  const listeningQuestions = Array.isArray(listeningReview?.questions)
    ? listeningReview.questions.filter(isRecord)
    : [];
  const writingItems = Array.isArray(writingReview?.items)
    ? writingReview.items.filter(isRecord)
    : [];

  return (
    <section style={panelStyle}>
      <div style={{ display: "flex", gap: 18, flexWrap: "wrap", alignItems: "center" }}>
        <div
          style={{
            ...scoreDialStyle,
            background: passed ? "#dcfce7" : "#fee2e2",
            color: passed ? "#15803d" : "#b91c1c",
          }}
        >
          <Trophy size={24} aria-hidden />
          <strong style={{ fontSize: 22, fontWeight: 800 }}>
            {attempt.overall_score?.toFixed(1) ?? "--"}
          </strong>
        </div>
        <div style={{ flex: "1 1 260px" }}>
          <h2 style={sectionTitleStyle}>
            {passed
              ? "Level passed"
              : attempt.status === "timed_out"
                ? "Timed out"
                : "Level not passed"}
          </h2>
          <p style={{ margin: "8px 0 0", color: "#4a6880", lineHeight: 1.6, fontSize: 14 }}>
            {passed
              ? `You reached the pass threshold of ${passThreshold.toFixed(1)}.`
              : `You needed ${passThreshold.toFixed(1)} to pass this level.`}
          </p>
          {passed && levelNumber < 3 && (
            <p style={{ margin: "8px 0 0", color: "#15803d", fontWeight: 700, fontSize: 14 }}>
              Level {levelNumber + 1} is now unlocked.
            </p>
          )}
          <p style={{ margin: "8px 0 0", color: "#4a6880", lineHeight: 1.6, fontSize: 14 }}>
            {feedbackSummary ??
              "Reading and Listening were graded from answer keys, Writing was evaluated, and Speaking was scored from transcripts only."}
          </p>
        </div>
      </div>
      <div style={scoreGridStyle}>
        {(["listening", "reading", "writing", "speaking"] as SectionKey[]).map((section) => (
          <div key={section} style={scoreCellStyle}>
            <span style={{ textTransform: "capitalize", fontSize: 13, fontWeight: 700 }}>
              {section}
            </span>
            <strong style={{ color: "#0d1f36", fontSize: 15 }}>
              {scores[section]?.toFixed(1) ?? "--"}
            </strong>
          </div>
        ))}
      </div>
      <div style={averageRowStyle}>
        <div
          style={{
            ...averageCircleStyle,
            background: passed ? "#dcfce7" : "#fee2e2",
            borderColor: passed ? "#16a34a" : "#dc2626",
            color: passed ? "#15803d" : "#b91c1c",
          }}
        >
          <strong style={{ fontSize: 22, fontWeight: 800, lineHeight: 1 }}>
            {averageScore != null ? averageScore.toFixed(1) : "--"}
          </strong>
          <span style={{ fontSize: 10, fontWeight: 800, letterSpacing: "0.04em" }}>
            AVG
          </span>
        </div>
        <span
          style={{
            fontSize: 13.5,
            fontWeight: 800,
            color: passed ? "#15803d" : "#b91c1c",
          }}
        >
          {passed ? "Passed" : "Failed"} · pass mark {passThreshold.toFixed(1)}
        </span>
      </div>
      {(readingQuestions.length > 0 || listeningQuestions.length > 0) && (
        <div style={{ marginTop: 18, display: "grid", gap: 12 }}>
          {readingQuestions.length > 0 && (
            <ReviewBlock title="Reading review" questions={readingQuestions} />
          )}
          {listeningQuestions.length > 0 && (
            <ReviewBlock title="Listening review" questions={listeningQuestions} />
          )}
        </div>
      )}
      {writingItems.length > 0 && (
        <div style={{ marginTop: 14 }}>
          <h3 style={{ ...sectionTitleStyle, fontSize: 15, marginBottom: 10 }}>Writing summary</h3>
          <div style={{ display: "grid", gap: 10 }}>
            {writingItems.map((item, index) => {
              const issues = Array.isArray(item.issues) ? item.issues.filter(isRecord) : [];
              const summary =
                typeof item.summary === "string" ? item.summary : "Writing feedback unavailable.";
              return (
                <div key={String(item.item_id ?? index)} style={feedbackTipStyle}>
                  <strong style={{ display: "block", marginBottom: 6 }}>{summary}</strong>
                  {issues.slice(0, 2).map((issue, issueIndex) => (
                    <p
                      key={issueIndex}
                      style={{ margin: "4px 0 0", color: "#4a6880", fontSize: 13.5, lineHeight: 1.5 }}
                    >
                      {typeof issue.issue === "string" ? issue.issue : "Review this sentence."}
                    </p>
                  ))}
                </div>
              );
            })}
          </div>
        </div>
      )}
      {nextTips.length > 0 && (
        <div style={feedbackTipGridStyle}>
          {nextTips.map(({ section, tip }) => (
            <div key={section} style={feedbackTipStyle}>
              <span
                style={{
                  textTransform: "capitalize",
                  fontSize: 12,
                  fontWeight: 800,
                  color: "#0070C4",
                  letterSpacing: "0.01em",
                }}
              >
                {section}
              </span>
              <p style={{ margin: "6px 0 0", lineHeight: 1.55, color: "#4a6880", fontSize: 13.5 }}>
                {tip}
              </p>
            </div>
          ))}
        </div>
      )}
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 18 }}>
        <button type="button" style={submitButtonStyle} onClick={() => router.push("/challenges/ielts")}>
          Back to IELTS Sprint
        </button>
        <button
          type="button"
          style={secondaryButtonStyle}
          onClick={() => router.push(`/challenges/ielts?retry=${levelNumber}`)}
        >
          <RotateCcw size={16} aria-hidden />
          Retry level
        </button>
      </div>
    </section>
  );
}

function ReviewBlock({
  title,
  questions,
}: {
  title: string;
  questions: Record<string, unknown>[];
}) {
  return (
    <div style={feedbackTipStyle}>
      <h3 style={{ ...sectionTitleStyle, fontSize: 15, marginBottom: 10 }}>{title}</h3>
      <div style={{ display: "grid", gap: 8 }}>
        {questions.map((question, index) => {
          const correct = question.correct === true;
          const prompt =
            typeof question.prompt === "string"
              ? question.prompt
              : `Question ${index + 1}`;
          return (
            <div
              key={String(question.item_id ?? index)}
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: 12,
                color: correct ? "#15803d" : "#b91c1c",
                fontSize: 13.5,
                fontWeight: 600,
              }}
            >
              <span style={{ color: "#0d1f36", fontWeight: 600 }}>{prompt}</span>
              <span>{correct ? "Correct" : "Incorrect"}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── Styles ─── */

const panelStyle: CSSProperties = {
  background: "rgba(255,255,255,0.85)",
  backdropFilter: "blur(18px)",
  WebkitBackdropFilter: "blur(18px)",
  border: "1.5px solid rgba(0,112,196,0.2)",
  borderRadius: 22,
  padding: 28,
  boxShadow: "0 4px 24px rgba(80,110,180,0.1)",
};

const sectionTitleStyle: CSSProperties = {
  margin: 0,
  color: "#0d1f36",
  fontSize: 17,
  lineHeight: 1.3,
  fontWeight: 800,
  letterSpacing: 0,
};

const secondaryButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 7,
  border: "1.5px solid #d0dde9",
  borderRadius: 10,
  background: "white",
  color: "#0d1f36",
  padding: "9px 14px",
  fontSize: 13,
  fontWeight: 700,
  cursor: "pointer",
  fontFamily: "inherit",
};

const submitButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 8,
  padding: "12px 24px",
  borderRadius: 14,
  fontSize: 14.5,
  fontWeight: 800,
  background: "#0070C4",
  color: "white",
  border: "none",
  boxShadow: "0 4px 16px rgba(0,112,196,0.35)",
  cursor: "pointer",
  flexShrink: 0,
};

const scoreDialStyle: CSSProperties = {
  width: 110,
  height: 110,
  borderRadius: "50%",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: 6,
  background: "#d6e8f7",
  color: "#0070C4",
};

const scoreGridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
  gap: 10,
  marginTop: 18,
};

const averageRowStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 14,
  marginTop: 14,
};

const averageCircleStyle: CSSProperties = {
  width: 72,
  height: 72,
  borderRadius: "50%",
  border: "2.5px solid",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: 2,
  flexShrink: 0,
};

const scoreCellStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 10,
  border: "1.5px solid #d0dde9",
  borderRadius: 12,
  padding: "12px 14px",
  color: "#4a6880",
  background: "white",
};

const feedbackTipGridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  gap: 10,
  marginTop: 14,
};

const feedbackTipStyle: CSSProperties = {
  border: "1.5px solid #d0dde9",
  borderRadius: 12,
  padding: "14px 16px",
  color: "#0d1f36",
  background: "white",
  fontSize: 14,
};
