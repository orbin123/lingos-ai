"use client";

import { useEffect, useState } from "react";
import type { AnimationType } from "@/lib/streak-api";
import { streakApi } from "@/lib/streak-api";

interface Props {
  streak: number;
  best: number;
  animationType: AnimationType;
  /** Called after the user dismisses (or auto-dismiss after 4s). */
  onClose?: () => void;
}

/**
 * One-shot celebration overlay. Marks the animation as seen on the server
 * the moment it mounts so a refresh during/after won't replay it.
 *
 * Visual structure is a flat, lightweight port of the StreakCelebration in
 * the Dashboard.html reference — single flame SVG, count-up, brief message.
 */
export function StreakCelebration({ streak, best, animationType, onClose }: Props) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    // Fire-and-forget: persist that the user has seen today's animation.
    streakApi.markAnimationSeen().catch(() => {
      /* swallow — best effort */
    });
    const t = setTimeout(() => {
      setVisible(false);
      onClose?.();
    }, 4200);
    return () => clearTimeout(t);
  }, [onClose]);

  if (!visible) return null;

  const isFrozen = animationType === "frozen";
  const headline =
    animationType === "initial"
      ? "First streak. Welcome to the fire."
      : animationType === "frozen"
        ? "Saved by a freeze."
        : streak === best && streak > 1
          ? "New personal best."
          : streak === 1
            ? "Streak started."
            : "Streak alive.";

  const flame1 = isFrozen ? "#7dc8ff" : "#ff7a18";
  const flame2 = isFrozen ? "#bfe5ff" : "#ffb547";

  return (
    <div
      role="dialog"
      aria-live="polite"
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(8, 12, 20, 0.55)",
        backdropFilter: "blur(4px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
        animation: "streakFade 0.25s ease",
      }}
      onClick={() => {
        setVisible(false);
        onClose?.();
      }}
    >
      <style>{`
        @keyframes streakFade { from { opacity: 0 } to { opacity: 1 } }
        @keyframes streakPop {
          0% { transform: scale(0.6); opacity: 0 }
          60% { transform: scale(1.08); opacity: 1 }
          100% { transform: scale(1); opacity: 1 }
        }
        @keyframes streakFlicker {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.04); }
        }
      `}</style>
      <div
        style={{
          background: "white",
          borderRadius: 24,
          padding: "40px 36px 32px",
          minWidth: 320,
          maxWidth: 380,
          textAlign: "center",
          animation: "streakPop 0.5s cubic-bezier(0.2, 0.9, 0.3, 1.2) both",
        }}
      >
        <svg
          width="120"
          height="150"
          viewBox="0 0 200 260"
          style={{ animation: "streakFlicker 1.2s ease-in-out infinite" }}
        >
          <defs>
            <linearGradient id="cel-flame" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor={flame2} />
              <stop offset="100%" stopColor={flame1} />
            </linearGradient>
          </defs>
          <path
            d="M100 6 C 60 50, 38 88, 38 160 C 38 220, 68 254, 100 254 C 132 254, 162 220, 162 160 C 162 124, 144 108, 128 96 C 128 120, 116 130, 102 122 C 102 90, 84 60, 100 6 Z"
            fill="url(#cel-flame)"
          />
        </svg>
        <div
          style={{
            fontSize: 56,
            fontWeight: 900,
            lineHeight: 1,
            background: `linear-gradient(135deg, ${flame1}, ${flame2})`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
            marginTop: 8,
          }}
        >
          {streak}
        </div>
        <div
          style={{
            fontSize: 12,
            fontWeight: 800,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "oklch(45% 0.07 240)",
            marginTop: 6,
          }}
        >
          day streak
        </div>
        <div
          style={{
            fontSize: 15,
            fontWeight: 700,
            color: "oklch(20% 0.09 245)",
            marginTop: 18,
            lineHeight: 1.4,
          }}
        >
          {headline}
        </div>
      </div>
    </div>
  );
}
