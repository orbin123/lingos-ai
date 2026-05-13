"use client";

import { useState } from "react";
import { TaskHeader, I, type WidgetState } from "./shared";

interface Props {
  state: WidgetState;
}

type Mode = "list" | "single" | "read" | "role";

const MODES: { id: Mode; label: string }[] = [
  { id: "list", label: "List" },
  { id: "single", label: "Single Prompt" },
  { id: "read", label: "Read Aloud" },
  { id: "role", label: "Roleplay" },
];

const LIST_PROMPTS = [
  { id: 1, q: "Introduce yourself in 15 seconds.", dur: "0:14" },
  { id: 2, q: "Describe your morning routine.", dur: "0:28" },
  { id: 3, q: "Talk about a hobby you started this year.", dur: null },
];

export function SpeakRecordWidget({ state }: Props) {
  const [mode, setMode] = useState<Mode>("single");
  const [recording, setRecording] = useState(false);

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Speaking · Real-life Scenarios"
        intro={{
          title: "Record your response",
          body: "Use the microphone to record your spoken answer. Up to 3 re-record attempts before submission.",
        }}
        sub_skill="Spoken Fluency"
        activity="Speak & Record"
        time={6}
      />

      <div className="tw-mode-tabs">
        {MODES.map((m) => (
          <button
            key={m.id}
            className={`tw-mode-tab${mode === m.id ? " active" : ""}`}
            onClick={() => setMode(m.id)}
          >
            {m.label}
          </button>
        ))}
      </div>

      {mode === "single" && (
        <>
          <div
            className="tw-card"
            style={{ background: "oklch(96% 0.04 290)", borderColor: "oklch(82% 0.1 290)" }}
          >
            <div className="tw-rule-label" style={{ color: "oklch(40% 0.16 290)" }}>
              Speaking prompt
            </div>
            <div style={{ fontSize: 17, fontWeight: 700, color: "var(--tw-navy)", lineHeight: 1.4, marginTop: 4 }}>
              Tell me about a place that feels like home — describe what you see, hear, and smell there.
            </div>
          </div>

          {state === "before" ? (
            <div className="tw-mic-stage">
              <div className="tw-prep-countdown">{I.clock} Prep time · 0:18 left</div>
              <div className="tw-mic-prompt">When ready, tap to record</div>
              <div style={{ fontSize: 15, fontWeight: 700, color: "var(--tw-navy)", marginBottom: 14 }}>
                Target length: 30–60 seconds
              </div>
              <div className="tw-mic-button-wrap">
                <button
                  className={`tw-mic-button${recording ? " recording" : ""}`}
                  onClick={() => setRecording((r) => !r)}
                >
                  {I.mic}
                </button>
                <span className="tw-mic-ring" />
              </div>
              <div className="tw-mic-instruction">{recording ? "Listening…" : "Tap to begin"}</div>
              <div className="tw-mic-sub">
                {recording ? "Tap again to stop" : "Microphone permission required"}
              </div>
              {recording && (
                <>
                  <div className="tw-mic-live-bars">
                    {Array.from({ length: 21 }).map((_, i) => (
                      <span
                        key={i}
                        className="tw-mic-live-bar"
                        style={{ animationDelay: `${i * 0.06}s`, height: 8 + (i % 5) * 4 }}
                      />
                    ))}
                  </div>
                  <div className="tw-rec-timer">
                    <span className="tw-rec-dot" />
                    0:23
                  </div>
                </>
              )}
              <div className="tw-attempts-row">
                <span>Attempts:</span>
                <span className="tw-attempt-dot used" />
                <span className="tw-attempt-dot" />
                <span className="tw-attempt-dot" />
                <span style={{ marginLeft: 4 }}>1 of 3 used</span>
              </div>
            </div>
          ) : (
            <>
              <div className="tw-result-banner good">
                <div className="tw-result-icon" style={{ color: "var(--tw-green)" }}>{I.check}</div>
                <div className="tw-result-text">
                  <div className="tw-result-headline">Recorded · 42 sec · sent for analysis</div>
                  <div className="tw-result-sub">Pronunciation clear · 2 hesitations · pace 124 wpm.</div>
                </div>
                <div>
                  <div className="tw-result-score">0:42</div>
                  <div className="tw-result-score-sub">Duration</div>
                </div>
              </div>
              <div className="tw-card" style={{ display: "flex", alignItems: "center", gap: 14 }}>
                <button className="tw-audio-play-btn playing" style={{ width: 44, height: 44 }}>
                  {I.play}
                </button>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "var(--tw-navy)" }}>Your recording</div>
                  <div style={{ fontSize: 11.5, color: "var(--tw-ink-muted)", fontWeight: 600 }}>
                    blob://recording-3a8c · 42 seconds · final attempt
                  </div>
                </div>
                <div className="tw-audio-wave">
                  {Array.from({ length: 24 }).map((_, i) => (
                    <span
                      key={i}
                      className="tw-audio-wave-bar played"
                      style={{ height: 6 + Math.abs(Math.sin(i * 0.7) * 16) + (i % 3) * 2 }}
                    />
                  ))}
                </div>
              </div>
              <div className="tw-rerecord-row">
                <button className="tw-action-pill">
                  <span style={{ transform: "scaleX(-1)", display: "inline-block" }}>{I.replay}</span> Re-record (2 left)
                </button>
                <button className="tw-action-pill primary">{I.send} Submit recording</button>
              </div>
            </>
          )}
        </>
      )}

      {mode === "list" && (
        <div>
          {LIST_PROMPTS.map((p) => (
            <div className="tw-card" key={p.id} style={{ display: "flex", gap: 14, alignItems: "center" }}>
              <div className="tw-q-number-badge">{p.id}</div>
              <div style={{ flex: 1, fontSize: 14, fontWeight: 600, color: "var(--tw-navy)" }}>{p.q}</div>
              {p.dur && state === "after" ? (
                <span className="tw-recorded-clip">
                  <span className="tw-play-mini">{I.playMini}</span> {p.dur}
                </span>
              ) : (
                <button className="tw-action-pill">
                  <span style={{ color: "var(--tw-red)" }}>{I.micSm}</span> Record
                </button>
              )}
            </div>
          ))}
          {state === "before" && (
            <button className="tw-submit-btn" disabled>
              {I.send} Record all 3 to submit
            </button>
          )}
        </div>
      )}

      {mode === "read" && (
        <div>
          <div className="tw-passage">
            <div className="tw-passage-label">Passage · 64 words</div>
            <span style={{ fontSize: 15, lineHeight: 1.85 }}>
              {state === "after" ? (
                <>
                  <span style={{ background: "var(--tw-green-soft)", padding: "1px 3px", borderRadius: 3 }}>
                    The old library on Elm Street has stood for over a hundred years.
                  </span>{" "}
                  Inside, the air smells of paper and varnish.{" "}
                  <span style={{ background: "oklch(94% 0.07 65)", padding: "1px 3px", borderRadius: 3, color: "oklch(40% 0.14 65)" }}>
                    Children gather in the corner on Saturday mornings,
                  </span>{" "}
                  listening to volunteers read aloud while their parents browse the stacks for something new — or something they&apos;ve forgotten they once loved.
                </>
              ) : (
                "The old library on Elm Street has stood for over a hundred years. Inside, the air smells of paper and varnish. Children gather in the corner on Saturday mornings, listening to volunteers read aloud while their parents browse the stacks for something new — or something they've forgotten they once loved."
              )}
            </span>
          </div>
          {state === "before" ? (
            <div className="tw-mic-stage">
              <div className="tw-mic-prompt">Read the passage above out loud</div>
              <div style={{ fontSize: 13, color: "var(--tw-ink-muted)", marginBottom: 14 }}>
                We&apos;ll score pace, pronunciation, and word-stress.
              </div>
              <div className="tw-mic-button-wrap">
                <button className="tw-mic-button">{I.mic}</button>
                <span className="tw-mic-ring" />
              </div>
              <div className="tw-mic-instruction">Tap to start reading</div>
            </div>
          ) : (
            <div className="tw-result-banner mid">
              <div className="tw-result-icon">{I.spark}</div>
              <div className="tw-result-text">
                <div className="tw-result-headline">Clear read · 1 hesitation</div>
                <div className="tw-result-sub">
                  &quot;Gather&quot; pronounced softly — try a harder G sound. Otherwise excellent pace at 132 wpm.
                </div>
              </div>
              <div>
                <div className="tw-result-score">
                  8.6<span style={{ fontSize: 14, color: "var(--tw-ink-muted)" }}>/10</span>
                </div>
                <div className="tw-result-score-sub">Read score</div>
              </div>
            </div>
          )}
        </div>
      )}

      {mode === "role" && (
        <div>
          <div style={{ fontSize: 12.5, color: "var(--tw-ink-muted)", fontWeight: 600, marginBottom: 10 }}>
            Roleplay · You&apos;re checking into a hotel. The AI plays the front-desk agent — record your reply each turn.
          </div>
          <div className="tw-chat-stack">
            <div className="tw-chat-row">
              <div className="tw-chat-avatar">AI</div>
              <div className="tw-chat-bubble">
                <div className="tw-tts-line">
                  <button className="tw-tts-play">{I.playMini}</button>
                  <span>Good evening! Do you have a reservation with us tonight?</span>
                </div>
              </div>
            </div>
            <div className="tw-chat-row user">
              <div className="tw-chat-avatar">You</div>
              <div className="tw-chat-bubble">
                <span className="tw-recorded-clip">
                  <span className="tw-play-mini">{I.playMini}</span> 0:09
                </span>
                {state === "after" && (
                  <div style={{ fontSize: 12.5, marginTop: 6, color: "var(--tw-ink-muted)" }}>
                    &quot;Yes, I have a reservation under the name Patel for two nights.&quot;
                  </div>
                )}
              </div>
            </div>
            <div className="tw-chat-row">
              <div className="tw-chat-avatar">AI</div>
              <div className="tw-chat-bubble">
                <div className="tw-tts-line">
                  <button className="tw-tts-play">{I.playMini}</button>
                  <span>
                    Perfect, I see your booking. Would you prefer a quiet room facing the courtyard, or a higher floor with a city view?
                  </span>
                </div>
              </div>
            </div>
            <div className="tw-chat-row user">
              <div className="tw-chat-avatar">You</div>
              <div
                className="tw-chat-bubble"
                style={{
                  background: state === "after" ? undefined : "oklch(96% 0.02 240)",
                  borderStyle: state === "after" ? "solid" : "dashed",
                }}
              >
                {state === "after" ? (
                  <span className="tw-recorded-clip">
                    <span className="tw-play-mini">{I.playMini}</span> 0:07
                  </span>
                ) : (
                  <button className="tw-action-pill">
                    <span style={{ color: "var(--tw-red)" }}>{I.micSm}</span> Record your reply
                  </button>
                )}
              </div>
            </div>
          </div>
          {state === "after" && (
            <div className="tw-result-banner good" style={{ marginTop: 4 }}>
              <div className="tw-result-icon" style={{ color: "var(--tw-green)" }}>{I.check}</div>
              <div className="tw-result-text">
                <div className="tw-result-headline">2 turns recorded · natural flow</div>
                <div className="tw-result-sub">
                  Polite register maintained. Try &quot;I&apos;d prefer&quot; instead of &quot;I want&quot; for a softer tone.
                </div>
              </div>
              <div>
                <div className="tw-result-score">
                  9.0<span style={{ fontSize: 14, color: "var(--tw-ink-muted)" }}>/10</span>
                </div>
                <div className="tw-result-score-sub">Score</div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
