"use client";

import { useEffect, useRef, useState } from "react";
import { tasksApi } from "@/lib/tasks-api";
import { TaskHeader, I } from "./shared";
import { formatDuration, resolveAudioUrl } from "./types";
import type { StoryboardPayload, StoryboardScene, WidgetProps } from "./types";

type Props = WidgetProps<StoryboardPayload>;

interface SceneTimestamp {
  scene_id: string;
  started_at_seconds: number;
  ended_at_seconds: number;
}

interface StoryboardAnswers {
  audio_blob_url?: string;
  transcript?: string;
  scene_timestamps?: SceneTimestamp[];
  duration_seconds?: number;
  time_spent_seconds?: number;
}

function pickMimeType(): string {
  if (typeof MediaRecorder === "undefined") return "";
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
    "audio/ogg",
    "audio/mp4",
  ];
  return candidates.find((t) => MediaRecorder.isTypeSupported(t)) ?? "";
}

function extensionForMime(mime: string): string {
  if (mime.includes("ogg")) return ".ogg";
  if (mime.includes("mp4")) return ".mp4";
  return ".webm";
}

export function StoryboardWidget({ payload, answers, setAnswers, state, onSubmit }: Props) {
  const submitted = state === "after";
  const scenes = payload.scenes ?? [];
  const cap = Math.max(1, payload.speaking_duration_seconds || 90);

  const startedAtRef = useRef(Date.now());
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const recordingStartedAtRef = useRef(0);
  const sceneStartedAtRef = useRef<Map<string, number>>(new Map());

  const [activeIdx, setActiveIdx] = useState(0);
  const [recording, setRecording] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | undefined>(
    (answers as StoryboardAnswers).audio_blob_url,
  );
  const [transcript, setTranscript] = useState<string | undefined>(
    (answers as StoryboardAnswers).transcript,
  );
  const [sceneTimestamps, setSceneTimestamps] = useState<SceneTimestamp[]>(
    (answers as StoryboardAnswers).scene_timestamps ?? [],
  );

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const publish = (
    nextAudioUrl: string,
    nextTranscript: string,
    nextTimestamps: SceneTimestamp[],
    duration: number,
  ) => {
    setAnswers({
      audio_blob_url: nextAudioUrl,
      transcript: nextTranscript,
      scene_timestamps: nextTimestamps,
      duration_seconds: duration,
      time_spent_seconds: Math.round((Date.now() - startedAtRef.current) / 1000),
    });
  };

  const stopRecording = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (recorderRef.current && recorderRef.current.state !== "inactive") {
      recorderRef.current.stop();
    }
  };

  const startRecording = async () => {
    if (submitted || recording || uploading) return;
    setError(null);
    chunksRef.current = [];
    sceneStartedAtRef.current.clear();
    if (scenes[0]) sceneStartedAtRef.current.set(scenes[0].scene_id, 0);
    setSceneTimestamps([]);
    setActiveIdx(0);
    setRecording(true);
    setElapsed(0);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mimeType = pickMimeType();
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});
      recorderRef.current = recorder;
      recorder.ondataavailable = (e: BlobEvent) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = async () => {
        const duration = Math.round((Date.now() - recordingStartedAtRef.current) / 1000);
        streamRef.current?.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
        // Close out the last scene with the final elapsed time.
        const finalTimestamps = closeOutTimestamps(duration);
        setRecording(false);
        setUploading(true);
        const usedMime = recorder.mimeType || mimeType || "audio/webm";
        const blob = new Blob(chunksRef.current, { type: usedMime });
        const ext = extensionForMime(usedMime);
        try {
          const result = await tasksApi.transcribeAudio(blob, `storyboard${ext}`);
          setAudioUrl(result.audio_url);
          setTranscript(result.transcript);
          setSceneTimestamps(finalTimestamps);
          publish(result.audio_url, result.transcript, finalTimestamps, duration);
        } catch {
          setError("Transcription failed. Please record again.");
        } finally {
          setUploading(false);
        }
      };
      recordingStartedAtRef.current = Date.now();
      recorder.start(250);
      timerRef.current = setInterval(() => {
        setElapsed((prev) => {
          const next = prev + 1;
          if (next >= cap) stopRecording();
          return next;
        });
      }, 1000);
    } catch {
      setRecording(false);
      setError("Microphone access is needed for this storyboard.");
    }
  };

  const closeOutTimestamps = (finalElapsed: number): SceneTimestamp[] => {
    const result: SceneTimestamp[] = [];
    const ids = Array.from(sceneStartedAtRef.current.keys());
    ids.forEach((sceneId, i) => {
      const started = sceneStartedAtRef.current.get(sceneId) ?? 0;
      const next = ids[i + 1];
      const ended = next ? sceneStartedAtRef.current.get(next) ?? finalElapsed : finalElapsed;
      result.push({
        scene_id: sceneId,
        started_at_seconds: started,
        ended_at_seconds: ended,
      });
    });
    return result;
  };

  const advanceScene = () => {
    if (!recording || submitted) return;
    if (activeIdx >= scenes.length - 1) return;
    const nextIdx = activeIdx + 1;
    const nextScene = scenes[nextIdx];
    if (nextScene) {
      sceneStartedAtRef.current.set(nextScene.scene_id, elapsed);
    }
    setActiveIdx(nextIdx);
  };

  const hasRecording = !!audioUrl;
  const canSubmit = !submitted && hasRecording && !recording && !uploading;
  const activeScene = scenes[activeIdx];

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Storyboard"
        intro={{
          title: payload.task_intro || "Tell the story scene by scene",
          body: payload.instructions || "One continuous recording. Tap Next Scene when you move on.",
        }}
        sub_skill={payload.sub_skill || "Narrative"}
        activity={payload.activity || "Storyboard Speaking"}
        time={payload.estimated_time_minutes ?? Math.ceil(cap / 60)}
      />

      <div
        className="tw-card"
        style={{
          background: "linear-gradient(135deg, oklch(96% 0.04 290), white)",
          borderColor: "oklch(82% 0.1 290)",
        }}
      >
        <div className="tw-rule-label" style={{ color: "oklch(40% 0.16 290)" }}>
          Premise
        </div>
        <div
          style={{
            fontSize: 15,
            fontWeight: 700,
            color: "var(--tw-navy)",
            lineHeight: 1.5,
            marginTop: 4,
          }}
        >
          {payload.overall_story_premise}
        </div>
        {payload.narrative_pattern && (
          <div style={{ fontSize: 12, color: "var(--tw-ink-muted)", marginTop: 6, fontStyle: "italic" }}>
            Pattern: {payload.narrative_pattern}
          </div>
        )}
      </div>

      <div className="tw-scene-strip">
        {scenes.map((s, i) => (
          <SceneCard
            key={s.scene_id}
            scene={s}
            isActive={!submitted && i === activeIdx}
            onClick={() => !submitted && !recording && setActiveIdx(i)}
          />
        ))}
      </div>

      {!submitted && (
        <>
          {activeScene && (
            <div className="tw-scene-active-banner">
              <div className="tw-scene-active-num">{activeScene.scene_number}</div>
              <div className="tw-scene-active-text">
                <div className="tw-scene-active-label">
                  Now narrating · Scene {activeScene.scene_number} of {scenes.length}
                </div>
                <div className="tw-scene-active-focus">{activeScene.narration_focus}</div>
              </div>
            </div>
          )}

          {error && (
            <div
              style={{
                background: "oklch(96% 0.05 25)",
                border: "1px solid oklch(84% 0.1 25)",
                color: "oklch(35% 0.16 25)",
                borderRadius: 12,
                padding: "10px 12px",
                fontSize: 13,
                marginBottom: 14,
              }}
            >
              {error}
            </div>
          )}

          <div className="tw-mic-stage">
            <div className="tw-mic-prompt">
              {recording
                ? "Recording your story"
                : hasRecording
                ? "Re-record to overwrite"
                : "One take · keep going through all scenes"}
            </div>
            <div className="tw-mic-button-wrap">
              <button
                className={`tw-mic-button${recording ? " recording" : ""}`}
                onClick={() => (recording ? stopRecording() : startRecording())}
                disabled={uploading}
                aria-label={recording ? "Stop recording" : "Start recording"}
              >
                {recording ? I.stop : I.mic}
              </button>
              <span className="tw-mic-ring" />
            </div>
            <div className="tw-mic-instruction">
              {recording
                ? "Tap to stop · or finish all scenes first"
                : uploading
                ? "Transcribing…"
                : "Tap to start the single take"}
            </div>
            <div className="tw-mic-sub">We&apos;ll mark when you click Next Scene</div>
            {recording && (
              <div className="tw-rec-timer">
                <span className="tw-rec-dot" />
                {formatDuration(elapsed)} / {formatDuration(cap)}
              </div>
            )}
          </div>

          <div className="tw-scene-nav">
            <button
              className="tw-scene-nav-btn"
              disabled={!recording || activeIdx === 0}
              onClick={() => setActiveIdx((a) => Math.max(0, a - 1))}
            >
              {I.arrowL} Previous
            </button>
            <button
              className={`tw-scene-nav-btn${activeIdx < scenes.length - 1 ? " primary" : ""}`}
              onClick={advanceScene}
              disabled={!recording || activeIdx >= scenes.length - 1}
            >
              {activeIdx === scenes.length - 1 ? "Last scene" : "Next scene"} {I.arrowR}
            </button>
          </div>
        </>
      )}

      {submitted && (
        <>
          <div className="tw-result-banner good">
            <div className="tw-result-icon" style={{ color: "var(--tw-green)" }}>
              {I.check}
            </div>
            <div className="tw-result-text">
              <div className="tw-result-headline">
                Story complete · {formatDuration((answers as StoryboardAnswers).duration_seconds ?? 0)}{" "}
                across {scenes.length} scene{scenes.length === 1 ? "" : "s"}
              </div>
              <div className="tw-result-sub">
                {transcript ? "Transcript captured below." : "Recording uploaded."}
              </div>
            </div>
            <div>
              <div className="tw-result-score">
                {formatDuration((answers as StoryboardAnswers).duration_seconds ?? 0)}
              </div>
              <div className="tw-result-score-sub">Total</div>
            </div>
          </div>

          {audioUrl && (
            <div className="tw-card">
              <div className="tw-rule-label" style={{ marginBottom: 8 }}>
                Your recording
              </div>
              <audio src={resolveAudioUrl(audioUrl)} controls style={{ width: "100%" }} />
            </div>
          )}

          {transcript && (
            <div className="tw-card">
              <div className="tw-rule-label" style={{ marginBottom: 8 }}>
                Transcript
              </div>
              <div style={{ fontSize: 13.5, lineHeight: 1.6, color: "var(--tw-navy)" }}>
                {transcript}
              </div>
            </div>
          )}

          {payload.sample_narration && (
            <div className="tw-compare-card sample">
              <div className="tw-compare-label">{I.spark} Sample narration</div>
              <div className="tw-compare-body">{payload.sample_narration}</div>
            </div>
          )}

          {sceneTimestamps.length > 0 && (
            <div className="tw-ts-table" style={{ marginTop: 14 }}>
              <div className="tw-ts-row head">
                <div>#</div>
                <div>Scene focus</div>
                <div>Time</div>
              </div>
              {sceneTimestamps.map((t, i) => {
                const scene = scenes.find((s) => s.scene_id === t.scene_id);
                return (
                  <div className="tw-ts-row" key={t.scene_id}>
                    <div className="tw-ts-scene-num">{scene?.scene_number ?? i + 1}</div>
                    <div className="tw-ts-cap">{scene?.narration_focus ?? t.scene_id}</div>
                    <div className="tw-ts-time">
                      {formatDuration(t.started_at_seconds)}–{formatDuration(t.ended_at_seconds)}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {!submitted && (
        <button
          className="tw-submit-btn"
          disabled={!canSubmit}
          onClick={onSubmit}
          style={{ marginTop: 14 }}
        >
          {I.send} Submit storyboard
        </button>
      )}
    </div>
  );
}

function SceneCard({
  scene,
  isActive,
  onClick,
}: {
  scene: StoryboardScene;
  isActive: boolean;
  onClick: () => void;
}) {
  const imageUrl = resolveAudioUrl(scene.image_url);
  const hasImage = !!imageUrl;
  return (
    <div
      className={`tw-scene-card${isActive ? " active" : ""}`}
      onClick={onClick}
      role="button"
    >
      <div
        className={`tw-scene-img${hasImage ? " filled" : " skeleton"}`}
        style={
          hasImage
            ? {
                backgroundImage: `url(${imageUrl})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
              }
            : undefined
        }
      >
        {!hasImage && (
          <span style={{ fontSize: 12, color: "var(--tw-ink-muted)" }}>Loading…</span>
        )}
      </div>
      <div className="tw-scene-meta">
        <div className="tw-scene-num">Scene {scene.scene_number}</div>
        <div className="tw-scene-caption">{scene.narration_focus}</div>
      </div>
    </div>
  );
}
