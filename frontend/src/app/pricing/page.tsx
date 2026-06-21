"use client";

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Check, X } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/lib/auth-api";
import { LandingNavbar } from "@/components/layout/LandingNavbar";
import { LandingFooter } from "@/components/layout/LandingFooter";

const ACCENT_HUE = 240;
const PLANS = {
  "beginner-24w": { name: "24-Week Intensive Program", price: 999 },
  "beginner-48w": { name: "48-Week Complete Program", price: 1999 },
} as const;

type PlanId = keyof typeof PLANS;

// Reusable UI components
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

// ── NAV REPLACED WITH SHARED COMPONENT ───────────────────────────────────────

export default function PricingPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  // Users with running access don't belong on pricing. Keyed on
  // access_state, NOT preference: a plan-selected-but-no-trial user has a
  // preference row already and must still reach this page.
  const { data: me } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isAuthenticated,
  });
  useEffect(() => {
    if (me && (me.access_state === "trial" || me.access_state === "active")) {
      router.replace("/dashboard");
    }
  }, [me, router]);

  // The Trial-vs-Pay-Now fork now lives on /choose-start. Pricing just picks a
  // plan and routes there (authenticated) or to register (anonymous).
  const handleBuyNow = (planId: PlanId) => {
    if (!isAuthenticated) {
      router.push("/register");
    } else {
      router.push(`/choose-start?plan=${encodeURIComponent(planId)}`);
    }
  };

  const ctaLabel = isAuthenticated ? "Choose how to start" : "Get started";

  return (
    <main
      style={{
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        minHeight: "100svh",
        background: `radial-gradient(circle at top right, oklch(90% 0.05 ${ACCENT_HUE}) 0%, oklch(95% 0.02 ${
          ACCENT_HUE + 10
        }) 40%, #ffffff 100%)`,
        paddingTop: 100,
        paddingBottom: 0,
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />
      <LandingNavbar showCTA={false} />
      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "0 24px" }}>
        {/* Hero Section */}
        <section style={{ textAlign: "center", marginBottom: 60 }}>
          {isAuthenticated && (
            <button
              onClick={() => router.push("/dashboard")}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                fontSize: 14,
                fontWeight: 600,
                color: `oklch(40% 0.14 ${ACCENT_HUE})`,
                background: `oklch(95% 0.05 ${ACCENT_HUE})`,
                border: "none",
                borderRadius: 50,
                padding: "8px 16px",
                cursor: "pointer",
                marginBottom: 24,
              }}
            >
              ← Back to dashboard
            </button>
          )}
          <h1
            style={{
              fontSize: "clamp(32px, 4vw, 48px)",
              fontWeight: 800,
              color: "oklch(20% 0.09 245)",
              letterSpacing: "-1px",
              marginBottom: 16,
            }}
          >
            Choose your learning path
          </h1>
          <p
            style={{
              fontSize: 18,
              color: "oklch(45% 0.08 240)",
              maxWidth: 600,
              margin: "0 auto",
              lineHeight: 1.6,
            }}
          >
            Structured AI learning designed to fit your goals. Master English
            communication with consistent daily practice.
          </p>
        </section>

        {/* 2. Pricing Cards */}
        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
            gap: 32,
            marginBottom: 80,
          }}
        >
          {/* Card 1 */}
          <GlassCard
            style={{
              padding: 40,
              display: "flex",
              flexDirection: "column",
              position: "relative",
            }}
          >
            <div
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: `oklch(40% 0.14 ${ACCENT_HUE})`,
                background: `oklch(95% 0.05 ${ACCENT_HUE})`,
                padding: "6px 14px",
                borderRadius: 50,
                display: "inline-block",
                marginBottom: 20,
                alignSelf: "flex-start",
              }}
            >
              For Intermediate Learners
            </div>
            <h2
              style={{
                fontSize: 24,
                fontWeight: 700,
                color: "oklch(20% 0.09 245)",
                marginBottom: 12,
              }}
            >
              24-Week Intensive Program
            </h2>
            <p
              style={{
                fontSize: 15,
                color: "oklch(40% 0.07 240)",
                lineHeight: 1.6,
                marginBottom: 32,
                minHeight: 48,
              }}
            >
              Designed to take you from intermediate to advanced communication
            </p>

            <div style={{ marginBottom: 32 }}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
                <span
                  style={{
                    fontSize: 20,
                    color: "oklch(60% 0.05 240)",
                    textDecoration: "line-through",
                  }}
                >
                  ₹1200
                </span>
                <span
                  style={{
                    fontSize: 42,
                    fontWeight: 800,
                    color: "oklch(15% 0.09 245)",
                    letterSpacing: "-1px",
                  }}
                >
                  ₹999
                </span>
              </div>
              <div style={{ fontSize: 13, color: "oklch(50% 0.07 240)" }}>
                Billed once
              </div>
            </div>

            <ul style={{ listStyle: "none", padding: 0, margin: "0 0 32px 0", flex: 1 }}>
              {[
                "Full access to AI diagnosis",
                "Daily personalized tasks",
                "Grammar & vocabulary tracking",
                "Weekly progress reports",
              ].map((feature, i) => (
                <li
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    marginBottom: 16,
                    fontSize: 15,
                    color: "oklch(30% 0.08 240)",
                  }}
                >
                  <div
                    style={{
                      background: `oklch(90% 0.06 ${ACCENT_HUE})`,
                      borderRadius: "50%",
                      padding: 4,
                      display: "flex",
                    }}
                  >
                    <Check size={14} color={`oklch(35% 0.14 ${ACCENT_HUE})`} />
                  </div>
                  {feature}
                </li>
              ))}
            </ul>

            <button
              onClick={() => handleBuyNow("beginner-24w")}
              style={{
                width: "100%",
                padding: "16px 0",
                borderRadius: 12,
                border: `1px solid rgba(100,140,220,0.3)`,
                background: "white",
                color: `oklch(25% 0.1 ${ACCENT_HUE})`,
                fontSize: 16,
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.2s",
                boxShadow: "0 2px 8px rgba(30,60,120,0.05)",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = `oklch(97% 0.02 ${ACCENT_HUE})`;
                e.currentTarget.style.borderColor = `rgba(100,140,220,0.5)`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "white";
                e.currentTarget.style.borderColor = `rgba(100,140,220,0.3)`;
              }}
            >
              {ctaLabel}
            </button>
            <p style={{ textAlign: "center", fontSize: 13, color: "oklch(50% 0.05 240)", marginTop: 12 }}>
              7-day free trial without credit card
            </p>
          </GlassCard>

          {/* Card 2 (Highlighted) */}
          <GlassCard
            style={{
              padding: 40,
              display: "flex",
              flexDirection: "column",
              position: "relative",
              border: `2px solid oklch(50% 0.18 ${ACCENT_HUE})`,
              boxShadow: "0 12px 48px rgba(50,100,220,0.15)",
              transform: "scale(1.02)",
            }}
          >
            <div
              style={{
                position: "absolute",
                top: -14,
                left: "50%",
                transform: "translateX(-50%)",
                background: `linear-gradient(135deg, oklch(50% 0.18 ${ACCENT_HUE}), oklch(40% 0.2 ${ACCENT_HUE}))`,
                color: "white",
                padding: "6px 16px",
                borderRadius: 50,
                fontSize: 12,
                fontWeight: 700,
                letterSpacing: 0.5,
                boxShadow: "0 4px 12px rgba(50,100,220,0.3)",
                whiteSpace: "nowrap",
              }}
            >
              MOST POPULAR
            </div>

            <div
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: `oklch(40% 0.14 ${ACCENT_HUE})`,
                background: `oklch(95% 0.05 ${ACCENT_HUE})`,
                padding: "6px 14px",
                borderRadius: 50,
                display: "inline-block",
                marginBottom: 20,
                alignSelf: "flex-start",
              }}
            >
              Best for Beginners
            </div>
            <h2
              style={{
                fontSize: 24,
                fontWeight: 700,
                color: "oklch(20% 0.09 245)",
                marginBottom: 12,
              }}
            >
              48-Week Complete Program
            </h2>
            <p
              style={{
                fontSize: 15,
                color: "oklch(40% 0.07 240)",
                lineHeight: 1.6,
                marginBottom: 32,
                minHeight: 48,
              }}
            >
              Start from basics and build strong English skills step by step
            </p>

            <div style={{ marginBottom: 32 }}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
                <span
                  style={{
                    fontSize: 20,
                    color: "oklch(60% 0.05 240)",
                    textDecoration: "line-through",
                  }}
                >
                  ₹2400
                </span>
                <span
                  style={{
                    fontSize: 42,
                    fontWeight: 800,
                    color: "oklch(15% 0.09 245)",
                    letterSpacing: "-1px",
                  }}
                >
                  ₹1999
                </span>
              </div>
              <div style={{ fontSize: 13, color: "oklch(50% 0.07 240)" }}>
                Billed once
              </div>
            </div>

            <ul style={{ listStyle: "none", padding: 0, margin: "0 0 32px 0", flex: 1 }}>
              {[
                "Everything in 24-Week Program",
                "Advanced pronunciation feedback",
                "Real-time speaking analysis",
                "Priority coach access",
              ].map((feature, i) => (
                <li
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    marginBottom: 16,
                    fontSize: 15,
                    color: "oklch(30% 0.08 240)",
                  }}
                >
                  <div
                    style={{
                      background: `linear-gradient(135deg, oklch(50% 0.18 ${ACCENT_HUE}), oklch(40% 0.2 ${ACCENT_HUE}))`,
                      borderRadius: "50%",
                      padding: 4,
                      display: "flex",
                    }}
                  >
                    <Check size={14} color="white" />
                  </div>
                  <span style={i === 0 ? { fontWeight: 600 } : {}}>{feature}</span>
                </li>
              ))}
            </ul>

            <button
              onClick={() => handleBuyNow("beginner-48w")}
              style={{
                width: "100%",
                padding: "16px 0",
                borderRadius: 12,
                border: "none",
                background: `linear-gradient(135deg, oklch(45% 0.18 ${ACCENT_HUE}), oklch(35% 0.2 ${ACCENT_HUE}))`,
                color: "white",
                fontSize: 16,
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.2s",
                boxShadow: "0 6px 20px rgba(50,100,220,0.3)",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.boxShadow = "0 8px 24px rgba(50,100,220,0.4)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 6px 20px rgba(50,100,220,0.3)";
              }}
            >
              {ctaLabel}
            </button>
            <p style={{ textAlign: "center", fontSize: 13, color: "oklch(50% 0.05 240)", marginTop: 12 }}>
              7-day free trial without credit card
            </p>
          </GlassCard>
        </section>

        {/* 3. Comparison Table */}
        <section style={{ marginBottom: 80 }}>
          <h3
            style={{
              fontSize: 28,
              fontWeight: 700,
              color: "oklch(20% 0.09 245)",
              textAlign: "center",
              marginBottom: 32,
            }}
          >
            Compare Plans
          </h3>
          <GlassCard style={{ padding: "0 24px", overflow: "hidden" }}>
            <div className="mkt-table-scroll">
            <table style={{ width: "100%", minWidth: 420, borderCollapse: "collapse", textAlign: "left" }}>
              <thead>
                <tr>
                  <th style={{ padding: "24px 16px", borderBottom: "1px solid rgba(0,0,0,0.05)", width: "50%", color: "oklch(30% 0.08 240)", fontWeight: 600 }}>Features</th>
                  <th style={{ padding: "24px 16px", borderBottom: "1px solid rgba(0,0,0,0.05)", fontWeight: 600, color: "oklch(30% 0.08 240)", textAlign: "center" }}>24-Week</th>
                  <th style={{ padding: "24px 16px", borderBottom: "1px solid rgba(0,0,0,0.05)", fontWeight: 600, color: `oklch(40% 0.18 ${ACCENT_HUE})`, textAlign: "center" }}>48-Week</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { name: "AI Diagnosis", basic: true, pro: true },
                  { name: "Daily Personalized Tasks", basic: true, pro: true },
                  { name: "Weekly Progress Reports", basic: true, pro: true },
                  { name: "Advanced Pronunciation Feedback", basic: false, pro: true },
                  { name: "Real-time Speaking Analysis", basic: false, pro: true },
                  { name: "Priority Coach Access", basic: false, pro: true },
                ].map((row, i) => (
                  <tr key={i}>
                    <td style={{ padding: "20px 16px", borderBottom: "1px solid rgba(0,0,0,0.05)", color: "oklch(30% 0.08 240)", fontSize: 15 }}>{row.name}</td>
                    <td style={{ padding: "20px 16px", borderBottom: "1px solid rgba(0,0,0,0.05)", textAlign: "center" }}>
                      {row.basic ? <Check size={20} color="oklch(50% 0.1 145)" style={{ margin: "0 auto" }} /> : <X size={20} color="oklch(70% 0.05 240)" style={{ margin: "0 auto" }} />}
                    </td>
                    <td style={{ padding: "20px 16px", borderBottom: "1px solid rgba(0,0,0,0.05)", textAlign: "center" }}>
                      {row.pro ? <Check size={20} color={`oklch(45% 0.18 ${ACCENT_HUE})`} style={{ margin: "0 auto" }} /> : <X size={20} color="oklch(70% 0.05 240)" style={{ margin: "0 auto" }} />}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </GlassCard>
        </section>

        {/* 4. Value Section */}
        <section style={{ textAlign: "center", marginBottom: 80, padding: "0 20px" }}>
          <h3
            style={{
              fontSize: 28,
              fontWeight: 700,
              color: "oklch(20% 0.09 245)",
              marginBottom: 16,
            }}
          >
            Why longer practice matters
          </h3>
          <p
            style={{
              fontSize: 18,
              color: "oklch(45% 0.08 240)",
              maxWidth: 700,
              margin: "0 auto",
              lineHeight: 1.7,
            }}
          >
            Language acquisition isn&apos;t about cramming; it&apos;s about consistency. A longer learning duration ensures that vocabulary and grammar rules move from short-term memory to long-term fluency. Committing to a 48-week journey builds the enduring habits needed for true mastery.
          </p>
        </section>

        {/* 5. Final CTA */}
        <section
          style={{
            background: `linear-gradient(135deg, oklch(25% 0.1 ${ACCENT_HUE}), oklch(15% 0.1 ${ACCENT_HUE}))`,
            borderRadius: 24,
            padding: "60px 40px",
            textAlign: "center",
            color: "white",
            boxShadow: "0 20px 40px rgba(20,40,80,0.2)",
            marginBottom: 80,
          }}
        >
          <h2 style={{ fontSize: 36, fontWeight: 800, marginBottom: 20, letterSpacing: "-0.5px" }}>
            Start your learning journey today
          </h2>
          <p style={{ fontSize: 18, color: "rgba(255,255,255,0.8)", marginBottom: 32, maxWidth: 500, margin: "0 auto 32px auto" }}>
            Join thousands of learners who have transformed their English communication skills with LingosAI.
          </p>
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            style={{
              padding: "16px 36px",
              borderRadius: 50,
              border: "none",
              background: "white",
              color: `oklch(20% 0.1 ${ACCENT_HUE})`,
              fontSize: 16,
              fontWeight: 700,
              cursor: "pointer",
              transition: "transform 0.2s, box-shadow 0.2s",
              boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 12px 32px rgba(0,0,0,0.2)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,0,0,0.15)";
            }}
          >
            Choose Your Plan
          </button>
        </section>
      </div>
      <LandingFooter />
    </main>
  );
}
