"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { AxiosError } from "axios";

import type { EnrollmentRead } from "@/lib/courses-api";
import { getApiErrorMessage } from "@/lib/errors";
import { useNextTask } from "@/hooks/useNextTask";
import { tasksApi, type UserTask } from "@/lib/tasks-api";

interface DailyTaskPanelProps {
  enrollment: EnrollmentRead;
}

// ── Activity helpers ────────────────────────────────────────────────────────

type Activity = "read" | "write" | "listen" | "speak";

const ACTIVITY_LABELS: Record<Activity, string> = {
  read: "Reading",
  write: "Writing",
  listen: "Listening",
  speak: "Speaking",
};

const ACTIVITY_COLORS: Record<Activity, { bg: string; text: string }> = {
  read:   { bg: "#dbeafe", text: "#1d4ed8" },
  write:  { bg: "#ede9fe", text: "#6d28d9" },
  listen: { bg: "#ffedd5", text: "#c2410c" },
  speak:  { bg: "#dcfce7", text: "#15803d" },
};

function ActivityBadge({ activity }: { activity: string }) {
  const a = activity as Activity;
  const colors = ACTIVITY_COLORS[a] ?? { bg: "#e5e7eb", text: "#374151" };
  const label = ACTIVITY_LABELS[a] ?? activity;
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 8px",
        borderRadius: 999,
        background: colors.bg,
        color: colors.text,
        fontSize: 11,
        fontWeight: 700,
        letterSpacing: "0.02em",
      }}
    >
      {label}
    </span>
  );
}

/** Extract the activity string from task content if present (curriculum tasks). */
function getActivity(content: unknown): string | null {
  if (content && typeof content === "object" && "activity" in content) {
    const a = (content as Record<string, unknown>).activity;
    if (typeof a === "string") return a;
  }
  return null;
}

function PlayIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M5 3.5v9l8-4.5-8-4.5z" />
    </svg>
  );
}

function LockIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <rect x="4" y="7" width="8" height="6" rx="1.2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M5.8 7V5a2.2 2.2 0 0 1 4.4 0v2" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M4 8.5l2.5 2.5L12 5.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
      <path d="M6 4l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function RetryIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
      <path
        d="M2.5 8A5.5 5.5 0 0 1 13 5.5"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
      />
      <path d="M11 3l2 2.5-2.5 1.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
      <path
        d="M13.5 8A5.5 5.5 0 0 1 3 10.5"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
      />
      <path d="M5 13l-2-2.5 2.5-1.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function DailyTaskPanel({ enrollment }: DailyTaskPanelProps) {
  const router = useRouter();
  const taskQuery = useNextTask(true);
  const bundle = taskQuery.data ?? [];
  const [retryingId, setRetryingId] = useState<number | null>(null);

  const isTaskComplete = useCallback(
    (task: UserTask) => task.status === "completed",
    [],
  );

  const activeIndex = bundle.findIndex((task) => !isTaskComplete(task));
  const allComplete = bundle.length > 0 && activeIndex === -1;

  const handleRetry = useCallback(
    async (e: React.MouseEvent, taskId: number) => {
      e.stopPropagation();
      setRetryingId(taskId);
      try {
        await tasksApi.retryTask(taskId);
        await taskQuery.refetch();
        router.push(`/task/chat?id=${taskId}`);
      } catch {
        setRetryingId(null);
      }
    },
    [taskQuery, router],
  );

  return (
    <div
      style={{
        background: "rgba(255,255,255,0.85)",
        backdropFilter: "blur(18px)",
        WebkitBackdropFilter: "blur(18px)",
        border: "1.5px solid rgba(255,255,255,0.92)",
        borderRadius: 22,
        padding: 24,
        boxShadow: "0 4px 24px rgba(80,110,180,0.1)",
        animation: "fadeSlideUp 0.4s ease both",
      }}
    >
      {/* Card header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-end",
          marginBottom: 14,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 17,
              fontWeight: 800,
              color: "oklch(20% 0.09 245)",
              letterSpacing: "-0.01em",
            }}
          >
            Today&apos;s plan
          </div>
          <div
            style={{
              fontSize: 12.5,
              color: "oklch(45% 0.07 240)",
              marginTop: 3,
            }}
          >
            {enrollment.course.title} · {enrollment.course.duration_weeks}-week plan
          </div>
        </div>
        <button
          style={{
            fontSize: 13,
            fontWeight: 700,
            color: "#0070C4",
            background: "none",
            border: "none",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: 4,
            padding: 0,
            fontFamily: "inherit",
          }}
        >
          View week <ArrowIcon />
        </button>
      </div>

      {/* Plan meta tags */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        <span
          style={{
            padding: "5px 12px",
            borderRadius: 999,
            background: "#d6e8f7",
            color: "#00599e",
            fontSize: 12,
            fontWeight: 700,
          }}
        >
          Day {enrollment.current_day_in_week}
        </span>
        <span
          style={{
            padding: "5px 12px",
            borderRadius: 999,
            background: "oklch(96% 0.04 290)",
            color: "oklch(45% 0.16 290)",
            fontSize: 12,
            fontWeight: 700,
          }}
        >
          {enrollment.course.target_level}
        </span>
        <span
          style={{
            padding: "5px 12px",
            borderRadius: 999,
            background: "oklch(96% 0.04 60)",
            color: "oklch(45% 0.14 60)",
            fontSize: 12,
            fontWeight: 700,
          }}
        >
          {enrollment.tasks_per_day} tasks
        </span>
      </div>

      {/* Content */}
      {taskQuery.isLoading && <LoadingBlock />}
      {taskQuery.isError && (
        <ErrorBlock
          message={getApiErrorMessage(taskQuery.error as AxiosError)}
          retryLabel={
            (taskQuery.error as AxiosError)?.response?.status === 503
              ? "Try again"
              : "Retry"
          }
          onRetry={() => taskQuery.refetch()}
        />
      )}
      {!taskQuery.isLoading && !taskQuery.isError && (bundle.length === 0 || allComplete) && (
        <CompletedTodayBlock />
      )}
      {!taskQuery.isLoading && !taskQuery.isError && bundle.length > 0 && !allComplete && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          {bundle.map((task, index) => {
            const complete = isTaskComplete(task);
            const active = !complete && index === activeIndex;
            const locked = !complete && index > activeIndex;

            let itemBg = "white";
            let itemBorder = "1.5px solid oklch(88% 0.025 240)";
            let itemOpacity = 1;

            if (complete) {
              itemBg = "oklch(97% 0.04 155)";
              itemBorder = "1.5px solid oklch(80% 0.08 155)";
            } else if (active) {
              itemBg = "linear-gradient(135deg, white, #d6e8f7)";
              itemBorder = "2px solid #0070C4";
            } else if (locked) {
              itemBg = "oklch(97% 0.02 240)";
              itemOpacity = 0.65;
            }

            const iconBg = complete
              ? "oklch(58% 0.16 155)"
              : active
              ? "#0070C4"
              : "oklch(94% 0.02 240)";

            const iconColor = complete || active ? "white" : "oklch(55% 0.04 240)";

            return (
              <div
                key={task.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 14,
                  padding: "16px 18px",
                  borderRadius: 16,
                  border: itemBorder,
                  background: itemBg,
                  opacity: itemOpacity,
                  position: "relative",
                }}
              >
                {/* Main clickable area */}
                <button
                  disabled={locked}
                  onClick={() => !complete && router.push(`/task/chat?id=${task.id}`)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 14,
                    flex: 1,
                    minWidth: 0,
                    background: "none",
                    border: "none",
                    padding: 0,
                    cursor: locked || complete ? "default" : "pointer",
                    textAlign: "left",
                    fontFamily: "inherit",
                    transition: "transform 0.15s, box-shadow 0.15s",
                  }}
                  onMouseEnter={(e) => {
                    if (locked || complete) return;
                    e.currentTarget.style.transform = "translateY(-1px)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = "translateY(0)";
                  }}
                >
                  {/* Icon */}
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: 12,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                      background: iconBg,
                      color: iconColor,
                      boxShadow:
                        active
                          ? "0 4px 10px rgba(0,112,196,0.3)"
                          : complete
                          ? "0 4px 10px rgba(80,180,120,0.2)"
                          : "none",
                    }}
                  >
                    {complete ? <CheckIcon /> : active ? <PlayIcon /> : <LockIcon />}
                  </div>

                  {/* Body */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        fontSize: 15,
                        fontWeight: 700,
                        color: "oklch(20% 0.09 245)",
                        marginBottom: 4,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {task.task.title}
                    </div>
                    {(() => {
                      const activity = getActivity(task.task.content);
                      return activity ? (
                        <ActivityBadge activity={activity} />
                      ) : (
                        <div
                          style={{
                            fontSize: 12.5,
                            color: "oklch(45% 0.07 240)",
                            textTransform: "capitalize",
                          }}
                        >
                          {task.task.task_type.replace(/^curriculum_/, "").replace(/_/g, " ")}
                        </div>
                      );
                    })()}
                  </div>

                  {/* CTA / Retry */}
                  {complete ? (
                    <span
                      onClick={(e) => handleRetry(e, task.id)}
                      style={{
                        flexShrink: 0,
                        width: 30,
                        height: 30,
                        borderRadius: 8,
                        border: "1.5px solid oklch(75% 0.06 155)",
                        background: retryingId === task.id ? "oklch(94% 0.04 155)" : "white",
                        color: "oklch(43% 0.16 155)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        cursor: retryingId === task.id ? "default" : "pointer",
                        transition: "background 0.15s, transform 0.15s",
                      }}
                      onMouseEnter={(e) => {
                        if (retryingId === task.id) return;
                        e.currentTarget.style.background = "oklch(94% 0.06 155)";
                        e.currentTarget.style.transform = "scale(1.1)";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = "white";
                        e.currentTarget.style.transform = "scale(1)";
                      }}
                    >
                      {retryingId === task.id ? (
                        <span
                          style={{
                            width: 11,
                            height: 11,
                            borderRadius: "50%",
                            border: "2px solid oklch(75% 0.06 155)",
                            borderTopColor: "oklch(43% 0.16 155)",
                            display: "inline-block",
                            animation: "spin 0.7s linear infinite",
                          }}
                        />
                      ) : (
                        <RetryIcon />
                      )}
                    </span>
                  ) : active ? (
                    <span
                      style={{
                        fontSize: 13,
                        fontWeight: 700,
                        color: "#0070C4",
                        flexShrink: 0,
                        display: "flex",
                        alignItems: "center",
                        gap: 4,
                      }}
                    >
                      Start <ArrowIcon />
                    </span>
                  ) : (
                    <span
                      style={{
                        fontSize: 13,
                        fontWeight: 700,
                        color: "oklch(55% 0.04 240)",
                        flexShrink: 0,
                        display: "flex",
                        alignItems: "center",
                        gap: 4,
                      }}
                    >
                      Unlocks next
                    </span>
                  )}
                </button>

                {/* Done label */}
                {complete && (
                  <span
                    style={{
                      fontSize: 13,
                      fontWeight: 700,
                      color: "oklch(43% 0.16 155)",
                      flexShrink: 0,
                      display: "flex",
                      alignItems: "center",
                      gap: 4,
                    }}
                  >
                    Done
                  </span>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function CompletedTodayBlock() {
  return (
    <div
      style={{
        padding: "28px 18px 10px",
        textAlign: "center",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 14,
      }}
    >
      <span
        style={{
          width: 54,
          height: 54,
          borderRadius: "50%",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          background: "oklch(55% 0.18 155)",
          color: "white",
        }}
      >
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
          <path
            d="M5 13l4 4L19 7"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </span>
      <div>
        <h3
          style={{
            margin: "0 0 6px",
            color: "oklch(20% 0.09 245)",
            fontSize: 18,
            fontWeight: 800,
          }}
        >
          Today&apos;s tasks are complete
        </h3>
        <p
          style={{
            margin: 0,
            color: "oklch(45% 0.07 240)",
            fontSize: 14,
            lineHeight: 1.6,
          }}
        >
          Your next set will unlock tomorrow.
        </p>
      </div>
    </div>
  );
}

function LoadingBlock() {
  return (
    <div style={{ padding: "26px 0", textAlign: "center" }}>
      <span
        style={{
          display: "inline-flex",
          width: 36,
          height: 36,
          borderRadius: "50%",
          border: "3px solid oklch(88% 0.03 240)",
          borderTopColor: "#0070C4",
          animation: "spin 0.8s linear infinite",
          marginBottom: 12,
        }}
      />
      <p style={{ margin: 0, color: "oklch(45% 0.07 240)", fontSize: 14 }}>
        Loading today&apos;s tasks...
      </p>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

function ErrorBlock({
  message,
  retryLabel,
  onRetry,
}: {
  message: string;
  retryLabel: string;
  onRetry: () => void;
}) {
  return (
    <div
      style={{
        padding: "20px 0",
        textAlign: "center",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
      }}
    >
      <p style={{ margin: 0, color: "oklch(40% 0.15 15)", fontSize: 14 }}>
        {message}
      </p>
      <button
        onClick={onRetry}
        style={{
          padding: "10px 24px",
          borderRadius: 10,
          border: "none",
          background: "#0070C4",
          color: "white",
          fontSize: 13,
          fontWeight: 700,
          cursor: "pointer",
          fontFamily: "inherit",
        }}
      >
        {retryLabel}
      </button>
    </div>
  );
}
