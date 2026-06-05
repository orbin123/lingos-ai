import { normalizeSkillKey, SKILL_ORDER } from "@/lib/skill-labels";

export const DEFAULT_PROGRESSION_SKILLS: readonly string[] = [
  "pronunciation",
  "grammar",
  "vocabulary",
  "fluency",
];

export const PROGRESSION_STORAGE_KEY = "stats:progression-skills";

export const SKILL_COLORS: Record<string, string> = {
  grammar: "#0070C4",
  vocabulary: "#7c3aed",
  pronunciation: "#ef4444",
  fluency: "#10b981",
  expression: "#f59e0b",
  comprehension: "#06b6d4",
  tone: "#ec4899",
};

const VALID_KEYS = new Set(SKILL_ORDER);

function roundHalf(n: number): number {
  return Math.round(n * 2) / 2;
}

export function skillColor(name: string): string {
  return SKILL_COLORS[normalizeSkillKey(name)] ?? "#888";
}

export function normalizeSelectedSkills(keys: string[]): string[] {
  const seen = new Set<string>();
  const normalized: string[] = [];
  for (const key of keys) {
    const canonical = normalizeSkillKey(key);
    if (!VALID_KEYS.has(canonical) || seen.has(canonical)) continue;
    seen.add(canonical);
    normalized.push(canonical);
    if (normalized.length >= 4) break;
  }
  return normalized;
}

export function loadSelectedSkills(): string[] {
  if (typeof window === "undefined") {
    return [...DEFAULT_PROGRESSION_SKILLS];
  }
  try {
    const raw = localStorage.getItem(PROGRESSION_STORAGE_KEY);
    if (!raw) return [...DEFAULT_PROGRESSION_SKILLS];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [...DEFAULT_PROGRESSION_SKILLS];
    const normalized = normalizeSelectedSkills(parsed.map(String));
    if (normalized.length === 0) return [...DEFAULT_PROGRESSION_SKILLS];
    return normalized;
  } catch {
    return [...DEFAULT_PROGRESSION_SKILLS];
  }
}

export function saveSelectedSkills(keys: string[]): void {
  if (typeof window === "undefined") return;
  const normalized = normalizeSelectedSkills(keys);
  if (normalized.length === 0) return;
  localStorage.setItem(PROGRESSION_STORAGE_KEY, JSON.stringify(normalized));
}

export function computeProgressionYAxis(
  values: number[],
): { yMin: number; yMax: number; ticks: number[] } {
  if (values.length === 0) {
    return { yMin: 1.5, yMax: 3.0, ticks: [1.5, 2.0, 2.5, 3.0] };
  }

  const dataMin = Math.min(...values);
  const dataMax = Math.max(...values);

  let yMin = 0.0;
  let yMax = 10.0;
  let ticks: number[] = [0.0, 3.3, 6.7, 10.0];

  if (dataMax <= 3.0) {
    yMax = 3.0;
    if (dataMin >= 1.5) {
      yMin = 1.5;
      ticks = [1.5, 2.0, 2.5, 3.0];
    } else {
      yMin = 0.0;
      ticks = [0.0, 1.0, 2.0, 3.0];
    }
  } else if (dataMax <= 6.0) {
    yMax = 6.0;
    if (dataMin >= 3.0) {
      yMin = 3.0;
      ticks = [3.0, 4.0, 5.0, 6.0];
    } else {
      yMin = 0.0;
      ticks = [0.0, 2.0, 4.0, 6.0];
    }
  } else {
    yMax = 10.0;
    if (dataMin >= 7.0) {
      yMin = 7.0;
      ticks = [7.0, 8.0, 9.0, 10.0];
    } else if (dataMin >= 4.0) {
      yMin = 4.0;
      ticks = [4.0, 6.0, 8.0, 10.0];
    } else if (dataMin >= 1.0) {
      yMin = 1.0;
      ticks = [1.0, 4.0, 7.0, 10.0];
    } else {
      yMin = 0.0;
      ticks = [0.0, 3.3, 6.7, 10.0];
    }
  }

  return { yMin, yMax, ticks };
}
