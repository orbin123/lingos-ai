"use client";

import { useCallback, useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { FileText, LayoutDashboard, MessageCircle, MoreHorizontal, RotateCcw, Sparkles } from "lucide-react";

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
} from "@/components/chat/TaskChatSkeletons";
import { AppConfirmDialog } from "@/components/ui/AppConfirmDialog";
import { SessionScorecard as DaySessionScorecard } from "@/components/sessions/SessionScorecard";
import { type SessionScorecardRead, type PronunciationResult } from "@/lib/sessions-api";
import {
  WIDGET_COMPONENTS,
  WIDGET_SECTION_LABEL,
  normalizeWidgetKey,
} from "@/components/chat/runtimeMapping";
import type {
  AnyTaskPayload,
  WidgetKey,
} from "@/components/chat/runtimeMapping";
import {
  RuntimeEvaluationCard,
  RuntimeFeedbackCard,
  RuntimeFinalScorecard,
  RuntimeRagFeedback,
} from "@/components/chat/runtimeReviewMapping";
import { adaptContractTask } from "@/components/chat/contractTaskAdapter";
import { TaskWidgetRenderer } from "@/components/chat/tasks/task_widgets/TaskWidgetRenderer";
import {
  ChatBubble,
  ChatGlobalStyles,
  ChatMain,
  ChatPageShell,
  ChatTopbar,
  LessonMetaCard,
  SectionMarker,
  roundIconButton,
} from "@/components/chat/ChatChrome";

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

interface RuntimeBlueprintPayload {
  blueprint?: {
    teaching?: {
      lesson_goal?: string;
      lesson_description?: string;
      focus?: string;
      topic?: string;
      skill_name?: string;
    };
    activities?: RuntimeActivityContract[];
    final_review?: Record<string, unknown>;
  };
  _session?: RuntimeSessionMeta;
}

type RuntimeBlueprint = NonNullable<RuntimeBlueprintPayload["blueprint"]>;

interface RuntimeSessionMeta {
  theme_type?: string | null;
  cefr_level?: string | null;
  day_number?: number | string | null;
  week_number?: number | string | null;
}

interface LessonMeta {
  title: string;
  focus: string;
  theme: string;
  cefr: string;
  dayNumber: number | null;
}

type RuntimeActivityContract = Record<string, unknown> & {
  activity_id?: string;
  sequence?: number;
  archetype_id?: string;
  activity?: string;
  task_widget?: string;
  evaluation_widget?: string;
  feedback_widget?: string;
};

interface FinalScorecardPayload {
  points_earned?: Record<string, number>;
  skill_labels?: Record<string, string>;
  activities?: Array<{
    sequence?: number;
    archetype_id?: string;
    raw_score?: number;
    base_reward?: number;
  }>;
  mentor_note?: string | null;
}

interface RagFeedbackPayload {
  mentor_note?: string | null;
  available?: boolean;
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
  | { kind: "final_scorecard"; payload: FinalScorecardPayload }
  | { kind: "rag_feedback"; payload: RagFeedbackPayload }
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

function isKnownWidget(widget: string): widget is WidgetKey {
  return normalizeWidgetKey(widget) in WIDGET_COMPONENTS;
}

function findRuntimeActivityContract(
  blueprint: RuntimeBlueprint | null,
  payload: Record<string, unknown>,
): RuntimeActivityContract | null {
  const activities = blueprint?.activities ?? [];
  if (!activities.length) return null;

  const activityId = String(payload.activity_id || "");
  const archetypeId = String(payload.archetype_id || "");
  const sequence = Number(payload.sequence || payload.activity_sequence || 0);

  return (
    activities.find((activity) => activityId && activity.activity_id === activityId) ||
    activities.find((activity) => archetypeId && activity.archetype_id === archetypeId) ||
    activities.find((activity) => sequence > 0 && Number(activity.sequence || 0) === sequence) ||
    null
  );
}

function shouldShowActivitySkeletonAfterChat(content?: string) {
  const text = (content || "").toLowerCase();
  return (
    text.includes("here is activity") ||
    text.includes("here is your practice task") ||
    text.includes("continue with activity")
  );
}

function textValue(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function numberValue(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim()) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function displayLabel(value: string): string {
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function buildLessonEyebrow(meta: LessonMeta): string {
  const parts = [
    meta.theme || "Lesson",
    meta.cefr,
    meta.dayNumber ? `Day ${meta.dayNumber}` : "",
  ].filter(Boolean);
  return parts.join(" · ");
}

function agentDebugLog(message: string, data: Record<string, unknown>, hypothesisId: string) {
  // #region agent log
  fetch('http://127.0.0.1:7588/ingest/7b2f1294-46b7-45e6-9e45-9caa7b81d367',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'dfa507'},body:JSON.stringify({sessionId:'dfa507',runId:'initial',hypothesisId,location:'frontend/src/app/task/chat/[sessionId]/page.tsx',message,data,timestamp:Date.now()})}).catch(()=>{});
  // #endregion
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
/* ── Sub-components ──────────────────────────────────────────────────── */
function Topbar({
  onRestart,
  restarting,
}: {
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
    <ChatTopbar
      subtitle="Chat session"
      onBack={() => router.push("/dashboard")}
      actions={
        <div ref={menuRef} style={{ position: "relative" }}>
          <button
            type="button"
            aria-label="Session options"
            aria-haspopup="menu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((open) => !open)}
            style={{
              ...roundIconButton,
              cursor: "pointer",
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
      }
    />
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
        animation: "chatFadeIn 0.35s ease both",
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
  const [lessonMeta, setLessonMeta] = useState<LessonMeta>({
    title: "Today's lesson",
    focus: "",
    theme: "Lesson",
    cefr: "",
    dayNumber: null,
  });
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
  const eventsRef = useRef<ChatEvent[]>(events);
  const runtimeBlueprintRef = useRef<RuntimeBlueprint | null>(null);

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
      const payloadKind = String(msg.payload?.payload_kind || "");
      if (msg.widget === "session_blueprint" || payloadKind === "session_blueprint") {
        const payload = msg.payload as RuntimeBlueprintPayload;
        const teaching = payload.blueprint?.teaching;
        const sessionMeta = payload._session;
        runtimeBlueprintRef.current = payload.blueprint ?? null;
        setLessonMeta((curr) => ({
          title:
            textValue(teaching?.topic) ||
            textValue(teaching?.lesson_goal) ||
            textValue(teaching?.skill_name) ||
            curr.title,
          focus:
            textValue(teaching?.focus) ||
            textValue(teaching?.lesson_description) ||
            curr.focus,
          theme: displayLabel(textValue(sessionMeta?.theme_type)) || curr.theme,
          cefr: textValue(sessionMeta?.cefr_level) || curr.cefr,
          dayNumber: numberValue(sessionMeta?.day_number) ?? curr.dayNumber,
        }));
        return;
      }
      if (msg.widget === "final_scorecard" || payloadKind === "final_scorecard") {
        setLoadingType(null);
        const payload = msg.payload as unknown as FinalScorecardPayload;
        setEvents((prev) => [
          ...prev,
          { kind: "section", tone: "score", label: "Final scorecard" },
          { kind: "final_scorecard", payload },
        ]);
        return;
      }
      if (msg.widget === "rag_feedback" || payloadKind === "rag_feedback") {
        const payload = msg.payload as unknown as RagFeedbackPayload;
        if (payload.available !== false) {
          setEvents((prev) => [
            ...prev,
            { kind: "section", tone: "feedback", label: "Coach note" },
            { kind: "rag_feedback", payload },
          ]);
        }
        return;
      }
      if (msg.widget === "session_completed" || payloadKind === "completed") {
        setPhase("ended");
        setLoadingType(null);
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
      if (msg.widget === "scorecard" || payloadKind === "evaluation") {
        setLoadingType("feedback_loading");
        const payload = msg.payload as unknown as ScorecardPayload;
        setLessonMeta((curr) => ({
          ...curr,
          title: curr.title === "Today's lesson" ? payload.topic || curr.title : curr.title,
          theme: curr.theme === "Lesson" ? displayLabel(payload.skill_name || "") || curr.theme : curr.theme,
        }));
        setEvents((prev) => [
          ...prev,
          { kind: "section", tone: "score", label: "Activity score" },
          { kind: "scorecard", payload },
        ]);
        setPhase("submitted");
        return;
      }
      if (msg.widget === "feedback_card" || payloadKind === "feedback") {
        setLoadingType(null);
        const payload = msg.payload as unknown as FeedbackPayload;
        setEvents((prev) => [
          ...prev,
          { kind: "section", tone: "feedback", label: "Activity feedback" },
          { kind: "feedback", payload },
        ]);
        return;
      }

      const widget = normalizeWidgetKey(
        String(
          (msg.payload?.task_widget as string | undefined) ||
          (msg.payload?.widget as string | undefined) ||
          msg.widget,
        ),
      );
      if (isKnownWidget(widget)) {
        setLoadingType(null);
        const activityContract = findRuntimeActivityContract(
          runtimeBlueprintRef.current,
          msg.payload,
        );
        const payload = {
          ...msg.payload,
          blueprint_contract: activityContract ?? undefined,
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
        if (topicName) {
          setLessonMeta((curr) => ({
            ...curr,
            title: curr.title === "Today's lesson" ? topicName : curr.title,
          }));
        }
        setEvents((prev) => [
          ...prev,
          { kind: "section", tone: "task", label: WIDGET_SECTION_LABEL[widget] },
          { kind: "task", payload, submitted: false, answers: {} },
        ]);
        setPhase("practice");
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
      setLessonMeta((curr) => ({
        ...curr,
        title: res.data.topic || "Today's lesson",
        theme: displayLabel(res.data.skill_name || "") || curr.theme,
        focus: "",
      }));
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
      <ChatGlobalStyles />

      <ChatPageShell>
        <Topbar
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

        <ChatMain bottomPadding={200}>
          <LessonMetaCard
            eyebrow={buildLessonEyebrow(lessonMeta)}
            title={lessonMeta.title}
            focus={lessonMeta.focus}
          />

          <SectionMarker tone="intro" icon={<MessageCircle size={13} />}>Teaching</SectionMarker>

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
              return (
                <SectionMarker
                  key={i}
                  tone={evt.tone}
                  icon={evt.tone === "task" ? <FileText size={13} /> : <Sparkles size={13} />}
                >
                  {evt.label}
                </SectionMarker>
              );
            }
            if (evt.kind === "task") {
              const widget = evt.payload.widget;
              // M4: render converged archetypes through the rich widget library
              // in live interactive mode — editable input before submission and
              // a graded review after — replacing the generic RuntimeTaskWidget.
              const richTask = adaptContractTask(evt.payload);
              if (richTask) {
                return (
                  <TaskWidgetRenderer
                    key={i}
                    task={richTask}
                    previewState="default"
                    live={{
                      answers: evt.answers,
                      setAnswers: (next) => setTaskAnswers(i, next),
                      onSubmit: (answers) => handleSubmitTask(i, answers),
                      submitted: evt.submitted,
                    }}
                  />
                );
              }
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
              return (
                <RuntimeEvaluationCard
                  key={i}
                  scorecard={evt.payload}
                  taskPayload={lastTask?.kind === "task" ? lastTask.payload : null}
                  taskAnswers={lastTask?.kind === "task" ? lastTask.answers : undefined}
                />
              );
            }
            if (evt.kind === "final_scorecard") {
              return <RuntimeFinalScorecard key={i} payload={evt.payload} />;
            }
            if (evt.kind === "rag_feedback") {
              return <RuntimeRagFeedback key={i} payload={evt.payload} />;
            }
            if (evt.kind === "feedback") {
              const lastTask = events.slice(0, i).reverse().find((e) => e.kind === "task");
              return (
                <RuntimeFeedbackCard
                  key={i}
                  feedback={evt.payload}
                  taskPayload={lastTask?.kind === "task" ? lastTask.payload : null}
                />
              );
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
        </ChatMain>

        <Composer
          value={composer}
          onChange={setComposer}
          onSend={handleSendComposer}
          placeholder={composerPlaceholder}
        />
        {/* lastTaskIdx is exposed for future scroll-into-view; keeps lint quiet */}
        <span data-last-task={lastTaskIdx} style={{ display: "none" }} />
      </ChatPageShell>
    </>
  );
}
