"use client";

import { FileText, Sparkles } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, WriteParagraphTask } from "../source";
import {
  LiveTextItems,
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function WriteParagraphTaskWidget({
  task,
  previewState,
  live,
}: {
  task: WriteParagraphTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  if (live) {
    return (
      <TaskWidgetFrame task={task} icon={<FileText size={18} strokeWidth={2.5} />}>
        <RuleCallout label="Grammar Rule">{task.grammarRule}</RuleCallout>
        <LiveTextItems
          items={[
            {
              itemId: task.itemId ?? "item_1",
              prompt: task.prompt,
              sampleAnswer: task.sampleAnswer,
              minHeight: 120,
              placeholder: "Write your paragraph here...",
              hints: task.answerHints,
            },
          ]}
          live={live}
          numbered={false}
          yourLabel="Your paragraph"
          sampleLabel="Model Answer"
        />
      </TaskWidgetFrame>
    );
  }
  const isDefault = previewState === "default";
  const answers = isDefault ? [] : task.answers[previewState];
  const correctCount = isDefault ? 0 : answers.filter((answer) => answer.isCorrect).length;
  const answer = answers[0];

  // Helper to count words
  const getWordCount = (text?: string) => {
    if (!text) return 0;
    return text.trim().split(/\s+/).filter(Boolean).length;
  };

  const currentText = isDefault ? "" : answer?.text || "";
  const wordCount = getWordCount(currentText);

  return (
    <TaskWidgetFrame task={task} icon={<FileText size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Grammar Rule">{task.grammarRule}</RuleCallout>

      {!isDefault && (
        <ResultBanner
          total={1}
          correct={correctCount}
          label={`${correctCount} of 1 paragraph accepted`}
        />
      )}

      <div className="tw-card" style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 14, fontWeight: 800, color: "var(--tw-navy)", marginBottom: 10 }}>
          {task.prompt}
        </div>

        {isDefault ? (
          <>
            <div
              className="tw-write-area"
              style={{
                color: "oklch(55% 0.07 240)",
                minHeight: 120,
                pointerEvents: "none",
                borderRadius: 12,
                border: "1.5px solid oklch(90% 0.02 240)",
                padding: "12px 14px",
                background: "oklch(99% 0.005 240)",
                fontSize: 14,
                lineHeight: 1.6,
              }}
            >
              Write your paragraph here...
            </div>
            <div className="tw-write-helper" style={{ display: "flex", justifyContent: "space-between", marginTop: 8, fontSize: 12, color: "oklch(45% 0.07 240)" }}>
              <span>Minimum {task.minimumWords} words required.</span>
              <span className="tw-count short" style={{ fontWeight: 700, color: "oklch(40% 0.16 25)" }}>
                0 words - need more
              </span>
            </div>
          </>
        ) : (
          <div className="tw-compare-grid" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div className="tw-compare-card" style={{ flex: 1, border: "1px solid oklch(90% 0.03 240)", borderRadius: 12, padding: 14, background: "white" }}>
              <div className="tw-compare-label" style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12.5, fontWeight: 800, color: "oklch(35% 0.07 240)", marginBottom: 8 }}>
                <StatusDot ok={Boolean(answer?.isCorrect)} />
                Your paragraph
              </div>
              <div 
                className="tw-compare-body" 
                style={{ 
                  fontSize: 14.5, 
                  lineHeight: 1.65, 
                  color: "oklch(20% 0.09 245)",
                  background: "oklch(99% 0.005 240)",
                  padding: 10,
                  borderRadius: 8
                }}
              >
                {answer?.text}
              </div>
              <div style={{ marginTop: 8, fontSize: 12, color: "oklch(45% 0.07 240)", fontWeight: 700 }}>
                {wordCount} words - meets requirements
              </div>
            </div>

            <div className="tw-compare-card sample" style={{ flex: 1, border: "1.5px dashed oklch(85% 0.05 155)", borderRadius: 12, padding: 14, background: "oklch(98% 0.02 155)" }}>
              <div className="tw-compare-label" style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12.5, fontWeight: 800, color: "oklch(35% 0.18 155)", marginBottom: 8 }}>
                <Sparkles size={13} style={{ color: "oklch(40% 0.18 155)" }} />
                Model Answer
              </div>
              <div className="tw-compare-body" style={{ fontSize: 14.5, lineHeight: 1.65, color: "oklch(20% 0.09 245)" }}>
                {task.sampleAnswer}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="tw-hints-block">
        <div className="tw-hints-label">Hints Checklist</div>
        <div className="tw-hints-list">
          {task.answerHints.map((hint) => (
            <div className="tw-hint-item" key={hint}>
              <span className="tw-hint-dot" />
              {hint}
            </div>
          ))}
        </div>
      </div>
    </TaskWidgetFrame>
  );
}
