"use client";

import { useEffect, useState } from "react";
import { Check, Pause, Play, Volume2, X } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { ListenToneTask, LiveTaskController } from "../source";
import {
  ListeningAudioCard,
  liveMcqAnswerRecord,
  McqOptionList,
  mcqSubmission,
  ResultBanner,
  RuleCallout,
  SubmitButton,
  TaskWidgetFrame,
  roundIconButton,
} from "./TaskWidgetFrame";

export function ListenToneTaskWidget({
  task,
  previewState,
  live,
}: {
  task: ListenToneTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  if (live) {
    return <LiveListenTone task={task} live={live} />;
  }
  return <PreviewListenTone task={task} previewState={previewState} />;
}

function LiveListenTone({ task, live }: { task: ListenToneTask; live: LiveTaskController }) {
  const [audioComplete, setAudioComplete] = useState(false);
  const unlocked = live.submitted || audioComplete;
  const interactive = !live.submitted && unlocked;
  const showResults = live.submitted;
  const answers = liveMcqAnswerRecord(live.answers);
  const allAnswered = task.items.every((item) => answers[item.itemId] !== undefined);

  const pick = (itemId: string, optionIndex: number) => {
    live.setAnswers({ ...live.answers, [itemId]: optionIndex });
  };

  return (
    <TaskWidgetFrame task={task} icon={<Volume2 size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Tone focus">{task.grammarRule}</RuleCallout>

      <ListeningAudioCard
        title={task.audioGenre || "Audio"}
        script={task.audioScript || ""}
        audioUrl={task.audioUrl}
        durationSeconds={task.audioDurationSeconds || 0}
        completed={unlocked}
        hint="Listen once to unlock the questions below."
        onComplete={() => setAudioComplete(true)}
      />

      {unlocked &&
        task.items.map((item, index) => (
          <div className="tw-card" key={item.itemId}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">{item.prompt}</div>
            </div>
            <McqOptionList
              item={item}
              selected={answers[item.itemId]}
              interactive={interactive}
              showResults={showResults}
              onPick={(optionIndex) => pick(item.itemId, optionIndex)}
            />
          </div>
        ))}

      {interactive && (
        <SubmitButton
          disabled={!allAnswered}
          onClick={() => live.onSubmit(mcqSubmission(task.items, answers))}
        />
      )}
    </TaskWidgetFrame>
  );
}

function PreviewListenTone({
  task,
  previewState,
}: {
  task: ListenToneTask;
  previewState: SessionPreviewState;
}) {
  const [playingId, setPlayingId] = useState<string | null>(null);
  const isDefault = previewState === "default";
  const answers = isDefault ? {} : task.answers[previewState];
  const correctCount = isDefault
    ? 0
    : task.items.filter((item) => answers[item.itemId] === item.correctIndex).length;

  useEffect(() => {
    return () => {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const playScript = (id: string, script: string) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;

    window.speechSynthesis.cancel();

    if (playingId === id) {
      setPlayingId(null);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(script);
    utterance.rate = 0.9;
    utterance.onend = () => {
      setPlayingId(null);
    };
    utterance.onerror = () => {
      setPlayingId(null);
    };

    setPlayingId(id);
    window.speechSynthesis.speak(utterance);
  };

  return (
    <TaskWidgetFrame task={task} icon={<Volume2 size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Tone focus">{task.grammarRule}</RuleCallout>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: 16,
          marginTop: 16,
          marginBottom: 16,
        }}
      >
        {task.intros.map((intro, index) => {
          const isPlaying = playingId === intro.id;
          const bgGrad =
            index === 0
              ? "linear-gradient(135deg, rgba(238,245,255,0.7), rgba(255,255,255,0.96))"
              : "linear-gradient(135deg, rgba(255,242,242,0.7), rgba(255,255,255,0.96))";
          const borderColor = index === 0 ? "oklch(85% 0.025 240)" : "oklch(85% 0.025 20)";

          return (
            <div
              key={intro.id}
              style={{
                borderRadius: 16,
                padding: "16px 18px",
                background: bgGrad,
                border: `1.5px solid ${borderColor}`,
                boxShadow: "0 4px 16px rgba(80,110,180,0.05)",
                display: "flex",
                flexDirection: "column",
                gap: 12,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <button
                  type="button"
                  onClick={() => playScript(intro.id, intro.audioScript)}
                  title={isPlaying ? "Pause audio" : "Play audio"}
                  aria-label={isPlaying ? "Pause audio" : "Play audio"}
                  style={{
                    ...roundIconButton,
                    background: isPlaying ? "var(--tw-red)" : "#0070C4",
                    boxShadow: isPlaying
                      ? "0 6px 16px rgba(220,50,50,0.28)"
                      : "0 6px 16px rgba(0,112,196,0.28)",
                  }}
                >
                  {isPlaying ? (
                    <Pause size={18} fill="currentColor" />
                  ) : (
                    <Play size={18} fill="currentColor" />
                  )}
                </button>
                <div style={{ minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: 11,
                      fontWeight: 800,
                      color: "oklch(45% 0.07 240)",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                    }}
                  >
                    {intro.label}
                  </div>
                  <div
                    style={{
                      fontSize: 14,
                      fontWeight: 700,
                      color: "var(--tw-navy)",
                      marginTop: 2,
                    }}
                  >
                    {intro.speaker.replace(/\s*\(.*?\)/g, "")}
                  </div>
                </div>
              </div>
              {!isDefault && (
                <div
                  style={{
                    fontSize: 13,
                    lineHeight: 1.55,
                    color: "var(--tw-ink-muted)",
                    background: "rgba(255,255,255,0.6)",
                    padding: "10px 12px",
                    borderRadius: 10,
                    border: "1px dashed rgba(80,110,180,0.15)",
                  }}
                >
                  &ldquo;{intro.audioScript}&rdquo;
                </div>
              )}
            </div>
          );
        })}
      </div>

      {!isDefault && (
        <ResultBanner
          total={task.items.length}
          correct={correctCount}
          label={`${correctCount} of ${task.items.length} tones identified`}
        />
      )}

      {task.items.map((item, index) => {
        const selected = answers[item.itemId];
        return (
          <div className="tw-card" key={item.itemId}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">{item.prompt}</div>
            </div>
            <div className="tw-opt-list">
              {item.options.map((option, optionIndex) => {
                const isCorrect = !isDefault && optionIndex === item.correctIndex;
                const isWrongPick = !isDefault && optionIndex === selected && !isCorrect;
                const cls = `tw-opt-row${isCorrect ? " correct" : ""}${isWrongPick ? " wrong" : ""}`;
                return (
                  <div className={cls} key={option} style={{ cursor: "default" }}>
                    <span className="tw-opt-key">{optionIndex + 1}</span>
                    <span style={{ flex: 1 }}>{option}</span>
                    {isCorrect && <Check size={14} strokeWidth={2.8} />}
                    {isWrongPick && <X size={14} strokeWidth={2.8} />}
                  </div>
                );
              })}
            </div>
            {!isDefault && (
              <div className="tw-fb-explain" style={{ marginTop: 12, paddingTop: 10 }}>
                <strong>{selected === item.correctIndex ? "Correct." : "Why it is wrong."}</strong>{" "}
                {item.explanation}
              </div>
            )}
          </div>
        );
      })}
    </TaskWidgetFrame>
  );
}
