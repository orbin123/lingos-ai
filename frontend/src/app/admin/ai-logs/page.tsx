"use client";

import Link from "next/link";
import { useState } from "react";
import type { CSSProperties } from "react";
import { useQuery } from "@tanstack/react-query";
import { Check, Copy, Eye, X } from "lucide-react";

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
  const [selectedError, setSelectedError] = useState<string | null>(null);

  return (
    <AdminLayout title="AI Logs" eyebrow="Model operations">
      <AdminPanel style={{ overflow: "hidden" }}>
        <div style={{ overflowX: "auto" }}>
          <table style={{ ...tableStyle, minWidth: 1100 }}>
            <thead>
              <tr>
                <th style={thStyle}>Agent</th>
                <th style={thStyle}>User</th>
                <th style={thStyle}>Model</th>
                <th style={thStyle}>Tokens</th>
                <th style={thStyle}>Cost</th>
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
                  <td style={tdStyle}>{formatCost(log.cost_usd)}</td>
                  <td style={tdStyle}>{log.latency_ms == null ? "—" : `${log.latency_ms} ms`}</td>
                  <td style={tdStyle}>
                    <StatusBadge status={log.status} />
                  </td>
                  <td style={tdStyle}>
                    {log.error_message ? (
                      <span
                        style={errorTextStyle}
                        onClick={() => setSelectedError(log.error_message!)}
                        title="Click to view full error"
                      >
                        {log.error_message}
                      </span>
                    ) : (
                      <span style={mutedTextStyle}>—</span>
                    )}
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
                  <td style={tdStyle} colSpan={11}>
                    No AI logs found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </AdminPanel>
      {selectedError && (
        <ErrorModal error={selectedError} onClose={() => setSelectedError(null)} />
      )}
    </AdminLayout>
  );
}

function ErrorModal({ error, onClose }: { error: string; onClose: () => void }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(error);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        <div style={modalHeaderStyle}>
          <span style={modalTitleStyle}>Error Details</span>
          <button style={iconButtonStyle} onClick={onClose} aria-label="Close">
            <X size={16} />
          </button>
        </div>
        <pre style={modalPreStyle}>{error}</pre>
        <div style={modalFooterStyle}>
          <button style={copyButtonStyle} onClick={handleCopy}>
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>
      </div>
    </div>
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

function formatCost(cost: number | null) {
  if (cost == null) return "—";
  return `$${cost.toFixed(4)}`;
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
  maxWidth: 260,
  overflow: "hidden",
  textOverflow: "ellipsis",
  whiteSpace: "nowrap",
  fontStyle: "italic",
  color: "oklch(42% 0.16 25)",
  cursor: "pointer",
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

const overlayStyle: CSSProperties = {
  position: "fixed",
  inset: 0,
  background: "rgba(10, 20, 40, 0.45)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  zIndex: 1000,
};

const modalStyle: CSSProperties = {
  background: "white",
  borderRadius: 10,
  padding: 24,
  maxWidth: 640,
  width: "90%",
  maxHeight: "80vh",
  display: "flex",
  flexDirection: "column",
  gap: 16,
  boxShadow: "0 24px 64px rgba(10,20,60,0.22)",
};

const modalHeaderStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
};

const modalTitleStyle: CSSProperties = {
  fontSize: 15,
  fontWeight: 800,
  color: "oklch(18% 0.055 245)",
};

const modalPreStyle: CSSProperties = {
  background: "oklch(97% 0.008 245)",
  border: "1px solid oklch(88% 0.018 245)",
  borderRadius: 6,
  padding: "14px 16px",
  fontSize: 13,
  fontFamily: "ui-monospace, 'Cascadia Code', 'Fira Mono', monospace",
  overflowY: "auto",
  overflowX: "auto",
  maxHeight: "52vh",
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
  margin: 0,
  color: "oklch(32% 0.16 25)",
  lineHeight: 1.6,
};

const modalFooterStyle: CSSProperties = {
  display: "flex",
  justifyContent: "flex-end",
};

const copyButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  padding: "8px 16px",
  borderRadius: 7,
  border: "1px solid oklch(82% 0.02 245)",
  background: "white",
  color: "oklch(30% 0.055 245)",
  fontSize: 13,
  fontWeight: 700,
  cursor: "pointer",
};

const iconButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  width: 32,
  height: 32,
  borderRadius: 6,
  border: "none",
  background: "transparent",
  color: "oklch(48% 0.045 245)",
  cursor: "pointer",
};
