"use client";

import { CheckSquare } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, ReadWordMatchTask } from "../source";
import {
  FeedbackRow,
  liveMcqAnswerRecord,
  McqOptionList,
  mcqSubmission,
  normalizeAnswer,
  ResultBanner,
  RuleCallout,
  StatusDot,
  SubmitButton,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function ReadWordMatchTaskWidget({
  task,
  previewState,
  live,
}: {
  task: ReadWordMatchTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  if (live) {
    return <LiveWordMatch task={task} live={live} />;
  }
  return <PreviewWordMatch task={task} previewState={previewState} />;
}

// READ_WORD_MATCH is an Mcq archetype on the wire (objective index scoring), so
// live mode renders each prompt as a labelled option set and submits
// `selected_index` — mirroring the other Mcq-family widgets.
function LiveWordMatch({ task, live }: { task: ReadWordMatchTask; live: LiveTaskController }) {
  const interactive = !live.submitted;
  const showResults = live.submitted;
  const answers = liveMcqAnswerRecord(live.answers);
  const items = task.items.map((item) => ({
    itemId: item.itemId,
    prompt: item.prompt,
    options: item.options ?? [],
    correctIndex: item.correctIndex ?? -1,
    explanation: item.explanation,
  }));
  const allAnswered = items.every((item) => answers[item.itemId] !== undefined);

  const pick = (itemId: string, optionIndex: number) => {
    live.setAnswers({ ...live.answers, [itemId]: optionIndex });
  };

  return (
    <TaskWidgetFrame task={task} icon={<CheckSquare size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Grammar rule">{task.grammarRule}</RuleCallout>
      {items.map((item, index) => (
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
          onClick={() => live.onSubmit(mcqSubmission(items, answers))}
        />
      )}
    </TaskWidgetFrame>
  );
}

function PreviewWordMatch({
  task,
  previewState,
}: {
  task: ReadWordMatchTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? {} : task.answers[previewState];
  const correctCount = isDefault
    ? 0
    : task.items.filter(
        (item) => normalizeAnswer(answers[item.itemId]) === normalizeAnswer(item.correctAnswer),
      ).length;

  return (
    <TaskWidgetFrame task={task} icon={<CheckSquare size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Grammar rule">{task.grammarRule}</RuleCallout>
      {!isDefault && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} items matched`}
        />
      )}
      {isDefault && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 18 }}>
          {task.options.map((opt) => (
            <div
              key={opt}
              style={{
                padding: "8px 16px",
                borderRadius: 8,
                background: "white",
                border: "1.5px solid var(--tw-border)",
                boxShadow: "0 2px 6px rgba(80,110,180,0.08)",
                fontWeight: 700,
                color: "var(--tw-navy)",
                cursor: "grab",
                userSelect: "none"
              }}
            >
              {opt}
            </div>
          ))}
        </div>
      )}

      <div style={{ display: "grid", gap: 10, marginBottom: isDefault ? 0 : 20 }}>
        {task.items.map((item) => {
          const value = answers[item.itemId];
          const isCorrect = normalizeAnswer(value) === normalizeAnswer(item.correctAnswer);
          return (
            <div className="tw-card" key={item.itemId} style={{ padding: "12px 16px", display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 0 }}>
              <div style={{ fontWeight: 600, color: "var(--tw-navy)", fontSize: 15 }}>{item.prompt}</div>
              {isDefault ? (
                <div style={{
                  minWidth: 100,
                  height: 38,
                  border: "2px dashed oklch(85% 0.025 240)",
                  borderRadius: 8,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "oklch(62% 0.16 240)",
                  fontSize: 13,
                  fontWeight: 600,
                  background: "oklch(98% 0.01 245)"
                }}>
                  Drop here
                </div>
              ) : (
                <div style={{ display: "flex", alignItems: "center", gap: 8, fontWeight: 700, color: isCorrect ? "var(--tw-success)" : "var(--tw-error)" }}>
                  <div style={{
                    padding: "6px 14px",
                    borderRadius: 8,
                    background: isCorrect ? "rgba(46, 160, 67, 0.1)" : "rgba(248, 81, 73, 0.1)",
                    border: `1.5px solid ${isCorrect ? "var(--tw-success)" : "var(--tw-error)"}`,
                  }}>
                    {value}
                  </div>
                  <StatusDot ok={isCorrect} />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {!isDefault && (
        <div style={{ display: "grid", gap: 8 }}>
          {task.items.map((item) => {
            const value = answers[item.itemId];
            const isCorrect = normalizeAnswer(value) === normalizeAnswer(item.correctAnswer);
            return (
              <FeedbackRow
                key={item.itemId}
                ok={isCorrect}
                title={`${item.prompt} -> ${item.correctAnswer}`}
                body={isCorrect ? item.explanation : `${item.explanation} Correct answer: ${item.correctAnswer}.`}
              />
            );
          })}
        </div>
      )}
    </TaskWidgetFrame>
  );
}
