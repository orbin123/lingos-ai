"use client";

import type { CSSProperties } from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { LucideIcon } from "lucide-react";
import {
  AlertTriangle,
  ArrowLeft,
  BookOpen,
  Clock3,
  Headphones,
  Mic,
  PenLine,
  RotateCcw,
  Send,
  Square,
  Trophy,
} from "lucide-react";
import { authApi } from "@/lib/auth-api";
import { challengesApi } from "@/lib/challenges-api";
import type {
  ChallengeAttemptRead,
  ChallengeSpeakingUploadRead,
} from "@/lib/challenges-api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useAuthStore } from "@/store/authStore";

type SectionKey = "listening" | "reading" | "writing" | "speaking";

interface MCQItem {
  item_id: string;
  prompt: string;
  options: string[];
  correct_index?: number;
  explanation?: string;
}

interface ReadingSectionPayload {
  passage_title?: string;
  passage?: string;
  items?: MCQItem[];
}

interface WritingPrompt {
  item_id: string;
  prompt: string;
  target_word_count?: number;
}

interface WritingSectionPayload {
  items?: WritingPrompt[];
  target_word_count?: number;
}

interface ListeningSectionPayload {
  audio_script?: string;
  audio_url?: string | null;
  audio_cache_hit?: boolean;
  audio_duration_seconds?: number;
  items?: MCQItem[];
}

interface SpeakingSectionPayload {
  speaking_prompts?: string[];
  speaking_duration_seconds?: number;
}

type SpeakingResponseValue = ChallengeSpeakingUploadRead & {
  duration_seconds?: number;
};

interface ChallengeResponses {
  listening: Record<string, string>;
  reading: Record<string, string>;
  writing: Record<string, string>;
  speaking: Record<string, SpeakingResponseValue>;
}

const emptyResponses: ChallengeResponses = {
  listening: {},
  reading: {},
  writing: {},
  speaking: {},
};

const sectionNav: Array<{
  key: SectionKey;
  label: string;
  Icon: LucideIcon;
}> = [
  { key: "listening", label: "Listening", Icon: Headphones },
  { key: "reading", label: "Reading", Icon: BookOpen },
  { key: "writing", label: "Writing", Icon: PenLine },
  { key: "speaking", label: "Speaking", Icon: Mic },
];

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readStringMap(value: unknown): Record<string, string> {
  if (!isRecord(value)) return {};
  return Object.fromEntries(
    Object.entries(value).filter((entry): entry is [string, string] => {
      return typeof entry[1] === "string";
    }),
  );
}

function readSpeakingMap(value: unknown): Record<string, SpeakingResponseValue> {
  if (!isRecord(value)) return {};
  const entries = Object.entries(value)
    .map(([key, raw]) => {
      if (!isRecord(raw)) return null;
      const audioUrl = raw.audio_url;
      const audioStorageKey = raw.audio_storage_key;
      const contentType = raw.content_type;
      const sizeBytes = raw.size_bytes;
      if (
        typeof audioUrl !== "string" ||
        typeof audioStorageKey !== "string" ||
        typeof contentType !== "string" ||
        typeof sizeBytes !== "number"
      ) {
        return null;
      }
      const duration =
        typeof raw.duration_seconds === "number" ? raw.duration_seconds : undefined;
      return [
        key,
        {
          prompt_id: key,
          audio_url: audioUrl,
          audio_storage_key: audioStorageKey,
          content_type: contentType,
          size_bytes: sizeBytes,
          ...(duration ? { duration_seconds: duration } : {}),
        },
      ] as const;
    })
    .filter((entry): entry is readonly [string, SpeakingResponseValue] => entry !== null);
  return Object.fromEntries(entries);
}

function normalizeResponses(payload: Record<string, unknown> | null): ChallengeResponses {
  return {
    listening: readStringMap(payload?.listening),
    reading: readStringMap(payload?.reading),
    writing: readStringMap(payload?.writing),
    speaking: readSpeakingMap(payload?.speaking),
  };
}

function getSectionPayload<T>(
  taskPayload: Record<string, unknown> | undefined,
  section: SectionKey,
): T {
  const rawSections = taskPayload?.sections;
  const sections = isRecord(rawSections) ? rawSections : {};
  const raw = sections[section];
  return (isRecord(raw) ? raw : {}) as T;
}

function formatRemaining(totalSeconds: number): string {
  const safe = Math.max(0, Math.floor(totalSeconds));
  const minutes = Math.floor(safe / 60);
  const seconds = safe % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

function countWords(text: string): number {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

function progressLabel(
  section: SectionKey,
  responses: ChallengeResponses,
  listening: ListeningSectionPayload,
  reading: ReadingSectionPayload,
  writing: WritingSectionPayload,
  speaking: SpeakingSectionPayload,
): string {
  if (section === "listening") {
    const total = listening.items?.length ?? 0;
    const answered = Object.keys(responses.listening).length;
    return `${Math.min(answered, total)}/${total} answered`;
  }
  if (section === "reading") {
    const total = reading.items?.length ?? 0;
    const answered = Object.keys(responses.reading).length;
    return `${Math.min(answered, total)}/${total} answered`;
  }
  if (section === "writing") {
    const prompts = writing.items ?? [];
    const answered = prompts.filter((prompt) =>
      responses.writing[prompt.item_id]?.trim(),
    ).length;
    return `${answered}/${prompts.length} drafted`;
  }
  const prompts = speaking.speaking_prompts ?? [];
  const uploaded = Object.keys(responses.speaking).length;
  return `${Math.min(uploaded, prompts.length)}/${prompts.length} uploaded`;
}

export default function ChallengeAttemptPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { logout } = useAuthStore();
  const { isReady } = useRequireAuth();
  const attemptId = Number(params.id);

  const { data: user } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });

  const attemptQuery = useQuery({
    queryKey: ["challenge-attempt", attemptId],
    queryFn: () => challengesApi.getAttempt(attemptId),
    enabled: isReady && Number.isFinite(attemptId),
  });

  const [activeSection, setActiveSection] = useState<SectionKey>("reading");
  const [responses, setResponses] = useState<ChallengeResponses>(emptyResponses);
  const [remainingSeconds, setRemainingSeconds] = useState(0);
  const [submittedAttempt, setSubmittedAttempt] =
    useState<ChallengeAttemptRead | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const initializedAttemptId = useRef<number | null>(null);
  const responsesRef = useRef<ChallengeResponses>(responses);
  const attemptRef = useRef<ChallengeAttemptRead | null>(null);
  const submitInFlightRef = useRef(false);

  const currentAttempt = submittedAttempt ?? attemptQuery.data ?? null;
  const taskPayload = currentAttempt?.task_payload;
  const reading = getSectionPayload<ReadingSectionPayload>(taskPayload, "reading");
  const writing = getSectionPayload<WritingSectionPayload>(taskPayload, "writing");
  const listening = getSectionPayload<ListeningSectionPayload>(
    taskPayload,
    "listening",
  );
  const speaking = getSectionPayload<SpeakingSectionPayload>(taskPayload, "speaking");

  const submitMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      challengesApi.submitAttempt(attemptId, payload),
    onSuccess: (attempt) => {
      setSubmittedAttempt(attempt);
      setSubmitError(null);
      queryClient.setQueryData(["challenge-attempt", attemptId], attempt);
    },
    onError: (error) => {
      const message = error instanceof Error ? error.message : "Submit failed";
      setSubmitError(message);
      queryClient.invalidateQueries({ queryKey: ["challenge-attempt", attemptId] });
    },
  });

  useEffect(() => {
    if (user && !user.diagnosis_completed) router.replace("/diagnosis");
  }, [user, router]);

  useEffect(() => {
    responsesRef.current = responses;
  }, [responses]);

  useEffect(() => {
    attemptRef.current = currentAttempt;
  }, [currentAttempt]);

  useEffect(() => {
    const attempt = attemptQuery.data;
    if (!attempt || initializedAttemptId.current === attempt.id) return;
    setResponses(normalizeResponses(attempt.response_payload));
    initializedAttemptId.current = attempt.id;
  }, [attemptQuery.data]);

  const submitNow = useCallback(() => {
    const attempt = attemptRef.current;
    if (!attempt || attempt.status !== "in_progress" || submitInFlightRef.current) {
      return;
    }
    submitInFlightRef.current = true;
    setSubmitError(null);
    submitMutation.mutate(
      { ...responsesRef.current },
      {
        onSettled: () => {
          submitInFlightRef.current = false;
        },
      },
    );
  }, [submitMutation]);

  useEffect(() => {
    const attempt = currentAttempt;
    if (!attempt || attempt.status !== "in_progress") return;

    const updateRemaining = () => {
      const next = Math.max(
        0,
        Math.ceil((new Date(attempt.expires_at).getTime() - Date.now()) / 1000),
      );
      setRemainingSeconds(next);
      if (next === 0) submitNow();
    };

    updateRemaining();
    const interval = window.setInterval(updateRemaining, 1000);
    return () => window.clearInterval(interval);
  }, [currentAttempt, submitNow]);

  useEffect(() => {
    if (currentAttempt?.status !== "in_progress") return;
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [currentAttempt?.status]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!isReady) return null;

  const status = currentAttempt?.status;
  const inProgress = status === "in_progress";
  const isComplete = status === "completed" || status === "timed_out";
  const warning = inProgress && remainingSeconds <= 60;

  return (
    <div style={pageWrapperStyle}>
      {/* Dot grid overlay */}
      <div style={dotGridStyle} aria-hidden />

      {/* Top nav */}
      <header style={topBarStyle}>
        <div style={topBarInnerStyle}>
          <button
            type="button"
            onClick={() => router.push("/challenges")}
            style={backLinkStyle}
          >
            <ArrowLeft size={14} aria-hidden />
            Challenges
          </button>
          <div style={{ flex: 1 }} />
          <span style={userNameStyle}>
            {user?.display_name || user?.name || "Learner"}
          </span>
          <button type="button" onClick={handleLogout} style={signOutButtonStyle}>
            Sign out
          </button>
        </div>
      </header>

      <main style={mainStyle}>
        {attemptQuery.isLoading && (
          <div style={panelStyle}>Loading attempt...</div>
        )}

        {attemptQuery.isError && (
          <div style={alertStyle}>Could not load this challenge attempt.</div>
        )}

        {currentAttempt && (
          <>
            {/* Exam header */}
            <div style={examHeaderStyle}>
              <div
                style={{
                  ...timerPillStyle,
                  borderColor: warning ? "rgba(240,80,60,0.35)" : "rgba(255,255,255,0.92)",
                }}
                aria-live="polite"
                aria-label={`${Math.ceil(remainingSeconds / 60)} minutes remaining`}
              >
                <Clock3
                  size={16}
                  aria-hidden
                  style={{ color: warning ? "#e03a2f" : "#4a6880", flexShrink: 0 }}
                />
                <span
                  style={{
                    ...timerTimeStyle,
                    color: warning ? "#e03a2f" : "#0d1f36",
                  }}
                >
                  {inProgress ? formatRemaining(remainingSeconds) : "Submitted"}
                </span>
              </div>

              <div style={{ flex: 1, minWidth: 0 }}>
                <h1 style={examTitleStyle}>IELTS Sprint Attempt</h1>
                <p style={examSubStyle}>
                  <span style={inProgressDotStyle} />
                  Level attempt #{currentAttempt.id} · {status?.replace("_", " ")}
                </p>
              </div>

              {inProgress && (
                <button
                  type="button"
                  onClick={submitNow}
                  disabled={submitMutation.isPending}
                  style={submitButtonStyle}
                >
                  <Send size={15} aria-hidden />
                  {submitMutation.isPending ? "Submitting" : "Submit"}
                </button>
              )}
            </div>

            {/* Section tabs */}
            <nav style={tabRailStyle} aria-label="Challenge sections">
              {sectionNav.map(({ key, label, Icon }) => {
                const active = activeSection === key;
                return (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setActiveSection(key)}
                    style={{
                      ...tabButtonStyle,
                      background: active ? "#0f1e30" : "rgba(255,255,255,0.75)",
                      borderColor: active ? "#0f1e30" : "rgba(255,255,255,0.85)",
                      boxShadow: active
                        ? "0 4px 16px rgba(10,20,50,0.22)"
                        : "0 2px 10px rgba(80,110,180,0.07)",
                    }}
                  >
                    <span
                      style={{
                        ...tabIconStyle,
                        background: active ? "rgba(255,255,255,0.12)" : "#f0f4f8",
                        color: active ? "white" : "#4a6880",
                      }}
                    >
                      <Icon size={16} aria-hidden />
                    </span>
                    <span style={tabBodyStyle}>
                      <span
                        style={{
                          ...tabNameStyle,
                          color: active ? "white" : "#0d1f36",
                        }}
                      >
                        {label}
                      </span>
                      <small
                        style={{
                          ...tabStatusStyle,
                          color: active ? "rgba(180,210,240,0.9)" : "#4a6880",
                        }}
                      >
                        {progressLabel(
                          key,
                          responses,
                          listening,
                          reading,
                          writing,
                          speaking,
                        )}
                      </small>
                    </span>
                  </button>
                );
              })}
            </nav>

            {submitError && (
              <div style={{ ...alertStyle, marginBottom: 16 }}>
                <AlertTriangle size={18} aria-hidden />
                {submitError}
              </div>
            )}

            {activeSection === "listening" && (
              <ListeningSection
                payload={listening}
                disabled={!inProgress}
                answers={responses.listening}
                onAnswer={(itemId, optionLetter) =>
                  setResponses((prev) => ({
                    ...prev,
                    listening: { ...prev.listening, [itemId]: optionLetter },
                  }))
                }
              />
            )}
            {activeSection === "reading" && (
              <ReadingSection
                payload={reading}
                disabled={!inProgress}
                answers={responses.reading}
                onAnswer={(itemId, optionLetter) =>
                  setResponses((prev) => ({
                    ...prev,
                    reading: { ...prev.reading, [itemId]: optionLetter },
                  }))
                }
              />
            )}
            {activeSection === "writing" && (
              <WritingSection
                payload={writing}
                disabled={!inProgress}
                answers={responses.writing}
                onAnswer={(itemId, value) =>
                  setResponses((prev) => ({
                    ...prev,
                    writing: { ...prev.writing, [itemId]: value },
                  }))
                }
              />
            )}
            {activeSection === "speaking" && (
              <SpeakingSection
                attemptId={attemptId}
                payload={speaking}
                disabled={!inProgress}
                answers={responses.speaking}
                onAnswer={(promptId, value) =>
                  setResponses((prev) => {
                    const nextSpeaking = { ...prev.speaking };
                    if (value) nextSpeaking[promptId] = value;
                    else delete nextSpeaking[promptId];
                    return { ...prev, speaking: nextSpeaking };
                  })
                }
              />
            )}

            {isComplete && <ResultsPanel attempt={currentAttempt} />}
          </>
        )}
      </main>
    </div>
  );
}

function ListeningSection({
  payload,
  answers,
  disabled,
  onAnswer,
}: {
  payload: ListeningSectionPayload;
  answers: Record<string, string>;
  disabled: boolean;
  onAnswer: (itemId: string, optionLetter: string) => void;
}) {
  const items = payload.items ?? [];
  const audioUrl = typeof payload.audio_url === "string" ? payload.audio_url : null;
  return (
    <section style={panelStyle}>
      <SectionHeading
        Icon={Headphones}
        title="Listening"
        meta={
          payload.audio_duration_seconds
            ? `${Math.round(payload.audio_duration_seconds)}s audio`
            : `${items.length} questions`
        }
      />
      {items.length === 0 ? (
        <PlaceholderContent
          Icon={Headphones}
          label="Listening"
          sub="Audio generation arrives in a future phase."
        />
      ) : (
        <>
          {audioUrl ? (
            <ListeningAudioPlayer audioUrl={audioUrl} disabled={disabled} />
          ) : (
            <>
              <div style={mutedBandStyle}>
                <p
                  style={{ margin: 0, color: "#4a6880", lineHeight: 1.6, fontSize: 14 }}
                >
                  Audio is temporarily unavailable. Use the transcript fallback for
                  this attempt.
                </p>
              </div>
              <div style={transcriptStyle}>
                {payload.audio_script ?? "Transcript unavailable."}
              </div>
            </>
          )}
          <QuestionList
            items={items}
            disabled={disabled}
            selected={answers}
            onAnswer={onAnswer}
          />
        </>
      )}
    </section>
  );
}

function ListeningAudioPlayer({
  audioUrl,
  disabled,
}: {
  audioUrl: string;
  disabled: boolean;
}) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const objectUrlRef = useRef<string | null>(null);
  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [playsUsed, setPlaysUsed] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const maxPlays = 3;

  useEffect(() => {
    let cancelled = false;
    setObjectUrl(null);
    setLoadError(null);
    setPlaysUsed(0);
    setCurrentTime(0);
    setDuration(0);
    setIsPlaying(false);

    challengesApi
      .getAttemptAudio(audioUrl)
      .then((blob) => {
        if (cancelled) return;
        const nextUrl = URL.createObjectURL(blob);
        objectUrlRef.current = nextUrl;
        setObjectUrl(nextUrl);
      })
      .catch(() => {
        if (!cancelled) setLoadError("Could not load the protected audio clip.");
      });

    return () => {
      cancelled = true;
      if (objectUrlRef.current) {
        URL.revokeObjectURL(objectUrlRef.current);
        objectUrlRef.current = null;
      }
    };
  }, [audioUrl]);

  const handlePlay = async () => {
    const audio = audioRef.current;
    if (!audio || disabled || playsUsed >= maxPlays) return;
    if (audio.ended) audio.currentTime = 0;
    setPlaysUsed((count) => count + 1);
    try {
      await audio.play();
    } catch {
      setPlaysUsed((count) => Math.max(0, count - 1));
      setLoadError("The browser could not start playback.");
    }
  };

  const progress = duration > 0 ? Math.min(100, (currentTime / duration) * 100) : 0;
  const remainingPlays = Math.max(0, maxPlays - playsUsed);

  return (
    <div style={audioPlayerStyle}>
      <audio
        ref={audioRef}
        src={objectUrl ?? undefined}
        onLoadedMetadata={(event) => setDuration(event.currentTarget.duration || 0)}
        onTimeUpdate={(event) => setCurrentTime(event.currentTarget.currentTime)}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
      />
      <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <button
          type="button"
          onClick={handlePlay}
          disabled={disabled || !objectUrl || playsUsed >= maxPlays || isPlaying}
          style={submitButtonStyle}
        >
          <Headphones size={15} aria-hidden />
          {playsUsed === 0 ? "Play" : "Replay"}
        </button>
        <span style={{ color: "#4a6880", fontSize: 13, fontWeight: 800 }}>
          {objectUrl
            ? `${remainingPlays} plays left`
            : loadError ?? "Preparing audio..."}
        </span>
      </div>
      <div style={audioProgressTrackStyle} aria-hidden>
        <div style={{ ...audioProgressFillStyle, width: `${progress}%` }} />
      </div>
      <div style={wordCountStyle}>
        {formatRemaining(currentTime)} / {formatRemaining(duration)}
      </div>
      {loadError && <div style={{ ...alertStyle, marginTop: 12 }}>{loadError}</div>}
    </div>
  );
}

function ReadingSection({
  payload,
  answers,
  disabled,
  onAnswer,
}: {
  payload: ReadingSectionPayload;
  answers: Record<string, string>;
  disabled: boolean;
  onAnswer: (itemId: string, optionLetter: string) => void;
}) {
  const items = payload.items ?? [];
  return (
    <section style={panelStyle}>
      <SectionHeading Icon={BookOpen} title="Reading" meta={`${items.length} questions`} />
      <article style={passageStyle}>
        <h2 style={passageTitleStyle}>{payload.passage_title ?? "Reading Passage"}</h2>
        <p style={{ margin: "10px 0 0", color: "#4a6880", lineHeight: 1.75, fontSize: 14, fontWeight: 500 }}>
          {payload.passage ?? "Passage unavailable."}
        </p>
      </article>
      <QuestionList
        items={items}
        disabled={disabled}
        selected={answers}
        onAnswer={onAnswer}
      />
    </section>
  );
}

function WritingSection({
  payload,
  answers,
  disabled,
  onAnswer,
}: {
  payload: WritingSectionPayload;
  answers: Record<string, string>;
  disabled: boolean;
  onAnswer: (itemId: string, value: string) => void;
}) {
  const prompts = payload.items ?? [];
  return (
    <section style={panelStyle}>
      <SectionHeading
        Icon={PenLine}
        title="Writing"
        meta={`${payload.target_word_count ?? 80} target words`}
      />
      <div style={{ display: "grid", gap: 16 }}>
        {prompts.map((prompt, index) => {
          const value = answers[prompt.item_id] ?? "";
          const target = prompt.target_word_count ?? payload.target_word_count ?? 80;
          return (
            <div key={prompt.item_id} style={questionCardStyle}>
              <div style={questionStemStyle}>
                <span style={numberBadgeStyle}>{index + 1}</span>
                <span>{prompt.prompt}</span>
              </div>
              <textarea
                value={value}
                disabled={disabled}
                onChange={(event) => onAnswer(prompt.item_id, event.target.value)}
                rows={9}
                placeholder="Write your response here…"
                style={textAreaStyle}
              />
              <div style={wordCountStyle}>
                {countWords(value)} / {target} words
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function SpeakingSection({
  attemptId,
  payload,
  disabled,
  answers,
  onAnswer,
}: {
  attemptId: number;
  payload: SpeakingSectionPayload;
  disabled: boolean;
  answers: Record<string, SpeakingResponseValue>;
  onAnswer: (promptId: string, value: SpeakingResponseValue | null) => void;
}) {
  const prompts = payload.speaking_prompts ?? ["Describe a skill you improved."];
  return (
    <section style={panelStyle}>
      <SectionHeading
        Icon={Mic}
        title="Speaking"
        meta={`${payload.speaking_duration_seconds ?? 30}s per response`}
      />
      {prompts.length === 0 ? (
        <PlaceholderContent
          Icon={Mic}
          label="Speaking"
          sub="Recording and scoring arrive in a future phase."
        />
      ) : (
        <div style={{ display: "grid", gap: 14 }}>
          {prompts.map((prompt, index) => (
            <SpeakingRecorder
              key={`s${index + 1}`}
              attemptId={attemptId}
              promptId={`s${index + 1}`}
              prompt={prompt}
              disabled={disabled}
              durationSeconds={payload.speaking_duration_seconds ?? 30}
              index={index + 1}
              initialAnswer={answers[`s${index + 1}`]}
              onUploaded={onAnswer}
            />
          ))}
        </div>
      )}
    </section>
  );
}

function pickSpeakingMimeType(): string {
  if (typeof MediaRecorder === "undefined") return "";
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
    "audio/ogg",
    "audio/mp4",
  ];
  return candidates.find((type) => MediaRecorder.isTypeSupported(type)) ?? "";
}

function extensionForMime(mime: string): string {
  if (mime.includes("ogg")) return ".ogg";
  if (mime.includes("mp4")) return ".mp4";
  return ".webm";
}

function SpeakingRecorder({
  attemptId,
  promptId,
  prompt,
  disabled,
  durationSeconds,
  index,
  initialAnswer,
  onUploaded,
}: {
  attemptId: number;
  promptId: string;
  prompt: string;
  disabled: boolean;
  durationSeconds: number;
  index: number;
  initialAnswer?: SpeakingResponseValue;
  onUploaded: (promptId: string, value: SpeakingResponseValue | null) => void;
}) {
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const intervalRef = useRef<number | null>(null);
  const audioUrlRef = useRef<string | null>(null);
  const mimeTypeRef = useRef("audio/webm");
  const recordingStartedAtRef = useRef(0);
  const [recording, setRecording] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [localBlob, setLocalBlob] = useState<Blob | null>(null);
  const [duration, setDuration] = useState(0);
  const [uploaded, setUploaded] = useState<SpeakingResponseValue | null>(
    initialAnswer ?? null,
  );
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cleanupStream = () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (intervalRef.current != null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const setPreviewBlob = (blob: Blob) => {
    if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current);
    const nextUrl = URL.createObjectURL(blob);
    audioUrlRef.current = nextUrl;
    setAudioUrl(nextUrl);
  };

  const stopRecording = useCallback(() => {
    if (recorderRef.current && recorderRef.current.state !== "inactive") {
      recorderRef.current.stop();
    }
  }, []);

  const startRecording = async () => {
    if (disabled || recording || uploading) return;
    if (typeof MediaRecorder === "undefined") {
      setError("Recording is not supported in this browser.");
      return;
    }
    setError(null);
    chunksRef.current = [];
    setElapsed(0);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mimeType = pickSpeakingMimeType();
      mimeTypeRef.current = mimeType || "audio/webm";
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});
      recorderRef.current = recorder;
      recorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = () => {
        const recordedDuration = Math.max(
          1,
          Math.round((Date.now() - recordingStartedAtRef.current) / 1000),
        );
        const usedMime = recorder.mimeType || mimeType || "audio/webm";
        const blob = new Blob(chunksRef.current, { type: usedMime });
        mimeTypeRef.current = usedMime;
        setPreviewBlob(blob);
        setLocalBlob(blob);
        setDuration(recordedDuration);
        setUploaded(null);
        onUploaded(promptId, null);
        setRecording(false);
        cleanupStream();
      };
      recorder.start(250);
      recordingStartedAtRef.current = Date.now();
      setRecording(true);
      intervalRef.current = window.setInterval(() => {
        setElapsed((current) => {
          const next = current + 1;
          if (next >= durationSeconds) stopRecording();
          return next;
        });
      }, 1000);
    } catch {
      setRecording(false);
      cleanupStream();
      setError("Microphone permission is needed for this section.");
    }
  };

  const uploadTake = async () => {
    if (!localBlob || disabled || uploading || recording) return;
    setUploading(true);
    setError(null);
    try {
      const extension = extensionForMime(localBlob.type || mimeTypeRef.current);
      const result = await challengesApi.uploadSpeakingTake(
        attemptId,
        promptId,
        localBlob,
        `speaking-${promptId}${extension}`,
      );
      const next = {
        ...result,
        duration_seconds: duration,
      };
      setUploaded(next);
      onUploaded(promptId, next);
    } catch {
      setError("Upload failed. Please try again or re-record this prompt.");
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    return () => {
      cleanupStream();
      if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current);
    };
  }, []);

  useEffect(() => {
    setUploaded(initialAnswer ?? null);
  }, [initialAnswer?.audio_storage_key, initialAnswer]);

  useEffect(() => {
    if (!initialAnswer?.audio_url || localBlob || audioUrl) return;
    let cancelled = false;
    challengesApi
      .getAttemptAudio(initialAnswer.audio_url)
      .then((blob) => {
        if (cancelled) return;
        setPreviewBlob(blob);
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [initialAnswer?.audio_url, localBlob, audioUrl]);

  return (
    <div style={questionCardStyle}>
      <div style={questionStemStyle}>
        <span style={numberBadgeStyle}>{index}</span>
        <span>{prompt}</span>
      </div>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
        <button
          type="button"
          disabled={disabled || uploading}
          onClick={recording ? stopRecording : startRecording}
          style={{
            ...iconActionStyle,
            background: recording ? "#c0392b" : "#0070C4",
          }}
          aria-label={recording ? "Stop recording" : "Start recording"}
        >
          {recording ? <Square size={19} /> : <Mic size={19} />}
        </button>
        <div style={{ color: "#4a6880", fontSize: 14, fontWeight: 700 }}>
          {recording
            ? `${formatRemaining(elapsed)} / ${formatRemaining(durationSeconds)}`
            : uploading
              ? "Uploading take..."
              : uploaded
                ? "Uploaded for scoring"
            : audioUrl
              ? "Local recording ready"
              : "Tap to record"}
        </div>
        {audioUrl && !recording && !uploaded && (
          <button
            type="button"
            disabled={disabled || uploading}
            onClick={uploadTake}
            style={submitButtonStyle}
          >
            <Send size={15} aria-hidden />
            Use this take
          </button>
        )}
        {audioUrl && !recording && (
          <button
            type="button"
            disabled={disabled || uploading}
            onClick={startRecording}
            style={secondaryButtonStyle}
          >
            <RotateCcw size={16} aria-hidden />
            Re-record
          </button>
        )}
      </div>
      {audioUrl && <audio controls src={audioUrl} style={{ width: "100%", marginTop: 12 }} />}
      {uploaded && (
        <div style={{ ...mutedBandStyle, marginTop: 12 }}>
          Uploaded {Math.round(uploaded.size_bytes / 1024)} KB for prompt {promptId}.
        </div>
      )}
      {error && <div style={{ ...alertStyle, marginTop: 12 }}>{error}</div>}
    </div>
  );
}

function QuestionList({
  items,
  selected,
  disabled,
  onAnswer,
}: {
  items: MCQItem[];
  selected: Record<string, string>;
  disabled: boolean;
  onAnswer: (itemId: string, optionLetter: string) => void;
}) {
  return (
    <div style={{ display: "grid", gap: 22 }}>
      {items.map((item, questionIndex) => (
        <div key={item.item_id}>
          {questionIndex > 0 && <div style={qDividerStyle} />}
          <div style={questionStemStyle}>
            <span style={numberBadgeStyle}>{questionIndex + 1}</span>
            <span>{item.prompt}</span>
          </div>
          <div style={{ display: "grid", gap: 9 }}>
            {item.options.map((option, optionIndex) => {
              const letter = String.fromCharCode(65 + optionIndex);
              const isSelected = selected[item.item_id] === letter;
              return (
                <button
                  key={`${item.item_id}-${letter}`}
                  type="button"
                  disabled={disabled}
                  onClick={() => onAnswer(item.item_id, letter)}
                  style={{
                    ...optionButtonStyle,
                    borderColor: isSelected ? "#0070C4" : "#d0dde9",
                    background: isSelected
                      ? "linear-gradient(135deg, white, #d6e8f7)"
                      : "white",
                    boxShadow: isSelected
                      ? "0 4px 14px rgba(0,112,196,0.14)"
                      : undefined,
                  }}
                >
                  <span
                    style={{
                      ...optionKeyStyle,
                      background: isSelected ? "#0070C4" : "#f0f4f8",
                      color: isSelected ? "white" : "#4a6880",
                      boxShadow: isSelected
                        ? "0 2px 8px rgba(0,112,196,0.3)"
                        : undefined,
                    }}
                  >
                    {letter}
                  </span>
                  <span
                    style={{
                      color: isSelected ? "#00599e" : "#0d1f36",
                      fontWeight: isSelected ? 700 : 600,
                      fontSize: 14,
                    }}
                  >
                    {option}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

function SectionHeading({
  Icon,
  title,
  meta,
}: {
  Icon: LucideIcon;
  title: string;
  meta: string;
}) {
  return (
    <div style={sectionHeadingStyle}>
      <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
        <Icon size={18} aria-hidden style={{ color: "#0d1f36" }} />
        <h2 style={sectionTitleStyle}>{title}</h2>
      </div>
      <span style={contentCountStyle}>{meta}</span>
    </div>
  );
}

function PlaceholderContent({
  Icon,
  label,
  sub,
}: {
  Icon: LucideIcon;
  label: string;
  sub: string;
}) {
  return (
    <div style={placeholderSectionStyle}>
      <div style={placeholderIconStyle}>
        <Icon size={24} style={{ color: "#4a6880" }} aria-hidden />
      </div>
      <div style={{ fontSize: 16, fontWeight: 800, color: "#6b8099" }}>{label}</div>
      <div style={{ fontSize: 13.5, color: "#7a9ab5", fontWeight: 500 }}>{sub}</div>
    </div>
  );
}

function ResultsPanel({ attempt }: { attempt: ChallengeAttemptRead }) {
  const scores = attempt.section_scores ?? {};
  const feedbackReport = isRecord(attempt.feedback_report) ? attempt.feedback_report : {};
  const feedbackSummary =
    typeof feedbackReport.overall_summary === "string"
      ? feedbackReport.overall_summary
      : null;
  const feedbackSections = isRecord(feedbackReport.sections)
    ? feedbackReport.sections
    : {};
  const nextTips = (["reading", "writing", "speaking"] as SectionKey[])
    .map((section) => {
      const sectionFeedback = feedbackSections[section];
      if (!isRecord(sectionFeedback) || typeof sectionFeedback.next_tip !== "string") {
        return null;
      }
      return { section, tip: sectionFeedback.next_tip };
    })
    .filter((tip): tip is { section: SectionKey; tip: string } => tip !== null);

  return (
    <section style={{ ...panelStyle, marginTop: 18, borderColor: "rgba(0,112,196,0.2)" }}>
      <div style={{ display: "flex", gap: 18, flexWrap: "wrap", alignItems: "center" }}>
        <div style={scoreDialStyle}>
          <Trophy size={24} aria-hidden />
          <strong style={{ fontSize: 22, fontWeight: 800 }}>
            {attempt.overall_score?.toFixed(1) ?? "--"}
          </strong>
        </div>
        <div style={{ flex: "1 1 260px" }}>
          <h2 style={sectionTitleStyle}>
            {attempt.status === "timed_out" ? "Timed out" : "Result saved"}
          </h2>
          <p style={{ margin: "8px 0 0", color: "#4a6880", lineHeight: 1.6, fontSize: 14 }}>
            {feedbackSummary ??
              "Reading and Listening were graded from answer keys, Writing was evaluated, and Speaking was scored from transcripts only."}
          </p>
        </div>
      </div>
      <div style={scoreGridStyle}>
        {(["listening", "reading", "writing", "speaking"] as SectionKey[]).map(
          (section) => (
            <div key={section} style={scoreCellStyle}>
              <span style={{ textTransform: "capitalize", fontSize: 13, fontWeight: 700 }}>
                {section}
              </span>
              <strong style={{ color: "#0d1f36", fontSize: 15 }}>
                {scores[section]?.toFixed(1) ?? "--"}
              </strong>
            </div>
          ),
        )}
      </div>
      {nextTips.length > 0 && (
        <div style={feedbackTipGridStyle}>
          {nextTips.map(({ section, tip }) => (
            <div key={section} style={feedbackTipStyle}>
              <span
                style={{
                  textTransform: "capitalize",
                  fontSize: 12,
                  fontWeight: 800,
                  color: "#0070C4",
                  letterSpacing: "0.01em",
                }}
              >
                {section}
              </span>
              <p style={{ margin: "6px 0 0", lineHeight: 1.55, color: "#4a6880", fontSize: 13.5 }}>
                {tip}
              </p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

/* ─── Styles ─── */

const pageWrapperStyle: CSSProperties = {
  minHeight: "100vh",
  fontFamily: "var(--font-geist-sans), 'Plus Jakarta Sans', Arial, sans-serif",
  background: "#dce8f5",
  backgroundImage:
    "radial-gradient(circle, rgba(90,130,210,0.13) 1px, transparent 1px)",
  backgroundSize: "22px 22px",
  color: "#111e2e",
  overflowX: "hidden",
};

const dotGridStyle: CSSProperties = {
  position: "fixed",
  inset: 0,
  pointerEvents: "none",
  zIndex: 0,
};

const topBarStyle: CSSProperties = {
  position: "sticky",
  top: 0,
  zIndex: 50,
  backdropFilter: "blur(24px)",
  WebkitBackdropFilter: "blur(24px)",
  background: "rgba(220,232,245,0.7)",
  borderBottom: "1px solid rgba(140,170,220,0.14)",
};

const topBarInnerStyle: CSSProperties = {
  maxWidth: 1240,
  margin: "0 auto",
  padding: "12px 32px",
  display: "flex",
  alignItems: "center",
  gap: 12,
};

const backLinkStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  fontSize: 13.5,
  fontWeight: 700,
  color: "#4a6880",
  background: "transparent",
  border: "none",
  cursor: "pointer",
  padding: "6px 0",
};

const userNameStyle: CSSProperties = {
  fontSize: 13.5,
  fontWeight: 700,
  color: "#0d1f36",
};

const signOutButtonStyle: CSSProperties = {
  padding: "7px 16px",
  borderRadius: 999,
  fontSize: 13,
  fontWeight: 700,
  color: "#1e3550",
  background: "white",
  border: "1.5px solid #d0dde9",
  cursor: "pointer",
};

const mainStyle: CSSProperties = {
  position: "relative",
  zIndex: 1,
  maxWidth: 1240,
  margin: "0 auto",
  padding: "28px 32px 60px",
};

const examHeaderStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 20,
  marginBottom: 22,
};

const timerPillStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 10,
  background: "rgba(255,255,255,0.9)",
  backdropFilter: "blur(18px)",
  border: "1.5px solid rgba(255,255,255,0.92)",
  borderRadius: 16,
  padding: "12px 20px",
  boxShadow: "0 4px 18px rgba(80,110,180,0.1)",
  flexShrink: 0,
};

const timerTimeStyle: CSSProperties = {
  fontSize: 22,
  fontWeight: 800,
  letterSpacing: "-0.02em",
  fontVariantNumeric: "tabular-nums",
  lineHeight: 1,
};

const examTitleStyle: CSSProperties = {
  margin: 0,
  fontSize: 22,
  fontWeight: 800,
  letterSpacing: "-0.02em",
  color: "#0d1f36",
  lineHeight: 1.15,
};

const examSubStyle: CSSProperties = {
  margin: "4px 0 0",
  fontSize: 13,
  color: "#4a6880",
  fontWeight: 600,
  display: "flex",
  alignItems: "center",
  gap: 8,
};

const inProgressDotStyle: CSSProperties = {
  display: "inline-block",
  width: 7,
  height: 7,
  borderRadius: "50%",
  background: "#2ea87e",
  animation: "pulse 2s ease infinite",
};

const submitButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 8,
  padding: "12px 24px",
  borderRadius: 14,
  fontSize: 14.5,
  fontWeight: 800,
  background: "#0070C4",
  color: "white",
  border: "none",
  boxShadow: "0 4px 16px rgba(0,112,196,0.35)",
  cursor: "pointer",
  flexShrink: 0,
};

const tabRailStyle: CSSProperties = {
  display: "flex",
  gap: 8,
  marginBottom: 22,
  overflowX: "auto",
  paddingBottom: 2,
};

const tabButtonStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 10,
  padding: "11px 18px",
  borderRadius: 14,
  backdropFilter: "blur(12px)",
  border: "1.5px solid rgba(255,255,255,0.85)",
  cursor: "pointer",
  flexShrink: 0,
  transition: "all 0.15s",
  fontFamily: "inherit",
};

const tabIconStyle: CSSProperties = {
  width: 30,
  height: 30,
  borderRadius: 8,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  flexShrink: 0,
};

const tabBodyStyle: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  alignItems: "flex-start",
  gap: 2,
};

const tabNameStyle: CSSProperties = {
  fontSize: 14,
  fontWeight: 800,
};

const tabStatusStyle: CSSProperties = {
  fontSize: 11,
  fontWeight: 700,
  letterSpacing: "0.01em",
};

const panelStyle: CSSProperties = {
  background: "rgba(255,255,255,0.85)",
  backdropFilter: "blur(18px)",
  WebkitBackdropFilter: "blur(18px)",
  border: "1.5px solid rgba(255,255,255,0.92)",
  borderRadius: 22,
  padding: 28,
  boxShadow: "0 4px 24px rgba(80,110,180,0.1)",
};

const sectionHeadingStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 12,
  flexWrap: "wrap",
  marginBottom: 20,
  paddingBottom: 16,
  borderBottom: "1px dashed #d8e4ee",
};

const sectionTitleStyle: CSSProperties = {
  margin: 0,
  color: "#0d1f36",
  fontSize: 17,
  lineHeight: 1.3,
  fontWeight: 800,
  letterSpacing: 0,
};

const contentCountStyle: CSSProperties = {
  fontSize: 13,
  fontWeight: 700,
  color: "#4a6880",
  background: "#f0f4f8",
  padding: "4px 12px",
  borderRadius: 8,
};

const passageStyle: CSSProperties = {
  border: "1.5px solid #d0dde9",
  borderRadius: 14,
  background: "#f5f8fc",
  padding: "22px 24px",
  marginBottom: 24,
};

const passageTitleStyle: CSSProperties = {
  margin: 0,
  fontSize: 16,
  fontWeight: 800,
  color: "#0d1f36",
  marginBottom: 10,
  letterSpacing: "-0.01em",
};

const qDividerStyle: CSSProperties = {
  height: 1,
  background: "#e8eef4",
  marginBottom: 22,
};

const questionCardStyle: CSSProperties = {
  background: "white",
  border: "1.5px solid #d0dde9",
  borderRadius: 13,
  padding: 15,
};

const questionStemStyle: CSSProperties = {
  display: "flex",
  gap: 12,
  alignItems: "flex-start",
  color: "#0d1f36",
  fontSize: 15,
  fontWeight: 700,
  lineHeight: 1.5,
  marginBottom: 14,
};

const numberBadgeStyle: CSSProperties = {
  width: 28,
  height: 28,
  flex: "0 0 auto",
  display: "grid",
  placeItems: "center",
  borderRadius: 9,
  background: "#d6e8f7",
  color: "#00599e",
  fontSize: 12.5,
  fontWeight: 800,
  marginTop: 1,
};

const optionButtonStyle: CSSProperties = {
  display: "flex",
  gap: 13,
  alignItems: "center",
  textAlign: "left",
  border: "1.5px solid #d0dde9",
  borderRadius: 13,
  background: "white",
  padding: "13px 16px",
  fontSize: 14,
  lineHeight: 1.45,
  cursor: "pointer",
  width: "100%",
  fontFamily: "inherit",
  transition: "all 0.14s",
};

const optionKeyStyle: CSSProperties = {
  width: 30,
  height: 30,
  display: "grid",
  placeItems: "center",
  borderRadius: 9,
  fontSize: 13,
  fontWeight: 800,
  flex: "0 0 auto",
  transition: "all 0.14s",
};

const textAreaStyle: CSSProperties = {
  width: "100%",
  boxSizing: "border-box",
  border: "1.5px solid #d0dde9",
  borderRadius: 14,
  padding: "16px 18px",
  color: "#0d1f36",
  font: "inherit",
  fontSize: 14,
  fontWeight: 500,
  lineHeight: 1.7,
  resize: "vertical",
  minHeight: 190,
  background: "#f5f8fc",
  outline: "none",
};

const wordCountStyle: CSSProperties = {
  display: "flex",
  justifyContent: "flex-end",
  marginTop: 10,
  color: "#4a6880",
  fontSize: 12,
  fontWeight: 600,
};

const mutedBandStyle: CSSProperties = {
  background: "#f5f8fc",
  border: "1.5px solid #d0dde9",
  borderRadius: 14,
  padding: "22px 24px",
  marginBottom: 18,
};

const transcriptStyle: CSSProperties = {
  background: "#0f1e30",
  color: "#edf5ff",
  borderRadius: 14,
  padding: "16px 18px",
  lineHeight: 1.65,
  marginBottom: 18,
  fontSize: 14,
};

const audioPlayerStyle: CSSProperties = {
  background: "#f5f8fc",
  border: "1.5px solid #d0dde9",
  borderRadius: 14,
  padding: "18px 20px",
  marginBottom: 18,
};

const audioProgressTrackStyle: CSSProperties = {
  width: "100%",
  height: 9,
  borderRadius: 999,
  background: "#dbe6f0",
  overflow: "hidden",
  marginTop: 16,
};

const audioProgressFillStyle: CSSProperties = {
  height: "100%",
  borderRadius: 999,
  background: "#0070C4",
  transition: "width 0.15s linear",
};

const placeholderSectionStyle: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  padding: "60px 20px",
  gap: 12,
  textAlign: "center",
};

const placeholderIconStyle: CSSProperties = {
  width: 52,
  height: 52,
  borderRadius: 16,
  background: "#f0f4f8",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  marginBottom: 4,
};

const secondaryButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 7,
  border: "1.5px solid #d0dde9",
  borderRadius: 10,
  background: "white",
  color: "#0d1f36",
  padding: "9px 14px",
  fontSize: 13,
  fontWeight: 700,
  cursor: "pointer",
  fontFamily: "inherit",
};

const iconActionStyle: CSSProperties = {
  width: 48,
  height: 48,
  display: "grid",
  placeItems: "center",
  border: "1px solid transparent",
  borderRadius: 12,
  color: "white",
  cursor: "pointer",
  flexShrink: 0,
};

const alertStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  background: "#fff8e6",
  border: "1px solid #ffd08a",
  color: "#68430a",
  borderRadius: 12,
  padding: "12px 16px",
  fontSize: 14,
  fontWeight: 700,
};

const scoreDialStyle: CSSProperties = {
  width: 110,
  height: 110,
  borderRadius: "50%",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: 6,
  background: "#d6e8f7",
  color: "#0070C4",
};

const scoreGridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
  gap: 10,
  marginTop: 18,
};

const scoreCellStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 10,
  border: "1.5px solid #d0dde9",
  borderRadius: 12,
  padding: "12px 14px",
  color: "#4a6880",
  background: "white",
};

const feedbackTipGridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  gap: 10,
  marginTop: 14,
};

const feedbackTipStyle: CSSProperties = {
  border: "1.5px solid #d0dde9",
  borderRadius: 12,
  padding: "14px 16px",
  color: "#0d1f36",
  background: "white",
  fontSize: 14,
};
