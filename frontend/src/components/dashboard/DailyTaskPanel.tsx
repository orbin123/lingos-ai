"use client";

import { useCallback, type CSSProperties } from "react";
import { useRouter } from "next/navigation";
import { AxiosError } from "axios";
import { Check, Lock, Play } from "lucide-react";

import type { EnrollmentRead } from "@/lib/courses-api";
import { getApiErrorMessage } from "@/lib/errors";
import { useNextTask } from "@/hooks/useNextTask";
import type { UserTask } from "@/lib/tasks-api";

interface DailyTaskPanelProps {
  enrollment: EnrollmentRead;
}

const panelStyle: CSSProperties = {
  background:
    "linear-gradient(135deg, oklch(93% 0.04 240) 0%, oklch(95% 0.02 245) 100%)",
  borderRadius: 18,
  border: "1px solid rgba(80,120,200,0.12)",
  padding: "28px 26px 24px",
  boxShadow:
    "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
  animation: "fadeSlideUp 0.4s ease 0.15s both",
};

export function DailyTaskPanel({ enrollment }: DailyTaskPanelProps) {
  const router = useRouter();
  const taskQuery = useNextTask(true);
  const bundle = taskQuery.data ?? [];

  const isTaskComplete = useCallback(
    (task: UserTask) => task.status === "completed",
    [],
  );

  const activeIndex = bundle.findIndex((task) => !isTaskComplete(task));
  const allComplete = bundle.length > 0 && activeIndex === -1;

  if (taskQuery.isLoading) {
    return (
      <section style={panelStyle}>
        <PanelHeading enrollment={enrollment} />
        <LoadingBlock />
      </section>
    );
  }

  if (taskQuery.isError) {
    const status = (taskQuery.error as AxiosError)?.response?.status;
    return (
      <section style={panelStyle}>
        <PanelHeading enrollment={enrollment} />
        <ErrorBlock
          message={getApiErrorMessage(taskQuery.error)}
          retryLabel={status === 503 ? "Try again" : "Retry"}
          onRetry={() => taskQuery.refetch()}
        />
      </section>
    );
  }

  if (bundle.length === 0 || allComplete) {
    return (
      <section style={panelStyle}>
        <PanelHeading enrollment={enrollment} />
        <CompletedTodayBlock />
      </section>
    );
  }

  return (
    <section style={panelStyle}>
      <PanelHeading enrollment={enrollment} />
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {bundle.map((task, index) => {
          const complete = isTaskComplete(task);
          const active = !complete && index === activeIndex;
          const locked = !complete && index > activeIndex;

          return (
            <button
              key={task.id}
              disabled={locked}
              onClick={() => router.push(`/task/chat?id=${task.id}`)}
              style={{
                display: "grid",
                gridTemplateColumns: "32px 1fr auto",
                gap: 12,
                alignItems: "center",
                padding: "13px 14px",
                borderRadius: 12,
                background: complete
                  ? "oklch(96% 0.025 155)"
                  : active
                    ? "white"
                    : "rgba(255,255,255,0.48)",
                border: complete
                  ? "1px solid oklch(86% 0.08 155)"
                  : active
                    ? "1px solid oklch(78% 0.09 240)"
                    : "1px dashed rgba(80,120,200,0.22)",
                opacity: locked ? 0.68 : 1,
                cursor: locked ? "not-allowed" : "pointer",
                textAlign: "left",
                fontFamily: "inherit",
                width: "100%",
                transition: "transform 0.15s ease, box-shadow 0.15s ease",
              }}
              onMouseEnter={(e) => {
                if (locked) return;
                e.currentTarget.style.transform = "translateY(-1px)";
                e.currentTarget.style.boxShadow =
                  "0 4px 16px rgba(80,120,200,0.14)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "none";
              }}
            >
              <span
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: "50%",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  background: complete
                    ? "oklch(55% 0.18 155)"
                    : active
                      ? "oklch(52% 0.18 240)"
                      : "oklch(87% 0.025 240)",
                  color: complete || active ? "white" : "oklch(45% 0.06 240)",
                  flexShrink: 0,
                }}
              >
                {complete ? (
                  <Check size={17} />
                ) : active ? (
                  <Play size={15} fill="currentColor" />
                ) : (
                  <Lock size={15} />
                )}
              </span>
              <div style={{ minWidth: 0 }}>
                <p
                  style={{
                    margin: 0,
                    color: "oklch(19% 0.08 245)",
                    fontSize: 14,
                    fontWeight: 800,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {task.task.title}
                </p>
                <p
                  style={{
                    margin: "3px 0 0",
                    color: "oklch(48% 0.06 240)",
                    fontSize: 12,
                    textTransform: "capitalize",
                  }}
                >
                  {task.task.task_type.replace(/_/g, " ")}
                </p>
              </div>
              <span
                style={{
                  fontSize: 12,
                  fontWeight: 800,
                  color: complete
                    ? "oklch(43% 0.16 155)"
                    : active
                      ? "oklch(42% 0.15 240)"
                      : "oklch(48% 0.05 240)",
                  flexShrink: 0,
                }}
              >
                {complete ? "Done" : active ? "Open" : "Locked"}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function PanelHeading({ enrollment }: { enrollment: EnrollmentRead }) {
  return (
    <div>
      <p
        style={{
          fontSize: 11,
          fontWeight: 800,
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          color: "oklch(52% 0.18 240)",
          margin: "0 0 8px",
        }}
      >
        Today&apos;s focus — {enrollment.course.title}
      </p>
      <h2
        style={{
          fontSize: 22,
          fontWeight: 800,
          color: "oklch(15% 0.09 245)",
          margin: "0 0 12px",
          letterSpacing: "-0.02em",
        }}
      >
        Today&apos;s tasks
      </h2>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          flexWrap: "wrap",
          marginBottom: 18,
        }}
      >
        <MetaBadge>Day {enrollment.current_day_in_week}</MetaBadge>
        <MetaBadge>{enrollment.tasks_per_day} per day</MetaBadge>
        <MetaBadge>{enrollment.course.target_level}</MetaBadge>
      </div>
    </div>
  );
}

function MetaBadge({ children }: { children: React.ReactNode }) {
  return (
    <span
      style={{
        fontSize: 12,
        fontWeight: 700,
        color: "oklch(45% 0.07 240)",
        background: "rgba(255,255,255,0.72)",
        border: "1px solid rgba(80,120,200,0.1)",
        padding: "4px 10px",
        borderRadius: 6,
      }}
    >
      {children}
    </span>
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
          width: 58,
          height: 58,
          borderRadius: "50%",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          background: "oklch(55% 0.18 155)",
          color: "white",
        }}
      >
        <Check size={30} />
      </span>
      <div>
        <h3
          style={{
            margin: "0 0 6px",
            color: "oklch(15% 0.09 245)",
            fontSize: 22,
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
          Your next set will unlock on the next calendar day.
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
          borderTopColor: "oklch(52% 0.18 240)",
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
          background: "oklch(52% 0.18 240)",
          color: "white",
          fontSize: 13,
          fontWeight: 700,
          cursor: "pointer",
        }}
      >
        {retryLabel}
      </button>
    </div>
  );
}
