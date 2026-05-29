"use client";

import { Volume2 } from "lucide-react";
import { useState } from "react";
import type { SessionPreviewState } from "../../teaching/source";
import type { ListenClozeTask, LiveTaskController } from "../source";
import {
  FeedbackRow,
  ListeningAudioCard,
  liveStringRecord,
  normalizeAnswer,
  ResultBanner,
  RuleCallout,
  StatusDot,
  SubmitButton,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function ListenClozeTaskWidget({
  task,
  previewState,
  live,
}: {
  task: ListenClozeTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  const [audioComplete, setAudioComplete] = useState(false);
  const unlocked = live ? live.submitted || audioComplete : previewState !== "default" || audioComplete;
  const interactive = Boolean(live) && !live!.submitted && unlocked;
  const showResults = live ? live.submitted : previewState !== "default";
  const answers: Record<string, string> = live
    ? liveStringRecord(live.answers)
    : previewState === "default"
      ? {}
      : task.answers[previewState];
  const correctCount = showResults
    ? task.items.filter(
        (item) => normalizeAnswer(answers[item.itemId]) === normalizeAnswer(item.correctAnswer),
      ).length
    : 0;
  const passageBlankCount = (task.passage.match(/___/g) ?? []).length;
  const passageAligned =
    task.passage.trim().length > 0 && passageBlankCount === task.items.length;
  const parts = task.passage.split("___");

  const setAnswer = (itemId: string, value: string) => {
    live?.setAnswers({ ...live.answers, [itemId]: value });
  };

  return (
    <TaskWidgetFrame task={task} icon={<Volume2 size={18} strokeWidth={2.5} />}>
      <ListeningAudioCard
        title={task.audioGenre}
        script={task.audioScript}
        audioUrl={task.audioUrl}
        durationSeconds={task.audioDurationSeconds}
        completed={unlocked}
        hint="Listen once to unlock the fill-in-the-blank task below."
        onComplete={() => setAudioComplete(true)}
      />
      {unlocked && task.grammarRule && <RuleCallout label="Listening focus">{task.grammarRule}</RuleCallout>}
      {unlocked && task.targetWords.length > 0 && (
        <div className="tw-target-chip-row" style={{ marginBottom: 14 }}>
          {task.targetWords.map((word) => (
            <span className="tw-target-chip used" key={word}>
              {word}
            </span>
          ))}
        </div>
      )}
      {showResults && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} blanks correct`}
        />
      )}
      {unlocked && (
        <div className="tw-passage">
          <div className="tw-passage-label">{task.passageTitle}</div>
          {passageAligned
            ? parts.map((part, index) => {
                const item = task.items[index];
                return (
                  <span key={`listen-part-${index}`}>
                    {part}
                    {item ? (
                      <InlineListenBlank
                        item={item}
                        value={answers[item.itemId]}
                        index={index}
                        interactive={interactive}
                        showResult={showResults}
                        onChange={(value) => setAnswer(item.itemId, value)}
                      />
                    ) : null}
                  </span>
                );
              })
            : task.items.map((item, index) => {
                const segments = item.sentenceWithBlank.includes("___")
                  ? item.sentenceWithBlank.split("___")
                  : [`${item.sentenceWithBlank} `, ""];
                return (
                  <div key={item.itemId} style={{ marginBottom: 6 }}>
                    {segments.map((segment, segIndex) => (
                      <span key={`${item.itemId}-seg-${segIndex}`}>
                        {segment}
                        {segIndex < segments.length - 1 ? (
                          <InlineListenBlank
                            item={item}
                            value={answers[item.itemId]}
                            index={index}
                            interactive={interactive}
                            showResult={showResults}
                            onChange={(value) => setAnswer(item.itemId, value)}
                          />
                        ) : null}
                      </span>
                    ))}
                  </div>
                );
              })}
        </div>
      )}
      {showResults && (
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
      {interactive && <SubmitButton onClick={() => live!.onSubmit(live!.answers)} />}
    </TaskWidgetFrame>
  );
}

function InlineListenBlank({
  item,
  value,
  index,
  interactive,
  showResult,
  onChange,
}: {
  item: ListenClozeTask["items"][number];
  value?: string;
  index: number;
  interactive: boolean;
  showResult: boolean;
  onChange: (value: string) => void;
}) {
  const wrapStyle = {
    display: "inline-flex",
    alignItems: "center",
    gap: 6,
    margin: "0 5px",
    whiteSpace: "nowrap" as const,
    verticalAlign: "baseline" as const,
  };

  if (interactive) {
    return (
      <span style={wrapStyle}>
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
        <input
          className="tw-blank-input"
          value={value ?? ""}
          onChange={(event) => onChange(event.target.value)}
          aria-label={`Blank ${index + 1}`}
          style={{ width: "clamp(96px, 18vw, 160px)", textAlign: "left" }}
        />
        {item.baseVerb && (
          <span style={{ fontSize: 12, fontWeight: 600, color: "var(--tw-primary)", fontStyle: "italic" }}>
            ({item.baseVerb})
          </span>
        )}
      </span>
    );
  }

  if (!showResult) {
    return (
      <span style={wrapStyle}>
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
          style={{ width: "clamp(88px, 18vw, 150px)", color: "oklch(55% 0.07 240)" }}
        >
          answer
        </span>
        {item.baseVerb && (
          <span style={{ fontSize: 12, fontWeight: 600, color: "var(--tw-primary)", fontStyle: "italic" }}>
            ({item.baseVerb})
          </span>
        )}
      </span>
    );
  }

  const isCorrect = normalizeAnswer(value) === normalizeAnswer(item.correctAnswer);

  return (
    <span style={wrapStyle}>
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
