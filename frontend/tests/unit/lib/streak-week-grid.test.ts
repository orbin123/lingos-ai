import { describe, expect, it } from "vitest";

import type { ActivityGridCell } from "@/lib/streak-api";
import {
  buildLastSevenDays,
  buildPreviewWeekDays,
} from "@/lib/streak-week-grid";

function cell(
  date: string,
  overrides: Partial<ActivityGridCell> = {},
): ActivityGridCell {
  return {
    date,
    activity_count: 0,
    completed: false,
    intensity: 0,
    frozen_protected: false,
    ...overrides,
  };
}

describe("buildLastSevenDays", () => {
  const grid: ActivityGridCell[] = [
    cell("2026-06-18"),
    cell("2026-06-19"),
    cell("2026-06-20"),
    cell("2026-06-21", { completed: true }),
    cell("2026-06-22"),
    cell("2026-06-23", { completed: true }),
    cell("2026-06-24", { completed: true }),
  ];

  it("maps the last 7 grid cells to weekday letters and day-of-month numbers", () => {
    const days = buildLastSevenDays(grid, "2026-06-24");

    expect(days).toHaveLength(7);
    expect(days.map((d) => d.n)).toEqual([18, 19, 20, 21, 22, 23, 24]);
    expect(days.map((d) => d.d)).toEqual(["T", "F", "S", "S", "M", "T", "W"]);
    expect(days.map((d) => d.date)).toEqual([
      "2026-06-18",
      "2026-06-19",
      "2026-06-20",
      "2026-06-21",
      "2026-06-22",
      "2026-06-23",
      "2026-06-24",
    ]);
  });

  it("marks completed non-today cells as done", () => {
    const days = buildLastSevenDays(grid, "2026-06-24");

    expect(days[3].st).toBe("done");
    expect(days[5].st).toBe("done");
  });

  it("marks an incomplete today as today", () => {
    const incompleteToday = grid.map((c) =>
      c.date === "2026-06-24" ? { ...c, completed: false } : c,
    );
    const days = buildLastSevenDays(incompleteToday, "2026-06-24");

    expect(days[6].st).toBe("today");
    expect(days[6].isToday).toBe(true);
  });

  it("marks a completed today as done while keeping isToday", () => {
    const days = buildLastSevenDays(grid, "2026-06-24");

    expect(days[6].st).toBe("done");
    expect(days[6].isToday).toBe(true);
  });

  it("marks frozen-protected cells as frozen", () => {
    const frozenGrid = grid.map((c) =>
      c.date === "2026-06-22"
        ? { ...c, frozen_protected: true, completed: false }
        : c,
    );
    const days = buildLastSevenDays(frozenGrid, "2026-06-24");

    expect(days[4].st).toBe("frozen");
  });

  it("parses YYYY-MM-DD in local time without UTC drift", () => {
    const days = buildLastSevenDays([cell("2026-06-24")], "2026-06-24");

    expect(days[0].n).toBe(24);
  });

  it("only uses the trailing 7 cells from a longer grid", () => {
    const longGrid = Array.from({ length: 91 }, (_, i) =>
      cell(`2026-03-${String((i % 28) + 1).padStart(2, "0")}`),
    );
    longGrid.splice(-7, 7, ...grid);

    const days = buildLastSevenDays(longGrid, "2026-06-24");

    expect(days.map((d) => d.n)).toEqual([18, 19, 20, 21, 22, 23, 24]);
  });
});

describe("buildPreviewWeekDays", () => {
  it("returns 7 days ending at local today", () => {
    const days = buildPreviewWeekDays();
    const today = new Date();

    expect(days).toHaveLength(7);
    expect(days[6].isToday).toBe(true);
    expect(days[6].n).toBe(today.getDate());
  });
});
