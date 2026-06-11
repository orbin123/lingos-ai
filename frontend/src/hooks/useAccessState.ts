"use client";

import { useQuery } from "@tanstack/react-query";
import { authApi } from "@/lib/auth-api";
import type { AccessState } from "@/lib/subscriptions-api";

export type BannerTier = "none" | "info" | "warning" | "expired";

/** Banner urgency from the entitlement: >3 days → info, ≤3 → warning,
 *  expired/cancelled → expired. Everything else shows nothing. */
export function bannerTierFor(
  accessState: AccessState | undefined,
  daysRemaining: number | null | undefined,
): BannerTier {
  if (accessState === "expired" || accessState === "cancelled") return "expired";
  if (accessState !== "trial") return "none";
  if (daysRemaining != null && daysRemaining <= 3) return "warning";
  return "info";
}

/**
 * Entitlement read straight off /auth/me (shared ["me"] query key, so it
 * stays in sync with everything else that reads the user). Backend
 * `days_remaining` is the single source for countdown copy — never
 * recompute it locally.
 */
export function useAccessState() {
  const query = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    staleTime: 30_000,
  });

  const user = query.data;
  const accessState = user?.access_state;
  const daysRemaining = user?.days_remaining ?? null;

  return {
    user,
    accessState,
    daysRemaining,
    trialEndsAt: user?.trial_ends_at ?? null,
    planId: user?.plan_id ?? null,
    bannerTier: bannerTierFor(accessState, daysRemaining),
    isLoading: query.isLoading,
    refetch: query.refetch,
  };
}
