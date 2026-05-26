"use client";

import { useRef } from "react";
import {
  areFillInBlanksAnswered,
  normalizeFillInBlanksPayload,
} from "./fillBlanksNormalize";
import { TaskHeader, I } from "./shared";
import { blankId } from "./types";
import type { BlankItem, FillInBlanksPayload, WidgetProps } from "./types";

type Props = WidgetProps<FillInBlanksPayload>;

function isCorrect(blank: BlankItem, value: string): boolean {
  return value.trim().toLowerCase() === blank.correct_answer.trim().toLowerCase();
}

export function FillBlanksWidget({ payload, answers, setAnswers, state, onSubmit }: Props) {
  const normalizedPayload = normalizeFillInBlanksPayload(payload);
  const blanks: BlankItem[] = normalizedPayload.items ?? normalizedPayload.blanks ?? [];
  const startedAtRef = useRef<number | null>(null);
  const submitted = state === "after";
  const valueFor = (b: BlankItem) => (answers[blankId(b)] as string | undefined) ?? "";

  const setValue = (b: BlankItem, next: string, eventTime: number) => {
    if (submitted) return;
    startedAtRef.current ??= eventTime;
    setAnswers({
      ...answers,
      [blankId(b)]: next,
      time_spent_seconds: Math.round((eventTime - startedAtRef.current) / 1000),
    });
  };

  const allAnswered = areFillInBlanksAnswered(blanks, answers);
  const correctCount = blanks.filter((b) => isCorrect(b, valueFor(b))).length;

  const passage = normalizedPayload.passage ?? "";
  const parts = passage.split("___");
  const hasInlineBlanks = parts.length > 1 && blanks.length > 0;

  const renderBlankInput = (blank: BlankItem, index: number) => {
    const value = valueFor(blank);
    const correct = submitted && isCorrect(blank, value);

    if (submitted) {
      return (
        <span
          key={`${blankId(blank)}-${index}`}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 4,
            margin: "0 4px",
            verticalAlign: "baseline",
            whiteSpace: "nowrap",
          }}
        >
          <span
            aria-hidden
            style={{
              width: 20,
              height: 20,
              borderRadius: "50%",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              background: correct ? "var(--tw-green)" : "var(--tw-red)",
              color: "white",
              fontSize: 10,
              fontWeight: 800,
              flexShrink: 0,
            }}
          >
            {correct ? "✓" : "✗"}
          </span>
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
        </span>
      );
    }

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
            background: "var(--tw-primary)",
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
          value={value}
          onChange={(e) => setValue(blank, e.target.value, e.timeStamp)}
          placeholder="answer"
          className="tw-blank-input"
          style={{
            width: "clamp(88px, 18vw, 150px)",
            textAlign: "center",
          }}
        />
        {blank.base_verb && (
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
      </span>
    );
  };

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Fill in the Blanks"
        intro={{
          title: normalizedPayload.task_intro || "Complete the passage",
          body: normalizedPayload.instructions || "Fill each blank with the correct word.",
        }}
        sub_skill={normalizedPayload.sub_skill || ""}
        activity={normalizedPayload.activity || "Fill in the Blanks"}
        time={normalizedPayload.estimated_time_minutes ?? 0}
      />

      {normalizedPayload.grammar_rule_explained && (
        <div className="tw-rule-callout">
          <div className="tw-rule-icon">{I.rule}</div>
          <div className="tw-rule-body">
            <div className="tw-rule-label">Grammar rule</div>
            <div className="tw-rule-text">{normalizedPayload.grammar_rule_explained}</div>
          </div>
        </div>
      )}

      {blanks.length === 0 && (
        <div className="tw-rule-callout" role="status">
          <div className="tw-rule-icon">!</div>
          <div className="tw-rule-body">
            <div className="tw-rule-label">Activity content missing</div>
            <div className="tw-rule-text">
              This fill-in-blanks activity did not include any blanks. Restart the
              session to fetch the latest authored content.
            </div>
          </div>
        </div>
      )}

      {hasInlineBlanks ? (
        <div className="tw-passage">
          {normalizedPayload.passage_title && (
            <div className="tw-passage-label">{normalizedPayload.passage_title}</div>
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
          {normalizedPayload.passage_title && (
            <div className="tw-passage-label">{normalizedPayload.passage_title}</div>
          )}
          {normalizedPayload.passage && <div style={{ marginBottom: 12 }}>{normalizedPayload.passage}</div>}
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
            <div className="tw-result-sub">Review the correct answers above.</div>
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

      {!submitted && (
        <button
          className="tw-submit-btn"
          disabled={!allAnswered}
          onClick={() => onSubmit()}
        >
          {I.spark} Submit all blanks
        </button>
      )}
    </div>
  );
}
