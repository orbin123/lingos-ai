"use client";

import { Check, Play, Send, Sparkles, X } from "lucide-react";
import type { CSSProperties, ReactNode } from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import type { LiveTaskController, SessionTask } from "../source";
import {
  SPATIAL_NAV_ROOT_ATTR,
  spatialFieldProps,
} from "@/lib/spatial-field-navigation";

/** Shared submit button for live interactive task widgets (M4). */
export function SubmitButton({
  onClick,
  disabled,
}: {
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      className="tw-submit-btn"
      disabled={disabled}
      onClick={onClick}
    >
      <Send size={15} />
      Submit answers
    </button>
  );
}

export function TaskWidgetFrame({
  task,
  icon,
  children,
}: {
  task: SessionTask;
  icon: ReactNode;
  children: ReactNode;
}) {
  return (
    <section
      className="tw-root"
      {...{ [SPATIAL_NAV_ROOT_ATTR]: "" }}
      style={{
        background: "rgba(255,255,255,0.96)",
        border: "1.5px solid rgba(255,255,255,0.9)",
        borderRadius: 22,
        padding: 22,
        boxShadow: "0 8px 32px rgba(80,110,180,0.14)",
        marginBottom: 16,
        animation: "testChatFadeIn 0.35s ease both",
      }}
    >
      <div className="tw-task-header">
        <div className="tw-task-topic">{task.topic}</div>
        <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
          <div
            style={{
              width: 38,
              height: 38,
              borderRadius: 12,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "#0070C4",
              color: "white",
              flexShrink: 0,
              boxShadow: "0 5px 14px rgba(0,112,196,0.28)",
            }}
          >
            {icon}
          </div>
          <div style={{ minWidth: 0 }}>
            <div className="tw-task-title">{task.taskIntro}</div>
            <div className="tw-task-intro">{task.instructions}</div>
          </div>
        </div>
        <div className="tw-task-pill-row">
          <span className="tw-task-pill">
            <span className="tw-dot" />
            {task.subSkill}
          </span>
          <span className="tw-task-pill activity">
            <span className="tw-dot" />
            {task.activity}
          </span>
          <span className="tw-task-pill time">
            <span className="tw-dot" />
            {task.estimatedMinutes} min
          </span>
        </div>
      </div>
      {children}
    </section>
  );
}

export function RuleCallout({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <div className="tw-rule-callout">
      <div className="tw-rule-icon">
        <Sparkles size={16} />
      </div>
      <div className="tw-rule-body">
        <div className="tw-rule-label">{label}</div>
        <div className="tw-rule-text">{children}</div>
      </div>
    </div>
  );
}

export function ResultBanner({
  total,
  correct,
  label,
}: {
  total: number;
  correct: number;
  label: string;
}) {
  const score = total > 0 ? Math.round((correct / total) * 100) : 0;
  const tone = score === 100 ? "good" : score >= 70 ? "mid" : "bad";

  return (
    <div className={`tw-result-banner ${tone}`}>
      <div className="tw-result-icon">
        <Sparkles size={18} />
      </div>
      <div className="tw-result-text">
        <div className="tw-result-headline">{label}</div>
        <div className="tw-result-sub">Completed and submitted preview state.</div>
      </div>
      <div>
        <div className="tw-result-score">
          {score}
          <span style={{ fontSize: 14, color: "var(--tw-ink-muted)" }}>%</span>
        </div>
        <div className="tw-result-score-sub">Score</div>
      </div>
    </div>
  );
}

export function FeedbackRow({
  ok,
  title,
  body,
}: {
  ok: boolean;
  title: string;
  body: string;
}) {
  return (
    <div className={`tw-fb-row ${ok ? "good" : "bad"}`}>
      <div className={`tw-fb-marker ${ok ? "ok" : "no"}`}>
        {ok ? <Check size={13} strokeWidth={3} /> : <X size={13} strokeWidth={3} />}
      </div>
      <div>
        <div className="tw-fb-q">{title}</div>
        <div className="tw-fb-explain">{body}</div>
      </div>
    </div>
  );
}

export function StatusDot({ ok }: { ok: boolean }) {
  return (
    <span
      aria-label={ok ? "Correct" : "Needs correction"}
      style={{
        width: 20,
        height: 20,
        borderRadius: "50%",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        background: ok ? "var(--tw-green)" : "var(--tw-red)",
        color: "white",
        flexShrink: 0,
      }}
    >
      {ok ? <Check size={12} strokeWidth={3} /> : <X size={12} strokeWidth={3} />}
    </span>
  );
}

export function ListeningAudioCard({
  title,
  script,
  audioUrl,
  durationSeconds,
  completed,
  hint,
  onComplete,
}: {
  title: string;
  script: string;
  audioUrl?: string | null;
  durationSeconds?: number;
  completed: boolean;
  hint?: string;
  onComplete: () => void;
}) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playing, setPlaying] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [duration, setDuration] = useState(durationSeconds || 0);
  const [fallbackUnavailable, setFallbackUnavailable] = useState(false);
  const resolvedAudioUrl = resolveAudioUrl(audioUrl);

  const finishPlayback = useCallback(() => {
    setPlaying(false);
    setFallbackUnavailable(false);
    setElapsed(duration || durationSeconds || 0);
    onComplete();
  }, [duration, durationSeconds, onComplete]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setDuration(durationSeconds || 0);
    setElapsed(0);
    setPlaying(false);
    setFallbackUnavailable(false);
  }, [audioUrl, script, durationSeconds]);

  useEffect(() => {
    if (completed) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setPlaying(false);
      setElapsed(duration || durationSeconds || 0);
    }
  }, [completed, duration, durationSeconds]);

  useEffect(() => {
    if (!playing || resolvedAudioUrl) return;

    const intervalTime = 100; // ms
    const timer = setInterval(() => {
      setElapsed((prev) => {
        const next = prev + intervalTime / 1000;
        if (next >= duration) {
          clearInterval(timer);
          finishPlayback();
          return duration;
        }
        return next;
      });
    }, intervalTime);

    return () => clearInterval(timer);
  }, [playing, resolvedAudioUrl, duration, finishPlayback]);

  const playWithSpeech = () => {
    if (!script || typeof window === "undefined" || !("speechSynthesis" in window)) {
      setFallbackUnavailable(true);
      return false;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(script);
    utterance.rate = 0.9;
    utterance.onend = finishPlayback;
    utterance.onerror = () => {
      setPlaying(false);
      setFallbackUnavailable(true);
    };
    setPlaying(true);
    try {
      window.speechSynthesis.speak(utterance);
      return true;
    } catch {
      setPlaying(false);
      setFallbackUnavailable(true);
      return false;
    }
  };

  const playOnce = () => {
    if (completed || playing) return;
    setFallbackUnavailable(false);
    if (resolvedAudioUrl && audioRef.current) {
      audioRef.current.currentTime = 0;
      setPlaying(true);
      void audioRef.current.play().catch(() => {
        setPlaying(false);
        playWithSpeech();
      });
      return;
    }
    playWithSpeech();
  };

  const durationLabel = formatClock(duration || durationSeconds || 0);
  const elapsedLabel = formatClock(Math.min(elapsed, duration || elapsed || 0));
  const progress = duration > 0 ? Math.min(1, elapsed / duration) : completed ? 1 : 0;
  const bars = [16, 24, 30, 21, 34, 38, 26, 18, 28, 32, 30, 22, 35, 37, 25, 19, 29, 36, 31, 23];

  return (
    <div
      className="tw-card"
      style={{
        background: "#fff4e5",
        border: "1.5px solid #fdc283",
        borderRadius: 16,
        padding: "12px 14px",
        marginBottom: 10,
      }}
    >
      {resolvedAudioUrl && (
        <audio
          ref={audioRef}
          preload="metadata"
          src={resolvedAudioUrl}
          onLoadedMetadata={(event) => {
            const nextDuration = event.currentTarget.duration;
            if (Number.isFinite(nextDuration)) setDuration(Math.round(nextDuration));
          }}
          onTimeUpdate={(event) => setElapsed(event.currentTarget.currentTime)}
          onEnded={finishPlayback}
        />
      )}
      <div style={{ display: "flex", alignItems: "center", gap: 12, minWidth: 0 }}>
        <button
          type="button"
          onClick={playOnce}
          title={completed ? "Audio already played" : "Play audio"}
          aria-label={completed ? "Audio already played" : "Play audio"}
          disabled={completed || playing}
          style={{
            ...roundIconButton,
            width: 48,
            height: 48,
            background: completed ? "#d9a46f" : "#f59e0b",
            boxShadow: "0 5px 14px rgba(245,158,11,0.24)",
            cursor: completed || playing ? "not-allowed" : "pointer",
            opacity: completed ? 0.75 : 1,
          }}
        >
          <Play size={19} fill="currentColor" />
        </button>

        <div style={{ minWidth: 0, flex: "1 1 auto" }}>
          <div style={{ fontSize: 15.5, lineHeight: 1.2, fontWeight: 850, color: "var(--tw-navy)" }}>
            {title || "Listening audio"}
          </div>
          <div style={{ marginTop: 3, fontSize: 12.5, color: "#235273" }}>
            Native speed · {durationLabel} total
          </div>
          {!completed && hint && (
            <div style={{ marginTop: 4, fontSize: 12, lineHeight: 1.25, color: "#7a5a2c" }}>
              {hint}
            </div>
          )}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 10, flex: "0 0 auto" }}>
          <div
            aria-hidden
            style={{
              display: "flex",
              alignItems: "center",
              gap: 2.5,
              height: 38,
              width: "clamp(96px, 18vw, 220px)",
            }}
          >
            {bars.map((height, index) => {
              const filled = index / Math.max(1, bars.length - 1) <= progress;
              return (
                <span
                  key={index}
                  style={{
                    width: 3,
                    height,
                    borderRadius: 999,
                    background: filled ? "#f59e0b" : "#d7a981",
                    opacity: filled ? 1 : 0.75,
                  }}
                />
              );
            })}
          </div>
          <div style={{ minWidth: 36, textAlign: "right", fontSize: 13.5, lineHeight: 1.15, fontWeight: 800, color: "#235273" }}>
            {elapsedLabel}
            <br />
            <span>{durationLabel}</span>
          </div>
        </div>
      </div>
      {fallbackUnavailable && !completed && (
        <div
          style={{
            marginTop: 12,
            borderRadius: 12,
            border: "1px solid #f1b45d",
            background: "#fffaf0",
            padding: "10px 12px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 10,
          }}
        >
          <div style={{ fontSize: 12.5, lineHeight: 1.45, color: "#6f4a11", fontWeight: 700 }}>
            Audio playback is unavailable in this browser right now.
          </div>
          <button
            type="button"
            onClick={finishPlayback}
            style={{
              border: "none",
              borderRadius: 999,
              background: "#f59e0b",
              color: "white",
              fontSize: 12,
              fontWeight: 850,
              padding: "8px 12px",
              cursor: "pointer",
              flexShrink: 0,
            }}
          >
            Continue
          </button>
        </div>
      )}
    </div>
  );
}

function resolveAudioUrl(audioUrl?: string | null): string | null {
  if (!audioUrl) return null;
  if (/^(https?:|blob:|data:)/i.test(audioUrl)) return audioUrl;
  if (audioUrl.startsWith("/")) {
    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return `${apiBase.replace(/\/$/, "")}${audioUrl}`;
  }
  return audioUrl;
}

function formatClock(seconds: number): string {
  const total = Math.max(0, Math.round(seconds || 0));
  const minutes = Math.floor(total / 60);
  const rest = total % 60;
  return `${minutes}:${String(rest).padStart(2, "0")}`;
}

export function normalizeAnswer(value: string | undefined): string {
  return (value ?? "").trim().toLowerCase();
}

/** Words that fill a blank directly — no base-verb hint should appear beside them. */
const BLANK_HINT_WORDS = new Set([
  "i", "me", "you", "he", "him", "she", "her", "it", "we", "us", "they", "them",
  "mine", "yours", "his", "hers", "ours", "theirs",
  "my", "your", "our", "their", "its",
  "a", "an", "the", "this", "that", "these", "those",
]);

export function blankNeedsBaseVerbHint(item: {
  baseVerb?: string;
  correctAnswer?: string;
}): boolean {
  const baseVerb = item.baseVerb?.trim();
  if (!baseVerb) return false;
  const correct = normalizeAnswer(item.correctAnswer);
  if (BLANK_HINT_WORDS.has(correct)) return false;
  if (BLANK_HINT_WORDS.has(baseVerb.toLowerCase())) return false;
  // Never let the hint spell out the answer.
  if (normalizeAnswer(baseVerb) === correct) return false;
  return true;
}

/** Remove inline `(hint)` groups that leaked into passage text after a blank. */
export function stripLeadingParentheticalHints(text: string): string {
  const withoutHints = text.replace(/^(\s*\([^)]+\))+/, "");
  if (withoutHints === text) return text;
  return withoutHints.replace(/^\s+/, "");
}

/** Remove `(baseVerb)` hints from passage text — the UI renders them from `baseVerb`. */
export function stripInlineVerbHint(text: string, baseVerb?: string): string {
  if (!baseVerb?.trim()) return text;
  const escaped = baseVerb.trim().replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return text.replace(new RegExp(`\\(\\s*${escaped}\\s*\\)`, "gi"), "").replace(/^\s+/, "");
}

/** Coerce a live answers map to string values (fill-in / text widgets). */
export function liveStringRecord(
  answers: Record<string, unknown>,
): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [key, value] of Object.entries(answers)) {
    out[key] = value == null ? "" : String(value);
  }
  return out;
}

/** Coerce a live answers map to numeric values (MCQ option indices). */
export function liveNumberRecord(
  answers: Record<string, unknown>,
): Record<string, number> {
  const out: Record<string, number> = {};
  for (const [key, value] of Object.entries(answers)) {
    const num = Number(value);
    if (Number.isFinite(num)) out[key] = num;
  }
  return out;
}

/** Read MCQ selections from flat keys or nested inner_response.answers rows. */
export function liveMcqAnswerRecord(
  answers: Record<string, unknown>,
): Record<string, number> {
  const inner = answers.inner_response;
  if (typeof inner === "object" && inner !== null && !Array.isArray(inner)) {
    const rows = (inner as { answers?: unknown }).answers;
    if (Array.isArray(rows)) {
      const out: Record<string, number> = {};
      for (const row of rows) {
        if (typeof row !== "object" || row === null) continue;
        const itemId = (row as { item_id?: unknown }).item_id;
        const selected = (row as { selected_index?: unknown }).selected_index;
        const num = Number(selected);
        if (typeof itemId === "string" && itemId && Number.isFinite(num)) {
          out[itemId] = num;
        }
      }
      if (Object.keys(out).length > 0) return out;
    }
  }
  return liveNumberRecord(answers);
}

/**
 * Build the MCQ submit payload the backend MCQ evaluator accepts (see
 * `_listen_mcq_answer_rows`): a flat `item_id → selected_index` map plus the
 * nested `inner_response.answers[]` rows. Shared by every Mcq-family widget so
 * the submit shape never drifts between siblings.
 */
export function mcqSubmission(
  items: { itemId: string }[],
  answers: Record<string, number>,
): Record<string, unknown> {
  const answered = items.filter((item) => answers[item.itemId] !== undefined);
  return {
    ...Object.fromEntries(answered.map((item) => [item.itemId, answers[item.itemId]])),
    inner_response: {
      widget: "mcq",
      answers: answered.map((item) => ({
        item_id: item.itemId,
        selected_index: answers[item.itemId],
      })),
    },
  };
}

/**
 * Shared MCQ option list + explanation used by every Mcq-family widget. In live
 * interactive mode the options are clickable; after submit (live) or in a
 * preview review state they show the correct answer and the learner's wrong pick.
 */
export function McqOptionList({
  item,
  selected,
  interactive,
  showResults,
  onPick,
  optionKey,
}: {
  item: { itemId: string; options: string[]; correctIndex: number; explanation: string };
  selected: number | undefined;
  interactive: boolean;
  showResults: boolean;
  onPick: (optionIndex: number) => void;
  optionKey?: (optionIndex: number) => ReactNode;
}) {
  return (
    <>
      <div className="tw-opt-list">
        {item.options.map((option, optionIndex) => {
          const isSelected = optionIndex === selected;
          const isCorrect = showResults && optionIndex === item.correctIndex;
          const isWrongPick = showResults && isSelected && !isCorrect;
          const cls =
            "tw-opt-row" +
            (isCorrect ? " correct" : "") +
            (isWrongPick ? " wrong" : "") +
            (interactive && isSelected ? " selected" : "");
          const keyNode = optionKey ? optionKey(optionIndex) : optionIndex + 1;
          if (interactive) {
            return (
              <button
                type="button"
                key={option}
                className={cls}
                onClick={() => onPick(optionIndex)}
              >
                <span className="tw-opt-key">{keyNode}</span>
                <span style={{ flex: 1 }}>{option}</span>
                {isSelected && <Check size={14} strokeWidth={2.8} />}
              </button>
            );
          }
          return (
            <div className={cls} key={option} style={{ cursor: "default" }}>
              <span className="tw-opt-key">{keyNode}</span>
              <span style={{ flex: 1 }}>{option}</span>
              {isCorrect && <Check size={14} strokeWidth={2.8} />}
              {isWrongPick && <X size={14} strokeWidth={2.8} />}
            </div>
          );
        })}
      </div>
      {showResults && (
        <div className="tw-fb-explain" style={{ marginTop: 12, paddingTop: 10 }}>
          <strong>{selected === item.correctIndex ? "Correct." : "Why it is wrong."}</strong>{" "}
          {item.explanation}
        </div>
      )}
    </>
  );
}

export interface LiveTextItem {
  itemId: string;
  prompt?: string;
  sampleAnswer: string;
  context?: ReactNode;
  hints?: string[];
  placeholder?: string;
  minHeight?: number;
}

/**
 * Shared live 3-mode body for text-answer families (OpenText, Transform,
 * ErrorCorrection): a textarea per item before submit, a "your answer vs sample"
 * compare after submit, and a submit button. Submits the flat `live.answers`
 * map (item_id → text) the generic LLM evaluator reads. Per-item correctness is
 * decided by the LLM (shown in the feedback card), so no pass/fail marks here.
 */
export function LiveTextItems({
  items,
  live,
  numbered = true,
  yourLabel = "Your answer",
  sampleLabel = "Sample answer",
}: {
  items: LiveTextItem[];
  live: LiveTaskController;
  numbered?: boolean;
  yourLabel?: string;
  sampleLabel?: string;
}) {
  const interactive = !live.submitted;
  const answers = liveStringRecord(live.answers);
  const setAnswer = (itemId: string, value: string) =>
    live.setAnswers({ ...live.answers, [itemId]: value });
  const allAnswered = items.every((item) => (answers[item.itemId] ?? "").trim().length > 0);

  return (
    <>
      {items.map((item, index) => (
        <div className="tw-card" key={item.itemId}>
          {(numbered || item.prompt) && (
            <div className="tw-q-number-row" style={{ marginBottom: 12 }}>
              {numbered && <div className="tw-q-number-badge">{index + 1}</div>}
              {item.prompt && <div className="tw-q-stem">{item.prompt}</div>}
            </div>
          )}
          {item.context}
          {interactive ? (
            <textarea
              className="tw-write-area"
              value={answers[item.itemId] ?? ""}
              onChange={(event) => setAnswer(item.itemId, event.target.value)}
              placeholder={item.placeholder ?? "Write your answer here..."}
              style={{ minHeight: item.minHeight ?? 92 }}
              {...spatialFieldProps(index)}
            />
          ) : (
            <div className="tw-compare-grid">
              <div className="tw-compare-card">
                <div className="tw-compare-label">{yourLabel}</div>
                <div className="tw-compare-body">{answers[item.itemId]}</div>
              </div>
              {item.sampleAnswer.trim().length > 0 && (
                <div className="tw-compare-card sample">
                  <div className="tw-compare-label">
                    <Sparkles size={12} />
                    {sampleLabel}
                  </div>
                  <div className="tw-compare-body">{item.sampleAnswer}</div>
                </div>
              )}
            </div>
          )}
          {item.hints && item.hints.length > 0 && (
            <div className="tw-hints-block">
              <div className="tw-hints-label">Hints</div>
              <div className="tw-hints-list">
                {item.hints.map((hint) => (
                  <div className="tw-hint-item" key={hint}>
                    <span className="tw-hint-dot" />
                    {hint}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
      {interactive && (
        <SubmitButton disabled={!allAnswered} onClick={() => live.onSubmit(live.answers)} />
      )}
    </>
  );
}

export const roundIconButton: CSSProperties = {
  width: 42,
  height: 42,
  borderRadius: "50%",
  border: "none",
  background: "#0070C4",
  color: "white",
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  cursor: "pointer",
  flexShrink: 0,
  boxShadow: "0 6px 16px rgba(0,112,196,0.28)",
};
