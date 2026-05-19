"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { AxiosError } from "axios";

import type { EnrollmentRead } from "@/lib/courses-api";
import { getApiErrorMessage } from "@/lib/errors";
import { useStartTodaySession } from "@/hooks/useSessionsFlow";
import type {
  AttemptSkeleton,
  SessionStartResponse,
} from "@/lib/sessions-api";

interface DailyTaskPanelProps {
  enrollment: EnrollmentRead;
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
  const startToday = useStartTodaySession();

  // Fire once per mount. The dashboard re-keys this component on
  // (current_week, current_day_in_week), so mounting → fresh fetch is the
  // right cadence; we don't poll.
  const firedRef = useRef(false);
  useEffect(() => {
    if (firedRef.current) return;
    firedRef.current = true;
    startToday.mutate();
  }, [startToday]);

  const session: SessionStartResponse | null = startToday.data ?? null;
  const isLoading = startToday.isPending || (!session && !startToday.isError);
  const error = startToday.error;

  const completed = session?.status === "completed";
  const abandoned = session?.status === "abandoned";

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
      <PanelHeader enrollment={enrollment} />

      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        <Tag bg="#d6e8f7" color="#00599e">
          Day {enrollment.current_day_in_week}
        </Tag>
        <Tag bg="oklch(96% 0.04 290)" color="oklch(45% 0.16 290)">
          {enrollment.course.target_level}
        </Tag>
        <Tag bg="oklch(96% 0.04 60)" color="oklch(45% 0.14 60)">
          {activitiesPerDay(enrollment)} activities
        </Tag>
      </div>

      {isLoading && <LoadingBlock />}

      {error && !isLoading && (
        <ErrorBlock
          message={getApiErrorMessage(error as AxiosError)}
          onRetry={() => {
            firedRef.current = true;
            startToday.mutate();
          }}
        />
      )}

      {!isLoading && !error && session && completed && <CompletedTodayBlock />}

      {!isLoading && !error && session && abandoned && (
        <AbandonedBlock onStartFresh={() => startToday.mutate()} />
      )}

      {!isLoading && !error && session && !completed && !abandoned && (
        <ActiveSessionBlock
          session={session}
          onStart={() => router.push(`/sessions/${session.session_id}`)}
        />
      )}
    </div>
  );
}

function PanelHeader({ enrollment }: { enrollment: EnrollmentRead }) {
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
          {enrollment.course.title} · {enrollment.course.duration_weeks}-week plan
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

function ActiveSessionBlock({
  session,
  onStart,
}: {
  session: SessionStartResponse;
  onStart: () => void;
}) {
  const attempts = session.attempts;
  const activeIndex = attempts.findIndex((a) => a.status !== "evaluated");
  const allDone = attempts.length > 0 && activeIndex === -1;
  // `allDone` can hit before the session itself flips to `completed` (the
  // user has answered every activity but hasn't called /complete yet). In
  // that case we still let them tap into the session shell to finalize.

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
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
          ? "All activities answered — finish the session to lock in your score."
          : "Today's activities run in one session."}
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {attempts.map((attempt, index) => (
          <ActivityRow
            key={attempt.sequence}
            attempt={attempt}
            isActive={!allDone && index === activeIndex}
            isLocked={!allDone && index > activeIndex}
            isComplete={attempt.status === "evaluated"}
          />
        ))}
      </div>

      <button
        type="button"
        onClick={onStart}
        style={{
          alignSelf: "stretch",
          marginTop: 6,
          padding: "13px 18px",
          borderRadius: 14,
          border: "none",
          background: "#0070C4",
          color: "white",
          fontFamily: "inherit",
          fontSize: 14,
          fontWeight: 800,
          cursor: "pointer",
          boxShadow: "0 6px 18px rgba(0,112,196,0.22)",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 6,
        }}
      >
        {allDone ? "Finish session" : activeIndex === 0 ? "Start session" : "Continue session"}
        <ArrowIcon />
      </button>
    </div>
  );
}

function ActivityRow({
  attempt,
  isActive,
  isLocked,
  isComplete,
}: {
  attempt: AttemptSkeleton;
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
          {attempt.archetype_name}
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
          <span>Activity {attempt.sequence}</span>
          {attempt.is_mandatory && (
            <span
              style={{
                padding: "1px 6px",
                borderRadius: 6,
                background: "oklch(95% 0.05 30)",
                color: "oklch(45% 0.16 30)",
                fontWeight: 700,
                fontSize: 10.5,
                textTransform: "uppercase",
                letterSpacing: 0.4,
              }}
            >
              Mandatory
            </span>
          )}
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
      {isLocked && (
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

function CompletedTodayBlock() {
  return (
    <div
      style={{
        padding: "28px 18px 12px",
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
          Today&apos;s session is complete
        </h3>
        <p
          style={{
            margin: 0,
            color: "oklch(45% 0.07 240)",
            fontSize: 14,
            lineHeight: 1.6,
          }}
        >
          Come back tomorrow — the next day unlocks automatically.
        </p>
      </div>
    </div>
  );
}

function AbandonedBlock({ onStartFresh }: { onStartFresh: () => void }) {
  return (
    <div
      style={{
        padding: "22px 18px 10px",
        textAlign: "center",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
      }}
    >
      <p style={{ margin: 0, color: "oklch(40% 0.07 240)", fontSize: 14 }}>
        Your previous attempt for today was abandoned.
      </p>
      <button
        type="button"
        onClick={onStartFresh}
        style={{
          padding: "10px 18px",
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
        Start fresh
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
        Loading today&apos;s session...
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
