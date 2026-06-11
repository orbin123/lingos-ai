"use client";

import { useRouter } from "next/navigation";
import { useAccessState } from "@/hooks/useAccessState";

const TIER_STYLES = {
  info: {
    background: "oklch(96% 0.03 240)",
    border: "1px solid oklch(88% 0.05 240)",
    color: "oklch(35% 0.09 240)",
  },
  warning: {
    background: "oklch(96% 0.05 80)",
    border: "1px solid oklch(85% 0.09 80)",
    color: "oklch(40% 0.12 60)",
  },
  expired: {
    background: "oklch(96% 0.03 25)",
    border: "1px solid oklch(86% 0.07 25)",
    color: "oklch(42% 0.16 25)",
  },
} as const;

/** Trial countdown / expired banner for the dashboard (§10.3 tiers). */
export function TrialBanner() {
  const router = useRouter();
  const { bannerTier, daysRemaining, accessState } = useAccessState();

  if (bannerTier === "none") return null;

  const style = TIER_STYLES[bannerTier];
  const message =
    bannerTier === "expired"
      ? accessState === "cancelled"
        ? "Your subscription is cancelled. Resubscribe to keep learning."
        : "Your free trial has ended. Upgrade to keep learning."
      : daysRemaining === 1
        ? "1 day left on your free trial."
        : `${daysRemaining} days left on your free trial.`;

  return (
    <div
      role="status"
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 12,
        padding: "12px 16px",
        borderRadius: 12,
        marginBottom: 16,
        fontSize: 14,
        fontWeight: 600,
        ...style,
      }}
    >
      <span>
        {message}
        {bannerTier === "warning" && " Don't lose your progress."}
      </span>
      <button
        onClick={() => router.push("/pricing")}
        style={{
          flexShrink: 0,
          border: "none",
          borderRadius: 8,
          padding: "8px 14px",
          fontSize: 13,
          fontWeight: 700,
          cursor: "pointer",
          color: "white",
          background:
            bannerTier === "expired"
              ? "oklch(50% 0.18 25)"
              : "oklch(48% 0.17 240)",
        }}
      >
        {bannerTier === "expired" ? "Upgrade now" : "Upgrade"}
      </button>
    </div>
  );
}
