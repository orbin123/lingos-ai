"use client";

import { FileText, Sparkles } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, OpenTextTask } from "../source";
import { spatialFieldProps } from "@/lib/spatial-field-navigation";
import {
  liveStringRecord,
  ResultBanner,
  RuleCallout,
  StatusDot,
  SubmitButton,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function OpenTextTaskWidget({
  task,
  previewState,
  live,
}: {
  task: OpenTextTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  const interactive = Boolean(live) && !live!.submitted;
  // In live mode per-item correctness comes from the LLM evaluator (shown in the
  // feedback card), so the widget renders the learner's text vs the sample
  // without its own pass/fail marks.
  const liveAnswers = live ? liveStringRecord(live.answers) : null;
  const previewAnswers = !live && previewState !== "default" ? task.answers[previewState] : null;

  const setAnswer = (itemId: string, value: string) => {
    live?.setAnswers({ ...live.answers, [itemId]: value });
  };

  return (
    <TaskWidgetFrame task={task} icon={<FileText size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Rule">{task.grammarRule}</RuleCallout>
      {previewAnswers && (
        <ResultBanner
          total={task.items.length}
          correct={previewAnswers.filter((answer) => answer.isCorrect).length}
          label={`${previewAnswers.filter((answer) => answer.isCorrect).length} of ${task.items.length} sentences accepted`}
        />
      )}
      {task.items.map((item, index) => {
        const previewAnswer = previewAnswers?.find((row) => row.itemId === item.itemId);
        const liveText = liveAnswers?.[item.itemId] ?? "";
        return (
          <div className="tw-card" key={item.itemId}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">{item.prompt}</div>
            </div>
            {interactive ? (
              <textarea
                className="tw-write-area"
                value={liveText}
                onChange={(event) => setAnswer(item.itemId, event.target.value)}
                placeholder="Write your answer here..."
                style={{ minHeight: 92 }}
                {...spatialFieldProps(index)}
              />
            ) : live ? (
              <div className="tw-compare-grid">
                <div className="tw-compare-card">
                  <div className="tw-compare-label">Your answer</div>
                  <div className="tw-compare-body">{liveText}</div>
                </div>
                <div className="tw-compare-card sample">
                  <div className="tw-compare-label">
                    <Sparkles size={12} />
                    Sample answer
                  </div>
                  <div className="tw-compare-body">{item.sampleAnswer}</div>
                </div>
              </div>
            ) : previewState === "default" ? (
              <>
                <div
                  className="tw-write-area"
                  style={{ color: "oklch(55% 0.07 240)", minHeight: 92, pointerEvents: "none" }}
                >
                  Write your answer here...
                </div>
                <div className="tw-write-helper">
                  <span>Minimum 5 characters per prompt.</span>
                  <span className="tw-count short">0 words - need more</span>
                </div>
              </>
            ) : (
              <div className="tw-compare-grid">
                <div className="tw-compare-card">
                  <div className="tw-compare-label">
                    <StatusDot ok={Boolean(previewAnswer?.isCorrect)} />
                    Your answer
                  </div>
                  <div className="tw-compare-body">{previewAnswer?.text}</div>
                </div>
                <div className="tw-compare-card sample">
                  <div className="tw-compare-label">
                    <Sparkles size={12} />
                    Sample answer
                  </div>
                  <div className="tw-compare-body">{item.sampleAnswer}</div>
                </div>
              </div>
            )}
            <div className="tw-hints-block">
              <div className="tw-hints-label">Hints</div>
              <div className="tw-hints-list">
                {item.answerHints.map((hint) => (
                  <div className="tw-hint-item" key={hint}>
                    <span className="tw-hint-dot" />
                    {hint}
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      })}
      {interactive && <SubmitButton onClick={() => live!.onSubmit(live!.answers)} />}
    </TaskWidgetFrame>
  );
}
