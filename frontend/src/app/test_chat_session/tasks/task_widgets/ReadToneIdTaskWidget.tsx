"use client";

import { Check, FileText, MessageSquareText, X } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { ReadToneIdTask } from "../source";
import { ResultBanner, RuleCallout, TaskWidgetFrame } from "./TaskWidgetFrame";

export function ReadToneIdTaskWidget({
  task,
  previewState,
}: {
  task: ReadToneIdTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? {} : task.answers[previewState];
  const correctCount = isDefault
    ? 0
    : task.items.filter((item) => answers[item.itemId] === item.correctIndex).length;

  return (
    <TaskWidgetFrame task={task} icon={<MessageSquareText size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Tone focus">{task.grammarRule}</RuleCallout>

      <div className="tw-passage" style={{ marginBottom: 16 }}>
        <div className="tw-passage-label">{task.passageTitle}</div>
        Read each message and choose the tone that best matches the wording.
      </div>

      {!isDefault && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} tones identified`}
        />
      )}

      {task.items.map((item, index) => {
        const selected = answers[item.itemId];

        return (
          <div className="tw-card" key={item.itemId}>
            <div className="tw-q-number-row" style={{ marginBottom: 12 }}>
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">{item.prompt}</div>
            </div>

            <div
              style={{
                border: "1.5px solid oklch(89% 0.03 245)",
                borderRadius: 16,
                background: "linear-gradient(135deg, white, oklch(97% 0.02 245))",
                padding: 14,
                marginBottom: 14,
                display: "flex",
                gap: 12,
                alignItems: "flex-start",
              }}
            >
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 10,
                  background: "oklch(52% 0.18 240)",
                  color: "white",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                <FileText size={15} strokeWidth={2.5} />
              </div>
              <div style={{ minWidth: 0 }}>
                <div
                  style={{
                    fontSize: 11,
                    fontWeight: 800,
                    color: "oklch(45% 0.07 240)",
                    textTransform: "uppercase",
                    marginBottom: 5,
                  }}
                >
                  {item.sender}
                </div>
                <div
                  style={{
                    fontSize: 15,
                    lineHeight: 1.6,
                    color: "var(--tw-navy)",
                    fontWeight: 650,
                  }}
                >
                  &ldquo;{item.message}&rdquo;
                </div>
              </div>
            </div>

            <div className="tw-opt-list">
              {item.options.map((option, optionIndex) => {
                const isCorrect = !isDefault && optionIndex === item.correctIndex;
                const isWrongPick = !isDefault && optionIndex === selected && !isCorrect;
                const cls = `tw-opt-row${isCorrect ? " correct" : ""}${isWrongPick ? " wrong" : ""}`;

                return (
                  <div className={cls} key={option} style={{ cursor: "default" }}>
                    <span className="tw-opt-key">{optionIndex + 1}</span>
                    <span style={{ flex: 1 }}>{option}</span>
                    {isCorrect && <Check size={14} strokeWidth={2.8} />}
                    {isWrongPick && <X size={14} strokeWidth={2.8} />}
                  </div>
                );
              })}
            </div>

            {!isDefault && (
              <div className="tw-fb-explain" style={{ marginTop: 12, paddingTop: 10 }}>
                <strong>{selected === item.correctIndex ? "Correct." : "Why it is wrong."}</strong>{" "}
                {item.explanation}
              </div>
            )}
          </div>
        );
      })}
    </TaskWidgetFrame>
  );
}
