"use client";

import { useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { AxiosError } from "axios";

import type { UserCoursePreferenceRead } from "@/lib/preferences-api";
import { getApiErrorMessage } from "@/lib/errors";
import { useTodaySessionPlan, useStartLearningSession } from "@/hooks/useSessionsFlow";
import { sessionsApi, type DashboardPlanActivity } from "@/lib/sessions-api";
import { hasScorecardBeenViewed } from "@/lib/daily-session-entry";

interface DailyTaskPanelProps {
  preference: UserCoursePreferenceRead;
}

function activitiesPerDay(preference: UserCoursePreferenceRead) {
  return Math.max(2, Math.min(4, preference.tasks_per_day));
}

function courseLengthLabel(courseLength: "24w" | "48w"): string {
  return courseLength === "48w" ? "48-week plan" : "24-week plan";
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

export function DailyTaskPanel({ preference }: DailyTaskPanelProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const startMutation = useStartLearningSession();

  // GET /sessions/today-plan — preview plan or existing session, no LLM call.
  const { data: plan, isLoading, isError, error, refetch } = useTodaySessionPlan();

  const completed = plan?.status === "completed";
  const scorecardViewed = Boolean(
    plan?.session_id && completed && hasScorecardBeenViewed(plan.session_id),
  );
  const showLocked = Boolean(plan && completed && scorecardViewed);

  const unlockMutation = useMutation({
    mutationFn: sessionsApi.advanceDay,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sessions", "today-plan"] });
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });

  const handleStart = useCallback(async () => {
    const allDone = Boolean(
      plan &&
        !plan.is_preview &&
        plan.session_id &&
        plan.activities.length > 0 &&
        plan.activities.every((activity) => activity.status === "evaluated"),
    );
    if (allDone && plan?.session_id) {
      router.push(`/sessions/${plan.session_id}/scorecard`);
      return;
    }

    const week = Number(searchParams.get("week") || preference.current_week || 1);
    const day = Number(searchParams.get("day") || preference.current_day_in_week || 1);
    const result = await startMutation.mutateAsync({ week, day });
    router.push(`/task/chat/${result.session_id}`);
  }, [
    plan,
    preference.current_day_in_week,
    preference.current_week,
    searchParams,
    startMutation,
    router,
  ]);

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
      <PanelHeader preference={preference} />

      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        <Tag bg="#d6e8f7" color="#00599e">
          Day {preference.current_day_in_week}
        </Tag>
        <Tag bg="oklch(96% 0.04 290)" color="oklch(45% 0.16 290)">
          Week {preference.current_week}
        </Tag>
        <Tag bg="oklch(96% 0.04 60)" color="oklch(45% 0.14 60)">
          {activitiesPerDay(preference)} activities
        </Tag>
      </div>

      {isLoading && <LoadingBlock />}

      {isError && !isLoading && (
        <ErrorBlock
          message={getApiErrorMessage(error as AxiosError)}
          onRetry={() => refetch()}
        />
      )}

      {!isLoading && !isError && plan && showLocked && (
        <LockedDayBlock
          week={preference.current_week}
          day={preference.current_day_in_week}
          isUnlocking={unlockMutation.isPending}
          error={unlockMutation.error}
          onUnlock={() => unlockMutation.mutate()}
        />
      )}

      {!isLoading && !isError && plan && !showLocked && (
        <ActiveSessionBlock
          activities={plan.activities}
          topic={plan.topic}
          isPreview={plan.is_preview}
          sessionStatus={plan.status}
          isStarting={startMutation.isPending}
          startError={startMutation.error}
          onStart={handleStart}
        />
      )}
    </div>
  );
}

function PanelHeader({ preference }: { preference: UserCoursePreferenceRead }) {
  return (
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
          {courseLengthLabel(preference.course_length)}
        </div>
      </div>
    </div>
  );
}

function Tag({
  children,
  bg,
  color,
}: {
  children: React.ReactNode;
  bg: string;
  color: string;
}) {
  return (
    <span
      style={{
        padding: "5px 12px",
        borderRadius: 999,
        background: bg,
        color,
        fontSize: 12,
        fontWeight: 700,
      }}
    >
      {children}
    </span>
  );
}

const CORE_ACTIVITY_LABEL: Record<string, string> = {
  read: "Read",
  write: "Write",
  listen: "Listen",
  speak: "Speak",
};

function ActiveSessionBlock({
  activities,
  topic,
  isPreview,
  sessionStatus,
  isStarting,
  startError,
  onStart,
}: {
  activities: DashboardPlanActivity[];
  topic: string;
  isPreview: boolean;
  sessionStatus: string | null;
  isStarting: boolean;
  startError: Error | null;
  onStart: () => void;
}) {
  const activeIndex = activities.findIndex((a) => a.status !== "evaluated");
  const allDone = activities.length > 0 && activeIndex === -1;

  let buttonLabel = "Start session";
  if (!isPreview) {
    if (allDone) buttonLabel = "See results";
    else if (sessionStatus === "in_progress") buttonLabel = "Continue session";
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {topic && (
        <div
          style={{
            fontSize: 12.5,
            fontWeight: 700,
            color: "oklch(38% 0.09 245)",
            marginBottom: 2,
          }}
        >
          {topic}
        </div>
      )}

      {!isPreview && (
        <div
          style={{
            padding: "10px 12px",
            borderRadius: 12,
            background: "#eef6fc",
            border: "1px solid #c9deef",
            color: "#00599e",
            fontSize: 12.5,
            fontWeight: 700,
            lineHeight: 1.45,
          }}
        >
          {allDone
            ? "All activities answered — review your scorecard when you're ready."
            : "Today's activities run in one session."}
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {activities.map((activity, index) => (
          <ActivityRow
            key={activity.sequence}
            activity={activity}
            coreActivityLabel={CORE_ACTIVITY_LABEL[activity.core_activity] ?? activity.core_activity}
            isActive={!isPreview && !allDone && index === activeIndex}
            isLocked={isPreview || (!allDone && index > activeIndex)}
            isComplete={activity.status === "evaluated"}
          />
        ))}
      </div>

      {startError && (
        <p style={{ margin: 0, color: "oklch(40% 0.15 15)", fontSize: 13 }}>
          {getApiErrorMessage(startError as AxiosError)}
        </p>
      )}

      <button
        type="button"
        onClick={onStart}
        disabled={isStarting}
        style={{
          alignSelf: "stretch",
          marginTop: 6,
          padding: "13px 18px",
          borderRadius: 14,
          border: "none",
          background: isStarting ? "oklch(68% 0.06 240)" : "#0070C4",
          color: "white",
          fontFamily: "inherit",
          fontSize: 14,
          fontWeight: 800,
          cursor: isStarting ? "default" : "pointer",
          boxShadow: isStarting ? "none" : "0 6px 18px rgba(0,112,196,0.22)",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 6,
        }}
      >
        {isStarting ? "Starting…" : buttonLabel}
        {!isStarting && <ArrowIcon />}
      </button>
    </div>
  );
}

function ActivityRow({
  activity,
  coreActivityLabel,
  isActive,
  isLocked,
  isComplete,
}: {
  activity: DashboardPlanActivity;
  coreActivityLabel: string;
  isActive: boolean;
  isLocked: boolean;
  isComplete: boolean;
}) {
  let itemBg = "white";
  let itemBorder = "1.5px solid oklch(88% 0.025 240)";
  let itemOpacity = 1;

  if (isComplete) {
    itemBg = "oklch(97% 0.04 155)";
    itemBorder = "1.5px solid oklch(80% 0.08 155)";
  } else if (isActive) {
    itemBg = "linear-gradient(135deg, white, #d6e8f7)";
    itemBorder = "2px solid #0070C4";
  } else if (isLocked) {
    itemBg = "oklch(97% 0.02 240)";
    itemOpacity = 0.65;
  }

  const iconBg = isComplete
    ? "oklch(58% 0.16 155)"
    : isActive
    ? "#0070C4"
    : "oklch(94% 0.02 240)";

  const iconColor = isComplete || isActive ? "white" : "oklch(55% 0.04 240)";

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 14,
        padding: "14px 16px",
        borderRadius: 16,
        border: itemBorder,
        background: itemBg,
        opacity: itemOpacity,
      }}
    >
      <div
        style={{
          width: 40,
          height: 40,
          borderRadius: 12,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
          background: iconBg,
          color: iconColor,
          boxShadow: isActive
            ? "0 4px 10px rgba(0,112,196,0.3)"
            : isComplete
            ? "0 4px 10px rgba(80,180,120,0.2)"
            : "none",
        }}
      >
        {isComplete ? <CheckIcon /> : isActive ? <PlayIcon /> : <LockIcon />}
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontSize: 14.5,
            fontWeight: 700,
            color: "oklch(20% 0.09 245)",
            marginBottom: 2,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {activity.archetype_name}
        </div>
        <div
          style={{
            fontSize: 12,
            color: "oklch(45% 0.07 240)",
            display: "flex",
            gap: 8,
            alignItems: "center",
          }}
        >
          <span>{coreActivityLabel} · Activity {activity.sequence}</span>
        </div>
      </div>

      {isComplete && (
        <span
          style={{
            fontSize: 12.5,
            fontWeight: 700,
            color: "oklch(43% 0.16 155)",
            flexShrink: 0,
          }}
        >
          Done
        </span>
      )}
      {isLocked && !isComplete && (
        <span
          style={{
            fontSize: 12.5,
            fontWeight: 700,
            color: "oklch(55% 0.04 240)",
            flexShrink: 0,
          }}
        >
          Unlocks next
        </span>
      )}
    </div>
  );
}

function LockedDayBlock({
  week,
  day,
  isUnlocking,
  error,
  onUnlock,
}: {
  week: number;
  day: number;
  isUnlocking: boolean;
  error: Error | null;
  onUnlock: () => void;
}) {
  return (
    <div
      style={{
        padding: "26px 18px 10px",
        textAlign: "center",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
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
          background: "oklch(20% 0.09 245)",
          color: "white",
        }}
      >
        <LockIcon />
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
          Day {week}.{day} complete
        </h3>
        <p
          style={{
            margin: 0,
            color: "oklch(45% 0.07 240)",
            fontSize: 14,
            lineHeight: 1.6,
          }}
        >
          Ready for tomorrow?
        </p>
      </div>
      {error && (
        <p style={{ margin: 0, color: "oklch(40% 0.15 15)", fontSize: 13 }}>
          {getApiErrorMessage(error as AxiosError)}
        </p>
      )}
      <button
        type="button"
        onClick={onUnlock}
        disabled={isUnlocking}
        style={{
          alignSelf: "stretch",
          marginTop: 8,
          padding: "13px 18px",
          borderRadius: 14,
          border: "none",
          background: isUnlocking ? "oklch(68% 0.06 240)" : "#0070C4",
          color: "white",
          fontFamily: "inherit",
          fontSize: 14,
          fontWeight: 800,
          cursor: isUnlocking ? "default" : "pointer",
          boxShadow: isUnlocking ? "none" : "0 6px 18px rgba(0,112,196,0.22)",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 6,
        }}
      >
        {isUnlocking ? "Unlocking..." : "Unlock next day"}
        {!isUnlocking && <ArrowIcon />}
      </button>
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
        Loading today&apos;s plan...
      </p>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

function ErrorBlock({
  message,
  onRetry,
}: {
  message: string;
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
        Retry
      </button>
    </div>
  );
}
