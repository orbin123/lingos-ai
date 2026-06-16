import { describe, expect, it } from "vitest";

import {
  fillBlankSchema,
  readAloudSchema,
  selfAssessmentSchema,
  writingSchema,
} from "@/lib/validators/diagnosis";

describe("selfAssessmentSchema", () => {
  const base = {
    self_assessed_level: "beginner",
    goal: "casual",
    daily_time_minutes: 30,
    content_exposure: "low",
    interests: ["movies"],
  };

  it("accepts a valid self-assessment", () => {
    expect(selfAssessmentSchema.safeParse(base).success).toBe(true);
  });

  it("coerces a numeric string for daily_time_minutes", () => {
    const r = selfAssessmentSchema.safeParse({ ...base, daily_time_minutes: "45" });
    expect(r.success).toBe(true);
    if (r.success) expect(r.data.daily_time_minutes).toBe(45);
  });

  it("rejects times below 5 or above 240 minutes", () => {
    expect(selfAssessmentSchema.safeParse({ ...base, daily_time_minutes: 4 }).success).toBe(false);
    expect(selfAssessmentSchema.safeParse({ ...base, daily_time_minutes: 241 }).success).toBe(false);
  });

  it("rejects an unknown enum value", () => {
    expect(selfAssessmentSchema.safeParse({ ...base, goal: "fluent-by-friday" }).success).toBe(false);
  });

  it("caps interests at 3", () => {
    expect(
      selfAssessmentSchema.safeParse({ ...base, interests: ["a", "b", "c", "d"] }).success,
    ).toBe(false);
  });
});

describe("fillBlankSchema", () => {
  it("requires exactly 5 non-empty answers", () => {
    expect(fillBlankSchema.safeParse({ answers: ["a", "b", "c", "d", "e"] }).success).toBe(true);
    expect(fillBlankSchema.safeParse({ answers: ["a", "b", "c", "d"] }).success).toBe(false);
    expect(fillBlankSchema.safeParse({ answers: ["a", "", "c", "d", "e"] }).success).toBe(false);
  });
});

describe("writingSchema", () => {
  it("requires 10–2000 characters", () => {
    expect(writingSchema.safeParse({ response_text: "x".repeat(10) }).success).toBe(true);
    expect(writingSchema.safeParse({ response_text: "too short" }).success).toBe(false);
    expect(writingSchema.safeParse({ response_text: "x".repeat(2001) }).success).toBe(false);
  });
});

describe("readAloudSchema", () => {
  const scores = {
    overall_score: 80,
    accuracy_score: 80,
    fluency_score: 80,
    completeness_score: 80,
    prosody_score: 80,
  };

  it("accepts a non-empty Blob with valid scores (words defaults to [])", () => {
    const r = readAloudSchema.safeParse({ audioBlob: new Blob(["audio"]), ...scores });
    expect(r.success).toBe(true);
    if (r.success) expect(r.data.words).toEqual([]);
  });

  it("rejects an empty recording", () => {
    const r = readAloudSchema.safeParse({ audioBlob: new Blob([]), ...scores });
    expect(r.success).toBe(false);
  });

  it("rejects out-of-range scores", () => {
    expect(
      readAloudSchema.safeParse({ audioBlob: new Blob(["a"]), ...scores, overall_score: 101 })
        .success,
    ).toBe(false);
  });
});
