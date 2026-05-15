"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import type { CSSProperties } from "react";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import { AdminPanel, formatAdminDateTime } from "@/components/admin/AdminPrimitives";
import { adminApi } from "@/lib/admin-api";

export default function AdminAILogDetailPage() {
  const params = useParams<{ id: string }>();
  const logId = Number(params.id);
  const logQuery = useQuery({
    queryKey: ["admin", "ai-log", logId],
    queryFn: () => adminApi.aiLog(logId),
    enabled: Number.isFinite(logId),
  });
  const log = logQuery.data;

  return (
    <AdminLayout
      title="AI Log Detail"
      eyebrow="Safe debug"
      actions={
        <Link href="/admin/ai-logs" style={backLinkStyle}>
          <ArrowLeft size={16} />
          Back
        </Link>
      }
    >
      <div style={gridStyle}>
        <AdminPanel style={{ padding: 20 }}>
          <h2 style={sectionTitleStyle}>Request</h2>
          <dl style={detailGridStyle}>
            <Detail label="Agent" value={log?.agent_name} />
            <Detail label="Model" value={log?.model} />
            <Detail label="Status" value={log?.status} />
            <Detail label="Trace ID" value={log?.trace_id ?? "—"} />
            <Detail label="Prompt version" value={log?.prompt_version ?? "—"} />
            <Detail label="Created" value={formatAdminDateTime(log?.created_at)} />
          </dl>
        </AdminPanel>

        <AdminPanel style={{ padding: 20 }}>
          <h2 style={sectionTitleStyle}>Usage</h2>
          <dl style={detailGridStyle}>
            <Detail label="Input tokens" value={numberValue(log?.input_tokens)} />
            <Detail label="Output tokens" value={numberValue(log?.output_tokens)} />
            <Detail label="Latency" value={log?.latency_ms == null ? "—" : `${log.latency_ms} ms`} />
            <Detail label="User" value={log?.user ? `${log.user.name} (${log.user.email})` : "System"} />
          </dl>
        </AdminPanel>
      </div>

      <AdminPanel style={{ marginTop: 18, padding: 20 }}>
        <h2 style={sectionTitleStyle}>Error</h2>
        <pre style={preStyle}>{log?.error_message ?? "No error message recorded."}</pre>
      </AdminPanel>
    </AdminLayout>
  );
}

function Detail({ label, value }: { label: string; value: string | number | undefined }) {
  return (
    <div>
      <dt style={labelStyle}>{label}</dt>
      <dd style={valueStyle}>{value ?? "—"}</dd>
    </div>
  );
}

function numberValue(value: number | null | undefined) {
  return value == null ? "—" : value.toLocaleString();
}

const gridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
  gap: 18,
};

const sectionTitleStyle: CSSProperties = {
  margin: "0 0 16px",
  color: "oklch(18% 0.055 245)",
  fontSize: 18,
  fontWeight: 850,
};

const detailGridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
  gap: 14,
  margin: 0,
};

const labelStyle: CSSProperties = {
  color: "oklch(48% 0.045 245)",
  fontSize: 11,
  fontWeight: 850,
  letterSpacing: "0.05em",
  textTransform: "uppercase",
};

const valueStyle: CSSProperties = {
  margin: "5px 0 0",
  color: "oklch(18% 0.055 245)",
  fontSize: 14,
  fontWeight: 700,
  overflowWrap: "anywhere",
};

const preStyle: CSSProperties = {
  minHeight: 120,
  margin: 0,
  padding: 14,
  borderRadius: 8,
  background: "oklch(97% 0.01 245)",
  color: "oklch(25% 0.06 245)",
  whiteSpace: "pre-wrap",
  overflowWrap: "anywhere",
  fontSize: 13,
  lineHeight: 1.5,
};

const backLinkStyle: CSSProperties = {
  minHeight: 38,
  display: "inline-flex",
  alignItems: "center",
  gap: 8,
  borderRadius: 8,
  padding: "0 12px",
  background: "white",
  border: "1px solid oklch(86% 0.018 245)",
  color: "oklch(28% 0.06 245)",
  textDecoration: "none",
  fontSize: 13,
  fontWeight: 800,
};
