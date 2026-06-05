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

function ChevronDownIcon({ open }: { open: boolean }) {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 12 12"
      fill="none"
      style={{
        transform: open ? "rotate(180deg)" : "rotate(0deg)",
        transition: "transform 0.15s ease",
      }}
    >
      <path
        d="M2.5 4.5L6 8L9.5 4.5"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
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
  const h = 260;
  const pad = { l: 42, r: 22, t: 20, b: 34 };

  if (!series.length || !labels.length) {
    return (
      <div
        style={{
          height: 260,
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
      <div style={{ position: "relative", height: h }}>
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
                stroke="oklch(93% 0.015 240)"
                strokeDasharray="4 4"
              />
              <text
                x={pad.l - 8}
                y={yScale(v) + 4}
                textAnchor="end"
                fontSize="12"
                fill="oklch(40% 0.05 240)"
                fontWeight="700"
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
              fontSize="12"
              fill="oklch(40% 0.05 240)"
              fontWeight="700"
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
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginTop: 16,
          paddingLeft: pad.l,
          paddingRight: pad.r,
          gap: 16,
          flexWrap: "wrap",
        }}
      >
        {/* Legend */}
        <div
          style={{
            display: "flex",
            gap: "10px 16px",
            fontSize: 12,
            color: T.inkMuted,
            fontWeight: 600,
            flexWrap: "wrap",
            alignItems: "center",
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

        {/* Options Button and Selection Popover */}
        <div ref={pickerRef} style={{ position: "relative" }}>
          <button
            type="button"
            title="Choose skills to compare"
            aria-label="Choose skills to compare"
            aria-expanded={pickerOpen}
            onClick={() => setPickerOpen((open) => !open)}
            style={{
              height: 32,
              borderRadius: 999,
              border: `1.5px solid ${T.line}`,
              background: "white",
              color: T.navy,
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "0 12px 0 10px",
              cursor: "pointer",
              fontSize: 12,
              fontWeight: 700,
              boxShadow: "0 2px 6px rgba(80,110,180,0.08)",
              transition: "all 0.15s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = T.primary;
              e.currentTarget.style.background = "oklch(99% 0.005 240)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = T.line;
              e.currentTarget.style.background = "white";
            }}
          >
            <FilterIcon />
            <span>Compare Skills</span>
            <ChevronDownIcon open={pickerOpen} />
          </button>

          {pickerOpen && (
            <div
              style={{
                position: "absolute",
                right: 0,
                bottom: "calc(100% + 8px)",
                width: 260,
                padding: "16px 14px",
                borderRadius: 16,
                background: "white",
                border: `1.5px solid ${T.line}`,
                boxShadow: "0 12px 32px rgba(40,80,150,0.18)",
                zIndex: 100,
              }}
            >
              <div
                style={{
                  fontSize: 13,
                  fontWeight: 800,
                  color: T.navy,
                  marginBottom: 2,
                }}
              >
                Compare sub-skills
              </div>
              <div
                style={{
                  fontSize: 11.5,
                  fontWeight: 500,
                  color: T.inkMuted,
                  marginBottom: 12,
                }}
              >
                Select up to 4 ({selectedKeys.length}/4 selected)
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
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
                        justifyContent: "space-between",
                        padding: "6px 8px",
                        borderRadius: 8,
                        fontSize: 12.5,
                        fontWeight: 600,
                        color: disabled && !checked ? "oklch(70% 0.03 240)" : T.navy,
                        cursor: disabled ? "not-allowed" : "pointer",
                        background: checked ? "oklch(97% 0.01 240)" : "transparent",
                        transition: "all 0.12s",
                      }}
                      onMouseEnter={e => {
                        if (!disabled) e.currentTarget.style.background = checked ? "oklch(95% 0.018 240)" : "oklch(97% 0.01 240)";
                      }}
                      onMouseLeave={e => {
                        if (!disabled) e.currentTarget.style.background = checked ? "oklch(97% 0.01 240)" : "transparent";
                      }}
                    >
                      <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span
                          style={{
                            display: "inline-block",
                            width: 8,
                            height: 8,
                            borderRadius: "50%",
                            background: skillColor(key),
                            flexShrink: 0,
                          }}
                        />
                        {label}
                      </span>
                      <input
                        type="checkbox"
                        checked={checked}
                        disabled={disabled}
                        onChange={() => toggleSkill(key)}
                        style={{
                          accentColor: T.primary,
                          cursor: disabled ? "not-allowed" : "pointer",
                          width: 14,
                          height: 14,
                        }}
                      />
                    </label>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
