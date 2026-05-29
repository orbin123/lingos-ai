"use client";

export type TaskChatLoadingType =
  | "teacher_loading"
  | "activity_loading"
  | "feedback_loading"
  | "next_activity_loading"
  | null;

const LABELS: Record<Exclude<TaskChatLoadingType, null>, string> = {
  teacher_loading: "Preparing your tutor reply...",
  activity_loading: "Loading the activity...",
  feedback_loading: "Checking your answer...",
  next_activity_loading: "Preparing the next activity...",
};

export function TaskChatLoadingSkeleton({ type }: { type: TaskChatLoadingType }) {
  if (!type) return null;
  return (
    <div
      style={{
        borderRadius: 18,
        padding: "14px 16px",
        margin: "12px 0",
        background: "rgba(255,255,255,0.82)",
        border: "1px solid oklch(86% 0.025 240)",
        color: "oklch(42% 0.07 240)",
        fontSize: 13,
        fontWeight: 700,
        display: "flex",
        alignItems: "center",
        gap: 10,
        animation: "fadeIn 0.25s ease both",
      }}
    >
      <span
        aria-hidden
        style={{
          width: 9,
          height: 9,
          borderRadius: "50%",
          background: "#0070C4",
          boxShadow: "16px 0 0 rgba(0,112,196,0.35), 32px 0 0 rgba(0,112,196,0.18)",
          marginRight: 32,
        }}
      />
      {LABELS[type]}
    </div>
  );
}
