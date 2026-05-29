"use client";

import { Check, Volume2, X } from "lucide-react";
import { useState } from "react";
import type { SessionPreviewState } from "../../teaching/source";
import type { ListenMcqTask, LiveTaskController } from "../source";
import {
  ListeningAudioCard,
  liveNumberRecord,
  SubmitButton,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function ListenMcqTaskWidget({
  task,
  previewState,
  live,
}: {
  task: ListenMcqTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  const [audioComplete, setAudioComplete] = useState(false);
  const unlocked = live ? live.submitted || audioComplete : previewState !== "default" || audioComplete;
  const interactive = Boolean(live) && !live!.submitted && unlocked;
  const showResults = live ? live.submitted : previewState !== "default";
  const answers: Record<string, number> = live
    ? liveNumberRecord(live.answers)
    : previewState === "default"
      ? {}
      : task.answers[previewState];

  const allAnswered = task.items.every((item) => answers[item.itemId] !== undefined);

  const pick = (itemId: string, optionIndex: number) => {
    live?.setAnswers({ ...live.answers, [itemId]: optionIndex });
  };
  const submitAnswers = () => {
    live?.onSubmit({
      inner_response: {
        widget: "mcq",
        answers: task.items
          .filter((item) => answers[item.itemId] !== undefined)
          .map((item) => ({
            item_id: item.itemId,
            selected_index: answers[item.itemId],
          })),
      },
    });
  };

  return (
    <TaskWidgetFrame task={task} icon={<Volume2 size={18} strokeWidth={2.5} />}>
      <ListeningAudioCard
        title={task.audioGenre}
        script={task.audioScript}
        audioUrl={task.audioUrl}
        durationSeconds={task.audioDurationSeconds}
        completed={unlocked}
        hint="Listen once to unlock the questions below."
        onComplete={() => setAudioComplete(true)}
      />
      {unlocked && task.items.map((item, index) => {
        const selected = answers[item.itemId];
        return (
          <div className="tw-card" key={item.itemId}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">{item.prompt}</div>
            </div>
            <div className="tw-opt-list">
              {item.options.map((option, optionIndex) => {
                const isSelected = optionIndex === selected;
                const isCorrect = showResults && optionIndex === item.correctIndex;
                const isWrongPick = showResults && isSelected && !isCorrect;
                const cls =
                  `tw-opt-row` +
                  (isCorrect ? " correct" : "") +
                  (isWrongPick ? " wrong" : "") +
                  (interactive && isSelected ? " selected" : "");
                if (interactive) {
                  return (
                    <button
                      type="button"
                      key={option}
                      className={cls}
                      onClick={() => pick(item.itemId, optionIndex)}
                    >
                      <span className="tw-opt-key">{optionIndex + 1}</span>
                      <span style={{ flex: 1 }}>{option}</span>
                      {isSelected && <Check size={14} strokeWidth={2.8} />}
                    </button>
                  );
                }
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
            {showResults && (
              <div className="tw-fb-explain" style={{ marginTop: 12, paddingTop: 10 }}>
                <strong>{selected === item.correctIndex ? "Correct." : "Why it is wrong."}</strong>{" "}
                {item.explanation}
              </div>
            )}
          </div>
        );
      })}
      {interactive && <SubmitButton disabled={!allAnswered} onClick={submitAnswers} />}
    </TaskWidgetFrame>
  );
}
