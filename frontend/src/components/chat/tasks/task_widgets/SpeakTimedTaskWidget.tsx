"use client";

import { extensionForMime, isVoiceRecordingSupported, useVoiceRecorder } from "@/lib/hooks/useVoiceRecorder";
import { tasksApi } from "@/lib/tasks-api";
import { Loader2, Mic2, RotateCcw, Sparkles, Square } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, SpeakTimedTask } from "../source";
import {
  ResultBanner,
  RuleCallout,
  StatusDot,
  SubmitButton,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

type TimedPrompt = {
  id: string;
  prompt: string;
  sampleResponse: string;
};

type TimedRecording = {
  item_id: string;
  transcript: string;
  audio_blob_url: string;
  duration_seconds: number;
  attempt_number: number;
};

export function SpeakTimedTaskWidget({
  task,
  previewState,
  live,
}: {
  task: SpeakTimedTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  if (live) {
    return <LiveSpeakTimed task={task} live={live} />;
  }
  return <PreviewSpeakTimed task={task} previewState={previewState} />;
}

function LiveSpeakTimed({ task, live }: { task: SpeakTimedTask; live: LiveTaskController }) {
  const interactive = !live.submitted;
  const prompts = useMemo(() => timedPrompts(task), [task]);
  const recordingsById = useMemo(() => recordingsFromAnswers(live.answers), [live.answers]);
  const recorder = useVoiceRecorder();
  const startedAtRef = useRef(Date.now());
  const recordingStartedAtRef = useRef(Date.now());
  const [activeItemId, setActiveItemId] = useState<string | null>(null);
  const [transcribingItemId, setTranscribingItemId] = useState<string | null>(null);
  const [recordingSupported, setRecordingSupported] = useState(true);

  useEffect(() => {
    setRecordingSupported(isVoiceRecordingSupported());
  }, []);

  useEffect(() => {
    if (recorder.state === "error") setActiveItemId(null);
  }, [recorder.state]);

  const busy = recorder.state === "recording" || recorder.state === "paused" || recorder.state === "transcribing";
  const allRecorded = prompts.length > 0 && prompts.every((prompt) => recordingsById[prompt.id]?.transcript?.trim());

  const saveRecording = (itemId: string, recording: TimedRecording) => {
    const nextById = { ...recordingsById, [itemId]: recording };
    live.setAnswers({
      ...live.answers,
      recordings: prompts.map((prompt) => nextById[prompt.id]).filter(Boolean),
    });
  };

  const startRecording = async (itemId: string) => {
    if (!recordingSupported || busy || live.submitted) return;
    setActiveItemId(itemId);
    recordingStartedAtRef.current = Date.now();
    await recorder.start();
  };

  const stopRecording = async () => {
    const itemId = activeItemId;
    if (!itemId) return;
    const startedAt = recordingStartedAtRef.current || Date.now();
    const blob = await recorder.stop();
    setActiveItemId(null);

    if (!blob || blob.size === 0) {
      recorder.setError("No audio was captured. Please record that prompt again.");
      return;
    }

    setTranscribingItemId(itemId);
    recorder.setTranscribing(true);
    let completed = false;
    try {
      const ext = extensionForMime(blob.type || recorder.mimeType || "audio/webm");
      const result = await tasksApi.transcribeAudio(blob, `speak-${itemId}${ext}`);
      const transcript = result.transcript.trim();
      if (!transcript) {
        throw new Error("empty transcript");
      }
      saveRecording(itemId, {
        item_id: itemId,
        transcript,
        audio_blob_url: result.audio_url,
        duration_seconds: Math.max(1, Math.round((Date.now() - startedAt) / 1000)),
        attempt_number: (recordingsById[itemId]?.attempt_number ?? 0) + 1,
      });
      completed = true;
    } catch {
      recorder.setError("Transcription failed. Please record that prompt again.");
    } finally {
      setTranscribingItemId(null);
      if (completed) recorder.setTranscribing(false);
    }
  };

  const submitRecordings = () => {
    live.onSubmit({
      recordings: prompts.map((prompt) => recordingsById[prompt.id]).filter(Boolean),
      time_spent_seconds: Math.max(1, Math.round((Date.now() - startedAtRef.current) / 1000)),
    });
  };

  return (
    <TaskWidgetFrame task={task} icon={<Mic2 size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Speaking focus">{task.grammarRule}</RuleCallout>

      {interactive ? (
        <>
          {!recordingSupported && (
            <div className="tw-card" style={{ background: "#fff4e5", borderColor: "#fdc283" }}>
              <div style={{ fontSize: 13.5, fontWeight: 800, color: "#7a4d00" }}>
                Microphone recording is not available in this browser.
              </div>
            </div>
          )}
          {prompts.map((prompt, index) => {
            const recording = recordingsById[prompt.id];
            const isRecording = activeItemId === prompt.id && recorder.state === "recording";
            const isTranscribing = transcribingItemId === prompt.id;
            return (
              <div className="tw-card" key={prompt.id}>
                <div className="tw-q-number-row">
                  <div className="tw-q-number-badge">{index + 1}</div>
                  <div className="tw-q-stem">{prompt.prompt}</div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
                  {isRecording ? (
                    <button
                      type="button"
                      className="tw-submit-btn"
                      onClick={stopRecording}
                      style={{ background: "#cf2e2e", boxShadow: "0 6px 16px rgba(207,46,46,0.24)" }}
                    >
                      <Square size={14} fill="currentColor" />
                      Stop recording
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="tw-submit-btn"
                      disabled={!recordingSupported || busy}
                      onClick={() => startRecording(prompt.id)}
                    >
                      {recording ? <RotateCcw size={14} /> : <Mic2 size={14} />}
                      {recording ? "Record again" : "Record"}
                    </button>
                  )}
                  <div className="tw-write-helper" style={{ margin: 0 }}>
                    {isRecording
                      ? `${Math.round(recorder.elapsedMs / 1000)}s recorded`
                      : `Target: about ${task.speakingDurationSeconds}s`}
                  </div>
                  {isTranscribing && (
                    <div className="tw-write-helper" style={{ margin: 0, display: "inline-flex", alignItems: "center", gap: 6 }}>
                      <Loader2 size={13} className="animate-spin" />
                      Transcribing
                    </div>
                  )}
                </div>

                {recording && (
                  <div className="tw-compare-card" style={{ marginTop: 12 }}>
                    <div className="tw-compare-label">
                      <StatusDot ok />
                      Transcript
                    </div>
                    <div className="tw-compare-body">&ldquo;{recording.transcript}&rdquo;</div>
                    <div style={{ marginTop: 8, fontSize: 12, color: "var(--tw-ink-muted)", fontWeight: 700 }}>
                      {recording.duration_seconds}s recording
                    </div>
                  </div>
                )}
              </div>
            );
          })}
          {recorder.errorMessage && (
            <div className="tw-fb-explain" style={{ color: "var(--tw-red)", fontWeight: 800 }}>
              {recorder.errorMessage}
            </div>
          )}
          <div className="tw-write-helper">
            <span>{prompts.filter((prompt) => recordingsById[prompt.id]?.transcript?.trim()).length} of {prompts.length} prompts transcribed.</span>
          </div>
          <SubmitButton disabled={!allRecorded || busy} onClick={submitRecordings} />
        </>
      ) : (
        <>
          {prompts.map((prompt, index) => {
            const recording = recordingsById[prompt.id];
            return (
              <div className="tw-compare-grid" key={prompt.id}>
                <div className="tw-compare-card">
                  <div className="tw-compare-label">
                    <StatusDot ok={Boolean(recording?.transcript)} />
                    Prompt {index + 1}
                  </div>
                  <div className="tw-compare-body" style={{ fontWeight: 700, marginBottom: 10 }}>
                    {prompt.prompt}
                  </div>
                  <div className="tw-compare-body" style={{ fontStyle: "italic" }}>
                    &ldquo;{recording?.transcript || "No transcript submitted."}&rdquo;
                  </div>
                </div>
                <div className="tw-compare-card sample">
                  <div className="tw-compare-label">
                    <Sparkles size={12} fill="currentColor" />
                    Model response
                  </div>
                  <div className="tw-compare-body" style={{ fontWeight: 500, lineHeight: 1.6 }}>
                    {prompt.sampleResponse}
                  </div>
                </div>
              </div>
            );
          })}
        </>
      )}
    </TaskWidgetFrame>
  );
}

function timedPrompts(task: SpeakTimedTask): TimedPrompt[] {
  const promptTexts = (task.prompts && task.prompts.length > 0)
    ? task.prompts
    : task.prompt
      ? [task.prompt]
      : [];
  const sampleTexts = (task.sampleResponses && task.sampleResponses.length > 0)
    ? task.sampleResponses
    : task.sampleResponse
      ? [task.sampleResponse]
      : [];
  return promptTexts.map((prompt, index) => ({
    id: `prompt_${index + 1}`,
    prompt,
    sampleResponse: sampleTexts[index] || "",
  }));
}

function recordingsFromAnswers(answers: Record<string, unknown>): Record<string, TimedRecording> {
  const rows = Array.isArray(answers.recordings) ? answers.recordings : [];
  const out: Record<string, TimedRecording> = {};
  for (const row of rows) {
    if (!row || typeof row !== "object") continue;
    const record = row as Partial<TimedRecording>;
    if (!record.item_id || !record.transcript) continue;
    out[record.item_id] = {
      item_id: String(record.item_id),
      transcript: String(record.transcript),
      audio_blob_url: String(record.audio_blob_url ?? ""),
      duration_seconds: Number(record.duration_seconds) || 0,
      attempt_number: Number(record.attempt_number) || 1,
    };
  }
  return out;
}

function PreviewSpeakTimed({
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
  const prompts = timedPrompts(task);
  const firstPrompt = prompts[0];

  return (
    <TaskWidgetFrame task={task} icon={<Mic2 size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Speaking focus">{task.grammarRule}</RuleCallout>

      {!isDefault && (
        <ResultBanner
          total={Math.max(1, prompts.length)}
          correct={correctCount}
          label={
            answer?.isCorrect
              ? "Speech fluent and clear"
              : "Speech complete but needs improvement"
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
          }}
        >
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
              marginBottom: 16,
            }}
          >
            &ldquo;{firstPrompt?.prompt || "Speaking prompt is missing."}&rdquo;
          </div>
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
              cursor: "default",
            }}
          >
            <Mic2 size={26} strokeWidth={2.4} />
          </button>
          <div style={{ fontSize: 12.5, color: "var(--tw-ink-muted)", marginTop: 12 }}>
            You will have {task.speakingDurationSeconds} seconds to record your answer.
          </div>
        </div>
      ) : (
        <div className="tw-compare-grid">
          <div className="tw-compare-card">
            <div className="tw-compare-label">
              <StatusDot ok={Boolean(answer?.isCorrect)} />
              Your spoken monologue
            </div>
            <div className="tw-compare-body" style={{ fontStyle: "italic" }}>
              &ldquo;{answer?.transcript}&rdquo;
            </div>
            <div style={{ marginTop: 10, fontSize: 12, color: "var(--tw-ink-muted)", fontWeight: 700 }}>
              {answer?.durationSeconds}s recording • timed limit: {task.speakingDurationSeconds}s
            </div>
          </div>
          <div className="tw-compare-card sample">
            <div className="tw-compare-label">
              <Sparkles size={12} fill="currentColor" />
              Model presentation
            </div>
            <div className="tw-compare-body" style={{ fontWeight: 500, lineHeight: 1.6 }}>
              {firstPrompt?.sampleResponse}
            </div>
          </div>
        </div>
      )}
    </TaskWidgetFrame>
  );
}
