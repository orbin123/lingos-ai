"use client";

import { Mic2, MessageSquare, Sparkles, Trophy } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, SpeakDebateTask } from "../source";
import { DialogueContextBlock, LiveSpeakingRecorder } from "./LiveSpeakingRecorder";
import {
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function SpeakDebateTaskWidget({
  task,
  previewState,
  live,
}: {
  task: SpeakDebateTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  if (live) {
    return (
      <TaskWidgetFrame task={task} icon={<Trophy size={18} strokeWidth={2.5} />}>
        <RuleCallout label="Speaking Focus">{task.grammarRule}</RuleCallout>
        <LiveSpeakingRecorder
          live={live}
          durationSeconds={task.speakingDurationSeconds}
          slots={[
            {
              id: "prompt_1",
              prompt: task.prompts?.[0] || "Present your argument out loud.",
              sampleResponse: task.sampleResponses?.[0] || "",
              context: <DialogueContextBlock turns={task.debateContext} />,
            },
          ]}
        />
      </TaskWidgetFrame>
    );
  }
  const isDefault = previewState === "default";
  const answers = isDefault ? [] : task.answers[previewState];
  const correctCount = isDefault ? 0 : answers.filter((answer) => answer.isCorrect).length;
  const answer = answers[0];

  return (
    <TaskWidgetFrame task={task} icon={<Trophy size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Speaking Focus">{task.grammarRule}</RuleCallout>

      {!isDefault && (
        <ResultBanner
          total={1}
          correct={correctCount}
          label={
            answer?.isCorrect
              ? "Polished counter-argument delivered successfully"
              : "Counter-argument complete but missed target debate markers"
          }
        />
      )}

      {/* Debate Arena */}
      <div 
        style={{
          border: "1.5px solid oklch(88% 0.03 240)",
          borderRadius: 20,
          background: "linear-gradient(to bottom, oklch(99% 0.01 245), oklch(97% 0.015 245))",
          padding: 18,
          display: "flex",
          flexDirection: "column",
          gap: 16,
          marginBottom: 16,
          boxShadow: "0 4px 16px rgba(80,110,180,0.02)"
        }}
      >
        <div 
          style={{ 
            fontSize: 11, 
            fontWeight: 800, 
            color: "oklch(45% 0.07 240)", 
            textTransform: "uppercase", 
            letterSpacing: "0.06em", 
            borderBottom: "1.5px dashed oklch(85% 0.03 240)", 
            paddingBottom: 8,
            display: "flex",
            alignItems: "center",
            gap: 6
          }}
        >
          <MessageSquare size={13} />
          <span>Debate Arena: Learn alone vs. with others</span>
        </div>

        {task.debateContext.map((bubble, index) => {
          const isModerator = bubble.role.includes("Moderator");
          const isOpponent = bubble.role.includes("Opponent");

          if (isModerator) {
            return (
              <div 
                key={`${bubble.role}-${index}`}
                style={{
                  display: "flex",
                  justifyContent: "center",
                  width: "100%",
                  margin: "4px 0"
                }}
              >
                <div 
                  style={{
                    background: "oklch(94% 0.02 245)",
                    border: "1px solid oklch(88% 0.02 245)",
                    borderRadius: 12,
                    padding: "8px 14px",
                    fontSize: 12,
                    color: "oklch(40% 0.05 240)",
                    fontWeight: 700,
                    textAlign: "center",
                    maxWidth: "90%"
                  }}
                >
                  <span style={{ fontWeight: 800, color: "#0070C4" }}>{bubble.role}:</span> {bubble.text}
                </div>
              </div>
            );
          }

          if (isOpponent) {
            return (
              <div 
                key={`${bubble.role}-${index}`}
                style={{
                  display: "flex",
                  flexDirection: "row",
                  alignItems: "flex-start",
                  gap: 10,
                  width: "100%"
                }}
              >
                <div 
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 10,
                    background: "oklch(55% 0.16 20)",
                    color: "white",
                    fontSize: 12,
                    fontWeight: 800,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    boxShadow: "0 3px 8px rgba(220,80,50,0.15)",
                    flexShrink: 0
                  }}
                >
                  AI
                </div>
                <div style={{ maxWidth: "80%" }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: "oklch(45% 0.07 20)", marginBottom: 3 }}>
                    {bubble.role}
                  </div>
                  <div 
                    style={{
                      padding: "10px 14px",
                      borderRadius: "0 14px 14px 14px",
                      background: "white",
                      border: "1px solid oklch(90% 0.02 20)",
                      color: "oklch(20% 0.09 245)",
                      fontSize: 13.5,
                      lineHeight: 1.5,
                      boxShadow: "0 2px 6px rgba(0,0,0,0.02)"
                    }}
                  >
                    {bubble.text}
                  </div>
                </div>
              </div>
            );
          }

          // Learner turn
          return (
            <div 
              key={`${bubble.role}-${index}`}
              style={{
                display: "flex",
                flexDirection: "row-reverse",
                alignItems: "flex-start",
                gap: 10,
                width: "100%"
              }}
            >
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
                  boxShadow: "0 3px 8px rgba(0,180,100,0.1)",
                  flexShrink: 0
                }}
              >
                YOU
              </div>
              <div style={{ maxWidth: "80%", width: "100%" }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: "oklch(45% 0.07 155)", marginBottom: 3, textAlign: "right" }}>
                  Your Counter-Argument
                </div>

                <div 
                  style={{
                    padding: "12px 16px",
                    borderRadius: "14px 0 14px 14px",
                    background: isDefault ? "white" : "oklch(91% 0.04 155)",
                    border: isDefault ? "1.5px dashed oklch(85% 0.03 240)" : "1px solid oklch(83% 0.05 155)",
                    color: "oklch(20% 0.09 245)",
                    fontSize: 13.5,
                    lineHeight: 1.5,
                    boxShadow: "0 2px 6px rgba(0,0,0,0.02)"
                  }}
                >
                  {isDefault ? (
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "12px 0", gap: 10 }}>
                      <div
                        style={{
                          position: "relative",
                          width: 64,
                          height: 64,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        <svg width="64" height="64" viewBox="0 0 64 64" style={{ position: "absolute", inset: 0 }}>
                          <circle cx="32" cy="32" r="28" stroke="oklch(91% 0.02 245)" strokeWidth="4" fill="none" />
                          <circle
                            cx="32"
                            cy="32"
                            r="28"
                            stroke="#0070C4"
                            strokeWidth="4"
                            fill="none"
                            strokeLinecap="round"
                            strokeDasharray={2 * Math.PI * 28}
                            strokeDashoffset={2 * Math.PI * 28 * 0.25}
                            transform="rotate(-90 32 32)"
                          />
                        </svg>
                        <div 
                          style={{
                            width: 44,
                            height: 44,
                            borderRadius: "50%",
                            background: "#0070C4",
                            color: "white",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            boxShadow: "0 4px 12px rgba(0,112,196,0.25)"
                          }}
                        >
                          <Mic2 size={18} strokeWidth={2.5} />
                        </div>
                      </div>
                      <div style={{ textAlign: "center" }}>
                        <div style={{ fontSize: 13.5, fontWeight: 800, color: "oklch(20% 0.09 245)" }}>Tap to record counter-argument</div>
                        <div style={{ fontSize: 11, color: "oklch(45% 0.07 240)", marginTop: 2 }}>Record up to {task.speakingDurationSeconds}s</div>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, fontWeight: 800, color: "oklch(35% 0.18 155)", marginBottom: 6 }}>
                        <StatusDot ok={Boolean(answer?.isCorrect)} />
                        <span>YOUR RECORDED RESPONSE</span>
                      </div>
                      <div style={{ fontStyle: "italic", fontSize: 13.5, color: "oklch(20% 0.09 245)", marginBottom: 6, lineHeight: 1.5 }}>
                        &ldquo;{answer?.transcript}&rdquo;
                      </div>
                      <div style={{ fontSize: 11, color: "oklch(42% 0.08 155)", fontWeight: 700 }}>
                        {answer?.durationSeconds}s recording • Limit: {task.speakingDurationSeconds}s
                      </div>
                    </div>
                  )}
                </div>

                {!isDefault && (
                  <div 
                    style={{ 
                      marginTop: 8, 
                      padding: "10px 14px", 
                      borderRadius: 12, 
                      background: "oklch(96% 0.02 155)", 
                      border: "1.5px dashed oklch(85% 0.05 155)",
                      fontSize: 12.5,
                      color: "oklch(30% 0.16 155)",
                      display: "flex",
                      flexDirection: "column",
                      gap: 4
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 5, fontWeight: 800, color: "oklch(35% 0.18 155)" }}>
                      <Sparkles size={12} fill="currentColor" />
                      <span>Model Counter-Argument Suggestion</span>
                    </div>
                    <div style={{ lineHeight: 1.5 }}>{bubble.text}</div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </TaskWidgetFrame>
  );
}
