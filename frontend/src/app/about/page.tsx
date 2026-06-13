"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Brain,
  Target,
  Wrench,
  Activity,
  Layers,
  BookOpen,
  Mic,
  Headphones,
  Zap,
  ArrowRight,
  Sparkles,
} from "lucide-react";
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

export default function AboutPage() {
  const router = useRouter();
  const { isAuthed, ctaLabel, ctaHref } = useMarketingCTA();

  return (
    <main
      style={{
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        minHeight: "100svh",
        background: `radial-gradient(circle at top right, oklch(90% 0.05 ${ACCENT_HUE}) 0%, oklch(95% 0.02 ${
          ACCENT_HUE + 10
        }) 40%, #ffffff 100%)`,
        paddingTop: 100,
        color: "oklch(20% 0.05 240)",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />
      <LandingNavbar showCTA={false} />

      {/* 1. HERO SECTION */}
      <section
        style={{
          position: "relative",
          padding: "80px 40px",
          textAlign: "center",
          maxWidth: 900,
          margin: "0 auto",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: "10%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: 400,
            height: 400,
            background: `radial-gradient(circle, oklch(85% 0.08 ${ACCENT_HUE}) 0%, transparent 70%)`,
            opacity: 0.5,
            pointerEvents: "none",
            zIndex: -1,
          }}
        />
        <h1
          style={{
            fontSize: "clamp(36px, 4vw, 56px)",
            fontWeight: 800,
            color: "oklch(15% 0.09 245)",
            lineHeight: 1.15,
            letterSpacing: "-1px",
            marginBottom: 24,
          }}
        >
          Built to make English learning structured, personal, and practical.
        </h1>
        <p
          style={{
            fontSize: 20,
            color: "oklch(40% 0.05 240)",
            lineHeight: 1.6,
            marginBottom: 40,
            maxWidth: 700,
            margin: "0 auto 40px auto",
          }}
        >
          LingosAI helps non-native speakers improve real-world communication
          through AI-powered feedback and personalized practice.
        </p>

        <div style={{ display: "flex", justifyContent: "center", gap: 16 }}>
          <div
            style={{
              width: 60,
              height: 60,
              borderRadius: 20,
              background: `oklch(95% 0.05 ${ACCENT_HUE})`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 8px 24px rgba(100,140,210,0.15)",
            }}
          >
            <Brain size={32} color={`oklch(45% 0.18 ${ACCENT_HUE})`} />
          </div>
          <div
            style={{
              width: 60,
              height: 60,
              borderRadius: 20,
              background: `oklch(95% 0.05 ${ACCENT_HUE})`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 8px 24px rgba(100,140,210,0.15)",
            }}
          >
            <Sparkles size={32} color={`oklch(45% 0.18 ${ACCENT_HUE})`} />
          </div>
        </div>
      </section>

      {/* 2. THE PROBLEM SECTION */}
      <section style={{ padding: "80px 40px", background: "white", position: "relative" }}>
        <DotGrid opacity={0.12} />
        <div style={{ maxWidth: 1000, margin: "0 auto", position: "relative" }}>
          <div style={{ textAlign: "center", marginBottom: 40 }}>
            <h2
              style={{
                fontSize: 36,
                fontWeight: 800,
                color: "oklch(20% 0.05 240)",
                marginBottom: 16,
                letterSpacing: "-0.5px",
              }}
            >
              Most English learning platforms are too generic.
            </h2>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: 24,
              marginBottom: 40,
            }}
          >
            {[
              "Random exercises without a clear plan",
              "Same static content for everyone",
              "No deep or actionable feedback",
              "No understanding of your personal weaknesses",
            ].map((point, i) => (
              <GlassCard key={i} style={{ padding: 24, textAlign: "center", background: "rgba(250, 245, 245, 0.5)", border: "1px solid rgba(230, 200, 200, 0.4)" }}>
                <p style={{ fontSize: 16, fontWeight: 600, color: "oklch(35% 0.1 20)", margin: 0 }}>
                  {point}
                </p>
              </GlassCard>
            ))}
          </div>

          <div style={{ textAlign: "center" }}>
            <div
              style={{
                display: "inline-block",
                padding: "12px 24px",
                background: `oklch(96% 0.03 ${ACCENT_HUE})`,
                borderRadius: 50,
                color: `oklch(35% 0.14 ${ACCENT_HUE})`,
                fontWeight: 700,
                fontSize: 18,
                boxShadow: "0 4px 16px rgba(100,150,220,0.1)",
              }}
            >
              We wanted to build something different.
            </div>
          </div>
        </div>
      </section>

      {/* 3. OUR APPROACH SECTION */}
      <section style={{ padding: "100px 40px", background: "oklch(98% 0.01 240)" }}>
        <div style={{ maxWidth: 1180, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 60 }}>
            <h2
              style={{
                fontSize: 36,
                fontWeight: 800,
                color: "oklch(20% 0.05 240)",
                marginBottom: 20,
                letterSpacing: "-0.5px",
              }}
            >
              A skill-based approach to communication
            </h2>
            <p
              style={{
                fontSize: 18,
                color: "oklch(40% 0.05 240)",
                maxWidth: 700,
                margin: "0 auto",
                lineHeight: 1.6,
              }}
            >
              Instead of treating English as one skill, LingosAI breaks communication into multiple subskills like grammar, fluency, pronunciation, confidence, and idea organization.
            </p>
          </div>

          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              justifyContent: "center",
              gap: 16,
            }}
          >
            {[
              { title: "Grammar & Structure", icon: <Layers size={20} /> },
              { title: "Vocabulary", icon: <BookOpen size={20} /> },
              { title: "Pronunciation", icon: <Mic size={20} /> },
              { title: "Fluency", icon: <Activity size={20} /> },
              { title: "Organization", icon: <Brain size={20} /> },
              { title: "Listening", icon: <Headphones size={20} /> },
              { title: "Confidence", icon: <Zap size={20} /> },
            ].map((skill, i) => (
              <GlassCard
                key={i}
                style={{
                  padding: "16px 20px",
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  minWidth: 200,
                }}
              >
                <div style={{ color: `oklch(45% 0.15 ${ACCENT_HUE})` }}>{skill.icon}</div>
                <div style={{ fontWeight: 600, fontSize: 15, color: "oklch(25% 0.05 240)" }}>{skill.title}</div>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* 4. HOW LINGOSAI HELPS */}
      <section style={{ padding: "100px 40px", background: "white" }}>
        <div style={{ maxWidth: 1000, margin: "0 auto" }}>
          <h2
            style={{
              fontSize: 36,
              fontWeight: 800,
              color: "oklch(20% 0.05 240)",
              marginBottom: 60,
              textAlign: "center",
              letterSpacing: "-0.5px",
            }}
          >
            How it works
          </h2>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
              gap: 40,
              position: "relative",
            }}
          >
            {/* Connection line for desktop */}
            <div
              style={{
                position: "absolute",
                top: 40,
                left: "15%",
                right: "15%",
                height: 2,
                background: `linear-gradient(90deg, transparent, oklch(80% 0.1 ${ACCENT_HUE}), transparent)`,
                zIndex: 0,
                display: "none", // Ideally mapped to a media query, but let's keep it simple
              }}
              className="md:block" // Assumes Tailwind is available globally for simple media query hiding if needed, else we rely on grid gap.
            />

            {[
              {
                step: "1",
                title: "Analyze",
                desc: "Understand your exact strengths and weaknesses across all subskills.",
                icon: <Brain size={32} color={`oklch(40% 0.15 ${ACCENT_HUE})`} />,
              },
              {
                step: "2",
                title: "Personalize",
                desc: "Generate smart tasks based purely on your level and interests.",
                icon: <Target size={32} color={`oklch(40% 0.15 ${ACCENT_HUE})`} />,
              },
              {
                step: "3",
                title: "Improve",
                desc: "Receive structured, granular feedback and visually track progress.",
                icon: <Wrench size={32} color={`oklch(40% 0.15 ${ACCENT_HUE})`} />,
              },
            ].map((item, i) => (
              <div key={i} style={{ textAlign: "center", position: "relative", zIndex: 1 }}>
                <div
                  style={{
                    width: 80,
                    height: 80,
                    borderRadius: "50%",
                    background: "white",
                    border: `2px solid oklch(85% 0.08 ${ACCENT_HUE})`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 32,
                    margin: "0 auto 24px auto",
                    boxShadow: "0 8px 24px rgba(100,140,210,0.12)",
                  }}
                >
                  {item.icon}
                </div>
                <h3 style={{ fontSize: 22, fontWeight: 700, marginBottom: 12, color: "oklch(20% 0.05 240)" }}>
                  {item.title}
                </h3>
                <p style={{ fontSize: 16, color: "oklch(45% 0.05 240)", lineHeight: 1.6 }}>
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 5. WHY WE BUILT THIS */}
      <section
        style={{
          padding: "100px 40px",
          background: `linear-gradient(135deg, oklch(35% 0.15 ${ACCENT_HUE}), oklch(25% 0.1 ${ACCENT_HUE}))`,
          color: "white",
          textAlign: "center",
        }}
      >
        <div style={{ maxWidth: 800, margin: "0 auto" }}>
          <h2 style={{ fontSize: 36, fontWeight: 800, marginBottom: 24, letterSpacing: "-0.5px" }}>
            Why LingosAI exists
          </h2>
          <p style={{ fontSize: 20, color: "rgba(255,255,255,0.9)", lineHeight: 1.7 }}>
            &ldquo;Many learners practice English every day but still struggle to communicate confidently. LingosAI was created to make improvement more structured, personalized, and feedback-driven.&rdquo;
          </p>
        </div>
      </section>

      {/* 6. FUTURE VISION SECTION */}
      <section style={{ padding: "100px 40px", background: "oklch(98% 0.01 240)" }}>
        <div style={{ maxWidth: 1000, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 60 }}>
            <h2
              style={{
                fontSize: 32,
                fontWeight: 800,
                color: "oklch(20% 0.05 240)",
                marginBottom: 16,
                letterSpacing: "-0.5px",
              }}
            >
              The future of AI-assisted communication learning
            </h2>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 24,
            }}
          >
            {[
              "Personalized coaching",
              "Speaking analysis",
              "Real-world communication training",
              "Adaptive learning systems",
            ].map((vision, i) => (
              <GlassCard key={i} style={{ padding: 24, display: "flex", alignItems: "center", gap: 16, height: "100%" }}>
                <div
                  style={{
                    background: `oklch(90% 0.08 ${ACCENT_HUE})`,
                    borderRadius: "50%",
                    padding: 8,
                    display: "flex",
                  }}
                >
                  <ArrowRight size={18} color={`oklch(40% 0.15 ${ACCENT_HUE})`} />
                </div>
                <div style={{ fontWeight: 600, fontSize: 16, color: "oklch(30% 0.05 240)" }}>{vision}</div>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* 7. FINAL CTA SECTION */}
      <section style={{ padding: "120px 40px", background: "white", textAlign: "center" }}>
        <div style={{ maxWidth: 800, margin: "0 auto" }}>
          <h2
            style={{
              fontSize: "clamp(36px, 4vw, 48px)",
              fontWeight: 800,
              color: "oklch(15% 0.09 245)",
              marginBottom: 40,
              letterSpacing: "-1px",
            }}
          >
            Start improving with smarter practice
          </h2>
          <div style={{ display: "flex", justifyContent: "center", gap: 16, flexWrap: "wrap" }}>
            <button
              onClick={() => router.push(ctaHref)}
              style={{
                padding: "16px 36px",
                borderRadius: 50,
                border: "none",
                background: `oklch(20% 0.09 ${ACCENT_HUE})`,
                color: "white",
                fontSize: 16,
                fontWeight: 700,
                cursor: "pointer",
                transition: "transform 0.2s, box-shadow 0.2s",
                boxShadow: "0 8px 24px rgba(20,50,120,0.2)",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.boxShadow = "0 12px 32px rgba(20,50,120,0.3)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 8px 24px rgba(20,50,120,0.2)";
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                {isAuthed ? ctaLabel : "Try Now"} <ArrowRight size={18} />
              </div>
            </button>
            <button
              onClick={() => router.push("/features")}
              style={{
                padding: "16px 36px",
                borderRadius: 50,
                border: "2px solid rgba(100,140,220,0.3)",
                background: "transparent",
                color: `oklch(25% 0.1 ${ACCENT_HUE})`,
                fontSize: 16,
                fontWeight: 700,
                cursor: "pointer",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(100,140,220,0.05)";
                e.currentTarget.style.borderColor = `rgba(100,140,220,0.5)`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "transparent";
                e.currentTarget.style.borderColor = `rgba(100,140,220,0.3)`;
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                Explore Features <ArrowRight size={18} />
              </div>
            </button>
          </div>
        </div>
      </section>
      <LandingFooter />
    </main>
  );
}
