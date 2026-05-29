"use client";

import { Mic2, MessageSquare, Sparkles } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { SpeakRoleplayTask } from "../source";
import {
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function SpeakRoleplayTaskWidget({
  task,
  previewState,
}: {
  task: SpeakRoleplayTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? [] : task.answers[previewState];
  const learnerTurnIndexes = task.dialogueContext
    .map((bubble, index) => (bubble.speaker === "learner" ? index : -1))
    .filter((index) => index !== -1);
  const correctCount = isDefault ? 0 : answers.filter((answer) => answer.isCorrect).length;

  return (
    <TaskWidgetFrame task={task} icon={<MessageSquare size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Speaking focus">{task.grammarRule}</RuleCallout>

      <div style={{ marginBottom: 14 }}>
        <div style={{ fontSize: 12, fontWeight: 800, color: "oklch(45% 0.07 240)", marginBottom: 6, textTransform: "uppercase" }}>
          Target Words
        </div>
        <div className="tw-target-chip-row">
          {task.targetWords.map((word) => (
            <span 
              className="tw-target-chip used" 
              key={word}
              style={{
                background: "oklch(93% 0.04 155)",
                color: "oklch(42% 0.16 155)",
                border: "1px solid oklch(85% 0.06 155)"
              }}
            >
              {word}
            </span>
          ))}
        </div>
      </div>

      {!isDefault && (
        <ResultBanner
          total={learnerTurnIndexes.length}
          correct={correctCount}
          label={`${correctCount} of ${learnerTurnIndexes.length} responses correct`}
        />
      )}

      {/* Roleplay Chat Window */}
      <div 
        style={{
          border: "1.5px solid oklch(90% 0.02 240)",
          borderRadius: 18,
          background: "oklch(97% 0.015 245)",
          padding: 16,
          display: "flex",
          flexDirection: "column",
          gap: 16,
          marginBottom: 16,
          boxShadow: "inset 0 2px 8px rgba(80,110,180,0.03)"
        }}
      >
        <div style={{ fontSize: 11, fontWeight: 800, color: "oklch(45% 0.07 240)", textTransform: "uppercase", letterSpacing: "0.05em", borderBottom: "1px dashed oklch(85% 0.03 240)", paddingBottom: 6 }}>
          Conversation
        </div>

        {task.dialogueContext.map((bubble, index) => {
          const isPartner = bubble.speaker === "partner";
          const learnerTurnIndex = learnerTurnIndexes.indexOf(index);
          const turnAnswer = learnerTurnIndex !== -1 ? answers[learnerTurnIndex] : null;

          return (
            <div 
              key={`${bubble.role}-${index}`}
              style={{
                display: "flex",
                flexDirection: isPartner ? "row" : "row-reverse",
                alignItems: "flex-start",
                gap: 10,
                width: "100%"
              }}
            >
              {/* Avatar Badge */}
              <div 
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 10,
                  background: isPartner ? "oklch(55% 0.16 240)" : "oklch(45% 0.18 155)",
                  color: "white",
                  fontSize: 12,
                  fontWeight: 800,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: "0 3px 8px rgba(0,0,0,0.06)",
                  flexShrink: 0
                }}
              >
                {bubble.role[0]}
              </div>

              {/* Message Bubble */}
              <div style={{ maxWidth: "80%" }}>
                <div 
                  style={{ 
                    fontSize: 11, 
                    fontWeight: 700, 
                    color: "oklch(45% 0.07 240)", 
                    marginBottom: 3,
                    textAlign: isPartner ? "left" : "right"
                  }}
                >
                  {bubble.role}
                </div>

                <div 
                  style={{
                    padding: "10px 14px",
                    borderRadius: 14,
                    borderTopLeftRadius: isPartner ? 0 : 14,
                    borderTopRightRadius: isPartner ? 14 : 0,
                    background: isPartner ? "white" : "oklch(90% 0.05 155)",
                    border: isPartner ? "1px solid oklch(90% 0.02 240)" : "1px solid oklch(85% 0.05 155)",
                    color: "oklch(20% 0.09 245)",
                    fontSize: 13.5,
                    lineHeight: 1.5,
                    boxShadow: "0 2px 6px rgba(0,0,0,0.02)"
                  }}
                >
                  {isPartner ? (
                    bubble.text
                  ) : isDefault ? (
                    // Default State recording prompt
                    <div style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer" }}>
                      <div 
                        style={{
                          width: 28,
                          height: 28,
                          borderRadius: "50%",
                          background: "#0070C4",
                          color: "white",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center"
                        }}
                      >
                        <Mic2 size={13} strokeWidth={2.5} />
                      </div>
                      <div style={{ minWidth: 0 }}>
                        <div style={{ fontSize: 13, fontWeight: 800 }}>Tap to record</div>
                        <div style={{ fontSize: 10.5, opacity: 0.8 }}>Record up to {task.speakingDurationSeconds}s</div>
                      </div>
                    </div>
                  ) : (
                    // Submitted State Transcript
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, fontWeight: 800, color: "oklch(35% 0.18 155)", marginBottom: 4 }}>
                        <StatusDot ok={Boolean(turnAnswer?.isCorrect)} />
                        <span>YOUR RESPONSE</span>
                      </div>
                      <div style={{ fontStyle: "italic", fontSize: 13, color: "oklch(20% 0.09 245)", marginBottom: 4 }}>
                        &ldquo;{turnAnswer?.transcript}&rdquo;
                      </div>
                      <div style={{ fontSize: 10.5, opacity: 0.75, fontWeight: 600 }}>
                        {turnAnswer?.durationSeconds}s recording
                      </div>
                    </div>
                  )}
                </div>

                {/* Model response helper shown in evaluated states */}
                {!isPartner && !isDefault && (
                  <div 
                    style={{ 
                      marginTop: 6, 
                      padding: "8px 10px", 
                      borderRadius: 8, 
                      background: "oklch(96% 0.02 155)", 
                      border: "1px dashed oklch(85% 0.05 155)",
                      fontSize: 12,
                      color: "oklch(35% 0.18 155)",
                      display: "flex",
                      flexDirection: "column",
                      gap: 2
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 4, fontWeight: 800 }}>
                      <Sparkles size={11} />
                      <span>Model Answer</span>
                    </div>
                    <div>{bubble.text}</div>
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
