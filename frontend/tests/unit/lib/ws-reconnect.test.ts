import { describe, expect, it } from "vitest";

import {
  buildLearningWsUrl,
  MAX_RECONNECT_ATTEMPTS,
  nextReconnectDelayMs,
  reconnectExhausted,
  RECONNECT_MAX_DELAY_MS,
  shouldScheduleReconnect,
} from "@/lib/ws-reconnect";

describe("nextReconnectDelayMs", () => {
  it("doubles each attempt then caps at the max delay", () => {
    expect(nextReconnectDelayMs(0)).toBe(600);
    expect(nextReconnectDelayMs(1)).toBe(1200);
    expect(nextReconnectDelayMs(2)).toBe(2400);
    expect(nextReconnectDelayMs(3)).toBe(4800);
    expect(nextReconnectDelayMs(4)).toBe(9600);
    // 600 * 2^5 = 19200 → capped.
    expect(nextReconnectDelayMs(5)).toBe(RECONNECT_MAX_DELAY_MS);
    expect(nextReconnectDelayMs(99)).toBe(RECONNECT_MAX_DELAY_MS);
  });

  it("is monotonically non-decreasing and never below the base", () => {
    let prev = 0;
    for (let f = 0; f <= 10; f += 1) {
      const d = nextReconnectDelayMs(f);
      expect(d).toBeGreaterThanOrEqual(prev);
      expect(d).toBeGreaterThanOrEqual(600);
      prev = d;
    }
  });

  it("treats negative/NaN failure counts as the first attempt", () => {
    expect(nextReconnectDelayMs(-3)).toBe(600);
    expect(nextReconnectDelayMs(Number.NaN)).toBe(600);
  });
});

describe("reconnectExhausted", () => {
  it("is false below the cap and true at/above it", () => {
    expect(reconnectExhausted(0)).toBe(false);
    expect(reconnectExhausted(MAX_RECONNECT_ATTEMPTS - 1)).toBe(false);
    expect(reconnectExhausted(MAX_RECONNECT_ATTEMPTS)).toBe(true);
    expect(reconnectExhausted(MAX_RECONNECT_ATTEMPTS + 5)).toBe(true);
  });
});

describe("shouldScheduleReconnect", () => {
  // The reconnect decision is phase-independent — the pre-Phase-4 bug was that
  // it only ran during feedback. These cases pass NO phase at all, proving the
  // policy can't be gated by one.
  it("reconnects on a dropped socket regardless of phase", () => {
    expect(
      shouldScheduleReconnect({
        connectionState: "closed",
        accessBlocked: false,
        exhausted: false,
      }),
    ).toBe(true);
    expect(
      shouldScheduleReconnect({
        connectionState: "error",
        accessBlocked: false,
        exhausted: false,
      }),
    ).toBe(true);
  });

  it("does not reconnect while healthy or mid-connect", () => {
    expect(
      shouldScheduleReconnect({
        connectionState: "open",
        accessBlocked: false,
        exhausted: false,
      }),
    ).toBe(false);
    expect(
      shouldScheduleReconnect({
        connectionState: "connecting",
        accessBlocked: false,
        exhausted: false,
      }),
    ).toBe(false);
  });

  it("stops once the budget is spent or access is revoked", () => {
    expect(
      shouldScheduleReconnect({
        connectionState: "closed",
        accessBlocked: false,
        exhausted: true,
      }),
    ).toBe(false);
    expect(
      shouldScheduleReconnect({
        connectionState: "closed",
        accessBlocked: true,
        exhausted: false,
      }),
    ).toBe(false);
  });
});

describe("buildLearningWsUrl", () => {
  it("embeds the session id in the path and the token as an encoded query param", () => {
    const url = buildLearningWsUrl("ws://localhost:8000", "sess-123", "tok-abc");
    expect(url).toBe("ws://localhost:8000/ws/learning/sess-123?token=tok-abc");
  });

  it("url-encodes tokens containing special characters", () => {
    const url = buildLearningWsUrl("wss://api.example.com", "s1", "a b/c+d=e");
    expect(url).toBe(
      "wss://api.example.com/ws/learning/s1?token=a%20b%2Fc%2Bd%3De",
    );
  });

  it("carries a refreshed token (a reconnect after refresh differs from the stale URL)", () => {
    const stale = buildLearningWsUrl("ws://h", "s1", "stale-jwt");
    const fresh = buildLearningWsUrl("ws://h", "s1", "fresh-jwt");
    expect(stale).not.toBe(fresh);
    expect(fresh).toContain("token=fresh-jwt");
  });
});
