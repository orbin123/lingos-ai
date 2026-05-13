"use client";

import { TaskHeader, I, type WidgetState } from "./shared";

interface Props {
  state: WidgetState;
}

const TOTAL_SEC = 180;
const TARGET_WORDS = 80;

const LIVE_TEXT_BEFORE =
  "Last weekend I traveled to a small mountain town with two old friends. We rented a cabin near a frozen lake and spent most of Saturday hiking. The trail was steeper than we expected, and by the time we reached the top we were exhausted but";
const LIVE_TEXT_AFTER =
  "Last weekend I traveled to a small mountain town with two old friends. We rented a cabin near a frozen lake and spent most of Saturday hiking. The trail was steeper than we expected, and by the time we reached the top we were exhausted but happy. We made a simple dinner of pasta and tomato sauce, talked for hours about the past, and went to bed early because the cold drained all our energy. On Sunday morning we walked back down through fresh snow.";

export function TimedTextWidget({ state }: Props) {
  const elapsed = state === "before" ? 52 : TOTAL_SEC;
  const remaining = TOTAL_SEC - elapsed;
  const mm = String(Math.floor(remaining / 60));
  const ss = String(remaining % 60).padStart(2, "0");
  const liveText = state === "before" ? LIVE_TEXT_BEFORE : LIVE_TEXT_AFTER;
  const wordCount = liveText.trim().split(/\s+/).length;

  const R = 22;
  const C = 2 * Math.PI * R;
  const dash = state === "before" ? C * (elapsed / TOTAL_SEC) : C;

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Fluency · Write Without Stopping"
        intro={{
          title: "Just keep writing",
          body: "No editing, no backspace — once the timer starts, only forward motion. The point is to build flow, not perfection.",
        }}
        sub_skill="Writing Fluency"
        activity="Timed Free-write"
        time={3}
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
        <div style={{ fontSize: 17, fontWeight: 700, color: "var(--tw-navy)", lineHeight: 1.4, marginTop: 4 }}>
          Describe a recent trip in as much sensory detail as you can — what you saw, smelled, ate, and how it made you feel.
        </div>
      </div>

      <div className="tw-timer-bar">
        <div className={`tw-timer-dial${remaining < 30 && state === "before" ? " warn" : ""}`}>
          <svg width="56" height="56" viewBox="0 0 56 56">
            <circle cx="28" cy="28" r={R} fill="none" stroke="oklch(92% 0.02 240)" strokeWidth="4" />
            <circle
              cx="28"
              cy="28"
              r={R}
              fill="none"
              stroke={remaining < 30 && state === "before" ? "var(--tw-amber)" : "var(--tw-violet)"}
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
          <div className="tw-timer-label">{state === "before" ? "Time remaining" : "Time up"}</div>
          <div className="tw-timer-hint">
            {state === "before" ? "Keep going — don't stop or edit" : "Response auto-submitted"}
          </div>
          <div className="tw-timer-sub">
            {state === "before" ? "Backspace and delete are disabled" : "Total time spent: 3:00"}
          </div>
        </div>
        <div className="tw-timer-words">
          <div className={`tw-timer-words-num ${wordCount < TARGET_WORDS ? "short" : "ok"}`}>
            {wordCount}
          </div>
          <div className="tw-timer-words-target">of {TARGET_WORDS} words</div>
        </div>
      </div>

      <textarea
        className="tw-write-area"
        style={{
          minHeight: 180,
          fontSize: 15,
          lineHeight: 1.7,
          background: state === "after" ? "oklch(98% 0.01 240)" : "white",
        }}
        defaultValue={liveText}
        readOnly={state === "after"}
      />

      <div className="tw-lock-banner warn">
        {I.lock}{" "}
        {state === "before"
          ? "Editing locked after 3s of typing — Backspace & Delete blocked."
          : "Textarea locked. Submission recorded with full keystroke trace."}
      </div>

      {state === "before" ? (
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
          </span>
          <button className="tw-done-early-btn">{I.check} I&apos;m done early</button>
        </div>
      ) : (
        <>
          <div className="tw-result-banner good" style={{ marginTop: 14 }}>
            <div className="tw-result-icon" style={{ color: "var(--tw-green)" }}>{I.check}</div>
            <div className="tw-result-text">
              <div className="tw-result-headline">
                Strong fluency — {wordCount} words in 3:00
              </div>
              <div className="tw-result-sub">
                Avg pace: {Math.round(wordCount / 3)} wpm · sensory verbs: 7 · zero stops over 5s.
              </div>
            </div>
            <div>
              <div className="tw-result-score">
                {wordCount}
                <span style={{ fontSize: 14, color: "var(--tw-ink-muted)" }}> / {TARGET_WORDS}</span>
              </div>
              <div className="tw-result-score-sub">Words</div>
            </div>
          </div>
          <div className="tw-analytics-grid">
            <div className="tw-metric">
              <div className="tw-metric-num primary">{Math.round(wordCount / 3)}</div>
              <div className="tw-metric-label">Words / min</div>
            </div>
            <div className="tw-metric">
              <div className="tw-metric-num">2</div>
              <div className="tw-metric-label">Pauses &gt;5s</div>
            </div>
            <div className="tw-metric">
              <div className="tw-metric-num" style={{ color: "var(--tw-green)" }}>3:00</div>
              <div className="tw-metric-label">Time spent</div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
