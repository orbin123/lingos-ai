"use client";

import { useState } from "react";
import { TaskHeader, I, type WidgetState } from "./shared";

interface Props {
  state: WidgetState;
}

const MCQ_ITEMS = [
  {
    q: "Why did the speaker form a task force?",
    opts: ["To launch a new payments product", "To fix a recurring outage", "To replace the existing team", "To audit security"],
    correct: 1,
    user: 1,
  },
  {
    q: "Roughly how long did the fix take?",
    opts: ["One week", "About a month", "Six weeks", "Three months"],
    correct: 2,
    user: 2,
  },
  {
    q: "According to the speaker, what was the hardest part?",
    opts: ["The engineering work", "Getting alignment across teams", "Recruiting more engineers", "Convincing the CEO"],
    correct: 1,
    user: 0,
  },
];

const WAVE_BARS = Array.from({ length: 42 });

export function ListenAndRespondWidget({ state }: Props) {
  const [playing, setPlaying] = useState(false);
  const [transcript, setTranscript] = useState(false);
  const [unlocked, setUnlocked] = useState(state === "after");

  const playedTo = state === "after" ? 42 : 0;

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Listening · Job Interview Excerpt"
        intro={{
          title: "Listen, then respond",
          body: "Play the clip first — the questions unlock after the first play-through. Re-listening is encouraged.",
        }}
        sub_skill="Listening Comprehension"
        activity="Listen → Multiple Choice"
        time={6}
      />

      <div className="tw-audio-player">
        <button
          className={`tw-audio-play-btn${playing ? " playing" : ""}`}
          onClick={() => {
            setPlaying((p) => !p);
            setUnlocked(true);
          }}
        >
          {playing ? I.pause : I.play}
        </button>
        <div className="tw-audio-info">
          <div className="tw-audio-title">Interview clip — &quot;Tell me about a challenge&quot;</div>
          <div className="tw-audio-meta">
            Native speed · 0:48 total · plays: {state === "after" ? 2 : 0}
          </div>
        </div>
        <div className="tw-audio-wave">
          {WAVE_BARS.map((_, i) => {
            const h = 6 + Math.abs(Math.sin(i * 0.6) * 18) + (i % 4) * 1.5;
            return (
              <span
                key={i}
                className={`tw-audio-wave-bar${i < playedTo ? " played" : ""}`}
                style={{ height: h }}
              />
            );
          })}
        </div>
        <div className="tw-audio-time">{state === "after" ? "0:48" : "0:00"} / 0:48</div>
      </div>

      <div className="tw-listen-controls">
        <button
          className={`tw-transcript-toggle${transcript ? " on" : ""}`}
          onClick={() => setTranscript((t) => !t)}
        >
          {I.doc} {transcript ? "Hide transcript" : "Show transcript"}
        </button>
        <button className="tw-transcript-toggle">{I.replay} Replay 0.75×</button>
        {!unlocked && (
          <button className="tw-skip-task" onClick={() => setUnlocked(true)}>
            Skip to task →
          </button>
        )}
      </div>

      {transcript && (
        <div className="tw-transcript-box">
          &quot;Last year my team inherited a payments service that was failing once a week. I led a small task force, mapped every failure mode, and over six weeks we drove the error rate from 1.4% to under 0.05%. The hardest part wasn&apos;t the engineering — it was getting three teams to agree on what counted as a real outage.&quot;
        </div>
      )}

      <div
        className={!unlocked ? "tw-locked-veil" : ""}
        style={{ position: "relative", minHeight: !unlocked ? 280 : "auto" }}
      >
        <div
          style={{
            fontSize: 11,
            fontWeight: 800,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
            color: "var(--tw-ink-muted)",
            marginBottom: 8,
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          {I.ear} Inner task · Multiple choice (3 questions)
        </div>

        {MCQ_ITEMS.map((item, qi) => (
          <div className="tw-card" key={qi}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{qi + 1}</div>
              <div className="tw-q-stem">{item.q}</div>
            </div>
            <div className="tw-opt-list">
              {item.opts.map((o, oi) => {
                let cls = "tw-opt-row";
                if (state === "before" && item.user === oi) cls += " selected";
                else if (state === "after") {
                  if (oi === item.correct) cls += " correct";
                  else if (oi === item.user && oi !== item.correct) cls += " wrong";
                }
                return (
                  <button key={oi} className={cls} disabled={state === "after"}>
                    <span className="tw-opt-key">{String.fromCharCode(65 + oi)}</span>
                    <span style={{ flex: 1 }}>{o}</span>
                    {state === "after" && oi === item.correct && (
                      <span style={{ color: "var(--tw-green)" }}>{I.check}</span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {state === "after" && (
        <>
          <div className="tw-result-banner mid" style={{ marginTop: 14 }}>
            <div className="tw-result-icon">{I.spark}</div>
            <div className="tw-result-text">
              <div className="tw-result-headline">2 of 3 correct · listening analytics captured</div>
              <div className="tw-result-sub">
                You re-listened twice and toggled the transcript once — healthy signs of careful listening.
              </div>
            </div>
            <div>
              <div className="tw-result-score">
                67<span style={{ fontSize: 14, color: "var(--tw-ink-muted)" }}>%</span>
              </div>
              <div className="tw-result-score-sub">Comp.</div>
            </div>
          </div>
          <div className="tw-analytics-grid">
            <div className="tw-metric">
              <div className="tw-metric-num primary">2</div>
              <div className="tw-metric-label">Plays</div>
            </div>
            <div className="tw-metric">
              <div className="tw-metric-num">1</div>
              <div className="tw-metric-label">Transcript toggles</div>
            </div>
            <div className="tw-metric">
              <div className="tw-metric-num" style={{ color: "var(--tw-green)" }}>0:48</div>
              <div className="tw-metric-label">Listened</div>
            </div>
          </div>
        </>
      )}

      {state === "before" && unlocked && (
        <button className="tw-submit-btn">{I.send} Submit answers + listening trace</button>
      )}
    </div>
  );
}
