"use client";

import { Mic2, Volume2 } from "lucide-react";
import { useState } from "react";
import type { SessionPreviewState } from "../../teaching/source";
import type { ListenShadowTask, LiveTaskController } from "../source";
import { LivePronunciationRecorder } from "./LivePronunciationRecorder";
import { ListeningAudioCard, ResultBanner, RuleCallout, TargetWordsRow, TaskWidgetFrame, StatusDot } from "./TaskWidgetFrame";

function LiveListenShadow({ task, live }: { task: ListenShadowTask; live: LiveTaskController }) {
  const [audioComplete, setAudioComplete] = useState(false);
  const unlocked = live.submitted || audioComplete;
  return (
    <TaskWidgetFrame task={task} icon={<Volume2 size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Shadowing focus">{task.grammarRule}</RuleCallout>
      <TargetWordsRow words={task.targetWords} label="Target phrases" />
      <ListeningAudioCard
        title={task.audioGenre}
        script={task.audioScript}
        audioUrl={task.audioUrl}
        durationSeconds={task.audioDurationSeconds}
        completed={unlocked}
        hint="Listen once, then shadow (repeat) the line aloud."
        onComplete={() => setAudioComplete(true)}
      />
      {unlocked && (
        <>
          <div className="tw-passage">
            <div className="tw-passage-label">Shadow this line</div>
            {task.textToShadow}
          </div>
          <LivePronunciationRecorder
            live={live}
            referenceText={task.textToShadow}
            durationSeconds={task.audioDurationSeconds || 30}
          />
        </>
      )}
    </TaskWidgetFrame>
  );
}

export function ListenShadowTaskWidget({
  task,
  previewState,
  live,
}: {
  task: ListenShadowTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  if (live) {
    return <LiveListenShadow task={task} live={live} />;
  }
  const isDefault = previewState === "default";
  const answer = isDefault ? null : task.answers[previewState][0];
  const correctCount = answer?.isCorrect ? 1 : 0;

  return (
    <TaskWidgetFrame task={task} icon={<Volume2 size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Shadowing focus">{task.grammarRule}</RuleCallout>

      {/* Target phrases highlight */}
      <div style={{ marginBottom: 14 }}>
        <div style={{ fontSize: 12, fontWeight: 800, color: "oklch(45% 0.07 240)", marginBottom: 6, textTransform: "uppercase" }}>
          Target fast possessives
        </div>
        <div className="tw-target-chip-row">
          {task.targetWords.map((word) => (
            <span 
              className="tw-target-chip used" 
              key={word}
              style={{
                background: "oklch(93% 0.04 155)",
                color: "oklch(42% 0.16 155)",
                border: "1px solid oklch(85% 0.06 155)"
              }}
            >
              {word}
            </span>
          ))}
        </div>
      </div>

      {/* Audio player UI */}
      <div 
        style={{
          border: "1.5px solid oklch(90% 0.02 240)",
          borderRadius: 18,
          background: "oklch(97% 0.015 245)",
          padding: 16,
          display: "flex",
          alignItems: "center",
          gap: 14,
          marginBottom: 16,
          boxShadow: "inset 0 2px 8px rgba(80,110,180,0.03)"
        }}
      >
        <button
          type="button"
          disabled
          aria-label="Play source audio"
          title="Play source audio"
          style={{
            width: 44,
            height: 44,
            borderRadius: "50%",
            background: "#0070C4",
            color: "white",
            border: "none",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 4px 14px rgba(0,112,196,0.3)",
            cursor: "default",
            flexShrink: 0
          }}
        >
          <Volume2 size={20} strokeWidth={2.5} />
        </button>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13.5, fontWeight: 800, color: "oklch(20% 0.09 245)" }}>
            {task.audioGenre} ({task.audioDurationSeconds}s)
          </div>
          <div style={{ display: "flex", gap: 3, alignItems: "center", marginTop: 4, height: 16 }}>
            {/* Visual audio wave-like representation */}
            {[2, 5, 8, 3, 6, 9, 4, 7, 2, 5, 8, 3, 6, 9, 4, 7, 2, 5, 8, 3, 6, 9].map((height, idx) => (
              <span
                key={idx}
                style={{
                  width: 2.5,
                  height: `${height * 1.5 + 4}px`,
                  borderRadius: 1,
                  background: "#0070C4",
                  opacity: 0.6 + (idx % 4) * 0.1
                }}
              />
            ))}
          </div>
        </div>
      </div>

      {!isDefault && (
        <ResultBanner
          total={1}
          correct={correctCount}
          label={answer?.isCorrect ? "Shadowing recording clear" : "Shadowing has pronunciation errors"}
        />
      )}

      {isDefault ? (
        <div className="tw-mic-stage" style={{ marginBottom: 0 }}>
          <div className="tw-mic-prompt">Ready to shadow</div>
          <div className="tw-mic-button-wrap">
            <button
              type="button"
              disabled
              aria-label="Preview recording button"
              title="Preview recording button"
              className="tw-mic-button"
              style={{ cursor: "default" }}
            >
              <Mic2 size={28} strokeWidth={2.5} />
            </button>
            <span className="tw-mic-ring" />
          </div>
          <div className="tw-mic-instruction">Listen and repeat (shadow) the Monologue</div>
          <div className="tw-mic-sub">Record up to {task.audioDurationSeconds} seconds.</div>
        </div>
      ) : (
        <div className="tw-compare-grid">
          <div className="tw-compare-card">
            <div className="tw-compare-label">
              <StatusDot ok={Boolean(answer?.isCorrect)} />
              Your Shadowing Transcript
            </div>
            <div className="tw-compare-body" style={{ fontStyle: "italic" }}>
              &ldquo;{answer?.transcript}&rdquo;
            </div>
            <div style={{ marginTop: 8, fontSize: 12, color: "var(--tw-ink-muted)", fontWeight: 700 }}>
              {answer?.durationSeconds}s recording
            </div>
          </div>
          <div className="tw-compare-card sample">
            <div className="tw-compare-label">
              <Volume2 size={12} />
              Correct Script
            </div>
            <div className="tw-compare-body">{task.textToShadow}</div>
          </div>
        </div>
      )}
    </TaskWidgetFrame>
  );
}
