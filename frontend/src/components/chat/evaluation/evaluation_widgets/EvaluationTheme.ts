import type { CSSProperties } from "react";
import type { EvaluationTier } from "../source";

export const tierStyles: Record<EvaluationTier, { bg: string; fg: string; label: string }> = {
  excellent: { bg: "oklch(94% 0.06 155)", fg: "oklch(35% 0.18 155)", label: "Excellent" },
  good: { bg: "oklch(94% 0.06 210)", fg: "oklch(35% 0.18 240)", label: "Good" },
  average: { bg: "oklch(95% 0.05 90)", fg: "oklch(40% 0.14 75)", label: "Average" },
  needs_work: { bg: "oklch(94% 0.06 25)", fg: "oklch(40% 0.16 25)", label: "Needs work" },
};

export const sectionLabelStyle: CSSProperties = {
  fontSize: 11.5,
  fontWeight: 800,
  textTransform: "uppercase",
  color: "oklch(45% 0.07 240)",
  marginBottom: 10,
};

export const skillOrder = [
  "grammar",
  "vocabulary",
  "pronunciation",
  "fluency",
  "expression",
  "comprehension",
  "tone",
];
