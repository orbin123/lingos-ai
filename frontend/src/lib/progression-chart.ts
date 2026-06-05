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
): { yMin: number; yMax: number; ticks: [number, number, number] } {
  if (values.length === 0) {
    return { yMin: 1, yMax: 3, ticks: [1, 2, 3] };
  }

  const dataMin = Math.min(...values);
  const dataMax = Math.max(...values);

  let yMax: number;
  let yMin: number;

  if (dataMax <= 3) {
    yMax = 3;
    yMin = roundHalf(Math.max(0, dataMin - 0.5));
  } else if (dataMax <= 6) {
    yMin = 2;
    yMax = 6;
  } else {
    yMax = Math.min(10, roundHalf(Math.ceil((dataMax + 0.5) / 2) * 2));
    yMin = Math.max(0, yMax - 4);
  }

  if (dataMin < yMin) yMin = roundHalf(Math.floor(dataMin * 2) / 2);
  if (dataMax > yMax) yMax = roundHalf(Math.ceil(dataMax * 2) / 2);

  if (values.every((v) => v > 0.5) && yMin === 0) {
    yMin = 0.5;
  }

  if (yMax - yMin < 1) {
    const mid = (dataMin + dataMax) / 2;
    yMin = roundHalf(Math.max(0, mid - 0.5));
    yMax = roundHalf(mid + 0.5);
    if (values.every((v) => v > 0.5) && yMin === 0) yMin = 0.5;
  }

  const midTick = roundHalf((yMin + yMax) / 2);
  return { yMin, yMax, ticks: [yMin, midTick, yMax] };
}
