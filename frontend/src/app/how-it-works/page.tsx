"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Brain,
  Target,
  Wrench,
  Repeat,
  BarChart,
  Layers,
  Activity,
  CheckCircle,
  XCircle,
  PenTool,
  Mic,
  Headphones,
  BookOpen,
  Calendar,
  MessageSquare,
  Zap,
  ArrowRight,
} from "lucide-react";
import { LandingNavbar } from "@/components/layout/LandingNavbar";
import { LandingFooter } from "@/components/layout/LandingFooter";

const ACCENT_HUE = 240;
const CTA_TEXT = "Try Free Diagnosis";

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

// ── Skill radar ─────────────────────────────────────────────────────────────
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
    <svg width="280" height="220" viewBox="-50 -20 280 220" style={{ overflow: "visible" }}>
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

// ── NAV REPLACED WITH SHARED COMPONENT ───────────────────────────────────────

export default function HowItWorksPage() {
  const router = useRouter();

  const handleCTAClick = () => {
    router.push("/diagnosis");
  };

  return (
    <main
      style={{
        minHeight: "100svh",
        background: `oklch(97% 0.02 ${ACCENT_HUE})`,
        fontFamily: "'Inter', 'Plus Jakarta Sans', sans-serif",
        color: "oklch(20% 0.05 240)",
        overflowX: "hidden",
      }}
    >
      <LandingNavbar onCTAClick={handleCTAClick} showCTA={false} />

      {/* SECTION 1: Why Most People Fail (Hero-ish) */}
      <section
        style={{
          position: "relative",
          padding: "160px 40px 100px",
          overflow: "hidden",
        }}
      >
        <DotGrid opacity={0.12} />
        <div
          style={{
            position: "absolute",
            top: "-10%",
            left: "-10%",
            width: "60%",
            height: "60%",
            background: `radial-gradient(circle, oklch(90% 0.08 ${ACCENT_HUE}) 0%, transparent 70%)`,
            opacity: 0.6,
            pointerEvents: "none",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: "0%",
            right: "-5%",
            width: "50%",
            height: "50%",
            background: `radial-gradient(circle, oklch(92% 0.06 ${ACCENT_HUE - 20
              }) 0%, transparent 70%)`,
            opacity: 0.6,
            pointerEvents: "none",
          }}
        />

        <div
          style={{
            maxWidth: 1180,
            margin: "0 auto",
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 60,
            alignItems: "center",
            position: "relative",
            zIndex: 10,
          }}
        >
          <div>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                background: "rgba(255,255,255,0.7)",
                backdropFilter: "blur(12px)",
                border: "1px solid rgba(255,255,255,0.9)",
                borderRadius: 50,
                padding: "6px 16px",
                marginBottom: 24,
                fontSize: 13,
                fontWeight: 600,
                color: `oklch(45% 0.15 20)`, // Red-ish accent for pain point
              }}
            >
              <XCircle size={14} color="currentColor" />
              The Old Way
            </div>
            <h1
              style={{
                fontSize: "clamp(36px, 4vw, 52px)",
                fontWeight: 800,
                lineHeight: 1.1,
                letterSpacing: "-1.2px",
                color: "oklch(15% 0.05 240)",
                marginBottom: 24,
              }}
            >
              Why learning English feels frustrating
            </h1>

            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {[
                "You don't know your exact weaknesses",
                "You practice randomly without direction",
                "No clear feedback on what to fix",
                "No structured plan for improvement",
              ].map((text, i) => (
                <div key={i} style={{ display: "flex", gap: 12, alignItems: "center" }}>
                  <div
                    style={{
                      width: 24,
                      height: 24,
                      borderRadius: "50%",
                      background: "rgba(230, 80, 80, 0.1)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "oklch(55% 0.18 20)",
                    }}
                  >
                    <XCircle size={14} />
                  </div>
                  <span style={{ fontSize: 16, color: "oklch(35% 0.05 240)", fontWeight: 500 }}>
                    {text}
                  </span>
                </div>
              ))}
            </div>

            <div
              style={{
                marginTop: 36,
                padding: "20px 24px",
                background: `linear-gradient(135deg, oklch(50% 0.18 ${ACCENT_HUE}) 0%, oklch(40% 0.16 ${ACCENT_HUE - 10}) 100%)`,
                borderRadius: 16,
                color: "white",
                boxShadow: "0 12px 32px rgba(40,80,200,0.2)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <CheckCircle size={24} color="rgba(255,255,255,0.9)" />
                <span style={{ fontSize: 18, fontWeight: 600, letterSpacing: "-0.2px" }}>
                  We fix this with a structured, skill-based system.
                </span>
              </div>
            </div>
          </div>

          <div style={{ position: "relative" }}>
            <div style={{
              padding: 40,
              display: "flex",
              flexDirection: "column",
              gap: 0,
              border: "1px solid rgba(255, 255, 255, 0.8)",
              borderRadius: 32,
              background: "linear-gradient(145deg, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0.3) 100%)",
              backdropFilter: "blur(20px)",
              boxShadow: "0 20px 40px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255,255,255,0.8)",
              position: "relative",
              overflow: "hidden"
            }}>
              {/* Subtle background graph paper pattern */}
              <div style={{
                position: "absolute",
                top: 0, left: 0, right: 0, bottom: 0,
                backgroundImage: "linear-gradient(rgba(0,0,0,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,0,0,0.03) 1px, transparent 1px)",
                backgroundSize: "20px 20px",
                pointerEvents: "none",
                maskImage: "linear-gradient(to bottom, transparent, black 10%, black 90%, transparent)",
                WebkitMaskImage: "linear-gradient(to bottom, transparent, black 10%, black 90%, transparent)"
              }} />

              {/* Random Practice Section */}
              <div style={{ position: "relative", zIndex: 1, paddingBottom: 30 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                  <div style={{ fontSize: 15, fontWeight: 700, color: "oklch(40% 0.1 20)", display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ width: 8, height: 8, borderRadius: "50%", background: "oklch(60% 0.2 20)" }} />
                    Random Practice
                  </div>
                  <div style={{ fontSize: 13, color: "oklch(50% 0.1 20)", background: "rgba(255,100,100,0.1)", padding: "4px 10px", borderRadius: 12, fontWeight: 600 }}>
                    Months of effort
                  </div>
                </div>
                
                <div style={{ height: 100, width: "100%", position: "relative" }}>
                  <svg width="100%" height="100%" viewBox="0 0 400 100" preserveAspectRatio="none" style={{ overflow: "visible" }}>
                    <path d="M 10 50 C 60 10, 100 90, 160 30 C 220 -20, 260 120, 320 60 C 360 20, 380 70, 390 50" fill="none" stroke="oklch(60% 0.2 20)" strokeWidth="2.5" strokeDasharray="6 6" strokeLinecap="round" opacity="0.6" />
                    <path d="M 20 80 C 80 120, 140 0, 200 60 C 260 120, 300 10, 380 80" fill="none" stroke="oklch(60% 0.2 20)" strokeWidth="1.5" strokeDasharray="4 8" strokeLinecap="round" opacity="0.3" />
                    {/* Glowing nodes */}
                    <circle cx="160" cy="30" r="5" fill="oklch(55% 0.2 20)" />
                    <circle cx="160" cy="30" r="12" fill="oklch(55% 0.2 20)" opacity="0.2" />
                    <circle cx="320" cy="60" r="5" fill="oklch(55% 0.2 20)" />
                    <circle cx="320" cy="60" r="12" fill="oklch(55% 0.2 20)" opacity="0.2" />
                  </svg>
                </div>
              </div>

              {/* Refined Divider */}
              <div style={{
                height: 1,
                width: "100%",
                background: "linear-gradient(90deg, transparent, rgba(0,0,0,0.08) 20%, rgba(0,0,0,0.08) 80%, transparent)",
                margin: "10px 0 40px 0"
              }} />

              {/* Structured Improvement Section */}
              <div style={{ position: "relative", zIndex: 1 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                  <div style={{ fontSize: 15, fontWeight: 700, color: `oklch(35% 0.15 ${ACCENT_HUE})`, display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ width: 8, height: 8, borderRadius: "50%", background: `oklch(50% 0.18 ${ACCENT_HUE})` }} />
                    Structured Improvement
                  </div>
                  <div style={{ fontSize: 13, color: `oklch(40% 0.15 ${ACCENT_HUE})`, background: `oklch(95% 0.05 ${ACCENT_HUE})`, padding: "4px 10px", borderRadius: 12, fontWeight: 600 }}>
                    Clear progression
                  </div>
                </div>
                
                <div style={{ height: 120, width: "100%", position: "relative" }}>
                  <svg width="100%" height="100%" viewBox="0 0 400 120" preserveAspectRatio="none" style={{ overflow: "visible" }}>
                    <defs>
                      <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={`oklch(50% 0.18 ${ACCENT_HUE})`} stopOpacity="0.3" />
                        <stop offset="100%" stopColor={`oklch(50% 0.18 ${ACCENT_HUE})`} stopOpacity="0" />
                      </linearGradient>
                    </defs>
                    <polygon points="10,110 100,85 200,60 300,35 390,10 390,120 10,120" fill="url(#areaGradient)" />
                    <path d="M 10 110 L 100 85 L 200 60 L 300 35 L 390 10" fill="none" stroke={`oklch(50% 0.18 ${ACCENT_HUE})`} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
                    
                    {/* Glowing nodes */}
                    <g transform="translate(100, 85)">
                      <circle r="6" fill="white" stroke={`oklch(50% 0.18 ${ACCENT_HUE})`} strokeWidth="3" />
                      <circle r="14" fill={`oklch(50% 0.18 ${ACCENT_HUE})`} opacity="0.15" />
                    </g>
                    <g transform="translate(200, 60)">
                      <circle r="6" fill="white" stroke={`oklch(50% 0.18 ${ACCENT_HUE})`} strokeWidth="3" />
                      <circle r="14" fill={`oklch(50% 0.18 ${ACCENT_HUE})`} opacity="0.15" />
                    </g>
                    <g transform="translate(300, 35)">
                      <circle r="6" fill="white" stroke={`oklch(50% 0.18 ${ACCENT_HUE})`} strokeWidth="3" />
                      <circle r="14" fill={`oklch(50% 0.18 ${ACCENT_HUE})`} opacity="0.15" />
                    </g>
                    <g transform="translate(390, 10)">
                      <circle r="8" fill={`oklch(50% 0.18 ${ACCENT_HUE})`} stroke="white" strokeWidth="2" />
                      <circle r="18" fill={`oklch(50% 0.18 ${ACCENT_HUE})`} opacity="0.25" />
                    </g>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 2: 7 Subskills */}
      <section
        style={{
          padding: "100px 40px",
          background: "white",
          borderTop: "1px solid rgba(0,0,0,0.04)",
          borderBottom: "1px solid rgba(0,0,0,0.04)",
        }}
      >
        <div style={{ maxWidth: 1180, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 60 }}>
            <h2
              style={{
                fontSize: "clamp(30px, 3.5vw, 42px)",
                fontWeight: 800,
                letterSpacing: "-1px",
                color: "oklch(15% 0.05 240)",
                marginBottom: 16,
              }}
            >
              We break English into 7 core skills
            </h2>
            <p
              style={{
                fontSize: 18,
                color: "oklch(40% 0.05 240)",
                maxWidth: 600,
                margin: "0 auto",
                lineHeight: 1.6,
              }}
            >
              Instead of treating English as one giant, confusing subject, we train each component separately.
            </p>
          </div>

          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              justifyContent: "center",
              gap: 20,
            }}
          >
            {[
              {
                title: "Grammar & Structure",
                desc: "Build correct and coherent sentences smoothly.",
                icon: <Layers size={22} />,
              },
              {
                title: "Vocabulary & Word Choice",
                desc: "Pick the right, precise words for any context.",
                icon: <BookOpen size={22} />,
              },
              {
                title: "Pronunciation & Clarity",
                desc: "Sound clear, natural, and easily understood.",
                icon: <Mic size={22} />,
              },
              {
                title: "Fluency & Spontaneity",
                desc: "Produce language in real-time under pressure.",
                icon: <Activity size={22} />,
              },
              {
                title: "Thought Organization",
                desc: "Bridge the gap between thinking and expressing.",
                icon: <Brain size={22} />,
              },
              {
                title: "Listening & Comprehension",
                desc: "Process native English at natural speeds.",
                icon: <Headphones size={22} />,
              },
              {
                title: "Tone & Confidence",
                desc: "Adjust to social contexts without anxiety.",
                icon: <Zap size={22} />,
              },
            ].map((skill, i) => (
              <GlassCard
                key={i}
                style={{
                  width: "280px",
                  padding: "24px",
                  background: "rgba(248, 250, 255, 0.7)",
                  border: "1px solid rgba(220, 230, 250, 0.8)",
                  boxShadow: "0 4px 20px rgba(0,0,0,0.02)",
                  transition: "transform 0.2s, box-shadow 0.2s",
                  cursor: "default",
                }}
                className="hover-lift"
              >
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: 12,
                    background: `oklch(94% 0.04 ${ACCENT_HUE})`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: `oklch(40% 0.16 ${ACCENT_HUE})`,
                    marginBottom: 16,
                  }}
                >
                  {skill.icon}
                </div>
                <h3
                  style={{
                    fontSize: 18,
                    fontWeight: 700,
                    marginBottom: 8,
                    color: "oklch(20% 0.05 240)",
                  }}
                >
                  {skill.title}
                </h3>
                <p style={{ fontSize: 14, color: "oklch(45% 0.05 240)", lineHeight: 1.6 }}>
                  {skill.desc}
                </p>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* SECTION 3: Activity Mapping (Alternating Pattern) */}
      <section style={{ padding: "100px 40px", position: "relative" }}>
        <div
          style={{
            maxWidth: 1180,
            margin: "0 auto",
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 80,
            alignItems: "center",
          }}
        >
          <div style={{ position: "relative" }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              {[
                { title: "Speaking", tags: ["Fluency", "Pronunciation", "Confidence"], icon: <Mic size={20} /> },
                { title: "Writing", tags: ["Grammar", "Idea Generation"], icon: <PenTool size={20} /> },
                { title: "Listening", tags: ["Comprehension", "Tone"], icon: <Headphones size={20} /> },
                { title: "Reading", tags: ["Comprehension", "Vocabulary"], icon: <BookOpen size={20} /> },
              ].map((act, i) => (
                <GlassCard key={i} style={{ padding: 20 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                    <div style={{ color: `oklch(45% 0.15 ${ACCENT_HUE})` }}>{act.icon}</div>
                    <div style={{ fontWeight: 700, fontSize: 16 }}>{act.title}</div>
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                    {act.tags.map((t, j) => (
                      <span
                        key={j}
                        style={{
                          fontSize: 11,
                          padding: "4px 8px",
                          background: `rgba(100, 150, 255, 0.1)`,
                          color: `oklch(40% 0.12 ${ACCENT_HUE})`,
                          borderRadius: 20,
                          fontWeight: 600,
                        }}
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </GlassCard>
              ))}
            </div>

            {/* Connection lines visual hint */}
            <div
              style={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
                width: 60,
                height: 60,
                borderRadius: "50%",
                background: "white",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
                zIndex: 10,
              }}
            >
              <Repeat size={24} color={`oklch(45% 0.15 ${ACCENT_HUE})`} />
            </div>
          </div>

          <div>
            <h2
              style={{
                fontSize: "clamp(30px, 3.5vw, 42px)",
                fontWeight: 800,
                letterSpacing: "-1px",
                color: "oklch(15% 0.05 240)",
                marginBottom: 20,
              }}
            >
              Every task improves multiple skills at once
            </h2>
            <p
              style={{
                fontSize: 18,
                color: "oklch(40% 0.05 240)",
                lineHeight: 1.6,
                marginBottom: 32,
              }}
            >
              We don&apos;t waste your time with single-focus drills. Our 4 core activity types are designed so that each action you take targets and strengthens multiple sub-skills simultaneously.
            </p>

            <div style={{ display: "flex", alignItems: "center", gap: 12, background: "rgba(255,255,255,0.7)", padding: "16px 20px", borderRadius: 12, border: "1px solid rgba(0,0,0,0.05)" }}>
              <div style={{ width: 40, height: 40, borderRadius: "50%", background: `oklch(94% 0.04 ${ACCENT_HUE})`, display: "flex", alignItems: "center", justifyContent: "center", color: `oklch(45% 0.15 ${ACCENT_HUE})` }}>
                <Target size={20} />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: 15, color: "oklch(20% 0.05 240)" }}>Maximum Efficiency</div>
                <div style={{ fontSize: 14, color: "oklch(45% 0.05 240)" }}>Learn faster by overlapping skill training.</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 4: Weekly Structure */}
      <section
        style={{
          padding: "100px 40px",
          background: "white",
          borderTop: "1px solid rgba(0,0,0,0.04)",
        }}
      >
        <div
          style={{
            maxWidth: 1180,
            margin: "0 auto",
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 80,
            alignItems: "center",
          }}
        >
          <div style={{ order: 2 }}>
            <h2
              style={{
                fontSize: "clamp(30px, 3.5vw, 42px)",
                fontWeight: 800,
                letterSpacing: "-1px",
                color: "oklch(15% 0.05 240)",
                marginBottom: 20,
              }}
            >
              A structured weekly learning system
            </h2>
            <p
              style={{
                fontSize: 18,
                color: "oklch(40% 0.05 240)",
                lineHeight: 1.6,
                marginBottom: 32,
              }}
            >
              Every week consists of a 7-day loop, and each day targets a specific subskill. You&apos;ll complete daily task bundles that are structured but flexible enough for your busy schedule.
            </p>

            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 16 }}>
              {[
                { label: "Continuous 7-Day Loops", icon: <Calendar size={18} /> },
                { label: "1 Focus Skill Per Day", icon: <Target size={18} /> },
                { label: "2-3 Highly Focused Daily Tasks", icon: <CheckCircle size={18} /> },
              ].map((item, i) => (
                <li key={i} style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 16, fontWeight: 500, color: "oklch(30% 0.05 240)" }}>
                  <div style={{ color: `oklch(50% 0.18 ${ACCENT_HUE})` }}>{item.icon}</div>
                  {item.label}
                </li>
              ))}
            </ul>
          </div>

          <div style={{ order: 1, position: "relative" }}>
            <GlassCard style={{ padding: 32 }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                {[
                  { day: "Day 1", focus: "Grammar & Structure", tasks: "Reading + Writing" },
                  { day: "Day 2", focus: "Fluency & Spontaneity", tasks: "Speaking + Listening", active: true },
                  { day: "Day 3", focus: "Vocabulary & Word Choice", tasks: "Reading + Speaking" },
                ].map((row, i) => (
                  <div
                    key={i}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      padding: "16px",
                      background: row.active ? `oklch(96% 0.03 ${ACCENT_HUE})` : "transparent",
                      border: row.active ? `1.5px solid oklch(85% 0.1 ${ACCENT_HUE})` : "1.5px solid transparent",
                      borderRadius: 12,
                      gap: 20,
                      transition: "all 0.2s",
                    }}
                  >
                    <div
                      style={{
                        background: row.active ? `oklch(50% 0.18 ${ACCENT_HUE})` : "rgba(0,0,0,0.05)",
                        color: row.active ? "white" : "oklch(40% 0.05 240)",
                        padding: "6px 12px",
                        borderRadius: 8,
                        fontSize: 13,
                        fontWeight: 700,
                        minWidth: "64px",
                        textAlign: "center"
                      }}
                    >
                      {row.day}
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: 15, color: "oklch(20% 0.05 240)", marginBottom: 4 }}>
                        {row.focus}
                      </div>
                      <div style={{ fontSize: 13, color: "oklch(50% 0.05 240)" }}>
                        Tasks: {row.tasks}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* SECTION 5: AI Engine */}
      <section style={{ padding: "100px 40px", position: "relative" }}>
        <DotGrid opacity={0.15} />
        <div style={{ maxWidth: 1000, margin: "0 auto", textAlign: "center" }}>
          <h2
            style={{
              fontSize: "clamp(30px, 3.5vw, 42px)",
              fontWeight: 800,
              letterSpacing: "-1px",
              color: "oklch(15% 0.05 240)",
              marginBottom: 20,
            }}
          >
            Powered by an intelligent feedback system
          </h2>
          <p
            style={{
              fontSize: 18,
              color: "oklch(40% 0.05 240)",
              lineHeight: 1.6,
              marginBottom: 60,
              maxWidth: 600,
              margin: "0 auto 60px",
            }}
          >
            Our AI engine learns from your past responses to constantly adapt the curriculum to your needs.
          </p>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 20,
              position: "relative",
            }}
          >
            {/* Flow line */}
            <div
              style={{
                position: "absolute",
                top: 0,
                bottom: 0,
                left: "50%",
                width: 2,
                background: "rgba(100,150,250,0.2)",
                transform: "translateX(-50%)",
                zIndex: 0,
              }}
            />

            {[
              {
                title: "1. Task Generator",
                desc: "Identifies your level and creates tasks based on your weaknesses and interests.",
                icon: <Brain size={24} />,
              },
              {
                title: "2. Evaluator",
                desc: "Analyzes your response, detects mistakes, and scores your performance.",
                icon: <BarChart size={24} />,
              },
              {
                title: "3. Feedback Engine",
                desc: "Uses your past mistakes and current performance to give precise, personalized feedback.",
                icon: <MessageSquare size={24} />,
              },
            ].map((step, i) => (
              <GlassCard
                key={i}
                style={{
                  position: "relative",
                  zIndex: 1,
                  margin: "0 auto",
                  maxWidth: 600,
                  width: "100%",
                  padding: 24,
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 20,
                  textAlign: "left",
                  background: "rgba(255,255,255,0.85)",
                }}
              >
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: 12,
                    background: `linear-gradient(135deg, oklch(55% 0.18 ${ACCENT_HUE}) 0%, oklch(45% 0.16 ${ACCENT_HUE}) 100%)`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "white",
                    flexShrink: 0,
                    boxShadow: "0 4px 12px rgba(40,80,200,0.2)",
                  }}
                >
                  {step.icon}
                </div>
                <div>
                  <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8, color: "oklch(20% 0.05 240)" }}>
                    {step.title}
                  </h3>
                  <p style={{ fontSize: 15, color: "oklch(45% 0.05 240)", lineHeight: 1.5 }}>
                    {step.desc}
                  </p>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* SECTION 6: Diagnostic Stats */}
      <section
        style={{
          padding: "100px 40px",
          background: "white",
          borderTop: "1px solid rgba(0,0,0,0.04)",
        }}
      >
        <div
          style={{
            maxWidth: 1180,
            margin: "0 auto",
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 80,
            alignItems: "center",
          }}
        >
          <div>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                background: "rgba(100, 150, 255, 0.1)",
                borderRadius: 50,
                padding: "6px 16px",
                marginBottom: 24,
                fontSize: 13,
                fontWeight: 600,
                color: `oklch(40% 0.15 ${ACCENT_HUE})`,
              }}
            >
              <BarChart size={14} color="currentColor" />
              Detailed Diagnostics
            </div>
            <h2
              style={{
                fontSize: "clamp(30px, 3.5vw, 42px)",
                fontWeight: 800,
                letterSpacing: "-1px",
                color: "oklch(15% 0.05 240)",
                marginBottom: 20,
              }}
            >
              Track your exact level across all subskills
            </h2>
            <p
              style={{
                fontSize: 18,
                color: "oklch(40% 0.05 240)",
                lineHeight: 1.6,
                marginBottom: 32,
              }}
            >
              Get a comprehensive breakdown of your English level (0-10) with our interactive diagnostic spider chart. See your distinct strengths, pinpoint your exact weaknesses, and visualize your progress over time.
            </p>

            <div style={{ display: "flex", gap: 12 }}>
              <div style={{ background: "rgba(245, 250, 255, 1)", padding: "16px 20px", borderRadius: 12, border: "1px solid rgba(0,0,0,0.05)", flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: 15, color: "oklch(20% 0.05 240)", marginBottom: 4 }}>Strengths</div>
                <div style={{ fontSize: 13, color: "oklch(45% 0.05 240)" }}>See what you&apos;ve mastered.</div>
              </div>
              <div style={{ background: "rgba(255, 245, 245, 1)", padding: "16px 20px", borderRadius: 12, border: "1px solid rgba(0,0,0,0.05)", flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: 15, color: "oklch(20% 0.05 240)", marginBottom: 4 }}>Weaknesses</div>
                <div style={{ fontSize: 13, color: "oklch(45% 0.05 240)" }}>Know what to fix next.</div>
              </div>
            </div>
          </div>

          <div style={{ position: "relative" }}>
            <GlassCard style={{ padding: 40, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <RadarChart
                skills={[
                  { label: "Grammar", val: 0.6 },
                  { label: "Vocabulary", val: 0.8 },
                  { label: "Pronunciation", val: 0.5 },
                  { label: "Fluency", val: 0.7 },
                  { label: "Organization", val: 0.9 },
                  { label: "Listening", val: 0.85 },
                  { label: "Tone", val: 0.75 },
                ]}
              />
            </GlassCard>
          </div>
        </div>
      </section>

      {/* SECTION 7: CTA Section */}
      <section
        style={{
          padding: "120px 40px",
          background: `oklch(18% 0.05 240)`,
          color: "white",
          textAlign: "center",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `radial-gradient(circle at center, oklch(30% 0.1 ${ACCENT_HUE}) 0%, transparent 60%)`,
            opacity: 0.5,
          }}
        />
        <div style={{ position: "relative", zIndex: 1, maxWidth: 640, margin: "0 auto" }}>
          <h2
            style={{
              fontSize: "clamp(32px, 4vw, 48px)",
              fontWeight: 800,
              letterSpacing: "-1px",
              marginBottom: 20,
            }}
          >
            This is not just practice — it&apos;s guided improvement
          </h2>
          <p
            style={{
              fontSize: 18,
              color: "rgba(255,255,255,0.8)",
              lineHeight: 1.6,
              marginBottom: 40,
            }}
          >
            Instead of guessing what to learn, you get a system that understands you, corrects you, and helps you improve step by step.
          </p>

          <div style={{ display: "flex", gap: 16, justifyContent: "center", flexWrap: "wrap" }}>
            <button
              onClick={handleCTAClick}
              style={{
                padding: "16px 36px",
                borderRadius: 50,
                border: "none",
                cursor: "pointer",
                background: "white",
                color: `oklch(20% 0.09 ${ACCENT_HUE})`,
                fontFamily: "inherit",
                fontWeight: 700,
                fontSize: 16,
                boxShadow: "0 8px 30px rgba(0,0,0,0.3)",
                transition: "transform 0.15s, box-shadow 0.15s",
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "scale(1.04)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "scale(1)";
              }}
            >
              Try Free Diagnosis <ArrowRight size={18} />
            </button>
          </div>
        </div>
      </section>
      <LandingFooter />
    </main>
  );
}
