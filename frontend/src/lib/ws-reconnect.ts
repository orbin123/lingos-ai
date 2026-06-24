/**
 * Pure helpers for the learning-session WebSocket resilience layer (Phase 4).
 *
 * The connection lifecycle itself lives in the chat page, but the *decisions* —
 * how long to back off, when to give up, whether to reconnect, and how to build
 * the (token-bearing) URL — are extracted here so they can be unit-tested
 * without mounting the page or a real socket.
 *
 * Key design point: {@link shouldScheduleReconnect} deliberately takes NO phase
 * argument. The pre-Phase-4 bug was that reconnection only ran during the
 * feedback phase; reconnection is now phase-independent by construction.
 */

/** Client heartbeat cadence. Must stay well under the ALB's 120s idle timeout. */
export const HEARTBEAT_INTERVAL_MS = 25_000;

/** Give up auto-reconnecting after this many consecutive failed attempts. */
export const MAX_RECONNECT_ATTEMPTS = 5;

/** First backoff delay; each subsequent attempt doubles it (capped). */
export const RECONNECT_BASE_DELAY_MS = 600;

/** Upper bound on a single backoff delay. */
export const RECONNECT_MAX_DELAY_MS = 10_000;

export type ConnectionState = "connecting" | "open" | "closed" | "error";

/**
 * Exponential backoff with a cap.
 *
 * @param failures Consecutive failures so far (0 before the first retry).
 * @returns Delay in ms: 600, 1200, 2400, 4800, 9600, then capped at 10000.
 */
export function nextReconnectDelayMs(failures: number): number {
  const safe = Number.isFinite(failures) && failures > 0 ? failures : 0;
  const delay = RECONNECT_BASE_DELAY_MS * 2 ** safe;
  return Math.min(delay, RECONNECT_MAX_DELAY_MS);
}

/** True once we have burned through the auto-reconnect budget. */
export function reconnectExhausted(failures: number): boolean {
  return failures >= MAX_RECONNECT_ATTEMPTS;
}

/**
 * Whether the page should schedule another auto-reconnect.
 *
 * Intentionally phase-agnostic: a drop in *any* phase (teaching, practice,
 * submitted) is recoverable. We stop only when the socket is healthy, the
 * budget is spent, or access was revoked (4402 — the UI offers an upgrade).
 */
export function shouldScheduleReconnect(args: {
  connectionState: ConnectionState;
  accessBlocked: boolean;
  exhausted: boolean;
}): boolean {
  const { connectionState, accessBlocked, exhausted } = args;
  if (accessBlocked || exhausted) return false;
  return connectionState === "closed" || connectionState === "error";
}

/**
 * Build the learning-session WebSocket URL. The (freshly refreshed) JWT rides
 * as a query param because the handshake can't carry an Authorization header;
 * it is encoded so tokens with URL-special chars survive.
 */
export function buildLearningWsUrl(
  wsBaseUrl: string,
  sessionId: string,
  token: string,
): string {
  return `${wsBaseUrl}/ws/learning/${sessionId}?token=${encodeURIComponent(token)}`;
}
