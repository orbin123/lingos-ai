"use client";

import Link from "next/link";

import { useMarketingCTA } from "@/hooks/useMarketingCTA";

const FOOTER_COLUMNS = [
  {
    title: "Product",
    links: [
      { label: "Features", href: "/#features" },
      { label: "How it works", href: "/#how-it-works" },
      { label: "Pricing", href: "/pricing" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About", href: "/about" },
      { label: "Blog", href: "/blog" },
      { label: "Contact", href: "/contact" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy", href: "/privacy" },
      { label: "Terms", href: "/terms" },
    ],
  },
] as const;

export function LandingFooter() {
  const { homeHref } = useMarketingCTA();
  return (
    <footer
      className="mkt-section"
      style={{
        padding: "56px 40px 40px",
        background: "oklch(18% 0.09 245)",
        color: "rgba(255,255,255,0.55)",
      }}
    >
      <div
        className="mkt-footer-grid"
        style={{
          maxWidth: 1180,
          margin: "0 auto",
          display: "grid",
          gridTemplateColumns: "minmax(220px, 1.4fr) repeat(3, minmax(120px, 1fr))",
          gap: 32,
        }}
      >
        <div>
          <Link
            href={homeHref}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              textDecoration: "none",
            }}
          >
            <img
              src="/lingos-logo2.png"
              alt="LingosAI Logo"
              style={{ height: 36, width: "auto", borderRadius: 6 }}
            />
            <span
              style={{
                fontWeight: 700,
                fontSize: 15,
                color: "rgba(255,255,255,0.85)",
              }}
            >
              LingosAI
            </span>
          </Link>
          <p
            style={{
              maxWidth: 280,
              margin: "16px 0 0",
              fontSize: 13,
              lineHeight: 1.7,
              color: "rgba(255,255,255,0.5)",
            }}
          >
            Personal English practice shaped by diagnosis, daily tasks, and precise
            feedback.
          </p>
        </div>

        {FOOTER_COLUMNS.map((column) => (
          <div key={column.title}>
            <h3
              style={{
                margin: "0 0 14px",
                color: "rgba(255,255,255,0.84)",
                fontSize: 13,
                fontWeight: 700,
              }}
            >
              {column.title}
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {column.links.map((link) => (
                <Link
                  key={link.label}
                  href={link.href}
                  style={{
                    color: "rgba(255,255,255,0.5)",
                    fontSize: 13,
                    textDecoration: "none",
                  }}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div
        style={{
          maxWidth: 1180,
          margin: "36px auto 0",
          paddingTop: 24,
          borderTop: "1px solid rgba(255,255,255,0.12)",
          fontSize: 13,
        }}
      >
        © 2026 LingosAI. All rights reserved.
      </div>
    </footer>
  );
}
