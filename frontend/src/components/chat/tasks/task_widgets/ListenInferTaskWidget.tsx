"use client";

import { Ear, Sparkles } from "lucide-react";
import { useState } from "react";
import type { SessionPreviewState } from "../../teaching/source";
import type { ListenInferTask, LiveTaskController } from "../source";
import {
  ListeningAudioCard,
  liveMcqAnswerRecord,
  McqOptionList,
  mcqSubmission,
  ResultBanner,
  RuleCallout,
  SubmitButton,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function ListenInferTaskWidget({
  task,
  previewState,
  live,
}: {
  task: ListenInferTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  const [audioComplete, setAudioComplete] = useState(false);
  const unlocked = live ? live.submitted || audioComplete : previewState !== "default" || audioComplete;
  const interactive = Boolean(live) && !live!.submitted && unlocked;
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
    <TaskWidgetFrame task={task} icon={<Ear size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Listening focus">{task.intentFocus}</RuleCallout>

      <ListeningAudioCard
        title={task.audioGenre}
        script={task.audioScript}
        audioUrl={task.audioUrl}
        durationSeconds={task.audioDurationSeconds}
        completed={unlocked}
        hint="Listen once to unlock the questions below."
        onComplete={() => setAudioComplete(true)}
      />

      {showResults && !live?.submitted && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} intent questions correct`}
        />
      )}

      {unlocked &&
        task.items.map((item, index) => (
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
              optionKey={() => <Sparkles size={12} strokeWidth={2.8} />}
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
