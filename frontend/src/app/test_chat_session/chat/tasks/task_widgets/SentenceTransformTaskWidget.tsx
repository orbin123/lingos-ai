"use client";

import { FilePenLine, Sparkles } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { SentenceTransformTask } from "../source";
import {
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function SentenceTransformTaskWidget({
  task,
  previewState,
}: {
  task: SentenceTransformTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? [] : task.answers[previewState];
  const correctCount = isDefault ? 0 : answers.filter((answer) => answer.isCorrect).length;

  return (
    <TaskWidgetFrame task={task} icon={<FilePenLine size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Writing focus">{task.grammarRule}</RuleCallout>
      {!isDefault && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} sentences transformed`}
        />
      )}

      {task.items.map((item, index) => {
        const answer = answers.find((row) => row.itemId === item.itemId);
        return (
          <div className="tw-card" key={item.itemId}>
            <div className="tw-q-number-row" style={{ marginBottom: 12 }}>
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">Sentence {index + 1} of {task.items.length}</div>
            </div>

            <div
              style={{
                background: "oklch(96% 0.025 245)",
                border: "1.5px solid oklch(88% 0.035 245)",
                borderRadius: 12,
                padding: 16,
                marginBottom: 14,
              }}
            >
              <div
                style={{
                  fontSize: 11,
                  fontWeight: 800,
                  letterSpacing: "0.06em",
                  textTransform: "uppercase",
                  color: "var(--tw-primary)",
                  marginBottom: 8,
                }}
              >
                Rewrite this
              </div>
              <div
                style={{
                  fontSize: 16,
                  fontWeight: 700,
                  color: "var(--tw-navy)",
                  lineHeight: 1.5,
                }}
              >
                &ldquo;{item.sourceSentence}&rdquo;
              </div>
            </div>

            {isDefault ? (
              <>
                <div
                  className="tw-write-area"
                  style={{
                    color: "oklch(55% 0.07 240)",
                    minHeight: 82,
                    pointerEvents: "none",
                  }}
                >
                  Rewrite the sentence here...
                </div>
                <div className="tw-write-helper">
                  <span>Watch: {item.watchHints.join(", ")}.</span>
                  <span className="tw-count short">0 words - need more</span>
                </div>
              </>
            ) : (
              <div className="tw-compare-grid">
                <div className="tw-compare-card">
                  <div className="tw-compare-label">
                    <StatusDot ok={Boolean(answer?.isCorrect)} />
                    Your sentence
                  </div>
                  <div className="tw-compare-body">{answer?.text}</div>
                </div>
                <div className="tw-compare-card sample">
                  <div className="tw-compare-label">
                    <Sparkles size={12} />
                    Model sentence
                  </div>
                  <div className="tw-compare-body">{item.sampleAnswer}</div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </TaskWidgetFrame>
  );
}
