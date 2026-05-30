import { create } from "zustand";

interface StreakDemoState {
  /** null = use live API streak data */
  selectedPresetId: string | null;
  /** Incremented on Play to re-trigger the celebration overlay */
  playNonce: number;
  setPreset: (id: string | null) => void;
  requestPlay: () => void;
}

export const useStreakDemoStore = create<StreakDemoState>((set) => ({
  selectedPresetId: null,
  playNonce: 0,
  setPreset: (id) => set({ selectedPresetId: id }),
  requestPlay: () => set((s) => ({ playNonce: s.playNonce + 1 })),
}));
