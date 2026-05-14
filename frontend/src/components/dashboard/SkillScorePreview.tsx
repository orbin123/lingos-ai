"use client";

import { useEffect, useState } from "react";

interface SkillScorePreviewProps {
  scores: Record<string, number>;
}

const SKILL_LABELS: Record<string, string> = {
  grammar: "Grammar",
  vocabulary: "Vocabulary",
  pronunciation: "Pronunciation",
  fluency: "Fluency",
  thought_org: "Thought Org.",
  listening: "Listening",
  tone: "Tone & Register",
};

function getBarColor(score: number): string {
  if (score < 5) return "oklch(58% 0.2 15)";
  if (score < 7) return "oklch(52% 0.18 240)";
  return "oklch(48% 0.18 155)";
}

export function SkillScorePreview({ scores }: SkillScorePreviewProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Trigger animation after mount
    const timer = setTimeout(() => setMounted(true), 50);
    return () => clearTimeout(timer);
  }, []);

  const skillKeys = Object.keys(SKILL_LABELS);

  return (
    <section>
      {/* Bars */}
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {skillKeys.map((key, index) => {
          const score = scores[key] ?? 0;
          const pct = Math.min((score / 10) * 100, 100);
          const label = SKILL_LABELS[key] || key;

          return (
            <div
              key={key}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
              }}
            >
              {/* Label */}
              <span
                style={{
                  fontSize: 13,
                  fontWeight: 500,
                  color: "oklch(40% 0.07 240)",
                  width: 100,
                  flexShrink: 0,
                }}
              >
                {label}
              </span>

              {/* Bar track */}
              <div
                style={{
                  flex: 1,
                  height: 8,
                  borderRadius: 4,
                  background: "oklch(93% 0.025 250)",
                  overflow: "hidden",
                }}
              >
                {/* Bar fill */}
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

              {/* Score */}
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
