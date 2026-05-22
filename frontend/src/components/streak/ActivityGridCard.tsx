"use client";

import { useQuery } from "@tanstack/react-query";
import { streakApi, type ActivityGridCell, type StreakData } from "@/lib/streak-api";

function cellColor(cell: ActivityGridCell): string {
  if (cell.frozen_protected) return "#bfe5ff";
  switch (cell.intensity) {
    case 0:
      return "oklch(94% 0.02 240)";
    case 1:
      return "oklch(88% 0.06 240)";
    case 2:
      return "oklch(78% 0.1 230)";
    case 3:
      return "oklch(62% 0.14 230)";
    default:
      return "#0070C4";
  }
}

export function ActivityGridCard() {
  const { data } = useQuery<StreakData>({
    queryKey: ["streak", "me"],
    queryFn: streakApi.getMe,
    refetchOnWindowFocus: false,
  });

  const cells: ActivityGridCell[] =
    data?.activity_grid ??
    Array.from({ length: 91 }, (_, i) => ({
      date: `placeholder-${i}`,
      activity_count: 0,
      completed: false,
      intensity: 0 as const,
      frozen_protected: false,
    }));

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
      <div style={{ marginBottom: 6 }}>
        <div
          style={{
            fontSize: 17,
            fontWeight: 800,
            color: "oklch(20% 0.09 245)",
            letterSpacing: "-0.01em",
          }}
        >
          Activity
        </div>
        <div
          style={{
            fontSize: 12.5,
            color: "oklch(45% 0.07 240)",
            marginTop: 3,
          }}
        >
          Activities per day{data ? ` · ${data.timezone}` : ""}
        </div>
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(13, 1fr)",
          gap: 4,
          marginTop: 10,
        }}
      >
        {cells.map((c) => (
          <div
            key={c.date}
            title={
              data
                ? `${c.date} — ${c.activity_count} ${
                    c.activity_count === 1 ? "activity" : "activities"
                  }${c.frozen_protected ? " (freeze protected)" : ""}`
                : undefined
            }
            style={{
              aspectRatio: "1",
              borderRadius: 4,
              background: cellColor(c),
              border: c.frozen_protected ? "1px solid #7dc8ff" : "none",
            }}
          />
        ))}
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          marginTop: 12,
          fontSize: 11,
          color: "oklch(45% 0.07 240)",
          fontWeight: 600,
        }}
      >
        <span>Less</span>
        {[0, 1, 2, 3, 4].map((lvl) => (
          <div
            key={lvl}
            style={{
              width: 10,
              height: 10,
              borderRadius: 3,
              background: cellColor({
                date: "",
                activity_count: lvl,
                completed: lvl > 0,
                intensity: lvl as 0 | 1 | 2 | 3 | 4,
                frozen_protected: false,
              }),
            }}
          />
        ))}
        <span>More</span>
        <span style={{ marginLeft: "auto" }}>Last 13 weeks</span>
      </div>
    </div>
  );
}
