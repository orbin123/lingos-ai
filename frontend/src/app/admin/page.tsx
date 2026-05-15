"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight } from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import {
  AdminPanel,
  MetricCard,
  RolePill,
  StatusPill,
  formatAdminDate,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import { adminApi } from "@/lib/admin-api";

export default function AdminDashboardPage() {
  const summaryQuery = useQuery({
    queryKey: ["admin", "summary"],
    queryFn: adminApi.summary,
  });

  const summary = summaryQuery.data;

  return (
    <AdminLayout title="Dashboard" eyebrow="Production admin">
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 14 }}>
        <MetricCard label="Total users" value={summary?.total_users ?? "—"} />
        <MetricCard label="Active users" value={summary?.active_users ?? "—"} />
        <MetricCard label="Tasks completed" value={summary?.tasks_completed ?? "—"} />
        <MetricCard label="Feedback generated" value={summary?.feedback_generated ?? "—"} />
        <MetricCard label="AI requests 24h" value={summary?.ai_requests_24h ?? "—"} />
        <MetricCard label="AI errors 24h" value={summary?.ai_errors_24h ?? "—"} />
        <MetricCard
          label="Pending feedback"
          value={summary?.pending_feedback_reviews ?? "—"}
        />
      </div>

      <AdminPanel style={{ marginTop: 18, overflow: "hidden" }}>
        <div style={panelHeadStyle}>
          <div>
            <h2 style={sectionTitleStyle}>Recent users</h2>
            <p style={sectionSubStyle}>Newest accounts across learner and admin roles.</p>
          </div>
          <Link href="/admin/users" style={linkButtonStyle}>
            View users
            <ArrowRight size={16} />
          </Link>
        </div>

        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Name</th>
              <th style={thStyle}>Email</th>
              <th style={thStyle}>Role</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Created</th>
            </tr>
          </thead>
          <tbody>
            {(summary?.recent_users ?? []).map((user) => (
              <tr key={user.id}>
                <td style={tdStyle}>{user.name}</td>
                <td style={tdStyle}>{user.email}</td>
                <td style={tdStyle}>
                  <RolePill role={user.role} />
                </td>
                <td style={tdStyle}>
                  <StatusPill active={user.is_active} />
                </td>
                <td style={tdStyle}>{formatAdminDate(user.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </AdminPanel>
    </AdminLayout>
  );
}

const panelHeadStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 16,
  padding: "18px 18px 12px",
};

const sectionTitleStyle: CSSProperties = {
  margin: 0,
  color: "oklch(18% 0.055 245)",
  fontSize: 18,
  fontWeight: 850,
};

const sectionSubStyle: CSSProperties = {
  margin: "4px 0 0",
  color: "oklch(48% 0.045 245)",
  fontSize: 13,
  fontWeight: 600,
};

const linkButtonStyle: CSSProperties = {
  minHeight: 38,
  display: "inline-flex",
  alignItems: "center",
  gap: 8,
  borderRadius: 8,
  padding: "0 12px",
  background: "#0070C4",
  color: "white",
  textDecoration: "none",
  fontSize: 13,
  fontWeight: 800,
};
