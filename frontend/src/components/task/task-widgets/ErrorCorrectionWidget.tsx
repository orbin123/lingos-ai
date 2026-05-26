"use client";

import { useRef } from "react";
import { TaskHeader } from "./shared";
import { countWords } from "./types";
import type { ErrorCorrectionItem, ErrorCorrectionPayload, WidgetProps } from "./types";

type Props = WidgetProps<ErrorCorrectionPayload>;

export function ErrorCorrectionWidget({ payload, answers, setAnswers, state, onSubmit }: Props) {
  const items = payload.items ?? [];
  const submitted = state === "after";
  const startedAtRef = useRef(Date.now());
  const valueFor = (it: ErrorCorrectionItem) => (answers[it.item_id] as string | undefined) ?? "";

  const setValue = (it: ErrorCorrectionItem, next: string) => {
    if (submitted) return;
    setAnswers({
      ...answers,
      [it.item_id]: next,
      time_spent_seconds: Math.round((Date.now() - startedAtRef.current) / 1000),
    });
  };

  const allFilled = items.every((it) => valueFor(it).trim().length >= 5);

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Writing Task"
        intro={{
          title: payload.task_intro || "Correct the sentences",
          body: payload.instructions || "Rewrite each incorrect sentence so it is grammatically correct and natural.",
        }}
        sub_skill={payload.sub_skill || "grammar"}
        activity={payload.activity || "Error Correction"}
        time={payload.estimated_time_minutes ?? 5}
      />

      {items.map((item, idx) => {
        const val = valueFor(item);
        const wc = countWords(val);
        return (
          <div className="tw-card" key={item.item_id}>
            {items.length > 1 && (
              <div className="tw-q-number-row" style={{ marginBottom: 12 }}>
                <div className="tw-q-number-badge">{idx + 1}</div>
                <div className="tw-q-stem" style={{ fontSize: 13, color: "var(--tw-ink-muted)" }}>
                  Sentence {idx + 1} of {items.length}
                </div>
              </div>
            )}

            {/* Incorrect Sentence Box matching the design image */}
            <div
              style={{
                background: "#FEF2F2",
                border: "1.5px solid #FEE2E2",
                borderRadius: "12px",
                padding: "16px",
                marginBottom: "14px",
              }}
            >
              <div
                style={{
                  fontSize: "11px",
                  fontWeight: 800,
                  letterSpacing: "0.06em",
                  textTransform: "uppercase",
                  color: "#991B1B",
                  marginBottom: "8px",
                }}
              >
                INCORRECT — REWRITE THIS
              </div>
              <div
                style={{
                  fontSize: "16px",
                  fontWeight: 700,
                  color: "var(--tw-navy)",
                  lineHeight: "1.5",
                  fontFamily: "inherit",
                }}
              >
                &ldquo;{item.incorrect_sentence}&rdquo;
              </div>
            </div>

            {!submitted ? (
              <>
                <textarea
                  className="tw-write-area"
                  value={val}
                  onChange={(e) => setValue(item, e.target.value)}
                  placeholder="Write your correction here…"
                  rows={3}
                />
                <div
                  className="tw-write-helper"
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginTop: "8px",
                    width: "100%",
                  }}
                >
                  <span style={{ fontSize: "12.5px", color: "var(--tw-ink-muted)" }}>
                    {item.watch_hints && item.watch_hints.length > 0 && (
                      <>Watch: {item.watch_hints.join(", ")}.</>
                    )}
                  </span>
                  <span
                    className="tw-count ok"
                    style={{
                      fontSize: "12.5px",
                      fontWeight: 700,
                      color: "var(--tw-navy)",
                    }}
                  >
                    {wc} word{wc === 1 ? "" : "s"}
                  </span>
                </div>
              </>
            ) : (
              <div className="tw-compare-grid">
                <div className="tw-compare-card">
                  <div className="tw-compare-label">Your correction</div>
                  <div className="tw-compare-body">
                    {val || <em style={{ color: "var(--tw-ink-muted)" }}>No answer</em>}
                  </div>
                </div>
                <div className="tw-compare-card sample">
                  <div className="tw-compare-label">Sample correction</div>
                  <div className="tw-compare-body">{item.sample_answer}</div>
                </div>
              </div>
            )}
          </div>
        );
      })}

      {!submitted && (
        <button
          className="tw-submit-btn"
          disabled={!allFilled}
          onClick={() => onSubmit()}
        >
          + Submit correction
        </button>
      )}
    </div>
  );
}
