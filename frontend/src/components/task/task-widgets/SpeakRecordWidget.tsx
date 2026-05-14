"use client";

import { useEffect, useRef, useState } from "react";
import { tasksApi } from "@/lib/tasks-api";
import { TaskHeader, I } from "./shared";
import { formatDuration, resolveAudioUrl } from "./types";
import type { SpeakAndRecordPayload, SpeakRoleplayTurn, WidgetProps } from "./types";

type Props = WidgetProps<SpeakAndRecordPayload>;

interface Recording {
  item_id?: string;
  turn_id?: string;
  audio_blob_url: string;
  transcript: string;
  duration_seconds: number;
  attempt_number: number;
}

type Mode = "list" | "single" | "read" | "retell" | "role";

function detectMode(p: SpeakAndRecordPayload): Mode {
  if (p.turns && p.turns.length > 0) return "role";
  if (p.source_audio_url || p.source_audio_script) return "retell";
  if (p.text_to_read_aloud || p.passage) return "read";
  if (p.speaking_prompts && p.speaking_prompts.length > 0) return "list";
  return "single";
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

export function SpeakRecordWidget({ payload, answers, setAnswers, state, onSubmit }: Props) {
  const submitted = state === "after";
  const mode = detectMode(payload);

  // Items: a unified list of "things to record".
  const items: Array<{ id: string; label: string; kind: "prompt" | "turn"; turn?: SpeakRoleplayTurn; sampleResponse?: string | null }> = (() => {
    if (mode === "role") {
      return (payload.turns ?? [])
        .filter((t) => t.speaker === "user")
        .map((t, i) => ({
          id: t.turn_id,
          label: payload.sample_user_responses?.[i] || "Your reply",
          kind: "turn" as const,
          turn: t,
          sampleResponse: payload.sample_user_responses?.[i] ?? null,
        }));
    }
    if (mode === "list") {
      const prompts = payload.speaking_prompts ?? [];
      return prompts.map((p, i) => ({
        id: `prompt_${i + 1}`,
        label: p,
        kind: "prompt" as const,
        sampleResponse: payload.sample_responses?.[i] ?? null,
      }));
    }
    if (mode === "read") {
      return [
        {
          id: "read_aloud",
          label: payload.text_to_read_aloud || payload.passage || "",
          kind: "prompt" as const,
          sampleResponse: payload.sample_response ?? null,
        },
      ];
    }
    if (mode === "retell") {
      return [
        {
          id: "retell",
          label: payload.retelling_prompt || "Retell what you heard in your own words.",
          kind: "prompt" as const,
          sampleResponse: payload.sample_response ?? null,
        },
      ];
    }
    return [
      {
        id: "prompt_1",
        label: payload.speaking_prompt || "Speak your response",
        kind: "prompt" as const,
        sampleResponse: payload.sample_response ?? null,
      },
    ];
  })();

  const startedAtRef = useRef(Date.now());
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const recordingStartedAtRef = useRef<number>(0);

  const [recordings, setRecordings] = useState<Record<string, Recording>>({});
  const [activeItemId, setActiveItemId] = useState<string | null>(null);
  const [uploadingItemId, setUploadingItemId] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [prepRemaining, setPrepRemaining] = useState(payload.preparation_seconds ?? 0);
  const sourceAudioUrl = resolveAudioUrl(payload.source_audio_url);
  const referenceAudioUrl = resolveAudioUrl(payload.reference_audio_url);

  useEffect(() => {
    if (!payload.preparation_seconds || submitted) return;
    if (prepRemaining <= 0) return;
    const interval = setInterval(() => {
      setPrepRemaining((s) => Math.max(0, s - 1));
    }, 1000);
    return () => clearInterval(interval);
  }, [payload.preparation_seconds, prepRemaining, submitted]);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const publish = (next: Record<string, Recording>) => {
    setAnswers({
      recordings: items
        .map((it) => next[it.id])
        .filter(Boolean)
        .map((rec) => ({
          item_id: rec.item_id,
          turn_id: rec.turn_id,
          audio_blob_url: rec.audio_blob_url,
          duration_seconds: rec.duration_seconds,
          attempt_number: rec.attempt_number,
          transcript: rec.transcript,
        })),
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

  const startRecording = async (itemId: string) => {
    if (submitted || activeItemId || uploadingItemId) return;
    if (prepRemaining > 0) return;
    setError(null);
    chunksRef.current = [];
    setActiveItemId(itemId);
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
        setUploadingItemId(itemId);
        setActiveItemId(null);
        const usedMime = recorder.mimeType || mimeType || "audio/webm";
        const blob = new Blob(chunksRef.current, { type: usedMime });
        const ext = extensionForMime(usedMime);
        try {
          const result = await tasksApi.transcribeAudio(blob, `speak-${itemId}${ext}`);
          const item = items.find((it) => it.id === itemId);
          setRecordings((prev) => {
            const next: Record<string, Recording> = {
              ...prev,
              [itemId]: {
                ...(item?.kind === "turn"
                  ? { turn_id: itemId }
                  : { item_id: itemId }),
                audio_blob_url: result.audio_url,
                transcript: result.transcript,
                duration_seconds: duration,
                attempt_number: (prev[itemId]?.attempt_number ?? 0) + 1,
              },
            };
            publish(next);
            return next;
          });
        } catch {
          setError("Transcription failed. Please record that prompt again.");
        } finally {
          setUploadingItemId(null);
        }
      };
      recordingStartedAtRef.current = Date.now();
      recorder.start(250);
      const cap = payload.speaking_duration_seconds || 60;
      timerRef.current = setInterval(() => {
        setElapsed((prev) => {
          const next = prev + 1;
          if (next >= cap) stopRecording();
          return next;
        });
      }, 1000);
    } catch {
      setActiveItemId(null);
      setError("Microphone access is needed for this speaking activity.");
    }
  };

  const allRecorded = items.every((it) => recordings[it.id]?.transcript?.trim());
  const canSubmit = !submitted && allRecorded && !activeItemId && !uploadingItemId;

  const targetWordsHit = (() => {
    if (!payload.target_words || payload.target_words.length === 0) return [];
    const allText = Object.values(recordings)
      .map((r) => r.transcript)
      .join(" ")
      .toLowerCase();
    return payload.target_words.map((w) => ({
      word: w,
      used: new RegExp(`\\b${w.toLowerCase()}\\b`).test(allText),
    }));
  })();

  const cap = payload.speaking_duration_seconds || 60;

  return (
    <div className="tw-root">
      <TaskHeader
        topic={payload.topic_name || "Speaking task"}
        intro={{
          title: payload.task_intro || "Record your response",
          body: payload.instructions || "Tap the mic and speak naturally.",
        }}
        sub_skill={payload.sub_skill || ""}
        activity={payload.activity || "Speak & Record"}
        time={payload.estimated_time_minutes ?? 0}
        target_words={targetWordsHit.length > 0 ? targetWordsHit : undefined}
      />

      {payload.grammar_rule_to_practice && (
        <div className="tw-rule-callout">
          <div className="tw-rule-icon">{I.rule}</div>
          <div className="tw-rule-body">
            <div className="tw-rule-label">Target rule</div>
            <div className="tw-rule-text">{payload.grammar_rule_to_practice}</div>
          </div>
        </div>
      )}

      {payload.target_pattern && (
        <div className="tw-rule-callout">
          <div className="tw-rule-icon">{I.rule}</div>
          <div className="tw-rule-body">
            <div className="tw-rule-label">Target pattern</div>
            <div className="tw-rule-text">{payload.target_pattern}</div>
          </div>
        </div>
      )}

      {payload.target_tone && (
        <div className="tw-rule-callout">
          <div className="tw-rule-icon">{I.rule}</div>
          <div className="tw-rule-body">
            <div className="tw-rule-label">Target tone</div>
            <div className="tw-rule-text">{payload.target_tone}</div>
          </div>
        </div>
      )}

      {mode === "retell" && sourceAudioUrl && (
        <div className="tw-card" style={{ background: "oklch(96% 0.03 245)" }}>
          <div className="tw-rule-label" style={{ marginBottom: 8 }}>Source audio</div>
          <audio src={sourceAudioUrl} controls style={{ width: "100%" }} />
        </div>
      )}

      {referenceAudioUrl && (
        <div className="tw-card" style={{ background: "oklch(96% 0.03 245)" }}>
          <div className="tw-rule-label" style={{ marginBottom: 8 }}>Reference pronunciation</div>
          <audio src={referenceAudioUrl} controls style={{ width: "100%" }} />
        </div>
      )}

      {mode === "read" && (payload.text_to_read_aloud || payload.passage) && (
        <div className="tw-passage">
          <div className="tw-passage-label">Read aloud</div>
          {payload.text_to_read_aloud || payload.passage}
        </div>
      )}

      {payload.scenario_description && (
        <div
          className="tw-card"
          style={{ background: "oklch(96% 0.04 290)", borderColor: "oklch(82% 0.1 290)" }}
        >
          <div className="tw-rule-label" style={{ color: "oklch(40% 0.16 290)", marginBottom: 6 }}>
            Scenario
          </div>
          <div style={{ fontSize: 13.5, color: "var(--tw-navy)", lineHeight: 1.6 }}>
            {payload.scenario_description}
          </div>
        </div>
      )}

      {prepRemaining > 0 && !submitted && (
        <div className="tw-prep-countdown">
          {I.clock} Prep time · {formatDuration(prepRemaining)} left
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

      <div style={{ display: "grid", gap: 14, marginBottom: 18 }}>
        {items.map((item, index) => {
          const rec = recordings[item.id];
          const isActive = activeItemId === item.id;
          const isUploading = uploadingItemId === item.id;
          const attemptsUsed = rec?.attempt_number ?? 0;
          const reRecordsLeft = Math.max(0, 3 - attemptsUsed);
          return (
            <div className="tw-card" key={item.id}>
              {mode === "role" && item.turn && (
                <PriorRoleplayTurns
                  payload={payload}
                  thisTurnId={item.turn.turn_id}
                />
              )}
              <div className="tw-q-number-row">
                <div className="tw-q-number-badge">{index + 1}</div>
                <div className="tw-q-stem">
                  {mode === "role"
                    ? "Your reply"
                    : item.label}
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
                <button
                  type="button"
                  disabled={
                    submitted ||
                    !!uploadingItemId ||
                    (!!activeItemId && !isActive) ||
                    prepRemaining > 0
                  }
                  onClick={() => (isActive ? stopRecording() : startRecording(item.id))}
                  className={`tw-mic-button${isActive ? " recording" : ""}`}
                  style={{ width: 56, height: 56 }}
                  aria-label={isActive ? "Stop recording" : "Start recording"}
                >
                  {isActive ? I.stop : I.mic}
                </button>
                <div style={{ color: "var(--tw-ink-muted)", fontSize: 13, fontWeight: 700, flex: 1 }}>
                  {isActive
                    ? `Recording ${formatDuration(elapsed)} / ${formatDuration(cap)}`
                    : isUploading
                    ? "Transcribing…"
                    : rec
                    ? `Recorded ${rec.duration_seconds}s · attempt ${attemptsUsed}/3`
                    : prepRemaining > 0
                    ? "Prep timer running…"
                    : "Tap the mic to start"}
                </div>
                {rec && !submitted && reRecordsLeft > 0 && !activeItemId && !uploadingItemId && (
                  <button
                    className="tw-action-pill"
                    onClick={() => startRecording(item.id)}
                  >
                    <span style={{ transform: "scaleX(-1)", display: "inline-block" }}>
                      {I.replay}
                    </span>{" "}
                    Re-record ({reRecordsLeft} left)
                  </button>
                )}
              </div>
              {rec && (
                <div
                  style={{
                    marginTop: 12,
                    borderRadius: 12,
                    background: "oklch(96% 0.025 245)",
                    border: "1px solid oklch(86% 0.025 240)",
                    padding: "10px 12px",
                    color: "oklch(28% 0.07 240)",
                    fontSize: 13,
                    lineHeight: 1.6,
                  }}
                >
                  <strong>Transcript:</strong> {rec.transcript || "(no speech detected)"}
                </div>
              )}
              {submitted && item.sampleResponse && (
                <div
                  style={{
                    marginTop: 10,
                    borderRadius: 12,
                    background: "oklch(94% 0.07 155)",
                    border: "1px solid oklch(80% 0.1 155)",
                    padding: "10px 12px",
                    color: "oklch(24% 0.1 155)",
                    fontSize: 13,
                    lineHeight: 1.6,
                  }}
                >
                  <strong>Sample:</strong> {item.sampleResponse}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {submitted && payload.key_points_expected && payload.key_points_expected.length > 0 && (
        <div className="tw-hints-block" style={{ marginTop: 4 }}>
          <div className="tw-hints-label">Key points expected</div>
          <div className="tw-hints-list">
            {payload.key_points_expected.map((p, i) => (
              <div className="tw-hint-item" key={i}>
                <span className="tw-hint-dot" />
                {p}
              </div>
            ))}
          </div>
        </div>
      )}

      {submitted && payload.sample_talking_points && payload.sample_talking_points.length > 0 && (
        <div className="tw-hints-block" style={{ marginTop: 4 }}>
          <div className="tw-hints-label">Sample talking points</div>
          <div className="tw-hints-list">
            {payload.sample_talking_points.map((p, i) => (
              <div className="tw-hint-item" key={i}>
                <span className="tw-hint-dot" />
                {p}
              </div>
            ))}
          </div>
        </div>
      )}

      {!submitted && (
        <button
          className="tw-submit-btn"
          disabled={!canSubmit}
          onClick={onSubmit}
        >
          {I.send} Submit recordings
        </button>
      )}
    </div>
  );
}

function PriorRoleplayTurns({
  payload,
  thisTurnId,
}: {
  payload: SpeakAndRecordPayload;
  thisTurnId: string;
}) {
  const turns = payload.turns ?? [];
  const idx = turns.findIndex((t) => t.turn_id === thisTurnId);
  if (idx <= 0) return null;
  const priorAiTurn = [...turns.slice(0, idx)].reverse().find((t) => t.speaker === "ai");
  if (!priorAiTurn?.ai_line) return null;
  return (
    <div
      style={{
        background: "oklch(97% 0.02 245)",
        border: "1px dashed oklch(86% 0.025 240)",
        borderRadius: 10,
        padding: "8px 12px",
        marginBottom: 10,
        fontSize: 13,
        color: "var(--tw-navy)",
        lineHeight: 1.55,
      }}
    >
      <strong style={{ color: "oklch(48% 0.18 290)" }}>AI:</strong> {priorAiTurn.ai_line}
    </div>
  );
}
