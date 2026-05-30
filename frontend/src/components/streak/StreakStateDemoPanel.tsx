"use client";

import { Play } from "lucide-react";
import { STREAK_DEMO_PRESETS } from "@/components/streak/streak-demo-presets";
import { useStreakDemoStore } from "@/store/streakDemoStore";

export function StreakStateDemoPanel() {
  const selectedPresetId = useStreakDemoStore((s) => s.selectedPresetId);
  const setPreset = useStreakDemoStore((s) => s.setPreset);
  const requestPlay = useStreakDemoStore((s) => s.requestPlay);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 12,
        right: 12,
        zIndex: 50,
        width: 220,
        background: "white",
        borderRadius: 14,
        border: "1.5px solid oklch(88% 0.025 240)",
        boxShadow: "0 8px 28px rgba(40,80,150,0.14)",
        padding: "12px 12px 10px",
        fontFamily: "inherit",
      }}
    >
      <div
        style={{
          fontSize: 10,
          fontWeight: 800,
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          color: "oklch(35% 0.1 245)",
          marginBottom: 10,
        }}
      >
        Streak state demo
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {STREAK_DEMO_PRESETS.map((preset) => {
          const selected = selectedPresetId === preset.id;
          return (
            <button
              key={preset.id}
              type="button"
              onClick={() => setPreset(preset.id)}
              style={{
                display: "block",
                width: "100%",
                textAlign: "left",
                padding: "8px 10px",
                borderRadius: 8,
                border: "none",
                cursor: "pointer",
                fontFamily: "inherit",
                fontSize: 12.5,
                fontWeight: selected ? 700 : 500,
                color: selected ? "oklch(25% 0.1 245)" : "oklch(40% 0.07 240)",
                background: selected
                  ? "oklch(94% 0.04 230)"
                  : "transparent",
                transition: "background 0.12s",
              }}
            >
              {preset.label}
            </button>
          );
        })}
      </div>

      <button
        type="button"
        onClick={() => {
          if (!selectedPresetId) {
            setPreset(STREAK_DEMO_PRESETS[0].id);
          }
          requestPlay();
        }}
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 6,
          width: "100%",
          marginTop: 10,
          padding: "10px 12px",
          borderRadius: 10,
          border: "none",
          cursor: "pointer",
          fontFamily: "inherit",
          fontSize: 12.5,
          fontWeight: 800,
          color: "white",
          background: "linear-gradient(135deg, #ff7a18, #ffb547)",
          boxShadow: "0 2px 8px rgba(255,122,24,0.35)",
        }}
      >
        <Play size={14} fill="white" strokeWidth={0} />
        Play streak animation
      </button>

      {selectedPresetId !== null && (
        <button
          type="button"
          onClick={() => setPreset(null)}
          style={{
            display: "block",
            width: "100%",
            marginTop: 8,
            padding: "4px 0",
            border: "none",
            background: "transparent",
            cursor: "pointer",
            fontFamily: "inherit",
            fontSize: 11,
            fontWeight: 600,
            color: "oklch(50% 0.06 240)",
            textDecoration: "underline",
            textUnderlineOffset: 2,
          }}
        >
          Use live data
        </button>
      )}
    </div>
  );
}
