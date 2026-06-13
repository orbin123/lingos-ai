"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import { useQuery } from "@tanstack/react-query";

import { AdminLayout } from "@/components/admin/AdminLayout";
import {
  AdminPanel,
  MetricCard,
  formatAdminDateTime,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import { adminApi } from "@/lib/admin-api";

const DAYS = 7;

export default function AdminAIQualityPage() {
  const qualityQuery = useQuery({
    queryKey: ["admin", "ai-quality", DAYS],
    queryFn: () => adminApi.aiQuality(DAYS),
  });

  const report = qualityQuery.data;
  const feedback = report?.means.find((row) => row.target_type === "feedback");
  const mentorNote = report?.means.find((row) => row.target_type === "mentor_note");
  const worst = report?.worst ?? [];
  const series = report?.series ?? [];

  return (
    <AdminLayout
      title="AI Quality"
      eyebrow={`LLM-as-judge · last ${DAYS} days`}
    >
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
          gap: 14,
          marginBottom: 18,
        }}
      >
        <MetricCard label="Mean accuracy" value={fmtScore(feedback?.mean_accuracy)} />
        <MetricCard label="Mean relevance" value={fmtScore(feedback?.mean_relevance)} />
        <MetricCard label="Mean helpfulness" value={fmtScore(feedback?.mean_helpfulness)} />
        <MetricCard label="Mean correctness" value={fmtScore(feedback?.mean_correctness)} />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
          gap: 14,
          marginBottom: 18,
        }}
      >
        <MetricCard
          label="Mentor-note faithfulness (RAG)"
          value={fmtScore(mentorNote?.mean_faithfulness)}
        />
        <MetricCard
          label="Mentor notes judged"
          value={mentorNote?.judged_count ?? 0}
        />
        <MetricCard
          label="Feedback judged"
          value={feedback?.judged_count ?? 0}
        />
        <MetricCard
          label="Total judged (all types)"
          value={report?.judged_count ?? 0}
        />
      </div>

      <AdminPanel style={{ overflow: "hidden", marginBottom: 18 }}>
        <div style={panelHeaderStyle}>Means per day</div>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Date</th>
              <th style={thStyle}>Type</th>
              <th style={thStyle}>Judged</th>
              <th style={thStyle}>Acc</th>
              <th style={thStyle}>Rel</th>
              <th style={thStyle}>Help</th>
              <th style={thStyle}>Corr</th>
              <th style={thStyle}>Faith</th>
            </tr>
          </thead>
          <tbody>
            {series.map((point) => (
              <tr key={`${point.date}-${point.target_type}`}>
                <td style={tdStyle}>{point.date}</td>
                <td style={tdStyle}>{point.target_type}</td>
                <td style={tdStyle}>{point.judged_count}</td>
                <td style={tdStyle}>{fmtScore(point.mean_accuracy)}</td>
                <td style={tdStyle}>{fmtScore(point.mean_relevance)}</td>
                <td style={tdStyle}>{fmtScore(point.mean_helpfulness)}</td>
                <td style={tdStyle}>{fmtScore(point.mean_correctness)}</td>
                <td style={tdStyle}>{fmtScore(point.mean_faithfulness)}</td>
              </tr>
            ))}
            {series.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={8}>
                  {qualityQuery.isLoading
                    ? "Loading…"
                    : "No judged outputs in this window."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>

      <AdminPanel style={{ overflow: "hidden" }}>
        <div style={panelHeaderStyle}>
          Needs review — judged below 6 on any axis
        </div>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Type</th>
              <th style={thStyle}>Acc</th>
              <th style={thStyle}>Rel</th>
              <th style={thStyle}>Help</th>
              <th style={thStyle}>Corr</th>
              <th style={thStyle}>Faith</th>
              <th style={thStyle}>Rationale</th>
              <th style={thStyle}>Trace</th>
              <th style={thStyle}>Created</th>
              <th style={thStyle}>Review</th>
            </tr>
          </thead>
          <tbody>
            {worst.map((row) => (
              <tr key={row.id}>
                <td style={tdStyle}>{row.target_type}</td>
                <td style={tdStyle}>{fmtScore(row.accuracy)}</td>
                <td style={tdStyle}>{fmtScore(row.relevance)}</td>
                <td style={tdStyle}>{fmtScore(row.helpfulness)}</td>
                <td style={tdStyle}>{fmtScore(row.correctness)}</td>
                <td style={tdStyle}>{fmtScore(row.faithfulness)}</td>
                <td style={tdStyle}>
                  <span style={rationaleStyle}>{row.rationale ?? "—"}</span>
                </td>
                <td style={tdStyle}>
                  <span style={traceStyle}>{row.trace_id ?? "—"}</span>
                </td>
                <td style={tdStyle}>{formatAdminDateTime(row.created_at)}</td>
                <td style={tdStyle}>
                  <Link href={reviewHref(row)} style={reviewLinkStyle}>
                    Review
                  </Link>
                </td>
              </tr>
            ))}
            {worst.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={10}>
                  {qualityQuery.isLoading
                    ? "Loading…"
                    : "No low-scoring outputs in this window."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>
    </AdminLayout>
  );
}

function fmtScore(value: number | null | undefined) {
  if (value == null) return "—";
  return value.toFixed(1);
}

// Map a judged target to its row in the feedback analytics page and deep-link it.
//   feedback    -> activity_feedback   (ACTIVITY_FEEDBACK)
//   mentor_note -> session_scorecards  (COACH_NOTE)
function reviewHref(row: { target_type: string; target_id: string | null }) {
  const base = "/admin/feedback-analytics";
  const feedbackType =
    row.target_type === "mentor_note"
      ? "COACH_NOTE"
      : row.target_type === "feedback"
        ? "ACTIVITY_FEEDBACK"
        : null;
  if (!feedbackType || !row.target_id) return base;
  return `${base}?feedback_type=${feedbackType}&feedback_id=${encodeURIComponent(
    row.target_id,
  )}`;
}

const panelHeaderStyle: CSSProperties = {
  padding: "14px 16px",
  fontSize: 13,
  fontWeight: 800,
  color: "oklch(34% 0.06 245)",
  borderBottom: "1px solid oklch(93% 0.01 245)",
};

const rationaleStyle: CSSProperties = {
  display: "block",
  maxWidth: 360,
  fontSize: 13,
};

const traceStyle: CSSProperties = {
  fontSize: 12,
  fontFamily: "monospace",
  color: "oklch(48% 0.045 245)",
};

const reviewLinkStyle: CSSProperties = {
  minHeight: 32,
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  borderRadius: 8,
  padding: "0 12px",
  background: "#0070C4",
  color: "white",
  textDecoration: "none",
  fontSize: 13,
  fontWeight: 800,
};
