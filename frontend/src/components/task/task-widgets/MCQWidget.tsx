"use client";

import { useState } from "react";
import { TaskHeader, I } from "./shared";
import type { MCQPayload, WidgetProps } from "./types";

type Props = WidgetProps<MCQPayload>;

interface MCQAnswerRow {
  item_id: string;
  selected_index: number;
}

interface MCQAnswers {
  answers?: MCQAnswerRow[];
  time_spent_seconds?: number;
}

function selectionsFromAnswers(answers: Record<string, unknown>): Record<string, number> {
  const rows = (answers as MCQAnswers).answers ?? [];
  const out: Record<string, number> = {};
  for (const row of rows) {
    if (row && typeof row.item_id === "string" && typeof row.selected_index === "number") {
      out[row.item_id] = row.selected_index;
    }
  }
  return out;
}

export function MCQWidget({ payload, answers, setAnswers, state, onSubmit }: Props) {
  const items = payload.items ?? [];
  const [startedAt] = useState(() => Date.now());
  const selections = selectionsFromAnswers(answers);

  const setSelection = (itemId: string, optionIndex: number) => {
    if (state === "after") return;
    const next = { ...selections, [itemId]: optionIndex };
    const rows: MCQAnswerRow[] = items
      .filter((it) => next[it.item_id] !== undefined)
      .map((it) => ({ item_id: it.item_id, selected_index: next[it.item_id] }));
    setAnswers({
      answers: rows,
      time_spent_seconds: Math.round((Date.now() - startedAt) / 1000),
    });
  };

  const allAnswered = items.every((it) => selections[it.item_id] !== undefined);
  const correctCount = items.filter(
    (it) => selections[it.item_id] === it.correct_index,
  ).length;

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Multiple Choice"
        intro={{
          title: payload.task_intro || "Pick the best option",
          body: payload.instructions || "Choose the option that best answers each question.",
        }}
        sub_skill={payload.sub_skill || ""}
        activity={payload.activity || "Multiple Choice"}
        time={payload.estimated_time_minutes ?? 0}
        concepts={payload.tone_concepts_taught || payload.question_types_used}
        target_words={payload.target_words?.map((w) => ({ word: w, used: false }))}
      />

      {payload.pattern_explained && (
        <div className="tw-rule-callout">
          <div className="tw-rule-icon">{I.rule}</div>
          <div className="tw-rule-body">
            <div className="tw-rule-label">Pattern</div>
            <div className="tw-rule-text">{payload.pattern_explained}</div>
          </div>
        </div>
      )}

      {state === "after" && items.length > 0 && (
        <div className={`tw-result-banner ${correctCount === items.length ? "good" : "mid"}`}>
          <div className="tw-result-icon">{I.spark}</div>
          <div className="tw-result-text">
            <div className="tw-result-headline">
              {correctCount} of {items.length} correct
            </div>
            <div className="tw-result-sub">Review the explanations below.</div>
          </div>
          <div>
            <div className="tw-result-score">
              {Math.round((correctCount / items.length) * 100)}
              <span style={{ fontSize: 14, color: "var(--tw-ink-muted)" }}>%</span>
            </div>
            <div className="tw-result-score-sub">Score</div>
          </div>
        </div>
      )}

      {items.map((q, qi) => {
        const userIndex = selections[q.item_id];
        return (
          <div className="tw-card" key={q.item_id}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{qi + 1}</div>
              <div className="tw-q-stem">{q.prompt}</div>
            </div>
            <div className="tw-opt-list">
              {q.options.map((opt, oi) => {
                let cls = "tw-opt-row";
                if (state === "before") {
                  if (userIndex === oi) cls += " selected";
                } else {
                  if (oi === q.correct_index) cls += " correct";
                  else if (oi === userIndex && oi !== q.correct_index) cls += " wrong";
                }
                return (
                  <button
                    key={oi}
                    className={cls}
                    disabled={state === "after"}
                    onClick={() => setSelection(q.item_id, oi)}
                  >
                    <span className="tw-opt-key">{oi + 1}</span>
                    <span style={{ flex: 1 }}>{opt}</span>
                    {state === "after" && oi === q.correct_index && (
                      <span className="tw-opt-status" style={{ color: "var(--tw-green)" }}>
                        {I.check}
                      </span>
                    )}
                    {state === "after" && oi === userIndex && oi !== q.correct_index && (
                      <span className="tw-opt-status" style={{ color: "var(--tw-red)" }}>
                        ✕
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
            {state === "after" && (
              <div
                className="tw-fb-explain"
                style={{
                  borderTop: "1px dashed oklch(88% 0.02 240)",
                  marginTop: 12,
                  paddingTop: 10,
                }}
              >
                <strong>
                  {userIndex === q.correct_index ? "Correct." : "Why it's"}{" "}
                </strong>
                {q.options[q.correct_index]}: {q.explanation}
              </div>
            )}
          </div>
        );
      })}

      {state === "before" && (
        <button
          className="tw-submit-btn"
          disabled={!allAnswered}
          onClick={onSubmit}
        >
          {I.spark}{" "}
          {allAnswered ? "Submit answers" : `Answer all ${items.length} questions to submit`}
        </button>
      )}
    </div>
  );
}
