"use client";

import type { CSSProperties, ReactNode } from "react";

export function AdminPanel({
  children,
  style,
}: {
  children: ReactNode;
  style?: CSSProperties;
}) {
  return <section style={{ ...panelStyle, ...style }}>{children}</section>;
}

export function MetricCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div style={metricStyle}>
      <div style={metricLabelStyle}>{label}</div>
      <div style={metricValueStyle}>{value}</div>
    </div>
  );
}

export function StatusPill({ active }: { active: boolean }) {
  return (
    <span
      style={{
        ...pillStyle,
        background: active ? "oklch(94% 0.06 155)" : "oklch(95% 0.035 30)",
        color: active ? "oklch(34% 0.13 155)" : "oklch(42% 0.14 30)",
      }}
    >
      {active ? "Active" : "Inactive"}
    </span>
  );
}

export function RolePill({ role }: { role: string }) {
  return (
    <span style={{ ...pillStyle, background: "oklch(94% 0.04 240)", color: "#00599e" }}>
      {role.replace("_", " ")}
    </span>
  );
}

export function TemplateStatusPill({ status }: { status: string }) {
  const archived = status === "archived";
  const active = status === "active";
  return (
    <span
      style={{
        ...pillStyle,
        background: active
          ? "oklch(94% 0.06 155)"
          : archived
            ? "oklch(94% 0.015 245)"
            : "oklch(96% 0.05 80)",
        color: active
          ? "oklch(34% 0.13 155)"
          : archived
            ? "oklch(42% 0.035 245)"
            : "oklch(42% 0.12 70)",
      }}
    >
      {status}
    </span>
  );
}

export function AdminButton({
  children,
  onClick,
  type = "button",
  tone = "primary",
  disabled,
}: {
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  tone?: "primary" | "secondary" | "danger";
  disabled?: boolean;
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      style={{
        ...buttonStyle,
        ...(tone === "primary"
          ? primaryButtonStyle
          : tone === "danger"
            ? dangerButtonStyle
            : secondaryButtonStyle),
        opacity: disabled ? 0.6 : 1,
        cursor: disabled ? "not-allowed" : "pointer",
      }}
    >
      {children}
    </button>
  );
}

export function formatAdminDate(value: string | null | undefined) {
  if (!value) return "Not recorded";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

export function formatAdminDateTime(value: string | null | undefined) {
  if (!value) return "Not recorded";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export const tableStyle: CSSProperties = {
  width: "100%",
  borderCollapse: "separate",
  borderSpacing: 0,
  fontSize: 14,
};

export const thStyle: CSSProperties = {
  padding: "12px 14px",
  textAlign: "left",
  color: "oklch(46% 0.045 245)",
  fontSize: 12,
  fontWeight: 800,
  letterSpacing: "0.04em",
  textTransform: "uppercase",
  borderBottom: "1px solid oklch(90% 0.014 245)",
};

export const tdStyle: CSSProperties = {
  padding: "14px",
  borderBottom: "1px solid oklch(93% 0.01 245)",
  verticalAlign: "middle",
};

const panelStyle: CSSProperties = {
  background: "white",
  border: "1px solid oklch(88% 0.018 245)",
  borderRadius: 8,
  boxShadow: "0 10px 28px rgba(30,55,90,0.05)",
};

const metricStyle: CSSProperties = {
  background: "white",
  border: "1px solid oklch(88% 0.018 245)",
  borderRadius: 8,
  padding: 18,
  minHeight: 112,
};

const metricLabelStyle: CSSProperties = {
  color: "oklch(48% 0.045 245)",
  fontSize: 12,
  fontWeight: 800,
  letterSpacing: "0.05em",
  textTransform: "uppercase",
};

const metricValueStyle: CSSProperties = {
  marginTop: 12,
  color: "oklch(18% 0.055 245)",
  fontSize: 34,
  fontWeight: 850,
  lineHeight: 1,
};

const pillStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  minHeight: 26,
  borderRadius: 999,
  padding: "0 10px",
  fontSize: 12,
  fontWeight: 800,
  textTransform: "capitalize",
  whiteSpace: "nowrap",
};

const buttonStyle: CSSProperties = {
  minHeight: 38,
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 8,
  borderRadius: 8,
  padding: "0 13px",
  fontFamily: "inherit",
  fontSize: 13,
  fontWeight: 800,
  border: "1px solid transparent",
};

const primaryButtonStyle: CSSProperties = {
  background: "#0070C4",
  color: "white",
};

const secondaryButtonStyle: CSSProperties = {
  background: "white",
  color: "oklch(28% 0.06 245)",
  borderColor: "oklch(86% 0.018 245)",
};

const dangerButtonStyle: CSSProperties = {
  background: "oklch(95% 0.04 25)",
  color: "oklch(42% 0.16 25)",
  borderColor: "oklch(88% 0.05 25)",
};
