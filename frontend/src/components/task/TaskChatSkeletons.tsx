"use client";

import type React from "react";

export type TaskChatLoadingType =
  | "teacher_loading"
  | "activity_loading"
  | "feedback_loading"
  | "next_activity_loading"
  | null;

function SkeletonBlock({
  className = "",
  rounded = "rounded-full",
}: {
  className?: string;
  rounded?: string;
}) {
  return (
    <div
      aria-hidden
      className={`${rounded} bg-slate-200/80 animate-pulse ${className}`}
    />
  );
}

function LoadingStatus({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label={label}
      className="tw-root tw-fade-in"
    >
      <span className="sr-only">{label}</span>
      {children}
    </div>
  );
}

export function ChatMessageStreamingSkeleton() {
  return (
    <LoadingStatus label="LingosAI is preparing a response">
      <div className="mb-3 flex items-end gap-2.5">
        <div className="flex h-[30px] w-[30px] shrink-0 items-center justify-center rounded-full bg-[#0070C4] text-xs font-extrabold text-white shadow-sm">
          L
        </div>
        <div className="flex max-w-[78%] flex-col items-start gap-1">
          <div className="px-1 text-[11px] font-bold tracking-[0.02em] text-slate-500">
            LingosAI
          </div>
          <div className="rounded-[18px] rounded-bl-md border border-slate-200 bg-white px-4 py-3 shadow-sm">
            <div className="flex h-[22px] items-center gap-2">
              <SkeletonBlock className="h-2.5 w-20" />
              <SkeletonBlock className="h-2.5 w-28" />
              <SkeletonBlock className="h-2.5 w-12" />
            </div>
          </div>
        </div>
      </div>
    </LoadingStatus>
  );
}

export function ActivityCardSkeleton() {
  return (
    <LoadingStatus label="Preparing the activity">
      <div className="rounded-[22px] border border-white/90 bg-white/80 p-5 shadow-[0_8px_32px_rgba(80,110,180,0.12)] backdrop-blur">
        <div className="mb-5 border-b border-dashed border-slate-200 pb-5">
          <SkeletonBlock className="mb-2 h-3 w-28" />
          <SkeletonBlock className="mb-3 h-6 w-3/4" rounded="rounded-lg" />
          <SkeletonBlock className="mb-2 h-3.5 w-full" />
          <SkeletonBlock className="h-3.5 w-2/3" />
          <div className="mt-4 flex flex-wrap gap-2">
            <SkeletonBlock className="h-7 w-20" />
            <SkeletonBlock className="h-7 w-24" />
            <SkeletonBlock className="h-7 w-16" />
          </div>
        </div>

        {[0, 1, 2].map((row) => (
          <div
            key={row}
            className="mb-3 rounded-2xl border border-slate-200 bg-white p-4"
          >
            <div className="mb-3 flex items-center gap-3">
              <SkeletonBlock className="h-7 w-7" rounded="rounded-lg" />
              <SkeletonBlock className="h-4 flex-1" rounded="rounded-md" />
            </div>
            <div className="grid gap-2">
              <SkeletonBlock className="h-11 w-full" rounded="rounded-xl" />
              <SkeletonBlock className="h-11 w-full" rounded="rounded-xl" />
            </div>
          </div>
        ))}

        <SkeletonBlock className="mt-4 h-12 w-full" rounded="rounded-2xl" />
      </div>
    </LoadingStatus>
  );
}

export function FeedbackCardSkeleton() {
  return (
    <LoadingStatus label="Generating feedback">
      <div className="mb-6 overflow-hidden rounded-[22px] border border-white/90 bg-white/85 shadow-[0_4px_28px_rgba(80,110,180,0.1)] backdrop-blur">
        {[0, 1, 2].map((item) => (
          <div
            key={item}
            className="flex gap-3.5 border-b border-slate-200 p-5 last:border-b-0"
          >
            <SkeletonBlock className="h-7 w-7 shrink-0" />
            <div className="min-w-0 flex-1">
              <SkeletonBlock className="mb-2 h-4 w-5/6" rounded="rounded-md" />
              <SkeletonBlock className="mb-3 h-4 w-2/3" rounded="rounded-md" />
              <div className="rounded-xl bg-slate-50 p-3">
                <SkeletonBlock className="mb-2 h-3.5 w-full" rounded="rounded-md" />
                <SkeletonBlock className="mb-2 h-3.5 w-4/5" rounded="rounded-md" />
                <SkeletonBlock className="h-3.5 w-3/5" rounded="rounded-md" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </LoadingStatus>
  );
}

export function NextActivityTransitionSkeleton() {
  return (
    <LoadingStatus label="Preparing the next activity">
      <ChatMessageStreamingSkeleton />
      <div className="mt-2 rounded-[18px] border border-dashed border-slate-300 bg-white/70 p-4">
        <div className="mb-3 flex items-center gap-3">
          <SkeletonBlock className="h-9 w-9" rounded="rounded-xl" />
          <div className="flex-1">
            <SkeletonBlock className="mb-2 h-4 w-44" rounded="rounded-md" />
            <SkeletonBlock className="h-3 w-32" rounded="rounded-md" />
          </div>
        </div>
        <SkeletonBlock className="h-24 w-full" rounded="rounded-2xl" />
      </div>
    </LoadingStatus>
  );
}

export function TaskChatLoadingSkeleton({
  type,
}: {
  type: TaskChatLoadingType;
}) {
  if (type === "teacher_loading") return <ChatMessageStreamingSkeleton />;
  if (type === "activity_loading") return <ActivityCardSkeleton />;
  if (type === "feedback_loading") return <FeedbackCardSkeleton />;
  if (type === "next_activity_loading") return <NextActivityTransitionSkeleton />;
  return null;
}
