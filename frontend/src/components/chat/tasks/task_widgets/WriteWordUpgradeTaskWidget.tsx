"use client";

import { FilePenLine, Sparkles } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, WriteWordUpgradeTask } from "../source";
import {
  LiveTextItems,
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

function UpgradeSourceBox({ sourceSentence, targetUpgradeWord }: { sourceSentence: string; targetUpgradeWord: string }) {
  return (
    <div
      style={{
        background: "linear-gradient(135deg, oklch(98% 0.01 245) 0%, oklch(96% 0.02 245) 100%)",
        border: "1.5px solid oklch(90% 0.02 245)",
        borderRadius: 14,
        padding: "16px 18px",
        marginBottom: 14,
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
    >
      <div style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: "0.06em", textTransform: "uppercase", color: "#0070C4" }}>
        Original (Weak vocabulary)
      </div>
      <div style={{ fontSize: 15.5, fontWeight: 700, color: "var(--tw-navy)", lineHeight: 1.5 }}>
        &ldquo;{sourceSentence}&rdquo;
      </div>
      {targetUpgradeWord && (
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 6, fontSize: 12, fontWeight: 700, color: "oklch(45% 0.07 240)" }}>
          <span>Upgrade to:</span>
          <span style={{ background: "oklch(91% 0.04 155)", color: "oklch(35% 0.16 155)", padding: "3px 9px", borderRadius: 999, fontWeight: 800, textTransform: "lowercase" }}>
            {targetUpgradeWord}
          </span>
        </div>
      )}
    </div>
  );
}

export function WriteWordUpgradeTaskWidget({
  task,
  previewState,
  live,
}: {
  task: WriteWordUpgradeTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  if (live) {
    return (
      <TaskWidgetFrame task={task} icon={<FilePenLine size={18} strokeWidth={2.5} />}>
        <RuleCallout label="Writing focus">{task.grammarRule}</RuleCallout>
        <LiveTextItems
          items={task.items.map((item) => ({
            itemId: item.itemId,
            sampleAnswer: item.sampleAnswer,
            minHeight: 82,
            placeholder: item.targetUpgradeWord
              ? `Rewrite using "${item.targetUpgradeWord}"...`
              : "Rewrite the sentence...",
            hints: item.watchHints,
            context: (
              <UpgradeSourceBox
                sourceSentence={item.sourceSentence}
                targetUpgradeWord={item.targetUpgradeWord}
              />
            ),
          }))}
          live={live}
          yourLabel="Your Upgraded Sentence"
          sampleLabel="Model Answer"
        />
      </TaskWidgetFrame>
    );
  }
  const isDefault = previewState === "default";
  const answers = isDefault ? [] : task.answers[previewState];
  const correctCount = isDefault ? 0 : answers.filter((answer) => answer.isCorrect).length;

  return (
    <TaskWidgetFrame task={task} icon={<FilePenLine size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Writing focus">{task.grammarRule}</RuleCallout>

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
          Target Upgrade Words
        </div>
        <div className="tw-target-chip-row">
          {task.items.map((item) => (
            <span key={item.itemId} className="tw-target-chip used">
              {item.targetUpgradeWord}
            </span>
          ))}
        </div>
      </div>

      {!isDefault && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} sentences upgraded successfully`}
        />
      )}

      {task.items.map((item, index) => {
        const answer = answers.find((row) => row.itemId === item.itemId);
        return (
          <div className="tw-card" key={item.itemId}>
            <div className="tw-q-number-row" style={{ marginBottom: 12 }}>
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">
                Sentence {index + 1} of {task.items.length}
              </div>
            </div>

            <div
              style={{
                background: "linear-gradient(135deg, oklch(98% 0.01 245) 0%, oklch(96% 0.02 245) 100%)",
                border: "1.5px solid oklch(90% 0.02 245)",
                borderRadius: 14,
                padding: "16px 18px",
                marginBottom: 14,
                display: "flex",
                flexDirection: "column",
                gap: 6,
              }}
            >
              <div
                style={{
                  fontSize: 10.5,
                  fontWeight: 800,
                  letterSpacing: "0.06em",
                  textTransform: "uppercase",
                  color: "#0070C4",
                }}
              >
                Original (Weak vocabulary)
              </div>
              <div
                style={{
                  fontSize: 15.5,
                  fontWeight: 700,
                  color: "var(--tw-navy)",
                  lineHeight: 1.5,
                }}
              >
                &ldquo;{item.sourceSentence}&rdquo;
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  marginTop: 6,
                  fontSize: 12,
                  fontWeight: 700,
                  color: "oklch(45% 0.07 240)",
                }}
              >
                <span>Upgrade to:</span>
                <span
                  style={{
                    background: "oklch(91% 0.04 155)",
                    color: "oklch(35% 0.16 155)",
                    padding: "3px 9px",
                    borderRadius: 999,
                    fontWeight: 800,
                    textTransform: "lowercase",
                  }}
                >
                  {item.targetUpgradeWord}
                </span>
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
                    borderRadius: 14,
                  }}
                >
                  Rewrite the sentence using &ldquo;{item.targetUpgradeWord}&rdquo;...
                </div>
                <div className="tw-write-helper">
                  <span>Watch hints: {item.watchHints.join(", ")}.</span>
                  <span className="tw-count short">0 words - need more</span>
                </div>
              </>
            ) : (
              <div className="tw-compare-grid">
                <div className="tw-compare-card">
                  <div className="tw-compare-label">
                    <StatusDot ok={Boolean(answer?.isCorrect)} />
                    Your Upgraded Sentence
                  </div>
                  <div className="tw-compare-body" style={{ fontStyle: "italic" }}>
                    &ldquo;{answer?.text}&rdquo;
                  </div>
                </div>
                <div className="tw-compare-card sample">
                  <div className="tw-compare-label">
                    <Sparkles size={12} fill="currentColor" />
                    Model Answer
                  </div>
                  <div className="tw-compare-body" style={{ fontWeight: 600 }}>
                    &ldquo;{item.sampleAnswer}&rdquo;
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </TaskWidgetFrame>
  );
}
