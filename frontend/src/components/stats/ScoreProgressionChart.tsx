"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { SkillHistorySeries } from "@/lib/progress-api";
import {
  computeProgressionYAxis,
  loadSelectedSkills,
  normalizeSelectedSkills,
  saveSelectedSkills,
  skillColor,
} from "@/lib/progression-chart";
import { normalizeSkillKey, SKILL_ORDER } from "@/lib/skill-labels";

const T = {
  inkMuted: "oklch(45% 0.07 240)",
  line: "oklch(86% 0.025 240)",
  primary: "#0070C4",
  navy: "oklch(20% 0.09 245)",
};

function displaySkillName(name: string | null, displayLabel?: string) {
  if (displayLabel) return displayLabel;
  if (!name) return "No data yet";
  const norm = name.toLowerCase().replace(/[_&.]/g, " ").replace(/\s+/g, " ").trim();
  if (norm === "expression") return "Thought Organization";
  if (norm === "comprehension") return "Listening";
  if (norm === "tone") return "Tone & Social";
  return norm.split(" ").map((p) => p.charAt(0).toUpperCase() + p.slice(1)).join(" ");
}

function FilterIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden>
      <path
        d="M2 4h12M4.5 8h7M6.5 12h3"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

type SkillOption = {
  key: string;
  label: string;
};

function buildSkillOptions(series: SkillHistorySeries[]): SkillOption[] {
  const byKey = new Map<string, SkillOption>();
  for (const s of series) {
    const key = normalizeSkillKey(s.skill_name);
    byKey.set(key, {
      key,
      label: displaySkillName(s.skill_name, s.display_label),
    });
  }
  for (const key of SKILL_ORDER) {
    if (!byKey.has(key)) {
      byKey.set(key, { key, label: displaySkillName(key) });
    }
  }
  return SKILL_ORDER.map((key) => byKey.get(key)!);
}

export function ScoreProgressionChart({
  labels = [],
  series = [],
}: {
  labels?: string[];
  series?: SkillHistorySeries[];
}) {
  const [selectedKeys, setSelectedKeys] = useState<string[]>(() => loadSelectedSkills());
  const [pickerOpen, setPickerOpen] = useState(false);
  const pickerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    saveSelectedSkills(selectedKeys);
  }, [selectedKeys]);

  useEffect(() => {
    if (!pickerOpen) return;
    function handlePointerDown(event: PointerEvent) {
      if (!pickerRef.current?.contains(event.target as Node)) {
        setPickerOpen(false);
      }
    }
    document.addEventListener("pointerdown", handlePointerDown);
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, [pickerOpen]);

  const skillOptions = useMemo(() => buildSkillOptions(series), [series]);

  const visibleSeries = useMemo(
    () =>
      series.filter((s) =>
        selectedKeys.includes(normalizeSkillKey(s.skill_name)),
      ),
    [series, selectedKeys],
  );

  const w = 600;
  const h = 220;
  const pad = { l: 32, r: 14, t: 14, b: 28 };

  if (!series.length || !labels.length) {
    return (
      <div
        style={{
          height: 220,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: T.inkMuted,
          fontSize: 13,
        }}
      >
        Complete tasks to see score progression
      </div>
    );
  }

  const allVals = visibleSeries.flatMap((s) => s.scores);
  const { yMin, yMax, ticks } = computeProgressionYAxis(allVals);
  const xStep = labels.length > 1 ? (w - pad.l - pad.r) / (labels.length - 1) : 0;
  const yScale = (v: number) =>
    pad.t + (h - pad.t - pad.b) * (1 - (v - yMin) / (yMax - yMin));
  const xScale = (i: number) => pad.l + i * xStep;

  function toggleSkill(key: string) {
    setSelectedKeys((prev) => {
      const normalized = normalizeSkillKey(key);
      if (prev.includes(normalized)) {
        if (prev.length <= 1) return prev;
        return prev.filter((k) => k !== normalized);
      }
      if (prev.length >= 4) return prev;
      return normalizeSelectedSkills([...prev, normalized]);
    });
  }

  const atMax = selectedKeys.length >= 4;

  return (
    <div style={{ position: "relative", marginBottom: 8 }}>
      <div style={{ position: "relative", height: 220 }}>
        <svg
          width="100%"
          height={h}
          viewBox={`0 0 ${w} ${h}`}
          preserveAspectRatio="xMidYMid meet"
        >
          {ticks.map((v) => (
            <g key={v}>
              <line
                x1={pad.l}
                x2={w - pad.r}
                y1={yScale(v)}
                y2={yScale(v)}
                stroke="oklch(90% 0.02 240)"
                strokeDasharray="3 3"
              />
              <text
                x={pad.l - 8}
                y={yScale(v) + 4}
                textAnchor="end"
                fontSize="10"
                fill="oklch(50% 0.04 240)"
                fontWeight="600"
              >
                {Number.isInteger(v) ? v : v.toFixed(1)}
              </text>
            </g>
          ))}
          {labels.map((l, i) => (
            <text
              key={`${l}-${i}`}
              x={xScale(i)}
              y={h - 8}
              textAnchor="middle"
              fontSize="11"
              fill="oklch(50% 0.04 240)"
              fontWeight="600"
            >
              {l}
            </text>
          ))}
          {visibleSeries.map((s) => {
            const color = skillColor(s.skill_name);
            const path = s.scores
              .map((v, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(v)}`)
              .join(" ");
            return (
              <g key={s.skill_id}>
                <path
                  d={path}
                  fill="none"
                  stroke={color}
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                {s.scores.map((v, i) => (
                  <circle
                    key={i}
                    cx={xScale(i)}
                    cy={yScale(v)}
                    r={i === s.scores.length - 1 ? 4.5 : 3}
                    fill="white"
                    stroke={color}
                    strokeWidth="2"
                  />
                ))}
              </g>
            );
          })}
        </svg>

        <div ref={pickerRef} style={{ position: "absolute", right: 0, bottom: 0 }}>
          <button
            type="button"
            title="Choose skills to compare"
            aria-label="Choose skills to compare"
            aria-expanded={pickerOpen}
            onClick={() => setPickerOpen((open) => !open)}
            style={{
              width: 32,
              height: 32,
              borderRadius: 9,
              border: `1.5px solid ${T.line}`,
              background: "white",
              color: T.navy,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              boxShadow: "0 2px 8px rgba(80,110,180,0.12)",
            }}
          >
            <FilterIcon />
          </button>

          {pickerOpen && (
            <div
              style={{
                position: "absolute",
                right: 0,
                bottom: 40,
                width: 240,
                padding: "12px 14px",
                borderRadius: 14,
                background: "white",
                border: `1.5px solid ${T.line}`,
                boxShadow: "0 8px 28px rgba(80,110,180,0.18)",
                zIndex: 10,
              }}
            >
              <div
                style={{
                  fontSize: 12,
                  fontWeight: 700,
                  color: T.navy,
                  marginBottom: 10,
                }}
              >
                Compare up to 4 skills
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {skillOptions.map(({ key, label }) => {
                  const checked = selectedKeys.includes(key);
                  const disableUncheck = checked && selectedKeys.length <= 1;
                  const disableCheck = !checked && atMax;
                  const disabled = disableUncheck || disableCheck;
                  return (
                    <label
                      key={key}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        fontSize: 13,
                        fontWeight: 600,
                        color: disabled && !checked ? "oklch(70% 0.03 240)" : T.inkMuted,
                        cursor: disabled ? "not-allowed" : "pointer",
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={checked}
                        disabled={disabled}
                        onChange={() => toggleSkill(key)}
                        style={{ accentColor: T.primary, cursor: disabled ? "not-allowed" : "pointer" }}
                      />
                      <span
                        style={{
                          display: "inline-block",
                          width: 9,
                          height: 9,
                          borderRadius: 3,
                          background: skillColor(key),
                          flexShrink: 0,
                        }}
                      />
                      {label}
                    </label>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      <div
        style={{
          display: "flex",
          gap: 16,
          fontSize: 12,
          color: T.inkMuted,
          fontWeight: 600,
          flexWrap: "wrap",
          paddingLeft: 32,
          paddingRight: 40,
        }}
      >
        {visibleSeries.map((s) => (
          <span key={s.skill_id} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span
              style={{
                display: "inline-block",
                width: 9,
                height: 9,
                borderRadius: 3,
                background: skillColor(s.skill_name),
              }}
            />
            {displaySkillName(s.skill_name, s.display_label)}
          </span>
        ))}
      </div>
    </div>
  );
}
