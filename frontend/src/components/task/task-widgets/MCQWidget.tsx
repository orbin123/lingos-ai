"use client";

import { TaskHeader, I, type WidgetState } from "./shared";

interface Props {
  state: WidgetState;
}

const items = [
  {
    id: "q1",
    prompt: "The package _____ to the wrong address last week.",
    options: ["delivered", "was delivered", "has delivered", "is delivering"],
    correct_index: 1,
    user_index: 1,
    explanation:
      'The package received the action, so we need passive voice in the past: "be + past participle" = was delivered.',
  },
  {
    id: "q2",
    prompt: "If I _____ more time, I would finish the project today.",
    options: ["have", "had", "will have", "would have"],
    correct_index: 1,
    user_index: 1,
    explanation:
      "Second conditional uses past simple in the if-clause to talk about an unreal present.",
  },
  {
    id: "q3",
    prompt: "She works hard _____ she rarely gets the recognition she deserves.",
    options: ["so", "but", "because", "although"],
    correct_index: 1,
    user_index: 3,
    explanation:
      'The two clauses contrast each other, so we need a contrast connector. "But" links two independent clauses. "Although" would need a subordinate-clause structure.',
  },
];

export function MCQWidget({ state }: Props) {
  const correctCount = items.filter((i) => i.user_index === i.correct_index).length;
  const allAnswered = items.every((i) => i.user_index !== null);

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Grammar · Tense, Voice & Connectors"
        intro={{
          title: "Pick the most natural completion",
          body: "Read each sentence and choose the option that sounds most natural in everyday English. Press 1–4 to select quickly.",
        }}
        sub_skill="Mixed Grammar"
        activity="Multiple Choice"
        time={4}
        concepts={["passive voice", "2nd conditional", "contrast connectors"]}
      />

      {state === "after" && (
        <div className={`tw-result-banner ${correctCount === items.length ? "good" : "mid"}`}>
          <div className="tw-result-icon">{I.spark}</div>
          <div className="tw-result-text">
            <div className="tw-result-headline">
              {correctCount} of {items.length} correct
            </div>
            <div className="tw-result-sub">
              Solid work on passives &amp; conditionals. Watch contrast connectors.
            </div>
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

      {items.map((q, qi) => (
        <div className="tw-card" key={q.id}>
          <div className="tw-q-number-row">
            <div className="tw-q-number-badge">{qi + 1}</div>
            <div className="tw-q-stem">{q.prompt}</div>
          </div>
          <div className="tw-opt-list">
            {q.options.map((opt, oi) => {
              let cls = "tw-opt-row";
              if (state === "before") {
                if (q.user_index === oi) cls += " selected";
              } else {
                if (oi === q.correct_index) cls += " correct";
                else if (oi === q.user_index && oi !== q.correct_index) cls += " wrong";
              }
              return (
                <button key={oi} className={cls} disabled={state === "after"}>
                  <span className="tw-opt-key">{oi + 1}</span>
                  <span style={{ flex: 1 }}>{opt}</span>
                  {state === "after" && oi === q.correct_index && (
                    <span className="tw-opt-status" style={{ color: "var(--tw-green)" }}>
                      {I.check}
                    </span>
                  )}
                  {state === "after" && oi === q.user_index && oi !== q.correct_index && (
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
                {q.user_index === q.correct_index ? "Correct." : "Why it's"}{" "}
              </strong>
              {q.options[q.correct_index]}: {q.explanation}
            </div>
          )}
        </div>
      ))}

      {state === "before" && (
        <button className="tw-submit-btn" disabled={!allAnswered}>
          {I.spark}{" "}
          {allAnswered ? "Submit answers" : `Answer all ${items.length} questions to submit`}
        </button>
      )}
    </div>
  );
}
