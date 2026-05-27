import { X } from "lucide-react";
import type { FeedbackMistake } from "../source";

export function FeedbackMistakeRow({
  mistake,
  isLast,
}: {
  mistake: FeedbackMistake;
  isLast: boolean;
}) {
  return (
    <div
      style={{
        padding: "16px 20px",
        borderBottom: isLast ? "none" : "1px solid oklch(88% 0.025 240)",
        display: "flex",
        gap: 14,
      }}
    >
      <div
        style={{
          width: 26,
          height: 26,
          borderRadius: "50%",
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "oklch(58% 0.2 25)",
          color: "white",
        }}
      >
        <X size={14} strokeWidth={3} />
      </div>
      <div style={{ minWidth: 0, flex: 1 }}>
        <div style={{ fontSize: 13.5, color: "oklch(18% 0.06 240)", lineHeight: 1.55 }}>
          <strong>{mistake.issue}</strong>
          {mistake.userWrote && (
            <div style={{ marginTop: 8 }}>
              <strong style={{ color: "oklch(42% 0.07 240)" }}>Your version: </strong>
              <span
                style={{
                  display: "inline-block",
                  padding: "1px 6px",
                  borderRadius: 4,
                  fontWeight: 700,
                  background: "oklch(96% 0.018 245)",
                  color: "oklch(35% 0.07 240)",
                }}
              >
                {mistake.userWrote}
              </span>
            </div>
          )}
          {mistake.correction && (
            <div style={{ marginTop: 6 }}>
              <strong style={{ color: "oklch(42% 0.07 240)" }}>Improved version: </strong>
              <span
                style={{
                  display: "inline-block",
                  padding: "1px 6px",
                  borderRadius: 4,
                  fontWeight: 800,
                  background: "oklch(92% 0.1 155)",
                  color: "oklch(28% 0.16 155)",
                }}
              >
                {mistake.correction}
              </span>
            </div>
          )}
        </div>
        {mistake.rule && (
          <div
            style={{
              marginTop: 10,
              padding: "10px 12px",
              borderRadius: 10,
              background: "oklch(96% 0.025 245)",
              color: "oklch(45% 0.07 240)",
              fontSize: 13,
              lineHeight: 1.55,
            }}
          >
            <strong>Rule: </strong>
            {mistake.rule}
          </div>
        )}
      </div>
    </div>
  );
}
