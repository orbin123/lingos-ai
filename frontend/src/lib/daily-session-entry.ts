/** Tracks that the learner opened today's chat so the entry page can offer Resume. */

const STORAGE_KEY = "learning:dailyChatEntered";

export function localCalendarDateString(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function markDailyChatEntered(sessionId: string): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        date: localCalendarDateString(),
        sessionId,
      }),
    );
  } catch {
    /* quota / private mode */
  }
}

export function getResumeSessionIdForToday(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { date?: string; sessionId?: string };
    if (
      parsed?.date === localCalendarDateString() &&
      typeof parsed.sessionId === "string" &&
      parsed.sessionId.length > 0
    ) {
      return parsed.sessionId;
    }
    return null;
  } catch {
    return null;
  }
}
