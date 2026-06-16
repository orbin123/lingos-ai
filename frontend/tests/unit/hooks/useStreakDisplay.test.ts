import { describe, expect, it } from "vitest";
import { waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";

import { useStreakDisplay } from "@/hooks/useStreakDisplay";
import type { StreakData } from "@/lib/streak-api";
import { server } from "../../setup/msw/server";
import { renderHookWithProviders } from "../../utils/render";

const API = "http://localhost:8000";

function streak(overrides: Partial<StreakData>): StreakData {
  return {
    current_streak: 0,
    longest_streak: 0,
    freezes_remaining: 0,
    today_complete: false,
    today_streak_awarded: false,
    last_activity_date: null,
    last_streak_date: null,
    streak_status: "active",
    streak_state_for_ui: "STREAK_CONTINUED",
    should_show_animation: false,
    animation_type: null,
    activity_grid: [],
    ...overrides,
  } as StreakData;
}

function mockStreak(data: StreakData) {
  server.use(http.get(`${API}/api/streak/me`, () => HttpResponse.json(data)));
}

describe("useStreakDisplay", () => {
  it("derives streak/best/frozen/todayComplete from the API payload", async () => {
    mockStreak(
      streak({ current_streak: 3, longest_streak: 5, today_complete: true }),
    );

    const { result } = renderHookWithProviders(() => useStreakDisplay());

    await waitFor(() => expect(result.current.streak).toBe(3));
    expect(result.current.best).toBe(5);
    expect(result.current.frozen).toBe(false);
    expect(result.current.todayComplete).toBe(true);
    expect(result.current.celebrationVariant).toBe("default");
  });

  it("flags a frozen streak", async () => {
    mockStreak(streak({ current_streak: 4, streak_status: "frozen" }));

    const { result } = renderHookWithProviders(() => useStreakDisplay());

    await waitFor(() => expect(result.current.frozen).toBe(true));
  });

  it("uses the on_fire celebration variant for a 10+ on_fire streak", async () => {
    mockStreak(
      streak({
        current_streak: 12,
        should_show_animation: true,
        animation_type: "on_fire",
      }),
    );

    const { result } = renderHookWithProviders(() => useStreakDisplay());

    await waitFor(() => expect(result.current.showAutoCelebration).toBe(true));
    expect(result.current.autoAnimationType).toBe("on_fire");
    expect(result.current.celebrationVariant).toBe("on_fire");
  });

  it("stays on the default variant for an on_fire animation below 10", async () => {
    mockStreak(
      streak({
        current_streak: 6,
        should_show_animation: true,
        animation_type: "on_fire",
      }),
    );

    const { result } = renderHookWithProviders(() => useStreakDisplay());

    await waitFor(() => expect(result.current.showAutoCelebration).toBe(true));
    expect(result.current.celebrationVariant).toBe("default");
  });
});
