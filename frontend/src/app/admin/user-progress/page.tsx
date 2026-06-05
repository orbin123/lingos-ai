"use client";

import type { CSSProperties } from "react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ChevronDown, ChevronRight } from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import {
  AdminPanel,
  formatAdminDate,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import { adminApi, type UserProgressItem } from "@/lib/admin-api";

export default function AdminUserProgressPage() {
  const progressQuery = useQuery({
    queryKey: ["admin", "user-progress"],
    queryFn: adminApi.userProgress,
  });

  const rows = progressQuery.data ?? [];

  return (
    <AdminLayout
      title="User Progress"
      eyebrow="Learning operations"
    >
      <AdminPanel style={{ overflow: "hidden" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>User</th>
              <th style={thStyle}>Course</th>
              <th style={thStyle}>Purchase</th>
              <th style={thStyle}>Activities done</th>
              <th style={thStyle}>How they&apos;re doing</th>
              <th style={thStyle}>Access until</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <ProgressRow key={row.user_id} row={row} />
            ))}
            {rows.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={6}>
                  {progressQuery.isLoading ? "Loading…" : "No users found."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>
    </AdminLayout>
  );
}

function ProgressRow({ row }: { row: UserProgressItem }) {
  const [open, setOpen] = useState(false);
  const hasSkills = row.subskill_scores.length > 0;

  return (
    <>
      <tr>
        <td style={tdStyle}>
          <div style={strongTextStyle}>{row.name}</div>
          <div style={mutedTextStyle}>{row.email}</div>
        </td>
        <td style={tdStyle}>
          {row.plan_name ? (
            <span>{row.plan_name}</span>
          ) : (
            <span style={mutedTextStyle}>No course</span>
          )}
        </td>
        <td style={tdStyle}>
          <PurchaseBadge complete={row.purchase_complete} hasPlan={!!row.plan_id} />
        </td>
        <td style={tdStyle}>
          <span style={strongTextStyle}>{row.activities_completed}</span>
        </td>
        <td style={tdStyle}>
          <ScoreCell score={row.dashboard_score} />
          {hasSkills && (
            <button
              type="button"
              onClick={() => setOpen((v) => !v)}
              style={expandStyle}
            >
              {open ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
              {open ? "Hide" : "Per skill"}
            </button>
          )}
        </td>
        <td style={tdStyle}>{formatAdminDate(row.access_expires_at)}</td>
      </tr>
      {open && hasSkills && (
        <tr>
          <td style={{ ...tdStyle, background: "oklch(98% 0.006 245)" }} colSpan={6}>
            <div style={skillGridStyle}>
              {row.subskill_scores.map((skill) => (
                <div key={skill.skill_id} style={skillChipStyle}>
                  <span style={skillNameStyle}>{skill.skill_name}</span>
                  <span style={skillScoreStyle}>{skill.score.toFixed(1)}/10</span>
                </div>
              ))}
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

function ScoreCell({ score }: { score: number | null }) {
  if (score === null) return <span style={mutedTextStyle}>Not scored yet</span>;
  const hue = score >= 7 ? 145 : score >= 4 ? 80 : 25;
  return (
    <span
      style={{
        fontWeight: 800,
        color: `oklch(45% 0.14 ${hue})`,
      }}
    >
      {score.toFixed(1)}
      <span style={{ fontWeight: 600, color: "oklch(55% 0.04 245)" }}>/10</span>
    </span>
  );
}

function PurchaseBadge({
  complete,
  hasPlan,
}: {
  complete: boolean;
  hasPlan: boolean;
}) {
  if (!hasPlan) {
    return <span style={{ ...pillStyle, ...pillMutedStyle }}>None</span>;
  }
  return complete ? (
    <span style={{ ...pillStyle, ...pillOkStyle }}>Complete</span>
  ) : (
    <span style={{ ...pillStyle, ...pillWarnStyle }}>Incomplete</span>
  );
}

const strongTextStyle: CSSProperties = {
  color: "oklch(18% 0.055 245)",
  fontWeight: 800,
};

const mutedTextStyle: CSSProperties = {
  marginTop: 3,
  color: "oklch(48% 0.045 245)",
  fontSize: 12,
  fontWeight: 650,
};

const expandStyle: CSSProperties = {
  marginTop: 6,
  display: "inline-flex",
  alignItems: "center",
  gap: 4,
  border: "none",
  background: "none",
  color: "#0070C4",
  cursor: "pointer",
  fontFamily: "inherit",
  fontSize: 12,
  fontWeight: 750,
  padding: 0,
};

const skillGridStyle: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: 8,
};

const skillChipStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  padding: "6px 12px",
  borderRadius: 999,
  border: "1px solid oklch(90% 0.014 245)",
  background: "white",
};

const skillNameStyle: CSSProperties = {
  fontSize: 12.5,
  fontWeight: 700,
  color: "oklch(30% 0.05 245)",
};

const skillScoreStyle: CSSProperties = {
  fontSize: 12.5,
  fontWeight: 800,
  color: "oklch(40% 0.1 245)",
};

const pillStyle: CSSProperties = {
  display: "inline-block",
  padding: "3px 10px",
  borderRadius: 999,
  fontSize: 12,
  fontWeight: 750,
};

const pillOkStyle: CSSProperties = {
  background: "oklch(94% 0.06 150)",
  color: "oklch(40% 0.12 150)",
};

const pillWarnStyle: CSSProperties = {
  background: "oklch(95% 0.07 80)",
  color: "oklch(45% 0.12 70)",
};

const pillMutedStyle: CSSProperties = {
  background: "oklch(94% 0.01 245)",
  color: "oklch(50% 0.03 245)",
};
