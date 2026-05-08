"use client";

import { useEffect, useRef, useState } from "react";
import { tasksApi } from "@/lib/tasks-api";

// ─── Types ────────────────────────────────────────────────────────────

type RecordingState =
  | "idle"
  | "requesting_permission"
  | "recording"
  | "uploading"
  | "transcript_ready"
  | "error";

export interface SpeakAndRecordResult {
  transcript: string;
  duration_seconds: number;
  audio_url: string;
}

interface Props {
  /** Max seconds before recording auto-stops. */
  maxDurationSeconds: number;
  /** Minimum sentences required (shown as hint). */
  minimumSentences: number;
  /** Called once the learner has reviewed the transcript and clicks submit. */
  onSubmit: (result: SpeakAndRecordResult) => void;
  isPending: boolean;
}

// ─── Helpers ─────────────────────────────────────────────────────────

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

// ─── Component ───────────────────────────────────────────────────────

/**
 * Generic audio-recording component for generated speaking tasks.
 *
 * Flow:
 *   idle → requesting_permission → recording → uploading → transcript_ready
 *
 * Reusable for any speak_* task type — the parent passes the max duration
 * and minimum sentence count; the rest of the task-specific UI lives in
 * the parent component (e.g. GeneratedSpeakWithTense).
 */
export function SpeakAndRecord({
  maxDurationSeconds,
  minimumSentences,
  onSubmit,
  isPending,
}: Props) {
  const [state, setState] = useState<RecordingState>("idle");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [elapsed, setElapsed] = useState(0);
  const [transcript, setTranscript] = useState<string>("");
  const [audioUrl, setAudioUrl] = useState<string>("");
  const [recordingDuration, setRecordingDuration] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<BlobEvent["data"][]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimeRef = useRef<number>(0);

  // Clear timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // Auto-stop when max duration is reached
  useEffect(() => {
    if (elapsed >= maxDurationSeconds && state === "recording") {
      stopRecording();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [elapsed, maxDurationSeconds, state]);

  async function startRecording() {
    setState("requesting_permission");
    setErrorMessage("");
    audioChunksRef.current = [];

    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      setState("error");
      setErrorMessage(
        "Microphone access was denied. Please allow microphone access and try again."
      );
      return;
    }

    // Pick the best supported MIME type for cross-browser compat.
    const mimeType = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus",
      "audio/ogg",
      "audio/mp4",
    ].find((m) => MediaRecorder.isTypeSupported(m)) ?? "";

    const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});
    mediaRecorderRef.current = recorder;

    recorder.ondataavailable = (e: BlobEvent) => {
      if (e.data.size > 0) audioChunksRef.current.push(e.data);
    };

    recorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      const duration = Math.round((Date.now() - startTimeRef.current) / 1000);
      setRecordingDuration(duration);

      const mimeUsed = recorder.mimeType || "audio/webm";
      const blob = new Blob(audioChunksRef.current, { type: mimeUsed });
      const ext = mimeUsed.includes("ogg") ? ".ogg" : mimeUsed.includes("mp4") ? ".mp4" : ".webm";

      setState("uploading");
      try {
        const result = await tasksApi.transcribeAudio(blob, `recording${ext}`);
        setTranscript(result.transcript);
        setAudioUrl(result.audio_url);
        setRecordingDuration(duration);
        setState("transcript_ready");
      } catch {
        setState("error");
        setErrorMessage(
          "Transcription failed. Please check your connection and try recording again."
        );
      }
    };

    startTimeRef.current = Date.now();
    setElapsed(0);
    recorder.start(250); // collect chunks every 250 ms
    setState("recording");

    timerRef.current = setInterval(() => {
      setElapsed((prev) => prev + 1);
    }, 1000);
  }

  function stopRecording() {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
    }
  }

  function handleSubmit() {
    onSubmit({
      transcript,
      duration_seconds: recordingDuration,
      audio_url: audioUrl,
    });
  }

  function reset() {
    setState("idle");
    setElapsed(0);
    setTranscript("");
    setAudioUrl("");
    setErrorMessage("");
    setRecordingDuration(0);
    audioChunksRef.current = [];
  }

  // ─── Render ─────────────────────────────────────────────────────

  if (state === "error") {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <p
          style={{
            fontSize: 13,
            color: "oklch(45% 0.18 20)",
            background: "oklch(97% 0.02 20)",
            border: "1px solid oklch(88% 0.06 20)",
            borderRadius: 10,
            padding: "12px 16px",
          }}
        >
          {errorMessage}
        </p>
        <button
          type="button"
          onClick={reset}
          style={secondaryBtnStyle}
        >
          Try again
        </button>
      </div>
    );
  }

  if (state === "transcript_ready") {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {/* Transcript preview */}
        <div
          style={{
            background: "rgba(255,255,255,0.9)",
            borderRadius: 12,
            border: "1px solid rgba(80,120,200,0.15)",
            padding: "16px 18px",
          }}
        >
          <p
            style={{
              fontSize: 11,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              color: "oklch(50% 0.14 245)",
              marginBottom: 8,
            }}
          >
            Your transcript ({recordingDuration}s recorded)
          </p>
          <p
            style={{
              fontSize: 14,
              lineHeight: 1.65,
              color: "oklch(22% 0.08 240)",
              margin: 0,
              whiteSpace: "pre-wrap",
            }}
          >
            {transcript || "(no speech detected)"}
          </p>
        </div>

        {/* Re-record option */}
        <button type="button" onClick={reset} style={secondaryBtnStyle}>
          Re-record
        </button>

        {/* Submit */}
        <button
          type="button"
          disabled={!transcript.trim() || isPending}
          onClick={handleSubmit}
          style={{
            ...primaryBtnStyle,
            background:
              transcript.trim() && !isPending
                ? "oklch(52% 0.18 240)"
                : "oklch(85% 0.03 240)",
            color:
              transcript.trim() && !isPending
                ? "white"
                : "oklch(55% 0.05 240)",
            cursor:
              transcript.trim() && !isPending ? "pointer" : "not-allowed",
            opacity: isPending ? 0.6 : 1,
          }}
        >
          {isPending ? "Submitting…" : "Submit recording"}
        </button>
      </div>
    );
  }

  if (state === "uploading") {
    return (
      <p
        style={{
          fontSize: 14,
          color: "oklch(40% 0.1 245)",
          textAlign: "center",
          padding: "20px 0",
        }}
      >
        Transcribing your recording…
      </p>
    );
  }

  // idle / requesting_permission / recording
  const isRecording = state === "recording";
  const timeLeft = Math.max(0, maxDurationSeconds - elapsed);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, alignItems: "center" }}>
      {/* Timer */}
      <div
        style={{
          fontSize: 28,
          fontWeight: 800,
          color: isRecording ? "oklch(45% 0.18 20)" : "oklch(40% 0.07 240)",
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {isRecording
          ? `${formatTime(elapsed)} / ${formatTime(maxDurationSeconds)}`
          : formatTime(maxDurationSeconds)}
      </div>

      {isRecording && (
        <p style={{ fontSize: 12, color: "oklch(45% 0.07 240)", margin: 0 }}>
          {timeLeft > 0
            ? `${timeLeft}s remaining`
            : "Maximum time reached — stopping…"}
        </p>
      )}

      {/* Mic / stop button */}
      <button
        type="button"
        disabled={state === "requesting_permission"}
        onClick={isRecording ? stopRecording : startRecording}
        style={{
          width: 80,
          height: 80,
          borderRadius: "50%",
          border: "none",
          background: isRecording
            ? "oklch(52% 0.22 20)"
            : "oklch(52% 0.18 240)",
          color: "white",
          fontSize: 32,
          cursor: state === "requesting_permission" ? "wait" : "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: isRecording
            ? "0 0 0 6px oklch(52% 0.22 20 / 0.25)"
            : "0 4px 14px oklch(52% 0.18 240 / 0.35)",
          transition: "all 0.2s ease",
        }}
        aria-label={isRecording ? "Stop recording" : "Start recording"}
      >
        {isRecording ? "⏹" : "🎙"}
      </button>

      <p
        style={{
          fontSize: 12,
          color: "oklch(50% 0.07 240)",
          textAlign: "center",
          margin: 0,
        }}
      >
        {state === "requesting_permission"
          ? "Requesting microphone access…"
          : isRecording
          ? "Recording — click to stop when done"
          : `Click to start. Aim for ${minimumSentences}+ sentences.`}
      </p>
    </div>
  );
}

// ─── Shared button styles ─────────────────────────────────────────────

const primaryBtnStyle: React.CSSProperties = {
  width: "100%",
  padding: "14px 0",
  borderRadius: 12,
  border: "none",
  fontSize: 15,
  fontWeight: 700,
  transition: "all 0.2s ease",
};

const secondaryBtnStyle: React.CSSProperties = {
  width: "100%",
  padding: "10px 0",
  borderRadius: 10,
  border: "1px solid rgba(80,120,200,0.2)",
  background: "rgba(255,255,255,0.8)",
  color: "oklch(40% 0.1 245)",
  fontSize: 13,
  fontWeight: 600,
  cursor: "pointer",
};
