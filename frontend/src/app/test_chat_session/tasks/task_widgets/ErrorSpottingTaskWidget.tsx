"use client";

import { Search } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { ErrorSpottingTask } from "../source";
import {
  FeedbackRow,
  ResultBanner,
  RuleCallout,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function ErrorSpottingTaskWidget({
  task,
  previewState,
}: {
  task: ErrorSpottingTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const selectedTokenIds = isDefault ? [] : task.answers[previewState];
  const errorTokenIds = task.sentences.map((sentence) => sentence.error.tokenId);
  const correctCount = isDefault
    ? 0
    : errorTokenIds.filter((tokenId) => selectedTokenIds.includes(tokenId)).length;

  return (
    <TaskWidgetFrame task={task} icon={<Search size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Past-tense check">{task.grammarRule}</RuleCallout>
      {!isDefault && (
        <ResultBanner
          total={task.sentences.length}
          correct={correctCount}
          label={`${correctCount} of ${task.sentences.length} errors found`}
        />
      )}

      <div className="tw-error-passage">
        <div className="tw-passage-label">{task.passageTitle}</div>
        {task.sentences.map((sentence) => (
          <div className="tw-error-sentence" key={sentence.sentenceId}>
            {sentence.tokens.map((token) => {
              const isSelected = selectedTokenIds.includes(token.tokenId);
              const isMissed = !isDefault && token.isError && !isSelected;
              const isWrong = !isDefault && isSelected && !token.isError;
              const className = [
                "tw-error-token",
                isDefault ? "" : isSelected && token.isError ? "found" : "",
                isMissed ? "missed" : "",
                isWrong ? "wrong" : "",
              ]
                .filter(Boolean)
                .join(" ");

              return (
                <button
                  key={token.tokenId}
                  type="button"
                  className={className}
                  disabled
                  style={{ cursor: "default" }}
                >
                  {token.text}
                </button>
              );
            })}
          </div>
        ))}
      </div>

      {!isDefault && (
        <div style={{ display: "grid", gap: 8 }}>
          {task.sentences.map((sentence, index) => {
            const found = selectedTokenIds.includes(sentence.error.tokenId);
            return (
              <FeedbackRow
                key={sentence.sentenceId}
                ok={found}
                title={`${index + 1}. ${sentence.error.incorrectPhrase} -> ${sentence.error.correction}`}
                body={`${sentence.error.explanation} ${sentence.error.rule}`}
              />
            );
          })}
        </div>
      )}
    </TaskWidgetFrame>
  );
}
