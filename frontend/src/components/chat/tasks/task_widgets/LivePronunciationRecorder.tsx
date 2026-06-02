"use client";

import { blobToWav } from "@/lib/audio-utils";
import { isVoiceRecordingSupported, useVoiceRecorder } from "@/lib/hooks/useVoiceRecorder";
import { sessionsApi, type PronunciationResult } from "@/lib/sessions-api";
import { Loader2, Mic2, RotateCcw, Square } from "lucide-react";
import { useEffect, useState } from "react";
import type { LiveTaskController } from "../source";
import { SubmitButton } from "./TaskWidgetFrame";

/**
 * Live recorder for the speaking-pronunciation family (read_aloud, listen_shadow).
 * Records the learner reading the reference text, runs Azure pronunciation
 * scoring (`POST /api/sessions/pronunciation-score`), and submits the
 * `{ pronunciation, transcript }` shape the speak evaluator routes to the Azure
 * branch. Scores are not shown here; the pronunciation assessment widget shows them.
 */
function pronunciationFromAnswers(answers: Record<string, unknown>): PronunciationResult | null {
  const p = answers.pronunciation;
  if (
    p &&
    typeof p === "object" &&
    typeof (p as { overall_score?: unknown }).overall_score === "number"
  ) {
    return p as PronunciationResult;
  }
  return null;
}

export function LivePronunciationRecorder({
  live,
  referenceText,
  durationSeconds,
}: {
  live: LiveTaskController;
  referenceText: string;
  durationSeconds: number;
}) {
  const interactive = !live.submitted;
  const recorder = useVoiceRecorder();
  const [recordingSupported, setRecordingSupported] = useState(true);
  const [scoring, setScoring] = useState(false);
  const pronunciation = pronunciationFromAnswers(live.answers);

  useEffect(() => {
    setRecordingSupported(isVoiceRecordingSupported());
  }, []);

  const isRecording = recorder.state === "recording";
  const busy = isRecording || recorder.state === "paused" || scoring;

  const start = async () => {
    if (!recordingSupported || busy || live.submitted) return;
    await recorder.start();
  };

  const stopAndScore = async () => {
    const blob = await recorder.stop();
    if (!blob || blob.size === 0) {
      recorder.setError("No audio was captured. Please record again.");
      return;
    }
    setScoring(true);
    recorder.setTranscribing(true);
    try {
      const wavBlob = await blobToWav(blob);
      const result = await sessionsApi.scorePronunciation(wavBlob, referenceText);
      live.setAnswers({ ...live.answers, pronunciation: result, transcript: referenceText });
    } catch {
      recorder.setError("Pronunciation scoring failed. Please record again.");
    } finally {
      setScoring(false);
      recorder.setTranscribing(false);
    }
  };

  const submit = () => {
    if (!pronunciation) return;
    live.onSubmit({ pronunciation, transcript: referenceText });
  };

  if (!interactive) {
    return (
      <div className="tw-write-helper" style={{ marginTop: 12, fontWeight: 700 }}>
        The audio has been submitted.
      </div>
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
      <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", marginTop: 8 }}>
        {isRecording ? (
          <button
            type="button"
            className="tw-submit-btn"
            onClick={stopAndScore}
            style={{ background: "#cf2e2e", boxShadow: "0 6px 16px rgba(207,46,46,0.24)" }}
          >
            <Square size={14} fill="currentColor" />
            Stop &amp; score
          </button>
        ) : (
          <button
            type="button"
            className="tw-submit-btn"
            disabled={!recordingSupported || busy}
            onClick={start}
          >
            {pronunciation ? <RotateCcw size={14} /> : <Mic2 size={14} />}
            {pronunciation ? "Record again" : "Record"}
          </button>
        )}
        <div className="tw-write-helper" style={{ margin: 0 }}>
          {isRecording ? `${Math.round(recorder.elapsedMs / 1000)}s recorded` : `Speak clearly · about ${durationSeconds}s`}
        </div>
        {scoring && (
          <div className="tw-write-helper" style={{ margin: 0, display: "inline-flex", alignItems: "center", gap: 6 }}>
            <Loader2 size={13} className="animate-spin" />
            Scoring pronunciation
          </div>
        )}
      </div>
      {recorder.errorMessage && (
        <div className="tw-fb-explain" style={{ color: "var(--tw-red)", fontWeight: 800 }}>
          {recorder.errorMessage}
        </div>
      )}
      <SubmitButton disabled={!pronunciation || busy} onClick={submit} />
    </>
  );
}
