"use client";

/**
 * ReactionBar — the shared "Copy | 👍 | 👎" row shown under AI feedback.
 *
 * Reused by both per-activity feedback widgets and the Coach's Note. One
 * reaction at a time: clicking the active button clears it (toggle-off),
 * clicking the other switches. Updates are optimistic and revert on error.
 *
 * When `feedbackId` is missing (e.g. a preview render with no backend row) the
 * reaction buttons are hidden and only Copy shows — so the bar never posts to a
 * target that doesn't exist.
 */

import type { CSSProperties } from "react";
import { useState } from "react";
import { Check, Copy, ThumbsDown, ThumbsUp } from "lucide-react";

import {
  feedbackApi,
  type FeedbackReactionType,
  type ReactionValue,
} from "@/lib/feedback-api";

export function ReactionBar({
  feedbackId,
  feedbackType,
  initialReaction = null,
  copyText,
  align = "end",
}: {
  feedbackId?: number | null;
  feedbackType: FeedbackReactionType;
  initialReaction?: ReactionValue | null;
  copyText: string;
  align?: "start" | "end";
}) {
  const [copied, setCopied] = useState(false);
  const [reaction, setReaction] = useState<ReactionValue | null>(initialReaction);
  const [saving, setSaving] = useState(false);

  const canReact = typeof feedbackId === "number";

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(copyText);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard unavailable — silently ignore */
    }
  };

  const react = async (value: ReactionValue) => {
    if (!canReact || saving) return;
    const previous = reaction;
    // Re-clicking the active reaction clears it; otherwise set/switch.
    const next = reaction === value ? null : value;
    setReaction(next); // optimistic
    setSaving(true);
    try {
      // The server toggles off when it receives the reaction already stored,
      // so sending `value` (not `next`) yields the same end state either way.
      const result = await feedbackApi.react({
        feedbackId: feedbackId as number,
        feedbackType,
        reaction: value,
      });
      setReaction(result.user_reaction);
    } catch {
      setReaction(previous); // revert on failure
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 6,
        justifyContent: align === "end" ? "flex-end" : "flex-start",
      }}
    >
      <button
        type="button"
        onClick={copy}
        aria-label={copied ? "Copied" : "Copy feedback"}
        title={copied ? "Copied" : "Copy feedback"}
        style={{
          ...actionButtonStyle,
          color: copied ? "oklch(48% 0.16 155)" : "oklch(45% 0.07 240)",
        }}
      >
        {copied ? <Check size={14} /> : <Copy size={14} />}
      </button>

      {canReact && (
        <>
          <button
            type="button"
            onClick={() => react("LIKE")}
            disabled={saving}
            aria-label="Like this feedback"
            aria-pressed={reaction === "LIKE"}
            title="Helpful"
            style={reactionButtonStyle(reaction === "LIKE", "LIKE")}
          >
            <ThumbsUp size={14} />
          </button>
          <button
            type="button"
            onClick={() => react("DISLIKE")}
            disabled={saving}
            aria-label="Dislike this feedback"
            aria-pressed={reaction === "DISLIKE"}
            title="Not helpful"
            style={reactionButtonStyle(reaction === "DISLIKE", "DISLIKE")}
          >
            <ThumbsDown size={14} />
          </button>
        </>
      )}
    </div>
  );
}

const actionButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  padding: 6,
  borderRadius: 999,
  border: "1px solid oklch(88% 0.02 245)",
  background: "white",
  fontFamily: "inherit",
  cursor: "pointer",
};

function reactionButtonStyle(active: boolean, kind: ReactionValue): CSSProperties {
  const activeBg = kind === "LIKE" ? "oklch(92% 0.08 150)" : "oklch(93% 0.07 25)";
  const activeColor =
    kind === "LIKE" ? "oklch(38% 0.14 150)" : "oklch(42% 0.16 25)";
  return {
    ...actionButtonStyle,
    border: active ? "1px solid transparent" : actionButtonStyle.border,
    background: active ? activeBg : "white",
    color: active ? activeColor : "oklch(45% 0.07 240)",
  };
}
