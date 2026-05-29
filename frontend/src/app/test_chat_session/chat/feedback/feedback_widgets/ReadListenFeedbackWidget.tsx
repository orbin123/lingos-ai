import { Check, ListChecks } from "lucide-react";
import type { AnswerView } from "../../teaching/source";
import type { ActivityFeedback } from "../source";
import { FeedbackMistakeRow } from "./FeedbackMistakeRow";

export function ReadListenFeedbackWidget({
  feedback,
  answerView,
}: {
  feedback: ActivityFeedback;
  answerView: AnswerView;
}) {
  const output = feedback.outputs[answerView];
  const hasMistakes = output.mistakes.length > 0;

  return (
    <section
      style={{
        borderRadius: 22,
        marginBottom: 22,
        background: "rgba(255,255,255,0.94)",
        border: "1.5px solid rgba(255,255,255,0.92)",
        boxShadow: "0 4px 28px rgba(80,110,180,0.1)",
        overflow: "hidden",
        animation: "testChatFadeIn 0.35s ease both",
      }}
    >
      <FeedbackHeader
        score={output.score}
        summary={output.summary}
        didWell={output.didWell}
        hasMistakes={hasMistakes}
      />

      {output.mistakes.map((mistake, index) => (
        <FeedbackMistakeRow
          key={`${mistake.issue}-${index}`}
          mistake={mistake}
          isLast={index === output.mistakes.length - 1}
        />
      ))}

      <NextTip>{output.nextTip}</NextTip>
    </section>
  );
}

function FeedbackHeader({
  score,
  summary,
  didWell,
  hasMistakes,
}: {
  score: number;
  summary: string;
  didWell: string[];
  hasMistakes: boolean;
}) {
  return (
    <div style={{ padding: "17px 20px", borderBottom: hasMistakes ? "1px solid oklch(88% 0.025 240)" : "none" }}>
      <div style={{ display: "flex", gap: 14, alignItems: "center" }}>
        <div
          style={{
            width: 34,
            height: 34,
            borderRadius: "50%",
            flexShrink: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: hasMistakes ? "oklch(60% 0.15 60)" : "oklch(55% 0.16 155)",
            color: "white",
          }}
        >
          {hasMistakes ? <ListChecks size={17} /> : <Check size={18} strokeWidth={3} />}
        </div>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 14.5, fontWeight: 800, color: "oklch(18% 0.06 240)" }}>
            {summary}
          </div>
          {didWell.length > 0 && (
            <div style={{ marginTop: 5, fontSize: 12.5, color: "oklch(45% 0.07 240)", lineHeight: 1.5 }}>
              {didWell.join(" ")}
            </div>
          )}
        </div>
        <div
          style={{
            marginLeft: "auto",
            fontSize: 18,
            fontWeight: 800,
            color: "oklch(20% 0.09 245)",
            whiteSpace: "nowrap",
          }}
        >
          {score}/10
        </div>
      </div>
    </div>
  );
}

function NextTip({ children }: { children: string }) {
  return (
    <div
      style={{
        padding: "14px 20px",
        background: "oklch(96% 0.025 245)",
        fontSize: 13,
        lineHeight: 1.55,
        color: "oklch(35% 0.07 240)",
      }}
    >
      <strong>Next: </strong>
      {children}
    </div>
  );
}
