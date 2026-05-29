"use client";

import { Check, FileText, X } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { ReadCompMcqTask } from "../source";
import { ResultBanner, RuleCallout, TaskWidgetFrame } from "./TaskWidgetFrame";

export function ReadCompMcqTaskWidget({
  task,
  previewState,
}: {
  task: ReadCompMcqTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? {} : task.answers[previewState];
  const correctCount = isDefault
    ? 0
    : task.items.filter((item) => answers[item.itemId] === item.correctIndex).length;

  return (
    <TaskWidgetFrame task={task} icon={<FileText size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Reading focus">{task.grammarRule}</RuleCallout>
      <div className="tw-passage">
        <div className="tw-passage-label">{task.passageTitle}</div>
        {task.passage}
      </div>

      {!isDefault && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} questions correct`}
        />
      )}

      {task.items.map((item, index) => {
        const selected = answers[item.itemId];
        return (
          <div className="tw-card" key={item.itemId}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">{item.prompt}</div>
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
