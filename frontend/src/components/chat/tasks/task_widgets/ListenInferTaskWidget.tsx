"use client";

import { Check, Ear, Play, Sparkles, X } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { ListenInferTask } from "../source";
import { ResultBanner, RuleCallout, roundIconButton, TaskWidgetFrame } from "./TaskWidgetFrame";

export function ListenInferTaskWidget({
  task,
  previewState,
}: {
  task: ListenInferTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? {} : task.answers[previewState];
  const correctCount = isDefault
    ? 0
    : task.items.filter((item) => answers[item.itemId] === item.correctIndex).length;

  const playScript = () => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(task.audioScript);
    utterance.rate = 0.92;
    window.speechSynthesis.speak(utterance);
  };

  return (
    <TaskWidgetFrame task={task} icon={<Ear size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Listening focus">{task.intentFocus}</RuleCallout>

      <div className="tw-card" style={{ background: "oklch(97% 0.02 245)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button
            type="button"
            onClick={playScript}
            title="Play mock audio"
            aria-label="Play mock audio"
            style={roundIconButton}
          >
            <Play size={18} fill="currentColor" />
          </button>
          <div style={{ minWidth: 0 }}>
            <div className="tw-rule-label">{task.audioGenre}</div>
            <div style={{ fontSize: 13.5, lineHeight: 1.55, color: "var(--tw-navy)" }}>
              {task.audioScript}
            </div>
          </div>
        </div>
      </div>

      {!isDefault && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} intent questions correct`}
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
                    <span className="tw-opt-key">
                      <Sparkles size={12} strokeWidth={2.8} />
                    </span>
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
