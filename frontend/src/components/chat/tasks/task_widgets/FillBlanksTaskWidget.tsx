"use client";

import { FileText } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { FillBlanksTask } from "../source";
import {
  FeedbackRow,
  normalizeAnswer,
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function FillBlanksTaskWidget({
  task,
  previewState,
}: {
  task: FillBlanksTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? {} : task.answers[previewState];
  const correctCount = isDefault
    ? 0
    : task.items.filter(
        (item) => normalizeAnswer(answers[item.itemId]) === normalizeAnswer(item.correctAnswer),
      ).length;
  const parts = task.passage.split("___");

  return (
    <TaskWidgetFrame task={task} icon={<FileText size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Grammar rule">{task.grammarRule}</RuleCallout>
      {!isDefault && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} blanks correct`}
        />
      )}
      <div className="tw-passage">
        <div className="tw-passage-label">{task.passageTitle}</div>
        {parts.map((part, index) => {
          const item = task.items[index];
          return (
            <span key={`part-${index}`}>
              {part}
              {item ? (
                <InlineBlank
                  item={item}
                  value={answers[item.itemId]}
                  index={index}
                  isDefault={isDefault}
                />
              ) : null}
            </span>
          );
        })}
      </div>
      {!isDefault && (
        <div style={{ display: "grid", gap: 8 }}>
          {task.items.map((item, index) => {
            const value = answers[item.itemId];
            const isCorrect = normalizeAnswer(value) === normalizeAnswer(item.correctAnswer);
            return (
              <FeedbackRow
                key={item.itemId}
                ok={isCorrect}
                title={`${index + 1}. ${item.sentenceWithBlank}`}
                body={
                  isCorrect
                    ? item.explanation
                    : `${item.explanation} Correct answer: ${item.correctAnswer}.`
                }
              />
            );
          })}
        </div>
      )}
    </TaskWidgetFrame>
  );
}

function InlineBlank({
  item,
  value,
  index,
  isDefault,
}: {
  item: FillBlanksTask["items"][number];
  value?: string;
  index: number;
  isDefault: boolean;
}) {
  if (isDefault) {
    return (
      <span
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          margin: "0 5px",
          whiteSpace: "nowrap",
          verticalAlign: "baseline",
        }}
      >
        <span
          aria-hidden
          style={{
            width: 22,
            height: 22,
            borderRadius: "50%",
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            background: "var(--tw-primary)",
            color: "white",
            fontSize: 11,
            fontWeight: 800,
            lineHeight: 1,
            flexShrink: 0,
          }}
        >
          {index + 1}
        </span>
        <span
          className="tw-blank-input"
          style={{
            width: "clamp(88px, 18vw, 150px)",
            color: "oklch(55% 0.07 240)",
          }}
        >
          answer
        </span>
        <span style={{ fontSize: 12, fontWeight: 600, color: "var(--tw-primary)", fontStyle: "italic" }}>
          ({item.baseVerb})
        </span>
      </span>
    );
  }

  const isCorrect = normalizeAnswer(value) === normalizeAnswer(item.correctAnswer);

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 5,
        margin: "0 5px",
        whiteSpace: "nowrap",
        verticalAlign: "baseline",
      }}
    >
      <StatusDot ok={isCorrect} />
      <span
        className={isCorrect ? "tw-blank-input ok" : "tw-blank-input no"}
        style={{ minWidth: 74, width: "auto", fontStyle: "normal" }}
      >
        {value}
      </span>
      {!isCorrect && <span className="tw-blank-fix">{item.correctAnswer}</span>}
    </span>
  );
}
