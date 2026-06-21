"use client";

import { useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { useMarketingCTA } from "@/hooks/useMarketingCTA";

const ACCENT_HUE = 240;

const NAV_LINKS = [
  { label: "Features", href: "/features" },
  { label: "How It Works", href: "/how-it-works" },
  { label: "Pricing", href: "/pricing" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

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
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const isMinimal = variant === "minimal";
  const { isAuthed, homeHref, ctaLabel, ctaHref } = useMarketingCTA();

  useEffect(() => {
    const h = () => setScrolled(window.scrollY > 30);
    window.addEventListener("scroll", h);
    return () => window.removeEventListener("scroll", h);
  }, []);

  // Close the mobile menu whenever the route changes.
  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  const handleCTA = () => {
    setMenuOpen(false);
    if (isAuthed) router.push(ctaHref);
    else onCTAClick?.();
  };
  const showCTAButton = !isMinimal && (isAuthed || showCTA);

  return (
    <nav
      className="mkt-section"
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
          href={homeHref}
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
        <div className="mkt-nav-desktop" style={{ display: "flex", gap: 6, marginLeft: "auto" }}>
          {NAV_LINKS.map((l) => {
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
        {showCTAButton && (
          <button
            className="mkt-nav-desktop"
            onClick={handleCTA}
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
            {isAuthed ? ctaLabel : "Start Learning Free"}
          </button>
        )}

        {!isMinimal && (
          <button
            className="mkt-nav-toggle"
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((v) => !v)}
            style={{
              marginLeft: "auto",
              width: 42,
              height: 42,
              padding: 0,
              alignItems: "center",
              justifyContent: "center",
              borderRadius: 12,
              border: "1px solid rgba(255,255,255,0.7)",
              cursor: "pointer",
              background: "rgba(255,255,255,0.6)",
              backdropFilter: "blur(12px)",
              color: "oklch(20% 0.07 245)",
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
              {menuOpen ? (
                <>
                  <line x1="6" y1="6" x2="18" y2="18" />
                  <line x1="18" y1="6" x2="6" y2="18" />
                </>
              ) : (
                <>
                  <line x1="3" y1="6" x2="21" y2="6" />
                  <line x1="3" y1="12" x2="21" y2="12" />
                  <line x1="3" y1="18" x2="21" y2="18" />
                </>
              )}
            </svg>
          </button>
        )}
      </div>

      {!isMinimal && menuOpen && (
        <div
          className="mkt-nav-mobile-panel"
          style={{
            margin: "0 auto",
            maxWidth: 1180,
            padding: "8px 4px 16px",
            animation: "slideDown 0.2s ease",
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 4,
              padding: 12,
              borderRadius: 16,
              background: "rgba(245,250,255,0.96)",
              backdropFilter: "blur(20px)",
              border: "1px solid rgba(255,255,255,0.8)",
              boxShadow: "0 12px 40px rgba(30,60,120,0.16)",
            }}
          >
            {NAV_LINKS.map((l) => {
              const isActive = pathname === l.href;
              return (
                <Link
                  key={l.label}
                  href={l.href}
                  onClick={() => setMenuOpen(false)}
                  style={{
                    padding: "12px 16px",
                    borderRadius: 12,
                    fontSize: 15.5,
                    fontWeight: 600,
                    color: isActive
                      ? `oklch(40% 0.14 ${ACCENT_HUE})`
                      : "oklch(24% 0.07 245)",
                    background: isActive ? "rgba(255,255,255,0.7)" : "transparent",
                    textDecoration: "none",
                  }}
                >
                  {l.label}
                </Link>
              );
            })}
            {showCTAButton && (
              <button
                onClick={handleCTA}
                style={{
                  marginTop: 6,
                  padding: "13px 22px",
                  borderRadius: 12,
                  border: "none",
                  cursor: "pointer",
                  background: `oklch(22% 0.09 ${ACCENT_HUE})`,
                  color: "white",
                  fontFamily: "inherit",
                  fontWeight: 600,
                  fontSize: 15,
                  boxShadow: "0 2px 12px rgba(30,60,120,0.18)",
                }}
              >
                {isAuthed ? ctaLabel : "Start Learning Free"}
              </button>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
