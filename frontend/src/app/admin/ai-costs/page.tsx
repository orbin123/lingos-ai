"use client";

import type { CSSProperties } from "react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { AdminLayout } from "@/components/admin/AdminLayout";
import {
  AdminPanel,
  MetricCard,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import { adminApi } from "@/lib/admin-api";

const WINDOWS = [7, 30, 90] as const;

export default function AdminAICostsPage() {
  const [days, setDays] = useState<number>(30);

  const costQuery = useQuery({
    queryKey: ["admin", "ai-costs", days],
    queryFn: () => adminApi.aiCosts(days),
  });

  const report = costQuery.data;
  const byCapability = report?.by_capability ?? [];
  const byModel = report?.by_model ?? [];
  const daily = report?.daily ?? [];

  return (
    <AdminLayout
      title="AI Costs"
      eyebrow={`Derived from ai_request_logs · last ${days} days`}
      actions={
        <div style={{ display: "flex", gap: 6 }}>
          {WINDOWS.map((w) => (
            <button
              key={w}
              type="button"
              onClick={() => setDays(w)}
              style={dayButtonStyle(w === days)}
            >
              {w}d
            </button>
          ))}
        </div>
      }
    >
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
          gap: 14,
          marginBottom: 18,
        }}
      >
        <MetricCard label="Total cost (USD)" value={fmtUsd(report?.total_cost_usd)} />
        <MetricCard label="Requests" value={fmtNum(report?.total_requests)} />
        <MetricCard
          label="Tokens (in / out)"
          value={`${fmtNum(report?.total_input_tokens)} / ${fmtNum(
            report?.total_output_tokens,
          )}`}
        />
        <MetricCard label="Unpriced requests" value={fmtNum(report?.unpriced_requests)} />
      </div>

      <AdminPanel style={{ overflow: "hidden", marginBottom: 18 }}>
        <div style={panelHeaderStyle}>Cost by capability (agent)</div>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Agent</th>
              <th style={thStyle}>Requests</th>
              <th style={thStyle}>Errors</th>
              <th style={thStyle}>Input tokens</th>
              <th style={thStyle}>Output tokens</th>
              <th style={thStyle}>Cost (USD)</th>
            </tr>
          </thead>
          <tbody>
            {byCapability.map((row) => (
              <tr key={row.agent_name}>
                <td style={tdStyle}>{row.agent_name}</td>
                <td style={tdStyle}>{fmtNum(row.requests)}</td>
                <td style={tdStyle}>{fmtNum(row.errors)}</td>
                <td style={tdStyle}>{fmtNum(row.input_tokens)}</td>
                <td style={tdStyle}>{fmtNum(row.output_tokens)}</td>
                <td style={tdStyle}>{fmtUsd(row.cost_usd)}</td>
              </tr>
            ))}
            {byCapability.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={6}>
                  {costQuery.isLoading ? "Loading…" : "No AI requests in this window."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>

      <AdminPanel style={{ overflow: "hidden", marginBottom: 18 }}>
        <div style={panelHeaderStyle}>Cost by model</div>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Model</th>
              <th style={thStyle}>Requests</th>
              <th style={thStyle}>Input tokens</th>
              <th style={thStyle}>Output tokens</th>
              <th style={thStyle}>Cost (USD)</th>
            </tr>
          </thead>
          <tbody>
            {byModel.map((row) => (
              <tr key={row.model}>
                <td style={tdStyle}>{row.model}</td>
                <td style={tdStyle}>{fmtNum(row.requests)}</td>
                <td style={tdStyle}>{fmtNum(row.input_tokens)}</td>
                <td style={tdStyle}>{fmtNum(row.output_tokens)}</td>
                <td style={tdStyle}>
                  {row.cost_usd == null ? (
                    <span style={unpricedStyle}>unpriced</span>
                  ) : (
                    fmtUsd(row.cost_usd)
                  )}
                </td>
              </tr>
            ))}
            {byModel.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={5}>
                  {costQuery.isLoading ? "Loading…" : "No AI requests in this window."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>

      <AdminPanel style={{ overflow: "hidden" }}>
        <div style={panelHeaderStyle}>Daily spend</div>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Date (UTC)</th>
              <th style={thStyle}>Requests</th>
              <th style={thStyle}>Cost (USD)</th>
            </tr>
          </thead>
          <tbody>
            {daily.map((point) => (
              <tr key={point.date}>
                <td style={tdStyle}>{point.date}</td>
                <td style={tdStyle}>{fmtNum(point.requests)}</td>
                <td style={tdStyle}>{fmtUsd(point.cost_usd)}</td>
              </tr>
            ))}
            {daily.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={3}>
                  {costQuery.isLoading ? "Loading…" : "No AI requests in this window."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>

      <p style={noteStyle}>
        Cost is derived from (model, tokens) via the LLM pricing table — non-LLM spend
        (TTS/STT/embeddings) and any model missing from the table is counted under
        “unpriced requests”, not in the totals.
      </p>
    </AdminLayout>
  );
}

function fmtUsd(value: number | null | undefined) {
  if (value == null) return "—";
  return `$${value.toFixed(4)}`;
}

function fmtNum(value: number | null | undefined) {
  if (value == null) return "—";
  return value.toLocaleString();
}

const panelHeaderStyle: CSSProperties = {
  padding: "14px 16px",
  fontSize: 13,
  fontWeight: 800,
  color: "oklch(34% 0.06 245)",
  borderBottom: "1px solid oklch(93% 0.01 245)",
};

const unpricedStyle: CSSProperties = {
  fontSize: 12,
  color: "oklch(55% 0.04 245)",
  fontStyle: "italic",
};

const noteStyle: CSSProperties = {
  marginTop: 14,
  fontSize: 12,
  color: "oklch(50% 0.04 245)",
  maxWidth: 640,
};

function dayButtonStyle(active: boolean): CSSProperties {
  return {
    minHeight: 32,
    borderRadius: 8,
    padding: "0 12px",
    border: "1px solid oklch(88% 0.02 245)",
    background: active ? "#0070C4" : "white",
    color: active ? "white" : "oklch(40% 0.05 245)",
    fontSize: 13,
    fontWeight: 800,
    cursor: "pointer",
  };
}
