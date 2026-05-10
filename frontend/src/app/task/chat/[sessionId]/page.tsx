"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";

/* ── Types from backend ───────────────────────────────────────────────── */
interface BlankItem {
  item_id?: string;
  blank_id?: string;
  sentence_with_blank: string;
  base_verb?: string | null;
  correct_answer: string;
  distractors?: string[];
  options?: string[];
  grammar_rule?: string;
  explanation: string;
}

interface FillInBlanksPayload {
  task_intro?: string;
  estimated_time_minutes?: number;
  widget?: "fill_in_blanks";
  topic_id?: string;
  topic_name?: string;
  sub_skill?: string;
  sub_level?: number;
  activity?: string;
  instructions?: string;
  grammar_rule_explained?: string;
  passage_title?: string;
  passage?: string | null;
  blanks?: BlankItem[];
  items?: BlankItem[];
  total_blanks?: number;
  topic?: string;
}

interface OpenTextItem {
  item_id: string;
  prompt: string;
  sample_answer: string;
  answer_hints: string[];
}

interface OpenTextPayload {
  task_intro?: string;
  estimated_time_minutes?: number;
  widget: "open_text";
  topic_id?: string;
  topic_name?: string;
  sub_skill?: string;
  sub_level?: number;
  activity?: string;
  instructions?: string;
  grammar_rule_explained?: string;
  common_mistakes?: string[];
  items: OpenTextItem[];
}

interface ScorecardPayload {
  overall_score: number;
  skill_name: string;
  topic: string;
  total: number;
  correct_count: number;
  questions: Record<string, unknown>;
  subskill_score?: number | null;  // 0-10 for AI-evaluated writing tasks
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
  overall_message: string;
  errors: FeedbackError[];
  score: number;
  overall_level: string;
  practice_suggestion: string;
}

type TaskPayload = FillInBlanksPayload | OpenTextPayload;

type ChatEvent =
  | { kind: "chat"; role: "ai" | "you"; content: string; actions?: string[]; streamId?: string; streaming?: boolean }
  | { kind: "section"; tone: "intro" | "task" | "score" | "feedback"; label: string }
  | { kind: "task"; payload: TaskPayload; submitted: boolean; answers: Record<string, string> }
  | { kind: "scorecard"; payload: ScorecardPayload }
  | { kind: "feedback"; payload: FeedbackPayload };

type WSIncoming =
  | { type: "chat_message"; role?: string; content?: string; actions?: string[] }
  | { type: "chat_stream_start"; role?: string; stream_id?: string; actions?: string[] }
  | { type: "chat_stream_delta"; role?: string; stream_id?: string; content?: string }
  | { type: "chat_stream_end"; role?: string; stream_id?: string; content?: string; actions?: string[] }
  | { type: "ui_event"; widget: string; payload: Record<string, unknown> }
  | { type: "error"; content?: string };

type WSOutgoing =
  | { type: "user_message"; content: string }
  | { type: "task_submission"; answers: Record<string, string> }
  | { type: "follow_up_action"; action: string };

/* ── Icons ───────────────────────────────────────────────────────────── */
function BackIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M10 12L6 8L10 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function FlameIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
      <path d="M8 14c2.5 0 4.5-2 4.5-4.5 0-2-1-3-2-4.5 0 1.5-.7 2-1.5 2 0-1.5-1-3-2.5-4.5 0 3-3 4-3 7C3.5 12 5.5 14 8 14z" fill="#f97316" />
    </svg>
  );
}
function MoreIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <circle cx="3.5" cy="8" r="1.3" fill="currentColor" />
      <circle cx="8" cy="8" r="1.3" fill="currentColor" />
      <circle cx="12.5" cy="8" r="1.3" fill="currentColor" />
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
function Topbar({ skillLabel, sceneLabel }: { skillLabel: string; sceneLabel: string }) {
  const router = useRouter();
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

        <div style={{
          display: "inline-flex", alignItems: "center", gap: 6,
          background: "white", border: "1px solid oklch(85% 0.025 240)", borderRadius: 999,
          padding: "6px 12px", fontSize: 12.5, fontWeight: 700, color: "oklch(20% 0.09 245)",
        }}>
          <FlameIcon /> 7 day streak
        </div>

        <button style={{
          width: 36, height: 36, borderRadius: "50%",
          background: "white", border: "1px solid oklch(85% 0.025 240)",
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          color: "oklch(28% 0.08 245)", cursor: "pointer",
        }}>
          <MoreIcon />
        </button>
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

function blankId(blank: BlankItem) {
  return blank.item_id || blank.blank_id || blank.sentence_with_blank;
}

function PassageWithBlanks({
  passage,
  blanks,
  answers,
  setAnswers,
  submitted,
}: {
  passage: string;
  blanks: BlankItem[];
  answers: Record<string, string>;
  setAnswers: (next: Record<string, string>) => void;
  submitted: boolean;
}) {
  const parts = passage.split("___");
  const hasInlineBlanks = parts.length > 1;

  const inputForBlank = (blank: BlankItem, index: number) => {
    const id = blankId(blank);
    const value = answers[id] ?? "";
    const isCorrect = submitted && value.trim().toLowerCase() === blank.correct_answer.trim().toLowerCase();

    return (
      <span
        key={`${id}-${index}`}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          margin: "0 4px",
          verticalAlign: "baseline",
          whiteSpace: "nowrap",
        }}
      >
        <span
          aria-hidden
          style={{
            width: 24,
            height: 24,
            borderRadius: "50%",
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            background: submitted
              ? isCorrect
                ? "oklch(55% 0.16 155)"
                : "oklch(58% 0.2 25)"
              : "oklch(52% 0.18 240)",
            color: "white",
            fontSize: 12,
            fontWeight: 800,
            lineHeight: 1,
            flexShrink: 0,
          }}
        >
          {index + 1}
        </span>
        <input
          aria-label={`Blank ${index + 1}`}
          disabled={submitted}
          value={value}
          onChange={(e) => {
            if (!submitted) setAnswers({ ...answers, [id]: e.target.value });
          }}
          placeholder="answer"
          style={{
            width: "clamp(88px, 18vw, 150px)",
            height: 34,
            padding: "6px 10px",
            borderRadius: 9,
            border: submitted
              ? isCorrect
                ? "1.5px solid oklch(60% 0.16 155)"
                : "1.5px solid oklch(60% 0.18 25)"
              : "1.5px solid oklch(75% 0.06 240)",
            background: submitted
              ? isCorrect
                ? "oklch(94% 0.07 155)"
                : "oklch(94% 0.06 25)"
              : "white",
            color: "oklch(20% 0.09 245)",
            fontSize: 14,
            fontWeight: 700,
            fontFamily: "inherit",
            outline: "none",
            boxShadow: submitted ? "none" : "0 2px 8px rgba(80,110,180,0.08)",
          }}
        />
        {!submitted && blank.base_verb && (
          <span style={{
            fontSize: 12,
            fontWeight: 600,
            color: "oklch(52% 0.18 240)",
            fontStyle: "italic",
            whiteSpace: "nowrap",
          }}>
            ({blank.base_verb})
          </span>
        )}
      </span>
    );
  };

  return (
    <div style={{
      background: "oklch(96% 0.03 245)",
      borderLeft: "3px solid oklch(52% 0.18 240)",
      borderRadius: 10,
      padding: "18px 18px",
      fontSize: 16, lineHeight: 1.9,
      color: "oklch(20% 0.09 245)",
      marginBottom: 18,
      whiteSpace: "pre-wrap",
    }}>
      {hasInlineBlanks ? (
        parts.map((part, index) => (
          <span key={`part-${index}`}>
            {part}
            {index < blanks.length ? inputForBlank(blanks[index], index) : null}
          </span>
        ))
      ) : (
        blanks.map((blank, index) => {
          const sentenceParts = blank.sentence_with_blank.split("___");
          return (
            <div key={blankId(blank)} style={{ marginBottom: 8 }}>
              <span style={{ fontWeight: 700, marginRight: 6, color: "oklch(52% 0.18 240)" }}>{index + 1}.</span>
              {sentenceParts[0]}
              {inputForBlank(blank, index)}
              {sentenceParts[1] ?? ""}
            </div>
          );
        })
      )}
    </div>
  );
}

function TaskCard({
  payload,
  answers,
  setAnswers,
  submitted,
  onSubmit,
}: {
  payload: FillInBlanksPayload;
  answers: Record<string, string>;
  setAnswers: (next: Record<string, string>) => void;
  submitted: boolean;
  onSubmit: () => void;
}) {
  const blanks = payload.items ?? payload.blanks ?? [];
  const allAnswered = blanks.every((b) => !!answers[blankId(b)]);

  return (
    <div style={{
      borderRadius: 22, padding: "22px 24px",
      background: "rgba(255,255,255,0.82)",
      backdropFilter: "blur(18px)", WebkitBackdropFilter: "blur(18px)",
      border: "1.5px solid rgba(255,255,255,0.92)",
      boxShadow: "0 6px 28px rgba(80,110,180,0.12)",
      marginTop: 4, animation: "fadeIn 0.4s ease both",
    }}>
      <div style={{
        display: "flex", alignItems: "center", gap: 8,
        fontSize: 13, fontWeight: 700, color: "oklch(52% 0.18 240)",
        marginBottom: 14, paddingBottom: 12,
        borderBottom: "1px solid oklch(85% 0.025 240)",
      }}>
        <TaskIcon /> {payload.topic_name || payload.passage_title || "Fill in the correct word"}
      </div>

      {(payload.task_intro || payload.instructions) && (
        <div style={{
          fontSize: 14, lineHeight: 1.6,
          color: "oklch(35% 0.07 240)",
          marginBottom: 14,
        }}>
          {payload.task_intro || payload.instructions}
        </div>
      )}

      <PassageWithBlanks
        passage={payload.passage ?? ""}
        blanks={blanks}
        answers={answers}
        setAnswers={setAnswers}
        submitted={submitted}
      />

      {submitted && (
        <div style={{ display: "grid", gap: 10, marginBottom: 14 }}>
          {blanks.map((b, idx) => {
            const id = blankId(b);
            const answer = answers[id] ?? "";
            const isCorrect = answer.trim().toLowerCase() === b.correct_answer.trim().toLowerCase();
            return (
              <div
                key={id}
                style={{
                  display: "grid",
                  gap: 4,
                  padding: "10px 12px",
                  borderRadius: 10,
                  background: "rgba(255,255,255,0.72)",
                  border: "1px solid oklch(87% 0.025 240)",
                  fontSize: 12.5,
                  lineHeight: 1.5,
                  color: "oklch(45% 0.07 240)",
                }}
              >
                <div style={{ color: "oklch(20% 0.09 245)", fontWeight: 800 }}>
                  Blank {idx + 1}
                  {!isCorrect && <span>: correct answer is {b.correct_answer}</span>}
                </div>
                <div>{b.explanation}</div>
              </div>
            );
          })}
        </div>
      )}

      {!submitted && (
        <button
          disabled={!allAnswered}
          onClick={onSubmit}
          style={{
            width: "100%", padding: "14px 0", marginTop: 8,
            borderRadius: 14, border: "none",
            background: "oklch(20% 0.09 245)", color: "white",
            fontSize: 14.5, fontWeight: 700,
            boxShadow: "0 6px 20px rgba(20,40,90,0.25)",
            cursor: allAnswered ? "pointer" : "not-allowed",
            opacity: allAnswered ? 1 : 0.5,
            display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
            fontFamily: "inherit",
            transition: "transform 0.15s",
          }}
        >
          <SparkIcon /> Submit answers
        </button>
      )}
    </div>
  );
}

function OpenTextTaskCard({
  payload,
  answers,
  setAnswers,
  submitted,
  onSubmit,
}: {
  payload: OpenTextPayload;
  answers: Record<string, string>;
  setAnswers: (next: Record<string, string>) => void;
  submitted: boolean;
  onSubmit: () => void;
}) {
  const items = payload.items ?? [];
  const allFilled = items.every((it) => (answers[it.item_id] ?? "").trim().length >= 5);

  return (
    <div style={{
      borderRadius: 22, padding: "22px 24px",
      background: "rgba(255,255,255,0.82)",
      backdropFilter: "blur(18px)", WebkitBackdropFilter: "blur(18px)",
      border: "1.5px solid rgba(255,255,255,0.92)",
      boxShadow: "0 6px 28px rgba(80,110,180,0.12)",
      marginTop: 4, animation: "fadeIn 0.4s ease both",
    }}>
      {/* Header */}
      <div style={{
        display: "flex", alignItems: "center", gap: 8,
        fontSize: 13, fontWeight: 700, color: "oklch(52% 0.18 240)",
        marginBottom: 14, paddingBottom: 12,
        borderBottom: "1px solid oklch(85% 0.025 240)",
      }}>
        <TaskIcon />
        {payload.topic_name || "Writing task"}
        {payload.sub_skill && (
          <span style={{
            marginLeft: "auto", fontSize: 11, fontWeight: 600,
            color: "oklch(45% 0.07 240)", textTransform: "capitalize",
          }}>
            {payload.sub_skill} · {payload.activity}
          </span>
        )}
      </div>

      {/* Instructions */}
      {payload.instructions && (
        <div style={{ fontSize: 14, lineHeight: 1.6, color: "oklch(35% 0.07 240)", marginBottom: 14 }}>
          {payload.instructions}
        </div>
      )}

      {/* Grammar rule callout — shown before items so learner knows what to practice */}
      {payload.grammar_rule_explained && (
        <div style={{
          background: "oklch(94% 0.06 240)", borderLeft: "3px solid oklch(52% 0.18 240)",
          borderRadius: 10, padding: "12px 14px", marginBottom: 18,
          fontSize: 13.5, lineHeight: 1.6, color: "oklch(25% 0.08 245)",
        }}>
          <span style={{ fontWeight: 700, color: "oklch(40% 0.14 240)" }}>Rule: </span>
          {payload.grammar_rule_explained}
        </div>
      )}

      {/* Items */}
      <div style={{ display: "grid", gap: 18, marginBottom: 20 }}>
        {items.map((item, idx) => {
          const val = answers[item.item_id] ?? "";
          const hasContent = val.trim().length >= 5;
          return (
            <div key={item.item_id}>
              {/* Prompt */}
              <div style={{
                fontSize: 14, fontWeight: 700, color: "oklch(22% 0.07 240)",
                marginBottom: 8, lineHeight: 1.5,
                display: "flex", gap: 8, alignItems: "flex-start",
              }}>
                <span style={{
                  minWidth: 22, height: 22, borderRadius: "50%",
                  background: "oklch(52% 0.18 240)", color: "white",
                  display: "inline-flex", alignItems: "center", justifyContent: "center",
                  fontSize: 11, fontWeight: 800, flexShrink: 0, marginTop: 1,
                }}>
                  {idx + 1}
                </span>
                <span>{item.prompt}</span>
              </div>

              {/* Textarea */}
              {!submitted && (
                <textarea
                  rows={3}
                  value={val}
                  onChange={(e) => setAnswers({ ...answers, [item.item_id]: e.target.value })}
                  placeholder="Write your answer here…"
                  style={{
                    width: "100%", resize: "vertical",
                    padding: "12px 14px", borderRadius: 12,
                    border: hasContent
                      ? "1.5px solid oklch(60% 0.14 240)"
                      : "1.5px solid oklch(78% 0.05 240)",
                    background: "oklch(97% 0.02 245)", color: "oklch(18% 0.06 240)",
                    fontSize: 14, lineHeight: 1.6, fontFamily: "inherit",
                    outline: "none",
                    boxShadow: "0 2px 8px rgba(80,110,180,0.06)",
                    transition: "border-color 0.15s",
                  }}
                />
              )}

              {/* Post-submission: show user answer + sample + hints */}
              {submitted && (
                <div style={{ display: "grid", gap: 8, marginLeft: 30 }}>
                  {/* User's answer */}
                  <div style={{
                    padding: "10px 12px", borderRadius: 10,
                    background: "oklch(95% 0.03 245)",
                    border: "1px solid oklch(84% 0.03 245)",
                    fontSize: 13.5, color: "oklch(30% 0.07 240)", lineHeight: 1.55,
                  }}>
                    <span style={{ fontSize: 11, fontWeight: 700, color: "oklch(50% 0.07 240)", display: "block", marginBottom: 4 }}>YOUR ANSWER</span>
                    {val || <em style={{ color: "oklch(60% 0.05 240)" }}>No answer</em>}
                  </div>

                  {/* Sample answer */}
                  <div style={{
                    padding: "10px 12px", borderRadius: 10,
                    background: "oklch(94% 0.07 155)",
                    border: "1px solid oklch(80% 0.1 155)",
                    fontSize: 13.5, color: "oklch(22% 0.1 155)", lineHeight: 1.55,
                  }}>
                    <span style={{ fontSize: 11, fontWeight: 700, color: "oklch(35% 0.13 155)", display: "block", marginBottom: 4 }}>SAMPLE ANSWER</span>
                    {item.sample_answer}
                  </div>

                  {/* Hints (if any) */}
                  {item.answer_hints && item.answer_hints.length > 0 && (
                    <div style={{
                      padding: "8px 12px", borderRadius: 10,
                      background: "oklch(96% 0.04 60)",
                      border: "1px solid oklch(84% 0.08 60)",
                      fontSize: 13, color: "oklch(30% 0.1 60)", lineHeight: 1.55,
                    }}>
                      <span style={{ fontSize: 11, fontWeight: 700, color: "oklch(38% 0.12 60)", display: "block", marginBottom: 4 }}>HINTS</span>
                      <ul style={{ margin: 0, paddingLeft: 16 }}>
                        {item.answer_hints.map((h, hi) => <li key={hi}>{h}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Common mistakes — shown after submission */}
      {submitted && payload.common_mistakes && payload.common_mistakes.length > 0 && (
        <div style={{
          padding: "12px 14px", borderRadius: 12, marginBottom: 14,
          background: "oklch(95% 0.05 30)",
          border: "1px solid oklch(82% 0.1 30)",
        }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: "oklch(38% 0.14 30)", marginBottom: 6, letterSpacing: "0.04em" }}>
            COMMON MISTAKES TO WATCH FOR
          </div>
          <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13, color: "oklch(28% 0.1 30)", lineHeight: 1.6 }}>
            {payload.common_mistakes.map((m, i) => <li key={i}>{m}</li>)}
          </ul>
        </div>
      )}

      {/* Submit button */}
      {!submitted && (
        <button
          disabled={!allFilled}
          onClick={onSubmit}
          style={{
            width: "100%", padding: "14px 0",
            borderRadius: 14, border: "none",
            background: "oklch(20% 0.09 245)", color: "white",
            fontSize: 14.5, fontWeight: 700,
            boxShadow: "0 6px 20px rgba(20,40,90,0.25)",
            cursor: allFilled ? "pointer" : "not-allowed",
            opacity: allFilled ? 1 : 0.5,
            display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
            fontFamily: "inherit",
            transition: "transform 0.15s",
          }}
        >
          <SparkIcon /> Submit writing
        </button>
      )}
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

function Scorecard({ payload }: { payload: ScorecardPayload }) {
  const pct = payload.overall_score;
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
              : `${payload.correct_count} of ${payload.total} correct`}
          </div>
        </div>
        <ScoreRing pct={pct} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginTop: 16 }}>
        {[
          {
            num: payload.subskill_score != null ? `${payload.subskill_score}/10` : `${payload.correct_count}`,
            lbl: payload.subskill_score != null ? "Skill score" : "Correct",
          },
          {
            num: payload.subskill_score != null ? `${payload.correct_count}/${payload.total}` : `${payload.total - payload.correct_count}`,
            lbl: payload.subskill_score != null ? "Items done" : "To review",
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
      {errors.length === 0 && (
        <div style={{ padding: "20px 22px", display: "flex", gap: 14, alignItems: "center" }}>
          <div style={{
            width: 26, height: 26, borderRadius: "50%", flexShrink: 0,
            display: "flex", alignItems: "center", justifyContent: "center",
            background: "oklch(55% 0.16 155)",
          }}>
            <CheckIcon />
          </div>
          <div style={{ fontSize: 13.5, color: "oklch(18% 0.06 240)", lineHeight: 1.55 }}>
            All correct — solid run. {payload.practice_suggestion}
          </div>
        </div>
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

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
    if (ref.current) {
      ref.current.style.height = "auto";
      ref.current.style.height = Math.min(140, ref.current.scrollHeight) + "px";
    }
  };

  return (
    <div style={{
      position: "fixed", bottom: 0, left: 0, right: 0, zIndex: 40,
      padding: "14px 20px 18px",
      background: "linear-gradient(to bottom, rgba(232,240,252,0) 0%, rgba(232,240,252,0.7) 50%, rgba(232,240,252,0.92) 100%)",
      backdropFilter: "blur(8px)", WebkitBackdropFilter: "blur(8px)",
    }}>
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
              if (value.trim()) onSend();
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
          <button style={{
            width: 36, height: 36, borderRadius: "50%",
            background: "transparent", border: "none",
            color: "oklch(45% 0.07 240)",
            display: "flex", alignItems: "center", justifyContent: "center",
            cursor: "pointer",
          }}>
            <MicIcon />
          </button>
          <button
            onClick={onSend}
            disabled={!value.trim()}
            style={{
              width: 38, height: 38, borderRadius: "50%",
              background: "#0070C4", color: "white", border: "none",
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: "0 4px 12px rgba(0,112,196,0.35)",
              cursor: value.trim() ? "pointer" : "not-allowed",
              opacity: value.trim() ? 1 : 0.5,
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

  const wsRef = useRef<WebSocket | null>(null);
  const pendingSendsRef = useRef<WSOutgoing[]>([]);
  const stageRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const lastTaskIdx = useMemo(() => {
    for (let i = events.length - 1; i >= 0; i -= 1) {
      if (events[i].kind === "task") return i;
    }
    return -1;
  }, [events]);

  const handleIncoming = useCallback((msg: WSIncoming) => {
    if (msg.type === "chat_message") {
      if (msg.actions?.includes("Go to dashboard")) {
        setPhase("ended");
      }
      setEvents((prev) => [
        ...prev,
        {
          kind: "chat",
          role: "ai",
          content: msg.content || "",
          actions: msg.actions,
        },
      ]);
      return;
    }
    if (msg.type === "chat_stream_start") {
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
      if (msg.actions?.includes("Go to dashboard")) {
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
      if (msg.widget === "fill_in_blanks") {
        const payload = msg.payload as unknown as FillInBlanksPayload;
        setSkillName((curr) => curr || payload.topic_name || payload.topic || "");
        setEvents((prev) => [
          ...prev,
          { kind: "section", tone: "task", label: "Fill in the blanks" },
          { kind: "task", payload, submitted: false, answers: {} },
        ]);
        setPhase("practice");
        return;
      }
      if (msg.widget === "open_text") {
        const payload = msg.payload as unknown as OpenTextPayload;
        setSkillName((curr) => curr || payload.topic_name || "");
        setEvents((prev) => [
          ...prev,
          { kind: "section", tone: "task", label: "Writing task" },
          { kind: "task", payload, submitted: false, answers: {} },
        ]);
        setPhase("practice");
        return;
      }
      if (msg.widget === "scorecard") {
        const payload = msg.payload as unknown as ScorecardPayload;
        setSkillName((curr) => curr || payload.skill_name || "");
        setEvents((prev) => [
          ...prev,
          { kind: "section", tone: "score", label: "Today's scorecard" },
          { kind: "scorecard", payload },
        ]);
        setPhase("submitted");
        return;
      }
      if (msg.widget === "feedback_card") {
        const payload = msg.payload as unknown as FeedbackPayload;
        setEvents((prev) => [
          ...prev,
          { kind: "section", tone: "feedback", label: "Detailed feedback" },
          { kind: "feedback", payload },
        ]);
        return;
      }
      return;
    }
    if (msg.type === "error") {
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
    const url = `${wsBase}/ws/learning/${sessionId}?token=${encodeURIComponent(token)}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      if (wsRef.current !== ws) return;
      setConnectionState("open");
      const queued = pendingSendsRef.current.splice(0);
      queued.forEach((payload) => ws.send(JSON.stringify(payload)));
    };
    ws.onclose = () => {
      if (wsRef.current === ws) setConnectionState("closed");
    };
    ws.onerror = () => {
      if (wsRef.current === ws) setConnectionState("error");
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

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end", behavior: "smooth" });
  }, [events]);

  const send = useCallback((payload: WSOutgoing) => {
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
      // Treat free-form text as a follow-up question.
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
      queryClient.invalidateQueries({ queryKey: ["task", "next"] });
      queryClient.invalidateQueries({ queryKey: ["me"] });
      router.push("/dashboard");
      return;
    }
    setEvents((prev) => [...prev, { kind: "chat", role: "you", content: label }]);
    send({ type: "follow_up_action", action: label });
    if (label === "End session") setPhase("ended");
  }

  function setTaskAnswers(eventIdx: number, next: Record<string, string>) {
    setEvents((prev) =>
      prev.map((e, i) =>
        i === eventIdx && e.kind === "task" ? { ...e, answers: next } : e,
      ),
    );
  }

  function handleSubmitTask(eventIdx: number) {
    const evt = events[eventIdx];
    if (!evt || evt.kind !== "task") return;
    setEvents((prev) =>
      prev.map((e, i) =>
        i === eventIdx && e.kind === "task" ? { ...e, submitted: true } : e,
      ),
    );
    send({ type: "task_submission", answers: evt.answers });
    setPhase("submitted");
  }

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

        <Topbar skillLabel={skillName || "Lesson"} sceneLabel={sceneLabel} />

        <main ref={stageRef} style={{
          position: "relative", zIndex: 1,
          maxWidth: 720, margin: "0 auto",
          padding: "28px 20px 200px",
        }}>
          <SectionMarker kind="intro" icon={<SparkIcon />}>Intro</SectionMarker>

          {connectionState !== "open" && events.length === 0 && (
            <ChatBubble role="ai" name="LingosAI">
              {connectionState === "connecting" && "Connecting to your session…"}
              {connectionState === "closed" && "Connection closed. Refresh to reconnect."}
              {connectionState === "error" && "Could not reach the session. Make sure you're signed in."}
            </ChatBubble>
          )}

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
                  kind={evt.tone}
                  icon={evt.tone === "task" ? <TaskIcon /> : <SparkIcon />}
                >
                  {evt.label}
                </SectionMarker>
              );
            }
            if (evt.kind === "task") {
              if (evt.payload.widget === "open_text") {
                return (
                  <OpenTextTaskCard
                    key={i}
                    payload={evt.payload as OpenTextPayload}
                    answers={evt.answers}
                    setAnswers={(next) => setTaskAnswers(i, next)}
                    submitted={evt.submitted}
                    onSubmit={() => handleSubmitTask(i)}
                  />
                );
              }
              return (
                <TaskCard
                  key={i}
                  payload={evt.payload as FillInBlanksPayload}
                  answers={evt.answers}
                  setAnswers={(next) => setTaskAnswers(i, next)}
                  submitted={evt.submitted}
                  onSubmit={() => handleSubmitTask(i)}
                />
              );
            }
            if (evt.kind === "scorecard") {
              return <Scorecard key={i} payload={evt.payload} />;
            }
            if (evt.kind === "feedback") {
              return <FeedbackCard key={i} payload={evt.payload} />;
            }
            return null;
          })}

          <div ref={bottomRef} style={{ height: 60 }} />
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
