"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Brain, Target, Wrench, Repeat, BarChart, Layers, ArrowRight } from "lucide-react";
import { LandingNavbar } from "@/components/layout/LandingNavbar";
import { LandingFooter } from "@/components/layout/LandingFooter";
import { useMarketingCTA } from "@/hooks/useMarketingCTA";

const ACCENT_HUE = 240;

// ── Glassmorphism card ──────────────────────────────────────────────────────
function GlassCard({
  children,
  style,
  className,
}: {
  children: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
}) {
  return (
    <div
      className={className}
      style={{
        background: "rgba(255,255,255,0.6)",
        backdropFilter: "blur(18px)",
        WebkitBackdropFilter: "blur(18px)",
        border: "1.5px solid rgba(255,255,255,0.88)",
        borderRadius: 20,
        boxShadow:
          "0 4px 32px rgba(100,140,210,0.13), 0 1.5px 6px rgba(80,120,200,0.07)",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

// ── Dot grid texture ────────────────────────────────────────────────────────
function DotGrid({ opacity = 0.18 }: { opacity?: number }) {
  return (
    <svg
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
      }}
      aria-hidden
    >
      <defs>
        <pattern
          id="dots"
          x="0"
          y="0"
          width="22"
          height="22"
          patternUnits="userSpaceOnUse"
        >
          <circle cx="2" cy="2" r="1.1" fill={`rgba(90,130,210,${opacity})`} />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#dots)" />
    </svg>
  );
}

// ── NAV REPLACED WITH SHARED COMPONENT ───────────────────────────────────────

// ── UI Mock Components ───────────────────────────────────────────────────────
function FeedbackCard() {
  return (
    <GlassCard style={{ padding: 18, fontSize: 13, width: "100%" }}>
      <div
        style={{
          fontWeight: 600,
          color: "oklch(40% 0.1 240)",
          marginBottom: 10,
          fontSize: 12,
          letterSpacing: 0.5,
          textTransform: "uppercase",
        }}
      >
        AI Feedback
      </div>
      <div
        style={{ lineHeight: 1.7, color: "oklch(25% 0.07 240)" }}
      >
        &ldquo;I{" "}
        <span
          style={{
            background: "rgba(220,60,60,0.12)",
            borderBottom: "2px solid rgba(220,60,60,0.5)",
            borderRadius: 2,
          }}
        >
          am study
        </span>{" "}
        English every day.&rdquo;
      </div>
      <div
        style={{
          marginTop: 12,
          padding: "10px 12px",
          borderRadius: 10,
          background: "rgba(200,230,255,0.5)",
          border: "1px solid rgba(160,200,255,0.4)",
        }}
      >
        <div
          style={{
            fontWeight: 600,
            color: "oklch(35% 0.12 240)",
            fontSize: 12,
            marginBottom: 4,
          }}
        >
          ⚠ Grammar Error
        </div>
        <div
          style={{
            color: "oklch(30% 0.08 240)",
            fontSize: 12,
            lineHeight: 1.6,
          }}
        >
          Use present continuous correctly:{" "}
          <strong>&ldquo;I am studying&rdquo;</strong> — the verb requires the
          -ing form after &ldquo;am&rdquo;.
        </div>
      </div>
      <div
        style={{
          marginTop: 8,
          padding: "8px 12px",
          borderRadius: 10,
          background: "rgba(180,230,200,0.4)",
          border: "1px solid rgba(130,200,160,0.4)",
        }}
      >
        <div
          style={{
            fontWeight: 600,
            color: "oklch(35% 0.12 145)",
            fontSize: 12,
            marginBottom: 3,
          }}
        >
          ✓ Better version
        </div>
        <div style={{ color: "oklch(28% 0.08 145)", fontSize: 12 }}>
          &ldquo;I am studying English every day.&rdquo;
        </div>
      </div>
    </GlassCard>
  );
}

function RadarChart({
  skills,
}: {
  skills: { label: string; val: number }[];
}) {
  const cx = 90,
    cy = 90,
    r = 68;
  const n = skills.length;
  const pts = (level: number) =>
    skills.map((_, i) => {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
      const d = r * level;
      return [cx + d * Math.cos(angle), cy + d * Math.sin(angle)];
    });
  const toPath = (p: number[][]) =>
    p.map((pt, i) => `${i === 0 ? "M" : "L"}${pt[0]},${pt[1]}`).join(" ") +
    "Z";

  return (
    <svg width="280" height="220" viewBox="-50 -20 280 220">
      {[0.25, 0.5, 0.75, 1].map((l) => (
        <polygon
          key={l}
          points={pts(l)
            .map((p) => p.join(","))
            .join(" ")}
          fill="none"
          stroke="rgba(100,150,220,0.18)"
          strokeWidth="1"
        />
      ))}
      {skills.map((_, i) => {
        const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
        return (
          <line
            key={i}
            x1={cx}
            y1={cy}
            x2={cx + r * Math.cos(angle)}
            y2={cy + r * Math.sin(angle)}
            stroke="rgba(100,150,220,0.2)"
            strokeWidth="1"
          />
        );
      })}
      <path
        d={toPath(
          pts(1).map((_, i) => {
            const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
            const d = r * skills[i].val;
            return [cx + d * Math.cos(angle), cy + d * Math.sin(angle)];
          })
        )}
        fill="rgba(80,140,220,0.18)"
        stroke="rgba(80,140,220,0.7)"
        strokeWidth="1.5"
      />
      {skills.map((s, i) => {
        const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
        const d = r * s.val;
        return (
          <circle
            key={i}
            cx={cx + d * Math.cos(angle)}
            cy={cy + d * Math.sin(angle)}
            r="3.5"
            fill="rgba(60,120,210,0.9)"
          />
        );
      })}
      {skills.map((s, i) => {
        const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
        const lx = cx + (r + 16) * Math.cos(angle);
        const ly = cy + (r + 16) * Math.sin(angle);
        return (
          <text
            key={i}
            x={lx}
            y={ly}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize="9"
            fill="oklch(35% 0.1 240)"
            fontFamily="Plus Jakarta Sans"
          >
            {s.label}
          </text>
        );
      })}
    </svg>
  );
}

// ── HERO ─────────────────────────────────────────────────────────────────────
function Hero({ onCTAClick, ctaText }: { onCTAClick: () => void; ctaText: string }) {
  return (
    <section
      style={{
        minHeight: "75svh",
        background: `radial-gradient(ellipse 80% 60% at 50% 0%, oklch(82% 0.08 ${ACCENT_HUE}) 0%, oklch(88% 0.05 ${ACCENT_HUE - 5}) 45%, oklch(92% 0.03 ${ACCENT_HUE + 10}) 100%)`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
        paddingTop: 100,
        paddingBottom: 100,
        textAlign: "center",
      }}
    >
      <DotGrid opacity={0.14} />
      <div
        style={{
          maxWidth: 800,
          margin: "0 auto",
          padding: "0 40px",
          position: "relative",
          zIndex: 10,
        }}
      >
        <h1
          style={{
            fontSize: "clamp(38px, 5vw, 64px)",
            fontWeight: 800,
            lineHeight: 1.1,
            letterSpacing: "-1.5px",
            color: "oklch(15% 0.09 245)",
            marginBottom: 24,
          }}
        >
          A smarter way to improve your English —{" "}
          <span style={{ color: `oklch(40% 0.14 ${ACCENT_HUE})` }}>
            with real feedback, not guesses.
          </span>
        </h1>
        <p
          style={{
            fontSize: "clamp(18px, 2vw, 22px)",
            color: "oklch(38% 0.08 240)",
            lineHeight: 1.6,
            marginBottom: 44,
            fontWeight: 400,
          }}
        >
          Track your weaknesses, practice daily, and improve faster with AI.
        </p>
        <button
          onClick={onCTAClick}
          style={{
            padding: "16px 36px",
            borderRadius: 50,
            border: "none",
            cursor: "pointer",
            background: `oklch(20% 0.09 ${ACCENT_HUE})`,
            color: "white",
            fontFamily: "inherit",
            fontWeight: 700,
            fontSize: 17,
            boxShadow: "0 6px 28px rgba(20,50,120,0.25)",
            transition: "transform 0.15s, box-shadow 0.15s",
            letterSpacing: "-0.2px",
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "scale(1.04)";
            e.currentTarget.style.boxShadow =
              "0 8px 34px rgba(20,50,120,0.32)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "scale(1)";
            e.currentTarget.style.boxShadow =
              "0 6px 28px rgba(20,50,120,0.25)";
          }}
        >
          {ctaText} <ArrowRight size={18} />
        </button>
      </div>
    </section>
  );
}

// ── CORE FEATURES ────────────────────────────────────────────────────────────
function CoreFeatures() {
  const features = [
    {
      title: "Skill Breakdown Engine",
      desc: "Pinpoint your exact weaknesses across grammar, fluency, and clarity.",
      icon: <Brain size={26} strokeWidth={2.2} />,
      color: "230",
    },
    {
      title: "Adaptive Task System",
      desc: "Tasks that automatically adjust based on your performance.",
      icon: <Target size={26} strokeWidth={2.2} />,
      color: "250",
    },
    {
      title: "Precision Feedback Engine",
      desc: "Get exact corrections, explanations, and improvement tips.",
      icon: <Wrench size={26} strokeWidth={2.2} />,
      color: "210",
    },
    {
      title: "Pattern Detection",
      desc: "We track your repeated mistakes and help you fix them permanently.",
      icon: <Repeat size={26} strokeWidth={2.2} />,
      color: "270",
    },
    {
      title: "Progress Intelligence",
      desc: "Visualize your improvement across multiple communication skills.",
      icon: <BarChart size={26} strokeWidth={2.2} />,
      color: "220",
    },
    {
      title: "Multi-Skill Training",
      desc: "Every task improves multiple skills at once — not just one.",
      icon: <Layers size={26} strokeWidth={2.2} />,
      color: "245",
    },
  ];
  return (
    <section
      style={{
        padding: "100px 40px",
        background: "oklch(94% 0.015 240)",
      }}
    >
      <div style={{ maxWidth: 1180, margin: "0 auto" }}>
        <div style={{ textAlign: "center", marginBottom: 64 }}>
          <div
            style={{
              fontSize: 13,
              fontWeight: 600,
              letterSpacing: 1,
              color: "oklch(48% 0.14 240)",
              textTransform: "uppercase",
              marginBottom: 14,
            }}
          >
            Core Capabilities
          </div>
          <h2
            style={{
              fontSize: "clamp(30px, 3.5vw, 48px)",
              fontWeight: 800,
              letterSpacing: "-1px",
              color: "oklch(15% 0.09 245)",
              lineHeight: 1.15,
            }}
          >
            What makes LingosAI different
          </h2>
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
            gap: 24,
            justifyContent: "center",
          }}
        >
          {features.map((f, i) => (
            <GlassCard
              key={i}
              style={{
                padding: 32,
                transition: "transform 0.2s, box-shadow 0.2s",
                cursor: "default",
              }}
              className="landing-feature-card"
            >
              <div
                style={{
                  width: 52,
                  height: 52,
                  borderRadius: 14,
                  marginBottom: 20,
                  background: `oklch(82% 0.09 ${f.color})`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 26,
                  boxShadow: `0 4px 14px oklch(82% 0.09 ${f.color} / 0.4)`,
                }}
              >
                {f.icon}
              </div>
              <div
                style={{
                  fontWeight: 700,
                  fontSize: 18,
                  color: "oklch(18% 0.09 245)",
                  marginBottom: 10,
                }}
              >
                {f.title}
              </div>
              <div
                style={{
                  fontSize: 15,
                  color: "oklch(42% 0.07 240)",
                  lineHeight: 1.6,
                }}
              >
                {f.desc}
              </div>
            </GlassCard>
          ))}
        </div>
      </div>
    </section>
  );
}

// ── FEATURE BREAKDOWN ────────────────────────────────────────────────────────
function FeatureBreakdown() {
  return (
    <section
      style={{
        padding: "100px 40px",
        background:
          "linear-gradient(160deg, oklch(88% 0.045 240) 0%, oklch(91% 0.03 250) 100%)",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <DotGrid opacity={0.12} />
      <div style={{ maxWidth: 1080, margin: "0 auto", position: "relative" }}>

        {/* Row 1: Diagnosis */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 60,
            alignItems: "center",
            marginBottom: 120,
          }}
        >
          <div>
            <div
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: `oklch(45% 0.14 ${ACCENT_HUE})`,
                textTransform: "uppercase",
                letterSpacing: 1,
                marginBottom: 12,
              }}
            >
              Deep Skill Analysis
            </div>
            <h3
              style={{
                fontSize: 32,
                fontWeight: 800,
                color: "oklch(15% 0.09 245)",
                lineHeight: 1.2,
                letterSpacing: "-0.5px",
                marginBottom: 20,
              }}
            >
              Stop guessing what&apos;s holding you back
            </h3>
            <p
              style={{
                fontSize: 16,
                color: "oklch(38% 0.08 240)",
                lineHeight: 1.65,
              }}
            >
              LingosAI doesn&apos;t just test your vocabulary. We map your exact skill profile across 7 distinct dimensions. Our initial diagnosis uncovers the hidden grammar patterns and pronunciation hurdles that prevent you from sounding fluent.
            </p>
          </div>
          <div style={{ position: "relative" }}>
            <GlassCard style={{ padding: 32, display: "flex", flexDirection: "column", alignItems: "center" }}>
              <div
                style={{
                  fontWeight: 700,
                  fontSize: 14,
                  color: "oklch(38% 0.1 240)",
                  marginBottom: 20,
                  width: "100%",
                  textAlign: "center"
                }}
              >
                Your Skill Profile
              </div>
              <RadarChart
                skills={[
                  { label: "Grammar", val: 0.45 },
                  { label: "Vocabulary", val: 0.62 },
                  { label: "Pronunciation", val: 0.38 },
                  { label: "Fluency", val: 0.58 },
                  { label: "Expression", val: 0.42 },
                  { label: "Comprehension", val: 0.7 },
                  { label: "Speech Delivery", val: 0.35 },
                ]}
              />
            </GlassCard>
          </div>
        </div>

        {/* Row 2: Daily Tasks */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 60,
            alignItems: "center",
            marginBottom: 120,
          }}
        >
          <div style={{ order: 2 }}>
            <div
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: `oklch(45% 0.14 ${ACCENT_HUE})`,
                textTransform: "uppercase",
                letterSpacing: 1,
                marginBottom: 12,
              }}
            >
              Personalized Daily Tasks
            </div>
            <h3
              style={{
                fontSize: 32,
                fontWeight: 800,
                color: "oklch(15% 0.09 245)",
                lineHeight: 1.2,
                letterSpacing: "-0.5px",
                marginBottom: 20,
              }}
            >
              Built entirely around your weak areas
            </h3>
            <p
              style={{
                fontSize: 16,
                color: "oklch(38% 0.08 240)",
                lineHeight: 1.65,
              }}
            >
              Every morning, your AI coach generates a unique task designed to target the specific skills you need to improve. Whether it&apos;s practicing present continuous tenses or formatting a professional email, every task is purposeful.
            </p>
          </div>
          <div style={{ order: 1 }}>
            <GlassCard style={{ padding: 28 }}>
              <div
                style={{
                  fontWeight: 700,
                  fontSize: 14,
                  color: "oklch(38% 0.1 240)",
                  marginBottom: 4,
                }}
              >
                Today&apos;s Task
              </div>
              <div
                style={{
                  fontSize: 12,
                  color: "oklch(50% 0.07 240)",
                  marginBottom: 20,
                }}
              >
                Targeting: Grammar · Sentence Structure
              </div>
              <div
                style={{
                  background: "rgba(215,230,255,0.5)",
                  borderRadius: 14,
                  padding: 20,
                  marginBottom: 14,
                }}
              >
                <div
                  style={{
                    fontWeight: 700,
                    fontSize: 13,
                    color: "oklch(28% 0.12 240)",
                    marginBottom: 8,
                  }}
                >
                  📝 Writing Task — 5 min
                </div>
                <div
                  style={{
                    fontSize: 14,
                    color: "oklch(25% 0.08 240)",
                    lineHeight: 1.7,
                  }}
                >
                  Imagine you are writing an email to your manager explaining
                  why you will be 30 minutes late today. Write 3–4 sentences
                  using the correct present continuous tense.
                </div>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                {["Grammar", "Present Continuous", "Professional Writing"].map(
                  (t) => (
                    <span
                      key={t}
                      style={{
                        background: "rgba(190,215,255,0.55)",
                        borderRadius: 50,
                        padding: "4px 12px",
                        fontSize: 11,
                        fontWeight: 600,
                        color: "oklch(35% 0.14 240)",
                      }}
                    >
                      {t}
                    </span>
                  )
                )}
              </div>
            </GlassCard>
          </div>
        </div>

        {/* Row 3: Feedback Engine */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 60,
            alignItems: "center",
          }}
        >
          <div>
            <div
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: `oklch(45% 0.14 ${ACCENT_HUE})`,
                textTransform: "uppercase",
                letterSpacing: 1,
                marginBottom: 12,
              }}
            >
              Precise Feedback Engine
            </div>
            <h3
              style={{
                fontSize: 32,
                fontWeight: 800,
                color: "oklch(15% 0.09 245)",
                lineHeight: 1.2,
                letterSpacing: "-0.5px",
                marginBottom: 20,
              }}
            >
              Learn exactly why it&apos;s wrong
            </h3>
            <p
              style={{
                fontSize: 16,
                color: "oklch(38% 0.08 240)",
                lineHeight: 1.65,
              }}
            >
              Say goodbye to generic &ldquo;good job&rdquo; messages. Our AI acts like a strict human tutor. It breaks down every single sentence, flags the error, explains the underlying linguistic rule, and provides a corrected version so you never make the same mistake twice.
            </p>
          </div>
          <div>
            <FeedbackCard />
          </div>
        </div>
      </div>
    </section>
  );
}

// ── CTA ──────────────────────────────────────────────────────────────────────
function CTA({ onCTAClick, ctaText }: { onCTAClick: () => void; ctaText: string }) {
  return (
    <section
      style={{
        padding: "100px 40px",
        background: `linear-gradient(160deg, oklch(82% 0.07 ${ACCENT_HUE}) 0%, oklch(78% 0.09 ${ACCENT_HUE - 10}) 100%)`,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <DotGrid opacity={0.15} />
      <div
        style={{
          maxWidth: 700,
          margin: "0 auto",
          textAlign: "center",
          position: "relative",
        }}
      >
        <h2
          style={{
            fontSize: "clamp(32px, 4vw, 50px)",
            fontWeight: 800,
            letterSpacing: "-1.5px",
            color: "oklch(14% 0.09 245)",
            lineHeight: 1.1,
            marginBottom: 24,
          }}
        >
          Start improving your English today
        </h2>
        <div
          style={{
            display: "flex",
            gap: 14,
            justifyContent: "center",
            flexWrap: "wrap",
          }}
        >
          <button
            onClick={onCTAClick}
            style={{
              padding: "17px 44px",
              borderRadius: 50,
              border: "none",
              cursor: "pointer",
              background: "oklch(18% 0.09 245)",
              color: "white",
              fontFamily: "inherit",
              fontWeight: 700,
              fontSize: 18,
              boxShadow: "0 6px 30px rgba(10,30,100,0.25)",
              transition: "transform 0.15s, box-shadow 0.15s",
              letterSpacing: "-0.3px",
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "scale(1.04)";
              e.currentTarget.style.boxShadow =
                "0 8px 36px rgba(10,30,100,0.35)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "scale(1)";
              e.currentTarget.style.boxShadow =
                "0 6px 30px rgba(10,30,100,0.25)";
            }}
          >
            {ctaText} <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </section>
  );
}

// ── FOOTER REPLACED WITH SHARED COMPONENT ────────────────────────────────────

// ── PAGE ─────────────────────────────────────────────────────────────────────
export default function FeaturesPage() {
  const router = useRouter();
  const { isAuthed, ctaLabel, ctaHref } = useMarketingCTA();

  const handleCTA = () => router.push(ctaHref);

  return (
    <div
      style={{
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        background: "#dde8f5",
        color: "oklch(18% 0.06 240)",
        minHeight: "100vh",
        overflowX: "hidden",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />
      <LandingNavbar onCTAClick={handleCTA} showCTA={false} />
      <Hero onCTAClick={handleCTA} ctaText={isAuthed ? ctaLabel : "Start Free Diagnosis"} />
      <CoreFeatures />
      <FeatureBreakdown />
      <CTA onCTAClick={handleCTA} ctaText={isAuthed ? ctaLabel : "Try Now"} />
      <LandingFooter />
    </div>
  );
}
