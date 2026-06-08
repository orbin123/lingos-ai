"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { UserCoursePreferenceRead } from "@/lib/preferences-api";

interface CurriculumCalendarCardProps {
  preference: UserCoursePreferenceRead;
}

export function CurriculumCalendarCard({ preference }: CurriculumCalendarCardProps) {
  // Parse active progress
  const totalWeeks = preference.course_length === "48w" ? 48 : 24;
  const totalMonths = totalWeeks / 4;
  const activeMonth = Math.floor((preference.current_week - 1) / 4) + 1;

  // Selected month state
  const [selectedMonth, setSelectedMonth] = useState(activeMonth);

  // Sync selected month to the active progress week if it updates (render-time state adjustment)
  const [prevActiveMonth, setPrevActiveMonth] = useState(activeMonth);
  if (activeMonth !== prevActiveMonth) {
    setPrevActiveMonth(activeMonth);
    setSelectedMonth(activeMonth);
  }

  return (
    <div
      style={{
        background: "white",
        borderRadius: 16,
        border: "1px solid oklch(90% 0.025 240)",
        padding: 18,
        boxShadow: "0 1px 2px oklch(20% 0.05 240 / 0.04)",
      }}
    >
      <style>{`
        @keyframes pulseGlow {
          0% { box-shadow: 0 0 0 0px rgba(255, 122, 24, 0.4); }
          70% { box-shadow: 0 0 0 6px rgba(255, 122, 24, 0); }
          100% { box-shadow: 0 0 0 0px rgba(255, 122, 24, 0); }
        }
      `}</style>

      {/* Header section with month pagination */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: 16,
          gap: 8,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 17,
              fontWeight: 800,
              color: "oklch(20% 0.09 245)",
              letterSpacing: "-0.01em",
            }}
          >
            Curriculum Calendar
          </div>
          <div
            style={{
              fontSize: 12.5,
              fontWeight: 650,
              color: "oklch(45% 0.07 240)",
              marginTop: 3,
            }}
          >
            Month {selectedMonth}
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 2 }}>
          <button
            onClick={() => setSelectedMonth((prev) => Math.max(1, prev - 1))}
            disabled={selectedMonth === 1}
            style={{
              width: 28,
              height: 28,
              borderRadius: 6,
              border: "1.5px solid oklch(88% 0.025 240)",
              background: "white",
              cursor: selectedMonth === 1 ? "default" : "pointer",
              opacity: selectedMonth === 1 ? 0.4 : 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <ChevronLeft size={14} color="oklch(20% 0.09 245)" />
          </button>
          <button
            onClick={() => setSelectedMonth((prev) => Math.min(totalMonths, prev + 1))}
            disabled={selectedMonth === totalMonths}
            style={{
              width: 28,
              height: 28,
              borderRadius: 6,
              border: "1.5px solid oklch(88% 0.025 240)",
              background: "white",
              cursor: selectedMonth === totalMonths ? "default" : "pointer",
              opacity: selectedMonth === totalMonths ? 0.4 : 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <ChevronRight size={14} color="oklch(20% 0.09 245)" />
          </button>
        </div>
      </div>

      {/* Calendar Grid Headers */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "36px repeat(7, 1fr)",
          gap: 5,
          textAlign: "center",
          marginBottom: 6,
        }}
      >
        <div
          style={{
            fontSize: 10,
            fontWeight: 800,
            color: "oklch(45% 0.07 240)",
            textAlign: "left",
            alignSelf: "center",
            letterSpacing: "0.02em",
          }}
        >
          WEEK
        </div>
        {Array.from({ length: 7 }).map((_, idx) => (
          <div
            key={idx}
            style={{
              fontSize: 10,
              fontWeight: 800,
              color: "oklch(45% 0.07 240)",
              alignSelf: "center",
              letterSpacing: "0.02em",
            }}
          >
            D{idx + 1}
          </div>
        ))}
      </div>

      {/* Calendar Grid Rows */}
      <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
        {Array.from({ length: 4 }).map((_, rowIdx) => {
          const weekNum = (selectedMonth - 1) * 4 + rowIdx + 1;
          const isCurrentWeek = weekNum === preference.current_week;

          return (
            <div
              key={weekNum}
              style={{
                display: "grid",
                gridTemplateColumns: "36px repeat(7, 1fr)",
                gap: 5,
              }}
            >
              {/* Week Label */}
              <div
                style={{
                  fontSize: 11.5,
                  fontWeight: isCurrentWeek ? 800 : 600,
                  color: isCurrentWeek ? "#0070C4" : "oklch(35% 0.05 240)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "flex-start",
                }}
              >
                W{weekNum}
              </div>

              {/* Day Cells (Static progress blocks) */}
              {Array.from({ length: 7 }).map((_, colIdx) => {
                const dayNum = colIdx + 1;
                const isCompleted =
                  weekNum < preference.current_week ||
                  (weekNum === preference.current_week && dayNum < preference.current_day_in_week);
                const isCurrent =
                  weekNum === preference.current_week && dayNum === preference.current_day_in_week;

                // Color coding
                let bg = "oklch(94% 0.02 240)"; // Upcoming/blank color
                let animation = "none";

                if (isCompleted) {
                  bg = "#0070C4"; // Primary blue
                } else if (isCurrent) {
                  bg = "linear-gradient(135deg, #ff7a18, #ffb547)"; // Streak orange gradient
                  animation = "pulseGlow 2s infinite";
                }

                // Tooltip info
                const tooltip = `Week ${weekNum}, Day ${dayNum}${
                  isCurrent ? " (Active Day)" : isCompleted ? " (Completed)" : ""
                }`;

                return (
                  <div
                    key={dayNum}
                    title={tooltip}
                    style={{
                      aspectRatio: "1",
                      borderRadius: 6,
                      background: bg,
                      animation,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      position: "relative",
                    }}
                  />
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}
