"use client";

import { FileText, MessageSquareText } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, ReadToneIdTask } from "../source";
import {
  liveMcqAnswerRecord,
  McqOptionList,
  mcqSubmission,
  ResultBanner,
  RuleCallout,
  SubmitButton,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function ReadToneIdTaskWidget({
  task,
  previewState,
  live,
}: {
  task: ReadToneIdTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  const interactive = Boolean(live) && !live!.submitted;
  const showResults = live ? live.submitted : previewState !== "default";
  const answers: Record<string, number> = live
    ? liveMcqAnswerRecord(live.answers)
    : previewState === "default"
      ? {}
      : task.answers[previewState];
  const allAnswered = task.items.every((item) => answers[item.itemId] !== undefined);
  const correctCount = showResults
    ? task.items.filter((item) => answers[item.itemId] === item.correctIndex).length
    : 0;

  const pick = (itemId: string, optionIndex: number) => {
    live?.setAnswers({ ...live.answers, [itemId]: optionIndex });
  };

  return (
    <TaskWidgetFrame task={task} icon={<MessageSquareText size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Tone focus">{task.grammarRule}</RuleCallout>

      <div className="tw-passage" style={{ marginBottom: 16 }}>
        <div className="tw-passage-label">{task.passageTitle}</div>
        Read each message and choose the tone that best matches the wording.
      </div>

      {showResults && !live?.submitted && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} tones identified`}
        />
      )}

      {task.items.map((item, index) => (
        <div className="tw-card" key={item.itemId}>
          <div className="tw-q-number-row" style={{ marginBottom: 12 }}>
            <div className="tw-q-number-badge">{index + 1}</div>
            <div className="tw-q-stem">{item.prompt}</div>
          </div>

          {item.message && (
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
                {item.sender && (
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
                )}
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
          )}

          <McqOptionList
            item={item}
            selected={answers[item.itemId]}
            interactive={interactive}
            showResults={showResults}
            onPick={(optionIndex) => pick(item.itemId, optionIndex)}
          />
        </div>
      ))}

      {interactive && (
        <SubmitButton
          disabled={!allAnswered}
          onClick={() => live!.onSubmit(mcqSubmission(task.items, answers))}
        />
      )}
    </TaskWidgetFrame>
  );
}
