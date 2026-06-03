"use client";

import { FileText } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, ReadContextMcqTask } from "../source";
import {
  liveMcqAnswerRecord,
  McqOptionList,
  mcqSubmission,
  ResultBanner,
  RuleCallout,
  SubmitButton,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";
import { PassageBlock } from "./PassageBlock";

export function ReadContextMcqTaskWidget({
  task,
  previewState,
  live,
}: {
  task: ReadContextMcqTask;
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
    <TaskWidgetFrame task={task} icon={<FileText size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Reading focus">{task.grammarRule}</RuleCallout>
      <PassageBlock title={task.passageTitle}>{task.passage}</PassageBlock>

      {showResults && !live?.submitted && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} questions correct`}
        />
      )}

      {task.items.map((item, index) => (
        <div className="tw-card" key={item.itemId}>
          <div className="tw-q-number-row">
            <div className="tw-q-number-badge">{index + 1}</div>
            <div className="tw-q-stem">{item.prompt}</div>
          </div>
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
