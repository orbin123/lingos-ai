import { Sparkles } from "lucide-react";
import type { AnswerView } from "../../teaching/source";
import type { ActivityEvaluation } from "../source";
import { tierStyles } from "./EvaluationTheme";

export function WriteSpeakEvaluationWidget({
  evaluation,
  answerView,
}: {
  evaluation: ActivityEvaluation;
  answerView: AnswerView;
}) {
  const output = evaluation.outputs[answerView];
  const tier = tierStyles[output.tier];

  return (
    <section
      style={{
        borderRadius: 18,
        padding: "16px 18px",
        marginBottom: 14,
        display: "flex",
        alignItems: "center",
        gap: 14,
        background: "white",
        border: "1.5px solid oklch(85% 0.025 240)",
        boxShadow: "0 2px 10px rgba(80,110,180,0.07)",
        animation: "testChatFadeIn 0.35s ease both",
      }}
    >
      <div
        style={{
          width: 46,
          height: 46,
          borderRadius: 14,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: tier.bg,
          color: tier.fg,
          flexShrink: 0,
        }}
      >
        <Sparkles size={20} strokeWidth={2.5} />
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 15, fontWeight: 800, color: "oklch(20% 0.09 245)" }}>
          {output.attendedLabel}
        </div>
        <div style={{ marginTop: 3, fontSize: 12.5, color: "oklch(45% 0.07 240)" }}>
          Performance: {tier.label}
        </div>
      </div>
      <div style={{ textAlign: "right", flexShrink: 0 }}>
        <div style={{ fontSize: 24, fontWeight: 800, color: "oklch(20% 0.09 245)", lineHeight: 1 }}>
          {output.percentage}
          <span style={{ fontSize: 14, color: "oklch(45% 0.07 240)" }}>%</span>
        </div>
        <div style={{ marginTop: 4, fontSize: 11, fontWeight: 800, color: "oklch(45% 0.07 240)", textTransform: "uppercase" }}>
          Quality
        </div>
      </div>
    </section>
  );
}
