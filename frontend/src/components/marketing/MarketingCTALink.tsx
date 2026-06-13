"use client";

import Link from "next/link";
import type { CSSProperties } from "react";

import { useMarketingCTA } from "@/hooks/useMarketingCTA";

/**
 * Auth-aware CTA link for the marketing/info pages. A small client island so it
 * can be dropped into Server Components (blog, contact) without making the whole
 * page client-rendered.
 *
 * Anonymous visitors see `anonLabel` → `anonHref` (defaults to the sign-up
 * page); logged-in visitors see "Go to Dashboard" → /dashboard. See
 * useMarketingCTA for the (hydration-guarded) decision.
 */
export function MarketingCTALink({
  anonLabel,
  anonHref = "/register",
  className,
  style,
}: {
  anonLabel: string;
  anonHref?: string;
  className?: string;
  style?: CSSProperties;
}) {
  const { isAuthed, ctaLabel, ctaHref } = useMarketingCTA();
  return (
    <Link
      href={isAuthed ? ctaHref : anonHref}
      className={className}
      style={style}
    >
      {isAuthed ? ctaLabel : anonLabel}
    </Link>
  );
}
