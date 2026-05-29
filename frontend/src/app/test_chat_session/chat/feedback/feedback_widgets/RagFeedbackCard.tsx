import { GraduationCap } from "lucide-react";
import type { AnswerView } from "../../teaching/source";
import type { RagFeedback } from "../source";

export function RagFeedbackCard({
  ragFeedback,
  answerView,
}: {
  ragFeedback: RagFeedback;
  answerView: AnswerView;
}) {
  return (
    <section
      style={{
        background: "linear-gradient(135deg, oklch(95.5% 0.04 50) 0%, oklch(99.5% 0.005 60) 70%)",
        borderRadius: 22,
        padding: "20px 24px",
        border: "1.5px solid oklch(90% 0.04 50)",
        boxShadow: "0 6px 20px rgba(180,140,60,0.08)",
        display: "flex",
        flexDirection: "column",
        gap: 14,
        marginBottom: 22,
        animation: "testChatFadeIn 0.35s ease both",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: 8,
            background: "oklch(90% 0.06 50)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "oklch(40% 0.14 50)",
            flexShrink: 0,
          }}
        >
          <GraduationCap size={16} />
        </div>
        <span
          style={{
            fontSize: 11.5,
            fontWeight: 800,
            textTransform: "uppercase",
            color: "oklch(40% 0.12 50)",
          }}
        >
          Coach&apos;s Note
        </span>
      </div>
      <p
        style={{
          margin: 0,
          fontSize: 14.5,
          lineHeight: 1.65,
          color: "oklch(22% 0.04 240)",
          fontWeight: 450,
        }}
      >
        {ragFeedback.outputs[answerView]}
      </p>
    </section>
  );
}
