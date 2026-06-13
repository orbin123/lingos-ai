"use client";

import type { CSSProperties, ReactNode } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import type { AnimationType } from "@/lib/streak-api";

type StreakCelebrationVariant = "default" | "on_fire";
import { streakApi } from "@/lib/streak-api";

interface Props {
  streak: number;
  best: number;
  animationType: AnimationType;
  /** Demo panel: do not persist animation-seen on the server */
  preview?: boolean;
  variant?: StreakCelebrationVariant;
  /** Called after the user dismisses the overlay. */
  onClose?: () => void;
}

interface CountUpProps {
  to: number;
  duration?: number;
  delay?: number;
}

type CssVarStyle = CSSProperties & Record<`--${string}`, string>;

function seededRandom(seed: number) {
  const x = Math.sin(seed * 999.13) * 10000;
  return x - Math.floor(x);
}

function between(seed: number, min: number, max: number) {
  return min + seededRandom(seed) * (max - min);
}

function CountUp({ to, duration = 800, delay = 550 }: CountUpProps) {
  const [n, setN] = useState(0);

  useEffect(() => {
    let raf = 0;
    const t = window.setTimeout(() => {
      const start = performance.now();
      const step = (now: number) => {
        const elapsed = now - start;
        if (elapsed >= duration) {
          setN(to);
          return;
        }

        const p = elapsed / duration;
        const eased = 1 - Math.pow(1 - p, 3);
        setN(Math.round(eased * to));
        raf = requestAnimationFrame(step);
      };
      raf = requestAnimationFrame(step);
    }, delay);

    return () => {
      window.clearTimeout(t);
      cancelAnimationFrame(raf);
    };
  }, [delay, duration, to]);

  return <>{n}</>;
}

function resolveMessage(
  animationType: AnimationType,
  streak: number,
  best: number,
  variant: StreakCelebrationVariant,
  isThaw: boolean,
): ReactNode {
  if (isThaw) {
    return (
      <>
        You came back. The fire&apos;s <strong>lit again</strong> - show up
        tomorrow to build something new.
      </>
    );
  }

  if (animationType === "rekindle") {
    return (
      <>
        Streak rekindled. Day <strong>1 of a new run</strong> - show up
        tomorrow to climb to 2.
      </>
    );
  }

  if (variant === "on_fire" || (animationType === "on_fire" && streak >= 10)) {
    return (
      <>
        Hottest stretch of the month. Come back tomorrow to{" "}
        <strong>keep the fire alive</strong>.
      </>
    );
  }

  if (streak >= best && streak > 1) {
    return (
      <>
        <strong>New personal best.</strong> You&apos;ve never burned this bright.
      </>
    );
  }

  if (streak >= 3) {
    return (
      <>
        Your fire is growing. <strong>Show up tomorrow</strong> and it climbs
        to {streak + 1}.
      </>
    );
  }

  return (
    <>
      You lit it. <strong>Come back tomorrow</strong> to keep it burning.
    </>
  );
}

export function StreakCelebration({
  streak,
  best,
  animationType,
  preview = false,
  variant = "default",
  onClose,
}: Props) {
  const isThaw =
    animationType === "frozen_to_fire" ||
    (animationType === "frozen" && streak === 0);
  const displayStreak = isThaw ? 1 : streak;
  const [exiting, setExiting] = useState(false);
  const [ignited, setIgnited] = useState(!isThaw);
  const gradientIds = {
    ice: "cel-flame-ice",
    outer: "cel-flame-outer",
    inner: "cel-flame-inner",
  };

  const handleClose = useCallback(() => {
    if (exiting) return;
    setExiting(true);
    window.setTimeout(() => onClose?.(), 620);
  }, [exiting, onClose]);

  useEffect(() => {
    if (!preview) {
      streakApi.markAnimationSeen().catch(() => {
        /* swallow - best effort */
      });
    }
  }, [preview]);

  useEffect(() => {
    if (!isThaw) return;
    const t = window.setTimeout(() => setIgnited(true), 1450);
    return () => window.clearTimeout(t);
  }, [isThaw]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") handleClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [handleClose]);

  const embers = useMemo(
    () =>
      Array.from({ length: 36 }, (_, i) => {
        const angle = (i / 36) * Math.PI * 2 + between(i + 1, -0.175, 0.175);
        const dist = between(i + 101, 170, 390);
        const colors = ["#ffe27a", "#ffb547", "#ff7a18", "#ff4d00"];
        return {
          tx: Math.cos(angle) * dist,
          ty: Math.sin(angle) * dist - 50,
          size: between(i + 201, 4, 13),
          delay: between(i + 301, 0.55, 1),
          dur: between(i + 401, 1.2, 2.6),
          color: colors[i % colors.length],
        };
      }),
    [],
  );

  const sparks = useMemo(
    () =>
      Array.from({ length: 26 }, (_, i) => ({
        x: between(i + 501, 0, 100),
        delay: between(i + 601, 0, 4),
        dur: between(i + 701, 3, 7),
        size: between(i + 801, 2, 6),
        drift: between(i + 901, -30, 30),
      })),
    [],
  );

  const snowflakes = useMemo(
    () =>
      isThaw
        ? Array.from({ length: 22 }, (_, i) => ({
            x: between(i + 1801, 0, 100),
            delay: between(i + 1901, 0, 1.5),
            dur: between(i + 2001, 2.6, 5),
            size: between(i + 2101, 9, 19),
            drift: between(i + 2201, -50, 50),
          }))
        : [],
    [isThaw],
  );

  const shards = useMemo(
    () =>
      isThaw
        ? Array.from({ length: 16 }, (_, i) => {
            const angle =
              (i / 16) * Math.PI * 2 + between(i + 1101, -0.2, 0.2);
            const dist = between(i + 1201, 180, 360);
            return {
              tx: Math.cos(angle) * dist,
              ty: Math.sin(angle) * dist + 60,
              w: between(i + 1301, 6, 12),
              h: between(i + 1401, 12, 28),
              delay: between(i + 1501, 0, 0.15),
              dur: between(i + 1601, 0.85, 1.35),
              rot: between(i + 1701, -360, 360),
            };
          })
        : [],
    [isThaw],
  );

  const off = isThaw ? 1.5 : 0;
  const dayLetters = ["M", "T", "W", "T", "F", "S", "S"];
  const dayNums = [28, 29, 30, 1, 2, 3, 4];
  const litArr = isThaw
    ? [false, false, false, false, true, false, false]
    : Array.from({ length: 7 }, (_, i) => i < Math.min(displayStreak, 7));
  const todayIdx = 4;
  const eyebrowText =
    isThaw || animationType === "rekindle"
      ? "Streak rekindled"
      : "Streak extended";
  const message = resolveMessage(
    animationType,
    displayStreak,
    best,
    variant,
    isThaw,
  );

  const overlay = (
    <div
      className={`celebrate ${exiting ? "exit" : ""} ${isThaw ? "thaw" : ""} ${ignited ? "ignited" : ""}`}
      role="dialog"
      aria-label="Streak celebration"
      aria-modal="true"
    >
      <style>{CELEBRATION_CSS}</style>
      <div className="celebrate-vignette" />

      <div className="celebrate-sparks">
        {sparks.map((s, i) => (
          <span
            key={i}
            style={
              {
                left: `${s.x}%`,
                width: `${s.size}px`,
                height: `${s.size}px`,
                animationDelay: `${s.delay}s`,
                animationDuration: `${s.dur}s`,
                "--drift": `${s.drift}px`,
              } as CssVarStyle
            }
          />
        ))}
      </div>

      {isThaw && (
        <div className="celebrate-snow">
          {snowflakes.map((s, i) => (
            <span
              key={i}
              style={
                {
                  left: `${s.x}%`,
                  fontSize: `${s.size}px`,
                  animationDelay: `${s.delay}s`,
                  animationDuration: `${s.dur}s`,
                  "--drift": `${s.drift}px`,
                } as CssVarStyle
              }
            >
              ❄
            </span>
          ))}
        </div>
      )}

      {isThaw && <div className="celebrate-flash" />}

      <button
        className="celebrate-close"
        onClick={handleClose}
        aria-label="Close"
        type="button"
      >
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path
            d="M3 3l8 8M11 3l-8 8"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
        </svg>
      </button>

      <div className="celebrate-content">
        <div className="celebrate-eyebrow">
          <span>{eyebrowText}</span>
        </div>

        <div className="celebrate-hero">
          <div className="celebrate-glow" />
          {isThaw && <div className="celebrate-frost-halo" />}

          {isThaw && (
            <svg
              className="celebrate-flame ice"
              viewBox="0 0 200 260"
              preserveAspectRatio="xMidYMid meet"
            >
              <defs>
                <linearGradient id={gradientIds.ice} x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0" stopColor="#f4fbff" />
                  <stop offset="0.45" stopColor="#a8d4f0" />
                  <stop offset="1" stopColor="#3d6fa6" />
                </linearGradient>
              </defs>
              <path
                d="M100 6 C 60 50, 38 88, 38 160 C 38 220, 68 254, 100 254 C 132 254, 162 220, 162 160 C 162 124, 144 108, 128 96 C 128 120, 116 130, 102 122 C 102 90, 84 60, 100 6 Z"
                fill={`url(#${gradientIds.ice})`}
              />
              <g
                stroke="rgba(255,255,255,0.85)"
                strokeWidth="1.4"
                strokeLinecap="round"
                fill="none"
              >
                <path d="M85 100 v10 M80 105 h10 M82 102 l6 6 M88 102 l-6 6" />
                <path d="M120 140 v8 M116 144 h8 M118 141 l4 6 M122 141 l-4 6" />
                <path d="M95 175 v8 M91 179 h8" />
              </g>
            </svg>
          )}

          <svg
            className="celebrate-flame fire flicker-a"
            viewBox="0 0 200 260"
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <linearGradient id={gradientIds.outer} x1="0" x2="0" y1="0" y2="1">
                <stop offset="0" stopColor="#ffd166" />
                <stop offset="0.45" stopColor="#ff8c1a" />
                <stop offset="1" stopColor="#d92e00" />
              </linearGradient>
            </defs>
            <path
              d="M100 6 C 60 50, 38 88, 38 160 C 38 220, 68 254, 100 254 C 132 254, 162 220, 162 160 C 162 124, 144 108, 128 96 C 128 120, 116 130, 102 122 C 102 90, 84 60, 100 6 Z"
              fill={`url(#${gradientIds.outer})`}
            />
          </svg>

          <svg
            className="celebrate-flame fire flicker-b"
            viewBox="0 0 200 260"
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <linearGradient id={gradientIds.inner} x1="0" x2="0" y1="0" y2="1">
                <stop offset="0" stopColor="#fff7c2" />
                <stop offset="0.4" stopColor="#ffd166" />
                <stop offset="1" stopColor="#ff7a18" />
              </linearGradient>
            </defs>
            <path
              d="M100 70 C 80 102, 70 132, 70 178 C 70 214, 86 232, 100 232 C 114 232, 130 214, 130 178 C 130 150, 120 140, 112 132 C 112 148, 105 154, 100 152 C 100 134, 90 114, 100 70 Z"
              fill={`url(#${gradientIds.inner})`}
            />
          </svg>

          {isThaw && <div className="celebrate-shockwave" />}
          {isThaw &&
            shards.map((sh, i) => (
              <span
                key={i}
                className="celebrate-shard"
                style={
                  {
                    width: `${sh.w}px`,
                    height: `${sh.h}px`,
                    "--w": `${sh.w}px`,
                    "--h": `${sh.h}px`,
                    "--tx": `${sh.tx}px`,
                    "--ty": `${sh.ty}px`,
                    "--rot": `${sh.rot}deg`,
                    "--delay": `${sh.delay}s`,
                    "--dur": `${sh.dur}s`,
                  } as CssVarStyle
                }
              />
            ))}

          <div className="celebrate-num">
            <CountUp to={displayStreak} duration={800} delay={550 + off * 1000} />
          </div>

          {embers.map((e, i) => (
            <span
              key={i}
              className="celebrate-ember"
              style={
                {
                  "--tx": `${e.tx}px`,
                  "--ty": `${e.ty}px`,
                  "--size": `${e.size}px`,
                  "--delay": `${e.delay + off}s`,
                  "--dur": `${e.dur}s`,
                  "--color": e.color,
                } as CssVarStyle
              }
            />
          ))}
        </div>

        <div className="celebrate-label">day streak</div>
        <div className="celebrate-msg">{message}</div>

        <div className="celebrate-week">
          {dayLetters.map((d, i) => (
            <div
              key={`${d}-${dayNums[i]}-${i}`}
              className={`cw-cell ${litArr[i] ? "lit" : ""} ${
                i === todayIdx ? "today" : ""
              }`}
              style={{ animationDelay: `${1.3 + off + i * 0.07}s` }}
            >
              <span className="cw-d">{d}</span>
              <span className="cw-num">{dayNums[i]}</span>
            </div>
          ))}
        </div>

        <button className="celebrate-btn" onClick={handleClose} type="button">
          {isThaw ? "Keep it going" : "Keep going"}
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path
              d="M6 4l4 4-4 4"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  );

  if (typeof document === "undefined") return null;

  return createPortal(overlay, document.body);
}

const CELEBRATION_CSS = `
  .celebrate {
    position: fixed;
    inset: 0;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    isolation: isolate;
    --off: 0s;
    font-family: 'Plus Jakarta Sans', var(--font-geist-sans), Arial, sans-serif;
  }

  .celebrate.thaw { --off: 1.5s; }
  .celebrate.exit { pointer-events: none; }

  .celebrate-vignette {
    position: absolute;
    inset: 0;
    background:
      radial-gradient(ellipse 80% 60% at 50% 110%, rgba(255,90,10,0.55), transparent 60%),
      radial-gradient(ellipse 70% 50% at 50% 50%, rgba(60,20,40,0.55), transparent 70%),
      linear-gradient(180deg, rgba(10,8,18,0.92), rgba(20,8,20,0.97));
    animation: cel-bg-in 0.45s ease both;
  }

  .celebrate.exit .celebrate-vignette { animation: cel-bg-out 0.55s ease both; }
  @keyframes cel-bg-in { from { opacity: 0; } to { opacity: 1; } }
  @keyframes cel-bg-out { to { opacity: 0; } }

  .celebrate-sparks {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }

  .celebrate-sparks span {
    position: absolute;
    bottom: -20px;
    border-radius: 50%;
    background: radial-gradient(circle, #ffe27a 0%, #ff7a18 55%, transparent 75%);
    box-shadow: 0 0 10px #ff8a18, 0 0 22px rgba(255,138,24,0.5);
    animation: cel-spark-rise linear infinite;
    opacity: 0;
  }

  @keyframes cel-spark-rise {
    0% { transform: translate(0, 0) scale(1); opacity: 0; }
    8% { opacity: 0.9; }
    85% { opacity: 0.5; }
    100% { transform: translate(var(--drift, 20px), -110vh) scale(0.3); opacity: 0; }
  }

  .celebrate.exit .celebrate-sparks { animation: cel-bg-out 0.4s ease both; }

  .celebrate-close {
    position: absolute;
    top: 22px;
    right: 22px;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.7);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    transition: background 0.15s, color 0.15s, transform 0.25s;
    animation: cel-fade-in 0.5s ease 0.6s both;
    z-index: 5;
    cursor: pointer;
  }

  .celebrate-close:hover {
    background: rgba(255,255,255,0.16);
    color: white;
    transform: rotate(90deg);
  }

  .celebrate-content {
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 32px;
    max-width: 480px;
  }

  .celebrate.exit .celebrate-content { animation: cel-content-out 0.5s ease both; }
  @keyframes cel-content-out { to { opacity: 0; transform: translateY(-16px); } }

  .celebrate-eyebrow {
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: rgba(255,200,140,0.9);
    margin-bottom: 18px;
    animation: cel-fade-up 0.55s ease calc(var(--off) + 0.25s) both;
  }

  .celebrate-eyebrow span {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    background: rgba(255,140,40,0.12);
    border: 1px solid rgba(255,170,80,0.35);
  }

  .celebrate-hero {
    position: relative;
    width: 300px;
    height: 320px;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: cel-hero-in 0.95s cubic-bezier(0.34, 1.56, 0.64, 1) 0.1s both;
  }

  .celebrate.exit .celebrate-hero {
    animation: cel-hero-out 0.6s cubic-bezier(0.5, 0, 0.75, 0) both;
  }

  @keyframes cel-hero-in {
    0% { transform: translateY(80px) scale(0.2); opacity: 0; }
    55% { transform: translateY(-12px) scale(1.08); opacity: 1; }
    100% { transform: translateY(0) scale(1); opacity: 1; }
  }

  @keyframes cel-hero-out {
    to { transform: translate(38vw, -42vh) scale(0.08); opacity: 0; }
  }

  .celebrate-glow {
    position: absolute;
    inset: -50px;
    background: radial-gradient(circle, rgba(255,160,50,0.55), rgba(255,80,0,0.18) 40%, transparent 70%);
    filter: blur(14px);
    animation: cel-glow-pulse 2.6s ease-in-out infinite;
    z-index: 0;
  }

  @keyframes cel-glow-pulse {
    0%, 100% { transform: scale(1); opacity: 0.7; }
    50% { transform: scale(1.18); opacity: 1; }
  }

  .celebrate-flame {
    position: absolute;
    width: 100%;
    height: 100%;
    filter: drop-shadow(0 8px 26px rgba(255,90,10,0.7));
    z-index: 1;
  }

  .celebrate-flame.flicker-a {
    animation: cel-flicker-a 0.7s ease-in-out infinite alternate;
    transform-origin: 50% 100%;
  }

  .celebrate-flame.flicker-b {
    animation: cel-flicker-b 0.55s ease-in-out infinite alternate;
    transform-origin: 50% 100%;
    mix-blend-mode: screen;
    opacity: 0.95;
  }

  @keyframes cel-flicker-a {
    0% { transform: scale(1, 1) translateY(0); }
    100% { transform: scale(1.04, 0.96) translateY(-3px); }
  }

  @keyframes cel-flicker-b {
    0% { transform: scale(0.95, 1.02) translateY(2px); }
    100% { transform: scale(1.03, 1.06) translateY(-4px); }
  }

  .celebrate-num {
    position: relative;
    z-index: 3;
    font-family: 'Plus Jakarta Sans', var(--font-geist-sans), Arial, sans-serif;
    font-size: 132px;
    font-weight: 900;
    color: white;
    line-height: 1;
    letter-spacing: -0.05em;
    text-shadow:
      0 6px 0 rgba(170,30,0,0.55),
      0 12px 30px rgba(255,80,0,0.55),
      0 0 38px rgba(255,200,80,0.65);
    margin-top: 36px;
    animation: cel-num-in 0.7s cubic-bezier(0.34, 1.56, 0.64, 1) calc(var(--off) + 0.55s) both;
  }

  @keyframes cel-num-in {
    0% { transform: scale(0) rotate(-12deg); opacity: 0; }
    65% { transform: scale(1.18) rotate(4deg); opacity: 1; }
    100% { transform: scale(1) rotate(0); opacity: 1; }
  }

  .celebrate-ember {
    position: absolute;
    top: 50%;
    left: 50%;
    width: var(--size);
    height: var(--size);
    border-radius: 50%;
    background: var(--color);
    box-shadow: 0 0 12px var(--color), 0 0 26px rgba(255,140,40,0.45);
    animation: cel-ember-burst var(--dur) ease-out var(--delay) both;
    opacity: 0;
    z-index: 2;
  }

  @keyframes cel-ember-burst {
    0% { transform: translate(-50%, -50%) scale(0.4); opacity: 0; }
    15% { opacity: 1; }
    100% { transform: translate(calc(-50% + var(--tx)), calc(-50% + var(--ty))) scale(0.1); opacity: 0; }
  }

  .celebrate-label {
    font-size: 22px;
    font-weight: 700;
    color: rgba(255,210,150,0.95);
    letter-spacing: 0.04em;
    text-transform: lowercase;
    margin-top: 6px;
    animation: cel-fade-up 0.6s ease calc(var(--off) + 1.2s) both;
  }

  .celebrate-msg {
    font-size: 15.5px;
    font-weight: 500;
    line-height: 1.5;
    color: rgba(255,255,255,0.78);
    max-width: 360px;
    margin-top: 18px;
    animation: cel-fade-up 0.6s ease calc(var(--off) + 1.4s) both;
  }

  .celebrate-msg strong {
    color: rgba(255,210,140,1);
    font-weight: 800;
  }

  .celebrate-week {
    display: flex;
    gap: 8px;
    margin-top: 26px;
  }

  .cw-cell {
    width: 42px;
    height: 52px;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    color: rgba(255,255,255,0.4);
    background: rgba(255,255,255,0.05);
    border: 1.5px solid rgba(255,255,255,0.08);
    animation: cel-day-pop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
    position: relative;
  }

  .cw-cell.lit {
    background: linear-gradient(135deg, #ff7a18, #ffb547);
    color: white;
    border-color: rgba(255,200,120,0.55);
    box-shadow: 0 6px 18px rgba(255,120,20,0.45), inset 0 1px 0 rgba(255,255,255,0.35);
  }

  .cw-cell.today::after {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 14px;
    border: 2px solid rgba(255,255,255,0.6);
    animation: cel-today-pulse 1.6s ease-in-out infinite;
    pointer-events: none;
  }

  @keyframes cel-today-pulse {
    0%, 100% { transform: scale(1); opacity: 0.9; }
    50% { transform: scale(1.08); opacity: 0.3; }
  }

  .cw-d {
    font-size: 10px;
    opacity: 0.85;
    letter-spacing: 0.06em;
    font-weight: 800;
  }

  .cw-num {
    font-size: 14px;
    font-weight: 800;
  }

  @keyframes cel-day-pop {
    0% { transform: scale(0) translateY(16px); opacity: 0; }
    100% { transform: scale(1) translateY(0); opacity: 1; }
  }

  .celebrate-btn {
    margin-top: 36px;
    padding: 15px 48px;
    border-radius: 999px;
    border: none;
    font-size: 14.5px;
    font-weight: 800;
    letter-spacing: 0.02em;
    background: white;
    color: oklch(20% 0.05 240);
    display: inline-flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 12px 28px rgba(255,120,20,0.4);
    animation: cel-fade-up 0.55s ease calc(var(--off) + 1.95s) both, cel-btn-pulse 2.2s ease calc(var(--off) + 2.6s) infinite;
    transition: transform 0.15s, box-shadow 0.15s;
    cursor: pointer;
  }

  .celebrate-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 32px rgba(255,140,40,0.55);
  }

  @keyframes cel-btn-pulse {
    0%, 100% { box-shadow: 0 12px 28px rgba(255,120,20,0.4), 0 0 0 0 rgba(255,200,120,0.35); }
    50% { box-shadow: 0 12px 28px rgba(255,120,20,0.4), 0 0 0 14px rgba(255,200,120,0); }
  }

  @keyframes cel-fade-up {
    0% { transform: translateY(18px); opacity: 0; }
    100% { transform: translateY(0); opacity: 1; }
  }

  @keyframes cel-fade-in {
    0% { opacity: 0; }
    100% { opacity: 1; }
  }

  .celebrate.thaw .celebrate-vignette {
    background:
      radial-gradient(ellipse 80% 60% at 50% 110%, rgba(140,200,240,0.45), transparent 60%),
      radial-gradient(ellipse 70% 50% at 50% 45%, rgba(40,70,110,0.55), transparent 70%),
      linear-gradient(180deg, rgba(8,14,28,0.95), rgba(14,22,40,0.97));
    transition: background 0.9s ease;
  }

  .celebrate.thaw.ignited .celebrate-vignette {
    background:
      radial-gradient(ellipse 80% 60% at 50% 110%, rgba(255,90,10,0.55), transparent 60%),
      radial-gradient(ellipse 70% 50% at 50% 50%, rgba(60,20,40,0.55), transparent 70%),
      linear-gradient(180deg, rgba(10,8,18,0.92), rgba(20,8,20,0.97));
  }

  .celebrate-snow {
    position: absolute;
    inset: 0;
    pointer-events: none;
    transition: opacity 0.7s ease;
  }

  .celebrate.thaw.ignited .celebrate-snow { opacity: 0; }

  .celebrate-snow span {
    position: absolute;
    top: -24px;
    color: rgba(220,240,255,0.95);
    text-shadow: 0 0 8px rgba(160,210,250,0.7);
    user-select: none;
    animation: cel-snow-fall linear infinite;
    opacity: 0;
  }

  @keyframes cel-snow-fall {
    0% { transform: translate(0, 0) rotate(0); opacity: 0; }
    8% { opacity: 1; }
    90% { opacity: 0.7; }
    100% { transform: translate(var(--drift, 30px), 110vh) rotate(360deg); opacity: 0; }
  }

  .celebrate.thaw .celebrate-sparks {
    opacity: 0;
    transition: opacity 0.6s ease 0.2s;
  }

  .celebrate.thaw.ignited .celebrate-sparks { opacity: 1; }

  .celebrate-flame.ice {
    filter: drop-shadow(0 0 24px rgba(140,210,250,0.7));
    transition: opacity 0.55s ease, transform 0.55s ease;
    animation: cel-ice-breath 2.6s ease-in-out infinite alternate;
    transform-origin: 50% 100%;
  }

  @keyframes cel-ice-breath {
    0% { transform: scale(1, 1) translateY(0); }
    100% { transform: scale(1.015, 0.99) translateY(-2px); }
  }

  .celebrate.thaw.ignited .celebrate-flame.ice {
    opacity: 0;
    transform: scale(1.18) translateY(-6px);
  }

  .celebrate-frost-halo {
    position: absolute;
    inset: -40px;
    background: radial-gradient(circle, rgba(180,220,250,0.55), rgba(80,130,200,0.18) 45%, transparent 70%);
    filter: blur(14px);
    animation: cel-frost-shimmer 2.8s ease-in-out infinite;
    z-index: 0;
    transition: opacity 0.55s ease;
  }

  .celebrate.thaw.ignited .celebrate-frost-halo { opacity: 0; }

  @keyframes cel-frost-shimmer {
    0%, 100% { transform: scale(1); opacity: 0.7; }
    50% { transform: scale(1.12); opacity: 1; }
  }

  .celebrate.thaw .celebrate-glow {
    opacity: 0;
    transition: opacity 0.7s ease 0.15s;
  }

  .celebrate.thaw.ignited .celebrate-glow { opacity: 1; }

  .celebrate.thaw .celebrate-flame.fire {
    opacity: 0;
    transition: opacity 0.6s ease 0.2s;
  }

  .celebrate.thaw.ignited .celebrate-flame.fire { opacity: 1; }

  .celebrate-shard {
    position: absolute;
    top: 50%;
    left: 50%;
    width: var(--w, 8px);
    height: var(--h, 16px);
    background: linear-gradient(180deg, rgba(240,250,255,0.98), rgba(150,200,235,0.85));
    clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%);
    box-shadow: 0 0 12px rgba(200,230,255,0.6);
    opacity: 0;
    z-index: 4;
    transform: translate(-50%, -50%);
  }

  .celebrate.thaw.ignited .celebrate-shard {
    animation: cel-shard-fly var(--dur, 0.9s) cubic-bezier(0.35, 0.1, 0.7, 1) var(--delay, 0s) both;
  }

  @keyframes cel-shard-fly {
    0% { transform: translate(-50%, -50%) rotate(0); opacity: 0; }
    10% { opacity: 1; }
    100% {
      transform: translate(calc(-50% + var(--tx, 0px)), calc(-50% + var(--ty, 100px))) rotate(var(--rot, 360deg));
      opacity: 0;
    }
  }

  .celebrate-shockwave {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 40px;
    height: 40px;
    margin: -20px 0 0 -20px;
    border-radius: 50%;
    border: 3px solid rgba(255,220,140,0.95);
    opacity: 0;
    z-index: 3;
    pointer-events: none;
  }

  .celebrate.thaw.ignited .celebrate-shockwave {
    animation: cel-shockwave 0.85s cubic-bezier(0.2, 0.7, 0.4, 1) both;
  }

  @keyframes cel-shockwave {
    0% { transform: scale(0.3); opacity: 0; border-width: 4px; }
    18% { opacity: 1; }
    100% { transform: scale(15); opacity: 0; border-width: 1px; }
  }

  .celebrate-flash {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at center, rgba(255,240,180,0.85), rgba(255,180,80,0.3) 25%, transparent 55%);
    opacity: 0;
    pointer-events: none;
    z-index: 4;
  }

  .celebrate.thaw.ignited .celebrate-flash {
    animation: cel-flash 0.55s ease-out both;
  }

  @keyframes cel-flash {
    0% { opacity: 0; }
    20% { opacity: 1; }
    100% { opacity: 0; }
  }

  @media (max-width: 640px) {
    .celebrate-content {
      padding: 22px;
      max-width: 100vw;
    }

    .celebrate-hero {
      width: 240px;
      height: 260px;
    }

    .celebrate-num {
      font-size: 106px;
      margin-top: 30px;
    }

    .celebrate-week {
      gap: 6px;
    }

    .cw-cell {
      width: 36px;
      height: 46px;
      border-radius: 10px;
    }

    .celebrate-msg {
      max-width: 310px;
    }
  }
`;
