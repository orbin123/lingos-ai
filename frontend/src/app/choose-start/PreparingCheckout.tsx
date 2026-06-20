"use client";

import { useEffect, useState } from "react";

/**
 * "Preparing Secure Checkout" transitional view — the mock's processing
 * screen (docs/PAYMENT_INTEGRATION/loading_animation.png). Phase 1 renders it
 * as a self-animating visual stub triggered by the Pay-Now button; Phase 3
 * reuses it while `createOrder` runs and the Razorpay modal opens.
 *
 * The progress is intentionally driven internally (not by real async state)
 * and eases toward ~92% without completing — the real flow resolves by
 * navigating away, so the spinner should never claim "done" on its own.
 */
const PRIMARY = "#0070C4";
const PRIMARY_SOFT = "#d6e8f7";
const GREEN = "oklch(56% 0.15 155)";
const NAVY = "oklch(20% 0.09 245)";
const INK_MUTED = "oklch(45% 0.07 240)";
const INK_FAINT = "oklch(58% 0.05 240)";

const PAY_STEPS = [
  "Creating secure order",
  "Opening Razorpay checkout",
  "Verifying payment",
  "Activating your subscription",
];
const TRIAL_STEPS = [
  "Validating your account",
  "Creating subscription",
  "Provisioning access",
];

const CheckIcon = (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
    <path
      d="M5 13l4 4L19 7"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export function PreparingCheckout({ mode = "pay" }: { mode?: "pay" | "trial" }) {
  const labels = mode === "trial" ? TRIAL_STEPS : PAY_STEPS;
  const [pct, setPct] = useState(8);
  const [active, setActive] = useState(0);

  // Ease toward ~92% and walk the active step forward; never auto-complete.
  useEffect(() => {
    const tick = setInterval(() => {
      setPct((p) => (p >= 92 ? p : p + Math.max(1, Math.round((92 - p) / 8))));
    }, 280);
    const stepMs = 900;
    const timers = labels.map((_, i) =>
      setTimeout(
        () => setActive((a) => Math.min(labels.length - 1, Math.max(a, i))),
        stepMs * i,
      ),
    );
    return () => {
      clearInterval(tick);
      timers.forEach(clearTimeout);
    };
  }, [labels]);

  const r = 34;
  const c = 2 * Math.PI * r;
  const offset = c - (pct / 100) * c;

  return (
    <div
      style={{
        minHeight: "calc(100svh - 64px)",
        display: "grid",
        placeItems: "center",
        padding: "30px 24px",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 460,
          background: "white",
          borderRadius: 26,
          padding: "42px 38px",
          textAlign: "center",
          boxShadow: "0 24px 60px rgba(40,70,130,0.18)",
          border: "1.5px solid oklch(90% 0.02 240)",
        }}
      >
        <div
          style={{
            width: 76,
            height: 76,
            margin: "0 auto 26px",
            position: "relative",
          }}
        >
          <svg width="76" height="76" viewBox="0 0 76 76" style={{ transform: "rotate(-90deg)" }}>
            <circle cx="38" cy="38" r={r} strokeWidth="7" fill="none" stroke={PRIMARY_SOFT} />
            <circle
              cx="38"
              cy="38"
              r={r}
              strokeWidth="7"
              fill="none"
              stroke={PRIMARY}
              strokeLinecap="round"
              strokeDasharray={c}
              strokeDashoffset={offset}
              style={{ transition: "stroke-dashoffset 0.5s ease" }}
            />
          </svg>
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "grid",
              placeItems: "center",
              fontSize: 19,
              fontWeight: 800,
              color: NAVY,
            }}
          >
            {pct}%
          </div>
        </div>

        <h2
          style={{
            fontSize: 22,
            fontWeight: 800,
            color: NAVY,
            letterSpacing: "-0.02em",
          }}
        >
          {mode === "trial"
            ? "Setting up your free trial"
            : "Preparing secure checkout"}
        </h2>
        <p style={{ fontSize: 14, color: INK_MUTED, marginTop: 7 }}>
          This usually takes a few seconds. Please don&apos;t close this window.
        </p>

        <ul
          style={{
            listStyle: "none",
            margin: "26px 0 0",
            padding: 0,
            display: "flex",
            flexDirection: "column",
            gap: 4,
            textAlign: "left",
          }}
        >
          {labels.map((label, i) => {
            const state = i < active ? "done" : i === active ? "active" : "idle";
            return (
              <li
                key={label}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "12px 14px",
                  borderRadius: 13,
                  fontSize: 14.5,
                  fontWeight: 700,
                  color:
                    state === "active"
                      ? "var(--primary-deep, #00599e)"
                      : state === "done"
                        ? NAVY
                        : INK_FAINT,
                  background: state === "active" ? PRIMARY_SOFT : "transparent",
                  transition: "all 0.35s",
                }}
              >
                <span
                  style={{
                    flex: "none",
                    width: 26,
                    height: 26,
                    borderRadius: "50%",
                    display: "grid",
                    placeItems: "center",
                    fontSize: 12,
                    background:
                      state === "done"
                        ? GREEN
                        : state === "active"
                          ? PRIMARY
                          : "oklch(95% 0.015 240)",
                    color: state === "idle" ? INK_FAINT : "white",
                    transition: "all 0.35s",
                  }}
                >
                  {state === "done" ? (
                    CheckIcon
                  ) : state === "active" ? (
                    <span
                      style={{
                        width: 14,
                        height: 14,
                        border: "2.5px solid rgba(255,255,255,0.45)",
                        borderTopColor: "white",
                        borderRadius: "50%",
                        animation: "lingos-spin 0.7s linear infinite",
                      }}
                    />
                  ) : (
                    i + 1
                  )}
                </span>
                {label}
              </li>
            );
          })}
        </ul>
      </div>
      <style>{`@keyframes lingos-spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
