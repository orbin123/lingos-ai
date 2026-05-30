import { api } from "./api";

export type AnimationType =
  | "rekindle"
  | "on_fire"
  | "frozen_to_fire"
  | "frozen";

export type StreakStatus = "new" | "active" | "frozen" | "broken";

export type StreakState =
  | "NO_STREAK_YET"
  | "FIRST_STREAK_EARNED"
  | "STREAK_ALREADY_COMPLETED_TODAY"
  | "STREAK_CONTINUED"
  | "STREAK_FROZEN"
  | "STREAK_RESET"
  | "INACTIVE_TODAY";

export interface ActivityGridCell {
  date: string;
  activity_count: number;
  completed: boolean;
  intensity: 0 | 1 | 2 | 3 | 4;
  frozen_protected: boolean;
}

export interface StreakData {
  current_streak: number;
  longest_streak: number;
  freezes_remaining: number;
  today_complete: boolean;
  today_streak_awarded: boolean;
  last_activity_date: string | null;
  last_streak_date: string | null;
  streak_status: StreakStatus;
  streak_state_for_ui: StreakState;
  should_show_animation: boolean;
  animation_type: AnimationType | null;
  activity_grid: ActivityGridCell[];
  timezone: string;
}

export const streakApi = {
  getMe: () => api.get<StreakData>("/api/streak/me").then((r) => r.data),
  markAnimationSeen: () =>
    api.patch<StreakData>("/api/streak/animation-seen").then((r) => r.data),
};
