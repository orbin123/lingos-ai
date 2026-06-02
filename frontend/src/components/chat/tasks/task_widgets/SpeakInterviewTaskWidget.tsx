"use client";

import { Mic2, MessagesSquare, Sparkles } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, SpeakInterviewTask } from "../source";
import { LiveSpeakingRecorder } from "./LiveSpeakingRecorder";
import {
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function SpeakInterviewTaskWidget({
  task,
  previewState,
  live,
}: {
  task: SpeakInterviewTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  if (live) {
    return (
      <TaskWidgetFrame task={task} icon={<MessagesSquare size={18} strokeWidth={2.5} />}>
        <RuleCallout label="Interview focus">{task.grammarRule}</RuleCallout>
        {task.interviewContext && (
          <div className="tw-card" style={{ background: "oklch(98% 0.01 245)", marginBottom: 12 }}>
            {task.interviewContext}
          </div>
        )}
        <LiveSpeakingRecorder
          live={live}
          durationSeconds={task.speakingDurationSeconds}
          slots={task.questions.map((question, index) => ({
            id: `prompt_${index + 1}`,
            prompt: question.interviewerPrompt,
            sampleResponse: question.sampleAnswer,
            context: question.answerHint ? (
              <div className="tw-write-helper" style={{ marginBottom: 4 }}>
                Hint: {question.answerHint}
              </div>
            ) : undefined,
          }))}
        />
      </TaskWidgetFrame>
    );
  }
  const isDefault = previewState === "default";
  const answers = isDefault ? [] : task.answers[previewState];
  const correctCount = isDefault ? 0 : answers.filter((answer) => answer.isCorrect).length;

  return (
    <TaskWidgetFrame task={task} icon={<MessagesSquare size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Interview focus">{task.grammarRule}</RuleCallout>

      {!isDefault && (
        <ResultBanner
          total={task.questions.length}
          correct={correctCount}
          label={`${correctCount} of ${task.questions.length} interview answers clear`}
        />
      )}

      <div
        style={{
          border: "1.5px solid oklch(90% 0.02 240)",
          borderRadius: 18,
          background: "oklch(97% 0.015 245)",
          padding: 16,
          display: "flex",
          flexDirection: "column",
          gap: 14,
          marginBottom: 16,
          boxShadow: "inset 0 2px 8px rgba(80,110,180,0.03)",
        }}
      >
        <div style={{ fontSize: 11, fontWeight: 800, color: "oklch(45% 0.07 240)", textTransform: "uppercase", letterSpacing: "0.05em", borderBottom: "1px dashed oklch(85% 0.03 240)", paddingBottom: 6 }}>
          {task.interviewContext}
        </div>

        {task.questions.map((question, index) => {
          const answer = answers[index];
          return (
            <div key={question.itemId} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 10,
                    background: "oklch(55% 0.16 240)",
                    color: "white",
                    fontSize: 12,
                    fontWeight: 800,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  AI
                </div>
                <div style={{ maxWidth: "84%" }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: "oklch(45% 0.07 240)", marginBottom: 3 }}>
                    LingosAI
                  </div>
                  <div
                    style={{
                      padding: "10px 14px",
                      borderRadius: 14,
                      borderTopLeftRadius: 0,
                      background: "white",
                      border: "1px solid oklch(90% 0.02 240)",
                      color: "oklch(20% 0.09 245)",
                      fontSize: 13.5,
                      lineHeight: 1.5,
                    }}
                  >
                    {question.interviewerPrompt}
                  </div>
                </div>
              </div>

              <div style={{ display: "flex", flexDirection: "row-reverse", alignItems: "flex-start", gap: 10 }}>
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 10,
                    background: "oklch(45% 0.18 155)",
                    color: "white",
                    fontSize: 12,
                    fontWeight: 800,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  Y
                </div>
                <div style={{ maxWidth: "84%" }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: "oklch(45% 0.07 240)", marginBottom: 3, textAlign: "right" }}>
                    You
                  </div>
                  <div
                    style={{
                      padding: "10px 14px",
                      borderRadius: 14,
                      borderTopRightRadius: 0,
                      background: "oklch(90% 0.05 155)",
                      border: "1px solid oklch(85% 0.05 155)",
                      color: "oklch(20% 0.09 245)",
                      fontSize: 13.5,
                      lineHeight: 1.5,
                    }}
                  >
                    {isDefault ? (
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <div
                          style={{
                            width: 28,
                            height: 28,
                            borderRadius: "50%",
                            background: "#0070C4",
                            color: "white",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          <Mic2 size={13} strokeWidth={2.5} />
                        </div>
                        <div style={{ minWidth: 0 }}>
                          <div style={{ fontSize: 13, fontWeight: 800 }}>Tap to answer</div>
                          <div style={{ fontSize: 10.5, opacity: 0.8 }}>{question.answerHint}</div>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, fontWeight: 800, color: "oklch(35% 0.18 155)", marginBottom: 4 }}>
                          <StatusDot ok={Boolean(answer?.isCorrect)} />
                          <span>YOUR ANSWER</span>
                        </div>
                        <div style={{ fontStyle: "italic", fontSize: 13, color: "oklch(20% 0.09 245)", marginBottom: 4 }}>
                          &ldquo;{answer?.transcript}&rdquo;
                        </div>
                        <div style={{ fontSize: 10.5, opacity: 0.75, fontWeight: 600 }}>
                          {answer?.durationSeconds}s recording
                        </div>
                      </div>
                    )}
                  </div>

                  {!isDefault && (
                    <div
                      style={{
                        marginTop: 6,
                        padding: "8px 10px",
                        borderRadius: 8,
                        background: "oklch(96% 0.02 155)",
                        border: "1px dashed oklch(85% 0.05 155)",
                        fontSize: 12,
                        color: "oklch(35% 0.18 155)",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: 4, fontWeight: 800, marginBottom: 2 }}>
                        <Sparkles size={11} />
                        <span>Sample answer</span>
                      </div>
                      {question.sampleAnswer}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </TaskWidgetFrame>
  );
}
