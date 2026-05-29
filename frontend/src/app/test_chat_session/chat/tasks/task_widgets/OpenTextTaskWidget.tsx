"use client";

import { FileText, Sparkles } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { OpenTextTask } from "../source";
import {
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function OpenTextTaskWidget({
  task,
  previewState,
}: {
  task: OpenTextTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? [] : task.answers[previewState];
  const correctCount = isDefault ? 0 : answers.filter((answer) => answer.isCorrect).length;

  return (
    <TaskWidgetFrame task={task} icon={<FileText size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Rule">{task.grammarRule}</RuleCallout>
      <div className="tw-target-chip-row" style={{ marginBottom: 14 }}>
        {task.targetWords.map((word) => (
          <span className="tw-target-chip used" key={word}>
            {word}
          </span>
        ))}
      </div>
      {!isDefault && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} sentences accepted`}
        />
      )}
      {task.items.map((item, index) => {
        const answer = answers.find((row) => row.itemId === item.itemId);
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
                    minHeight: 92,
                    pointerEvents: "none",
                  }}
                >
                  Write your answer here...
                </div>
                <div className="tw-write-helper">
                  <span>Minimum 5 characters per prompt.</span>
                  <span className="tw-count short">0 words - need more</span>
                </div>
              </>
            ) : (
              <div className="tw-compare-grid">
                <div className="tw-compare-card">
                  <div className="tw-compare-label">
                    <StatusDot ok={Boolean(answer?.isCorrect)} />
                    Your answer
                  </div>
                  <div className="tw-compare-body">{answer?.text}</div>
                </div>
                <div className="tw-compare-card sample">
                  <div className="tw-compare-label">
                    <Sparkles size={12} />
                    Sample answer
                  </div>
                  <div className="tw-compare-body">{item.sampleAnswer}</div>
                </div>
              </div>
            )}
            <div className="tw-hints-block">
              <div className="tw-hints-label">Hints</div>
              <div className="tw-hints-list">
                {item.answerHints.map((hint) => (
                  <div className="tw-hint-item" key={hint}>
                    <span className="tw-hint-dot" />
                    {hint}
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      })}
    </TaskWidgetFrame>
  );
}
