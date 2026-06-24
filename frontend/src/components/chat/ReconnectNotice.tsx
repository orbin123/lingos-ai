"use client";

import { ChatBubble } from "@/components/chat/ChatChrome";
import type { ConnectionState } from "@/lib/ws-reconnect";

export interface ReconnectNoticeProps {
  connectionState: ConnectionState;
  accessBlocked: boolean;
  isReconnecting: boolean;
  /** Auto-reconnect budget is spent → show the manual "Reload session" CTA. */
  exhausted: boolean;
  /** Show the "LingosAI" name on the bubble (used before any events exist). */
  labelAsLingos?: boolean;
  onReload: () => void;
}

/**
 * Honest connection-status messaging for the chat socket (Phase 4).
 *
 * The pre-Phase-4 UI printed a permanent "Connection closed. Reconnecting…"
 * that never recovered. This surfaces three truthful states instead:
 *  - access revoked (4402) → upgrade prompt;
 *  - reconnect budget spent → a real "Reload session" action (never an
 *    infinite "Reconnecting…");
 *  - actively recovering / transient drop → a calm "Reconnecting…" line.
 */
export function ReconnectNotice({
  connectionState,
  accessBlocked,
  isReconnecting,
  exhausted,
  labelAsLingos,
  onReload,
}: ReconnectNoticeProps) {
  if (accessBlocked) {
    return (
      <div style={{ marginTop: 16 }}>
        <ChatBubble role="ai" name={labelAsLingos ? "LingosAI" : undefined}>
          Your trial has ended — upgrade to continue this lesson.{" "}
          <a href="/pricing" style={{ fontWeight: 700 }}>
            Upgrade now
          </a>
        </ChatBubble>
      </div>
    );
  }

  if (exhausted) {
    return (
      <div style={{ marginTop: 16 }}>
        <ChatBubble role="ai" name={labelAsLingos ? "LingosAI" : undefined}>
          We couldn&apos;t reconnect to your session. Reload to pick up where you
          left off — your progress is saved.
        </ChatBubble>
        <div style={{ marginTop: 10, display: "flex", gap: 8 }}>
          <button
            type="button"
            onClick={onReload}
            style={{
              borderRadius: 999,
              border: "1px solid oklch(82% 0.03 240)",
              background: "white",
              padding: "8px 14px",
              fontSize: 13,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Reload session
          </button>
        </div>
      </div>
    );
  }

  const message =
    isReconnecting || connectionState === "closed"
      ? "Reconnecting…"
      : connectionState === "connecting"
        ? "Connecting to your session…"
        : "Could not reach the session. Make sure you're signed in.";

  return (
    <div style={{ marginTop: 16 }}>
      <ChatBubble role="ai" name={labelAsLingos ? "LingosAI" : undefined}>
        {message}
      </ChatBubble>
    </div>
  );
}
