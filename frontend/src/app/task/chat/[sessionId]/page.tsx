"use client";

import { useCallback, useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { LayoutDashboard, MoreHorizontal, RotateCcw } from "lucide-react";

import { api } from "@/lib/api";

import { tasksApi } from "@/lib/tasks-api";
import {
  extensionForMime,
  isVoiceRecordingSupported,
  useVoiceRecorder,
} from "@/lib/hooks/useVoiceRecorder";
import { markDailyChatEntered, markScorecardViewed } from "@/lib/daily-session-entry";
import {
  TaskChatLoadingSkeleton,
  type TaskChatLoadingType,
} from "@/components/task/TaskChatSkeletons";
import { AppConfirmDialog } from "@/components/ui/AppConfirmDialog";
import { SessionScorecard as DaySessionScorecard } from "@/components/sessions/SessionScorecard";
import { type SessionScorecardRead, type PronunciationResult } from "@/lib/sessions-api";
import {
  FillBlanksWidget,
  ErrorSpottingWidget,
  ErrorCorrectionWidget,
  ListenAndRespondWidget,
  MCQWidget,
  normalizeWidgetKey,
  OpenTextWidget,
  SpeakRecordWidget,
  StoryboardWidget,
  StructuredEssayWidget,
  TimedTextWidget,
} from "@/components/task/task-widgets";
import type {
  AnyTaskPayload,
  WidgetKey,
  WidgetProps,
} from "@/components/task/task-widgets";

/* ── Score / Feedback payloads (rendered by chat session, not by widgets) ── */
interface ScorecardPayload {
  overall_score: number;
  skill_name: string;
  topic: string;
  total?: number;
  correct_count?: number;
  answered_count?: number;
  questions?: Record<string, unknown>;
  rubric_scores?: Record<string, number>;
  weighted_points?: Record<string, number>;
  subskill_score?: number | null;
}

interface FeedbackError {
  question_id: string;
  user_answer: string;
  correct_answer: string;
  correction?: string | null;
  error_type: string;
  why_wrong: string;
  rule: string;
  memory_tip: string;
}

interface FeedbackPayload {
  overall_message?: string;
  widget?: string;
  errors?: FeedbackError[];
  summary?: string;
  did_well?: string[];
  mistakes?: Array<{
    issue: string;
    user_wrote?: string | null;
    correction?: string | null;
    rule?: string | null;
    sub_skills_affected?: string[];
  }>;
  score: number;
  overall_level?: string;
  practice_suggestion?: string;
  next_tip?: string | null;
  sub_skill_breakdown?: Record<string, number>;
}

/* ── Pronunciation result payload ─────────────────────────────────────── */
interface PronunciationResultPayload {
  pronunciation: PronunciationResult;
  raw_score: number;
  reference_text: string;
  feedback: {
    score: number;
    summary?: string;
    did_well?: string[];
    mistakes?: Array<{ issue: string; rule?: string | null }>;
    next_tip?: string | null;
  };
}

/* ── Event log ───────────────────────────────────────────────────────── */
type ChatEvent =
  | { kind: "chat"; role: "ai" | "you"; content: string; actions?: string[]; streamId?: string; streaming?: boolean }
  | { kind: "section"; tone: "intro" | "task" | "score" | "feedback"; label: string }
  | { kind: "task"; payload: AnyTaskPayload; submitted: boolean; answers: Record<string, unknown> }
  | { kind: "scorecard"; payload: ScorecardPayload }
  | { kind: "feedback"; payload: FeedbackPayload }
  | { kind: "pronunciation"; payload: PronunciationResultPayload };

type WSIncoming =
  | { type: "chat_message"; role?: string; content?: string; actions?: string[] }
  | { type: "chat_stream_start"; role?: string; stream_id?: string; actions?: string[] }
  | { type: "chat_stream_delta"; role?: string; stream_id?: string; content?: string }
  | { type: "chat_stream_end"; role?: string; stream_id?: string; content?: string; actions?: string[] }
  | { type: "ui_event"; widget: string; payload: Record<string, unknown> }
  | { type: "error"; content?: string };

type WSOutgoing =
  | { type: "user_message"; content: string }
  | { type: "task_submission"; answers: Record<string, unknown> }
  | { type: "follow_up_action"; action: string };

/* ── Widget dispatch ─────────────────────────────────────────────────── */
const WIDGET_COMPONENTS: Record<WidgetKey, React.ComponentType<WidgetProps>> = {
  mcq: MCQWidget as React.ComponentType<WidgetProps>,
  fill_in_blanks: FillBlanksWidget as React.ComponentType<WidgetProps>,
  open_text: OpenTextWidget as React.ComponentType<WidgetProps>,
  timed_text: TimedTextWidget as React.ComponentType<WidgetProps>,
  structured_essay: StructuredEssayWidget as React.ComponentType<WidgetProps>,
  speak_and_record: SpeakRecordWidget as React.ComponentType<WidgetProps>,
  listen_and_respond: ListenAndRespondWidget as React.ComponentType<WidgetProps>,
  error_spotting: ErrorSpottingWidget as React.ComponentType<WidgetProps>,
  storyboard: StoryboardWidget as React.ComponentType<WidgetProps>,
  error_correction: ErrorCorrectionWidget as React.ComponentType<WidgetProps>,
};

const WIDGET_SECTION_LABEL: Record<WidgetKey, string> = {
  mcq: "Multiple choice",
  fill_in_blanks: "Fill in the blanks",
  open_text: "Writing task",
  timed_text: "Timed writing",
  structured_essay: "Essay",
  speak_and_record: "Speaking task",
  listen_and_respond: "Listening task",
  error_spotting: "Error spotting",
  storyboard: "Storyboard",
  error_correction: "Error correction",
};

function showsInlineActivityScore(widget: WidgetKey): boolean {
  return (
    widget === "fill_in_blanks" ||
    widget === "listen_and_respond" ||
    widget === "error_spotting"
  );
}

function isWritingSpeakingWidget(widget: WidgetKey): boolean {
  return (
    widget === "open_text" ||
    widget === "timed_text" ||
    widget === "structured_essay" ||
    widget === "speak_and_record" ||
    widget === "storyboard" ||
    widget === "error_correction"
  );
}

function isOpenEndedFeedbackWidget(widget?: string): boolean {
  const normalized = normalizeWidgetKey(widget ?? "");
  return (
    normalized === "open_text" ||
    normalized === "timed_text" ||
    normalized === "structured_essay" ||
    normalized === "speak_and_record" ||
    normalized === "storyboard" ||
    normalized === "error_correction"
  );
}

function isKnownWidget(widget: string): widget is WidgetKey {
  return normalizeWidgetKey(widget) in WIDGET_COMPONENTS;
}

function shouldShowActivitySkeletonAfterChat(content?: string) {
  const text = (content || "").toLowerCase();
  return (
    text.includes("here is activity") ||
    text.includes("here is your practice task") ||
    text.includes("continue with activity")
  );
}

function agentDebugLog(message: string, data: Record<string, unknown>, hypothesisId: string) {
  // #region agent log
  fetch('http://127.0.0.1:7588/ingest/7b2f1294-46b7-45e6-9e45-9caa7b81d367',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'dfa507'},body:JSON.stringify({sessionId:'dfa507',runId:'initial',hypothesisId,location:'frontend/src/app/task/chat/[sessionId]/page.tsx',message,data,timestamp:Date.now()})}).catch(()=>{});
  // #endregion
}

/* ── Icons ───────────────────────────────────────────────────────────── */
function BackIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M10 12L6 8L10 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function SendIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
      <path d="M14 8L2.5 3L5 8L2.5 13L14 8Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" fill="currentColor" />
    </svg>
  );
}
function MicIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <rect x="6" y="2" width="4" height="7" rx="2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M3.5 8a4.5 4.5 0 0 0 9 0M8 13v1.5M5.5 14.5h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}
function SparkIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
      <path d="M7 1L8 5L12 6L8 7L7 11L6 7L2 6L6 5L7 1Z" fill="currentColor" />
    </svg>
  );
}
function TaskIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
      <path d="M3 3.5h6M3 7h8M3 10.5h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M11 9.5l1 1 2-2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function CheckIcon({ color = "white" }: { color?: string }) {
  return (
    <svg width="11" height="11" viewBox="0 0 12 12" fill="none">
      <path d="M3 6.5L5 8.5L9 4" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function XIcon() {
  return (
    <svg width="11" height="11" viewBox="0 0 12 12" fill="none">
      <path d="M3.5 3.5L8.5 8.5M8.5 3.5L3.5 8.5" stroke="white" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
function LogoIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 18 18" fill="none">
      <path d="M3.5 14L9 4L14.5 14" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M5.7 10.5h6.6" stroke="white" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

/* ── Sub-components ──────────────────────────────────────────────────── */
function Topbar({
  skillLabel,
  sceneLabel,
  onRestart,
  restarting,
}: {
  skillLabel: string;
  sceneLabel: string;
  onRestart: () => void;
  restarting: boolean;
}) {
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!menuOpen) return;
    const handlePointerDown = (event: PointerEvent) => {
      if (!menuRef.current?.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [menuOpen]);

  const goToDashboard = () => {
    setMenuOpen(false);
    router.push("/dashboard");
  };

  const restart = () => {
    setMenuOpen(false);
    onRestart();
  };

  return (
    <div style={{
      position: "sticky", top: 0, zIndex: 50,
      backdropFilter: "blur(24px)", WebkitBackdropFilter: "blur(24px)",
      background: "rgba(232,240,252,0.55)",
      borderBottom: "1px solid rgba(140,170,220,0.14)",
    }}>
      <div style={{
        maxWidth: 880, margin: "0 auto", padding: "14px 20px",
        display: "flex", alignItems: "center", gap: 12,
      }}>
        <button
          aria-label="Back to dashboard"
          onClick={() => router.push("/dashboard")}
          style={{
            width: 36, height: 36, borderRadius: "50%",
            background: "white", border: "1px solid oklch(85% 0.025 240)",
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            color: "oklch(28% 0.08 245)", cursor: "pointer",
          }}
        >
          <BackIcon />
        </button>

        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 34, height: 34, borderRadius: 9, background: "oklch(52% 0.18 240)",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 4px 12px rgba(60,100,200,0.3)",
          }}>
            <LogoIcon />
          </div>
          <span style={{ fontSize: 16, fontWeight: 800, letterSpacing: "-0.02em", color: "oklch(20% 0.09 245)" }}>
            LingosAI
          </span>
        </div>

        <span style={{
          display: "inline-flex", alignItems: "center", gap: 6,
          padding: "5px 11px", borderRadius: 999,
          background: "oklch(94% 0.05 145)", border: "1px solid oklch(82% 0.1 150)",
          fontSize: 12, fontWeight: 700, color: "oklch(35% 0.13 150)",
          textTransform: "capitalize",
        }}>
          {skillLabel} · {sceneLabel}
        </span>

        <div style={{ flex: 1 }} />

        <div ref={menuRef} style={{ position: "relative" }}>
          <button
            aria-label="Session options"
            aria-haspopup="menu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((open) => !open)}
            style={{
              width: 36, height: 36, borderRadius: "50%",
              background: "white", border: "1px solid oklch(85% 0.025 240)",
              display: "inline-flex", alignItems: "center", justifyContent: "center",
              color: "oklch(28% 0.08 245)", cursor: "pointer",
            }}
          >
            <MoreHorizontal size={17} strokeWidth={2.4} />
          </button>

          {menuOpen && (
            <div
              role="menu"
              aria-label="Session options"
              style={{
                position: "absolute",
                top: 44,
                right: 0,
                width: 210,
                padding: 6,
                borderRadius: 14,
                background: "white",
                border: "1px solid oklch(85% 0.025 240)",
                boxShadow: "0 14px 34px rgba(35,55,100,0.18)",
              }}
            >
              <button
                role="menuitem"
                disabled={restarting}
                onClick={restart}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "10px 11px",
                  borderRadius: 10,
                  border: "none",
                  background: "transparent",
                  color: "oklch(28% 0.08 245)",
                  fontSize: 13,
                  fontWeight: 700,
                  fontFamily: "inherit",
                  cursor: restarting ? "not-allowed" : "pointer",
                  opacity: restarting ? 0.55 : 1,
                  textAlign: "left",
                }}
              >
                <RotateCcw size={15} />
                {restarting ? "Restarting..." : "Restart session"}
              </button>
              <button
                role="menuitem"
                onClick={goToDashboard}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "10px 11px",
                  borderRadius: 10,
                  border: "none",
                  background: "transparent",
                  color: "oklch(28% 0.08 245)",
                  fontSize: 13,
                  fontWeight: 700,
                  fontFamily: "inherit",
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                <LayoutDashboard size={15} />
                Back to dashboard
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ChatBubble({
  role,
  name,
  children,
  actions,
  streaming,
  onAction,
}: {
  role: "ai" | "you";
  name?: string;
  children: React.ReactNode;
  actions?: string[];
  streaming?: boolean;
  onAction?: (label: string) => void;
}) {
  const isAi = role === "ai";
  return (
    <div style={{
      display: "flex", gap: 10, marginBottom: 12,
      alignItems: "flex-end",
      flexDirection: isAi ? "row" : "row-reverse",
      animation: "fadeIn 0.4s ease both",
    }}>
      <div style={{
        width: 30, height: 30, borderRadius: "50%",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 12, fontWeight: 800, color: "white",
        flexShrink: 0, marginBottom: 2,
        background: isAi ? "oklch(52% 0.18 240)" : "oklch(20% 0.09 245)",
        boxShadow: "0 2px 6px rgba(60,100,200,0.18)",
      }}>
        {isAi ? "L" : "U"}
      </div>
      <div style={{ maxWidth: "78%", display: "flex", flexDirection: "column", gap: 3, alignItems: isAi ? "flex-start" : "flex-end" }}>
        {name && (
          <div style={{ fontSize: 11, fontWeight: 700, color: "oklch(45% 0.07 240)", padding: "0 4px", letterSpacing: "0.02em" }}>
            {name}
          </div>
        )}
        <div style={{
          padding: "13px 16px", borderRadius: 18,
          fontSize: 14.5, lineHeight: 1.55, wordWrap: "break-word",
          ...(isAi ? {
            background: "white", color: "oklch(18% 0.06 240)",
            border: "1px solid oklch(85% 0.025 240)",
            borderBottomLeftRadius: 6,
            boxShadow: "0 2px 10px rgba(80,110,180,0.06)",
          } : {
            background: "oklch(52% 0.18 240)", color: "white",
            borderBottomRightRadius: 6,
            boxShadow: "0 4px 14px rgba(60,100,200,0.25)",
          }),
        }}>
          {children}
          {isAi && streaming && (
            <span
              aria-hidden
              style={{
                display: "inline-block",
                width: 7,
                height: 16,
                marginLeft: 3,
                borderRadius: 999,
                background: "oklch(52% 0.18 240)",
                verticalAlign: "-3px",
                animation: "streamPulse 0.9s ease-in-out infinite",
              }}
            />
          )}
          {isAi && actions && actions.length > 0 && (
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 }}>
              {actions.map((label) => (
                <button
                  key={label}
                  onClick={() => onAction?.(label)}
                  style={{
                    padding: "7px 13px", borderRadius: 999,
                    background: "white", border: "1px solid oklch(85% 0.025 240)",
                    fontSize: 12.5, fontWeight: 600, color: "oklch(20% 0.09 245)",
                    cursor: "pointer", fontFamily: "inherit",
                    transition: "all 0.15s",
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function SectionMarker({
  kind,
  icon,
  children,
}: {
  kind: "intro" | "task" | "score" | "feedback";
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  const colors: Record<string, string> = {
    intro: "oklch(52% 0.18 240)",
    task: "oklch(48% 0.18 290)",
    score: "oklch(40% 0.16 155)",
    feedback: "oklch(48% 0.16 60)",
  };
  return (
    <div style={{ display: "flex", justifyContent: "center", margin: "10px 0 14px" }}>
      <div style={{
        display: "inline-flex", alignItems: "center", gap: 7,
        padding: "6px 13px", borderRadius: 999,
        background: "white", border: "1px solid oklch(85% 0.025 240)",
        fontSize: 12.5, fontWeight: 700, letterSpacing: "0.01em",
        color: colors[kind],
        boxShadow: "0 2px 8px rgba(80,110,180,0.06)",
        animation: "fadeIn 0.4s ease both",
      }}>
        {icon}
        <span>{children}</span>
      </div>
    </div>
  );
}

function ScoreRing({ pct }: { pct: number }) {
  const r = 38;
  const c = 2 * Math.PI * r;
  const off = c - (pct / 100) * c;
  return (
    <div style={{ position: "relative", width: 92, height: 92, flexShrink: 0 }}>
      <svg width="92" height="92" viewBox="0 0 92 92">
        <circle cx="46" cy="46" r={r} stroke="oklch(92% 0.025 240)" strokeWidth="9" fill="none" />
        <circle
          cx="46" cy="46" r={r}
          stroke="url(#ringGrad)" strokeWidth="9" fill="none"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={off}
          transform="rotate(-90 46 46)"
          style={{ transition: "stroke-dashoffset 1.2s ease" }}
        />
        <defs>
          <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="oklch(52% 0.18 240)" />
            <stop offset="100%" stopColor="oklch(72% 0.12 200)" />
          </linearGradient>
        </defs>
      </svg>
      <div style={{
        position: "absolute", inset: 0,
        display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column",
        fontWeight: 800, color: "oklch(20% 0.09 245)",
      }}>
        <span style={{ fontSize: 22, lineHeight: 1, letterSpacing: "-0.02em" }}>
          {pct}<span style={{ fontSize: 13, color: "oklch(45% 0.07 240)", fontWeight: 700 }}>%</span>
        </span>
        <span style={{ fontSize: 10, color: "oklch(45% 0.07 240)", fontWeight: 700, letterSpacing: "0.05em", marginTop: 2 }}>
          SCORE
        </span>
      </div>
    </div>
  );
}

function countTaskItems(taskPayload: AnyTaskPayload): number {
  switch (taskPayload.widget) {
    case "open_text":
      return (taskPayload.items ?? []).length || 1;
    case "structured_essay":
      return (taskPayload.sections ?? []).length || 1;
    case "storyboard":
      return (taskPayload.scenes ?? []).length || 1;
    case "speak_and_record": {
      const p = taskPayload;
      if (p.turns && p.turns.length > 0) return p.turns.filter((t) => t.speaker === "user").length || 1;
      if (p.speaking_prompts && p.speaking_prompts.length > 0) return p.speaking_prompts.length;
      if (p.speaking_items && p.speaking_items.length > 0) return p.speaking_items.length;
      return 1;
    }
    case "timed_text":
      return 1;
    default:
      return (taskPayload as { total?: number }).total ?? 1;
  }
}

function countSubmittedRecordings(taskAnswers?: Record<string, unknown>): number {
  const recordings = taskAnswers?.recordings;
  if (!Array.isArray(recordings)) return 0;
  return recordings.filter(
    (row) =>
      typeof row === "object" &&
      row !== null &&
      typeof (row as { transcript?: string }).transcript === "string" &&
      (row as { transcript: string }).transcript.trim().length > 0,
  ).length;
}

function buildScoreBannerLabel(
  taskPayload: AnyTaskPayload | null,
  taskAnswers?: Record<string, unknown>,
): string {
  if (taskPayload?.widget === "speak_and_record") {
    const total = taskPayload ? countTaskItems(taskPayload) : 1;
    const submitted = countSubmittedRecordings(taskAnswers);
    if (submitted > 0) {
      return submitted === 1
        ? "1 recording submitted"
        : total > 1
          ? `${submitted} of ${total} recordings submitted`
          : `${submitted} recordings submitted`;
    }
  }
  const total = taskPayload ? countTaskItems(taskPayload) : 1;
  return total === 1 ? "1 question attended" : `${total} out of ${total} attended`;
}

function InlineScoreBanner({
  scorePayload,
  taskPayload,
  taskAnswers,
}: {
  scorePayload: ScorecardPayload;
  taskPayload: AnyTaskPayload | null;
  taskAnswers?: Record<string, unknown>;
}) {
  const pct = scorePayload.overall_score <= 10
    ? Math.round(scorePayload.overall_score * 10)
    : Math.round(scorePayload.overall_score);
  const label = buildScoreBannerLabel(taskPayload, taskAnswers);
  return (
    <div
      style={{
        borderRadius: 14,
        padding: "14px 18px",
        marginBottom: 16,
        marginTop: 4,
        display: "flex",
        alignItems: "center",
        gap: 14,
        background: "white",
        border: "1.5px solid oklch(85% 0.025 240)",
        boxShadow: "0 2px 10px rgba(80,110,180,0.07)",
        animation: "fadeIn 0.4s ease both",
      }}
    >
      <div className="tw-result-icon">
        <SparkIcon />
      </div>
      <div className="tw-result-text">
        <div className="tw-result-headline">{label}</div>
        <div className="tw-result-sub">Review the feedback below.</div>
      </div>
      <div>
        <div className="tw-result-score">
          {pct}<span style={{ fontSize: 14 }}>%</span>
        </div>
        <div className="tw-result-score-sub">SCORE</div>
      </div>
    </div>
  );
}

function Scorecard({ payload }: { payload: ScorecardPayload }) {
  const pct = payload.overall_score <= 10
    ? Math.round(payload.overall_score * 10)
    : payload.overall_score;
  const correctCount = payload.correct_count ?? Math.round(payload.overall_score);
  const total = payload.total ?? 10;
  const rubricCount = Object.keys(payload.rubric_scores ?? {}).length;
  return (
    <div style={{
      borderRadius: 22, padding: 24,
      background: "linear-gradient(135deg, oklch(94% 0.06 240) 0%, white 60%)",
      border: "1.5px solid rgba(255,255,255,0.92)",
      boxShadow: "0 8px 32px rgba(80,110,180,0.16)",
      animation: "fadeIn 0.4s ease both",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 18 }}>
        <div>
          <div style={{ fontSize: 18, fontWeight: 800, color: "oklch(20% 0.09 245)", letterSpacing: "-0.01em", textTransform: "capitalize" }}>
            {payload.skill_name} — {payload.topic}
          </div>
          <div style={{ fontSize: 13, color: "oklch(45% 0.07 240)", marginTop: 3 }}>
            {payload.subskill_score != null
              ? `Grammar score: ${payload.subskill_score}/10`
              : rubricCount > 0
                ? `${rubricCount} rubric areas checked`
                : `${correctCount} of ${total} correct`}
          </div>
        </div>
        <ScoreRing pct={pct} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginTop: 16 }}>
        {[
          {
            num: payload.subskill_score != null
              ? `${payload.subskill_score}/10`
              : `${payload.overall_score}/10`,
            lbl: payload.subskill_score != null ? "Skill score" : "Raw score",
          },
          {
            num: payload.subskill_score != null
              ? `${payload.answered_count ?? correctCount}/${total}`
              : String(rubricCount || total),
            lbl: payload.subskill_score != null ? "Items done" : "Rubrics",
          },
          { num: `${pct}%`, lbl: "Score" },
        ].map((s) => (
          <div key={s.lbl} style={{
            background: "white", borderRadius: 12, padding: "12px 14px",
            border: "1px solid oklch(85% 0.025 240)",
          }}>
            <div style={{ fontSize: 20, fontWeight: 800, color: "oklch(20% 0.09 245)", letterSpacing: "-0.02em" }}>{s.num}</div>
            <div style={{ fontSize: 11.5, fontWeight: 600, color: "oklch(45% 0.07 240)", marginTop: 2, letterSpacing: "0.02em" }}>{s.lbl}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function FeedbackCard({ payload }: { payload: FeedbackPayload }) {
  const errors = payload.errors ?? [];
  const mistakes = payload.mistakes ?? [];
  const summary = payload.summary || payload.overall_message || "";
  const openEndedFeedback = isOpenEndedFeedbackWidget(payload.widget);
  const errorSpottingFeedback = normalizeWidgetKey(payload.widget ?? "") === "error_spotting";
  return (
    <div style={{
      borderRadius: 22,
      marginBottom: 24,
      background: "rgba(255,255,255,0.85)",
      backdropFilter: "blur(18px)", WebkitBackdropFilter: "blur(18px)",
      border: "1.5px solid rgba(255,255,255,0.92)",
      boxShadow: "0 4px 28px rgba(80,110,180,0.1)",
      overflow: "hidden",
      animation: "fadeIn 0.4s ease both",
    }}>
      {errors.length === 0 && mistakes.length === 0 && (
        <div style={{ padding: "20px 22px", display: "flex", gap: 14, alignItems: "center" }}>
          <div style={{
            width: 26, height: 26, borderRadius: "50%", flexShrink: 0,
            display: "flex", alignItems: "center", justifyContent: "center",
            background: "oklch(55% 0.16 155)",
          }}>
            <CheckIcon />
          </div>
          <div style={{ fontSize: 13.5, color: "oklch(18% 0.06 240)", lineHeight: 1.55 }}>
            {summary || "No major issues found."} {payload.practice_suggestion || payload.next_tip || ""}
          </div>
        </div>
      )}
      {mistakes.length > 0 && (
        <>
          <div style={{ padding: "16px 20px", borderBottom: "1px solid oklch(85% 0.025 240)" }}>
            <div style={{ fontSize: 13.5, color: "oklch(18% 0.06 240)", lineHeight: 1.55 }}>
              {summary}
            </div>
            {payload.did_well && payload.did_well.length > 0 && (
              <div style={{ marginTop: 8, fontSize: 12.5, color: "oklch(45% 0.07 240)", lineHeight: 1.5 }}>
                {payload.did_well.join(" ")}
              </div>
            )}
          </div>
          {mistakes.map((mistake, i) => {
            const falsePositive =
              errorSpottingFeedback && mistake.correction === "Do not flag this word";
            return (
            <div key={`${mistake.issue}-${i}`} style={{
              padding: "16px 20px",
              borderBottom: i < mistakes.length - 1 ? "1px solid oklch(85% 0.025 240)" : "none",
              display: "flex", gap: 14,
            }}>
              <div style={{
                width: 26, height: 26, borderRadius: "50%", flexShrink: 0,
                display: "flex", alignItems: "center", justifyContent: "center",
                background: openEndedFeedback ? "oklch(60% 0.15 60)" : "oklch(58% 0.2 25)",
                color: "white",
              }}>
                {openEndedFeedback ? <SparkIcon /> : <XIcon />}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 13.5, color: "oklch(18% 0.06 240)", marginBottom: 6, lineHeight: 1.55 }}>
                  {errorSpottingFeedback ? (
                    falsePositive ? (
                      <strong>{mistake.issue}</strong>
                    ) : (
                      <>
                        {mistake.user_wrote && (
                          <span style={{
                            display: "inline-block", padding: "0 6px", borderRadius: 4,
                            fontWeight: 700, margin: "0 1px",
                            background: "oklch(92% 0.08 25)",
                            color: "oklch(35% 0.18 25)",
                            textDecoration: "line-through",
                          }}>
                            {mistake.user_wrote}
                          </span>
                        )}
                        {mistake.user_wrote && mistake.correction && " -> "}
                        {mistake.correction && (
                          <span style={{
                            display: "inline-block", padding: "0 6px", borderRadius: 4,
                            fontWeight: 700, margin: "0 1px",
                            background: "oklch(92% 0.1 155)",
                            color: "oklch(28% 0.16 155)",
                          }}>
                            {mistake.correction}
                          </span>
                        )}
                      </>
                    )
                  ) : (
                    <strong>{mistake.issue}</strong>
                  )}
                  {!errorSpottingFeedback && openEndedFeedback && mistake.user_wrote && (
                    <div style={{ marginTop: 8 }}>
                      <strong style={{ color: "oklch(42% 0.07 240)" }}>Your version:</strong>{" "}
                      <span style={{
                        display: "inline-block", padding: "1px 6px", borderRadius: 4,
                        fontWeight: 650, margin: "0 1px",
                        background: "oklch(96% 0.018 245)",
                        color: "oklch(35% 0.07 240)",
                      }}>
                        {mistake.user_wrote}
                      </span>
                    </div>
                  )}
                  {!errorSpottingFeedback && openEndedFeedback && mistake.correction && (
                    <div style={{ marginTop: 6 }}>
                      <strong style={{ color: "oklch(42% 0.07 240)" }}>Improved version:</strong>{" "}
                      <span style={{
                        display: "inline-block", padding: "1px 6px", borderRadius: 4,
                        fontWeight: 700, margin: "0 1px",
                        background: "oklch(92% 0.1 155)",
                        color: "oklch(28% 0.16 155)",
                      }}>
                        {mistake.correction}
                      </span>
                    </div>
                  )}
                  {!errorSpottingFeedback && !openEndedFeedback && mistake.user_wrote && (
                    <>
                      {": "}
                      <span style={{
                        display: "inline-block", padding: "0 6px", borderRadius: 4,
                        fontWeight: 700, margin: "0 1px",
                        background: "oklch(92% 0.08 25)",
                        color: "oklch(35% 0.18 25)",
                        textDecoration: mistake.correction ? "line-through" : "none",
                      }}>
                        {mistake.user_wrote}
                      </span>
                    </>
                  )}
                  {!errorSpottingFeedback && !openEndedFeedback && mistake.correction && (
                    <>
                      {" -> "}
                      <span style={{
                        display: "inline-block", padding: "0 6px", borderRadius: 4,
                        fontWeight: 700, margin: "0 1px",
                        background: "oklch(92% 0.1 155)", color: "oklch(28% 0.16 155)",
                      }}>
                        {mistake.correction}
                      </span>
                    </>
                  )}
                </div>
                {(mistake.rule || payload.next_tip) && (
                  <div style={{
                    fontSize: 13, color: "oklch(45% 0.07 240)", lineHeight: 1.55,
                    background: "oklch(96% 0.025 245)",
                    borderRadius: 10, padding: "10px 12px", marginTop: 4,
                  }}>
                    {mistake.rule && <div><strong>Rule:</strong> {mistake.rule}</div>}
                    {payload.next_tip && i === mistakes.length - 1 && (
                      <div style={{ marginTop: mistake.rule ? 4 : 0 }}>
                        <strong>Next:</strong> {payload.next_tip}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
            );
          })}
        </>
      )}
      {errors.map((err, i) => (
        <div key={err.question_id} style={{
          padding: "16px 20px",
          borderBottom: i < errors.length - 1 ? "1px solid oklch(85% 0.025 240)" : "none",
          display: "flex", gap: 14,
        }}>
          <div style={{
            width: 26, height: 26, borderRadius: "50%", flexShrink: 0,
            display: "flex", alignItems: "center", justifyContent: "center",
            background: "oklch(58% 0.2 25)",
          }}>
            <XIcon />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 13.5, color: "oklch(18% 0.06 240)", marginBottom: 6, lineHeight: 1.55 }}>
              <strong>{err.question_id}.</strong>{" "}
              <span style={{
                display: "inline-block", padding: "0 6px", borderRadius: 4,
                fontWeight: 700, margin: "0 1px",
                background: "oklch(92% 0.08 25)",
                color: "oklch(35% 0.18 25)",
                textDecoration: "line-through",
              }}>
                {err.user_answer || "—"}
              </span>{" "}→{" "}
              <span style={{
                display: "inline-block", padding: "0 6px", borderRadius: 4,
                fontWeight: 700, margin: "0 1px",
                background: "oklch(92% 0.1 155)", color: "oklch(28% 0.16 155)",
              }}>
                {err.correct_answer}
              </span>
            </div>
            <div style={{
              fontSize: 13, color: "oklch(45% 0.07 240)", lineHeight: 1.55,
              background: "oklch(96% 0.025 245)",
              borderRadius: 10, padding: "10px 12px", marginTop: 4,
            }}>
              <div><strong>Why:</strong> {err.why_wrong}</div>
              <div style={{ marginTop: 4 }}><strong>Rule:</strong> {err.rule}</div>
              <div style={{ marginTop: 4 }}><strong>Memory tip:</strong> {err.memory_tip}</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function ChatPronunciationCard({ payload }: { payload: PronunciationResultPayload }) {
  const { pronunciation: p, raw_score, reference_text, feedback } = payload;

  function scoreColor(score: number) {
    if (score >= 80) return "oklch(48% 0.18 155)";
    if (score >= 60) return "oklch(60% 0.13 80)";
    return "oklch(50% 0.15 25)";
  }
  function scoreBg(score: number) {
    if (score >= 80) return "oklch(96% 0.02 155)";
    if (score >= 60) return "oklch(98% 0.01 80)";
    return "oklch(98% 0.01 25)";
  }

  const pct = raw_score <= 10 ? Math.round(raw_score * 10) : Math.round(raw_score);
  const overallBg =
    pct >= 80 ? "oklch(48% 0.18 155)" :
    pct >= 60 ? "oklch(52% 0.18 240)" :
    pct >= 40 ? "oklch(60% 0.13 80)" :
               "oklch(58% 0.2 15)";

  const scores = [
    { label: "Accuracy", score: p.accuracy_score, desc: "Phoneme precision" },
    { label: "Fluency", score: p.fluency_score, desc: "Pacing \u0026 pauses" },
    { label: "Completeness", score: p.completeness_score, desc: "Words spoken" },
    ...(p.prosody_score != null && p.prosody_score > 0
      ? [{ label: "Prosody", score: p.prosody_score, desc: "Stress \u0026 rhythm" }]
      : []),
  ];

  return (
    <div
      style={{
        borderRadius: 22,
        background: "rgba(255,255,255,0.92)",
        backdropFilter: "blur(18px)",
        WebkitBackdropFilter: "blur(18px)",
        border: "1.5px solid rgba(255,255,255,0.92)",
        boxShadow: "0 8px 32px rgba(80,110,180,0.13)",
        overflow: "hidden",
        animation: "fadeIn 0.4s ease both",
        marginBottom: 16,
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "20px 22px 16px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: "1px solid oklch(92% 0.01 245)",
        }}
      >
        <div>
          <div style={{ fontSize: 17, fontWeight: 800, color: "oklch(20% 0.09 245)", letterSpacing: "-0.01em" }}>
            Pronunciation Assessment
          </div>
          <div style={{ fontSize: 13, color: "oklch(45% 0.07 240)", marginTop: 3 }}>
            {feedback.summary || "Here is your detailed pronunciation feedback."}
          </div>
        </div>
        <div
          style={{
            background: overallBg,
            color: "white",
            borderRadius: 10,
            padding: "10px 16px",
            fontWeight: 800,
            fontSize: 20,
            minWidth: 72,
            textAlign: "center",
            boxShadow: "0 4px 14px rgba(0,0,0,0.08)",
            lineHeight: 1,
          }}
        >
          {pct}<span style={{ fontSize: 13, opacity: 0.85 }}>%</span>
        </div>
      </div>

      {/* Score breakdown bars */}
      <div style={{ padding: "16px 22px", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12 }}>
        {scores.map((s) => (
          <div
            key={s.label}
            style={{
              background: scoreBg(s.score),
              border: "1px solid oklch(93% 0.01 245)",
              padding: "12px 14px",
              borderRadius: 12,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
              <span style={{ fontSize: 13, fontWeight: 700, color: "oklch(20% 0.09 245)" }}>{s.label}</span>
              <span style={{ fontSize: 14, fontWeight: 800, color: scoreColor(s.score) }}>{s.score.toFixed(0)}%</span>
            </div>
            <div style={{ width: "100%", height: 6, background: "oklch(93% 0.01 245)", borderRadius: 999, overflow: "hidden" }}>
              <div style={{ width: `${s.score}%`, height: "100%", background: scoreColor(s.score), borderRadius: 999, transition: "width 1s ease" }} />
            </div>
            <div style={{ fontSize: 11, color: "oklch(45% 0.07 240)", marginTop: 5 }}>{s.desc}</div>
          </div>
        ))}
      </div>

      {/* Word-level breakdown */}
      <div style={{ padding: "4px 22px 16px" }}>
        <div style={{ fontSize: 11.5, textTransform: "uppercase", letterSpacing: 0.8, fontWeight: 700, color: "oklch(50% 0.05 240)", marginBottom: 8 }}>
          How you read it
        </div>
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "8px 5px",
            lineHeight: 1.8,
            fontSize: 15,
            padding: "14px 16px",
            background: "oklch(99% 0.01 245)",
            border: "1px solid oklch(93% 0.01 245)",
            borderRadius: 12,
          }}
        >
          {p.words.map((w, i) => {
            let color = "oklch(48% 0.18 155)";
            let bg = "transparent";
            let textDecoration = "none";
            let fontWeight = 500;

            if (w.error_type === "omission") {
              color = "oklch(60% 0.1 20)";
              textDecoration = "line-through";
              fontWeight = 400;
            } else if (w.error_type === "insertion") {
              color = "oklch(50% 0.15 45)";
              bg = "oklch(96% 0.05 45)";
              fontWeight = 700;
            } else if (w.error_type === "mispronunciation") {
              color = "oklch(50% 0.15 25)";
              bg = "oklch(96% 0.05 25)";
              fontWeight = 700;
            } else if (w.accuracy_score < 80) {
              color = "oklch(60% 0.13 80)";
              fontWeight = 600;
            }

            return (
              <span
                key={i}
                title={`Accuracy: ${w.accuracy_score}%${w.error_type && w.error_type !== "none" ? ` (${w.error_type})` : ""}`}
                style={{
                  color,
                  backgroundColor: bg,
                  textDecoration,
                  fontWeight,
                  padding: bg !== "transparent" ? "2px 6px" : "0 2px",
                  borderRadius: 4,
                  cursor: "help",
                }}
              >
                {w.word}
              </span>
            );
          })}
        </div>

        {/* Legend */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px 16px", fontSize: 11.5, color: "oklch(45% 0.07 240)", marginTop: 8, paddingLeft: 2 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
            <span style={{ width: 9, height: 9, borderRadius: "50%", background: "oklch(48% 0.18 155)" }} />
            <span>Good (\u226580%)</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
            <span style={{ width: 9, height: 9, borderRadius: "50%", background: "oklch(60% 0.13 80)" }} />
            <span>Needs work</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
            <span style={{ width: 9, height: 9, borderRadius: "50%", background: "oklch(50% 0.15 25)" }} />
            <span>Mispronounced</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
            <span style={{ textDecoration: "line-through", color: "oklch(60% 0.1 20)", fontWeight: 700, fontSize: 12 }}>Aa</span>
            <span>Omitted</span>
          </div>
        </div>
      </div>

      {/* Reference passage */}
      {reference_text && (
        <div style={{ padding: "0 22px 16px" }}>
          <div style={{ fontSize: 11.5, textTransform: "uppercase", letterSpacing: 0.8, fontWeight: 700, color: "oklch(50% 0.05 240)", marginBottom: 8 }}>
            Model passage
          </div>
          <div
            style={{
              padding: "14px 16px",
              background: "oklch(96% 0.02 245)",
              borderRadius: 12,
              fontSize: 14,
              lineHeight: 1.65,
              color: "oklch(20% 0.09 245)",
              borderLeft: "4px solid oklch(62% 0.16 240)",
            }}
          >
            {reference_text}
          </div>
        </div>
      )}

      {/* Coaching tips from LLM feedback */}
      {(feedback.did_well?.length || feedback.mistakes?.length || feedback.next_tip) && (
        <div style={{ padding: "0 22px 20px", display: "flex", flexDirection: "column", gap: 12, borderTop: "1px solid oklch(92% 0.01 245)", paddingTop: 16 }}>
          <div style={{ fontSize: 11.5, textTransform: "uppercase", letterSpacing: 0.8, fontWeight: 700, color: "oklch(50% 0.05 240)", marginBottom: 2 }}>
            Coach&apos;s tips
          </div>

          {feedback.did_well && feedback.did_well.length > 0 && (
            <div>
              <div style={{ fontSize: 12.5, fontWeight: 700, color: "oklch(48% 0.18 155)", marginBottom: 4 }}>What you did well</div>
              <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13, lineHeight: 1.6, color: "oklch(20% 0.09 245)" }}>
                {feedback.did_well.map((item, idx) => (
                  <li key={idx} style={{ marginBottom: 2 }}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {feedback.mistakes && feedback.mistakes.length > 0 && (
            <div>
              <div style={{ fontSize: 12.5, fontWeight: 700, color: "oklch(50% 0.15 25)", marginBottom: 4 }}>Areas to improve</div>
              {feedback.mistakes.map((m, idx) => (
                <div key={idx} style={{ background: "oklch(98% 0.01 25)", padding: "8px 12px", borderRadius: 8, borderLeft: "3px solid oklch(65% 0.15 25)", marginBottom: 6 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "oklch(20% 0.09 245)" }}>{m.issue}</div>
                  {m.rule && <div style={{ fontSize: 12, color: "oklch(45% 0.07 240)", marginTop: 2 }}>{m.rule}</div>}
                </div>
              ))}
            </div>
          )}

          {feedback.next_tip && (
            <div style={{ background: "oklch(96% 0.03 245)", padding: "10px 14px", borderRadius: 8, fontSize: 13 }}>
              <span style={{ fontWeight: 700, color: "oklch(52% 0.18 240)" }}>Next tip: </span>
              <span style={{ color: "oklch(20% 0.09 245)" }}>{feedback.next_tip}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const MAX_RECORD_MS = 60_000;

function StopGlyph() {
  return (
    <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
      <rect x="4" y="4" width="8" height="8" rx="1.5" fill="currentColor" />
    </svg>
  );
}
function Spinner() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="8" r="6" stroke="currentColor" strokeOpacity="0.25" strokeWidth="2" />
      <path d="M14 8a6 6 0 0 0-6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <animateTransform attributeName="transform" type="rotate" from="0 8 8" to="360 8 8" dur="0.9s" repeatCount="indefinite" />
      </path>
    </svg>
  );
}

function formatElapsed(ms: number): string {
  const total = Math.floor(ms / 1000);
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function ProgressRing({ progress }: { progress: number }) {
  const size = 36;
  const stroke = 2.5;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - Math.min(1, Math.max(0, progress)));
  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      style={{
        position: "absolute",
        inset: 0,
        transform: "rotate(-90deg)",
      }}
    >
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="rgba(0,112,196,0.15)"
        strokeWidth={stroke}
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="#0070C4"
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        style={{ transition: "stroke-dashoffset 200ms linear" }}
      />
    </svg>
  );
}

function subscribeVoiceSupport(onStoreChange: () => void) {
  if (typeof window === "undefined") return () => {};
  const id = window.setTimeout(onStoreChange, 0);
  return () => window.clearTimeout(id);
}

function voiceSupportSnapshot() {
  return isVoiceRecordingSupported();
}

function voiceSupportServerSnapshot() {
  return false;
}

function Composer({
  value,
  onChange,
  onSend,
  placeholder,
}: {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  placeholder: string;
}) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const recorder = useVoiceRecorder();
  const voiceSupported = useSyncExternalStore(
    subscribeVoiceSupport,
    voiceSupportSnapshot,
    voiceSupportServerSnapshot,
  );
  const autoStoppedRef = useRef(false);

  const isVoiceBusy =
    recorder.state === "recording" ||
    recorder.state === "transcribing";

  const insertTranscript = (transcript: string) => {
    const clean = transcript.trim();
    if (!clean) return;
    const el = ref.current;
    let next: string;
    let cursorPos: number;
    if (el && typeof el.selectionStart === "number") {
      const start = el.selectionStart;
      const end = el.selectionEnd ?? start;
      const before = value.slice(0, start);
      const after = value.slice(end);
      const needsLeadingSpace = before.length > 0 && !/\s$/.test(before);
      const needsTrailingSpace = after.length > 0 && !/^\s/.test(after);
      const insert =
        (needsLeadingSpace ? " " : "") +
        clean +
        (needsTrailingSpace ? " " : "");
      next = before + insert + after;
      cursorPos = (before + insert).length;
    } else {
      const sep = value.length > 0 && !/\s$/.test(value) ? " " : "";
      next = value + sep + clean;
      cursorPos = next.length;
    }
    onChange(next);
    // Restore cursor on the next tick (after React re-renders).
    requestAnimationFrame(() => {
      if (ref.current) {
        ref.current.focus();
        try {
          ref.current.setSelectionRange(cursorPos, cursorPos);
        } catch {
          /* ignore */
        }
        ref.current.style.height = "auto";
        ref.current.style.height = Math.min(140, ref.current.scrollHeight) + "px";
      }
    });
  };

  const finalizeRecording = useCallback(async () => {
    const blob = await recorder.stop();
    if (!blob || blob.size === 0) {
      recorder.setError("No audio captured. Try again.");
      return;
    }
    recorder.setTranscribing(true);
    try {
      const ext = extensionForMime(recorder.mimeType || "audio/webm");
      const result = await tasksApi.transcribeAudio(blob, `voice${ext}`);
      const transcript = (result.transcript || "").trim();
      if (!transcript) {
        recorder.setError("No speech detected.");
        return;
      }
      insertTranscript(transcript);
      recorder.setTranscribing(false);
    } catch {
      recorder.setError("Couldn't transcribe — try again.");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [recorder, value]);

  // Auto-finalize when the 1-minute cap is hit.
  useEffect(() => {
    if (
      recorder.state === "recording" &&
      recorder.elapsedMs >= MAX_RECORD_MS &&
      !autoStoppedRef.current
    ) {
      autoStoppedRef.current = true;
      finalizeRecording();
    }
    if (recorder.state === "idle" || recorder.state === "error") {
      autoStoppedRef.current = false;
    }
  }, [recorder.state, recorder.elapsedMs, finalizeRecording]);

  // Clear an error if the user starts typing.
  useEffect(() => {
    if (recorder.state === "error" && value.length > 0) {
      recorder.setError(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
    if (ref.current) {
      ref.current.style.height = "auto";
      ref.current.style.height = Math.min(140, ref.current.scrollHeight) + "px";
    }
  };

  const handleMicClick = async () => {
    if (recorder.state === "idle" || recorder.state === "error") {
      await recorder.start();
    } else if (recorder.state === "recording") {
      autoStoppedRef.current = true;
      await finalizeRecording();
    }
  };

  const progress = Math.min(1, recorder.elapsedMs / MAX_RECORD_MS);
  const sendDisabled = !value.trim() || isVoiceBusy;

  const micTitle = (() => {
    switch (recorder.state) {
      case "recording": return "Stop recording";
      case "transcribing": return "Transcribing…";
      case "error": return recorder.errorMessage ?? "Try again";
      default: return "Record voice message";
    }
  })();

  return (
    <div style={{
      position: "fixed", bottom: 0, left: 0, right: 0, zIndex: 40,
      padding: "14px 20px 18px",
      background: "linear-gradient(to bottom, rgba(232,240,252,0) 0%, rgba(232,240,252,0.7) 50%, rgba(232,240,252,0.92) 100%)",
      backdropFilter: "blur(8px)", WebkitBackdropFilter: "blur(8px)",
    }}>
      {(isVoiceBusy || recorder.state === "error") && (
        <div style={{
          maxWidth: 720, margin: "0 auto 6px",
          display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 8,
          fontSize: 12, color: recorder.state === "error" ? "#c0392b" : "oklch(40% 0.08 240)",
        }}>
          {recorder.state === "error" ? (
            <span>{recorder.errorMessage}</span>
          ) : recorder.state === "transcribing" ? (
            <span>Transcribing…</span>
          ) : (
            <span>{formatElapsed(recorder.elapsedMs)} / 1:00</span>
          )}
        </div>
      )}
      <div style={{
        maxWidth: 720, margin: "0 auto",
        display: "flex", alignItems: "flex-end", gap: 10,
        background: "white", borderRadius: 22,
        padding: "8px 8px 8px 18px",
        border: "1.5px solid rgba(255,255,255,0.92)",
        boxShadow: "0 8px 28px rgba(80,110,180,0.18)",
      }}>
        <textarea
          ref={ref}
          rows={1}
          placeholder={placeholder}
          value={value}
          onChange={handleChange}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              if (!sendDisabled) onSend();
            }
          }}
          style={{
            flex: 1, resize: "none", border: "none", background: "transparent",
            fontSize: 14.5, lineHeight: 1.5, color: "oklch(18% 0.06 240)",
            padding: "9px 0", maxHeight: 140, minHeight: 22,
            fontFamily: "inherit",
            outline: "none",
          }}
        />
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          {voiceSupported && (
            <div style={{ position: "relative", width: 36, height: 36 }}>
              {recorder.state === "recording" && (
                <ProgressRing progress={progress} />
              )}
              <button
                type="button"
                onClick={handleMicClick}
                disabled={recorder.state === "transcribing"}
                title={micTitle}
                aria-label={micTitle}
                style={{
                  position: "absolute", inset: 0,
                  width: 36, height: 36, borderRadius: "50%",
                  background: recorder.state === "recording"
                    ? "rgba(0,112,196,0.08)"
                    : "transparent",
                  border: "none",
                  color: recorder.state === "error" ? "#c0392b" : "oklch(45% 0.07 240)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  cursor: recorder.state === "transcribing" ? "wait" : "pointer",
                }}
              >
                {recorder.state === "transcribing" ? (
                  <Spinner />
                ) : recorder.state === "recording" ? (
                  <StopGlyph />
                ) : (
                  <MicIcon />
                )}
              </button>
            </div>
          )}
          <button
            onClick={onSend}
            disabled={sendDisabled}
            style={{
              width: 38, height: 38, borderRadius: "50%",
              background: "#0070C4", color: "white", border: "none",
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: "0 4px 12px rgba(0,112,196,0.35)",
              cursor: sendDisabled ? "not-allowed" : "pointer",
              opacity: sendDisabled ? 0.5 : 1,
            }}
          >
            <SendIcon />
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── Main page ───────────────────────────────────────────────────────── */
export default function ChatSessionPage() {
  const params = useParams<{ sessionId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const sessionId = params?.sessionId;

  useEffect(() => {
    if (typeof sessionId === "string" && sessionId.length > 0) {
      markDailyChatEntered(sessionId);
    }
  }, [sessionId]);

  const initialConnectionState = useMemo<
    "connecting" | "open" | "closed" | "error"
  >(() => {
    if (typeof window === "undefined") return "connecting";
    return localStorage.getItem("token") ? "connecting" : "error";
  }, []);

  const [events, setEvents] = useState<ChatEvent[]>([]);
  const [composer, setComposer] = useState("");
  const [connectionState, setConnectionState] = useState(initialConnectionState);
  const [skillName, setSkillName] = useState("");
  const [phase, setPhase] = useState<"teaching" | "practice" | "submitted" | "ended">("teaching");
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const [loadingType, setLoadingType] = useState<TaskChatLoadingType>(
    initialConnectionState === "connecting" ? "teacher_loading" : null,
  );
  const [restarting, setRestarting] = useState(false);
  const [restartDialogOpen, setRestartDialogOpen] = useState(false);
  const [daySessionScorecard, setDaySessionScorecard] =
    useState<SessionScorecardRead | null>(null);
  const [daySessionScorecardError, setDaySessionScorecardError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const pendingSendsRef = useRef<WSOutgoing[]>([]);
  const stageRef = useRef<HTMLDivElement>(null);
  const eventsRef = useRef<ChatEvent[]>(events);

  useEffect(() => {
    eventsRef.current = events;
  }, [events]);

  useEffect(() => {
    if (phase !== "ended") return;
    if (typeof sessionId !== "string" || sessionId.length === 0) return;
    if (daySessionScorecard !== null) return;

    let cancelled = false;
    Promise.resolve().then(() => {
      if (!cancelled) setDaySessionScorecardError(null);
    });
    api
      .get<SessionScorecardRead>(`/api/learning/sessions/${sessionId}/scorecard`)
      .then((r) => {
        if (cancelled) return;
        setDaySessionScorecard(r.data);
        markScorecardViewed(r.data.session_id);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const detail =
          (err as { response?: { data?: { detail?: string } }; message?: string })
            ?.response?.data?.detail ||
          (err as { message?: string })?.message ||
          "Could not load your session scorecard.";
        setDaySessionScorecardError(detail);
      });

    return () => {
      cancelled = true;
    };
  }, [phase, sessionId, daySessionScorecard]);

  useEffect(() => {
    if (phase === "ended") return;
    if (connectionState !== "closed" && connectionState !== "error") return;
    if (typeof sessionId !== "string" || sessionId.length === 0) return;
    if (daySessionScorecard !== null) return;

    let cancelled = false;
    api
      .get<SessionScorecardRead>(`/api/learning/sessions/${sessionId}/scorecard`)
      .then((r) => {
        if (cancelled) return;
        setDaySessionScorecard(r.data);
        markScorecardViewed(r.data.session_id);
        setPhase("ended");
        setLoadingType(null);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        // Only surface the error if the session genuinely has no scorecard yet
        // (i.e. it is still in-progress). For completed sessions the scorecard
        // fetch should always succeed with the corrected URL above.
        const status = (err as { response?: { status?: number } })?.response?.status;
        if (status && status !== 404) {
          const detail =
            (err as { response?: { data?: { detail?: string } }; message?: string })
              ?.response?.data?.detail ||
            (err as { message?: string })?.message ||
            "Could not load your session scorecard.";
          setDaySessionScorecardError(detail);
          setPhase("ended");
          setLoadingType(null);
        }
        // 404 = session not yet complete; keep the "connection closed" UI.
      });

    return () => {
      cancelled = true;
    };
  }, [connectionState, phase, sessionId, daySessionScorecard]);

  const lastTaskIdx = useMemo(() => {
    for (let i = events.length - 1; i >= 0; i -= 1) {
      if (events[i].kind === "task") return i;
    }
    return -1;
  }, [events]);

  const handleIncoming = useCallback((msg: WSIncoming) => {
    if (msg.type === "chat_message") {
      setLoadingType((curr) =>
        shouldShowActivitySkeletonAfterChat(msg.content)
          ? "activity_loading"
          : curr === "teacher_loading" ||
              curr === "next_activity_loading" ||
              curr === "feedback_loading"
            ? null
            : curr,
      );
      if (
        msg.actions?.includes("Go to dashboard") &&
        !msg.actions.includes("Next activity")
      ) {
        setPhase("ended");
      }
      const role = msg.role === "user" || msg.role === "you" ? "you" : "ai";
      setEvents((prev) => [
        ...prev,
        {
          kind: "chat",
          role,
          content: msg.content || "",
          actions: msg.actions,
        },
      ]);
      return;
    }
    if (msg.type === "chat_stream_start") {
      setLoadingType((curr) =>
        curr === "teacher_loading" || curr === "next_activity_loading" ? null : curr,
      );
      const streamId = msg.stream_id || `stream-${Date.now()}`;
      const role = msg.role === "user" || msg.role === "you" ? "you" : "ai";
      setEvents((prev) => [
        ...prev,
        {
          kind: "chat",
          role,
          content: "",
          streamId,
          streaming: true,
        },
      ]);
      return;
    }
    if (msg.type === "chat_stream_delta") {
      const streamId = msg.stream_id;
      const delta = msg.content || "";
      if (!streamId || !delta) return;
      setEvents((prev) => {
        let found = false;
        const next = prev.map((evt) => {
          if (evt.kind !== "chat" || evt.streamId !== streamId) return evt;
          found = true;
          return { ...evt, content: evt.content + delta, streaming: true };
        });
        if (found) return next;
        return [
          ...prev,
          {
            kind: "chat",
            role: "ai",
            content: delta,
            streamId,
            streaming: true,
          },
        ];
      });
      return;
    }
    if (msg.type === "chat_stream_end") {
      setLoadingType((curr) =>
        shouldShowActivitySkeletonAfterChat(msg.content)
          ? "activity_loading"
          : curr === "teacher_loading" || curr === "next_activity_loading"
            ? null
            : curr,
      );
      if (
        msg.actions?.includes("Go to dashboard") &&
        !msg.actions.includes("Next activity")
      ) {
        setPhase("ended");
      }
      const streamId = msg.stream_id;
      if (!streamId) {
        if (msg.content) {
          setEvents((prev) => [
            ...prev,
            { kind: "chat", role: "ai", content: msg.content || "", actions: msg.actions },
          ]);
        }
        return;
      }
      setEvents((prev) => {
        let found = false;
        const next = prev.map((evt) => {
          if (evt.kind !== "chat" || evt.streamId !== streamId) return evt;
          found = true;
          return {
            ...evt,
            content: msg.content ?? evt.content,
            actions: msg.actions,
            streaming: false,
          };
        });
        if (found) return next;
        if (!msg.content) return prev;
        return [
          ...prev,
          {
            kind: "chat",
            role: "ai",
            content: msg.content,
            actions: msg.actions,
            streamId,
            streaming: false,
          },
        ];
      });
      return;
    }
    if (msg.type === "ui_event") {
      const widget = normalizeWidgetKey(msg.widget);
      if (isKnownWidget(widget)) {
        setLoadingType(null);
        const payload = {
          ...msg.payload,
          widget,
        } as unknown as AnyTaskPayload;
        if (widget === "listen_and_respond") {
          const listenPayload = payload as AnyTaskPayload & {
            audio_url?: string | null;
            browser_tts_fallback?: boolean;
            audio_script?: string;
            inner_widget?: string;
            items?: unknown[];
            tts_error?: string;
          };
          agentDebugLog(
            "Received listen_and_respond ui_event",
            {
              audio_url_present: Boolean(listenPayload.audio_url),
              audio_url: listenPayload.audio_url,
              browser_tts_fallback: listenPayload.browser_tts_fallback,
              audio_script_len: listenPayload.audio_script?.length ?? 0,
              inner_widget: listenPayload.inner_widget,
              items_len: Array.isArray(listenPayload.items) ? listenPayload.items.length : null,
              phase: (msg.payload as { phase?: string }).phase,
              archetype_id: (msg.payload as { archetype_id?: string }).archetype_id,
              tts_error: listenPayload.tts_error,
            },
            "H2,H3",
          );
        }
        const topicName =
          (payload as { topic_name?: string; topic?: string }).topic_name ||
          (payload as { topic_name?: string; topic?: string }).topic ||
          "";
        setSkillName((curr) => curr || topicName);
        setEvents((prev) => [
          ...prev,
          { kind: "section", tone: "task", label: WIDGET_SECTION_LABEL[widget] },
          { kind: "task", payload, submitted: false, answers: {} },
        ]);
        setPhase("practice");
        return;
      }
      if (msg.widget === "pronunciation_result") {
        setLoadingType(null);
        const payload = msg.payload as unknown as PronunciationResultPayload;
        setEvents((prev) => [
          ...prev,
          { kind: "section", tone: "score", label: "Pronunciation assessment" },
          { kind: "pronunciation", payload },
        ]);
        setPhase("submitted");
        return;
      }
      if (msg.widget === "scorecard") {
        setLoadingType("feedback_loading");
        const payload = msg.payload as unknown as ScorecardPayload;
        setSkillName((curr) => curr || payload.skill_name || "");
        setEvents((prev) => [
          ...prev,
          { kind: "section", tone: "score", label: "Activity score" },
          { kind: "scorecard", payload },
        ]);
        setPhase("submitted");
        return;
      }
      if (msg.widget === "feedback_card") {
        setLoadingType(null);
        const payload = msg.payload as unknown as FeedbackPayload;
        setEvents((prev) => [
          ...prev,
          { kind: "section", tone: "feedback", label: "Activity feedback" },
          { kind: "feedback", payload },
        ]);
        return;
      }
      // Unknown widget — surface as a chat message so the session doesn't get stuck silently.
      setLoadingType(null);
      setEvents((prev) => [
        ...prev,
        {
          kind: "chat",
          role: "ai",
          content: `This activity uses the ${msg.widget.replace(/_/g, " ")} widget, which isn't supported yet.`,
        },
      ]);
      return;
    }
    if (msg.type === "error") {
      setLoadingType(null);
      setEvents((prev) => [
        ...prev,
        { kind: "chat", role: "ai", content: `⚠️ ${msg.content || "Something went wrong."}` },
      ]);
    }
  }, []);

  /* --- WebSocket lifecycle ---------------------------------------- */
  useEffect(() => {
    if (!sessionId) return;
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    if (!token) return;

    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const wsBase = apiBase.replace(/^http/, "ws");
    const url = `${wsBase}/ws/learning/${sessionId}?token=${encodeURIComponent(token || "")}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      if (wsRef.current !== ws) return;
      setConnectionState("open");
      setLoadingType((curr) => curr ?? (eventsRef.current.length === 0 ? "teacher_loading" : null));
      setEvents((prev) => prev.filter((e) => e.kind === "chat"));
      const queued = pendingSendsRef.current.splice(0);
      queued.forEach((payload) => ws.send(JSON.stringify(payload)));
    };
    ws.onclose = () => {
      if (wsRef.current === ws) {
        setConnectionState("closed");
        setLoadingType(null);
      }
    };
    ws.onerror = () => {
      if (wsRef.current === ws) {
        setConnectionState("error");
        setLoadingType(null);
      }
    };

    ws.onmessage = (raw) => {
      if (wsRef.current !== ws) return;
      try {
        const msg = JSON.parse(raw.data) as WSIncoming;
        handleIncoming(msg);
      } catch (err) {
        console.error("Bad WS payload", err);
      }
    };

    return () => {
      ws.close();
      if (wsRef.current === ws) wsRef.current = null;
    };
  }, [sessionId, handleIncoming, reconnectAttempt]);

  const send = useCallback((payload: WSOutgoing) => {
    // This local loading phase mirrors WebSocket waits only; backend session phase remains authoritative.
    if (payload.type === "task_submission") {
      setLoadingType("feedback_loading");
    } else if (payload.type === "follow_up_action") {
      setLoadingType(
        payload.action.trim().toLowerCase() === "next activity"
          ? "next_activity_loading"
          : "teacher_loading",
      );
    } else {
      setLoadingType("teacher_loading");
    }
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(payload));
      return;
    }
    pendingSendsRef.current.push(payload);
    setConnectionState("connecting");
    setReconnectAttempt((attempt) => attempt + 1);
  }, []);

  function handleSendComposer() {
    const trimmed = composer.trim();
    if (!trimmed) return;

    if (phase === "submitted" || phase === "ended") {
      setEvents((prev) => [...prev, { kind: "chat", role: "you", content: trimmed }]);
      send({ type: "follow_up_action", action: trimmed });
    } else {
      setEvents((prev) => [...prev, { kind: "chat", role: "you", content: trimmed }]);
      send({ type: "user_message", content: trimmed });
    }
    setComposer("");
  }

  function handleAction(label: string) {
    if (label === "Go to dashboard") {
      router.push("/dashboard");
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ["task", "next"] });
        queryClient.invalidateQueries({ queryKey: ["me"] });
      }, 0);
      return;
    }
    setEvents((prev) => [...prev, { kind: "chat", role: "you", content: label }]);
    send({ type: "follow_up_action", action: label });
    if (label === "Next activity") setPhase("practice");
  }

  function requestRestartSession() {
    if (!sessionId || restarting) return;
    setRestartDialogOpen(true);
  }

  async function confirmRestartSession() {
    if (!sessionId || restarting) return;

    setRestarting(true);
    setLoadingType("teacher_loading");
    try {
      const restartPath = `/api/learning/sessions/${encodeURIComponent(sessionId)}/restart`;
      const res = await api.post<{
        session_id: string;
        topic: string;
        skill_name: string;
        task_type: string;
        user_task_id?: number | null;
        message: string;
      }>(restartPath);

      pendingSendsRef.current = [];
      wsRef.current?.close();
      wsRef.current = null;
      setEvents([]);
      setComposer("");
      setPhase(res.data.message === "Session complete" ? "ended" : "teaching");
      setSkillName(res.data.skill_name || "");
      setConnectionState("connecting");
      setReconnectAttempt((attempt) => attempt + 1);
      markDailyChatEntered(res.data.session_id);
      queryClient.invalidateQueries({ queryKey: ["task", "next"] });
      setRestartDialogOpen(false);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } }; message?: string })
          ?.response?.data?.detail ||
        (err as { message?: string })?.message ||
        "Could not restart this session.";
      setLoadingType(null);
      setEvents((prev) => [
        ...prev,
        { kind: "chat", role: "ai", content: detail },
      ]);
      setRestartDialogOpen(false);
    } finally {
      setRestarting(false);
    }
  }

  const setTaskAnswers = useCallback((eventIdx: number, next: Record<string, unknown>) => {
    setEvents((prev) =>
      prev.map((e, i) =>
        i === eventIdx && e.kind === "task" ? { ...e, answers: next } : e,
      ),
    );
  }, []);

  const handleSubmitTask = useCallback((
    eventIdx: number,
    answersOverride?: Record<string, unknown>,
  ) => {
    const evt = eventsRef.current[eventIdx];
    if (!evt || evt.kind !== "task" || evt.submitted) return;
    const answers = answersOverride ?? evt.answers ?? {};
    send({ type: "task_submission", answers });
    setEvents((prev) =>
      prev.map((e, i) =>
        i === eventIdx && e.kind === "task"
          ? { ...e, submitted: true, answers }
          : e,
      ),
    );
    setPhase("submitted");
  }, [send]);

  /* --- Render ----------------------------------------------------- */
  const sceneLabel =
    phase === "teaching" ? "Intro"
    : phase === "practice" ? "Practice"
    : phase === "submitted" ? "Results"
    : "Wrap up";

  const composerPlaceholder =
    phase === "teaching" ? "Type your answer…"
    : phase === "practice" ? "Use the task above…"
    : "Ask a follow-up question…";

  const hasActiveAiStream = events.some(
    (evt) => evt.kind === "chat" && evt.role === "ai" && evt.streaming,
  );
  const hasFeedback = events.some((evt) => evt.kind === "feedback" || evt.kind === "pronunciation");
  const visibleLoadingType: TaskChatLoadingType =
    loadingType === "teacher_loading" && hasActiveAiStream
      ? null
      : loadingType === "feedback_loading" && hasFeedback
        ? null
        : loadingType;

  return (
    <>
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />
      <style>{`
        *, *::before, *::after { box-sizing: border-box; }
        body { overflow-x: hidden; }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes streamPulse {
          0%, 100% { opacity: 0.25; transform: scaleY(0.75); }
          50% { opacity: 1; transform: scaleY(1); }
        }
        strong { font-weight: 700; }
        em { font-style: italic; }
      `}</style>

      <div style={{
        minHeight: "100vh",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        background: "oklch(91% 0.04 245)",
        position: "relative",
        color: "oklch(18% 0.06 240)",
      }}>
        <div aria-hidden style={{
          position: "fixed", inset: 0, pointerEvents: "none",
          backgroundImage: "radial-gradient(circle, rgba(90,130,210,0.13) 1px, transparent 1px)",
          backgroundSize: "22px 22px", zIndex: 0,
        }} />

        <Topbar
          skillLabel={skillName || "Lesson"}
          sceneLabel={sceneLabel}
          onRestart={requestRestartSession}
          restarting={restarting}
        />

        <AppConfirmDialog
          open={restartDialogOpen}
          title="Restart chat session?"
          description="Your completed dashboard activities will stay completed. This only restarts the chat teaching flow."
          confirmLabel="Restart session"
          loadingLabel="Restarting..."
          isLoading={restarting}
          tone="warning"
          onCancel={() => setRestartDialogOpen(false)}
          onConfirm={confirmRestartSession}
        />

        <main ref={stageRef} style={{
          position: "relative", zIndex: 1,
          maxWidth: 720, margin: "0 auto",
          padding: "28px 20px 200px",
        }}>
          <SectionMarker kind="intro" icon={<SparkIcon />}>Intro</SectionMarker>

          {events.map((evt, i) => {
            if (evt.kind === "chat") {
              return (
                <ChatBubble
                  key={i}
                  role={evt.role}
                  name={i === 0 && evt.role === "ai" ? "LingosAI" : undefined}
                  actions={evt.actions}
                  streaming={evt.streaming}
                  onAction={handleAction}
                >
                  {evt.content}
                </ChatBubble>
              );
            }
            if (evt.kind === "section") {
              // Widgets that show their own inline score tile suppress this marker.
              if (evt.tone === "score") {
                const lastTask = events.slice(0, i).reverse().find((e) => e.kind === "task");
                if (
                  lastTask?.kind === "task" &&
                  (showsInlineActivityScore(lastTask.payload.widget) ||
                    isWritingSpeakingWidget(lastTask.payload.widget))
                ) {
                  return null;
                }
              }
              return (
                <SectionMarker
                  key={i}
                  kind={evt.tone}
                  icon={evt.tone === "task" ? <TaskIcon /> : <SparkIcon />}
                >
                  {evt.label}
                </SectionMarker>
              );
            }
            if (evt.kind === "task") {
              const widget = evt.payload.widget;
              const Widget = WIDGET_COMPONENTS[widget];
              if (!Widget) {
                return (
                  <ChatBubble key={i} role="ai">
                    This activity uses the {widget.replace(/_/g, " ")} widget, which isn&apos;t supported yet.
                  </ChatBubble>
                );
              }
              return (
                <Widget
                  key={i}
                  payload={evt.payload}
                  answers={evt.answers}
                  setAnswers={(next) => setTaskAnswers(i, next)}
                  state={evt.submitted ? "after" : "before"}
                  onSubmit={(answers) => handleSubmitTask(i, answers)}
                />
              );
            }
            if (evt.kind === "scorecard") {
              const lastTask = events.slice(0, i).reverse().find((e) => e.kind === "task");
              if (lastTask?.kind === "task") {
                if (showsInlineActivityScore(lastTask.payload.widget)) {
                  return null;
                }
                if (isWritingSpeakingWidget(lastTask.payload.widget)) {
                  return (
                    <InlineScoreBanner
                      key={i}
                      scorePayload={evt.payload}
                      taskPayload={lastTask.payload}
                      taskAnswers={lastTask.answers}
                    />
                  );
                }
              }
              return <Scorecard key={i} payload={evt.payload} />;
            }
            if (evt.kind === "feedback") {
              return <FeedbackCard key={i} payload={evt.payload} />;
            }
            if (evt.kind === "pronunciation") {
              return <ChatPronunciationCard key={i} payload={evt.payload} />;
            }
            return null;
          })}

          <TaskChatLoadingSkeleton type={visibleLoadingType} />

          {connectionState !== "open" && phase !== "ended" && !visibleLoadingType && (
            <div style={{ marginTop: 16 }}>
              <ChatBubble role="ai" name={events.length === 0 ? "LingosAI" : undefined}>
                {connectionState === "connecting" && "Connecting to your session…"}
                {connectionState === "closed" && "Connection closed. Refresh to reconnect."}
                {connectionState === "error" && "Could not reach the session. Make sure you're signed in."}
              </ChatBubble>
            </div>
          )}

          {phase === "ended" && (
            <div style={{ marginTop: 24 }}>
              {daySessionScorecard ? (
                <DaySessionScorecard
                  scorecard={daySessionScorecard}
                  onGoToDashboard={() => {
                    queryClient.invalidateQueries({ queryKey: ["sessions", "today-plan"] });
                    queryClient.invalidateQueries({ queryKey: ["me"] });
                    router.push("/dashboard");
                  }}
                />
              ) : daySessionScorecardError ? (
                <ChatBubble role="ai">
                  Could not load your session scorecard: {daySessionScorecardError}
                </ChatBubble>
              ) : (
                <ChatBubble role="ai">Loading your session scorecard…</ChatBubble>
              )}
            </div>
          )}

          <div style={{ height: 60 }} />
        </main>

        <Composer
          value={composer}
          onChange={setComposer}
          onSend={handleSendComposer}
          placeholder={composerPlaceholder}
        />
        {/* lastTaskIdx is exposed for future scroll-into-view; keeps lint quiet */}
        <span data-last-task={lastTaskIdx} style={{ display: "none" }} />
      </div>
    </>
  );
}
