"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { streakApi, type AnimationType, type StreakData } from "@/lib/streak-api";

export interface StreakDisplay {
  streak: number;
  best: number;
  frozen: boolean;
  todayComplete: boolean;
  /** Live API data for popover week grid */
  apiData: StreakData | undefined;
  /** Auto-play from API */
  showAutoCelebration: boolean;
  autoAnimationType: AnimationType | null;
  /** on_fire variant for continued streak celebrations */
  celebrationVariant: "default" | "on_fire";
  refetch: () => void;
}

export function useStreakDisplay(): StreakDisplay {
  const { data, refetch } = useQuery<StreakData>({
    queryKey: ["streak", "me"],
    queryFn: streakApi.getMe,
    refetchOnWindowFocus: false,
  });

  return useMemo(() => {
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
      showAutoCelebration,
      autoAnimationType: autoType,
      celebrationVariant,
      refetch: () => {
        void refetch();
      },
    };
  }, [data, refetch]);
}
