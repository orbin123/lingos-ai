"use client";

import { useAuthStore } from "@/store/authStore";

/**
 * useMarketingCTA
 *
 * Single source of truth for auth-aware navigation on the public/marketing
 * pages (landing, features, how-it-works, about, contact, blog, legal). The
 * shared LandingNavbar/LandingFooter and each page's in-body CTA consume this
 * so a logged-in visitor never sees the first-time "Start Learning Free"
 * chrome.
 *
 * Gated on `_hydrated` (the localStorage read) so the logged-out version
 * renders during SSR/first paint — the logged-in CTA never flickers in for a
 * split second. Same guard pattern as useRedirectIfAuthed / LegalFooterCTA.
 */
export interface MarketingCTA {
  /** True only once hydration has run AND the user is authenticated. */
  isAuthed: boolean;
  /** Where the logo should point: dashboard when logged in, else home. */
  homeHref: string;
  /** Primary CTA label. */
  ctaLabel: string;
  /** Primary CTA destination. */
  ctaHref: string;
}

export function useMarketingCTA(): MarketingCTA {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const hydrated = useAuthStore((s) => s._hydrated);
  const isAuthed = hydrated && isAuthenticated;

  return {
    isAuthed,
    homeHref: isAuthed ? "/dashboard" : "/",
    ctaLabel: isAuthed ? "Go to Dashboard" : "Start Learning Free",
    ctaHref: isAuthed ? "/dashboard" : "/register",
  };
}
