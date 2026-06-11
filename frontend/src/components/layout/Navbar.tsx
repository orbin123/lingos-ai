"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronDown, LogOut, Settings, User } from "lucide-react";
import type { UserOut } from "@/lib/auth-api";
import type { ActivityGridCell } from "@/lib/streak-api";
import { StreakCelebration } from "@/components/streak/StreakCelebration";
import { useStreakDisplay } from "@/hooks/useStreakDisplay";
import { useStreakDemoStore } from "@/store/streakDemoStore";

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

// Maps a single backend activity_grid cell to the navbar popup's
// per-day "state" — done | today | miss | future | frozen.
type DayState = "done" | "today" | "miss" | "future" | "frozen";

interface PopupDay {
  d: string; // weekday letter
  n: number; // day-of-month
  st: DayState;
}

const WEEKDAY_LETTER = ["S", "M", "T", "W", "T", "F", "S"] as const;

function buildLastSevenDays(
  grid: ActivityGridCell[],
  todayIso: string | null,
): PopupDay[] {
  // The backend grid is ascending and always 91 cells; the last 7 are the
  // most recent week (oldest → today). Each cell's `date` is YYYY-MM-DD in
  // the user's timezone, so we parse with `T00:00:00` to avoid UTC drift.
  const slice = grid.slice(-7);
  return slice.map((cell) => {
    const parts = cell.date.split("-").map((n) => Number.parseInt(n, 10));
    const localDate = new Date(parts[0], parts[1] - 1, parts[2]);
    const isToday = todayIso !== null && cell.date === todayIso;
    let st: DayState;
    if (cell.frozen_protected) st = "frozen";
    else if (isToday) st = cell.completed ? "done" : "today";
    else if (cell.completed) st = "done";
    else st = "miss";
    return {
      d: WEEKDAY_LETTER[localDate.getDay()],
      n: localDate.getDate(),
      st,
    };
  });
}

function FlameIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
      <path
        d="M8 14.5c2.7 0 4.8-2 4.8-4.7 0-2.2-1.1-3.3-2.2-4.8 0 1.5-.7 2-1.5 2 0-1.6-1-3.2-2.7-4.7 0 3.2-3.2 4.2-3.2 7.5C3.2 12.5 5.3 14.5 8 14.5z"
        fill="white"
      />
    </svg>
  );
}

function FlakeIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 16 16"
      fill="none"
      stroke="white"
      strokeWidth="1.6"
      strokeLinecap="round"
    >
      <path d="M8 2v12M2 8h12M3.5 3.5l9 9M12.5 3.5l-9 9" />
      <path d="M8 4l-1.5 1.5M8 4l1.5 1.5M8 12l-1.5-1.5M8 12l1.5-1.5M4 8l1.5-1.5M4 8l1.5 1.5M12 8l-1.5-1.5M12 8l-1.5 1.5" />
    </svg>
  );
}

function TrialPill({ user }: { user: UserOut | undefined }) {
  const router = useRouter();
  const state = user?.access_state;

  // Trial countdown while on trial; "Trial ended" link when expired or
  // cancelled. Hidden for active/verified/legacy users.
  if (state !== "trial" && state !== "expired" && state !== "cancelled") {
    return null;
  }

  const ended = state !== "trial";
  const days = user?.days_remaining;
  const label = ended
    ? "Trial ended"
    : days === 1
      ? "Trial · 1 day left"
      : `Trial · ${days ?? "—"} days left`;

  return (
    <button
      type="button"
      onClick={() => router.push("/pricing")}
      title={ended ? "Upgrade to continue learning" : "Upgrade your plan"}
      style={{
        height: 40,
        display: "flex",
        alignItems: "center",
        gap: 6,
        border: ended
          ? "1.5px solid oklch(85% 0.06 25)"
          : "1.5px solid oklch(86% 0.025 240)",
        borderRadius: 999,
        background: ended ? "oklch(97% 0.02 25)" : "white",
        padding: "4px 14px",
        cursor: "pointer",
        fontFamily: "inherit",
        fontSize: 13,
        fontWeight: 700,
        color: ended ? "oklch(45% 0.16 25)" : "oklch(38% 0.1 240)",
        whiteSpace: "nowrap",
      }}
    >
      {label}
    </button>
  );
}


function StreakPill() {
  const [open, setOpen] = useState(false);
  const popoverRef = useRef<HTMLDivElement>(null);
  const [dismissedPlayKey, setDismissedPlayKey] = useState(0);

  const display = useStreakDisplay();
  const playNonce = useStreakDemoStore((s) => s.playNonce);
  const setDemoPreset = useStreakDemoStore((s) => s.setPreset);

  useEffect(() => {
    if (!open) return;
    function handlePointerDown(event: PointerEvent) {
      if (!popoverRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("pointerdown", handlePointerDown);
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, [open]);

  const streak = display.streak;
  const best = display.best;
  const frozen = display.frozen;

  const gridData = display.apiData;

  const todayIso = useMemo(() => {
    if (!gridData) return null;
    return gridData.activity_grid[gridData.activity_grid.length - 1]?.date ?? null;
  }, [gridData]);

  const days: PopupDay[] = useMemo(
    () =>
      gridData ? buildLastSevenDays(gridData.activity_grid, todayIso) : [],
    [gridData, todayIso],
  );

  const showAutoCelebration =
    display.showAutoCelebration && !!display.autoAnimationType;
  const showManualCelebration =
    display.isDemo &&
    playNonce > 0 &&
    playNonce !== dismissedPlayKey &&
    display.demoSnapshot !== null;

  const circleStyle: React.CSSProperties = {
    width: 30,
    height: 30,
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
    position: "relative",
    background: frozen
      ? "linear-gradient(135deg, #93c4e8, #c8e0f4)"
      : "linear-gradient(135deg, #ff7a18, #ffb547)",
    boxShadow: frozen
      ? "0 2px 8px rgba(147,196,232,0.5), inset 0 1px 0 rgba(255,255,255,0.6)"
      : "0 2px 8px rgba(255,122,24,0.4), inset 0 1px 0 rgba(255,255,255,0.4)",
  };

  function dayColor(st: DayState) {
    if (st === "done") return "linear-gradient(135deg, #ff7a18, #ffb547)";
    if (st === "today") return "transparent";
    if (st === "frozen") return "linear-gradient(135deg, #7dc8ff, #bfe5ff)";
    if (st === "miss") return "oklch(94% 0.02 240)";
    return "transparent";
  }

  function dayBorder(st: DayState) {
    if (st === "today") return "2px solid #0070C4";
    if (st === "future") return "1.5px dashed oklch(80% 0.03 240)";
    return "none";
  }

  function dayTextColor(st: DayState) {
    if (st === "done" || st === "frozen") return "white";
    if (st === "today") return "#0070C4";
    if (st === "miss") return "oklch(60% 0.04 240)";
    return "oklch(65% 0.03 240)";
  }

  function handleManualCelebrationClose() {
    const frozenPillDemo =
      display.demoSnapshot?.animationType === "frozen" &&
      display.demoSnapshot.frozen;

    setDismissedPlayKey(playNonce);
    if (frozenPillDemo) {
      setDemoPreset("frozen-to-fire");
    }
  }

  return (
    <div style={{ position: "relative" }} ref={popoverRef}>
      {showAutoCelebration && display.autoAnimationType && (
        <StreakCelebration
          streak={streak}
          best={best}
          animationType={display.autoAnimationType}
          variant={display.celebrationVariant}
          onClose={() => display.refetch()}
        />
      )}
      {showManualCelebration && display.demoSnapshot && (
        <StreakCelebration
          key={playNonce}
          streak={display.demoSnapshot.streak}
          best={display.demoSnapshot.best}
          animationType={display.demoSnapshot.animationType}
          variant={display.demoSnapshot.variant}
          preview
          onClose={handleManualCelebrationClose}
        />
      )}
      {/* Pill trigger */}
      <button
        type="button"
        aria-label="Open streak details"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "5px 14px 5px 5px",
          borderRadius: 999,
          background: "white",
          border: `1.5px solid ${frozen ? "rgba(140,180,220,0.4)" : open ? "rgba(255,140,50,0.4)" : "oklch(86% 0.025 240)"}`,
          boxShadow: open
            ? frozen
              ? "0 4px 12px rgba(140,180,220,0.18)"
              : "0 4px 12px rgba(255,140,50,0.15)"
            : "none",
          cursor: "pointer",
          fontFamily: "inherit",
          transition: "border-color 0.15s, box-shadow 0.15s",
        }}
      >
        <div style={circleStyle}>
          {frozen ? <FlakeIcon /> : <FlameIcon />}
          <span
            style={{
              position: "absolute",
              fontSize: 11,
              fontWeight: 800,
              color: "white",
            }}
          >
            {streak}
          </span>
        </div>
        <span
          style={{
            fontSize: 13,
            fontWeight: 700,
            color: frozen
              ? "oklch(50% 0.04 230)"
              : "oklch(20% 0.09 245)",
            letterSpacing: "0.01em",
          }}
        >
          {frozen ? "Frozen" : `${streak} day${streak === 1 ? "" : "s"}`}
        </span>
      </button>

      {/* Click-open panel */}
      {open && (
        <div
          style={{
            position: "absolute",
            top: "calc(100% + 10px)",
            right: 0,
            width: 300,
            background: "white",
            borderRadius: 18,
            border: "1.5px solid oklch(86% 0.025 240)",
            boxShadow: "0 12px 40px rgba(40,80,150,0.15)",
            padding: 18,
            zIndex: 60,
            overflow: "hidden",
            boxSizing: "border-box",
          }}
        >
          {/* Arrow */}
          <div
            style={{
              position: "absolute",
              top: -7,
              right: 22,
              width: 14,
              height: 14,
              background: "white",
              borderTop: "1.5px solid oklch(86% 0.025 240)",
              borderLeft: "1.5px solid oklch(86% 0.025 240)",
              transform: "rotate(45deg)",
            }}
          />

          {/* Head */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              marginBottom: 14,
            }}
          >
            <div>
              <div
                style={{
                  fontSize: 11,
                  fontWeight: 700,
                  color: "oklch(45% 0.07 240)",
                  letterSpacing: "0.04em",
                  textTransform: "uppercase",
                }}
              >
                Current streak
              </div>
              <div
                style={{
                  fontSize: 30,
                  fontWeight: 800,
                  color: "oklch(20% 0.09 245)",
                  letterSpacing: "-0.03em",
                  lineHeight: 1,
                  marginTop: 4,
                }}
              >
                {streak}
                <span
                  style={{
                    fontSize: 14,
                    color: "oklch(45% 0.07 240)",
                    fontWeight: 600,
                    marginLeft: 4,
                  }}
                >
                  day{streak === 1 ? "" : "s"}
                </span>
              </div>
            </div>
            <div
              style={{
                background: "oklch(96% 0.04 60)",
                borderRadius: 10,
                padding: "8px 10px",
                textAlign: "right",
              }}
            >
              <div
                style={{
                  fontSize: 18,
                  fontWeight: 800,
                  color: "oklch(45% 0.18 60)",
                  lineHeight: 1,
                }}
              >
                {best}
              </div>
              <div
                style={{
                  fontSize: 10,
                  color: "oklch(45% 0.1 60)",
                  fontWeight: 700,
                  letterSpacing: "0.05em",
                  textTransform: "uppercase",
                  marginTop: 3,
                }}
              >
                Personal best
              </div>
            </div>
          </div>

          {/* Week grid — minmax(0,1fr) + no minHeight so aspect-ratio tiles
              stay within the popover (minHeight was forcing 44px-wide cells). */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(7, minmax(0, 1fr))",
              gap: 4,
              marginBottom: 14,
            }}
          >
            {days.length === 0 &&
              Array.from({ length: 7 }).map((_, i) => (
                <div
                  key={`ph-${i}`}
                  style={{
                    aspectRatio: "1",
                    minWidth: 0,
                    borderRadius: 10,
                    background: "oklch(96% 0.015 240)",
                  }}
                />
              ))}
            {days.map((day, i) => (
              <div
                key={i}
                style={{
                  aspectRatio: "1",
                  minWidth: 0,
                  borderRadius: 10,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 10,
                  fontWeight: 700,
                  background: dayColor(day.st),
                  color: dayTextColor(day.st),
                  border: dayBorder(day.st),
                  boxShadow:
                    day.st === "done"
                      ? "0 2px 6px rgba(255,122,24,0.3)"
                      : day.st === "frozen"
                        ? "0 2px 6px rgba(125,200,255,0.35)"
                        : "none",
                  position: "relative",
                }}
              >
                <span style={{ fontSize: 9, opacity: 0.85 }}>{day.d}</span>
                <span style={{ fontSize: 12, fontWeight: 800, marginTop: 1 }}>
                  {day.n}
                </span>
                {day.st === "done" && (
                  <span
                    style={{
                      position: "absolute",
                      top: 2,
                      right: 3,
                      fontSize: 7,
                    }}
                  >
                    🔥
                  </span>
                )}
                {day.st === "frozen" && (
                  <span
                    style={{
                      position: "absolute",
                      top: 2,
                      right: 3,
                      fontSize: 7,
                    }}
                  >
                    ❄
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* Footer note */}
          <div
            style={{
              fontSize: 12,
              lineHeight: 1.5,
              color: "oklch(45% 0.07 240)",
              paddingTop: 12,
              borderTop: "1px dashed oklch(88% 0.02 240)",
            }}
          >
            {streak === 0 ? (
              <>
                <strong style={{ color: "oklch(20% 0.09 245)", fontWeight: 700 }}>
                  Complete a lesson today
                </strong>{" "}
                to start your streak.
              </>
            ) : frozen ? (
              <>
                Streak at risk.{" "}
                <strong style={{ color: "oklch(20% 0.09 245)", fontWeight: 700 }}>
                  Show up today
                </strong>{" "}
                to keep it going — your record is {best}.
              </>
            ) : display.todayComplete ? (
              <>
                <strong style={{ color: "oklch(20% 0.09 245)", fontWeight: 700 }}>
                  Lit today.
                </strong>{" "}
                Come back tomorrow to climb to {streak + 1} — personal best {best}.
              </>
            ) : (
              <>
                You&apos;re{" "}
                <strong style={{ color: "oklch(20% 0.09 245)", fontWeight: 700 }}>
                  {streak} day{streak === 1 ? "" : "s"} strong
                </strong>
                . Keep going — personal best {best}.
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
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
        backdropFilter: "blur(24px)",
        WebkitBackdropFilter: "blur(24px)",
        background: "rgba(232,240,252,0.55)",
        borderBottom: "1px solid rgba(140,170,220,0.14)",
        animation: "slideDown 0.3s ease both",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
      }}
    >
      <div
        style={{
          maxWidth: 1240,
          margin: "0 auto",
          display: "flex",
          alignItems: "center",
          height: 64,
          padding: "0 32px",
          gap: 14,
        }}
      >
        {/* Logo */}
        <Link
          href="/dashboard"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            textDecoration: "none",
            flexShrink: 0,
          }}
        >
          <img
            src="/lingosai_logo.png"
            alt="LingosAI Logo"
            style={{ height: 50, width: "auto", borderRadius: 8 }}
          />
          <span
            style={{
              fontSize: 17,
              fontWeight: 800,
              letterSpacing: "-0.02em",
              color: "oklch(20% 0.09 245)",
            }}
          >
            LingosAI
          </span>
        </Link>

        {/* Nav links */}
        <div style={{ display: "flex", gap: 4, margin: "0 28px" }}>
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                style={{
                  padding: "9px 18px",
                  borderRadius: 999,
                  fontSize: 14,
                  fontWeight: isActive ? 700 : 600,
                  color: isActive
                    ? "#00599e"
                    : "oklch(45% 0.07 240)",
                  background: isActive ? "#d6e8f7" : "transparent",
                  textDecoration: "none",
                  transition: "all 0.15s",
                }}
              >
                {link.label}
              </Link>
            );
          })}
        </div>

        <span style={{ flex: 1 }} />

        {/* Right actions */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <TrialPill user={user} />
          <StreakPill />

          {/* Avatar / account menu */}
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
                gap: 6,
                border: "1.5px solid oklch(86% 0.025 240)",
                borderRadius: 999,
                background: "white",
                padding: "4px 10px 4px 4px",
                cursor: "pointer",
                fontFamily: "inherit",
                transition: "box-shadow 0.15s ease",
              }}
            >
              <span
                style={{
                  width: 30,
                  height: 30,
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  background: "#0070C4",
                  color: "white",
                  fontSize: 12,
                  fontWeight: 800,
                }}
              >
                {getInitials(user?.name)}
              </span>
              <ChevronDown
                size={14}
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

                <AccountMenuLink
                  href="/profile"
                  label="Profile"
                  icon={<User size={16} />}
                />
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
