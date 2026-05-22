"use client";

import { useRef } from "react";
import { TaskHeader, I } from "./shared";
import { countWords, resolveAudioUrl } from "./types";
import type { OpenTextItem, OpenTextPayload, WidgetProps } from "./types";

type Props = WidgetProps<OpenTextPayload>;

export function OpenTextWidget({ payload, answers, setAnswers, state, onSubmit }: Props) {
  const items = payload.items ?? [];
  const submitted = state === "after";
  const startedAtRef = useRef(Date.now());
  const valueFor = (it: OpenTextItem) => (answers[it.item_id] as string | undefined) ?? "";

  const setValue = (it: OpenTextItem, next: string) => {
    if (submitted) return;
    setAnswers({
      ...answers,
      [it.item_id]: next,
      time_spent_seconds: Math.round((Date.now() - startedAtRef.current) / 1000),
    });
  };

  const allFilled = items.every((it) => valueFor(it).trim().length >= 5);

  const allText = items.map((it) => valueFor(it)).join(" ").toLowerCase();
  const targetWords = (payload.target_words ?? []).map((w) => ({
    word: w,
    used: new RegExp(`\\b${w.toLowerCase()}\\b`).test(allText),
  }));

  const sourceAudioUrl = resolveAudioUrl(payload.source_audio_url);
  const contextPassage = payload.source_passage || payload.passage;

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Writing Task"
        intro={{
          title: payload.task_intro || "Write your response",
          body: payload.instructions || "Answer each prompt in 3–5 sentences.",
        }}
        sub_skill={payload.sub_skill || ""}
        activity={payload.activity || "Open Writing"}
        time={payload.estimated_time_minutes ?? 0}
        target_words={targetWords.length > 0 ? targetWords : undefined}
      />

      {payload.grammar_rule_explained && (
        <div className="tw-rule-callout">
          <div className="tw-rule-icon">{I.rule}</div>
          <div className="tw-rule-body">
            <div className="tw-rule-label">Rule</div>
            <div className="tw-rule-text">{payload.grammar_rule_explained}</div>
          </div>
        </div>
      )}

      {payload.target_register && (
        <div
          className="tw-card"
          style={{ background: "oklch(96% 0.04 290)", borderColor: "oklch(82% 0.1 290)" }}
        >
          <div className="tw-rule-label" style={{ color: "oklch(40% 0.16 290)", marginBottom: 4 }}>
            Target register
          </div>
          <div style={{ fontSize: 13.5, color: "var(--tw-navy)", lineHeight: 1.6 }}>
            {payload.target_register}
          </div>
        </div>
      )}

      {contextPassage && (
        <div
          className="tw-card"
          style={{ background: "oklch(96% 0.04 290)", borderColor: "oklch(82% 0.1 290)" }}
        >
          <div className="tw-rule-label" style={{ color: "oklch(40% 0.16 290)", marginBottom: 6 }}>
            Context · short reading
          </div>
          <div style={{ fontSize: 13.5, color: "var(--tw-navy)", lineHeight: 1.6 }}>
            {contextPassage}
          </div>
          {payload.structure_pattern_taught && (
            <div style={{ fontSize: 12, color: "var(--tw-ink-muted)", marginTop: 8, fontStyle: "italic" }}>
              Structure: {payload.structure_pattern_taught}
            </div>
          )}
        </div>
      )}

      {sourceAudioUrl && (
        <div
          className="tw-card"
          style={{ background: "oklch(97% 0.02 245)", borderColor: "var(--tw-line)" }}
        >
          <div className="tw-rule-label" style={{ marginBottom: 8 }}>
            Source audio
          </div>
          <audio src={sourceAudioUrl} controls style={{ width: "100%" }} />
        </div>
      )}

      {items.map((item, idx) => {
        const val = valueFor(item);
        const wc = countWords(val);
        const hasContent = val.trim().length >= 5;
        return (
          <div className="tw-card" key={item.item_id}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{idx + 1}</div>
              <div className="tw-q-stem">{item.prompt}</div>
            </div>
            {!submitted ? (
              <>
                <textarea
                  className="tw-write-area"
                  value={val}
                  onChange={(e) => setValue(item, e.target.value)}
                  placeholder="Write your answer here…"
                  rows={3}
                />
                <div className="tw-write-helper">
                  <span>Minimum 5 characters per prompt.</span>
                  <span className={`tw-count ${hasContent ? "ok" : "short"}`}>
                    {wc} word{wc === 1 ? "" : "s"} {hasContent ? "· ✓ valid" : "· need more"}
                  </span>
                </div>
              </>
            ) : (
              <div className="tw-compare-grid">
                <div className="tw-compare-card">
                  <div className="tw-compare-label">{I.doc} Your answer</div>
                  <div className="tw-compare-body">
                    {val || <em style={{ color: "var(--tw-ink-muted)" }}>No answer</em>}
                  </div>
                </div>
                <div className="tw-compare-card sample">
                  <div className="tw-compare-label">{I.spark} Sample answer</div>
                  <div className="tw-compare-body">{item.sample_answer}</div>
                </div>
              </div>
            )}
            {submitted && item.answer_hints && item.answer_hints.length > 0 && (
              <div className="tw-hints-block" style={{ marginTop: 10 }}>
                <div className="tw-hints-label">{I.spark} Hints</div>
                <div className="tw-hints-list">
                  {item.answer_hints.map((h, hi) => (
                    <div className="tw-hint-item" key={hi}>
                      <span className="tw-hint-dot" />
                      {h}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })}

      {submitted && payload.common_mistakes && payload.common_mistakes.length > 0 && (
        <div className="tw-hints-block" style={{ background: "oklch(96% 0.04 30)", marginTop: 4 }}>
          <div className="tw-hints-label" style={{ color: "oklch(38% 0.14 30)" }}>
            Common mistakes to watch for
          </div>
          <div className="tw-hints-list">
            {payload.common_mistakes.map((m, i) => (
              <div className="tw-hint-item" key={i}>
                <span className="tw-hint-dot" style={{ background: "var(--tw-amber)" }} />
                {m}
              </div>
            ))}
          </div>
        </div>
      )}

      {!submitted && (
        <button
          className="tw-submit-btn"
          disabled={!allFilled}
          onClick={() => onSubmit()}
        >
          {I.send} Submit writing
        </button>
      )}
    </div>
  );
}
