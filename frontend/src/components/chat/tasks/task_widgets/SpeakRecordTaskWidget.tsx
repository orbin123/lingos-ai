"use client";

import { Mic2 } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { SpeakRecordTask } from "../source";
import {
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function SpeakRecordTaskWidget({
  task,
  previewState,
}: {
  task: SpeakRecordTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? [] : task.answers[previewState];
  const correctCount = isDefault ? 0 : answers.filter((answer) => answer.isCorrect).length;

  return (
    <TaskWidgetFrame task={task} icon={<Mic2 size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Speaking pattern">{task.grammarRule}</RuleCallout>
      {!isDefault && (
        <ResultBanner
          total={task.prompts.length}
          correct={correctCount}
          label={`${correctCount} of ${task.prompts.length} recordings clear`}
        />
      )}
      {task.prompts.map((prompt, index) => {
        const answer = answers[index];
        return (
          <div className="tw-card" key={prompt}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">{prompt}</div>
            </div>
            {isDefault ? (
              <div className="tw-card" style={{ background: "oklch(97% 0.02 245)", marginBottom: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <div
                    style={{
                      width: 42,
                      height: 42,
                      borderRadius: "50%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      background: "#0070C4",
                      color: "white",
                      flexShrink: 0,
                    }}
                  >
                    <Mic2 size={20} strokeWidth={2.4} />
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: 13.5, fontWeight: 800, color: "var(--tw-navy)" }}>
                      Tap to record
                    </div>
                    <div style={{ marginTop: 3, fontSize: 12.5, color: "var(--tw-ink-muted)", lineHeight: 1.45 }}>
                      Record up to {task.speakingDurationSeconds} seconds for this prompt.
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                  gap: 10,
                }}
              >
                <div className="tw-compare-card">
                  <div className="tw-compare-label">
                    <StatusDot ok={answer.isCorrect} />
                    Transcript
                  </div>
                  <div className="tw-compare-body">{answer.transcript}</div>
                  <div style={{ marginTop: 8, fontSize: 12, color: "var(--tw-ink-muted)", fontWeight: 700 }}>
                    {answer.durationSeconds}s recording
                  </div>
                </div>
                <div className="tw-compare-card sample">
                  <div className="tw-compare-label">
                    <Mic2 size={12} />
                    Model
                  </div>
                  <div className="tw-compare-body">{task.sampleResponses[index]}</div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </TaskWidgetFrame>
  );
}
