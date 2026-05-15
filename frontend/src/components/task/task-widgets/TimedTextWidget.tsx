"use client";

import { useEffect, useRef, useState } from "react";
import { TaskHeader, I } from "./shared";
import { countWords } from "./types";
import type { TimedTextPayload, WidgetProps } from "./types";

type Props = WidgetProps<TimedTextPayload>;

export function TimedTextWidget({ payload, answers, setAnswers, state, onSubmit }: Props) {
  const submitted = state === "after";
  const totalSec = Math.max(1, payload.time_limit_seconds || 180);
  const targetWords = payload.target_word_count || 80;
  const minWords = payload.minimum_word_count || 0;
  const noEditing = !!payload.no_editing_allowed;

  const startedAtRef = useRef(Date.now());
  const firstTypeAtRef = useRef<number | null>(null);
  const submittedRef = useRef(submitted);
  submittedRef.current = submitted;

  const [text, setText] = useState<string>((answers.user_answer as string) ?? "");
  const [elapsed, setElapsed] = useState(0);
  const autoSubmittedRef = useRef(false);

  const remaining = Math.max(0, totalSec - elapsed);
  const wordCount = countWords(text);

  // Tick timer
  useEffect(() => {
    if (submitted) return;
    const interval = setInterval(() => {
      setElapsed((e) => e + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [submitted]);

  // Auto-submit when timer hits 0
  useEffect(() => {
    if (submitted || autoSubmittedRef.current) return;
    if (elapsed < totalSec) return;
    autoSubmittedRef.current = true;
    publish(text, true);
    onSubmit();
  }, [elapsed, totalSec, submitted, text, onSubmit]); // eslint-disable-line react-hooks/exhaustive-deps

  const publish = (nextText: string, completedNormally: boolean) => {
    const wc = countWords(nextText);
    setAnswers({
      user_answer: nextText,
      word_count: wc,
      time_spent_seconds: Math.min(totalSec, Math.round((Date.now() - startedAtRef.current) / 1000)),
      hit_target_word_count: wc >= targetWords,
      completed_normally: completedNormally,
    });
  };

  const handleChange = (next: string) => {
    if (submitted) return;
    if (firstTypeAtRef.current == null) firstTypeAtRef.current = Date.now();
    setText(next);
    publish(next, false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (!noEditing || submitted) return;
    if (firstTypeAtRef.current == null) return;
    const sinceFirst = Date.now() - firstTypeAtRef.current;
    if (sinceFirst < 3000) return;
    if (e.key === "Backspace" || e.key === "Delete") {
      e.preventDefault();
    }
  };

  const mm = String(Math.floor(remaining / 60));
  const ss = String(remaining % 60).padStart(2, "0");
  const R = 22;
  const C = 2 * Math.PI * R;
  const dash = submitted ? C : C * (elapsed / totalSec);
  const warning = !submitted && remaining < 30;

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Timed Writing"
        intro={{
          title: payload.task_intro || "Just keep writing",
          body: payload.instructions || "No editing — write as much as you can before the timer runs out.",
        }}
        sub_skill={payload.sub_skill || "Writing fluency"}
        activity={payload.activity || "Timed Free-write"}
        time={payload.estimated_time_minutes ?? Math.ceil(totalSec / 60)}
      />

      <div
        className="tw-card"
        style={{
          background: "linear-gradient(135deg, oklch(96% 0.04 290), white)",
          borderColor: "oklch(82% 0.1 290)",
        }}
      >
        <div className="tw-rule-label" style={{ color: "oklch(40% 0.16 290)" }}>
          Prompt
        </div>
        <div
          style={{
            fontSize: 17,
            fontWeight: 700,
            color: "var(--tw-navy)",
            lineHeight: 1.4,
            marginTop: 4,
          }}
        >
          {payload.writing_prompt}
        </div>
      </div>

      <div className="tw-timer-bar">
        <div className={`tw-timer-dial${warning ? " warn" : ""}`}>
          <svg width="56" height="56" viewBox="0 0 56 56">
            <circle cx="28" cy="28" r={R} fill="none" stroke="oklch(92% 0.02 240)" strokeWidth="4" />
            <circle
              cx="28"
              cy="28"
              r={R}
              fill="none"
              stroke={warning ? "var(--tw-amber)" : "var(--tw-violet)"}
              strokeWidth="4"
              strokeLinecap="round"
              strokeDasharray={`${dash} ${C}`}
              transform="rotate(-90 28 28)"
            />
          </svg>
          <span style={{ fontSize: 13, position: "relative", zIndex: 1 }}>
            {mm}:{ss}
          </span>
        </div>
        <div className="tw-timer-text">
          <div className="tw-timer-label">{submitted ? "Time up" : "Time remaining"}</div>
          <div className="tw-timer-hint">
            {submitted ? "Response submitted" : "Keep going — don't stop"}
          </div>
          <div className="tw-timer-sub">
            {noEditing
              ? submitted
                ? "Backspace was locked"
                : "Backspace & Delete blocked after 3s of typing"
              : "Free editing allowed"}
          </div>
        </div>
        <div className="tw-timer-words">
          <div className={`tw-timer-words-num ${wordCount < targetWords ? "short" : "ok"}`}>
            {wordCount}
          </div>
          <div className="tw-timer-words-target">of {targetWords} words</div>
        </div>
      </div>

      <textarea
        className="tw-write-area"
        style={{
          minHeight: 180,
          fontSize: 15,
          lineHeight: 1.7,
          background: submitted ? "oklch(98% 0.01 240)" : "white",
        }}
        value={text}
        onChange={(e) => handleChange(e.target.value)}
        onKeyDown={handleKeyDown}
        readOnly={submitted}
        autoCorrect="off"
        autoCapitalize="off"
        spellCheck={false}
        placeholder="Start typing immediately…"
      />

      {noEditing && (
        <div className="tw-lock-banner warn">
          {I.lock}{" "}
          {submitted
            ? "Textarea locked. Submission recorded."
            : "Editing locked after 3s of typing — Backspace & Delete blocked."}
        </div>
      )}

      {!submitted ? (
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginTop: 14,
            gap: 10,
            flexWrap: "wrap",
          }}
        >
          <span style={{ fontSize: 12, color: "var(--tw-ink-muted)", fontWeight: 600 }}>
            Auto-submit when timer hits 0:00
            {minWords > 0 && ` · Minimum ${minWords} words to count`}
          </span>
          <button
            className="tw-done-early-btn"
            onClick={() => {
              publish(text, true);
              onSubmit();
            }}
            disabled={wordCount < Math.max(1, minWords)}
          >
            {I.check} I&apos;m done early
          </button>
        </div>
      ) : (
        <>
          <div className="tw-result-banner good" style={{ marginTop: 14 }}>
            <div className="tw-result-icon" style={{ color: "var(--tw-green)" }}>
              {I.check}
            </div>
            <div className="tw-result-text">
              <div className="tw-result-headline">
                {wordCount} words in {formatTime(Math.min(elapsed, totalSec))}
              </div>
              <div className="tw-result-sub">
                {wordCount >= targetWords
                  ? "Hit the target word count."
                  : `${targetWords - wordCount} words short of target.`}
              </div>
            </div>
            <div>
              <div className="tw-result-score">
                {wordCount}
                <span style={{ fontSize: 14, color: "var(--tw-ink-muted)" }}>
                  {" "}/ {targetWords}
                </span>
              </div>
              <div className="tw-result-score-sub">Words</div>
            </div>
          </div>
          {payload.sample_response && (
            <div className="tw-compare-card sample" style={{ marginTop: 8 }}>
              <div className="tw-compare-label">{I.spark} Sample response</div>
              <div className="tw-compare-body">{payload.sample_response}</div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}
