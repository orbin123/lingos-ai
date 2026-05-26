"use client";

import type { FeedbackRead, EvaluationRead, PronunciationResult } from "@/lib/sessions-api";

interface Props {
  feedback: FeedbackRead;
  evaluation: EvaluationRead;
  taskContent?: Record<string, any>;
  onContinue?: () => void;
}

export function PronunciationFeedbackCard({ feedback, evaluation, taskContent, onContinue }: Props) {
  let pronunciation: PronunciationResult | null = null;
  
  if (evaluation.evaluator_notes) {
    try {
      const parsed = JSON.parse(evaluation.evaluator_notes);
      if (parsed.task_type === "speak_read_aloud" && parsed.pronunciation) {
        pronunciation = parsed.pronunciation;
      }
    } catch (e) {
      // Not JSON or missing pronunciation data
    }
  }

  const referenceText = taskContent?.text_to_read_aloud || taskContent?.passage || "";

  return (
    <section
      style={{
        background: "white",
        borderRadius: 16,
        padding: 24,
        border: "1px solid oklch(88% 0.03 245)",
        display: "flex",
        flexDirection: "column",
        gap: 24,
        boxShadow: "0 4px 20px rgba(0,0,0,0.02)",
      }}
    >
      <header>
        <h3 style={{ fontSize: 18, fontWeight: 800, color: "var(--tw-navy)", margin: 0 }}>
          Detailed Pronunciation Assessment
        </h3>
        <p style={{ margin: "4px 0 0", fontSize: 14, color: "var(--tw-ink-muted)", lineHeight: 1.5 }}>
          {feedback.summary || "Here is your detailed feedback for the reading practice."}
        </p>
      </header>

      {pronunciation ? (
        <>
          {/* Detailed Scores Breakdown */}
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <h4 style={sectionHeaderStyle}>Pronunciation Scores Breakdown</h4>
            
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 16 }}>
              <ScoreCardProgress label="Accuracy" score={pronunciation.accuracy_score} description="Phoneme precision" />
              <ScoreCardProgress label="Fluency" score={pronunciation.fluency_score} description="Pacing and pauses" />
              <ScoreCardProgress label="Completeness" score={pronunciation.completeness_score} description="Words spoken" />
              {pronunciation.prosody_score !== undefined && pronunciation.prosody_score > 0 && (
                <ScoreCardProgress label="Prosody" score={pronunciation.prosody_score} description="Stress and rhythm" />
              )}
            </div>

            {/* Overall Score Badge Displayed Last */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "16px 20px",
                background: "oklch(97% 0.02 245)",
                borderRadius: 12,
                marginTop: 8,
                border: "1px dashed oklch(88% 0.03 245)",
              }}
            >
              <div>
                <div style={{ fontWeight: 800, fontSize: 15, color: "var(--tw-navy)" }}>Overall Performance</div>
                <div style={{ fontSize: 12, color: "var(--tw-ink-muted)" }}>Scaled overall scorecard result</div>
              </div>
              <ScoreBadge score={evaluation.raw_score} />
            </div>
          </div>

          {/* Word Breakdown & Highlights */}
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <h4 style={sectionHeaderStyle}>How You Read It (Mistakes Highlighted)</h4>
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "8px 6px",
                lineHeight: 1.8,
                fontSize: 16,
                padding: "16px",
                background: "oklch(99% 0.01 245)",
                border: "1px solid oklch(93% 0.01 245)",
                borderRadius: 12,
              }}
            >
              {pronunciation.words.map((w, i) => {
                let color = "var(--tw-navy)";
                let bg = "transparent";
                let textDecoration = "none";
                let fontWeight = 500;
                
                if (w.error_type === "omission") {
                  color = "oklch(60% 0.1 20)";
                  textDecoration = "line-through";
                  fontWeight = 400;
                } else if (w.error_type === "insertion") {
                  color = "oklch(50% 0.15 45)";
                  bg = "oklch(96% 0.05 45)";
                  fontWeight = 700;
                } else if (w.error_type === "mispronunciation") {
                  color = "oklch(50% 0.15 25)";
                  bg = "oklch(96% 0.05 25)";
                  fontWeight = 700;
                } else if (w.accuracy_score && w.accuracy_score < 80) {
                  color = "oklch(60% 0.13 80)"; // Yellow/Orange
                  fontWeight = 600;
                } else if (w.accuracy_score && w.accuracy_score >= 80) {
                  color = "oklch(48% 0.18 155)"; // Green
                }

                return (
                  <span
                    key={i}
                    title={`Word accuracy: ${w.accuracy_score || 0}%${w.error_type ? ` (${w.error_type})` : ""}`}
                    style={{
                      color,
                      backgroundColor: bg,
                      textDecoration,
                      fontWeight,
                      padding: bg !== "transparent" ? "2px 6px" : "0 2px",
                      borderRadius: 4,
                      cursor: "help",
                    }}
                  >
                    {w.word}
                  </span>
                );
              })}
            </div>
            
            {/* Word Breakdown Legend */}
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "12px 16px",
                fontSize: 12,
                color: "var(--tw-ink-muted)",
                paddingLeft: 4,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 10, height: 10, borderRadius: "50%", background: "oklch(48% 0.18 155)" }} />
                <span>Good (≥80%)</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 10, height: 10, borderRadius: "50%", background: "oklch(60% 0.13 80)" }} />
                <span>Needs Work (&lt;80%)</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 10, height: 10, borderRadius: "50%", background: "oklch(50% 0.15 25)" }} />
                <span>Mispronounced</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 10, height: 10, textDecoration: "line-through", color: "oklch(60% 0.1 20)", fontWeight: 700 }}>Aa</span>
                <span>Omitted</span>
              </div>
            </div>
          </div>

          {/* Model Passage (Expected version) */}
          {referenceText && (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <h4 style={sectionHeaderStyle}>Model Passage (Expected Version)</h4>
              <div
                style={{
                  padding: "16px",
                  background: "oklch(96% 0.02 245)",
                  borderRadius: 12,
                  fontSize: 14.5,
                  lineHeight: 1.6,
                  color: "var(--tw-navy)",
                  borderLeft: "4px solid oklch(62% 0.16 240)",
                }}
              >
                {referenceText}
              </div>
            </div>
          )}
        </>
      ) : (
        <div style={{ color: "var(--tw-ink-muted)", fontSize: 14 }}>
          No detailed pronunciation data available.
        </div>
      )}

      {/* Tutor Feedback Section */}
      {(feedback.did_well.length > 0 || feedback.mistakes.length > 0 || feedback.next_tip) && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16, borderTop: "1px solid oklch(92% 0.01 245)", paddingTop: 20 }}>
          <h4 style={sectionHeaderStyle}>Tutor's Recommendations</h4>
          
          {feedback.did_well.length > 0 && (
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "oklch(48% 0.18 155)", marginBottom: 6 }}>What You Did Well</div>
              <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13.5, lineHeight: 1.6, color: "var(--tw-navy)" }}>
                {feedback.did_well.map((item, idx) => (
                  <li key={idx} style={{ marginBottom: 4 }}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {feedback.mistakes.length > 0 && (
            <div style={{ marginTop: 4 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: "oklch(50% 0.15 25)", marginBottom: 6 }}>Suggested Improvements</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {feedback.mistakes.map((mistake, idx) => (
                  <div key={idx} style={{ background: "oklch(98% 0.01 25)", padding: "10px 14px", borderRadius: 8, borderLeft: "3px solid oklch(65% 0.15 25)" }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: "var(--tw-navy)" }}>{mistake.issue}</div>
                    {mistake.rule && <div style={{ fontSize: 12, color: "var(--tw-ink-muted)", marginTop: 2 }}>{mistake.rule}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {feedback.next_tip && (
            <div style={{ marginTop: 4, background: "oklch(96% 0.03 245)", padding: "12px 16px", borderRadius: 8 }}>
              <span style={{ fontWeight: 700, fontSize: 13, color: "oklch(52% 0.18 240)" }}>Next Tip: </span>
              <span style={{ fontSize: 13, color: "var(--tw-navy)" }}>{feedback.next_tip}</span>
            </div>
          )}
        </div>
      )}

      {onContinue && (
        <button
          type="button"
          onClick={onContinue}
          style={{
            alignSelf: "flex-start",
            background: "oklch(52% 0.18 240)",
            color: "white",
            fontWeight: 700,
            padding: "10px 24px",
            borderRadius: 8,
            border: "none",
            cursor: "pointer",
            fontSize: 14.5,
            boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
            marginTop: 8,
          }}
        >
          Continue
        </button>
      )}
    </section>
  );
}

function ScoreBadge({ score }: { score: number }) {
  const bg =
    score >= 8 ? "oklch(48% 0.18 155)" :
    score >= 6 ? "oklch(52% 0.18 240)" :
    score >= 4 ? "oklch(60% 0.13 80)"  :
                 "oklch(58% 0.2 15)";
  return (
    <div
      style={{
        background: bg,
        color: "white",
        borderRadius: 8,
        padding: "8px 14px",
        fontWeight: 800,
        fontSize: 18,
        minWidth: 64,
        textAlign: "center",
        boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
      }}
    >
      {score.toFixed(1)}/10
    </div>
  );
}

function ScoreCardProgress({ label, score, description }: { label: string; score: number; description?: string }) {
  const color =
    score >= 80 ? "oklch(48% 0.18 155)" : // Green
    score >= 60 ? "oklch(60% 0.13 80)" :  // Yellow/Orange
                  "oklch(50% 0.15 25)";   // Red

  const bg =
    score >= 80 ? "oklch(96% 0.02 155)" :
    score >= 60 ? "oklch(98% 0.01 80)" :
                  "oklch(98% 0.01 25)";

  return (
    <div
      style={{
        background: bg,
        border: `1px solid oklch(93% 0.01 245)`,
        padding: "12px 16px",
        borderRadius: 12,
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 13, fontWeight: 700, color: "var(--tw-navy)" }}>{label}</span>
        <span style={{ fontSize: 14, fontWeight: 800, color }}>{score.toFixed(0)}%</span>
      </div>
      
      {/* Progress Bar */}
      <div style={{ width: "100%", height: 6, background: "oklch(93% 0.01 245)", borderRadius: 999, overflow: "hidden" }}>
        <div style={{ width: `${score}%`, height: "100%", background: color, borderRadius: 999 }} />
      </div>

      {description && (
        <span style={{ fontSize: 11, color: "var(--tw-ink-muted)" }}>{description}</span>
      )}
    </div>
  );
}

const sectionHeaderStyle: React.CSSProperties = {
  fontSize: 12,
  textTransform: "uppercase",
  letterSpacing: 0.8,
  fontWeight: 700,
  color: "oklch(50% 0.05 240)",
  margin: "0 0 4px 0",
};
