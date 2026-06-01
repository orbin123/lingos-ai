"use client";

import { Mic2, Volume2 } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, ReadAloudTask } from "../source";
import { LivePronunciationRecorder } from "./LivePronunciationRecorder";
import {
  ResultBanner,
  RuleCallout,
  StatusDot,
  TargetWordsRow,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function ReadAloudTaskWidget({
  task,
  previewState,
  live,
}: {
  task: ReadAloudTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  if (live) {
    return (
      <TaskWidgetFrame task={task} icon={<Mic2 size={18} strokeWidth={2.5} />}>
        <RuleCallout label="Read-aloud focus">{task.grammarRule}</RuleCallout>
        <TargetWordsRow words={task.targetWords} label="Target words" />
        <div className="tw-passage">
          <div className="tw-passage-label">Text to read aloud</div>
          {task.textToReadAloud}
        </div>
        <LivePronunciationRecorder
          live={live}
          referenceText={task.textToReadAloud}
          durationSeconds={task.speakingDurationSeconds}
        />
      </TaskWidgetFrame>
    );
  }
  const isDefault = previewState === "default";
  const answer = isDefault ? null : task.answers[previewState][0];
  const correctCount = answer?.isCorrect ? 1 : 0;

  return (
    <TaskWidgetFrame task={task} icon={<Mic2 size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Read-aloud focus">{task.grammarRule}</RuleCallout>
      <div className="tw-target-chip-row" style={{ marginBottom: 14 }}>
        {task.targetWords.map((word) => (
          <span className="tw-target-chip used" key={word}>
            {word}
          </span>
        ))}
      </div>

      <div className="tw-passage">
        <div className="tw-passage-label">Text to read aloud</div>
        {task.textToReadAloud}
      </div>

      {!isDefault && (
        <ResultBanner
          total={1}
          correct={correctCount}
          label={answer?.isCorrect ? "Read-aloud recording clear" : "Read-aloud needs one correction"}
        />
      )}

      {isDefault ? (
        <div className="tw-mic-stage" style={{ marginBottom: 0 }}>
          <div className="tw-mic-prompt">Ready to record</div>
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
          <div className="tw-mic-instruction">Read the passage aloud</div>
          <div className="tw-mic-sub">Record up to {task.speakingDurationSeconds} seconds.</div>
        </div>
      ) : (
        <div className="tw-compare-grid">
          <div className="tw-compare-card">
            <div className="tw-compare-label">
              <StatusDot ok={Boolean(answer?.isCorrect)} />
              Transcript
            </div>
            <div className="tw-compare-body">{answer?.transcript}</div>
            <div style={{ marginTop: 8, fontSize: 12, color: "var(--tw-ink-muted)", fontWeight: 700 }}>
              {answer?.durationSeconds}s recording
            </div>
          </div>
          <div className="tw-compare-card sample">
            <div className="tw-compare-label">
              <Volume2 size={12} />
              Passage
            </div>
            <div className="tw-compare-body">{task.textToReadAloud}</div>
          </div>
        </div>
      )}
    </TaskWidgetFrame>
  );
}
