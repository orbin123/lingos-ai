"use client";

import { TaskHeader, I, type WidgetState } from "./shared";

interface Props {
  state: WidgetState;
}

const userAnswer1 =
  "On Saturday I went to the market with my brother. We bought some fresh fruit and then we walked to a small café. I ordered an espresso while he tried the iced matcha.";
const userAnswer2 =
  "It was a relaxed weekend overall. I felt calm because I didn't check work email once.";

const targets = [
  { word: "went", used: /\bwent\b/i.test(userAnswer1 + " " + userAnswer2) },
  { word: "bought", used: /\bbought\b/i.test(userAnswer1 + " " + userAnswer2) },
  { word: "ordered", used: /\bordered\b/i.test(userAnswer1 + " " + userAnswer2) },
  { word: "tried", used: /\btried\b/i.test(userAnswer1 + " " + userAnswer2) },
  { word: "felt", used: /\bfelt\b/i.test(userAnswer1 + " " + userAnswer2) },
  { word: "spoke", used: /\bspoke\b/i.test(userAnswer1 + " " + userAnswer2) },
];

export function OpenTextWidget({ state }: Props) {
  return (
    <div className="tw-root">
      <TaskHeader
        topic="Speaking-prep · Last Weekend"
        intro={{
          title: "Write about your weekend",
          body: "Use the past simple tense and try to include the target verbs below naturally. Aim for 3–5 sentences per prompt.",
        }}
        sub_skill="Past Simple"
        activity="Open Writing"
        time={8}
        target_words={targets}
      />

      <div
        className="tw-card"
        style={{ background: "oklch(96% 0.04 290)", borderColor: "oklch(82% 0.1 290)" }}
      >
        <div className="tw-rule-label" style={{ color: "oklch(40% 0.16 290)", marginBottom: 6 }}>
          Context · short reading
        </div>
        <div style={{ fontSize: 13.5, color: "var(--tw-navy)", lineHeight: 1.6 }}>
          Many learners struggle to talk about a recent weekend without slipping into the present tense.
          The trick is to commit to past simple in the first sentence and keep the same time-frame the whole way through.
        </div>
      </div>

      <div className="tw-card">
        <div className="tw-q-number-row">
          <div className="tw-q-number-badge">1</div>
          <div className="tw-q-stem">What did you do on Saturday? Describe two activities.</div>
        </div>
        {state === "before" ? (
          <>
            <textarea className="tw-write-area" defaultValue={userAnswer1} />
            <div className="tw-write-helper">
              <span>Use at least two of the target verbs above.</span>
              <span className="tw-count ok">38 words · ✓ valid</span>
            </div>
          </>
        ) : (
          <div className="tw-compare-grid">
            <div className="tw-compare-card">
              <div className="tw-compare-label">{I.doc} Your answer</div>
              <div className="tw-compare-body">{userAnswer1}</div>
            </div>
            <div className="tw-compare-card sample">
              <div className="tw-compare-label">{I.spark} Sample answer</div>
              <div className="tw-compare-body">
                On Saturday morning I went to the farmers&apos; market and bought a bag of peaches. Later I tried a new bakery near the river — the croissants were excellent.
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="tw-card">
        <div className="tw-q-number-row">
          <div className="tw-q-number-badge">2</div>
          <div className="tw-q-stem">How did the weekend make you feel and why?</div>
        </div>
        {state === "before" ? (
          <>
            <textarea className="tw-write-area" defaultValue={userAnswer2} style={{ minHeight: 72 }} />
            <div className="tw-write-helper">
              <span>
                Try to use <strong>felt</strong> or <strong>spoke</strong> if you can.
              </span>
              <span className="tw-count ok">19 words · ✓ valid</span>
            </div>
          </>
        ) : (
          <div className="tw-compare-grid">
            <div className="tw-compare-card">
              <div className="tw-compare-label">{I.doc} Your answer</div>
              <div className="tw-compare-body">{userAnswer2}</div>
            </div>
            <div className="tw-compare-card sample">
              <div className="tw-compare-label">{I.spark} Sample answer</div>
              <div className="tw-compare-body">
                I felt completely recharged. I didn&apos;t check email and I spoke to my parents on the phone for an hour, which I almost never do during the week.
              </div>
            </div>
          </div>
        )}
      </div>

      {state === "after" && (
        <div className="tw-hints-block">
          <div className="tw-hints-label">{I.spark} Answer hints to remember</div>
          <div className="tw-hints-list">
            <div className="tw-hint-item">
              <span className="tw-hint-dot" />
              Commit to past simple in your first verb — readers latch onto the tense immediately.
            </div>
            <div className="tw-hint-item">
              <span className="tw-hint-dot" />
              Vary your verbs: &quot;went / bought / tried / ordered&quot; sounds more natural than &quot;did&quot; five times.
            </div>
            <div className="tw-hint-item">
              <span className="tw-hint-dot" />
              Connect cause &amp; effect with <em>because</em>, <em>so</em>, <em>then</em> — your second paragraph did this well.
            </div>
          </div>
        </div>
      )}

      {state === "before" && (
        <button className="tw-submit-btn">{I.send} Submit my writing</button>
      )}
    </div>
  );
}
