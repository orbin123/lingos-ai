import type { AnimationType } from "@/lib/streak-api";

export type StreakPillMode = "fire" | "frozen";

export type StreakCelebrationVariant = "default" | "on_fire";

export interface StreakDisplaySnapshot {
  streak: number;
  best: number;
  frozen: boolean;
  todayComplete: boolean;
  animationType: AnimationType;
  variant?: StreakCelebrationVariant;
}

export interface StreakDemoPreset {
  id: string;
  label: string;
  snapshot: StreakDisplaySnapshot;
}

export const STREAK_DEMO_PRESETS: StreakDemoPreset[] = [
  {
    id: "fire-5",
    label: "Fire (5-day streak)",
    snapshot: {
      streak: 5,
      best: 21,
      frozen: false,
      todayComplete: true,
      animationType: "on_fire",
      variant: "default",
    },
  },
  {
    id: "on-fire-12",
    label: "On fire (12 days)",
    snapshot: {
      streak: 12,
      best: 21,
      frozen: false,
      todayComplete: true,
      animationType: "on_fire",
      variant: "on_fire",
    },
  },
  {
    id: "frozen-0",
    label: "Frozen (missed days)",
    snapshot: {
      streak: 5,
      best: 21,
      frozen: true,
      todayComplete: false,
      animationType: "frozen",
      variant: "default",
    },
  },
  {
    id: "rekindled-1",
    label: "Just rekindled (1 day)",
    snapshot: {
      streak: 1,
      best: 21,
      frozen: false,
      todayComplete: true,
      animationType: "rekindle",
      variant: "default",
    },
  },
  {
    id: "frozen-to-fire",
    label: "Frozen → fire (return)",
    snapshot: {
      streak: 1,
      best: 21,
      frozen: false,
      todayComplete: true,
      animationType: "frozen_to_fire",
      variant: "default",
    },
  },
];

export function getStreakDemoPreset(id: string): StreakDemoPreset | undefined {
  return STREAK_DEMO_PRESETS.find((p) => p.id === id);
}
