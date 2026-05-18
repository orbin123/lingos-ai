"use client";

import { useEffect, useState } from "react";

import { SKILL_LABEL_FALLBACK, SKILL_ORDER, getSkillLabel } from "@/lib/skill-labels";

interface SkillScorePreviewProps {
  /** Score per sub-skill, keyed by backend identifier (legacy names). */
  scores: Record<string, number>;
  /**
   * Optional API-provided display labels (`{skill_name: display_label}`).
   * When omitted, the static fallback in `@/lib/skill-labels` is used.
   * The fallback is keyed to the LEGACY backend identifiers so labels
   * resolve correctly even when the API hasn't been updated yet.
   */
  labels?: Record<string, string>;
}

function getBarColor(score: number): string {
  if (score < 5) return "oklch(58% 0.2 15)";
  if (score < 7) return "oklch(52% 0.18 240)";
  return "oklch(48% 0.18 155)";
}

export function SkillScorePreview({ scores, labels }: SkillScorePreviewProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 50);
    return () => clearTimeout(timer);
  }, []);

  // Render in canonical SKILL_ORDER. Skills present in `scores` but unknown
  // to SKILL_ORDER (defensive: future skills) tail-append.
  const knownKeys = SKILL_ORDER.filter((k) => k in SKILL_LABEL_FALLBACK);
  const extraKeys = Object.keys(scores).filter((k) => !knownKeys.includes(k));
  const skillKeys = [...knownKeys, ...extraKeys];

  return (
    <section>
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {skillKeys.map((key, index) => {
          const score = scores[key] ?? 0;
          const pct = Math.min((score / 10) * 100, 100);
          const label = getSkillLabel(key, labels);

          return (
            <div
              key={key}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
              }}
            >
              <span
                style={{
                  fontSize: 13,
                  fontWeight: 500,
                  color: "oklch(40% 0.07 240)",
                  width: 120,
                  flexShrink: 0,
                }}
              >
                {label}
              </span>

              <div
                style={{
                  flex: 1,
                  height: 8,
                  borderRadius: 4,
                  background: "oklch(93% 0.025 250)",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    borderRadius: 4,
                    background: getBarColor(score),
                    width: mounted ? `${pct}%` : "0%",
                    transition: `width 0.6s ease ${index * 0.1}s`,
                  }}
                />
              </div>

              <span
                style={{
                  fontSize: 13,
                  fontWeight: 600,
                  color: "oklch(40% 0.07 240)",
                  width: 32,
                  textAlign: "right",
                  flexShrink: 0,
                }}
              >
                {score.toFixed(1)}
              </span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
