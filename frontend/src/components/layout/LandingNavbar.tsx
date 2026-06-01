"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";

const ACCENT_HUE = 240;

interface LandingNavbarProps {
  variant?: "full" | "minimal";
  onCTAClick?: () => void;
  showCTA?: boolean;
}

export function LandingNavbar({
  variant = "full",
  onCTAClick,
  showCTA = false,
}: LandingNavbarProps) {
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();
  const isMinimal = variant === "minimal";

  useEffect(() => {
    const h = () => setScrolled(window.scrollY > 30);
    window.addEventListener("scroll", h);
    return () => window.removeEventListener("scroll", h);
  }, []);

  return (
    <nav
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        padding: "0 40px",
        transition: "all 0.3s",
        background: scrolled ? "rgba(220,235,250,0.82)" : "transparent",
        backdropFilter: scrolled ? "blur(20px)" : "none",
        borderBottom: scrolled ? "1px solid rgba(255,255,255,0.7)" : "none",
      }}
    >
      <div
        style={{
          maxWidth: 1180,
          margin: "0 auto",
          display: "flex",
          alignItems: "center",
          height: 68,
          gap: 40,
        }}
      >
        <Link
          href="/"
          aria-label="LingosAI home"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            textDecoration: "none",
          }}
        >
          <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
            <img
              src="/lingosai_logo.png"
              alt="LingosAI Logo"
              style={{ height: 50, width: "auto", borderRadius: 8 }}
            />
          </div>
          <span
            style={{
              fontWeight: 700,
              fontSize: 17,
              letterSpacing: "-0.3px",
              color: "oklch(18% 0.09 245)",
            }}
          >
            LingosAI
          </span>
        </Link>
        {!isMinimal && (
        <div style={{ display: "flex", gap: 6, marginLeft: "auto" }}>
          {[
            { label: "Features", href: "/features" },
            { label: "How It Works", href: "/how-it-works" },
            { label: "Pricing", href: "/pricing" },
            { label: "About", href: "/about" },
          ].map((l) => {
            const isActive = pathname === l.href;
            return (
              <Link
                key={l.label}
                href={l.href}
                style={{
                  padding: "7px 16px",
                  borderRadius: 50,
                  fontSize: 14,
                  fontWeight: 500,
                  color: isActive ? `oklch(40% 0.14 ${ACCENT_HUE})` : "oklch(28% 0.08 240)",
                  background: isActive ? "rgba(255,255,255,0.5)" : "transparent",
                  textDecoration: "none",
                  transition: "background 0.15s",
                }}
                onMouseEnter={(e) =>
                  ((e.target as HTMLElement).style.background = "rgba(255,255,255,0.7)")
                }
                onMouseLeave={(e) =>
                  ((e.target as HTMLElement).style.background = isActive ? "rgba(255,255,255,0.5)" : "transparent")
                }
              >
                {l.label}
              </Link>
            );
          })}
        </div>
        )}
        {!isMinimal && showCTA && (
          <button
            onClick={onCTAClick}
            style={{
              padding: "9px 22px",
              borderRadius: 50,
              border: "none",
              cursor: "pointer",
              background: `oklch(22% 0.09 ${ACCENT_HUE})`,
              color: "white",
              fontFamily: "inherit",
              fontWeight: 600,
              fontSize: 14,
              boxShadow: "0 2px 12px rgba(30,60,120,0.18)",
              transition: "transform 0.15s, box-shadow 0.15s",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.transform = "scale(1.04)";
              (e.currentTarget as HTMLElement).style.boxShadow =
                "0 4px 18px rgba(30,60,120,0.28)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.transform = "scale(1)";
              (e.currentTarget as HTMLElement).style.boxShadow =
                "0 2px 12px rgba(30,60,120,0.18)";
            }}
          >
            Start Learning Free
          </button>
        )}
      </div>
    </nav>
  );
}
