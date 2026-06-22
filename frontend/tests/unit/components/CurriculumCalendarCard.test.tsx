import { describe, expect, it } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import { CurriculumCalendarCard } from "@/components/dashboard/CurriculumCalendarCard";
import type { UserCoursePreferenceRead } from "@/lib/preferences-api";
import { routerMock } from "../../setup/router-mock";

function makePreference(
  overrides: Partial<UserCoursePreferenceRead> = {},
): UserCoursePreferenceRead {
  return {
    course_length: "24w",
    tasks_per_day: 2,
    allow_read: true,
    allow_write: true,
    allow_listen: true,
    allow_speak: true,
    current_week: 1,
    current_day_in_week: 3,
    current_day_started_at: "2026-01-01T00:00:00Z",
    last_completed_on: null,
    course_completed_at: null,
    require_pass_to_advance: false,
    pass_threshold_pct: 65,
    ...overrides,
  };
}

describe("CurriculumCalendarCard", () => {
  it("in-progress: marks the active day, completed past days, and leaves cells static", () => {
    render(<CurriculumCalendarCard preference={makePreference()} />);

    expect(screen.getByTitle("Week 1, Day 3 (Active Day)")).toBeInTheDocument();
    expect(screen.getByTitle("Week 1, Day 1 (Completed)")).toBeInTheDocument();
    // A future day carries no status suffix and is not a review button.
    expect(screen.getByTitle("Week 1, Day 5")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Review/ })).not.toBeInTheDocument();
  });

  it("when complete: every day becomes a review button and none is the active day", () => {
    render(
      <CurriculumCalendarCard
        preference={makePreference({ course_completed_at: "2026-06-22T10:00:00Z" })}
      />,
    );

    // No pulsing "active day" once finished.
    expect(screen.queryByTitle(/Active Day/)).not.toBeInTheDocument();
    // Cells are now review entry points.
    expect(
      screen.getByRole("button", { name: "Review Week 1, Day 5" }),
    ).toBeInTheDocument();
  });

  it("clicking a day in review mode routes to the preview path without advancing", () => {
    render(
      <CurriculumCalendarCard
        preference={makePreference({ course_completed_at: "2026-06-22T10:00:00Z" })}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Review Week 2, Day 4" }));

    expect(routerMock.push).toHaveBeenCalledWith("/dashboard?week=2&day=4");
  });
});
