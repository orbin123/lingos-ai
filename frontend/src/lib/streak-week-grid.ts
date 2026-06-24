import type { ActivityGridCell } from "@/lib/streak-api";

export type DayState = "done" | "today" | "miss" | "future" | "frozen";

export interface StreakWeekDay {
  date: string;
  d: string;
  n: number;
  st: DayState;
  isToday: boolean;
}

export const WEEKDAY_LETTER = ["S", "M", "T", "W", "T", "F", "S"] as const;

function parseLocalDate(isoDate: string): Date {
  const parts = isoDate.split("-").map((n) => Number.parseInt(n, 10));
  return new Date(parts[0], parts[1] - 1, parts[2]);
}

function formatLocalIso(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function buildLastSevenDays(
  grid: ActivityGridCell[],
  todayIso: string | null,
): StreakWeekDay[] {
  const slice = grid.slice(-7);
  return slice.map((cell) => {
    const localDate = parseLocalDate(cell.date);
    const isToday = todayIso !== null && cell.date === todayIso;
    let st: DayState;
    if (cell.frozen_protected) st = "frozen";
    else if (isToday) st = cell.completed ? "done" : "today";
    else if (cell.completed) st = "done";
    else st = "miss";
    return {
      date: cell.date,
      d: WEEKDAY_LETTER[localDate.getDay()],
      n: localDate.getDate(),
      st,
      isToday,
    };
  });
}

/** Preview/demo week ending at the local today when no API grid is available. */
export function buildPreviewWeekDays(): StreakWeekDay[] {
  const today = new Date();
  const todayIso = formatLocalIso(today);
  const cells: ActivityGridCell[] = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(today);
    d.setDate(today.getDate() - (6 - i));
    return {
      date: formatLocalIso(d),
      activity_count: 0,
      completed: false,
      intensity: 0,
      frozen_protected: false,
    };
  });
  return buildLastSevenDays(cells, todayIso);
}
