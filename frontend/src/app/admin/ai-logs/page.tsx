"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import { useQuery } from "@tanstack/react-query";
import { Eye } from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import {
  AdminPanel,
  formatAdminDateTime,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import { adminApi, type AIRequestLog } from "@/lib/admin-api";

export default function AdminAILogsPage() {
  const logsQuery = useQuery({
    queryKey: ["admin", "ai-logs"],
    queryFn: adminApi.aiLogs,
  });
  const logs = logsQuery.data ?? [];

  return (
    <AdminLayout title="AI Logs" eyebrow="Model operations">
      <AdminPanel style={{ overflow: "hidden" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Agent</th>
              <th style={thStyle}>User</th>
              <th style={thStyle}>Model</th>
              <th style={thStyle}>Tokens</th>
              <th style={thStyle}>Latency</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Error</th>
              <th style={thStyle}>Created</th>
              <th style={thStyle}>Trace</th>
              <th style={thStyle}>Detail</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td style={tdStyle}>{log.agent_name}</td>
                <td style={tdStyle}>
                  <UserCell log={log} />
                </td>
                <td style={tdStyle}>{log.model}</td>
                <td style={tdStyle}>{tokenUsage(log)}</td>
                <td style={tdStyle}>{log.latency_ms == null ? "—" : `${log.latency_ms} ms`}</td>
                <td style={tdStyle}>
                  <StatusBadge status={log.status} />
                </td>
                <td style={tdStyle}>
                  <span style={errorTextStyle}>{log.error_message ?? "—"}</span>
                </td>
                <td style={tdStyle}>{formatAdminDateTime(log.created_at)}</td>
                <td style={tdStyle}>{log.trace_id ?? "—"}</td>
                <td style={tdStyle}>
                  <Link href={`/admin/ai-logs/${log.id}`} style={detailLinkStyle}>
                    <Eye size={15} />
                    View
                  </Link>
                </td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={10}>
                  No AI logs found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>
    </AdminLayout>
  );
}

function UserCell({ log }: { log: AIRequestLog }) {
  if (!log.user) return <span style={mutedTextStyle}>System</span>;
  return (
    <div>
      <div style={strongTextStyle}>{log.user.name}</div>
      <div style={mutedTextStyle}>{log.user.email}</div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const ok = status === "success";
  return (
    <span
      style={{
        ...badgeStyle,
        background: ok ? "oklch(94% 0.06 155)" : "oklch(95% 0.04 25)",
        color: ok ? "oklch(34% 0.13 155)" : "oklch(42% 0.16 25)",
      }}
    >
      {status}
    </span>
  );
}

function tokenUsage(log: AIRequestLog) {
  if (log.input_tokens == null && log.output_tokens == null) return "—";
  return `${log.input_tokens ?? 0} in / ${log.output_tokens ?? 0} out`;
}

const strongTextStyle: CSSProperties = {
  color: "oklch(18% 0.055 245)",
  fontWeight: 800,
};

const mutedTextStyle: CSSProperties = {
  color: "oklch(48% 0.045 245)",
  fontSize: 12,
  fontWeight: 650,
};

const errorTextStyle: CSSProperties = {
  display: "block",
  maxWidth: 280,
  overflow: "hidden",
  textOverflow: "ellipsis",
  whiteSpace: "nowrap",
};

const badgeStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  minHeight: 26,
  borderRadius: 999,
  padding: "0 10px",
  fontSize: 12,
  fontWeight: 800,
  textTransform: "capitalize",
};

const detailLinkStyle: CSSProperties = {
  minHeight: 36,
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 8,
  borderRadius: 8,
  padding: "0 12px",
  background: "#0070C4",
  color: "white",
  textDecoration: "none",
  fontSize: 13,
  fontWeight: 800,
};
