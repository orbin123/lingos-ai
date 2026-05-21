"use client";

import { useEffect, useRef, useState } from "react";
import { TaskHeader, I } from "./shared";
import { formatDuration, resolveAudioUrl } from "./types";
import type {
  ListenAndRespondPayload,
  MCQItem,
  OpenTextItem,
  WidgetProps,
} from "./types";

type Props = WidgetProps<ListenAndRespondPayload>;

interface ListenAnalytics {
  play_count: number;
  total_listen_seconds: number;
  transcript_revealed: boolean;
}

interface ListenAndRespondAnswers {
  listen_analytics?: ListenAnalytics;
  inner_response?: {
    widget: string;
    answers?: Array<Record<string, unknown>>;
  };
  time_spent_seconds?: number;
}

export function ListenAndRespondWidget({ payload, answers, setAnswers, state, onSubmit }: Props) {
  const submitted = state === "after";
  const audioRef = useRef<HTMLAudioElement>(null);
  const startedAtRef = useRef(Date.now());
  const playStartedAtRef = useRef<number | null>(null);
  const [playCount, setPlayCount] = useState(0);
  const [totalListenSeconds, setTotalListenSeconds] = useState(0);
  const [unlocked, setUnlocked] = useState(submitted);
  const [hasPlayedFull, setHasPlayedFull] = useState(submitted);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [actualDuration, setActualDuration] = useState(0);
  const [transcriptOpen, setTranscriptOpen] = useState(false);
  const [transcriptRevealed, setTranscriptRevealed] = useState(false);
  const duration =
    actualDuration ||
    audioRef.current?.duration ||
    payload.audio_duration_seconds ||
    0;
  const audioUrl = resolveAudioUrl(payload.audio_url);

  const innerWidget = payload.inner_widget;
  const items: Array<MCQItem | OpenTextItem> = payload.items ?? [];
  const mcqItems = innerWidget === "mcq" ? (items as MCQItem[]) : [];
  const openTextItems = innerWidget === "open_text" ? (items as OpenTextItem[]) : [];

  const [mcqSelections, setMcqSelections] = useState<Record<string, number>>({});
  const [openTextValues, setOpenTextValues] = useState<Record<string, string>>({});

  const publish = (
    overrides: Partial<{
      mcq: Record<string, number>;
      openText: Record<string, string>;
      analytics: ListenAnalytics;
    }> = {},
  ) => {
    const mcq = overrides.mcq ?? mcqSelections;
    const ot = overrides.openText ?? openTextValues;
    const analytics: ListenAnalytics = overrides.analytics ?? {
      play_count: playCount,
      total_listen_seconds: Math.round(totalListenSeconds),
      transcript_revealed: transcriptRevealed,
    };

    let innerResponse: ListenAndRespondAnswers["inner_response"];
    if (innerWidget === "mcq") {
      innerResponse = {
        widget: "mcq",
        answers: mcqItems
          .filter((it) => mcq[it.item_id] !== undefined)
          .map((it) => ({
            item_id: it.item_id,
            selected_index: mcq[it.item_id],
          })),
      };
    } else if (innerWidget === "open_text") {
      innerResponse = {
        widget: "open_text",
        answers: openTextItems
          .filter((it) => (ot[it.item_id] ?? "").trim().length > 0)
          .map((it) => ({
            item_id: it.item_id,
            user_answer: ot[it.item_id],
          })),
      };
    } else {
      innerResponse = { widget: innerWidget };
    }

    setAnswers({
      listen_analytics: {
        play_count: analytics.play_count,
        total_listen_seconds: Math.round(analytics.total_listen_seconds),
        transcript_revealed: analytics.transcript_revealed,
      },
      inner_response: innerResponse,
      time_spent_seconds: Math.round((Date.now() - startedAtRef.current) / 1000),
    });
  };

  const commitListenSeconds = () => {
    if (playStartedAtRef.current == null) return totalListenSeconds;
    const next = totalListenSeconds + (Date.now() - playStartedAtRef.current) / 1000;
    playStartedAtRef.current = null;
    setTotalListenSeconds(next);
    return next;
  };

  const togglePlay = async () => {
    const audio = audioRef.current;
    if (!audio || !audioUrl) return;
    if (isPlaying) {
      audio.pause();
    } else {
      await audio.play();
    }
  };

  const selectMCQ = (itemId: string, optionIndex: number) => {
    if (submitted) return;
    const next = { ...mcqSelections, [itemId]: optionIndex };
    setMcqSelections(next);
    publish({ mcq: next });
  };

  const setOpenTextValue = (itemId: string, value: string) => {
    if (submitted) return;
    const next = { ...openTextValues, [itemId]: value };
    setOpenTextValues(next);
    publish({ openText: next });
  };

  const toggleTranscript = () => {
    setTranscriptOpen((o) => {
      const next = !o;
      if (next && !transcriptRevealed) {
        setTranscriptRevealed(true);
        publish({
          analytics: {
            play_count: playCount,
            total_listen_seconds: Math.round(totalListenSeconds),
            transcript_revealed: true,
          },
        });
      }
      return next;
    });
  };

  const allInnerAnswered = (() => {
    if (innerWidget === "mcq") {
      return mcqItems.length > 0 && mcqItems.every((it) => mcqSelections[it.item_id] !== undefined);
    }
    if (innerWidget === "open_text") {
      return (
        openTextItems.length > 0 &&
        openTextItems.every((it) => (openTextValues[it.item_id] ?? "").trim().length >= 5)
      );
    }
    return true;
  })();

  const canSubmit = !submitted && unlocked && allInnerAnswered;

  useEffect(() => {
    if (submitted && !unlocked) setUnlocked(true);
  }, [submitted, unlocked]);

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Listening Task"
        intro={{
          title: payload.task_intro || "Listen, then respond",
          body: payload.instructions || "Play the clip first — the questions unlock after the first play-through.",
        }}
        sub_skill={payload.sub_skill || ""}
        activity={payload.activity || "Listen → respond"}
        time={payload.estimated_time_minutes ?? 0}
      />

      <div className="tw-audio-player">
        <audio
          ref={audioRef}
          src={audioUrl}
          preload="metadata"
          onLoadedMetadata={(e) => setActualDuration(e.currentTarget.duration)}
          onPlay={() => {
            setIsPlaying(true);
            setPlayCount((c) => {
              const next = c + 1;
              publish({
                analytics: {
                  play_count: next,
                  total_listen_seconds: Math.round(totalListenSeconds),
                  transcript_revealed: transcriptRevealed,
                },
              });
              return next;
            });
            playStartedAtRef.current = Date.now();
          }}
          onPause={() => {
            setIsPlaying(false);
            const next = commitListenSeconds();
            publish({
              analytics: {
                play_count: playCount,
                total_listen_seconds: Math.round(next),
                transcript_revealed: transcriptRevealed,
              },
            });
          }}
          onEnded={() => {
            setIsPlaying(false);
            setHasPlayedFull(true);
            setUnlocked(true);
            const next = commitListenSeconds();
            publish({
              analytics: {
                play_count: playCount,
                total_listen_seconds: Math.round(next),
                transcript_revealed: transcriptRevealed,
              },
            });
          }}
          onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
        />
        <button
          className={`tw-audio-play-btn${isPlaying ? " playing" : ""}`}
          onClick={togglePlay}
          disabled={!audioUrl}
          aria-label={isPlaying ? "Pause audio" : "Play audio"}
        >
          {isPlaying ? I.pause : I.play}
        </button>
        <div className="tw-audio-info">
          <div className="tw-audio-title">
            {payload.topic_name || "Audio clip"}
          </div>
          <div className="tw-audio-meta">
            {payload.audio_genre ? `${payload.audio_genre} · ` : ""}
            {duration ? `${formatDuration(duration)} total` : "loading…"} · plays: {playCount}
          </div>
        </div>
        <div className="tw-audio-wave">
          {Array.from({ length: 42 }).map((_, i) => {
            const active = duration ? i / 42 <= currentTime / duration : false;
            const h = 6 + Math.abs(Math.sin(i * 0.6) * 18) + (i % 4) * 1.5;
            return (
              <span
                key={i}
                className={`tw-audio-wave-bar${active ? " played" : ""}`}
                style={{ height: h }}
              />
            );
          })}
        </div>
        <div className="tw-audio-time">
          {formatDuration(currentTime)} / {formatDuration(duration)}
        </div>
      </div>

      <div className="tw-listen-controls">
        {submitted && (
          <button
            className={`tw-transcript-toggle${transcriptOpen ? " on" : ""}`}
            onClick={toggleTranscript}
          >
            {I.doc} {transcriptOpen ? "Hide transcript" : "Show transcript"}
          </button>
        )}
        {!unlocked && !submitted && (
          <button className="tw-skip-task" onClick={() => setUnlocked(true)}>
            Skip to task →
          </button>
        )}
      </div>

      {transcriptOpen && payload.audio_script && (
        <div className="tw-transcript-box">{payload.audio_script}</div>
      )}

      {!unlocked && !submitted && (
        <div
          style={{
            borderRadius: 12,
            background: "oklch(96% 0.03 60)",
            color: "oklch(42% 0.12 60)",
            padding: "10px 12px",
            fontSize: 13,
            fontWeight: 750,
            marginBottom: 16,
          }}
        >
          Listen to the full audio once to unlock the questions.
        </div>
      )}

      {(unlocked || submitted) && innerWidget === "mcq" && (
        <div
          className={!unlocked && !submitted ? "tw-locked-veil" : ""}
          style={{ position: "relative" }}
        >
          <div
            style={{
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              color: "var(--tw-ink-muted)",
              marginBottom: 8,
              display: "flex",
              alignItems: "center",
              gap: 6,
            }}
          >
            {I.ear} Inner task · Multiple choice ({mcqItems.length} questions)
          </div>
          {mcqItems.map((item, qi) => {
            const selected = mcqSelections[item.item_id];
            return (
              <div className="tw-card" key={item.item_id}>
                <div className="tw-q-number-row">
                  <div className="tw-q-number-badge">{qi + 1}</div>
                  <div className="tw-q-stem">{item.prompt}</div>
                </div>
                <div className="tw-opt-list">
                  {item.options.map((option, oi) => {
                    let cls = "tw-opt-row";
                    if (state === "before" && selected === oi) cls += " selected";
                    else if (submitted) {
                      if (oi === item.correct_index) cls += " correct";
                      else if (oi === selected && oi !== item.correct_index) cls += " wrong";
                    }
                    return (
                      <button
                        key={oi}
                        className={cls}
                        disabled={submitted}
                        onClick={() => selectMCQ(item.item_id, oi)}
                      >
                        <span className="tw-opt-key">{String.fromCharCode(65 + oi)}</span>
                        <span style={{ flex: 1 }}>{option}</span>
                        {submitted && oi === item.correct_index && (
                          <span style={{ color: "var(--tw-green)" }}>{I.check}</span>
                        )}
                      </button>
                    );
                  })}
                </div>
                {submitted && (
                  <div className="tw-fb-explain" style={{ marginTop: 10 }}>
                    {item.explanation}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {(unlocked || submitted) && innerWidget === "open_text" && (
        <div>
          <div
            style={{
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              color: "var(--tw-ink-muted)",
              marginBottom: 8,
              display: "flex",
              alignItems: "center",
              gap: 6,
            }}
          >
            {I.ear} Inner task · Open text
          </div>
          {openTextItems.map((item, qi) => {
            const val = openTextValues[item.item_id] ?? "";
            return (
              <div className="tw-card" key={item.item_id}>
                <div className="tw-q-number-row">
                  <div className="tw-q-number-badge">{qi + 1}</div>
                  <div className="tw-q-stem">{item.prompt}</div>
                </div>
                {!submitted ? (
                  <textarea
                    className="tw-write-area"
                    value={val}
                    onChange={(e) => setOpenTextValue(item.item_id, e.target.value)}
                    rows={3}
                    placeholder="Type your response…"
                  />
                ) : (
                  <div className="tw-compare-grid">
                    <div className="tw-compare-card">
                      <div className="tw-compare-label">{I.doc} Your answer</div>
                      <div className="tw-compare-body">{val || "—"}</div>
                    </div>
                    <div className="tw-compare-card sample">
                      <div className="tw-compare-label">{I.spark} Sample answer</div>
                      <div className="tw-compare-body">{item.sample_answer}</div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {(unlocked || submitted) && innerWidget === "speak_and_record" && (
        <div className="tw-card" style={{ borderStyle: "dashed" }}>
          <div className="tw-rule-label">Shadowing exercise</div>
          <div style={{ fontSize: 13, color: "var(--tw-navy)", lineHeight: 1.55, marginTop: 6 }}>
            {payload.text_to_shadow ?? "Repeat after the audio."}
          </div>
          {payload.delay_seconds != null && (
            <div style={{ fontSize: 12, color: "var(--tw-ink-muted)", marginTop: 8 }}>
              Delay: {payload.delay_seconds}s · Speed: {payload.speed ?? "natural"}
            </div>
          )}
        </div>
      )}

      {submitted && (
        <div className="tw-analytics-grid" style={{ marginTop: 14 }}>
          <div className="tw-metric">
            <div className="tw-metric-num primary">{playCount}</div>
            <div className="tw-metric-label">Plays</div>
          </div>
          <div className="tw-metric">
            <div className="tw-metric-num">{transcriptRevealed ? "Yes" : "No"}</div>
            <div className="tw-metric-label">Transcript</div>
          </div>
          <div className="tw-metric">
            <div className="tw-metric-num" style={{ color: "var(--tw-green)" }}>
              {formatDuration(totalListenSeconds)}
            </div>
            <div className="tw-metric-label">Listened</div>
          </div>
        </div>
      )}

      {!submitted && (
        <button
          className="tw-submit-btn"
          disabled={!canSubmit}
          onClick={onSubmit}
        >
          {I.send} Submit listening answers
        </button>
      )}

      {/* hint: track hasPlayedFull lifecycle */}
      <span data-played-full={hasPlayedFull ? "1" : "0"} style={{ display: "none" }} />
    </div>
  );
}
