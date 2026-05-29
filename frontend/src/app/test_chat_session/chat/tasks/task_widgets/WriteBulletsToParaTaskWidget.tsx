"use client";

import { FileText, Sparkles, ShoppingBag } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { WriteBulletsToParaTask } from "../source";
import {
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function WriteBulletsToParaTaskWidget({
  task,
  previewState,
}: {
  task: WriteBulletsToParaTask;
  previewState: SessionPreviewState;
}) {
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
      <RuleCallout label="Writing focus">{task.grammarRule}</RuleCallout>

      {/* Shopping List Bullets Section */}
      <div 
        style={{
          background: "linear-gradient(135deg, #FFFDF6 0%, #FFF9E6 100%)",
          border: "1.5px solid #F3E5C8",
          borderRadius: 18,
          padding: "18px 20px",
          marginBottom: 18,
          boxShadow: "0 6px 20px rgba(220,180,100,0.12)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Subtle decorative lined paper effect */}
        <div
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            left: 36,
            width: 2,
            background: "rgba(220,100,100,0.15)",
          }}
        />

        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12, position: "relative", zIndex: 1 }}>
          <ShoppingBag size={18} style={{ color: "oklch(58% 0.16 60)" }} />
          <div style={{ fontSize: 13, fontWeight: 800, color: "oklch(42% 0.12 60)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Your Shopping List
          </div>
        </div>

        <ul style={{ margin: 0, paddingLeft: 24, listStyle: "none", display: "flex", flexDirection: "column", gap: 10, position: "relative", zIndex: 1 }}>
          {task.bullets.map((bullet) => (
            <li 
              key={bullet} 
              style={{ 
                display: "flex", 
                alignItems: "center", 
                gap: 12, 
                fontSize: 14.5, 
                fontWeight: 600, 
                color: "oklch(22% 0.06 60)",
                fontFamily: "inherit"
              }}
            >
              <div 
                style={{ 
                  width: 18, 
                  height: 18, 
                  borderRadius: 5, 
                  border: "1.8px solid oklch(58% 0.16 60)", 
                  background: "white",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0
                }}
              >
                <div style={{ width: 8, height: 8, borderRadius: 2, background: "oklch(58% 0.16 60)", opacity: 0.8 }} />
              </div>
              <span>{bullet}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Target Words Section */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 12, fontWeight: 800, color: "oklch(45% 0.07 240)", marginBottom: 8, textTransform: "uppercase" }}>
          Target words to use
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
          label={`${correctCount} of 1 paragraph accepted`}
        />
      )}

      {/* Write Input Area */}
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
              Write your message here...
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
                Your message
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

      {/* Hints Checklist */}
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
