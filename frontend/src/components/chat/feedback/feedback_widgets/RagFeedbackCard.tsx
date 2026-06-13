import { GraduationCap, CloudOff, Loader2 } from "lucide-react";
import type { AnswerView } from "../../teaching/source";
import type { RagFeedback } from "../source";
import { ReactionBar } from "../ReactionBar";

export type RagFeedbackState = "ready" | "pending" | "unavailable";

export function RagFeedbackCard({
  ragFeedback,
  answerView,
  state = "ready",
  scorecardId = null,
}: {
  ragFeedback: RagFeedback;
  answerView: AnswerView;
  state?: RagFeedbackState;
  scorecardId?: number | null;
}) {
  // Pending + unavailable share a muted, neutral treatment; the ready state
  // keeps the warm "coach" tone. Copy is kept in sync with the REST sessions
  // scorecard fallback (components/sessions/MentorNote.tsx).
  const muted = state !== "ready";

  return (
    <section
      style={{
        background: muted
          ? "linear-gradient(135deg, oklch(96% 0.01 240) 0%, oklch(99% 0.005 240) 70%)"
          : "linear-gradient(135deg, oklch(95.5% 0.04 50) 0%, oklch(99.5% 0.005 60) 70%)",
        borderRadius: 22,
        padding: "20px 24px",
        border: muted
          ? "1.5px solid oklch(92% 0.015 240)"
          : "1.5px solid oklch(90% 0.04 50)",
        boxShadow: muted
          ? "0 4px 14px rgba(100,120,160,0.06)"
          : "0 6px 20px rgba(180,140,60,0.08)",
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
            background: muted ? "oklch(92% 0.015 240)" : "oklch(90% 0.06 50)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: muted ? "oklch(55% 0.04 240)" : "oklch(40% 0.14 50)",
            flexShrink: 0,
          }}
        >
          {state === "pending" ? (
            <Loader2 size={16} className="animate-spin" />
          ) : state === "unavailable" ? (
            <CloudOff size={16} />
          ) : (
            <GraduationCap size={16} />
          )}
        </div>
        <span
          style={{
            fontSize: 11.5,
            fontWeight: 800,
            textTransform: "uppercase",
            letterSpacing: "0.04em",
            color: muted ? "oklch(55% 0.04 240)" : "oklch(40% 0.12 50)",
          }}
        >
          Coach&apos;s Note
        </span>
      </div>
      <p
        style={{
          margin: 0,
          fontSize: muted ? 13.5 : 14.5,
          lineHeight: 1.65,
          color: muted ? "oklch(45% 0.03 240)" : "oklch(22% 0.04 240)",
          fontWeight: muted ? 400 : 450,
          fontStyle: muted ? "italic" : "normal",
        }}
      >
        {state === "pending"
          ? "Generating your personalized coaching feedback from this session…"
          : state === "unavailable"
            ? "Your personalized coaching feedback couldn't be generated right now. Don't worry — your scores and progress are saved. Complete your next session to receive tailored mentor notes."
            : ragFeedback.outputs[answerView]}
      </p>

      {state === "ready" && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            paddingTop: 12,
            borderTop: "1px solid oklch(90% 0.04 50)",
          }}
        >
          <span
            style={{
              fontSize: 12,
              fontWeight: 700,
              color: "oklch(45% 0.06 50)",
            }}
          >
            Was this helpful?
          </span>
          <ReactionBar
            feedbackType="COACH_NOTE"
            feedbackId={scorecardId}
            copyText={ragFeedback.outputs[answerView] ?? ""}
            align="start"
          />
        </div>
      )}
    </section>
  );
}
