"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/lib/auth-api";
import { subscriptionsApi } from "@/lib/subscriptions-api";
import { paymentsApi } from "@/lib/payments-api";
import { useRazorpayCheckout } from "@/hooks/useRazorpayCheckout";
import { LandingNavbar } from "@/components/layout/LandingNavbar";
import { getApiErrorMessage } from "@/lib/errors";
import { PreparingCheckout } from "./PreparingCheckout";

// Local plan map — mirrors pricing/page.tsx. Amounts are display-only here;
// the server recomputes paise from PLAN_CATALOG on create-order (Phase 3).
const PLANS = {
  "beginner-24w": {
    name: "24-Week Intensive Program",
    short: "24-Week Program",
    price: 999,
    weeks: 24,
  },
  "beginner-48w": {
    name: "48-Week Complete Program",
    short: "48-Week Program",
    price: 1999,
    weeks: 48,
  },
} as const;

type PlanId = keyof typeof PLANS;
const DEFAULT_PLAN: PlanId = "beginner-48w";
const isPlanId = (v: string | null): v is PlanId => v != null && v in PLANS;

// ── palette (hybrid: mock body accents over the shared LandingNavbar) ────────
const PRIMARY = "#0070C4";
const PRIMARY_DEEP = "#00599e";
const PRIMARY_SOFT = "#d6e8f7";
const GREEN = "oklch(56% 0.15 155)";
const GREEN_DEEP = "oklch(46% 0.15 155)";
const GREEN_SOFT = "oklch(95% 0.05 155)";
const NAVY = "oklch(20% 0.09 245)";
const NAVY_SOFT = "oklch(28% 0.08 245)";
const INK_MUTED = "oklch(45% 0.07 240)";
const INK_FAINT = "oklch(58% 0.05 240)";
const LINE = "oklch(86% 0.025 240)";

const inr = (n: number) => "₹" + n.toLocaleString("en-IN");

// ── icons ────────────────────────────────────────────────────────────────────
const Check = (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
    <path d="M5 13l4 4L19 7" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);
const Arrow = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
    <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);
const Lock = (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
    <rect x="5" y="11" width="14" height="9" rx="2" stroke="currentColor" strokeWidth="2" />
    <path d="M8 11V8a4 4 0 018 0v3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  </svg>
);
const Spark = (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
    <path d="M12 3v6M12 15v6M3 12h6M15 12h6" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
  </svg>
);
const Back = (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
    <path d="M19 12H5M11 18l-6-6 6-6" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

// ── stepper (Plan → Checkout → Confirm) ───────────────────────────────────────
function Stepper({ step }: { step: number }) {
  const steps = ["Plan", "Checkout", "Confirm"];
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", margin: "8px auto 4px" }}>
      {steps.map((s, i) => {
        const active = step === i + 1;
        const done = step > i + 1;
        return (
          <div key={s} style={{ display: "flex", alignItems: "center" }}>
            {i > 0 && (
              <span style={{ width: 38, height: 2, background: done || active ? GREEN : LINE, margin: "0 10px", borderRadius: 2 }} />
            )}
            <span style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12.5, fontWeight: 700, color: active ? NAVY : INK_FAINT }}>
              <span
                style={{
                  width: 24,
                  height: 24,
                  borderRadius: "50%",
                  display: "grid",
                  placeItems: "center",
                  fontSize: 12,
                  background: done ? GREEN : active ? PRIMARY : "white",
                  borderWidth: 1.5,
                  borderStyle: "solid",
                  borderColor: done ? GREEN : active ? PRIMARY : LINE,
                  color: done || active ? "white" : INK_FAINT,
                }}
              >
                {done ? Check : i + 1}
              </span>
              {s}
            </span>
          </div>
        );
      })}
    </div>
  );
}

// ── feature lists ──────────────────────────────────────────────────────────────
const TRIAL_FEATURES = ["No card required", "7-day free trial", "Cancel anytime", "Instant access to everything"];
const PAY_FEATURES = [
  "Secure Razorpay payment",
  "Instant subscription activation",
  "No trial period — full access now",
  "One-time payment, no renewals",
];

function FeatureList({ items, tone }: { items: readonly string[]; tone: "green" | "blue" }) {
  return (
    <ul style={{ listStyle: "none", margin: "14px 0 0", padding: 0, display: "flex", flexDirection: "column", gap: 9, flex: 1 }}>
      {items.map((f) => (
        <li key={f} style={{ display: "flex", alignItems: "center", gap: 11, fontSize: 14.5, fontWeight: 500, color: NAVY_SOFT }}>
          <span
            style={{
              flex: "none",
              width: 22,
              height: 22,
              borderRadius: "50%",
              display: "grid",
              placeItems: "center",
              background: tone === "green" ? GREEN_SOFT : PRIMARY_SOFT,
              color: tone === "green" ? GREEN_DEEP : PRIMARY_DEEP,
            }}
          >
            {Check}
          </span>
          {f}
        </li>
      ))}
    </ul>
  );
}

function ChooseStartInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuthStore();

  const [plan, setPlan] = useState<PlanId>(() => {
    const q = searchParams.get("plan");
    return isPlanId(q) ? q : DEFAULT_PLAN;
  });
  const [phase, setPhase] = useState<"choose" | "preparing-trial" | "preparing-pay">("choose");
  const [error, setError] = useState<string | null>(null);
  // Set true the instant a Pay-Now verifies, BEFORE we refetch `me`. The guard
  // effect below would otherwise see the freshly-`active` `me` and clobber the
  // /payment/success navigation with a /dashboard bounce.
  const completedPayRef = useRef(false);

  // Unauthenticated users can't enrol — bounce to register.
  useEffect(() => {
    if (!isAuthenticated) router.replace("/register");
  }, [isAuthenticated, router]);

  const { data: me } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isAuthenticated,
  });

  // Trial users land here to UPGRADE (pay to convert their trial to a paid
  // plan), routed from /pricing with ?upgrade=1. Paid (`active`) users have
  // nothing to do here and are bounced — except the user who is completing a
  // payment on this very page (completedPayRef), who is being routed to
  // /payment/success and must not be bounced to /dashboard.
  const isUpgrade = me?.access_state === "trial" || searchParams.get("upgrade") === "1";
  useEffect(() => {
    if (completedPayRef.current) return;
    if (me && me.access_state === "active") {
      router.replace("/dashboard");
    }
  }, [me, router]);

  // Only fresh `verified` users may start a trial (one trial per user). Trial
  // users upgrading see Pay-Now only — the free-trial option is disabled.
  const trialEligible = me?.access_state === "verified";

  const { openCheckout } = useRazorpayCheckout();

  const startTrialMutation = useMutation({
    mutationFn: async (planId: PlanId) => {
      await subscriptionsApi.selectPlan(planId);
      return subscriptionsApi.startTrial();
    },
  });

  const createOrderMutation = useMutation({ mutationFn: paymentsApi.createOrder });
  const verifyMutation = useMutation({ mutationFn: paymentsApi.verify });

  const handleStartTrial = async () => {
    setError(null);
    setPhase("preparing-trial");
    try {
      await startTrialMutation.mutateAsync(plan);
      await queryClient.invalidateQueries({ queryKey: ["me"] });
      router.replace("/dashboard?trial=started");
    } catch (err) {
      setError(getApiErrorMessage(err));
      setPhase("choose");
    }
  };

  // Pay-Now: create the order (server recomputes paise from PLAN_CATALOG), open
  // the Razorpay modal, verify server-side, then route to the proof page.
  // Checkout is opened on explicit choice, not gated on access_state — `verified`,
  // `expired`, and `cancelled` users all pass the backend's `require_verified` guard.
  const handlePayNow = async () => {
    setError(null);
    setPhase("preparing-pay");
    try {
      const order = await createOrderMutation.mutateAsync(plan);
      await openCheckout({
        order,
        user: me ? { name: me.name, email: me.email } : undefined,
        onSuccess: async (payload) => {
          try {
            await verifyMutation.mutateAsync(payload);
            // Claim the in-flight payment, then navigate to the proof page
            // FIRST. Refresh `me` only afterwards so the now-`active` state
            // can't trip the guard effect into a /dashboard bounce.
            completedPayRef.current = true;
            router.replace(
              `/payment/success?order_id=${encodeURIComponent(payload.razorpay_order_id)}`,
            );
            await queryClient.invalidateQueries({ queryKey: ["me"] });
          } catch (err) {
            setError(getApiErrorMessage(err));
            setPhase("choose");
          }
        },
        // Modal dismissed, payment.failed, or checkout.js load failure — nothing charged.
        onFailure: (message) => {
          setError(message);
          setPhase("choose");
        },
      });
    } catch (err) {
      setError(getApiErrorMessage(err));
      setPhase("choose");
    }
  };

  if (phase !== "choose") {
    return (
      <>
        <PreparingCheckout mode={phase === "preparing-trial" ? "trial" : "pay"} />
        {phase === "preparing-pay" && (
          <div style={{ textAlign: "center", paddingBottom: 40 }}>
            <button
              onClick={() => setPhase("choose")}
              style={{ ...backlinkStyle, background: "none", border: "none", cursor: "pointer" }}
            >
              {Back} Cancel
            </button>
          </div>
        )}
      </>
    );
  }

  const p = PLANS[plan];

  return (
    <div style={{ maxWidth: 1080, margin: "0 auto", padding: "14px 28px 70px" }}>
      <Stepper step={1} />
      <h1 style={{ fontSize: 38, fontWeight: 800, letterSpacing: "-0.03em", color: NAVY, lineHeight: 1.05, textAlign: "center", marginTop: 18 }}>
        {isUpgrade ? "Complete your upgrade" : "Choose how you want to start"}
      </h1>
      <p style={{ fontSize: 16, color: INK_MUTED, textAlign: "center", maxWidth: 560, margin: "12px auto 0", lineHeight: 1.5 }}>
        {isUpgrade
          ? "Upgrade from your free trial with a secure one-time payment. Your progress carries over."
          : trialEligible
            ? "Try LingosAI free for 7 days, or unlock everything instantly. You can switch or cancel anytime."
            : "Unlock your full program instantly with a secure one-time payment."}
      </p>

      {/* plan switch — hidden during upgrade: the plan is locked to the one the
          learner is already trialing */}
      {!isUpgrade && (
      <div style={{ display: "flex", justifyContent: "center", marginTop: 24 }}>
        <div style={{ display: "inline-flex", gap: 4, padding: 4, background: "rgba(255,255,255,0.7)", border: `1.5px solid ${LINE}`, borderRadius: 999 }}>
          {(Object.keys(PLANS) as PlanId[]).map((id) => {
            const on = plan === id;
            return (
              <button
                key={id}
                onClick={() => setPlan(id)}
                style={{
                  padding: "9px 18px",
                  borderRadius: 999,
                  fontSize: 13.5,
                  fontWeight: 700,
                  border: "none",
                  cursor: "pointer",
                  color: on ? "white" : INK_MUTED,
                  background: on ? PRIMARY : "transparent",
                  boxShadow: on ? "0 4px 12px rgba(0,112,196,0.28)" : "none",
                  transition: "all 0.18s",
                }}
              >
                {PLANS[id].weeks}-Week · {inr(PLANS[id].price)}
              </button>
            );
          })}
        </div>
      </div>
      )}

      {error && (
        <p role="alert" style={{ textAlign: "center", color: "oklch(45% 0.18 25)", fontSize: 13.5, fontWeight: 600, marginTop: 18 }}>
          {error}
        </p>
      )}

      {/* option cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: trialEligible ? "repeat(auto-fit, minmax(320px, 1fr))" : "minmax(320px, 460px)",
          justifyContent: "center",
          gap: 16,
          marginTop: 34,
          maxWidth: 720,
          marginLeft: "auto",
          marginRight: "auto",
        }}
      >
        {trialEligible && (
          <div style={{ ...cardStyle, borderLeft: `5px solid ${GREEN}` }}>
            <span style={{ ...tagStyle, background: GREEN_SOFT, color: GREEN_DEEP }}>{Spark} RECOMMENDED</span>
            <h3 style={titleStyle}>Start Free Trial</h3>
            <div style={priceRowStyle}>
              <b style={priceBigStyle}>₹0</b>
              <span style={priceSubStyle}>due today</span>
            </div>
            <FeatureList items={TRIAL_FEATURES} tone="green" />
            <p style={{ fontSize: 12.5, color: INK_FAINT, fontWeight: 600, margin: "14px 0 16px" }}>
              Billing of {inr(p.price)} begins after your 7-day trial. {p.name}.
            </p>
            <button
              onClick={handleStartTrial}
              disabled={startTrialMutation.isPending}
              style={{ ...btnStyle, background: GREEN, color: "white", boxShadow: "0 8px 20px rgba(60,160,110,0.32)" }}
            >
              Start Free Trial {Arrow}
            </button>
          </div>
        )}

        <div style={{ ...cardStyle, borderLeft: `5px solid ${PRIMARY}` }}>
          <span style={{ ...tagStyle, background: PRIMARY_SOFT, color: PRIMARY_DEEP }}>
            {Lock} {isUpgrade ? "UPGRADE" : "PAY ONCE"}
          </span>
          <h3 style={titleStyle}>
            {isUpgrade ? "Purchase your course" : "Pay now & start immediately"}
          </h3>
          <div style={priceRowStyle}>
            <b style={priceBigStyle}>{inr(p.price)}</b>
            <span style={priceSubStyle}>one-time · {p.weeks} weeks</span>
          </div>
          <FeatureList items={PAY_FEATURES} tone="blue" />
          <button
            onClick={handlePayNow}
            style={{ ...btnStyle, marginTop: 18, background: PRIMARY, color: "white", boxShadow: "0 8px 20px rgba(0,112,196,0.32)" }}
          >
            {isUpgrade ? `Purchase for ${inr(p.price)}` : `Pay ${inr(p.price)} securely`} {Lock}
          </button>
        </div>
      </div>

      <div style={{ textAlign: "center" }}>
        <button onClick={() => router.push("/pricing")} style={{ ...backlinkStyle, background: "none", border: "none", cursor: "pointer" }}>
          {Back} Back to plans
        </button>
      </div>
    </div>
  );
}

// ── shared inline style objects ────────────────────────────────────────────────
const cardStyle: React.CSSProperties = {
  position: "relative",
  background: "rgba(255,255,255,0.92)",
  borderRadius: 24,
  padding: "28px 28px 26px",
  overflow: "hidden",
  border: "1.5px solid rgba(255,255,255,0.9)",
  boxShadow: "0 10px 34px rgba(80,110,180,0.12)",
  display: "flex",
  flexDirection: "column",
};
const tagStyle: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 7,
  alignSelf: "flex-start",
  padding: "6px 13px",
  borderRadius: 999,
  fontSize: 12,
  fontWeight: 800,
  letterSpacing: "0.02em",
};
const titleStyle: React.CSSProperties = { fontSize: 21, fontWeight: 800, letterSpacing: "-0.02em", color: NAVY, marginTop: 12 };
const priceRowStyle: React.CSSProperties = { display: "flex", alignItems: "baseline", gap: 9, marginTop: 14 };
const priceBigStyle: React.CSSProperties = { fontSize: 42, fontWeight: 800, letterSpacing: "-0.03em", color: NAVY, lineHeight: 1 };
const priceSubStyle: React.CSSProperties = { fontSize: 14, color: INK_MUTED, fontWeight: 600 };
const btnStyle: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 9,
  padding: "15px 24px",
  borderRadius: 14,
  fontSize: 15,
  fontWeight: 800,
  whiteSpace: "nowrap",
  border: "none",
  cursor: "pointer",
};
const backlinkStyle: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 7,
  fontSize: 14,
  fontWeight: 700,
  color: INK_MUTED,
  marginTop: 26,
};

export default function ChooseStartPage() {
  return (
    <main
      style={{
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        minHeight: "100svh",
        paddingTop: 100,
        background: "radial-gradient(1100px 620px at 78% -8%, rgba(0,112,196,0.10), transparent 60%), oklch(96% 0.02 245)",
      }}
    >
      <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" />
      <LandingNavbar showCTA={false} />
      <Suspense fallback={null}>
        <ChooseStartInner />
      </Suspense>
    </main>
  );
}
