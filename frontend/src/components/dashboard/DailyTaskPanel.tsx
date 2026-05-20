"use client";

import { useRouter } from "next/navigation";
import { AxiosError } from "axios";

import type { EnrollmentRead } from "@/lib/courses-api";
import { getApiErrorMessage } from "@/lib/errors";
import {
  useStartOrContinueTodaySession,
  useTodaySessionPlan,
} from "@/hooks/useSessionsFlow";
import type { DashboardPlanActivity } from "@/lib/sessions-api";

interface DailyTaskPanelProps {
  enrollment: EnrollmentRead;
}

const ACTIVITY_LABELS: Record<string, string> = {
  read: "Read",
  write: "Write",
  listen: "Listen",
  speak: "Speak",
};

function getActivityDisplayTitle(activity: DashboardPlanActivity): string {
  const type = ACTIVITY_LABELS[activity.core_activity] ?? activity.core_activity;
  return `${type} - ${activity.archetype_name}`;
}

function activitiesPerDay(enrollment: EnrollmentRead) {
  return Math.max(2, Math.min(4, enrollment.tasks_per_day));
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

export function DailyTaskPanel({ enrollment }: DailyTaskPanelProps) {
  const router = useRouter();
  const planQuery = useTodaySessionPlan();
  const startOrContinue = useStartOrContinueTodaySession();
  const plan = planQuery.data;
  const activities = plan?.activities ?? [];

  const isActivityComplete = (activity: DashboardPlanActivity) =>
    activity.status === "evaluated" || activity.status === "submitted";

  const activeIndex = activities.findIndex((activity) => !isActivityComplete(activity));
  const allComplete = plan?.status === "completed";

  function handleStartOrContinue() {
    startOrContinue.mutate(undefined, {
      onSuccess: (session) => {
        if (session.session_id && session.mode !== "completed") {
          router.push(`/task/chat/${session.session_id}`);
        }
      },
    });
  }

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
          {activitiesPerDay(enrollment)} tasks
        </span>
      </div>

      <div
        style={{
          marginBottom: 16,
          borderRadius: 12,
          background: "#eef6fc",
          border: "1px solid #c9deef",
          color: "#00599e",
          fontSize: 12.5,
          fontWeight: 700,
          lineHeight: 1.45,
          padding: "10px 12px",
        }}
      >
        Today&apos;s activities run in one chat session.
      </div>

      {planQuery.isLoading && <LoadingBlock />}
      {planQuery.isError && (
        <ErrorBlock
          message={getApiErrorMessage(planQuery.error as AxiosError)}
          retryLabel="Retry"
          onRetry={() => planQuery.refetch()}
        />
      )}
      {!planQuery.isLoading && !planQuery.isError && allComplete && (
        <CompletedTodayBlock />
      )}
      {!planQuery.isLoading && !planQuery.isError && !allComplete && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          {activities.map((activity, index) => {
            const complete = isActivityComplete(activity);
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
                key={`${activity.sequence}-${activity.archetype_id}`}
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
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 14,
                    flex: 1,
                    minWidth: 0,
                    textAlign: "left",
                    fontFamily: "inherit",
                  }}
                >
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
                      {getActivityDisplayTitle(activity)}
                    </div>
                    <div
                      style={{
                        fontSize: 12,
                        fontWeight: 700,
                        color: "oklch(48% 0.06 240)",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      Activity {activity.sequence}
                      {activity.is_mandatory ? " · Required" : " · Practice"}
                    </div>
                  </div>

                  {complete ? (
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
                      Active
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
                </div>
              </div>
            );
          })}
          {activities.length === 0 && (
            <p style={{ margin: 0, color: "oklch(45% 0.07 240)", fontSize: 14 }}>
              No activities are planned for today yet.
            </p>
          )}
          {activities.length > 0 && (
            <button
              type="button"
              onClick={handleStartOrContinue}
              disabled={startOrContinue.isPending}
              style={{
                width: "100%",
                marginTop: 6,
                border: "none",
                borderRadius: 14,
                background: "#0070C4",
                color: "white",
                cursor: startOrContinue.isPending ? "not-allowed" : "pointer",
                fontFamily: "inherit",
                fontSize: 14,
                fontWeight: 800,
                opacity: startOrContinue.isPending ? 0.7 : 1,
                padding: "14px 18px",
                boxShadow: "0 7px 20px rgba(0,112,196,0.24)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 6,
              }}
            >
              {startOrContinue.isPending
                ? "Preparing..."
                : plan?.session_id
                  ? "Continue session"
                  : "Start session"}
              {!startOrContinue.isPending && <ArrowIcon />}
            </button>
          )}
          {startOrContinue.isError && (
            <p style={{ margin: 0, color: "oklch(40% 0.15 15)", fontSize: 13 }}>
              {getApiErrorMessage(startOrContinue.error as AxiosError)}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function CompletedTodayBlock() {
  return (
    <div
      style={{
        padding: "28px 18px 18px",
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
          Today&apos;s activities are complete
        </h3>
        <p
          style={{
            margin: 0,
            color: "oklch(45% 0.07 240)",
            fontSize: 14,
            lineHeight: 1.6,
          }}
        >
          Your daily session has been scored and saved.
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
        Loading today&apos;s activities...
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
