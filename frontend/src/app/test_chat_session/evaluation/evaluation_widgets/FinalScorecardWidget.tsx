import { Check } from "lucide-react";
import type { AnswerView } from "../../teaching/source";
import type { OverallScorecard } from "../source";
import { sectionLabelStyle, skillOrder, tierStyles } from "./EvaluationTheme";

export function FinalScorecardWidget({
  scorecard,
  answerView,
}: {
  scorecard: OverallScorecard;
  answerView: AnswerView;
}) {
  const activities = scorecard.activities[answerView];
  const pointsEarned = scorecard.pointsEarned[answerView];
  const average = activities.length
    ? activities.reduce((sum, item) => sum + item.rawScore, 0) / activities.length
    : 0;

  return (
    <div style={{ animation: "testChatFadeIn 0.35s ease both", marginTop: 2, marginBottom: 16 }}>
      <header style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6, marginBottom: 14 }}>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 7,
            padding: "5px 12px",
            borderRadius: 999,
            background: "white",
            border: "1px solid oklch(85% 0.025 240)",
            fontSize: 12,
            fontWeight: 800,
            color: "oklch(40% 0.16 155)",
            textTransform: "uppercase",
          }}
        >
          <Check size={13} strokeWidth={3} />
          Session complete
        </div>
        <p style={{ margin: 0, fontSize: 14, color: "oklch(35% 0.09 240)" }}>
          Points added to the mock dashboard.
        </p>
      </header>

      <section
        style={{
          background: "linear-gradient(135deg, oklch(95% 0.05 240) 0%, white 70%)",
          borderRadius: 22,
          padding: "20px 24px",
          border: "1.5px solid rgba(255,255,255,0.92)",
          boxShadow: "0 8px 32px rgba(80,110,180,0.14)",
          display: "flex",
          flexDirection: "column",
          gap: 20,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 18 }}>
          <div>
            <div style={sectionLabelStyle}>Overall score</div>
            <div style={{ fontSize: 28, fontWeight: 800, color: "oklch(20% 0.09 245)", lineHeight: 1 }}>
              {average.toFixed(1)}
              <span style={{ fontSize: 16, color: "oklch(45% 0.07 240)" }}>/10</span>
            </div>
          </div>
          <ScoreRing pct={Math.round(average * 10)} />
        </div>

        <div>
          <div style={sectionLabelStyle}>Activity scores</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: 12 }}>
            {activities.map((activity) => {
              const tier = tierStyles[activity.tier];
              return (
                <div
                  key={activity.taskId}
                  style={{
                    border: "1px solid oklch(90% 0.03 240)",
                    borderRadius: 12,
                    padding: "12px 10px",
                    textAlign: "center",
                    background: "oklch(99% 0.005 240)",
                  }}
                >
                  <div style={{ fontSize: 14, fontWeight: 800, color: "oklch(35% 0.07 240)" }}>
                    {activity.label}
                  </div>
                  <div style={{ marginTop: 7, fontSize: 22, fontWeight: 800, color: "oklch(20% 0.08 245)" }}>
                    {activity.rawScore.toFixed(1)}
                    <span style={{ fontSize: 14, color: "oklch(50% 0.04 240)" }}>/10</span>
                  </div>
                  <div
                    style={{
                      display: "inline-block",
                      marginTop: 8,
                      padding: "3px 9px",
                      borderRadius: 999,
                      background: tier.bg,
                      color: tier.fg,
                      fontSize: 10.5,
                      fontWeight: 800,
                      textTransform: "uppercase",
                    }}
                  >
                    {tier.label}
                  </div>
                  <div style={{ marginTop: 8, fontSize: 13, fontWeight: 700, color: "oklch(40% 0.07 240)" }}>
                    +{activity.baseReward} pts
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div>
          <div style={sectionLabelStyle}>Sub-skill points earned</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(118px, 1fr))", gap: 10 }}>
            {skillOrder.map((skill) => {
              const earned = pointsEarned[skill] ?? 0;
              return (
                <div
                  key={skill}
                  style={{
                    border: "1px solid oklch(90% 0.03 240)",
                    borderRadius: 12,
                    padding: "10px 6px",
                    textAlign: "center",
                    background: earned > 0 ? "oklch(97% 0.03 155)" : "oklch(99% 0.005 240)",
                  }}
                >
                  <div
                    style={{
                      minHeight: 28,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 10,
                      fontWeight: 800,
                      color: "oklch(45% 0.07 240)",
                      textTransform: "uppercase",
                    }}
                  >
                    {scorecard.skillLabels[skill] ?? skill}
                  </div>
                  <div
                    style={{
                      marginTop: 5,
                      fontSize: 20,
                      fontWeight: 800,
                      color: earned > 0 ? "oklch(35% 0.18 155)" : "oklch(60% 0.03 240)",
                    }}
                  >
                    {earned > 0 ? `+${earned}` : "0"}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
}

function ScoreRing({ pct }: { pct: number }) {
  const r = 38;
  const c = 2 * Math.PI * r;
  const offset = c - (pct / 100) * c;

  return (
    <div style={{ position: "relative", width: 92, height: 92, flexShrink: 0 }}>
      <svg width="92" height="92" viewBox="0 0 92 92">
        <circle cx="46" cy="46" r={r} stroke="oklch(92% 0.025 240)" strokeWidth="9" fill="none" />
        <circle
          cx="46"
          cy="46"
          r={r}
          stroke="#0070C4"
          strokeWidth="9"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          transform="rotate(-90 46 46)"
        />
      </svg>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
          fontWeight: 800,
          color: "oklch(20% 0.09 245)",
        }}
      >
        <span style={{ fontSize: 22, lineHeight: 1 }}>
          {pct}
          <span style={{ fontSize: 13, color: "oklch(45% 0.07 240)" }}>%</span>
        </span>
        <span style={{ fontSize: 10, color: "oklch(45% 0.07 240)", marginTop: 2 }}>SCORE</span>
      </div>
    </div>
  );
}
