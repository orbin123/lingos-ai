import { describe, expect, it } from "vitest";

import {
  SKILL_LABEL_FALLBACK,
  SKILL_ORDER,
  emptySkillScores,
  getSkillLabel,
  normalizeSkillKey,
} from "@/lib/skill-labels";

describe("getSkillLabel", () => {
  it("prefers an API override over the static fallback", () => {
    expect(getSkillLabel("expression", { expression: "Expression (API)" })).toBe(
      "Expression (API)",
    );
  });

  it("falls back to the static label when no override is given", () => {
    expect(getSkillLabel("comprehension")).toBe("Listening");
    expect(getSkillLabel("tone")).toBe("Tone & Social");
  });

  it("returns the raw key for an unknown skill", () => {
    expect(getSkillLabel("made_up_skill")).toBe("made_up_skill");
  });

  it("ignores an override that lacks the requested key", () => {
    expect(getSkillLabel("grammar", { vocabulary: "Words" })).toBe("Grammar");
  });
});

describe("normalizeSkillKey", () => {
  it("collapses spec-wording aliases to the canonical legacy key", () => {
    expect(normalizeSkillKey("thought_org")).toBe("expression");
    expect(normalizeSkillKey("listening")).toBe("comprehension");
    expect(normalizeSkillKey("tone_social")).toBe("tone");
  });

  it("collapses the long-form legacy enum alias", () => {
    expect(normalizeSkillKey("thought_organization")).toBe("expression");
  });

  it("returns canonical and unknown keys unchanged", () => {
    expect(normalizeSkillKey("grammar")).toBe("grammar");
    expect(normalizeSkillKey("nonsense")).toBe("nonsense");
  });
});

describe("emptySkillScores", () => {
  it("initialises every canonical skill to 0 in canonical order", () => {
    const scores = emptySkillScores();
    expect(Object.keys(scores)).toEqual([...SKILL_ORDER]);
    expect(Object.values(scores).every((v) => v === 0)).toBe(true);
  });
});

describe("skill metadata", () => {
  it("keeps SKILL_ORDER aligned with the fallback label keys", () => {
    expect([...SKILL_ORDER].sort()).toEqual(Object.keys(SKILL_LABEL_FALLBACK).sort());
  });
});
