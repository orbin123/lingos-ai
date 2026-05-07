"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useRef, useState } from "react";
import { ChevronDown, LogOut, Settings, User } from "lucide-react";
import type { UserOut } from "@/lib/auth-api";

interface NavbarProps {
  user: UserOut | undefined;
  onSignOut?: () => void;
}

const NAV_LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/stats", label: "Stats" },
  { href: "/challenges", label: "Challenges" },
] as const;

function getInitials(name: string | undefined): string {
  if (!name) return "??";
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
}

export function Navbar({ user, onSignOut }: NavbarProps) {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handlePointerDown(event: PointerEvent) {
      if (!menuRef.current?.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }

    document.addEventListener("pointerdown", handlePointerDown);
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, []);

  return (
    <nav
      style={{
        position: "sticky",
        top: 0,
        zIndex: 50,
        background: "rgba(255,255,255,0.8)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
        borderBottom: "1px solid rgba(80,120,200,0.12)",
        animation: "slideDown 0.3s ease both",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
      }}
    >
      <div
        style={{
          maxWidth: 1180,
          margin: "0 auto",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          height: 64,
          padding: "0 24px",
        }}
      >
        {/* Left — Logo */}
        <Link
          href="/dashboard"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            textDecoration: "none",
          }}
        >
          <img
            src="/lingos-logo2.png"
            alt="LingosAI Logo"
            style={{ height: 50, width: "auto", borderRadius: 8 }}
          />
          <span
            style={{
              fontWeight: 700,
              fontSize: 17,
              color: "oklch(18% 0.09 245)",
              letterSpacing: "-0.3px",
            }}
          >
            LingosAI
          </span>
        </Link>

        {/* Center — Nav links */}
        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                style={{
                  position: "relative",
                  padding: "6px 14px",
                  borderRadius: 8,
                  fontSize: 14,
                  fontWeight: isActive ? 600 : 500,
                  color: isActive
                    ? "oklch(52% 0.18 240)"
                    : "oklch(45% 0.07 240)",
                  background: isActive
                    ? "oklch(93% 0.025 250)"
                    : "transparent",
                  textDecoration: "none",
                  transition:
                    "background 0.15s ease, color 0.15s ease",
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.background =
                      "oklch(95% 0.015 250)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.background = "transparent";
                  }
                }}
              >
                {link.label}
                {isActive && (
                  <span
                    style={{
                      position: "absolute",
                      bottom: -1,
                      left: "50%",
                      transform: "translateX(-50%)",
                      width: 20,
                      height: 2,
                      borderRadius: 1,
                      background: "oklch(52% 0.18 240)",
                    }}
                  />
                )}
              </Link>
            );
          })}
        </div>

        {/* Right — Account menu */}
        <div ref={menuRef} style={{ position: "relative", flexShrink: 0 }}>
          <button
            type="button"
            aria-label="Open profile menu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((open) => !open)}
            style={{
              height: 40,
              display: "flex",
              alignItems: "center",
              gap: 8,
              border: "1px solid rgba(80,120,200,0.18)",
              borderRadius: 999,
              background: "rgba(255,255,255,0.72)",
              padding: "2px 8px 2px 2px",
              cursor: "pointer",
              fontFamily: "inherit",
              boxShadow: menuOpen
                ? "0 8px 24px rgba(80,110,180,0.14)"
                : "0 1px 4px rgba(80,110,180,0.06)",
              transition: "box-shadow 0.15s ease, border-color 0.15s ease",
            }}
          >
            <span
              style={{
                width: 36,
                height: 36,
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: "oklch(52% 0.18 240)",
                color: "white",
                fontSize: 13,
                fontWeight: 700,
                letterSpacing: "0.5px",
              }}
            >
              {getInitials(user?.name)}
            </span>
            <ChevronDown
              size={16}
              strokeWidth={2.2}
              color="oklch(42% 0.08 240)"
              style={{
                transform: menuOpen ? "rotate(180deg)" : "rotate(0deg)",
                transition: "transform 0.15s ease",
              }}
            />
          </button>

          {menuOpen && (
            <div
              role="menu"
              style={{
                position: "absolute",
                top: 48,
                right: 0,
                width: 220,
                borderRadius: 8,
                border: "1px solid rgba(80,120,200,0.14)",
                background: "rgba(255,255,255,0.96)",
                boxShadow:
                  "0 18px 44px rgba(55,75,130,0.16), 0 2px 8px rgba(80,120,200,0.08)",
                padding: 8,
              }}
            >
              <div
                style={{
                  padding: "8px 10px 10px",
                  borderBottom: "1px solid rgba(80,120,200,0.1)",
                  marginBottom: 6,
                }}
              >
                <div
                  style={{
                    color: "oklch(18% 0.09 245)",
                    fontSize: 13,
                    fontWeight: 700,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {user?.name ?? "Your account"}
                </div>
                <div
                  style={{
                    color: "oklch(48% 0.06 240)",
                    fontSize: 12,
                    marginTop: 2,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {user?.email ?? "Profile menu"}
                </div>
              </div>

              <AccountMenuLink href="/profile" label="Profile" icon={<User size={16} />} />
              <AccountMenuLink
                href="/settings"
                label="Settings"
                icon={<Settings size={16} />}
              />

              <div
                style={{
                  height: 1,
                  background: "rgba(80,120,200,0.1)",
                  margin: "6px 0",
                }}
              />

              <button
                type="button"
                role="menuitem"
                onClick={onSignOut}
                style={{
                  width: "100%",
                  minHeight: 38,
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  border: "none",
                  borderRadius: 6,
                  background: "transparent",
                  color: "oklch(48% 0.18 28)",
                  cursor: "pointer",
                  fontFamily: "inherit",
                  fontSize: 14,
                  fontWeight: 650,
                  padding: "8px 10px",
                  textAlign: "left",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "oklch(96% 0.025 28)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "transparent";
                }}
              >
                <LogOut size={16} />
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

function AccountMenuLink({
  href,
  label,
  icon,
}: {
  href: string;
  label: string;
  icon: ReactNode;
}) {
  return (
    <Link
      href={href}
      role="menuitem"
      style={{
        minHeight: 38,
        display: "flex",
        alignItems: "center",
        gap: 10,
        borderRadius: 6,
        color: "oklch(30% 0.08 240)",
        fontSize: 14,
        fontWeight: 600,
        padding: "8px 10px",
        textDecoration: "none",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = "oklch(95% 0.015 250)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = "transparent";
      }}
    >
      {icon}
      {label}
    </Link>
  );
}
