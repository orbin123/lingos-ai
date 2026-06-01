"use client";

import { Search } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { ErrorSpottingTask, LiveTaskController } from "../source";
import {
  FeedbackRow,
  ResultBanner,
  RuleCallout,
  SubmitButton,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

function LiveErrorSpotting({ task, live }: { task: ErrorSpottingTask; live: LiveTaskController }) {
  const interactive = !live.submitted;
  const showResults = live.submitted;
  const selectedTokenIds: string[] = Array.isArray(live.answers.selected_token_ids)
    ? (live.answers.selected_token_ids as unknown[]).map(String)
    : [];

  const toggle = (tokenId: string) => {
    if (!interactive) return;
    const next = selectedTokenIds.includes(tokenId)
      ? selectedTokenIds.filter((id) => id !== tokenId)
      : [...selectedTokenIds, tokenId];
    live.setAnswers({ ...live.answers, selected_token_ids: next });
  };

  return (
    <TaskWidgetFrame task={task} icon={<Search size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Past-tense check">{task.grammarRule}</RuleCallout>
      <div className="tw-write-helper" style={{ marginBottom: 8 }}>
        Tap each word that contains a mistake, then submit.
      </div>

      <div className="tw-error-passage">
        <div className="tw-passage-label">{task.passageTitle}</div>
        {task.sentences.map((sentence) => (
          <div className="tw-error-sentence" key={sentence.sentenceId}>
            {sentence.tokens.map((token) => {
              const isSelected = selectedTokenIds.includes(token.tokenId);
              const isMissed = showResults && token.isError && !isSelected;
              const isWrong = showResults && isSelected && !token.isError;
              const className = [
                "tw-error-token",
                showResults ? (isSelected && token.isError ? "found" : "") : isSelected ? "found" : "",
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
                  disabled={!interactive}
                  onClick={() => toggle(token.tokenId)}
                  style={{ cursor: interactive ? "pointer" : "default" }}
                >
                  {token.text}
                </button>
              );
            })}
          </div>
        ))}
      </div>

      {showResults && (
        <div style={{ display: "grid", gap: 8, marginTop: 12 }}>
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

      {interactive && (
        <SubmitButton
          disabled={selectedTokenIds.length === 0}
          onClick={() => live.onSubmit({ selected_token_ids: selectedTokenIds })}
        />
      )}
    </TaskWidgetFrame>
  );
}

export function ErrorSpottingTaskWidget({
  task,
  previewState,
  live,
}: {
  task: ErrorSpottingTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  if (live) {
    return <LiveErrorSpotting task={task} live={live} />;
  }
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
