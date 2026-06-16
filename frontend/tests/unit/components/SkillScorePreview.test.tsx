import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";

import { SkillScorePreview } from "@/components/dashboard/SkillScorePreview";
import { renderWithProviders } from "../../utils/render";

describe("SkillScorePreview", () => {
  it("renders every known sub-skill with its fallback label and formats scores", () => {
    renderWithProviders(
      <SkillScorePreview scores={{ grammar: 7, expression: 6.4 }} />,
    );

    // All seven canonical skills always render, even at score 0.
    expect(screen.getByText("Grammar")).toBeInTheDocument();
    expect(screen.getByText("Thought Organization")).toBeInTheDocument(); // expression
    expect(screen.getByText("Listening")).toBeInTheDocument(); // comprehension
    expect(screen.getByText("Tone & Social")).toBeInTheDocument(); // tone

    // Scores are fixed to one decimal place.
    expect(screen.getByText("7.0")).toBeInTheDocument();
    expect(screen.getByText("6.4")).toBeInTheDocument();
    // Skills with no score default to 0.0 (e.g. vocabulary, pronunciation…).
    expect(screen.getAllByText("0.0").length).toBeGreaterThan(0);
  });

  it("prefers API-provided labels and tail-appends unknown skills", () => {
    renderWithProviders(
      <SkillScorePreview
        scores={{ grammar: 5, future_skill: 9 }}
        labels={{ grammar: "Grammar (live)", future_skill: "Future Skill" }}
      />,
    );

    // Override beats the static fallback.
    expect(screen.getByText("Grammar (live)")).toBeInTheDocument();
    expect(screen.queryByText("Grammar")).not.toBeInTheDocument();

    // A key outside SKILL_ORDER still renders (defensive tail-append).
    expect(screen.getByText("Future Skill")).toBeInTheDocument();
    expect(screen.getByText("9.0")).toBeInTheDocument();
  });
});
