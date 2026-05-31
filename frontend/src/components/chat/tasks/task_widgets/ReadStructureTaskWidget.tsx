"use client";

import { BookOpenCheck } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, ReadStructureTask } from "../source";
import {
  FeedbackRow,
  liveStringRecord,
  normalizeAnswer,
  ResultBanner,
  RuleCallout,
  StatusDot,
  SubmitButton,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

function LiveStructure({ task, live }: { task: ReadStructureTask; live: LiveTaskController }) {
  const interactive = !live.submitted;
  const showResults = live.submitted;
  const answers = liveStringRecord(live.answers);
  const allAnswered = task.items.every((item) => answers[item.itemId]);

  const setLabel = (itemId: string, value: string) => {
    live.setAnswers({ ...live.answers, [itemId]: value });
  };

  return (
    <TaskWidgetFrame task={task} icon={<BookOpenCheck size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Structure focus">{task.grammarRule}</RuleCallout>
      <div className="tw-passage" style={{ marginBottom: 16 }}>
        <div className="tw-passage-label">{task.passageTitle}</div>
        <div style={{ display: "grid", gap: 10 }}>
          {task.items.map((item, index) => {
            const value = answers[item.itemId] ?? "";
            const isCorrect = normalizeAnswer(value) === normalizeAnswer(item.correctAnswer);
            const itemLabel = item.label ?? `Paragraph ${index + 1}`;
            return (
              <div
                key={item.itemId}
                style={{
                  borderRadius: 14,
                  padding: "12px 14px",
                  background: "rgba(255,255,255,0.72)",
                  border: "1px solid oklch(90% 0.025 240)",
                }}
              >
                <div style={{ fontSize: 12, fontWeight: 900, color: "oklch(45% 0.07 240)", textTransform: "uppercase", marginBottom: 8 }}>
                  {itemLabel}
                </div>
                <div style={{ fontSize: 14.5, lineHeight: 1.65, color: "var(--tw-navy)", marginBottom: 10 }}>
                  {item.paragraph}
                </div>
                <select
                  value={value}
                  disabled={!interactive}
                  aria-label={`Choose structure label for ${itemLabel}`}
                  onChange={(event) => setLabel(item.itemId, event.target.value)}
                  style={{
                    width: "100%",
                    borderRadius: 10,
                    border: "1.5px solid oklch(85% 0.025 240)",
                    background: "white",
                    color: "var(--tw-navy)",
                    padding: "10px 12px",
                    fontFamily: "inherit",
                    fontSize: 13,
                    fontWeight: 800,
                  }}
                >
                  <option value="">Choose label</option>
                  {task.structureLabels.map((label) => (
                    <option key={label} value={label}>
                      {label}
                    </option>
                  ))}
                </select>
                {showResults && (
                  <div
                    style={{
                      marginTop: 8,
                      fontSize: 12.5,
                      fontWeight: 800,
                      color: isCorrect ? "var(--tw-green)" : "var(--tw-red)",
                    }}
                  >
                    {isCorrect ? "Correct." : `Correct label: ${item.correctAnswer}.`} {item.explanation}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
      {interactive && <SubmitButton disabled={!allAnswered} onClick={() => live.onSubmit(live.answers)} />}
    </TaskWidgetFrame>
  );
}

export function ReadStructureTaskWidget({
  task,
  previewState,
  live,
}: {
  task: ReadStructureTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  if (live) {
    return <LiveStructure task={task} live={live} />;
  }
  const isDefault = previewState === "default";
  const answers = isDefault ? {} : task.answers[previewState];
  const correctCount = isDefault
    ? 0
    : task.items.filter(
        (item) => normalizeAnswer(answers[item.itemId]) === normalizeAnswer(item.correctAnswer),
      ).length;

  return (
    <TaskWidgetFrame task={task} icon={<BookOpenCheck size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Structure focus">{task.grammarRule}</RuleCallout>

      <div className="tw-passage" style={{ marginBottom: 16 }}>
        <div className="tw-passage-label">{task.passageTitle}</div>
        <div style={{ display: "grid", gap: 10 }}>
          {task.items.map((item, index) => {
            const value = answers[item.itemId];
            const isCorrect = normalizeAnswer(value) === normalizeAnswer(item.correctAnswer);
            const itemLabel = item.label ?? `Paragraph ${index + 1}`;

            return (
              <div
                key={item.itemId}
                style={{
                  borderRadius: 14,
                  padding: "12px 14px",
                  background: "rgba(255,255,255,0.72)",
                  border: "1px solid oklch(90% 0.025 240)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 12,
                    alignItems: "flex-start",
                    marginBottom: 8,
                  }}
                >
                  <div
                    style={{
                      fontSize: 12,
                      fontWeight: 900,
                      color: "oklch(45% 0.07 240)",
                      textTransform: "uppercase",
                    }}
                  >
                    {itemLabel}
                  </div>
                  {!isDefault && (
                    <div style={{ display: "inline-flex", alignItems: "center", gap: 7 }}>
                      <StatusDot ok={isCorrect} />
                      <span
                        style={{
                          fontSize: 12.5,
                          fontWeight: 800,
                          color: isCorrect ? "var(--tw-green)" : "var(--tw-red)",
                        }}
                      >
                        {value}
                      </span>
                    </div>
                  )}
                </div>
                <div style={{ fontSize: 14.5, lineHeight: 1.65, color: "var(--tw-navy)" }}>
                  {item.paragraph}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {!isDefault && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} structure labels correct`}
        />
      )}

      {isDefault ? (
        <div style={{ display: "grid", gap: 10 }}>
          {task.items.map((item, index) => (
            <div
              className="tw-card"
              key={item.itemId}
              style={{
                marginBottom: 0,
                display: "grid",
                gridTemplateColumns: "minmax(0, 1fr) minmax(150px, 190px)",
                gap: 12,
                alignItems: "center",
              }}
            >
              <div style={{ fontSize: 14, fontWeight: 800, color: "var(--tw-navy)" }}>
                Label {item.label?.toLowerCase() ?? `paragraph ${index + 1}`}
              </div>
              <select
                disabled
                value=""
                aria-label={`Choose structure label for ${item.label?.toLowerCase() ?? `paragraph ${index + 1}`}`}
                style={{
                  width: "100%",
                  borderRadius: 10,
                  border: "1.5px solid oklch(85% 0.025 240)",
                  background: "oklch(99% 0.005 240)",
                  color: "oklch(55% 0.06 240)",
                  padding: "10px 12px",
                  fontFamily: "inherit",
                  fontSize: 13,
                  fontWeight: 800,
                }}
              >
                <option value="">Choose label</option>
                {task.structureLabels.map((label) => (
                  <option key={label} value={label}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ display: "grid", gap: 8 }}>
          {task.items.map((item, index) => {
            const value = answers[item.itemId];
            const isCorrect = normalizeAnswer(value) === normalizeAnswer(item.correctAnswer);
            const itemLabel = item.label ?? `Paragraph ${index + 1}`;

            return (
              <FeedbackRow
                key={item.itemId}
                ok={isCorrect}
                title={`${itemLabel}: ${item.correctAnswer}`}
                body={
                  isCorrect
                    ? item.explanation
                    : `${item.explanation} Correct label: ${item.correctAnswer}.`
                }
              />
            );
          })}
        </div>
      )}
    </TaskWidgetFrame>
  );
}
