"use client";

import { Mic2, Sparkles } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { SpeakTimedTask } from "../source";
import { ResultBanner, RuleCallout, StatusDot, TaskWidgetFrame } from "./TaskWidgetFrame";

export function SpeakTimedTaskWidget({
  task,
  previewState,
}: {
  task: SpeakTimedTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? [] : task.answers[previewState];
  const correctCount = isDefault ? 0 : answers.filter((answer) => answer.isCorrect).length;
  const answer = answers[0];

  return (
    <TaskWidgetFrame task={task} icon={<Mic2 size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Speaking focus">{task.grammarRule}</RuleCallout>

      <div style={{ marginBottom: 16 }}>
        <div
          style={{
            fontSize: 11,
            fontWeight: 800,
            color: "oklch(45% 0.07 240)",
            marginBottom: 8,
            textTransform: "uppercase",
            letterSpacing: "0.06em",
          }}
        >
          Target speaking cues
        </div>
        <div className="tw-target-chip-row">
          {task.targetWords.map((word) => (
            <span className="tw-target-chip used" key={word}>
              {word}
            </span>
          ))}
        </div>
      </div>

      {!isDefault && (
        <ResultBanner
          total={1}
          correct={correctCount}
          label={
            answer?.isCorrect
              ? "Speech fluent and target vocabulary used"
              : "Speech complete but missed target vocabulary"
          }
        />
      )}

      {isDefault ? (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            padding: "24px 18px",
            background: "linear-gradient(135deg, oklch(99% 0.005 240) 0%, oklch(96.5% 0.02 245) 100%)",
            border: "1.5px solid oklch(90% 0.02 240)",
            borderRadius: 18,
            textAlign: "center",
            boxShadow: "0 4px 16px rgba(80,110,180,0.03)",
          }}
        >
          <div
            style={{
              fontSize: 11,
              fontWeight: 800,
              color: "#0070C4",
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              marginBottom: 14,
            }}
          >
            Spoken Monologue prompt
          </div>
          <div
            style={{
              maxWidth: 520,
              borderRadius: 14,
              background: "white",
              border: "1px solid oklch(91% 0.015 240)",
              padding: "16px 20px",
              color: "var(--tw-navy)",
              fontSize: 15.5,
              lineHeight: 1.6,
              fontWeight: 700,
              boxShadow: "0 2px 10px rgba(0,0,0,0.02)",
              marginBottom: 20,
            }}
          >
            &ldquo;{task.prompt}&rdquo;
          </div>

          <div
            style={{
              position: "relative",
              width: 104,
              height: 104,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: 16,
            }}
          >
            {/* Visual Circular countdown representation */}
            <svg width="104" height="104" viewBox="0 0 104 104" style={{ position: "absolute", inset: 0 }}>
              <circle cx="52" cy="52" r="46" stroke="oklch(91% 0.02 245)" strokeWidth="6" fill="none" />
              <circle
                cx="52"
                cy="52"
                r="46"
                stroke="#0070C4"
                strokeWidth="6"
                fill="none"
                strokeLinecap="round"
                strokeDasharray={2 * Math.PI * 46}
                strokeDashoffset={2 * Math.PI * 46 * 0.15} // Mock timer countdown state
                transform="rotate(-90 52 52)"
                style={{ transition: "stroke-dashoffset 1s linear" }}
              />
            </svg>
            <button
              type="button"
              disabled
              aria-label="Speak recording button"
              title="Speak recording button"
              style={{
                width: 68,
                height: 68,
                borderRadius: "50%",
                background: "#0070C4",
                color: "white",
                border: "none",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 6px 18px rgba(0,112,196,0.32)",
                zIndex: 1,
                cursor: "default",
              }}
            >
              <Mic2 size={26} strokeWidth={2.4} />
            </button>
          </div>

          <div
            style={{
              fontSize: 14,
              fontWeight: 800,
              color: "var(--tw-navy)",
              marginBottom: 4,
            }}
          >
            Mild Timing Pressure
          </div>
          <div style={{ fontSize: 12.5, color: "var(--tw-ink-muted)", lineHeight: 1.45 }}>
            You will have {task.speakingDurationSeconds} seconds to formulate and record your answer.
          </div>
        </div>
      ) : (
        <div className="tw-compare-grid">
          <div className="tw-compare-card">
            <div className="tw-compare-label">
              <StatusDot ok={Boolean(answer?.isCorrect)} />
              Your Spoken Monologue
            </div>
            <div className="tw-compare-body" style={{ fontStyle: "italic" }}>
              &ldquo;{answer?.transcript}&rdquo;
            </div>
            <div
              style={{
                marginTop: 10,
                fontSize: 12,
                color: "var(--tw-ink-muted)",
                fontWeight: 700,
              }}
            >
              {answer?.durationSeconds}s recording • timed limit: {task.speakingDurationSeconds}s
            </div>
          </div>

          <div className="tw-compare-card sample">
            <div className="tw-compare-label">
              <Sparkles size={12} fill="currentColor" />
              Model Presentation
            </div>
            <div className="tw-compare-body" style={{ fontWeight: 500, lineHeight: 1.6 }}>
              {task.sampleResponse}
            </div>
          </div>
        </div>
      )}
    </TaskWidgetFrame>
  );
}
