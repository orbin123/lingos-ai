"use client";

import { extensionForMime, isVoiceRecordingSupported, useVoiceRecorder } from "@/lib/hooks/useVoiceRecorder";
import { tasksApi } from "@/lib/tasks-api";
import { Loader2, Mic2, RotateCcw, Sparkles, Square } from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { LiveTaskController } from "../source";
import { StatusDot, SubmitButton } from "./TaskWidgetFrame";

/**
 * Shared live recording machinery for the speaking (non-pronunciation) family.
 * Each speaking widget supplies its list of prompt slots (keyed `prompt_1..n`,
 * positionally compatible with the backend `build_speaking_eval_items`) and the
 * recorder handles record → transcribe → review and submits the canonical
 * `{ recordings: [{ item_id, transcript, audio_blob_url, duration_seconds,
 * attempt_number }], time_spent_seconds }` shape the speak evaluator reads.
 */
export interface SpeakingSlot {
  id: string;
  prompt: string;
  sampleResponse: string;
  context?: ReactNode;
}

/** Compact chat-bubble rendering of a dialogue/debate context for live mode. */
export function DialogueContextBlock({
  turns,
  learnerSpeaker = "learner",
}: {
  turns: { role: string; text: string; speaker: string }[];
  learnerSpeaker?: string;
}) {
  if (turns.length === 0) return null;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 12 }}>
      {turns.map((turn, index) => {
        const isLearner = turn.speaker === learnerSpeaker;
        return (
          <div
            key={index}
            style={{
              alignSelf: isLearner ? "flex-end" : "flex-start",
              maxWidth: "85%",
              background: isLearner ? "oklch(95% 0.04 240)" : "white",
              border: "1px solid var(--tw-border)",
              borderRadius: 12,
              padding: "8px 12px",
            }}
          >
            {turn.role && (
              <div style={{ fontSize: 10.5, fontWeight: 800, textTransform: "uppercase", color: "oklch(50% 0.07 240)", marginBottom: 3 }}>
                {turn.role}
              </div>
            )}
            <div style={{ fontSize: 13.5, color: "var(--tw-navy)", lineHeight: 1.5 }}>
              {turn.text || (isLearner ? "(your turn)" : "")}
            </div>
          </div>
        );
      })}
    </div>
  );
}

type SpeakRecording = {
  item_id: string;
  transcript: string;
  audio_blob_url: string;
  duration_seconds: number;
  attempt_number: number;
};

function recordingsFromAnswers(answers: Record<string, unknown>): Record<string, SpeakRecording> {
  const rows = Array.isArray(answers.recordings) ? answers.recordings : [];
  const out: Record<string, SpeakRecording> = {};
  for (const row of rows) {
    if (!row || typeof row !== "object") continue;
    const record = row as Partial<SpeakRecording>;
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

export function LiveSpeakingRecorder({
  live,
  slots,
  durationSeconds,
  showSampleAfterSubmit = true,
}: {
  live: LiveTaskController;
  slots: SpeakingSlot[];
  durationSeconds: number;
  showSampleAfterSubmit?: boolean;
}) {
  const interactive = !live.submitted;
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
  const allRecorded = slots.length > 0 && slots.every((slot) => recordingsById[slot.id]?.transcript?.trim());

  const saveRecording = (itemId: string, recording: SpeakRecording) => {
    const nextById = { ...recordingsById, [itemId]: recording };
    live.setAnswers({
      ...live.answers,
      recordings: slots.map((slot) => nextById[slot.id]).filter(Boolean),
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

  const submit = () => {
    live.onSubmit({
      recordings: slots.map((slot) => recordingsById[slot.id]).filter(Boolean),
      time_spent_seconds: Math.max(1, Math.round((Date.now() - startedAtRef.current) / 1000)),
    });
  };

  if (!interactive) {
    return (
      <>
        {slots.map((slot, index) => {
          const recording = recordingsById[slot.id];
          return (
            <div className="tw-compare-grid" key={slot.id}>
              <div className="tw-compare-card">
                <div className="tw-compare-label">
                  <StatusDot ok={Boolean(recording?.transcript)} />
                  Prompt {index + 1}
                </div>
                <div className="tw-compare-body" style={{ fontWeight: 700, marginBottom: 10 }}>
                  {slot.prompt}
                </div>
                <div className="tw-compare-body" style={{ fontStyle: "italic" }}>
                  &ldquo;{recording?.transcript || "No transcript submitted."}&rdquo;
                </div>
              </div>
              {showSampleAfterSubmit && slot.sampleResponse && (
                <div className="tw-compare-card sample">
                  <div className="tw-compare-label">
                    <Sparkles size={12} fill="currentColor" />
                    Model response
                  </div>
                  <div className="tw-compare-body" style={{ fontWeight: 500, lineHeight: 1.6 }}>
                    {slot.sampleResponse}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </>
    );
  }

  return (
    <>
      {!recordingSupported && (
        <div className="tw-card" style={{ background: "#fff4e5", borderColor: "#fdc283" }}>
          <div style={{ fontSize: 13.5, fontWeight: 800, color: "#7a4d00" }}>
            Microphone recording is not available in this browser.
          </div>
        </div>
      )}
      {slots.map((slot, index) => {
        const recording = recordingsById[slot.id];
        const isRecording = activeItemId === slot.id && recorder.state === "recording";
        const isTranscribing = transcribingItemId === slot.id;
        return (
          <div className="tw-card" key={slot.id}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">{slot.prompt}</div>
            </div>
            {slot.context}

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
                  onClick={() => startRecording(slot.id)}
                >
                  {recording ? <RotateCcw size={14} /> : <Mic2 size={14} />}
                  {recording ? "Record again" : "Record"}
                </button>
              )}
              <div className="tw-write-helper" style={{ margin: 0 }}>
                {isRecording
                  ? `${Math.round(recorder.elapsedMs / 1000)}s recorded`
                  : `Target: about ${durationSeconds}s`}
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
        <span>
          {slots.filter((slot) => recordingsById[slot.id]?.transcript?.trim()).length} of {slots.length} prompts transcribed.
        </span>
      </div>
      <SubmitButton disabled={!allRecorded || busy} onClick={submit} />
    </>
  );
}
