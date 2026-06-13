// Shared layout for the static legal pages (Privacy Policy, Terms of Service).
// No "use client" — pure markup that renders inside React Server Components, so
// each page can still export `metadata`. Visual language copied verbatim from
// the marketing pages (Contact / Blog) so the legal pages feel like the same
// product: shared navbar/footer, GlassCard, DotGrid, Plus Jakarta Sans,
// ACCENT_HUE = 240, pill buttons.

import { Suspense, type ReactNode } from "react";
import { type LucideIcon } from "lucide-react";

import { ACCENT_HUE, GlassCard } from "@/components/blog/BlogVisuals";
import { LegalFooterCTA } from "@/components/legal/LegalFooterCTA";
import { LandingFooter } from "@/components/layout/LandingFooter";
import { LandingNavbar } from "@/components/layout/LandingNavbar";

export type LegalSection = {
  icon: LucideIcon;
  heading: string;
  /** Optional lead paragraph(s). */
  body?: ReactNode;
  /** Optional bullet list rendered under the body. */
  bullets?: ReactNode[];
};

export function LegalPage({
  eyebrow,
  title,
  subtitle,
  lastUpdated,
  sections,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
  lastUpdated: string;
  sections: LegalSection[];
}) {
  return (
    <main
      style={{
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        minHeight: "100svh",
        background: `radial-gradient(circle at top right, oklch(90% 0.05 ${ACCENT_HUE}) 0%, oklch(95% 0.02 ${
          ACCENT_HUE + 10
        }) 40%, #ffffff 100%)`,
        paddingTop: 100,
        color: "oklch(20% 0.05 240)",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />
      <style>{STYLES}</style>
      <LandingNavbar showCTA={false} />

      {/* HERO */}
      <section
        style={{
          position: "relative",
          padding: "70px 40px 40px",
          maxWidth: 920,
          margin: "0 auto",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <span style={eyebrowStyle}>{eyebrow}</span>
          <h1
            style={{
              fontSize: "clamp(36px, 4.5vw, 60px)",
              fontWeight: 800,
              color: "oklch(15% 0.09 245)",
              lineHeight: 1.12,
              letterSpacing: "-1px",
              margin: "18px 0 20px",
            }}
          >
            {title}
          </h1>
          <p
            style={{
              fontSize: 20,
              color: "oklch(40% 0.05 240)",
              lineHeight: 1.6,
              maxWidth: 680,
              margin: "0 auto",
            }}
          >
            {subtitle}
          </p>
          <p
            style={{
              marginTop: 18,
              fontSize: 13.5,
              fontWeight: 600,
              letterSpacing: "0.02em",
              textTransform: "uppercase",
              color: "oklch(55% 0.04 240)",
            }}
          >
            Last updated {lastUpdated}
          </p>
        </div>
      </section>

      {/* CONTENT */}
      <section style={{ padding: "10px 40px 90px" }}>
        <div
          style={{
            maxWidth: 880,
            margin: "0 auto",
            display: "flex",
            flexDirection: "column",
            gap: 20,
          }}
        >
          {sections.map(({ icon: Icon, heading, body, bullets }) => (
            <GlassCard key={heading} style={{ padding: "28px 30px" }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 14,
                  marginBottom: 14,
                }}
              >
                <span style={iconBadgeStyle}>
                  <Icon size={20} aria-hidden />
                </span>
                <h2
                  style={{
                    fontSize: "clamp(19px, 2.2vw, 23px)",
                    fontWeight: 800,
                    color: "oklch(15% 0.09 245)",
                    letterSpacing: "-0.3px",
                    margin: 0,
                  }}
                >
                  {heading}
                </h2>
              </div>
              {body && <div style={bodyStyle}>{body}</div>}
              {bullets && bullets.length > 0 && (
                <ul style={{ margin: "12px 0 0", padding: 0, listStyle: "none" }}>
                  {bullets.map((item, i) => (
                    <li key={i} className="legal-bullet">
                      {item}
                    </li>
                  ))}
                </ul>
              )}
            </GlassCard>
          ))}
        </div>
      </section>

      {/* Conditional bottom region (signup back-link / nothing / marketing CTA) */}
      <Suspense fallback={null}>
        <LegalFooterCTA />
      </Suspense>

      <LandingFooter />
    </main>
  );
}

// ── shared inline styles ────────────────────────────────────────────────────
const eyebrowStyle = {
  display: "inline-block",
  padding: "7px 16px",
  background: `oklch(95% 0.04 ${ACCENT_HUE})`,
  borderRadius: 50,
  color: `oklch(40% 0.14 ${ACCENT_HUE})`,
  fontSize: 13,
  fontWeight: 700,
  letterSpacing: "0.04em",
  textTransform: "uppercase" as const,
};

const iconBadgeStyle = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  width: 44,
  height: 44,
  flexShrink: 0,
  borderRadius: 14,
  background: `oklch(94% 0.05 ${ACCENT_HUE})`,
  color: `oklch(40% 0.14 ${ACCENT_HUE})`,
};

const bodyStyle = {
  fontSize: 15.5,
  lineHeight: 1.7,
  color: "oklch(40% 0.05 240)",
};

const STYLES = `
  .legal-bullet {
    position: relative;
    padding: 4px 0 4px 22px;
    font-size: 15.5px;
    line-height: 1.6;
    color: oklch(40% 0.05 240);
  }
  .legal-bullet::before {
    content: "";
    position: absolute;
    left: 4px;
    top: 13px;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: oklch(55% 0.16 ${ACCENT_HUE});
  }
  .legal-bullet a, .legal-body-link { color: oklch(45% 0.16 ${ACCENT_HUE}); font-weight: 600; text-decoration: none; }
  .legal-bullet a:hover, .legal-body-link:hover { text-decoration: underline; }
`;
