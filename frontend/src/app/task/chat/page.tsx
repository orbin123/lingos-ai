"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";

/* ── Types ───────────────────────────────────────────────────────────── */
type Scene = "teaching" | "task" | "submitted";

interface Question {
  id: number;
  prefix: string;
  base: string;
  suffix: string;
  options: string[];
  answer: string;
}

type Answers = Record<number, string>;

/* ── Dummy data ──────────────────────────────────────────────────────── */
const TEACHING_MESSAGES = [
  {
    role: "ai" as const,
    name: "LingosAI",
    text: (
      <>
        Today we are working on <strong>past simple tense</strong> — one of the
        most important tenses for talking about your work experience and daily
        life. This comes up in almost every job interview and professional email.
      </>
    ),
  },
  {
    role: "ai" as const,
    text: (
      <>
        Quick question before we start — can you tell me one thing you did
        yesterday? Just one sentence, don&apos;t worry about being perfect.
      </>
    ),
  },
  {
    role: "you" as const,
    name: "You",
    text: "I go to the office and finish my report.",
  },
  {
    role: "ai" as const,
    text: (
      <>
        Good start! You have the right idea. But notice — you used &ldquo;go&rdquo; and
        &ldquo;finish&rdquo; which are present tense. For past simple, we change the verb:{" "}
        <em>&ldquo;I went to the office and finished my report.&rdquo;</em> Regular verbs
        like &ldquo;finish&rdquo; get <strong>-ed</strong>. Irregular verbs like &ldquo;go&rdquo;
        change completely to &ldquo;went&rdquo;.
      </>
    ),
  },
  {
    role: "ai" as const,
    text: <>Let me ask you another one — what did you eat for breakfast today?</>,
  },
  {
    role: "you" as const,
    text: "I ate rice and drank tea.",
  },
  {
    role: "ai" as const,
    text: (
      <>
        That is perfect. &ldquo;Ate&rdquo; and &ldquo;drank&rdquo; are both irregular past forms —
        you got them right. You are ready for the practice task.
      </>
    ),
  },
];

const TASK_PASSAGE_PARTS = [
  "Last Monday, Priya ",
  { blank: 1 },
  " up early. She ",
  { blank: 2 },
  " a job interview at 9 AM. She ",
  { blank: 3 },
  " her answers the night before, so she ",
  { blank: 4 },
  " confident.",
];

const QUESTIONS: Question[] = [
  {
    id: 1,
    prefix: "Priya",
    base: "wake",
    suffix: "up early.",
    options: ["wake", "woke", "waked", "woken"],
    answer: "woke",
  },
  {
    id: 2,
    prefix: "She",
    base: "have",
    suffix: "a job interview at 9 AM.",
    options: ["have", "has", "had", "having"],
    answer: "had",
  },
  {
    id: 3,
    prefix: "She",
    base: "prepare",
    suffix: "her answers the night before.",
    options: ["prepares", "prepare", "preparing", "prepared"],
    answer: "prepared",
  },
  {
    id: 4,
    prefix: "She",
    base: "feel",
    suffix: "confident.",
    options: ["feels", "felt", "feeling", "feeled"],
    answer: "felt",
  },
];

const SKILL_DELTAS = [
  { name: "Grammar", now: 68, delta: 8 },
  { name: "Vocabulary", now: 72, delta: 2 },
  { name: "Fluency", now: 64, delta: 0 },
  { name: "Expression", now: 58, delta: 1 },
];

function getExplanation(q: Question, sel: string, correct: boolean) {
  const explanations: Record<number, { ok: React.ReactNode; no: React.ReactNode }> = {
    1: {
      ok: (
        <>
          Nice — <strong>&ldquo;woke&rdquo;</strong> is the past simple of the irregular verb{" "}
          <em>&ldquo;wake&rdquo;</em>. Pattern: wake → woke → woken.
        </>
      ),
      no: (
        <>
          The base is <em>&ldquo;wake&rdquo;</em>, and it&apos;s irregular. Past simple is{" "}
          <strong>&ldquo;woke&rdquo;</strong>, not &ldquo;{sel}&rdquo;. &ldquo;Woken&rdquo; is the past participle (used
          with &ldquo;have/had&rdquo;), not past simple.
        </>
      ),
    },
    2: {
      ok: (
        <>
          Correct. <em>&ldquo;Have&rdquo;</em> is irregular — its past simple form is{" "}
          <strong>&ldquo;had&rdquo;</strong>. Always &ldquo;had&rdquo; for past, regardless of subject.
        </>
      ),
      no: (
        <>
          &ldquo;{sel}&rdquo; doesn&apos;t work in past simple. <em>&ldquo;Have&rdquo;</em> changes to{" "}
          <strong>&ldquo;had&rdquo;</strong> in the past — for I, you, she, he, we, they.
        </>
      ),
    },
    3: {
      ok: (
        <>
          Right. <em>&ldquo;Prepare&rdquo;</em> is regular, so we just add{" "}
          <strong>-d</strong>: prepare → <strong>prepared</strong>.
        </>
      ),
      no: (
        <>
          For regular verbs ending in <em>-e</em>, just add <strong>-d</strong>: prepare →{" "}
          <strong>prepared</strong>. &ldquo;{sel}&rdquo; is a different tense.
        </>
      ),
    },
    4: {
      ok: (
        <>
          Yes — <em>&ldquo;feel&rdquo;</em> is irregular. Past simple is <strong>&ldquo;felt&rdquo;</strong>{" "}
          (not &ldquo;feeled&rdquo; — that&apos;s a common mistake).
        </>
      ),
      no: (
        <>
          Watch out — <em>&ldquo;feel&rdquo;</em> is irregular, so we don&apos;t add{" "}
          <strong>-ed</strong>. Past simple is <strong>&ldquo;felt&rdquo;</strong>. &ldquo;Feeled&rdquo; is
          not a real word.
        </>
      ),
    },
  };
  return correct ? explanations[q.id].ok : explanations[q.id].no;
}

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
function Topbar({ scene }: { scene: Scene }) {
  const router = useRouter();
  const sceneLabel = scene === "teaching" ? "Intro" : scene === "task" ? "Practice" : "Results";
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
        }}>
          Day 1 · Grammar · {sceneLabel}
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
}: {
  role: "ai" | "you";
  name?: string;
  children: React.ReactNode;
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

function Divider({ label }: { label: string }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 14,
      margin: "22px 0 16px",
      color: "oklch(45% 0.07 240)",
      fontSize: 12, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase",
    }}>
      <div style={{ flex: 1, height: 1, background: "linear-gradient(to right, transparent, oklch(80% 0.04 240), transparent)" }} />
      {label}
      <div style={{ flex: 1, height: 1, background: "linear-gradient(to right, oklch(80% 0.04 240), transparent)" }} />
    </div>
  );
}

function PassageWithBlanks({ answers }: { answers: Answers }) {
  return (
    <div style={{
      background: "oklch(96% 0.03 245)",
      borderLeft: "3px solid oklch(52% 0.18 240)",
      borderRadius: 10,
      padding: "14px 16px",
      fontSize: 14.5, lineHeight: 1.7,
      color: "oklch(20% 0.09 245)",
      marginBottom: 18,
    }}>
      {TASK_PASSAGE_PARTS.map((part, i) => {
        if (typeof part === "string") return <span key={i}>{part}</span>;
        const val = answers[part.blank];
        return (
          <span key={i} style={{
            display: "inline-block",
            minWidth: 36, padding: "0 6px",
            borderBottom: "2px solid oklch(52% 0.18 240)",
            margin: "0 2px",
            fontStyle: "italic", fontWeight: 700, color: "oklch(52% 0.18 240)",
          }}>
            {val || "___"}
          </span>
        );
      })}
    </div>
  );
}

function TaskCard({
  answers,
  setAnswers,
  submitted,
  onSubmit,
}: {
  answers: Answers;
  setAnswers: React.Dispatch<React.SetStateAction<Answers>>;
  submitted: boolean;
  onSubmit: () => void;
}) {
  const allAnswered = QUESTIONS.every((q) => !!answers[q.id]);

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
        <TaskIcon /> Past simple — fill in the correct verb form
      </div>

      <PassageWithBlanks answers={answers} />

      {QUESTIONS.map((q) => {
        const sel = answers[q.id];
        return (
          <div key={q.id} style={{ marginBottom: 14 }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: "oklch(18% 0.06 240)", marginBottom: 8, lineHeight: 1.5 }}>
              <strong>{q.id}.</strong> {q.prefix}{" "}
              <span style={{ color: "oklch(60% 0.04 240)" }}>___</span>{" "}
              <span style={{ color: "oklch(52% 0.18 240)", fontWeight: 700, fontStyle: "italic" }}>({q.base})</span>{" "}
              {q.suffix}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8 }}>
              {q.options.map((opt) => {
                let bg = "white";
                let border = "1.5px solid oklch(85% 0.025 240)";
                let color = "oklch(20% 0.09 245)";
                let textDecoration = "none";

                if (submitted) {
                  if (opt === q.answer) {
                    bg = "oklch(94% 0.07 155)";
                    border = "1.5px solid oklch(60% 0.16 155)";
                    color = "oklch(28% 0.14 155)";
                  } else if (opt === sel && opt !== q.answer) {
                    bg = "oklch(94% 0.06 25)";
                    border = "1.5px solid oklch(60% 0.18 25)";
                    color = "oklch(35% 0.16 25)";
                    textDecoration = "line-through";
                  }
                } else if (sel === opt) {
                  bg = "oklch(52% 0.18 240)";
                  border = "1.5px solid oklch(52% 0.18 240)";
                  color = "white";
                }

                return (
                  <button
                    key={opt}
                    disabled={submitted}
                    onClick={() => {
                      if (!submitted) setAnswers((prev) => ({ ...prev, [q.id]: opt }));
                    }}
                    style={{
                      padding: "10px 8px", borderRadius: 10,
                      background: bg, border, color,
                      fontSize: 13.5, fontWeight: 600,
                      cursor: submitted ? "default" : "pointer",
                      transition: "all 0.15s",
                      textDecoration,
                      fontFamily: "inherit",
                      ...(sel === opt && !submitted ? { boxShadow: "0 4px 12px rgba(60,100,200,0.28)" } : {}),
                    }}
                  >
                    {opt}
                  </button>
                );
              })}
            </div>
          </div>
        );
      })}

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

function Scorecard({ correct, total }: { correct: number; total: number }) {
  const pct = Math.round((correct / total) * 100);
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
          <div style={{ fontSize: 18, fontWeight: 800, color: "oklch(20% 0.09 245)", letterSpacing: "-0.01em" }}>
            Day 1 — Past Simple
          </div>
          <div style={{ fontSize: 13, color: "oklch(45% 0.07 240)", marginTop: 3 }}>
            {correct} of {total} correct · 4m 12s
          </div>
        </div>
        <ScoreRing pct={pct} />
      </div>

      <div>
        {SKILL_DELTAS.map((d) => (
          <div key={d.name} style={{
            display: "flex", alignItems: "center", gap: 12,
            padding: "10px 0",
            borderBottom: "1px dashed oklch(88% 0.025 240)",
          }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: "oklch(20% 0.09 245)", width: 100, flexShrink: 0 }}>
              {d.name}
            </span>
            <div style={{ flex: 1, height: 6, borderRadius: 6, background: "oklch(92% 0.025 240)", overflow: "hidden", position: "relative" }}>
              <div style={{
                position: "absolute", left: 0, top: 0, height: "100%",
                width: `${d.now}%`,
                background: "linear-gradient(to right, oklch(52% 0.18 240), oklch(72% 0.12 230))",
                borderRadius: 6,
                transition: "width 1s ease",
              }} />
            </div>
            <span style={{ fontSize: 13, fontWeight: 700, color: "oklch(20% 0.09 245)", width: 40, textAlign: "right" }}>
              {d.now}%
            </span>
            <span style={{
              fontSize: 12, fontWeight: 700,
              padding: "3px 8px", borderRadius: 6, minWidth: 48, textAlign: "center",
              ...(d.delta === 0
                ? { background: "oklch(95% 0.015 240)", color: "oklch(45% 0.07 240)" }
                : { background: "oklch(94% 0.07 155)", color: "oklch(35% 0.14 155)" }),
            }}>
              {d.delta > 0 ? `+${d.delta}` : d.delta} pts
            </span>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginTop: 16 }}>
        {[
          { num: "+12", lbl: "XP earned" },
          { num: "7", lbl: "Day streak" },
          { num: "14", lbl: "New verbs learned" },
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

function FeedbackCard({ answers }: { answers: Answers }) {
  return (
    <div style={{
      borderRadius: 22,
      background: "rgba(255,255,255,0.85)",
      backdropFilter: "blur(18px)", WebkitBackdropFilter: "blur(18px)",
      border: "1.5px solid rgba(255,255,255,0.92)",
      boxShadow: "0 4px 28px rgba(80,110,180,0.1)",
      overflow: "hidden",
      animation: "fadeIn 0.4s ease both",
    }}>
      {QUESTIONS.map((q, i) => {
        const sel = answers[q.id];
        const correct = sel === q.answer;
        return (
          <div key={q.id} style={{
            padding: "16px 20px",
            borderBottom: i < QUESTIONS.length - 1 ? "1px solid oklch(85% 0.025 240)" : "none",
            display: "flex", gap: 14,
          }}>
            <div style={{
              width: 26, height: 26, borderRadius: "50%", flexShrink: 0,
              display: "flex", alignItems: "center", justifyContent: "center",
              background: correct ? "oklch(55% 0.16 155)" : "oklch(58% 0.2 25)",
            }}>
              {correct ? <CheckIcon /> : <XIcon />}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13.5, color: "oklch(18% 0.06 240)", marginBottom: 6, lineHeight: 1.55 }}>
                <strong>Q{q.id}.</strong> {q.prefix}{" "}
                <span style={{
                  display: "inline-block", padding: "0 6px", borderRadius: 4,
                  fontWeight: 700, margin: "0 1px",
                  background: correct ? "oklch(92% 0.1 155)" : "oklch(92% 0.08 25)",
                  color: correct ? "oklch(28% 0.16 155)" : "oklch(35% 0.18 25)",
                  textDecoration: correct ? "none" : "line-through",
                }}>
                  {sel}
                </span>
                {!correct && (
                  <>
                    {" → "}
                    <span style={{
                      display: "inline-block", padding: "0 6px", borderRadius: 4,
                      fontWeight: 700, margin: "0 1px",
                      background: "oklch(92% 0.1 155)", color: "oklch(28% 0.16 155)",
                    }}>
                      {q.answer}
                    </span>
                  </>
                )}{" "}
                {q.suffix}
              </div>
              <div style={{
                fontSize: 13, color: "oklch(45% 0.07 240)", lineHeight: 1.55,
                background: "oklch(96% 0.025 245)",
                borderRadius: 10, padding: "10px 12px", marginTop: 4,
              }}>
                {getExplanation(q, sel, correct)}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function Composer({
  value,
  onChange,
  placeholder,
}: {
  value: string;
  onChange: (v: string) => void;
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
              if (value.trim()) onChange("");
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
          <button style={{
            width: 38, height: 38, borderRadius: "50%",
            background: "#0070C4", color: "white", border: "none",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 4px 12px rgba(0,112,196,0.35)",
            cursor: "pointer",
          }}>
            <SendIcon />
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── Main page ───────────────────────────────────────────────────────── */
export default function TaskChatPage() {
  const [scene, setScene] = useState<Scene>("teaching");
  const [answers, setAnswers] = useState<Answers>({ 1: "", 2: "", 3: "", 4: "" });
  const [submitted, setSubmitted] = useState(false);
  const [composer, setComposer] = useState("");
  const stageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scene === "submitted") {
      setAnswers({ 1: "woke", 2: "had", 3: "prepared", 4: "feeled" });
      setSubmitted(true);
    } else if (scene === "task") {
      setAnswers({ 1: "", 2: "", 3: "", 4: "" });
      setSubmitted(false);
    } else {
      setAnswers({ 1: "", 2: "", 3: "", 4: "" });
      setSubmitted(false);
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [scene]);

  const handleSubmit = () => {
    setSubmitted(true);
    setScene("submitted");
  };

  const correctCount = QUESTIONS.filter((q) => answers[q.id] === q.answer).length;

  const composerPlaceholder =
    scene === "submitted" ? "Ask a follow-up question..." : "Type your answer...";

  return (
    <>
      <style>{`
        *, *::before, *::after { box-sizing: border-box; }
        body { overflow-x: hidden; }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
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
        {/* Dot grid */}
        <div aria-hidden style={{
          position: "fixed", inset: 0, pointerEvents: "none",
          backgroundImage: "radial-gradient(circle, rgba(90,130,210,0.13) 1px, transparent 1px)",
          backgroundSize: "22px 22px", zIndex: 0,
        }} />

        <Topbar scene={scene} />

        {/* Demo scene switcher */}
        <nav style={{
          position: "fixed", top: 76, right: 20, zIndex: 45,
          background: "white", border: "1px solid oklch(85% 0.025 240)", borderRadius: 14,
          padding: 8, boxShadow: "0 8px 24px rgba(80,110,180,0.14)",
          display: "flex", flexDirection: "column", gap: 4,
        }}>
          <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: "0.08em", color: "oklch(45% 0.07 240)", textTransform: "uppercase", padding: "4px 8px 2px" }}>
            Demo states
          </div>
          {(["teaching", "task", "submitted"] as Scene[]).map((s) => (
            <button
              key={s}
              onClick={() => setScene(s)}
              style={{
                background: scene === s ? "oklch(94% 0.05 240)" : "transparent",
                border: "none", textAlign: "left", padding: "7px 10px", borderRadius: 8,
                fontSize: 12.5, fontWeight: 600,
                color: scene === s ? "oklch(45% 0.2 250)" : "oklch(28% 0.08 245)",
                display: "flex", alignItems: "center", gap: 8, cursor: "pointer",
                fontFamily: "inherit", width: "100%",
              }}
            >
              <span style={{
                width: 6, height: 6, borderRadius: "50%",
                background: scene === s ? "oklch(52% 0.18 240)" : "oklch(80% 0.04 240)",
                boxShadow: scene === s ? "0 0 0 3px oklch(85% 0.1 240)" : "none",
                flexShrink: 0,
              }} />
              {s === "teaching" ? "Teaching" : s === "task" ? "Practice task" : "Score & feedback"}
            </button>
          ))}
        </nav>

        {/* Main chat area */}
        <main ref={stageRef} style={{
          position: "relative", zIndex: 1,
          maxWidth: 720, margin: "0 auto",
          padding: "28px 20px 200px",
        }}>
          <SectionMarker kind="intro" icon={<SparkIcon />}>Intro</SectionMarker>

          {TEACHING_MESSAGES.map((msg, i) => (
            <ChatBubble key={i} role={msg.role} name={msg.name}>
              {msg.text}
            </ChatBubble>
          ))}

          {(scene === "task" || scene === "submitted") && (
            <>
              <Divider label="task starting" />
              <SectionMarker kind="task" icon={<TaskIcon />}>Fill in the blanks</SectionMarker>
              <TaskCard
                answers={answers}
                setAnswers={setAnswers}
                submitted={submitted}
                onSubmit={handleSubmit}
              />
            </>
          )}

          {scene === "submitted" && (
            <>
              <div style={{ height: 16 }} />
              <ChatBubble role="ai">
                You finished — let me show you how today went.
              </ChatBubble>

              <div style={{ margin: "14px 0" }}>
                <SectionMarker kind="score" icon={<SparkIcon />}>
                  Today&apos;s scorecard
                </SectionMarker>
              </div>
              <Scorecard correct={correctCount} total={QUESTIONS.length} />

              <div style={{ margin: "20px 0 14px" }}>
                <SectionMarker kind="feedback" icon={<TaskIcon />}>
                  Detailed feedback
                </SectionMarker>
              </div>
              <FeedbackCard answers={answers} />

              <div style={{ height: 18 }} />
              <ChatBubble role="ai">
                <strong>One pattern I noticed:</strong> you sometimes added{" "}
                <em>-ed</em> to irregular verbs (like &ldquo;feeled&rdquo;). This is the most
                common past simple mistake — irregular verbs have their own forms
                you have to memorize. I&apos;ll add 5 of the most useful ones to
                tomorrow&apos;s review.
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 6 }}>
                  {["Show the 5 verbs", "Try another task", "End session"].map((label) => (
                    <button
                      key={label}
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
              </ChatBubble>
            </>
          )}

          <div style={{ height: 60 }} />
        </main>

        <Composer
          value={composer}
          onChange={setComposer}
          placeholder={composerPlaceholder}
        />
      </div>
    </>
  );
}
