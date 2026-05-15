"use client";

import type { CSSProperties } from "react";

export function maskProviderId(value: string | null | undefined) {
  if (!value) return "Not recorded";
  if (value.includes("...") || value.includes("*")) return value;
  if (value.length <= 8) return "*".repeat(value.length);
  return `${value.slice(0, 4)}...${value.slice(-4)}`;
}

export function BillingStatusBadge({ status }: { status: string }) {
  const normalized = status.toLowerCase();
  const positive = ["paid", "active", "trialing"].includes(normalized);
  const warning = ["past_due", "pending", "paused"].includes(normalized);
  return (
    <span
      style={{
        ...badgeStyle,
        background: positive
          ? "oklch(94% 0.06 155)"
          : warning
            ? "oklch(96% 0.05 80)"
            : "oklch(95% 0.04 25)",
        color: positive
          ? "oklch(34% 0.13 155)"
          : warning
            ? "oklch(42% 0.12 70)"
            : "oklch(42% 0.16 25)",
      }}
    >
      {status.replace("_", " ")}
    </span>
  );
}

const badgeStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  minHeight: 26,
  borderRadius: 999,
  padding: "0 10px",
  fontSize: 12,
  fontWeight: 800,
  textTransform: "capitalize",
  whiteSpace: "nowrap",
};
