"use client";

import { Check, FileText, X } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { ReadTfngTask } from "../source";
import { ResultBanner, RuleCallout, TaskWidgetFrame } from "./TaskWidgetFrame";

export function ReadTfngTaskWidget({
  task,
  previewState,
}: {
  task: ReadTfngTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? {} : task.answers[previewState];
  const correctCount = isDefault
    ? 0
    : task.items.filter((item) => answers[item.itemId] === item.correctAnswer).length;

  const options: ("True" | "False" | "Not Given")[] = ["True", "False", "Not Given"];

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
          label={`${correctCount} of ${task.items.length} statements correct`}
        />
      )}

      {task.items.map((item, index) => {
        const selected = answers[item.itemId];
        return (
          <div className="tw-card" key={item.itemId}>
            <div className="tw-q-number-row" style={{ marginBottom: 14 }}>
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem" style={{ fontWeight: 700 }}>{item.prompt}</div>
            </div>
            
            <div 
              style={{ 
                display: "grid", 
                gridTemplateColumns: "repeat(3, 1fr)", 
                gap: 8,
                marginTop: 10 
              }}
            >
              {options.map((option) => {
                const isSelected = selected === option;
                const isCorrectOption = option === item.correctAnswer;
                
                let bg = "oklch(98% 0.01 240)";
                let border = "1.5px solid var(--tw-line)";
                let color = "var(--tw-navy)";
                let iconEl = null;

                if (!isDefault) {
                  if (isSelected) {
                    if (isCorrectOption) {
                      bg = "var(--tw-green-soft)";
                      border = "1.5px solid var(--tw-green)";
                      color = "oklch(28% 0.14 155)";
                      iconEl = <Check size={14} strokeWidth={3} style={{ marginLeft: 4 }} />;
                    } else {
                      bg = "var(--tw-red-soft)";
                      border = "1.5px solid var(--tw-red)";
                      color = "oklch(35% 0.16 25)";
                      iconEl = <X size={14} strokeWidth={3} style={{ marginLeft: 4 }} />;
                    }
                  } else if (isCorrectOption) {
                    // Show correct answer even if the user didn't pick it in wrong state
                    bg = "var(--tw-green-soft)";
                    border = "1px dashed var(--tw-green)";
                    color = "oklch(28% 0.14 155)";
                  }
                } else {
                  // Default state design
                  if (option === "True") {
                    bg = "rgba(255, 255, 255, 0.9)";
                  }
                }

                return (
                  <button
                    key={option}
                    type="button"
                    disabled
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      padding: "10px 8px",
                      borderRadius: 10,
                      background: bg,
                      border: border,
                      color: color,
                      fontSize: 13,
                      fontWeight: 800,
                      cursor: "default",
                      transition: "all 0.15s"
                    }}
                  >
                    <span>{option}</span>
                    {iconEl}
                  </button>
                );
              })}
            </div>

            {!isDefault && (
              <div className="tw-fb-explain" style={{ marginTop: 12, paddingTop: 10 }}>
                <strong>{selected === item.correctAnswer ? "Correct." : "Why it is wrong."}</strong>{" "}
                {item.explanation}
              </div>
            )}
          </div>
        );
      })}
    </TaskWidgetFrame>
  );
}
