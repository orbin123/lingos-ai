"use client";

import { AlertCircle, Mic2 } from "lucide-react";
import { useState } from "react";
import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, SpeakPicDescTask } from "../source";
import { LiveSpeakingRecorder } from "./LiveSpeakingRecorder";
import {
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

function resolveImageUrl(imageUrl?: string | null): string | null {
  if (!imageUrl) return null;
  if (/^(https?:|blob:|data:)/i.test(imageUrl)) return imageUrl;
  if (imageUrl.startsWith("/")) {
    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return `${apiBase.replace(/\/$/, "")}${imageUrl}`;
  }
  return imageUrl;
}

function PicturePanel({
  imageUrl,
  imageAlt,
  imageError,
}: {
  imageUrl: string | null;
  imageAlt: string;
  imageError?: string;
}) {
  const resolvedUrl = resolveImageUrl(imageUrl);
  const [loadFailed, setLoadFailed] = useState(false);
  const showError = Boolean(imageError) || !resolvedUrl || loadFailed;

  return (
    <div
      style={{
        width: "100%",
        aspectRatio: "16 / 9",
        minHeight: 160,
        borderRadius: 14,
        marginBottom: 12,
        border: showError ? "1px solid oklch(85% 0.08 25)" : "1px solid var(--tw-border)",
        backgroundColor: showError ? "oklch(97% 0.03 25)" : "oklch(97% 0.02 245)",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
      role={showError ? undefined : "img"}
      aria-label={showError ? undefined : imageAlt || "Picture to describe"}
    >
      {showError ? (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 8,
            padding: "16px 20px",
            textAlign: "center",
          }}
        >
          <AlertCircle size={28} strokeWidth={2} color="oklch(55% 0.14 25)" />
          <div style={{ fontSize: 13.5, fontWeight: 800, color: "oklch(45% 0.12 25)" }}>
            Picture could not be loaded
          </div>
          <div style={{ fontSize: 12.5, color: "var(--tw-ink-muted)", lineHeight: 1.45, maxWidth: 320 }}>
            {imageError || "The scene image is unavailable. You can still record your description using the prompt below."}
          </div>
        </div>
      ) : (
        <img
          src={resolvedUrl!}
          alt={imageAlt || "Picture to describe"}
          onError={() => setLoadFailed(true)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            display: "block",
          }}
        />
      )}
    </div>
  );
}

export function SpeakPicDescTaskWidget({
  task,
  previewState,
  live,
}: {
  task: SpeakPicDescTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  const picturePanel = (
    <PicturePanel
      imageUrl={task.imageUrl}
      imageAlt={task.imageAlt}
      imageError={task.imageError}
    />
  );

  if (live) {
    return (
      <TaskWidgetFrame task={task} icon={<Mic2 size={18} strokeWidth={2.5} />}>
        <RuleCallout label="Speaking pattern">{task.grammarRule}</RuleCallout>
        <LiveSpeakingRecorder
          live={live}
          durationSeconds={task.speakingDurationSeconds}
          slots={[
            {
              id: "prompt_1",
              prompt: task.prompts?.[0] || "Describe what you see in the picture using full sentences.",
              sampleResponse: task.sampleResponses?.[0] || "",
              context: picturePanel,
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
    <TaskWidgetFrame task={task} icon={<Mic2 size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Speaking pattern">{task.grammarRule}</RuleCallout>
      {picturePanel}

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
