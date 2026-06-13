"use client";

// Conditional bottom region for the legal pages (Terms / Privacy). The chrome
// adapts to how the visitor arrived:
//   1. From signup (?from=signup) → a quiet "Back to the signup page" link.
//   2. Logged-in (via footer/navbar) → nothing; content only.
//   3. Anonymous, not from signup → the marketing "Get started" CTA.
// Lives in its own client component because it reads the query param and auth
// state, while LegalPage stays a Server Component so each page keeps `metadata`.

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";

import { ACCENT_HUE, DotGrid } from "@/components/blog/BlogVisuals";
import { useAuthStore } from "@/store/authStore";

export function LegalFooterCTA() {
  const fromSignup = useSearchParams().get("from") === "signup";
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const hydrated = useAuthStore((s) => s._hydrated);

  // State 1 — mid-signup. Auth-independent, so checked first.
  if (fromSignup) {
    return (
      <section style={{ padding: "0 40px 90px" }}>
        <div style={{ maxWidth: 880, margin: "0 auto" }}>
          <style>{BACK_LINK_STYLES}</style>
          <Link href="/register" className="legal-back">
            <ArrowLeft size={16} aria-hidden />
            Back to the signup page
          </Link>
        </div>
      </section>
    );
  }

  // Wait for localStorage to be read before deciding, so the State-3 CTA never
  // flashes for a logged-in user.
  if (!hydrated) return null;

  // State 2 — logged in. Content only.
  if (isAuthenticated) return null;

  // State 3 — anonymous visitor.
  return (
    <section style={{ padding: "0 40px 110px" }}>
      <style>{CTA_STYLES}</style>
      <div
        style={{
          maxWidth: 1080,
          margin: "0 auto",
          borderRadius: 28,
          padding: "64px 40px",
          textAlign: "center",
          background: `linear-gradient(135deg, oklch(35% 0.15 ${ACCENT_HUE}), oklch(25% 0.1 ${ACCENT_HUE}))`,
          color: "white",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <DotGrid opacity={0.16} />
        <div style={{ position: "relative" }}>
          <h2
            style={{
              fontSize: "clamp(28px, 3.5vw, 40px)",
              fontWeight: 800,
              margin: "0 0 28px",
              letterSpacing: "-0.5px",
            }}
          >
            Ready to improve your English communication with Lingos AI and get
            started
          </h2>
          <Link
            href="/register"
            className="legal-cta-btn"
            style={{
              display: "inline-block",
              padding: "15px 38px",
              borderRadius: 50,
              background: "white",
              color: "oklch(25% 0.1 240)",
              fontSize: 16,
              fontWeight: 700,
              textDecoration: "none",
              boxShadow: "0 8px 24px rgba(20,50,120,0.2)",
            }}
          >
            Get started
          </Link>
        </div>
      </div>
    </section>
  );
}

const BACK_LINK_STYLES = `
  .legal-back {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 8px 16px 8px 13px;
    border-radius: 50px;
    background: rgba(255,255,255,0.6);
    border: 1.5px solid rgba(255,255,255,0.88);
    box-shadow: 0 2px 14px rgba(100,140,210,0.12);
    color: oklch(35% 0.12 ${ACCENT_HUE});
    font-size: 13.5px;
    font-weight: 700;
    text-decoration: none;
    transition: transform .15s ease, box-shadow .15s ease;
  }
  .legal-back:hover { transform: translateX(-2px); box-shadow: 0 6px 20px rgba(80,120,200,0.18); }
`;

const CTA_STYLES = `
  .legal-cta-btn { transition: transform .15s ease, box-shadow .15s ease; }
  .legal-cta-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(0,0,0,0.18); }
`;
