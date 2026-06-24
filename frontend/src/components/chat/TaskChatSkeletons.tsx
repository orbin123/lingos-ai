"use client";

import type { CSSProperties } from "react";
import { FileText, Sparkles } from "lucide-react";

import { SectionMarker } from "./ChatChrome";

export type TaskChatLoadingType =
  | "teacher_loading"
  | "activity_loading"
  | "next_activity_loading"
  | "evaluation_loading"
  | "feedback_loading"
  | "completing"
  | null;

/* ── Shared shimmer primitive ──────────────────────────────────────────
 * Every skeleton is built from these blocks. The `shimmer` keyframe lives
 * in `ChatGlobalStyles` (ChatChrome.tsx) so it's mounted once per page. */
function ShimmerBlock({
  w,
  h,
  r = 8,
  style,
}: {
  w?: number | string;
  h: number;
  r?: number;
  style?: CSSProperties;
}) {
  return (
    <div
      aria-hidden
      style={{
        width: w ?? "100%",
        height: h,
        borderRadius: r,
        background:
          "linear-gradient(90deg, rgba(206,221,243,0.45) 25%, rgba(231,240,253,0.95) 50%, rgba(206,221,243,0.45) 75%)",
        backgroundSize: "200% 100%",
        animation: "shimmer 1.4s ease-in-out infinite",
        ...style,
      }}
    />
  );
}

const cardStyle: CSSProperties = {
  background: "rgba(255,255,255,0.96)",
  border: "1.5px solid rgba(255,255,255,0.9)",
  boxShadow: "0 8px 32px rgba(80,110,180,0.14)",
  animation: "fadeIn 0.25s ease both",
};

/* ── Teaching bubble (left AI bubble) — matches ChatBubble ── */
function TeachingBubbleSkeleton() {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "flex-end",
        gap: 10,
        marginBottom: 12,
        animation: "fadeIn 0.25s ease both",
      }}
    >
      <div
        aria-hidden
        style={{
          width: 30,
          height: 30,
          borderRadius: "50%",
          flexShrink: 0,
          marginBottom: 2,
          background: "oklch(52% 0.18 240)",
          opacity: 0.5,
        }}
      />
      <div
        style={{
          maxWidth: "78%",
          minWidth: 220,
          padding: "15px 16px",
          borderRadius: 18,
          borderBottomLeftRadius: 6,
          background: "white",
          border: "1px solid oklch(86% 0.025 240)",
          boxShadow: "0 2px 10px rgba(80,110,180,0.06)",
          display: "flex",
          flexDirection: "column",
          gap: 9,
        }}
      >
        <ShimmerBlock h={11} w="92%" />
        <ShimmerBlock h={11} w="98%" />
        <ShimmerBlock h={11} w="64%" />
      </div>
    </div>
  );
}

/* ── Task card — boxy, matches TaskWidgetFrame (radius 22 / padding 22) ── */
function TaskCardSkeleton() {
  return (
    <div
      style={{
        ...cardStyle,
        borderRadius: 22,
        padding: 22,
        display: "flex",
        flexDirection: "column",
        gap: 16,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <ShimmerBlock w={44} h={44} r={12} style={{ flexShrink: 0 }} />
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 7 }}>
          <ShimmerBlock h={13} w="56%" />
          <ShimmerBlock h={10} w="38%" />
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <ShimmerBlock h={46} r={12} />
        <ShimmerBlock h={46} r={12} />
        <ShimmerBlock h={46} r={12} />
      </div>
      <ShimmerBlock w={140} h={42} r={999} style={{ alignSelf: "flex-start" }} />
    </div>
  );
}

/* ── Activity score — small, matches EvaluationWidgetRenderer ── */
function ScoreCardSkeleton() {
  return (
    <div
      style={{
        ...cardStyle,
        borderRadius: 18,
        padding: 18,
        display: "flex",
        alignItems: "center",
        gap: 16,
      }}
    >
      <ShimmerBlock w={56} h={56} r={999} style={{ flexShrink: 0 }} />
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 9 }}>
        <ShimmerBlock h={12} w="48%" />
        <ShimmerBlock h={10} w="72%" />
      </div>
    </div>
  );
}

/* ── Activity feedback — wider/taller, matches FeedbackWidgetRenderer ── */
function FeedbackCardSkeleton() {
  return (
    <div
      style={{
        ...cardStyle,
        borderRadius: 18,
        padding: 20,
        display: "flex",
        flexDirection: "column",
        gap: 14,
      }}
    >
      <div style={{ display: "flex", flexDirection: "column", gap: 9 }}>
        <ShimmerBlock h={12} w="40%" />
        <ShimmerBlock h={11} w="96%" />
        <ShimmerBlock h={11} w="88%" />
      </div>
      <div
        style={{
          background: "rgba(238,245,255,0.7)",
          borderRadius: 14,
          padding: 14,
          display: "flex",
          flexDirection: "column",
          gap: 9,
        }}
      >
        <ShimmerBlock h={10} w="30%" />
        <ShimmerBlock h={11} w="82%" />
        <ShimmerBlock h={11} w="68%" />
      </div>
    </div>
  );
}

/* ── Wide result card — final scorecard + coach share one identical size ── */
function WideResultSkeleton() {
  return (
    <div
      style={{
        ...cardStyle,
        borderRadius: 20,
        padding: 22,
        display: "flex",
        flexDirection: "column",
        gap: 14,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <ShimmerBlock w={48} h={48} r={14} style={{ flexShrink: 0 }} />
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 8 }}>
          <ShimmerBlock h={13} w="50%" />
          <ShimmerBlock h={10} w="34%" />
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <ShimmerBlock h={11} w="94%" />
        <ShimmerBlock h={11} w="86%" />
        <ShimmerBlock h={11} w="72%" />
      </div>
    </div>
  );
}

function FinalScorecardSkeleton() {
  return <WideResultSkeleton />;
}

/* Exported on its own so the rag_feedback "pending" payload can render the
 * coach skeleton in place of the inline spinner (the event already carries
 * its own "Coach note" section marker). */
export function CoachSkeleton() {
  return <WideResultSkeleton />;
}

/**
 * Position-reserving, shape-aware trailing skeleton. Rendered once at the
 * bottom of the (append-only) transcript, shaped like the *next* widget so the
 * real event replaces it in place with minimal layout shift. `taskLabel` is the
 * deterministic next-activity label derived from the session blueprint.
 */
export function TaskChatLoadingSkeleton({
  type,
  taskLabel,
}: {
  type: TaskChatLoadingType;
  taskLabel?: string;
}) {
  if (!type) return null;

  if (type === "teacher_loading") {
    return <TeachingBubbleSkeleton />;
  }

  if (type === "activity_loading" || type === "next_activity_loading") {
    return (
      <>
        <SectionMarker tone="task" icon={<FileText size={13} />}>
          {taskLabel || "Practice task"}
        </SectionMarker>
        <TaskCardSkeleton />
      </>
    );
  }

  if (type === "evaluation_loading") {
    return (
      <>
        <SectionMarker tone="score" icon={<Sparkles size={13} />}>
          Activity score
        </SectionMarker>
        <ScoreCardSkeleton />
      </>
    );
  }

  if (type === "feedback_loading") {
    return (
      <>
        <SectionMarker tone="feedback" icon={<Sparkles size={13} />}>
          Activity feedback
        </SectionMarker>
        <FeedbackCardSkeleton />
      </>
    );
  }

  // completing — hold space for the final scorecard + coach note together.
  return (
    <>
      <SectionMarker tone="score" icon={<Sparkles size={13} />}>
        Final scorecard
      </SectionMarker>
      <FinalScorecardSkeleton />
      <SectionMarker tone="feedback" icon={<Sparkles size={13} />}>
        Coach note
      </SectionMarker>
      <CoachSkeleton />
    </>
  );
}
