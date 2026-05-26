"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { TaskHeader, I } from "./shared";
import { formatDuration, resolveAudioUrl } from "./types";
import {
  analyticsFromListenAnswers,
  blanksFromListenAnswers,
  countCorrectListeningBlanks,
  countCorrectListeningMCQ,
  isPlayableListeningTask,
  normalizeListenAndRespondPayload,
  openTextFromListenAnswers,
  selectionsFromListenAnswers,
  type ListenAnalytics,
  type ListenAndRespondAnswers,
} from "./listenAndRespondNormalize";
import type {
  BlankItem,
  ListenAndRespondPayload,
  MCQItem,
  OpenTextItem,
  WidgetProps,
} from "./types";

type Props = WidgetProps<ListenAndRespondPayload>;

function nowMs(): number {
  return Date.now();
}

function blankKey(blank: BlankItem): string {
  return blank.item_id || blank.blank_id || blank.sentence_with_blank;
}

function isBlankCorrect(blank: BlankItem, value: string): boolean {
  return value.trim().toLowerCase() === blank.correct_answer.trim().toLowerCase();
}

function agentDebugLog(message: string, data: Record<string, unknown>, hypothesisId: string) {
  // #region agent log
  fetch('http://127.0.0.1:7588/ingest/7b2f1294-46b7-45e6-9e45-9caa7b81d367',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'dfa507'},body:JSON.stringify({sessionId:'dfa507',runId:'initial',hypothesisId,location:'frontend/src/components/task/task-widgets/ListenAndRespondWidget.tsx',message,data,timestamp:Date.now()})}).catch(()=>{});
  // #endregion
}

export function ListenAndRespondWidget({ payload: rawPayload, answers, setAnswers, state, onSubmit }: Props) {
  const payload = useMemo(
    () => normalizeListenAndRespondPayload(rawPayload),
    [rawPayload],
  );
  const submitted = state === "after";
  const initialAnalytics = useMemo(() => analyticsFromListenAnswers(answers), [answers]);
  const audioRef = useRef<HTMLAudioElement>(null);
  const startedAtRef = useRef<number | null>(null);
  const playStartedAtRef = useRef<number | null>(null);
  const browserTtsTimerRef = useRef<number | null>(null);
  const browserTtsStartedAtRef = useRef<number | null>(null);
  const [playCount, setPlayCount] = useState(initialAnalytics.play_count);
  const [totalListenSeconds, setTotalListenSeconds] = useState(
    initialAnalytics.total_listen_seconds,
  );
  const [unlocked, setUnlocked] = useState(submitted);
  const [hasPlayedFull, setHasPlayedFull] = useState(submitted);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [actualDuration, setActualDuration] = useState(0);
  const [transcriptOpen, setTranscriptOpen] = useState(false);
  const [transcriptRevealed, setTranscriptRevealed] = useState(
    initialAnalytics.transcript_revealed,
  );
  const [audioLoadFailed, setAudioLoadFailed] = useState(false);
  const duration =
    actualDuration ||
    payload.audio_duration_seconds ||
    0;
  const audioUrl = resolveAudioUrl(payload.audio_url);
  const canUseBrowserTTS =
    !audioUrl &&
    typeof window !== "undefined" &&
    "speechSynthesis" in window &&
    "SpeechSynthesisUtterance" in window &&
    !!payload.audio_script?.trim();

  const innerWidget = payload.inner_widget;
  const items: Array<MCQItem | OpenTextItem | BlankItem> = payload.items ?? [];
  const blankItems = innerWidget === "fill_in_blanks"
    ? ((payload.items ?? payload.blanks ?? []) as BlankItem[])
    : [];
  const mcqItems = innerWidget === "mcq" ? (items as MCQItem[]) : [];
  const openTextItems = innerWidget === "open_text" ? (items as OpenTextItem[]) : [];
  const playableTask =
    isPlayableListeningTask(payload) &&
    !audioLoadFailed &&
    (!!audioUrl || canUseBrowserTTS);
  const taskBlocked = !playableTask;
  const blockReason = (() => {
    if (!payload.audio_url && !canUseBrowserTTS) return "Audio could not be prepared for this listening task.";
    if (audioLoadFailed) return "Audio could not load. Please restart the activity or try again later.";
    if (innerWidget === "mcq" && mcqItems.length === 0) return "No multiple-choice questions were provided for this listening task.";
    if (innerWidget === "fill_in_blanks" && blankItems.length === 0) return "No blanks were provided for this listening task.";
    if (innerWidget !== "mcq" && innerWidget !== "fill_in_blanks" && innerWidget !== "open_text" && innerWidget !== "speak_and_record") return "This listening task is not configured correctly.";
    return "";
  })();

  useEffect(() => {
    agentDebugLog(
      "Listen widget render decision",
      {
        raw_audio_url: rawPayload.audio_url,
        normalized_audio_url: payload.audio_url,
        resolved_audio_url: audioUrl,
        browser_tts_fallback: payload.browser_tts_fallback,
        can_use_browser_tts: canUseBrowserTTS,
        audio_script_len: payload.audio_script?.length ?? 0,
        inner_widget: innerWidget,
        items_len: mcqItems.length,
        blanks_len: blankItems.length,
        audio_load_failed: audioLoadFailed,
        playable_task: playableTask,
        task_blocked: taskBlocked,
        block_reason: blockReason,
        tts_error: payload.tts_error,
      },
      "H2,H3,H4",
    );
  }, [rawPayload, payload, audioUrl, canUseBrowserTTS, innerWidget, mcqItems.length, blankItems.length, audioLoadFailed, playableTask, taskBlocked, blockReason]);

  const [mcqSelections, setMcqSelections] = useState<Record<string, number>>(
    () => selectionsFromListenAnswers(answers),
  );
  const [openTextValues, setOpenTextValues] = useState<Record<string, string>>(
    () => openTextFromListenAnswers(answers),
  );
  const [blankValues, setBlankValues] = useState<Record<string, string>>(
    () => blanksFromListenAnswers(answers),
  );

  const startedAt = () => {
    if (startedAtRef.current == null) {
      startedAtRef.current = nowMs();
    }
    return startedAtRef.current;
  };

  const publish = (
    overrides: Partial<{
      mcq: Record<string, number>;
      openText: Record<string, string>;
      blanks: Record<string, string>;
      analytics: ListenAnalytics;
    }> = {},
  ) => {
    const mcq = overrides.mcq ?? mcqSelections;
    const ot = overrides.openText ?? openTextValues;
    const blankMap = overrides.blanks ?? blankValues;
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
    } else if (innerWidget === "fill_in_blanks") {
      innerResponse = {
        widget: "fill_in_blanks",
        answers: blankItems
          .filter((it) => (blankMap[blankKey(it)] ?? "").trim().length > 0)
          .map((it) => ({
            item_id: blankKey(it),
            user_answer: blankMap[blankKey(it)],
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
      time_spent_seconds: Math.round((nowMs() - startedAt()) / 1000),
    });
  };

  const commitListenSeconds = () => {
    if (playStartedAtRef.current == null) return totalListenSeconds;
    const next = totalListenSeconds + (nowMs() - playStartedAtRef.current) / 1000;
    playStartedAtRef.current = null;
    setTotalListenSeconds(next);
    return next;
  };

  const stopBrowserTTS = () => {
    if (browserTtsTimerRef.current != null) {
      window.clearInterval(browserTtsTimerRef.current);
      browserTtsTimerRef.current = null;
    }
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    browserTtsStartedAtRef.current = null;
    setIsPlaying(false);
  };

  const playBrowserTTS = () => {
    if (!canUseBrowserTTS || !payload.audio_script) return;
    window.speechSynthesis.cancel();
    const utterance = new window.SpeechSynthesisUtterance(payload.audio_script);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.onend = () => {
      if (browserTtsTimerRef.current != null) {
        window.clearInterval(browserTtsTimerRef.current);
        browserTtsTimerRef.current = null;
      }
      const startedAtMs = browserTtsStartedAtRef.current ?? nowMs();
      const listenedSeconds = Math.max(
        duration,
        (nowMs() - startedAtMs) / 1000,
      );
      browserTtsStartedAtRef.current = null;
      setIsPlaying(false);
      setCurrentTime(duration || listenedSeconds);
      setTotalListenSeconds((prev) => prev + listenedSeconds);
      setHasPlayedFull(true);
      setUnlocked(true);
      publish({
        analytics: {
          play_count: playCount + 1,
          total_listen_seconds: Math.round(totalListenSeconds + listenedSeconds),
          transcript_revealed: transcriptRevealed,
        },
      });
    };
    utterance.onerror = () => {
      setAudioLoadFailed(true);
      stopBrowserTTS();
    };
    browserTtsStartedAtRef.current = nowMs();
    setCurrentTime(0);
    setIsPlaying(true);
    setPlayCount((count) => count + 1);
    browserTtsTimerRef.current = window.setInterval(() => {
      const startedAtMs = browserTtsStartedAtRef.current;
      if (startedAtMs == null) return;
      const elapsed = (nowMs() - startedAtMs) / 1000;
      setCurrentTime(duration ? Math.min(duration, elapsed) : elapsed);
    }, 250);
    window.speechSynthesis.speak(utterance);
  };

  const togglePlay = async () => {
    if (canUseBrowserTTS) {
      if (isPlaying) {
        stopBrowserTTS();
      } else {
        playBrowserTTS();
      }
      return;
    }
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

  const setBlankValue = (blank: BlankItem, value: string) => {
    if (submitted) return;
    const key = blankKey(blank);
    const next = { ...blankValues, [key]: value };
    setBlankValues(next);
    publish({ blanks: next });
  };

  const toggleTranscript = () => {
    const nextTranscriptOpen = !transcriptOpen;
    setTranscriptOpen(nextTranscriptOpen);
    if (nextTranscriptOpen && !transcriptRevealed) {
      setTranscriptRevealed(true);
      publish({
        analytics: {
          play_count: playCount,
          total_listen_seconds: Math.round(totalListenSeconds),
          transcript_revealed: true,
        },
      });
    }
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
    if (innerWidget === "fill_in_blanks") {
      return (
        blankItems.length > 0 &&
        blankItems.every((it) => (blankValues[blankKey(it)] ?? "").trim().length > 0)
      );
    }
    return true;
  })();

  const questionsUnlocked = submitted || unlocked;
  const canSubmit = !submitted && questionsUnlocked && allInnerAnswered;
  const canSubmitListening = canSubmit && playableTask && hasPlayedFull;
  const correctCount = innerWidget === "mcq"
    ? countCorrectListeningMCQ(mcqItems, mcqSelections)
    : innerWidget === "fill_in_blanks"
      ? countCorrectListeningBlanks(blankItems, blankValues)
    : 0;
  const resultTotal = innerWidget === "fill_in_blanks" ? blankItems.length : mcqItems.length;
  const resultPct = resultTotal > 0
    ? Math.round((correctCount / resultTotal) * 100)
    : 0;

  useEffect(() => {
    const reset = window.setTimeout(() => {
      stopBrowserTTS();
      setAudioLoadFailed(false);
      setCurrentTime(0);
      setActualDuration(0);
      if (!submitted) {
        setUnlocked(false);
        setHasPlayedFull(false);
      }
    }, 0);
    return () => window.clearTimeout(reset);
  }, [audioUrl, submitted]);

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
          onLoadedMetadata={(e) => {
            const nextDuration = e.currentTarget.duration;
            setActualDuration(Number.isFinite(nextDuration) ? nextDuration : 0);
          }}
          onError={() => {
            agentDebugLog(
              "Audio element failed to load",
              {
                raw_audio_url: rawPayload.audio_url,
                resolved_audio_url: audioUrl,
                browser_tts_fallback: payload.browser_tts_fallback,
                audio_script_len: payload.audio_script?.length ?? 0,
              },
              "H4",
            );
            setAudioLoadFailed(true);
            setIsPlaying(false);
            commitListenSeconds();
          }}
          onPlay={() => {
            setIsPlaying(true);
            const nextPlayCount = playCount + 1;
            setPlayCount(nextPlayCount);
            publish({
              analytics: {
                play_count: nextPlayCount,
                total_listen_seconds: Math.round(totalListenSeconds),
                transcript_revealed: transcriptRevealed,
              },
            });
            playStartedAtRef.current = nowMs();
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
          disabled={(!audioUrl && !canUseBrowserTTS) || audioLoadFailed}
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
            {duration
              ? `${formatDuration(duration)} total`
              : (audioUrl && !audioLoadFailed ? "loading…" : canUseBrowserTTS ? "browser voice" : "unavailable")} · plays: {playCount}
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
      </div>

      {transcriptOpen && payload.audio_script && (
        <div className="tw-transcript-box">{payload.audio_script}</div>
      )}

      {taskBlocked && !submitted && (
        <div
          style={{
            borderRadius: 12,
            background: "oklch(96% 0.035 25)",
            color: "oklch(42% 0.16 25)",
            padding: "10px 12px",
            fontSize: 13,
            fontWeight: 750,
            marginBottom: 16,
          }}
        >
          {blockReason}
        </div>
      )}

      {!taskBlocked && !questionsUnlocked && !submitted && (
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

      {questionsUnlocked && innerWidget === "mcq" && (
        <div
          className={!questionsUnlocked ? "tw-locked-veil" : ""}
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

      {questionsUnlocked && innerWidget === "open_text" && (
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

      {questionsUnlocked && innerWidget === "fill_in_blanks" && (
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
            {I.ear} Inner task · Fill in the blanks ({blankItems.length} blanks)
          </div>
          <div className="tw-passage">
            {payload.passage_title && (
              <div className="tw-passage-label">{payload.passage_title}</div>
            )}
            {payload.passage && payload.passage.includes("___") ? (
              payload.passage.split("___").map((part, index) => {
                const blank = blankItems[index];
                const value = blank ? blankValues[blankKey(blank)] ?? "" : "";
                const correct = blank ? isBlankCorrect(blank, value) : false;
                return (
                  <span key={`listen-blank-part-${index}`}>
                    {part}
                    {blank && (
                      <span
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: 6,
                          margin: "0 4px",
                          verticalAlign: "baseline",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {!submitted ? (
                          <input
                            aria-label={`Blank ${index + 1}`}
                            value={value}
                            onChange={(e) => setBlankValue(blank, e.target.value)}
                            placeholder="answer"
                            className="tw-blank-input"
                            style={{
                              width: "clamp(88px, 18vw, 150px)",
                              textAlign: "center",
                            }}
                          />
                        ) : (
                          <>
                            <span
                              style={{
                                padding: "3px 10px",
                                borderRadius: 6,
                                background: correct ? "#dcfce7" : "#fee2e2",
                                color: correct ? "#16a34a" : "#dc2626",
                                fontWeight: 700,
                                fontSize: 14,
                                textDecoration: correct ? "none" : "line-through",
                              }}
                            >
                              {value || "—"}
                            </span>
                            {!correct && (
                              <span
                                style={{
                                  padding: "3px 10px",
                                  borderRadius: 6,
                                  background: "#dcfce7",
                                  color: "#16a34a",
                                  fontWeight: 700,
                                  fontSize: 14,
                                }}
                              >
                                {blank.correct_answer}
                              </span>
                            )}
                          </>
                        )}
                      </span>
                    )}
                  </span>
                );
              })
            ) : (
              blankItems.map((blank, index) => {
                const value = blankValues[blankKey(blank)] ?? "";
                const sentenceParts = blank.sentence_with_blank.split("___");
                return (
                  <div key={blankKey(blank)} style={{ marginBottom: 8 }}>
                    <span style={{ fontWeight: 700, marginRight: 6, color: "var(--tw-primary)" }}>
                      {index + 1}.
                    </span>
                    {sentenceParts[0]}
                    <input
                      aria-label={`Blank ${index + 1}`}
                      value={value}
                      onChange={(e) => setBlankValue(blank, e.target.value)}
                      disabled={submitted}
                      placeholder="answer"
                      className="tw-blank-input"
                      style={{
                        width: "clamp(88px, 18vw, 150px)",
                        textAlign: "center",
                        margin: "0 4px",
                      }}
                    />
                    {sentenceParts[1] ?? ""}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}

      {questionsUnlocked && innerWidget === "speak_and_record" && (
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

      {submitted && (innerWidget === "mcq" || innerWidget === "fill_in_blanks") && resultTotal > 0 && (
        <div
          className={`tw-result-banner ${correctCount === resultTotal ? "good" : "mid"}`}
          style={{ marginTop: 14 }}
        >
          <div className="tw-result-icon">{I.spark}</div>
          <div className="tw-result-text">
            <div className="tw-result-headline">
              {correctCount} of {resultTotal} answers correct
            </div>
            <div className="tw-result-sub">Review the explanations above.</div>
          </div>
          <div>
            <div className="tw-result-score">
              {resultPct}
              <span style={{ fontSize: 14, color: "var(--tw-ink-muted)" }}>%</span>
            </div>
            <div className="tw-result-score-sub">Score</div>
          </div>
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
          disabled={!canSubmitListening}
          onClick={() => onSubmit()}
        >
          {I.send} Submit listening answers
        </button>
      )}

      {/* hint: track hasPlayedFull lifecycle */}
      <span data-played-full={hasPlayedFull ? "1" : "0"} style={{ display: "none" }} />
    </div>
  );
}
