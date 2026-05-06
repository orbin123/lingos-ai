"use client";

import Link from "next/link";

export function LandingFooter() {
  return (
    <footer
      style={{
        padding: "48px 40px",
        background: "oklch(18% 0.09 245)",
        color: "rgba(255,255,255,0.55)",
      }}
    >
      <div
        style={{
          maxWidth: 1180,
          margin: "0 auto",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 20,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <img
            src="/lingosai_logo.png"
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
        </div>
        <div style={{ display: "flex", gap: 28, fontSize: 13 }}>
          {["Privacy", "Terms", "Contact", "Blog"].map((l) => (
            <a
              key={l}
              href="#"
              style={{ color: "rgba(255,255,255,0.5)", textDecoration: "none" }}
            >
              {l}
            </a>
          ))}
        </div>
        <div style={{ fontSize: 13 }}>© 2026 LingosAI. All rights reserved.</div>
      </div>
    </footer>
  );
}
