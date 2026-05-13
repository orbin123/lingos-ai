"use client";

import { TaskHeader, I, type WidgetState } from "./shared";

interface Props {
  state: WidgetState;
}

const sections = [
  {
    id: "intro",
    title: "Introduction",
    prompt: "State your position on remote work in 2–3 sentences.",
    min: 40,
    user: "Remote work has fundamentally changed how I think about productivity. After three years working from home, I believe the future belongs to teams that can be deliberate about when they need to be in the same room.",
    words: 38,
  },
  {
    id: "body1",
    title: "Body 1 — Argument",
    prompt: "Give your strongest argument with a concrete example.",
    min: 80,
    user: "The biggest win for me is uninterrupted focus time. Last quarter I shipped a database migration that had been stuck for two years, mostly because I had four-hour blocks without meetings, kitchen drop-ins, or surprise hallway questions. That depth was impossible in our old open-plan office, where I averaged 17 interruptions per day.",
    words: 56,
  },
  {
    id: "body2",
    title: "Body 2 — Counter",
    prompt: "Acknowledge the strongest counterargument and respond.",
    min: 80,
    user: "Critics fairly point out that mentorship suffers when junior engineers can't shadow seniors in person. That's real. But the answer isn't five days back in the office — it's structured pairing weeks and intentional in-person sprints, which is what my team now does once a month with much better results than the daily-commute era.",
    words: 58,
  },
  { id: "concl", title: "Conclusion", prompt: "Summarize and end with a clear recommendation.", min: 40, user: "", words: 0 },
];

const CONCLUSION_TEXT =
  "In the end, the binary \"remote vs. office\" framing misses the point. Strong teams should default to async focus and use co-located time intentionally — one week a month is plenty for most knowledge work.";

export function StructuredEssayWidget({ state }: Props) {
  const totalWords = sections.reduce((s, x) => s + x.words, 0);
  const currentIdx = state === "before" ? 2 : 3;
  const current = sections[currentIdx];

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Essay · Opinion Piece"
        intro={{
          title: "Build your argument section by section",
          body: "Move through each part in order. The submit button unlocks only when every section meets its minimum word count.",
        }}
        sub_skill="Persuasive Writing"
        activity="Structured Essay"
        time={20}
      />

      <div className="tw-progress-strip">
        <div className="tw-progress-row">
          <div>
            <div className="tw-progress-step-label">
              {state === "before" ? `Section ${currentIdx + 1} of ${sections.length}` : "All sections complete"}
            </div>
            <div className="tw-progress-section-title">
              {state === "before" ? current.title : "Ready to submit"}
            </div>
          </div>
          <div className="tw-progress-total">
            <span>Total written</span>
            <strong style={{ color: "var(--tw-navy)", fontWeight: 800, fontSize: 14 }}>
              {state === "before" ? totalWords : 218}
            </strong>{" "}
            words
          </div>
        </div>
        <div className="tw-dot-track">
          {sections.map((s, i) => {
            let cls = "tw-dot-step";
            if (state === "after") cls += " done";
            else if (i < currentIdx) cls += " done";
            else if (i === currentIdx) cls += " active";
            return <span key={s.id} className={cls} />;
          })}
        </div>
      </div>

      <div className="tw-section-tabs">
        {sections.map((s, i) => {
          let cls = "tw-section-tab";
          if (state === "after") cls += " done";
          else if (i === currentIdx) cls += " active";
          else if (i < currentIdx) cls += " done";
          return (
            <button key={s.id} className={cls}>
              <span className="tw-step-num">{i + 1}</span>
              <span>{s.title.split(" — ")[0]}</span>
              {(state === "after" || i < currentIdx) && (
                <span style={{ marginLeft: 4 }}>{I.check}</span>
              )}
            </button>
          );
        })}
      </div>

      {state === "before" ? (
        <div className="tw-card">
          <div className="tw-q-number-row">
            <div className="tw-q-number-badge">{currentIdx + 1}</div>
            <div className="tw-q-stem">
              <strong>{current.title}</strong>
              <br />
              <span style={{ fontSize: 13.5, fontWeight: 500, color: "var(--tw-ink-muted)" }}>
                {current.prompt}
              </span>
            </div>
          </div>
          <textarea className="tw-write-area" style={{ minHeight: 160 }} defaultValue={current.user} />
          <div className="tw-write-helper">
            <span>Minimum {current.min} words for this section</span>
            <span className={`tw-count ${current.words >= current.min ? "ok" : "short"}`}>
              {current.words} / {current.min} words{" "}
              {current.words >= current.min ? "· ✓ met" : `· ${current.min - current.words} to go`}
            </span>
          </div>
          <div className="tw-section-nav">
            <button className="tw-nav-btn prev">{I.arrowL} Previous</button>
            <button className="tw-nav-btn next" disabled={current.words < current.min}>
              Next section {I.arrowR}
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="tw-result-banner good">
            <div className="tw-result-icon" style={{ color: "var(--tw-green)" }}>{I.check}</div>
            <div className="tw-result-text">
              <div className="tw-result-headline">All 4 sections complete · 218 words</div>
              <div className="tw-result-sub">
                Strong thesis, balanced counter-argument, and a specific recommendation. Ready for AI feedback.
              </div>
            </div>
            <div>
              <div className="tw-result-score">
                218<span style={{ fontSize: 14, color: "var(--tw-ink-muted)" }}> / 240</span>
              </div>
              <div className="tw-result-score-sub">Words</div>
            </div>
          </div>
          {sections.map((s, i) => (
            <div className="tw-card" key={s.id} style={{ marginBottom: 10 }}>
              <div className="tw-q-number-row" style={{ marginBottom: 6 }}>
                <div
                  className="tw-q-number-badge"
                  style={{ background: "var(--tw-green-soft)", color: "oklch(28% 0.14 155)" }}
                >
                  {I.check}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13.5, fontWeight: 800, color: "var(--tw-navy)" }}>{s.title}</div>
                  <div style={{ fontSize: 11.5, color: "var(--tw-ink-muted)", fontWeight: 700 }}>
                    {i === 3 ? 54 : s.words} words · met minimum of {s.min}
                  </div>
                </div>
              </div>
              <div style={{ fontSize: 13.5, color: "var(--tw-navy)", lineHeight: 1.6 }}>
                {i === 3 ? CONCLUSION_TEXT : s.user}
              </div>
            </div>
          ))}
          <button className="tw-submit-btn">{I.send} Submit essay for AI feedback</button>
        </>
      )}
    </div>
  );
}
