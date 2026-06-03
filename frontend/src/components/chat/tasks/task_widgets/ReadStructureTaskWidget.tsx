"use client";

import { BookOpenCheck, Check, ChevronDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";
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

/**
 * Styled label picker for the structure task. Replaces the native `<select>`
 * so the closed control's chevron sits inset from the edge (not jammed far
 * right) and the open menu matches the widget's rounded navy/soft-blue look
 * instead of the browser's default option list.
 */
function StructureLabelSelect({
  value,
  options,
  onChange,
  disabled = false,
  ariaLabel,
}: {
  value: string;
  options: readonly string[];
  onChange: (value: string) => void;
  disabled?: boolean;
  ariaLabel: string;
}) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const hasValue = Boolean(value);

  return (
    <div ref={rootRef} style={{ position: "relative", width: "100%" }}>
      <button
        type="button"
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={ariaLabel}
        onClick={() => !disabled && setOpen((prev) => !prev)}
        style={{
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 10,
          borderRadius: 10,
          border: `1.5px solid ${open ? "oklch(60% 0.13 250)" : "oklch(85% 0.025 240)"}`,
          background: disabled ? "oklch(99% 0.005 240)" : "white",
          color: hasValue ? "var(--tw-navy)" : "oklch(45% 0.06 240)",
          padding: "10px 14px",
          fontFamily: "inherit",
          fontSize: 13,
          fontWeight: 800,
          textAlign: "left",
          cursor: disabled ? "not-allowed" : "pointer",
          boxShadow: open ? "0 0 0 3px oklch(60% 0.13 250 / 0.16)" : "none",
          transition: "border-color 120ms ease, box-shadow 120ms ease",
        }}
      >
        <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {value || "Choose label"}
        </span>
        <ChevronDown
          size={18}
          strokeWidth={2.5}
          style={{
            flexShrink: 0,
            color: "oklch(55% 0.08 245)",
            transform: open ? "rotate(180deg)" : "none",
            transition: "transform 140ms ease",
          }}
        />
      </button>

      {open && !disabled && (
        <ul
          role="listbox"
          aria-label={ariaLabel}
          style={{
            position: "absolute",
            top: "calc(100% + 6px)",
            left: 0,
            right: 0,
            zIndex: 20,
            margin: 0,
            padding: 6,
            listStyle: "none",
            display: "grid",
            gap: 2,
            background: "white",
            borderRadius: 12,
            border: "1px solid oklch(90% 0.025 240)",
            boxShadow: "0 12px 28px oklch(45% 0.07 240 / 0.18)",
          }}
        >
          {options.map((option) => {
            const selected = option === value;
            return (
              <li
                key={option}
                role="option"
                aria-selected={selected}
                tabIndex={0}
                onClick={() => {
                  onChange(option);
                  setOpen(false);
                }}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    onChange(option);
                    setOpen(false);
                  }
                }}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: 8,
                  borderRadius: 8,
                  padding: "9px 11px",
                  fontSize: 13,
                  fontWeight: 800,
                  color: "var(--tw-navy)",
                  background: selected ? "oklch(95% 0.04 245)" : "transparent",
                  cursor: "pointer",
                  outline: "none",
                }}
                onMouseEnter={(event) => {
                  if (!selected) event.currentTarget.style.background = "oklch(97% 0.02 245)";
                }}
                onMouseLeave={(event) => {
                  if (!selected) event.currentTarget.style.background = "transparent";
                }}
                onFocus={(event) => {
                  if (!selected) event.currentTarget.style.background = "oklch(97% 0.02 245)";
                }}
                onBlur={(event) => {
                  if (!selected) event.currentTarget.style.background = "transparent";
                }}
              >
                {option}
                {selected && <Check size={15} strokeWidth={3} style={{ color: "oklch(55% 0.13 250)" }} />}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

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
                <StructureLabelSelect
                  value={value}
                  options={task.structureLabels}
                  disabled={!interactive}
                  ariaLabel={`Choose structure label for ${itemLabel}`}
                  onChange={(next) => setLabel(item.itemId, next)}
                />
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
              <StructureLabelSelect
                value=""
                options={task.structureLabels}
                disabled
                ariaLabel={`Choose structure label for ${item.label?.toLowerCase() ?? `paragraph ${index + 1}`}`}
                onChange={() => {}}
              />
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
