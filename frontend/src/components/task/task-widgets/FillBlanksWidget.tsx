"use client";

import { useState } from "react";
import { TaskHeader, I } from "./shared";
import { blankId } from "./types";
import type { BlankItem, FillInBlanksPayload, WidgetProps } from "./types";

type Props = WidgetProps<FillInBlanksPayload>;

function isCorrect(blank: BlankItem, value: string): boolean {
  return value.trim().toLowerCase() === blank.correct_answer.trim().toLowerCase();
}

export function FillBlanksWidget({ payload, answers, setAnswers, state, onSubmit }: Props) {
  const blanks: BlankItem[] = payload.items ?? payload.blanks ?? [];
  const [startedAt] = useState(() => Date.now());
  const submitted = state === "after";
  const valueFor = (b: BlankItem) => (answers[blankId(b)] as string | undefined) ?? "";

  const setValue = (b: BlankItem, next: string) => {
    if (submitted) return;
    setAnswers({
      ...answers,
      [blankId(b)]: next,
      time_spent_seconds: Math.round((Date.now() - startedAt) / 1000),
    });
  };

  const allAnswered = blanks.every((b) => valueFor(b).trim().length > 0);
  const correctCount = blanks.filter((b) => isCorrect(b, valueFor(b))).length;

  const passage = payload.passage ?? "";
  const parts = passage.split("___");
  const hasInlineBlanks = parts.length > 1 && blanks.length > 0;

  const renderBlankInput = (blank: BlankItem, index: number) => {
    const value = valueFor(blank);
    const correct = submitted && isCorrect(blank, value);
    return (
      <span
        key={`${blankId(blank)}-${index}`}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          margin: "0 4px",
          verticalAlign: "baseline",
          whiteSpace: "nowrap",
        }}
      >
        <span
          aria-hidden
          style={{
            width: 22,
            height: 22,
            borderRadius: "50%",
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            background: submitted
              ? correct
                ? "var(--tw-green)"
                : "var(--tw-red)"
              : "var(--tw-primary)",
            color: "white",
            fontSize: 11,
            fontWeight: 800,
            lineHeight: 1,
            flexShrink: 0,
          }}
        >
          {index + 1}
        </span>
        <input
          aria-label={`Blank ${index + 1}`}
          disabled={submitted}
          value={value}
          onChange={(e) => setValue(blank, e.target.value)}
          placeholder="answer"
          className={
            submitted
              ? correct
                ? "tw-blank-input ok"
                : "tw-blank-input no"
              : "tw-blank-input"
          }
          style={{
            width: "clamp(88px, 18vw, 150px)",
            textAlign: "center",
          }}
        />
        {!submitted && blank.base_verb && (
          <span style={{
            fontSize: 12,
            fontWeight: 600,
            color: "var(--tw-primary)",
            fontStyle: "italic",
            whiteSpace: "nowrap",
          }}>
            ({blank.base_verb})
          </span>
        )}
        {submitted && !correct && (
          <span className="tw-blank-fix">{blank.correct_answer}</span>
        )}
      </span>
    );
  };

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Fill in the Blanks"
        intro={{
          title: payload.task_intro || "Complete the passage",
          body: payload.instructions || "Fill each blank with the correct word.",
        }}
        sub_skill={payload.sub_skill || ""}
        activity={payload.activity || "Fill in the Blanks"}
        time={payload.estimated_time_minutes ?? 0}
      />

      {payload.grammar_rule_explained && (
        <div className="tw-rule-callout">
          <div className="tw-rule-icon">{I.rule}</div>
          <div className="tw-rule-body">
            <div className="tw-rule-label">Grammar rule</div>
            <div className="tw-rule-text">{payload.grammar_rule_explained}</div>
          </div>
        </div>
      )}

      {hasInlineBlanks ? (
        <div className="tw-passage">
          {payload.passage_title && (
            <div className="tw-passage-label">{payload.passage_title}</div>
          )}
          {parts.map((part, index) => (
            <span key={`part-${index}`}>
              {part}
              {index < blanks.length ? renderBlankInput(blanks[index], index) : null}
            </span>
          ))}
        </div>
      ) : (
        <div className="tw-passage">
          {payload.passage_title && (
            <div className="tw-passage-label">{payload.passage_title}</div>
          )}
          {payload.passage && <div style={{ marginBottom: 12 }}>{payload.passage}</div>}
          {blanks.map((blank, index) => {
            const sentenceParts = blank.sentence_with_blank.split("___");
            return (
              <div key={blankId(blank)} style={{ marginBottom: 8 }}>
                <span style={{ fontWeight: 700, marginRight: 6, color: "var(--tw-primary)" }}>
                  {index + 1}.
                </span>
                {sentenceParts[0]}
                {renderBlankInput(blank, index)}
                {sentenceParts[1] ?? ""}
              </div>
            );
          })}
        </div>
      )}

      {submitted && blanks.length > 0 && (
        <div className={`tw-result-banner ${correctCount === blanks.length ? "good" : "mid"}`} style={{ marginTop: 14 }}>
          <div className="tw-result-icon">{I.spark}</div>
          <div className="tw-result-text">
            <div className="tw-result-headline">
              {correctCount} of {blanks.length} blanks correct
            </div>
            <div className="tw-result-sub">Review the explanations below.</div>
          </div>
          <div>
            <div className="tw-result-score">
              {Math.round((correctCount / blanks.length) * 100)}
              <span style={{ fontSize: 14, color: "var(--tw-ink-muted)" }}>%</span>
            </div>
            <div className="tw-result-score-sub">Score</div>
          </div>
        </div>
      )}

      {submitted && (
        <div style={{ display: "grid", gap: 10, marginBottom: 14 }}>
          {blanks.map((b, idx) => {
            const value = valueFor(b);
            const correct = isCorrect(b, value);
            return (
              <div
                key={blankId(b)}
                className={correct ? "tw-fb-row good" : "tw-fb-row bad"}
              >
                <div className={correct ? "tw-fb-marker ok" : "tw-fb-marker no"}>
                  {correct ? "✓" : "!"}
                </div>
                <div>
                  <div className="tw-fb-q">
                    <strong>Blank {idx + 1}:</strong>{" "}
                    <span style={{ color: "var(--tw-ink-muted)" }}>{value || "—"}</span>
                    {!correct && (
                      <>
                        {" → "}
                        <span style={{ color: "var(--tw-green)", fontWeight: 700 }}>
                          {b.correct_answer}
                        </span>
                      </>
                    )}
                  </div>
                  <div className="tw-fb-explain">{b.explanation}</div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {!submitted && (
        <button
          className="tw-submit-btn"
          disabled={!allAnswered}
          onClick={onSubmit}
        >
          {I.spark} Submit all blanks
        </button>
      )}
    </div>
  );
}
