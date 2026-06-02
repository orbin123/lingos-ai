"use client";

import { FileText, Play, Volume2 } from "lucide-react";
import { useState } from "react";
import type { SessionPreviewState } from "../../teaching/source";
import type { ListenDictationTask, LiveTaskController } from "../source";
import {
  FeedbackRow,
  ListeningAudioCard,
  LiveTextItems,
  normalizeAnswer,
  ResultBanner,
  roundIconButton,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

function LiveDictation({ task, live }: { task: ListenDictationTask; live: LiveTaskController }) {
  const [audioComplete, setAudioComplete] = useState(false);
  const unlocked = live.submitted || audioComplete;
  return (
    <TaskWidgetFrame task={task} icon={<Volume2 size={18} strokeWidth={2.5} />}>
      <ListeningAudioCard
        title={task.audioGenre}
        script={task.audioScript}
        audioUrl={task.audioUrl}
        durationSeconds={task.audioDurationSeconds}
        completed={unlocked}
        hint="Listen once to unlock the dictation below."
        onComplete={() => setAudioComplete(true)}
      />
      {unlocked && task.grammarRule && <RuleCallout label="Listening focus">{task.grammarRule}</RuleCallout>}
      {unlocked && (
        <LiveTextItems
          items={task.items.map((item) => ({
            itemId: item.itemId,
            prompt: item.prompt,
            sampleAnswer: item.correctAnswer,
            minHeight: 60,
            placeholder: "Type the exact sentence you heard...",
          }))}
          live={live}
          yourLabel="Your sentence"
          sampleLabel="Exact sentence"
        />
      )}
    </TaskWidgetFrame>
  );
}

export function ListenDictationTaskWidget({
  task,
  previewState,
  live,
}: {
  task: ListenDictationTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  if (live) {
    return <LiveDictation task={task} live={live} />;
  }
  const isDefault = previewState === "default";
  const answers = isDefault ? {} : task.answers[previewState];
  const correctCount = isDefault
    ? 0
    : task.items.filter(
        (item) => normalizeAnswer(answers[item.itemId]) === normalizeAnswer(item.correctAnswer),
      ).length;

  const playScript = () => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(task.audioScript);
    utterance.rate = 0.85;
    window.speechSynthesis.speak(utterance);
  };

  return (
    <TaskWidgetFrame task={task} icon={<Volume2 size={18} strokeWidth={2.5} />}>
      <div className="tw-card" style={{ background: "oklch(97% 0.02 245)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button
            type="button"
            onClick={playScript}
            title="Play mock audio"
            aria-label="Play mock audio"
            style={roundIconButton}
          >
            <Play size={18} fill="currentColor" />
          </button>
          <div style={{ minWidth: 0 }}>
            <div className="tw-rule-label">{task.audioGenre}</div>
            <div style={{ fontSize: 13.5, lineHeight: 1.55, color: "var(--tw-navy)" }}>
              {task.audioScript}
            </div>
          </div>
        </div>
      </div>

      <RuleCallout label="Listening focus">{task.grammarRule}</RuleCallout>

      {!isDefault && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} sentences exact`}
        />
      )}

      {task.items.map((item, index) => {
        const value = answers[item.itemId];
        const isCorrect = normalizeAnswer(value) === normalizeAnswer(item.correctAnswer);

        return (
          <div className="tw-card" key={item.itemId}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">{item.prompt}</div>
            </div>
            {isDefault ? (
              <>
                <div
                  className="tw-write-area"
                  style={{
                    color: "oklch(55% 0.07 240)",
                    minHeight: 74,
                    pointerEvents: "none",
                  }}
                >
                  Type the exact sentence here...
                </div>
                <div className="tw-write-helper">
                  <span>Listen for the helper verb and the -ing action.</span>
                  <span className="tw-count short">0 words - need more</span>
                </div>
              </>
            ) : (
              <div className="tw-compare-grid">
                <div className="tw-compare-card">
                  <div className="tw-compare-label">
                    <StatusDot ok={isCorrect} />
                    Your sentence
                  </div>
                  <div className="tw-compare-body">{value}</div>
                </div>
                <div className="tw-compare-card sample">
                  <div className="tw-compare-label">
                    <FileText size={12} />
                    Exact sentence
                  </div>
                  <div className="tw-compare-body">{item.correctAnswer}</div>
                </div>
              </div>
            )}
          </div>
        );
      })}

      {!isDefault && (
        <div style={{ display: "grid", gap: 8 }}>
          {task.items.map((item, index) => {
            const value = answers[item.itemId];
            const isCorrect = normalizeAnswer(value) === normalizeAnswer(item.correctAnswer);
            return (
              <FeedbackRow
                key={item.itemId}
                ok={isCorrect}
                title={`${index + 1}. ${item.prompt}`}
                body={
                  isCorrect
                    ? item.explanation
                    : `${item.explanation} Exact sentence: ${item.correctAnswer}`
                }
              />
            );
          })}
        </div>
      )}
    </TaskWidgetFrame>
  );
}
