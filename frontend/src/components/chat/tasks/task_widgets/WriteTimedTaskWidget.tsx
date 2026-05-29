"use client";

import { FileText, Sparkles, Timer } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { WriteTimedTask } from "../source";
import {
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function WriteTimedTaskWidget({
  task,
  previewState,
}: {
  task: WriteTimedTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? [] : task.answers[previewState];
  const correctCount = isDefault ? 0 : answers.filter((answer) => answer.isCorrect).length;
  const answer = answers[0];

  const getWordCount = (text?: string) => {
    if (!text) return 0;
    return text.trim().split(/\s+/).filter(Boolean).length;
  };

  const currentText = isDefault ? "" : answer?.text || "";
  const wordCount = getWordCount(currentText);

  return (
    <TaskWidgetFrame task={task} icon={<FileText size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Writing pressure">{task.grammarRule}</RuleCallout>

      <div style={{ marginBottom: 16 }}>
        <div
          style={{
            fontSize: 11,
            fontWeight: 800,
            color: "oklch(45% 0.07 240)",
            marginBottom: 8,
            textTransform: "uppercase",
            letterSpacing: "0.06em",
          }}
        >
          Target writing cues
        </div>
        <div className="tw-target-chip-row">
          {task.targetWords.map((word) => {
            const isUsed = !isDefault && currentText.toLowerCase().includes(word.toLowerCase());
            return (
              <span
                className={`tw-target-chip ${isUsed ? "used" : ""}`}
                key={word}
                style={{
                  background: isUsed ? "oklch(93% 0.04 155)" : "oklch(96% 0.015 240)",
                  color: isUsed ? "oklch(42% 0.16 155)" : "oklch(35% 0.05 240)",
                  border: isUsed ? "1px solid oklch(85% 0.06 155)" : "1px solid oklch(90% 0.02 240)",
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      </div>

      {!isDefault && (
        <ResultBanner
          total={1}
          correct={correctCount}
          label={
            answer?.isCorrect
              ? "Opinion expressed clearly with correct cues"
              : "Completed timed write but missed key cues"
          }
        />
      )}

      {isDefault ? (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            padding: "24px 18px",
            background: "linear-gradient(135deg, oklch(99% 0.005 240) 0%, oklch(96.5% 0.02 245) 100%)",
            border: "1.5px solid oklch(90% 0.02 240)",
            borderRadius: 18,
            textAlign: "center",
            boxShadow: "0 4px 16px rgba(80,110,180,0.03)",
          }}
        >
          <div
            style={{
              fontSize: 11,
              fontWeight: 800,
              color: "#0070C4",
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              marginBottom: 14,
            }}
          >
            Opinion Timed Prompt
          </div>
          <div
            style={{
              maxWidth: 520,
              borderRadius: 14,
              background: "white",
              border: "1px solid oklch(91% 0.015 240)",
              padding: "16px 20px",
              color: "var(--tw-navy)",
              fontSize: 15.5,
              lineHeight: 1.6,
              fontWeight: 700,
              boxShadow: "0 2px 10px rgba(0,0,0,0.02)",
              marginBottom: 20,
            }}
          >
            &ldquo;{task.prompt}&rdquo;
          </div>

          <div
            style={{
              display: "flex",
              width: "100%",
              flexDirection: "column",
              gap: 8,
              marginBottom: 18,
            }}
          >
            <textarea
              disabled
              placeholder="Start typing your opinion under 3-minute timed pressure..."
              style={{
                width: "100%",
                height: 110,
                borderRadius: 12,
                border: "1.5px solid oklch(88% 0.02 240)",
                background: "white",
                padding: 14,
                fontSize: 14.5,
                color: "oklch(60% 0.02 240)",
                resize: "none",
              }}
            />
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                fontSize: 12.5,
                color: "oklch(45% 0.05 240)",
              }}
            >
              <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
                <Timer size={14} style={{ color: "#0070C4" }} />
                <span>3:00 minutes remaining</span>
              </span>
              <span style={{ fontWeight: 700 }}>0 words</span>
            </div>
          </div>

          <div
            style={{
              fontSize: 13.5,
              color: "var(--tw-ink-muted)",
              lineHeight: 1.45,
            }}
          >
            You will have {task.writingDurationSeconds / 60} minutes to formulate and type your response.
          </div>
        </div>
      ) : (
        <div className="tw-card" style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 14, fontWeight: 800, color: "var(--tw-navy)", marginBottom: 14 }}>
            {task.prompt}
          </div>

          <div className="tw-compare-grid" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div
              className="tw-compare-card"
              style={{
                flex: 1,
                border: "1px solid oklch(90% 0.03 240)",
                borderRadius: 12,
                padding: 14,
                background: "white",
              }}
            >
              <div
                className="tw-compare-label"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  fontSize: 12.5,
                  fontWeight: 800,
                  color: "oklch(35% 0.07 240)",
                  marginBottom: 8,
                }}
              >
                <StatusDot ok={Boolean(answer?.isCorrect)} />
                Your timed response
              </div>
              <div
                className="tw-compare-body"
                style={{
                  fontSize: 14.5,
                  lineHeight: 1.65,
                  color: "oklch(20% 0.09 245)",
                  background: "oklch(99% 0.005 240)",
                  padding: 12,
                  borderRadius: 8,
                }}
              >
                {answer?.text}
              </div>
              <div
                style={{
                  marginTop: 10,
                  fontSize: 12,
                  color: "var(--tw-ink-muted)",
                  fontWeight: 700,
                }}
              >
                {wordCount} words • 165s write • timed limit: {task.writingDurationSeconds}s
              </div>
            </div>

            <div
              className="tw-compare-card sample"
              style={{
                flex: 1,
                border: "1.5px dashed oklch(85% 0.05 155)",
                borderRadius: 12,
                padding: 14,
                background: "oklch(98% 0.02 155)",
              }}
            >
              <div
                className="tw-compare-label"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  fontSize: 12.5,
                  fontWeight: 800,
                  color: "oklch(35% 0.18 155)",
                  marginBottom: 8,
                }}
              >
                <Sparkles size={13} style={{ color: "oklch(40% 0.18 155)" }} />
                Model Opinion
              </div>
              <div className="tw-compare-body" style={{ fontSize: 14.5, lineHeight: 1.65, color: "oklch(20% 0.09 245)" }}>
                {task.sampleAnswer}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="tw-hints-block" style={{ marginTop: 16 }}>
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
