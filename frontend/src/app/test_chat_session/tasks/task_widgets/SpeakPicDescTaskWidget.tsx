"use client";

import { Mic2, Image as ImageIcon } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { SpeakPicDescTask } from "../source";
import {
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function SpeakPicDescTaskWidget({
  task,
  previewState,
}: {
  task: SpeakPicDescTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? [] : task.answers[previewState];
  const correctCount = isDefault ? 0 : answers.filter((answer) => answer.isCorrect).length;
  const answer = answers[0];

  return (
    <TaskWidgetFrame task={task} icon={<Mic2 size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Speaking pattern">{task.grammarRule}</RuleCallout>
      
      <div style={{
        width: "100%",
        minHeight: 180,
        backgroundColor: "oklch(97% 0.02 245)",
        borderRadius: 12,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        color: "var(--tw-ink-muted)",
        marginBottom: 16,
        border: "1px solid var(--tw-border-light)",
        overflow: "hidden",
      }}>
        {task.imageUrl ? (
          <div
            role="img"
            aria-label={task.imageAlt}
            style={{
              width: "100%",
              aspectRatio: "2 / 1",
              minHeight: 180,
              backgroundImage: `url("${task.imageUrl}")`,
              backgroundPosition: "center",
              backgroundRepeat: "no-repeat",
              backgroundSize: "cover",
            }}
          />
        ) : (
          <>
            <ImageIcon size={32} style={{ marginBottom: 8, opacity: 0.5 }} />
            <div style={{ fontSize: 13, fontWeight: 500 }}>
              {task.imageAlt || "Image placeholder"}
            </div>
          </>
        )}
      </div>

      {!isDefault && (
        <ResultBanner
          total={1}
          correct={correctCount}
          label={`${correctCount} of 1 recording clear`}
        />
      )}
      
      <div className="tw-card" style={{ marginBottom: 0 }}>
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
                  Record up to {task.speakingDurationSeconds} seconds describing the picture.
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
                <StatusDot ok={answer?.isCorrect} />
                Transcript
              </div>
              <div className="tw-compare-body">{answer?.transcript}</div>
              <div style={{ marginTop: 8, fontSize: 12, color: "var(--tw-ink-muted)", fontWeight: 700 }}>
                {answer?.durationSeconds}s recording
              </div>
            </div>
          </div>
        )}
      </div>
    </TaskWidgetFrame>
  );
}
