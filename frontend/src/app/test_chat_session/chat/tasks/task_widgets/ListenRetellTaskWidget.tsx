"use client";

import { FileText, Mic2, Volume2 } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { ListenRetellTask } from "../source";
import { ResultBanner, RuleCallout, TaskWidgetFrame, StatusDot } from "./TaskWidgetFrame";

export function ListenRetellTaskWidget({
  task,
  previewState,
}: {
  task: ListenRetellTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answer = isDefault ? null : task.answers[previewState][0];
  const correctCount = answer?.isCorrect ? 1 : 0;
  const isWritten = task.responseMode === "written";
  const answerText = answer?.text ?? answer?.transcript ?? "";

  return (
    <TaskWidgetFrame task={task} icon={<Volume2 size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Retelling focus">{task.grammarRule}</RuleCallout>

      <div style={{ marginBottom: 14 }}>
        <div style={{ fontSize: 12, fontWeight: 800, color: "oklch(45% 0.07 240)", marginBottom: 6, textTransform: "uppercase" }}>
          Target phrases
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

      <div 
        style={{
          border: "1.5px solid oklch(90% 0.02 240)",
          borderRadius: 18,
          background: "oklch(97% 0.015 245)",
          padding: 16,
          display: "flex",
          alignItems: "center",
          gap: 14,
          marginBottom: 16,
          boxShadow: "inset 0 2px 8px rgba(80,110,180,0.03)"
        }}
      >
        <button
          type="button"
          disabled
          aria-label="Play source audio"
          title="Play source audio"
          style={{
            width: 44,
            height: 44,
            borderRadius: "50%",
            background: "#0070C4",
            color: "white",
            border: "none",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 4px 14px rgba(0,112,196,0.3)",
            cursor: "default",
            flexShrink: 0
          }}
        >
          <Volume2 size={20} strokeWidth={2.5} />
        </button>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13.5, fontWeight: 800, color: "oklch(20% 0.09 245)" }}>
            {task.audioGenre} ({task.audioDurationSeconds}s)
          </div>
          <div style={{ display: "flex", gap: 3, alignItems: "center", marginTop: 4, height: 16 }}>
            {/* Visual audio wave-like representation */}
            {[2, 5, 8, 3, 6, 9, 4, 7, 2, 5, 8, 3, 6, 9, 4, 7, 2, 5, 8, 3, 6, 9].map((height, idx) => (
              <span
                key={idx}
                style={{
                  width: 2.5,
                  height: `${height * 1.5 + 4}px`,
                  borderRadius: 1,
                  background: "#0070C4",
                  opacity: 0.6 + (idx % 4) * 0.1
                }}
              />
            ))}
          </div>
        </div>
      </div>

      {!isDefault && (
        <ResultBanner
          total={1}
          correct={correctCount}
          label={answer?.isCorrect ? "Summary clear and accurate" : "Summary has one changed detail"}
        />
      )}

      {isDefault && isWritten ? (
        <div
          style={{
            border: "1.5px solid oklch(88% 0.025 240)",
            borderRadius: 18,
            background: "white",
            padding: 14,
            minHeight: 132,
            marginBottom: 0,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: 12,
              fontWeight: 900,
              color: "#0070C4",
              textTransform: "uppercase",
              marginBottom: 10,
            }}
          >
            <FileText size={14} strokeWidth={2.5} />
            Written retell
          </div>
          <div
            style={{
              minHeight: 82,
              borderRadius: 14,
              border: "1.5px dashed oklch(86% 0.03 240)",
              background: "oklch(99% 0.005 240)",
              color: "oklch(55% 0.06 240)",
              padding: "13px 14px",
              fontSize: 14,
              lineHeight: 1.6,
            }}
          >
            Write the key points from the conversation in your own words.
          </div>
        </div>
      ) : isDefault ? (
        <div className="tw-mic-stage" style={{ marginBottom: 0 }}>
          <div className="tw-mic-prompt">Ready to retell</div>
          <div className="tw-mic-button-wrap">
            <button
              type="button"
              disabled
              aria-label="Preview recording button"
              title="Preview recording button"
              className="tw-mic-button"
              style={{ cursor: "default" }}
            >
              <Mic2 size={28} strokeWidth={2.5} />
            </button>
            <span className="tw-mic-ring" />
          </div>
          <div className="tw-mic-instruction">Listen and summarize the story in your own words</div>
          <div className="tw-mic-sub">Record up to {task.audioDurationSeconds} seconds.</div>
        </div>
      ) : (
        <div className="tw-compare-grid">
          <div className="tw-compare-card">
            <div className="tw-compare-label">
              <StatusDot ok={Boolean(answer?.isCorrect)} />
              {isWritten ? "Your Written Retell" : "Your Oral Summary"}
            </div>
            <div className="tw-compare-body" style={{ fontStyle: "italic" }}>
              &ldquo;{answerText}&rdquo;
            </div>
            {answer?.durationSeconds ? (
              <div style={{ marginTop: 8, fontSize: 12, color: "var(--tw-ink-muted)", fontWeight: 700 }}>
                {answer.durationSeconds}s recording
              </div>
            ) : null}
          </div>
          <div className="tw-compare-card sample">
            <div className="tw-compare-label">
              <Volume2 size={12} />
              Reference retell
            </div>
            <div className="tw-compare-body">{task.passageToRetell}</div>
          </div>
        </div>
      )}
    </TaskWidgetFrame>
  );
}
