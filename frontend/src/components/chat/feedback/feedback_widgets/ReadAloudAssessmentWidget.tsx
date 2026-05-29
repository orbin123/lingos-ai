import { FileText, Mic2, Sparkles } from "lucide-react";
import type { ReactNode } from "react";
import type { AnswerView } from "../../teaching/source";
import type { ReadAloudTask } from "../../tasks/source";
import type {
  ActivityEvaluation,
  PronunciationWordScore,
} from "../../evaluation/source";
import type { ActivityFeedback } from "../source";

export function ReadAloudAssessmentWidget({
  task,
  evaluation,
  feedback,
  answerView,
}: {
  task: ReadAloudTask;
  evaluation: ActivityEvaluation;
  feedback: ActivityFeedback;
  answerView: AnswerView;
}) {
  const evalOutput = evaluation.outputs[answerView];
  const feedbackOutput = feedback.outputs[answerView];
  const pronunciation = evalOutput.pronunciationAssessment;

  if (!pronunciation) {
    return null;
  }

  const scores = [
    { label: "Accuracy", score: pronunciation.accuracyScore, description: "Phoneme precision" },
    { label: "Fluency", score: pronunciation.fluencyScore, description: "Pacing and pauses" },
    { label: "Completeness", score: pronunciation.completenessScore, description: "Words spoken" },
    ...(pronunciation.prosodyScore != null && pronunciation.prosodyScore > 0
      ? [{ label: "Prosody", score: pronunciation.prosodyScore, description: "Stress and rhythm" }]
      : []),
  ];
  const metricAverage = Math.round(
    scores.reduce((sum, score) => sum + score.score, 0) / scores.length,
  );
  const wordsToReview = pronunciation.words.filter(
    (word) => word.errorType !== "none" || word.accuracyScore < 80,
  );

  return (
    <section
      style={{
        borderRadius: 22,
        marginBottom: 22,
        background: "rgba(255,255,255,0.94)",
        border: "1.5px solid rgba(255,255,255,0.92)",
        boxShadow: "0 8px 32px rgba(80,110,180,0.13)",
        overflow: "hidden",
        animation: "testChatFadeIn 0.35s ease both",
      }}
    >
      <div
        style={{
          padding: "20px 22px 16px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 16,
          borderBottom: "1px solid oklch(92% 0.01 245)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 14, minWidth: 0 }}>
          <div
            style={{
              width: 46,
              height: 46,
              borderRadius: 14,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              background: "#0070C4",
              flexShrink: 0,
              boxShadow: "0 5px 14px rgba(0,112,196,0.28)",
            }}
          >
            <Mic2 size={21} strokeWidth={2.5} />
          </div>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontSize: 18, fontWeight: 800, color: "oklch(20% 0.09 245)" }}>
              Read aloud assessment
            </div>
            <div style={{ fontSize: 13.5, color: "oklch(45% 0.07 240)", marginTop: 4, lineHeight: 1.45 }}>
              {feedbackOutput.summary}
            </div>
          </div>
        </div>
        <ScoreBadge score={pronunciation.overallScore} label="Overall" />
      </div>

      <div style={{ padding: "16px 22px", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12 }}>
        {scores.map((score) => (
          <MetricCard
            key={score.label}
            label={score.label}
            score={score.score}
            description={score.description}
          />
        ))}
        <MetricCard
          label="Average"
          score={metricAverage}
          description="Mean of visible metrics"
          emphasis
        />
      </div>

      <div style={{ padding: "2px 22px 16px" }}>
        <SectionTitle>How you read it</SectionTitle>
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "8px 5px",
            lineHeight: 1.8,
            fontSize: 15,
            padding: "14px 16px",
            background: "oklch(99% 0.01 245)",
            border: "1px solid oklch(93% 0.01 245)",
            borderRadius: 12,
          }}
        >
          {pronunciation.words.map((word, index) => (
            <PronunciationWord key={`${word.word}-${index}`} word={word} />
          ))}
        </div>
        <Legend />
      </div>

      {wordsToReview.length > 0 && (
        <div style={{ padding: "0 22px 16px" }}>
          <SectionTitle>Words to review</SectionTitle>
          <div style={{ display: "grid", gap: 8 }}>
            {wordsToReview.map((word, index) => (
              <WordReviewRow key={`${word.word}-review-${index}`} word={word} />
            ))}
          </div>
        </div>
      )}

      <div style={{ padding: "0 22px 16px" }}>
        <SectionTitle>Model passage</SectionTitle>
        <div
          style={{
            padding: "14px 16px",
            background: "oklch(96% 0.02 245)",
            borderRadius: 12,
            fontSize: 14,
            lineHeight: 1.65,
            color: "oklch(20% 0.09 245)",
            borderLeft: "4px solid oklch(62% 0.16 240)",
          }}
        >
          {task.textToReadAloud}
        </div>
      </div>

      <div
        style={{
          padding: "16px 22px 20px",
          display: "flex",
          flexDirection: "column",
          gap: 12,
          borderTop: "1px solid oklch(92% 0.01 245)",
        }}
      >
        <SectionTitle>Coach&apos;s tips</SectionTitle>
        {feedbackOutput.didWell.length > 0 && (
          <div>
            <div style={{ fontSize: 12.5, fontWeight: 800, color: "oklch(48% 0.18 155)", marginBottom: 4 }}>
              What you did well
            </div>
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13, lineHeight: 1.6, color: "oklch(20% 0.09 245)" }}>
              {feedbackOutput.didWell.map((item) => (
                <li key={item} style={{ marginBottom: 2 }}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {feedbackOutput.mistakes.length > 0 && (
          <div>
            <div style={{ fontSize: 12.5, fontWeight: 800, color: "oklch(50% 0.15 25)", marginBottom: 6 }}>
              Areas to improve
            </div>
            {feedbackOutput.mistakes.map((mistake, index) => (
              <div
                key={`${mistake.issue}-${index}`}
                style={{
                  background: "oklch(98% 0.01 25)",
                  padding: "9px 12px",
                  borderRadius: 8,
                  borderLeft: "3px solid oklch(65% 0.15 25)",
                  marginBottom: 6,
                }}
              >
                <div style={{ fontSize: 13, fontWeight: 800, color: "oklch(20% 0.09 245)" }}>
                  {mistake.issue}
                </div>
                {mistake.rule && (
                  <div style={{ fontSize: 12, color: "oklch(45% 0.07 240)", marginTop: 2 }}>
                    {mistake.rule}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div style={{ background: "oklch(96% 0.03 245)", padding: "10px 14px", borderRadius: 8, fontSize: 13 }}>
          <span style={{ fontWeight: 800, color: "oklch(52% 0.18 240)" }}>Next tip: </span>
          <span style={{ color: "oklch(20% 0.09 245)" }}>{feedbackOutput.nextTip}</span>
        </div>
      </div>
    </section>
  );
}

function MetricCard({
  label,
  score,
  description,
  emphasis = false,
}: {
  label: string;
  score: number;
  description: string;
  emphasis?: boolean;
}) {
  const color = scoreColor(score);

  return (
    <div
      style={{
        background: emphasis ? "oklch(96% 0.03 245)" : scoreBg(score),
        border: emphasis ? "1px dashed oklch(82% 0.06 245)" : "1px solid oklch(93% 0.01 245)",
        padding: "12px 14px",
        borderRadius: 12,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
        <span style={{ fontSize: 13, fontWeight: 800, color: "oklch(20% 0.09 245)" }}>{label}</span>
        <span style={{ fontSize: 14, fontWeight: 800, color }}>{Math.round(score)}%</span>
      </div>
      <div style={{ width: "100%", height: 6, background: "oklch(93% 0.01 245)", borderRadius: 999, overflow: "hidden" }}>
        <div style={{ width: `${Math.max(0, Math.min(100, score))}%`, height: "100%", background: color, borderRadius: 999 }} />
      </div>
      <div style={{ fontSize: 11, color: "oklch(45% 0.07 240)", marginTop: 5 }}>{description}</div>
    </div>
  );
}

function ScoreBadge({ score, label }: { score: number; label: string }) {
  return (
    <div
      style={{
        borderRadius: 12,
        padding: "10px 16px",
        background: scoreColor(score),
        color: "white",
        minWidth: 78,
        textAlign: "center",
        flexShrink: 0,
        boxShadow: "0 4px 14px rgba(0,0,0,0.08)",
      }}
    >
      <div style={{ fontSize: 24, fontWeight: 900, lineHeight: 1 }}>
        {Math.round(score)}
        <span style={{ fontSize: 13, opacity: 0.86 }}>%</span>
      </div>
      <div style={{ fontSize: 10, fontWeight: 800, textTransform: "uppercase", marginTop: 4 }}>
        {label}
      </div>
    </div>
  );
}

function PronunciationWord({ word }: { word: PronunciationWordScore }) {
  const style = wordStyle(word);

  return (
    <span
      title={`Accuracy: ${Math.round(word.accuracyScore)}%${word.errorType !== "none" ? ` (${word.errorType})` : ""}`}
      style={{
        color: style.color,
        backgroundColor: style.background,
        textDecoration: style.textDecoration,
        fontWeight: style.fontWeight,
        padding: style.background !== "transparent" ? "2px 6px" : "0 2px",
        borderRadius: 4,
        cursor: "help",
      }}
    >
      {word.word}
    </span>
  );
}

function WordReviewRow({ word }: { word: PronunciationWordScore }) {
  const weakestPhoneme = [...word.phonemes].sort((a, b) => a.accuracyScore - b.accuracyScore)[0];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "minmax(90px, 0.8fr) minmax(120px, 1fr) auto",
        gap: 10,
        alignItems: "center",
        padding: "10px 12px",
        borderRadius: 12,
        background: "oklch(98% 0.01 25)",
        border: "1px solid oklch(92% 0.03 25)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 7, minWidth: 0 }}>
        <FileText size={14} color="oklch(50% 0.15 25)" />
        <span style={{ fontSize: 13.5, fontWeight: 800, color: "oklch(20% 0.09 245)" }}>{word.word}</span>
      </div>
      <div style={{ fontSize: 12.5, color: "oklch(45% 0.07 240)", lineHeight: 1.35 }}>
        Weakest sound: {weakestPhoneme?.phoneme ?? "sound"} at {Math.round(weakestPhoneme?.accuracyScore ?? word.accuracyScore)}%
      </div>
      <div style={{ fontSize: 13, fontWeight: 900, color: scoreColor(word.accuracyScore) }}>
        {Math.round(word.accuracyScore)}%
      </div>
    </div>
  );
}

function Legend() {
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: "10px 16px", fontSize: 11.5, color: "oklch(45% 0.07 240)", marginTop: 8, paddingLeft: 2 }}>
      <LegendItem color="oklch(48% 0.18 155)" label="Good (>=80%)" />
      <LegendItem color="oklch(60% 0.13 80)" label="Needs work" />
      <LegendItem color="oklch(50% 0.15 25)" label="Mispronounced" />
      <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
        <span style={{ textDecoration: "line-through", color: "oklch(60% 0.1 20)", fontWeight: 800, fontSize: 12 }}>Aa</span>
        <span>Omitted</span>
      </div>
    </div>
  );
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
      <span style={{ width: 9, height: 9, borderRadius: "50%", background: color }} />
      <span>{label}</span>
    </div>
  );
}

function SectionTitle({ children }: { children: ReactNode }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 6,
        fontSize: 11.5,
        textTransform: "uppercase",
        letterSpacing: 0.8,
        fontWeight: 800,
        color: "oklch(50% 0.05 240)",
        marginBottom: 8,
      }}
    >
      <Sparkles size={13} />
      {children}
    </div>
  );
}

function wordStyle(word: PronunciationWordScore) {
  if (word.errorType === "omission") {
    return {
      color: "oklch(60% 0.1 20)",
      background: "transparent",
      textDecoration: "line-through",
      fontWeight: 500,
    };
  }
  if (word.errorType === "insertion") {
    return {
      color: "oklch(50% 0.15 45)",
      background: "oklch(96% 0.05 45)",
      textDecoration: "none",
      fontWeight: 800,
    };
  }
  if (word.errorType === "mispronunciation") {
    return {
      color: "oklch(50% 0.15 25)",
      background: "oklch(96% 0.05 25)",
      textDecoration: "none",
      fontWeight: 800,
    };
  }
  if (word.accuracyScore < 80) {
    return {
      color: "oklch(60% 0.13 80)",
      background: "transparent",
      textDecoration: "none",
      fontWeight: 700,
    };
  }
  return {
    color: "oklch(48% 0.18 155)",
    background: "transparent",
    textDecoration: "none",
    fontWeight: 600,
  };
}

function scoreColor(score: number) {
  if (score >= 80) return "oklch(48% 0.18 155)";
  if (score >= 60) return "oklch(60% 0.13 80)";
  return "oklch(50% 0.15 25)";
}

function scoreBg(score: number) {
  if (score >= 80) return "oklch(96% 0.02 155)";
  if (score >= 60) return "oklch(98% 0.01 80)";
  return "oklch(98% 0.01 25)";
}
