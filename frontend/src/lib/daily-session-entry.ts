/** Tracks that the learner opened today's chat so the entry page can offer Resume. */

const STORAGE_KEY = "learning:dailyChatEntered";
const SCORECARD_VIEWED_PREFIX = "lingos:scorecard-viewed:";

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

/**
 * Drop the stored resume sessionId so the next visit starts a fresh
 * session. Use after a profile-personalisation change, or when the
 * learner explicitly chooses "Start fresh" — otherwise the entry page
 * keeps offering to resume yesterday's already-cached task content.
 */
export function clearDailyChatEntry(): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    /* quota / private mode */
  }
}

export function markScorecardViewed(sessionId: string): void {
  if (typeof window === "undefined" || !sessionId) return;
  try {
    localStorage.setItem(`${SCORECARD_VIEWED_PREFIX}${sessionId}`, "1");
  } catch {
    /* quota / private mode */
  }
}

export function hasScorecardBeenViewed(sessionId: string): boolean {
  if (typeof window === "undefined" || !sessionId) return false;
  try {
    return localStorage.getItem(`${SCORECARD_VIEWED_PREFIX}${sessionId}`) === "1";
  } catch {
    return false;
  }
}
