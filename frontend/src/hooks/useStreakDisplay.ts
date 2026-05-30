"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  getStreakDemoPreset,
  type StreakDisplaySnapshot,
} from "@/components/streak/streak-demo-presets";
import { streakApi, type AnimationType, type StreakData } from "@/lib/streak-api";
import { useStreakDemoStore } from "@/store/streakDemoStore";

export interface StreakDisplay {
  streak: number;
  best: number;
  frozen: boolean;
  todayComplete: boolean;
  /** Live API data for popover week grid — never overridden by demo */
  apiData: StreakData | undefined;
  isDemo: boolean;
  /** Snapshot when a demo preset is selected */
  demoSnapshot: StreakDisplaySnapshot | null;
  /** Auto-play from API (live mode only) */
  showAutoCelebration: boolean;
  autoAnimationType: AnimationType | null;
  /** on_fire variant for continued streak celebrations */
  celebrationVariant: "default" | "on_fire";
  refetch: () => void;
}

export function useStreakDisplay(): StreakDisplay {
  const selectedPresetId = useStreakDemoStore((s) => s.selectedPresetId);

  const { data, refetch } = useQuery<StreakData>({
    queryKey: ["streak", "me"],
    queryFn: streakApi.getMe,
    refetchOnWindowFocus: false,
  });

  const preset = selectedPresetId
    ? getStreakDemoPreset(selectedPresetId)
    : undefined;

  return useMemo(() => {
    const isDemo = preset !== undefined;

    if (isDemo && preset) {
      const s = preset.snapshot;
      return {
        streak: s.streak,
        best: s.best,
        frozen: s.frozen,
        todayComplete: s.todayComplete,
        apiData: data,
        isDemo: true,
        demoSnapshot: s,
        showAutoCelebration: false,
        autoAnimationType: null,
        celebrationVariant: s.variant ?? "default",
        refetch: () => {
          void refetch();
        },
      };
    }

    const streak = data?.current_streak ?? 0;
    const best = data?.longest_streak ?? 0;
    const frozen = data?.streak_status === "frozen";
    const showAutoCelebration =
      !!data && data.should_show_animation && !!data.animation_type;
    const autoType = showAutoCelebration ? data!.animation_type : null;
    const celebrationVariant: "default" | "on_fire" =
      autoType === "on_fire" && streak >= 10 ? "on_fire" : "default";

    return {
      streak,
      best,
      frozen,
      todayComplete: data?.today_complete ?? false,
      apiData: data,
      isDemo: false,
      demoSnapshot: null,
      showAutoCelebration,
      autoAnimationType: autoType,
      celebrationVariant,
      refetch: () => {
        void refetch();
      },
    };
  }, [data, preset, refetch]);
}
