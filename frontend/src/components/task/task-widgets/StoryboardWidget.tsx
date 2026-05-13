"use client";

import { useState } from "react";
import { TaskHeader, I, type WidgetState } from "./shared";

interface Props {
  state: WidgetState;
}

const SCENES = [
  { id: 1, title: "Morning", focus: "Set the scene — where is she and what is she doing?", label: "Maya at kitchen, holding coffee", loaded: true },
  { id: 2, title: "Discovery", focus: "Describe what she finds and how she reacts.", label: "Envelope on the doormat", loaded: true },
  { id: 3, title: "Reaction", focus: "Express her emotion in detail — body language, thoughts.", label: "Maya reading the letter", loadedAfter: true },
  { id: 4, title: "Decision", focus: "What does she decide to do next? Use a future form.", label: "Maya packing a small bag", loadedAfter: true },
];

const TIMESTAMPS = [
  { id: 1, start: "0:00", end: "0:12" },
  { id: 2, start: "0:12", end: "0:26" },
  { id: 3, start: "0:26", end: "0:41" },
  { id: 4, start: "0:41", end: "0:58" },
];

export function StoryboardWidget({ state }: Props) {
  const [active, setActive] = useState(1);
  const [recording, setRecording] = useState(false);

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Speaking · Narrative Storyboard"
        intro={{
          title: "Tell the story scene by scene",
          body: "One continuous recording. Move to the next scene when you're ready — we'll capture the timestamp for each one automatically.",
        }}
        sub_skill="Narrative Past"
        activity="Storyboard Speaking"
        time={5}
      />

      <div className="tw-scene-strip">
        {SCENES.map((s) => {
          const loaded = s.loaded || (s.loadedAfter && state === "after");
          return (
            <div
              key={s.id}
              className={`tw-scene-card${s.id === active && state === "before" ? " active" : ""}`}
              onClick={() => state === "before" && setActive(s.id)}
            >
              <div className={`tw-scene-img${loaded ? " filled" : " skeleton"}`}>
                {loaded ? s.label : ""}
              </div>
              <div className="tw-scene-meta">
                <div className="tw-scene-num">Scene {s.id} · {s.title}</div>
                <div className="tw-scene-caption">{s.focus}</div>
              </div>
            </div>
          );
        })}
      </div>

      {state === "before" ? (
        <>
          <div className="tw-scene-active-banner">
            <div className="tw-scene-active-num">{active}</div>
            <div className="tw-scene-active-text">
              <div className="tw-scene-active-label">Now narrating · Scene {active} of {SCENES.length}</div>
              <div className="tw-scene-active-focus">
                {SCENES.find((s) => s.id === active)?.focus}
              </div>
            </div>
          </div>

          <div className="tw-mic-stage">
            <div className="tw-mic-prompt">
              {recording ? "Recording your story" : "One take · keep going through all scenes"}
            </div>
            <div className="tw-mic-button-wrap">
              <button
                className={`tw-mic-button${recording ? " recording" : ""}`}
                onClick={() => setRecording((r) => !r)}
              >
                {recording ? I.stop : I.mic}
              </button>
              <span className="tw-mic-ring" />
            </div>
            <div className="tw-mic-instruction">
              {recording ? "Tap to stop · or finish all scenes first" : "Tap to start the single take"}
            </div>
            <div className="tw-mic-sub">We&apos;ll mark when you click Next Scene</div>
            {recording && (
              <div className="tw-rec-timer">
                <span className="tw-rec-dot" />
                0:23
              </div>
            )}
          </div>

          <div className="tw-scene-nav">
            <button
              className="tw-scene-nav-btn"
              disabled={active === 1}
              onClick={() => setActive((a) => Math.max(1, a - 1))}
            >
              {I.arrowL} Previous
            </button>
            <button
              className={`tw-scene-nav-btn${active < SCENES.length ? " primary" : ""}`}
              onClick={() => setActive((a) => Math.min(SCENES.length, a + 1))}
              disabled={active === SCENES.length}
            >
              {active === SCENES.length ? "Last scene" : "Next scene"} {I.arrowR}
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="tw-result-banner good">
            <div className="tw-result-icon" style={{ color: "var(--tw-green)" }}>{I.check}</div>
            <div className="tw-result-text">
              <div className="tw-result-headline">Story complete · 58 sec across 4 scenes</div>
              <div className="tw-result-sub">
                Clear narrative arc · used past simple consistently · transitioned smoothly between scenes.
              </div>
            </div>
            <div>
              <div className="tw-result-score">0:58</div>
              <div className="tw-result-score-sub">Total</div>
            </div>
          </div>

          <div className="tw-card" style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <button className="tw-audio-play-btn playing" style={{ width: 44, height: 44 }}>
              {I.play}
            </button>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: "var(--tw-navy)" }}>
                Single continuous recording
              </div>
              <div style={{ fontSize: 11.5, color: "var(--tw-ink-muted)", fontWeight: 600 }}>
                blob://storyboard-7d2a · 4 scene markers
              </div>
            </div>
            <div className="tw-audio-wave">
              {Array.from({ length: 32 }).map((_, i) => (
                <span
                  key={i}
                  className="tw-audio-wave-bar played"
                  style={{ height: 6 + Math.abs(Math.sin(i * 0.5) * 16) + (i % 4) * 2 }}
                />
              ))}
            </div>
          </div>

          <div
            style={{
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              color: "var(--tw-ink-muted)",
              marginTop: 14,
              marginBottom: 8,
            }}
          >
            Scene timestamps captured
          </div>
          <div className="tw-ts-table">
            <div className="tw-ts-row head">
              <div>#</div>
              <div>Scene focus</div>
              <div>Time</div>
            </div>
            {TIMESTAMPS.map((t, i) => (
              <div className="tw-ts-row" key={t.id}>
                <div className="tw-ts-scene-num">{t.id}</div>
                <div className="tw-ts-cap">
                  {SCENES[i].title} — {SCENES[i].label}
                </div>
                <div className="tw-ts-time">
                  {t.start}–{t.end}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
