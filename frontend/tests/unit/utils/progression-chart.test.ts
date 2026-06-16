import { describe, expect, it } from "vitest";

import {
  computeProgressionYAxis,
  DEFAULT_PROGRESSION_SKILLS,
  normalizeSelectedSkills,
  skillColor,
} from "@/lib/progression-chart";

// Migrated from tests/progression-chart.test.mjs. The old snapshot expected a
// 3-tick axis and different yMin banding — STALE vs the real implementation
// (which returns four ticks). These assertions track the real source.
describe("computeProgressionYAxis", () => {
  it("returns four ticks anchored at yMin and yMax", () => {
    const axis = computeProgressionYAxis([2.1, 2.3, 2.4]);
    expect(axis.ticks).toHaveLength(4);
    expect(axis.ticks[0]).toBe(axis.yMin);
    expect(axis.ticks[axis.ticks.length - 1]).toBe(axis.yMax);
  });

  it("zooms into the low band (no zero tick) when min >= 1.5", () => {
    const axis = computeProgressionYAxis([1.8, 2.1, 2.5]);
    expect(axis.yMin).toBe(1.5);
    expect(axis.yMax).toBe(3);
    expect(axis.ticks).toEqual([1.5, 2.0, 2.5, 3.0]);
    expect(axis.ticks.every((tick) => tick > 0)).toBe(true);
  });

  it("uses the 0-6 band when max <= 6 but min < 3", () => {
    const axis = computeProgressionYAxis([2.4, 3.8, 5.2]);
    expect(axis.yMin).toBe(0);
    expect(axis.yMax).toBe(6);
    expect(axis.ticks).toEqual([0, 2, 4, 6]);
  });

  it("shifts to the 4-10 band once a score exceeds six", () => {
    const axis = computeProgressionYAxis([4.5, 6.2, 7.1]);
    expect(axis.yMin).toBe(4);
    expect(axis.yMax).toBe(10);
    expect(axis.ticks).toEqual([4, 6, 8, 10]);
  });

  it("falls back to a default axis for empty input", () => {
    expect(computeProgressionYAxis([])).toEqual({
      yMin: 1.5,
      yMax: 3.0,
      ticks: [1.5, 2.0, 2.5, 3.0],
    });
  });
});

describe("normalizeSelectedSkills", () => {
  it("keeps at most four known keys, preserving order", () => {
    expect(
      normalizeSelectedSkills([
        "grammar",
        "vocabulary",
        "pronunciation",
        "fluency",
        "tone",
        "unknown",
      ]),
    ).toEqual(["grammar", "vocabulary", "pronunciation", "fluency"]);
  });

  it("dedupes aliases that normalize to the same canonical key", () => {
    expect(
      normalizeSelectedSkills(["expression", "thought_org", "grammar"]),
    ).toEqual(["expression", "grammar"]);
  });

  it("drops unknown keys entirely", () => {
    expect(normalizeSelectedSkills(["nonsense", "grammar"])).toEqual(["grammar"]);
  });
});

describe("skill metadata", () => {
  it("exposes the core four default progression skills", () => {
    expect(DEFAULT_PROGRESSION_SKILLS).toEqual([
      "pronunciation",
      "grammar",
      "vocabulary",
      "fluency",
    ]);
  });

  it("resolves canonical and aliased skill colors", () => {
    expect(skillColor("pronunciation")).toBe("#ef4444");
    expect(skillColor("thought_org")).toBe("#f59e0b");
    expect(skillColor("totally-unknown")).toBe("#888");
  });
});
