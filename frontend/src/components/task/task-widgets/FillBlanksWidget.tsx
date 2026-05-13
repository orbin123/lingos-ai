"use client";

import { useState } from "react";
import { TaskHeader, I, type WidgetState } from "./shared";

interface Props {
  state: WidgetState;
}

export function FillBlanksWidget({ state }: Props) {
  const [picks, setPicks] = useState<{ b1: string; b2: string }>({ b1: "went", b2: "were" });

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Grammar · Past Tense Review"
        intro={{ title: "Complete the story", body: "Read the passage and fill each blank with the correct past form." }}
        sub_skill="Past Simple"
        activity="Fill in the Blanks"
        time={5}
      />

      <div className="tw-rule-callout">
        <div className="tw-rule-icon">{I.rule}</div>
        <div className="tw-rule-body">
          <div className="tw-rule-label">Grammar rule</div>
          <div className="tw-rule-text">
            Use <strong>past simple</strong> for finished actions at a finished time. Regular verbs add{" "}
            <strong>-ed</strong>; irregular verbs change form (<em>go → went, is → was, are → were</em>).
          </div>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
        <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: "0.06em", textTransform: "uppercase", color: "var(--tw-ink-muted)" }}>
          Part 1 · Beginner (Inline choice)
        </span>
        <span style={{ fontSize: 11, color: "var(--tw-ink-muted)", fontWeight: 600 }}>2 blanks</span>
      </div>

      <div className="tw-passage">
        <div className="tw-passage-label">Excerpt</div>
        Yesterday morning, we{" "}
        <span className="tw-blank-mcq">
          {["go", "went", "goed", "going"].map((opt) => {
            let cls = "tw-blank-mcq-btn";
            if (state === "before") {
              if (picks.b1 === opt) cls += " selected";
            } else {
              if (opt === "went") cls += " correct";
              else if (opt === picks.b1) cls += " wrong";
            }
            return (
              <button
                key={opt}
                className={cls}
                onClick={() => state === "before" && setPicks((p) => ({ ...p, b1: opt }))}
              >
                {opt}
              </button>
            );
          })}
        </span>{" "}
        to the lake. The water{" "}
        <span className="tw-blank-mcq">
          {["is", "was", "were", "been"].map((opt) => {
            let cls = "tw-blank-mcq-btn";
            if (state === "before") {
              if (picks.b2 === opt) cls += " selected";
            } else {
              if (opt === "was") cls += " correct";
              else if (opt === picks.b2) cls += " wrong";
            }
            return (
              <button
                key={opt}
                className={cls}
                onClick={() => state === "before" && setPicks((p) => ({ ...p, b2: opt }))}
              >
                {opt}
              </button>
            );
          })}
        </span>{" "}
        cold but the sun was bright.
      </div>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 18, marginBottom: 8 }}>
        <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: "0.06em", textTransform: "uppercase", color: "var(--tw-ink-muted)" }}>
          Part 2 · Intermediate – Expert (Text input)
        </span>
        <span style={{ fontSize: 11, color: "var(--tw-ink-muted)", fontWeight: 600 }}>3 blanks</span>
      </div>

      <div className="tw-passage">
        <div className="tw-passage-label">Continuation</div>
        We{" "}
        {state === "before" ? (
          <input className="tw-blank-input" defaultValue="rented" style={{ width: 80 }} />
        ) : (
          <span className="tw-blank-input ok">rented</span>
        )}{" "}
        a small boat and{" "}
        {state === "before" ? (
          <input className="tw-blank-input" defaultValue="rowed" style={{ width: 72 }} />
        ) : (
          <span className="tw-blank-input ok">rowed</span>
        )}{" "}
        out to the middle. Suddenly, a fish{" "}
        {state === "before" ? (
          <input className="tw-blank-input" defaultValue="jumpped" style={{ width: 90 }} />
        ) : (
          <>
            <span className="tw-blank-input no">jumpped</span>
            <span className="tw-blank-fix">jumped</span>
          </>
        )}{" "}
        out of the water right next to us.
      </div>

      {state === "after" && (
        <div className="tw-result-banner mid" style={{ marginTop: 14 }}>
          <div className="tw-result-icon">{I.spark}</div>
          <div className="tw-result-text">
            <div className="tw-result-headline">4 of 5 blanks correct</div>
            <div className="tw-result-sub">
              Watch the spelling rule for short-vowel verbs: jump → jumped (single -p).
            </div>
          </div>
          <div>
            <div className="tw-result-score">
              80<span style={{ fontSize: 14, color: "var(--tw-ink-muted)" }}>%</span>
            </div>
            <div className="tw-result-score-sub">Score</div>
          </div>
        </div>
      )}

      {state === "before" && (
        <button className="tw-submit-btn">{I.spark} Submit all blanks</button>
      )}
      {state === "after" && (
        <div className="tw-fb-row bad">
          <div className="tw-fb-marker no">!</div>
          <div>
            <div className="tw-fb-q">
              <strong>&quot;jumpped&quot;</strong> →{" "}
              <span style={{ color: "var(--tw-green)", fontWeight: 700 }}>&quot;jumped&quot;</span>
            </div>
            <div className="tw-fb-explain">
              Double the final consonant only when the verb has <strong>one syllable, one short vowel, and one final consonant</strong> AND the stress is on the last syllable.{" "}
              <em>&quot;Jump&quot;</em> ends in <strong>two consonants</strong> (-mp), so no doubling.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
