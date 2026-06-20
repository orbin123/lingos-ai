"use client";

import { Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { LandingNavbar } from "@/components/layout/LandingNavbar";
import { paymentsApi, type PaymentDetailRead } from "@/lib/payments-api";

/**
 * Payment Success — the reviewer-grade proof page (mock:
 * docs/PAYMENT_INTEGRATION/payment_successful.png).
 *
 * Data comes from `GET /api/payments/by-order/{order_id}` (paymentsApi.byOrder),
 * keyed off the `order_id` query param set by the Pay-Now flow after `verify`.
 */
const PRIMARY = "#0070C4";
const GREEN = "oklch(56% 0.15 155)";
const GREEN_DEEP = "oklch(46% 0.15 155)";
const GREEN_SOFT = "oklch(95% 0.05 155)";
const NAVY = "oklch(20% 0.09 245)";
const NAVY_SOFT = "oklch(28% 0.08 245)";
const INK_MUTED = "oklch(45% 0.07 240)";
const LINE_SOFT = "oklch(90% 0.02 240)";

const PLACEHOLDER = "—";

const CheckBig = (
  <svg width="46" height="46" viewBox="0 0 24 24" fill="none">
    <path d="M5 13l4 4L19 7" stroke="white" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);
const Arrow = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
    <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);
const Receipt = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
    <path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
    <path d="M9 8h6M9 12h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  </svg>
);
const Star = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
    <path d="M12 3l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9 6.8 19.2l1-5.8L3.5 9.2l5.9-.9L12 3z" />
  </svg>
);

const MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, monospace";

function TRow({ k, v, mono = false }: { k: string; v: string; mono?: boolean }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 20px", fontSize: 13.5, borderTop: `1px solid ${LINE_SOFT}` }}>
      <span style={{ color: INK_MUTED, fontWeight: 600 }}>{k}</span>
      <span style={{ color: NAVY, fontWeight: 700, fontFamily: mono ? MONO : undefined, fontSize: mono ? 12.5 : undefined }}>{v}</span>
    </div>
  );
}

function SubRow({ k, v }: { k: string; v: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 3, padding: "13px 20px", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
      <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.04em", textTransform: "uppercase", opacity: 0.6 }}>{k}</span>
      <span style={{ fontSize: 16, fontWeight: 800 }}>{v}</span>
    </div>
  );
}

// ── value formatters (defensive — fields may be null pre-webhook) ──────────────
const METHOD_LABELS: Record<string, string> = {
  card: "Card",
  upi: "UPI",
  netbanking: "Net Banking",
  wallet: "Wallet",
  emi: "EMI",
};

function formatMethod(method: string | null): string {
  if (!method) return "Processing…"; // filled by the webhook (Phase 4); render defensively
  const key = method.toLowerCase();
  return METHOD_LABELS[key] ?? method.charAt(0).toUpperCase() + method.slice(1);
}

function formatDateTime(iso: string | null): string {
  if (!iso) return PLACEHOLDER;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return PLACEHOLDER;
  return d.toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatDate(iso: string | null): string {
  if (!iso) return PLACEHOLDER;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return PLACEHOLDER;
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

function formatAmount(amount: number, currency: string): string {
  // `amount` is in rupees (catalog unit) per the by-order schema — not paise.
  const symbol =
    currency?.toUpperCase() === "INR" ? "₹" : currency ? `${currency.toUpperCase()} ` : "";
  return symbol + amount.toLocaleString("en-IN");
}

function titleCase(s: string | null): string {
  if (!s) return PLACEHOLDER;
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function Fallback({ message, onContinue }: { message: string; onContinue: () => void }) {
  return (
    <div style={{ maxWidth: 520, margin: "40px auto 0", padding: "0 28px", textAlign: "center" }}>
      <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", color: NAVY }}>
        Order not found
      </h1>
      <p style={{ fontSize: 15, color: INK_MUTED, marginTop: 10, lineHeight: 1.5 }}>{message}</p>
      <button
        onClick={onContinue}
        style={{
          marginTop: 24,
          display: "inline-flex",
          alignItems: "center",
          gap: 9,
          padding: "13px 24px",
          borderRadius: 14,
          fontSize: 15,
          fontWeight: 800,
          border: "none",
          cursor: "pointer",
          background: PRIMARY,
          color: "white",
          boxShadow: "0 8px 20px rgba(0,112,196,0.32)",
        }}
      >
        Go to dashboard {Arrow}
      </button>
    </div>
  );
}

function PaymentSuccessInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const orderId = searchParams.get("order_id");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["payment-by-order", orderId],
    queryFn: () => paymentsApi.byOrder(orderId as string),
    enabled: !!orderId,
    // Bounded poll: pick up `method` once the webhook lands; stop when filled or
    // after a few attempts (in verify-first ordering it may stay null until Phase 4).
    refetchInterval: (query) => {
      const d = query.state.data as PaymentDetailRead | undefined;
      if (!d || d.method != null) return false;
      return query.state.dataUpdateCount < 6 ? 4000 : false;
    },
  });

  if (!orderId) {
    return (
      <Fallback
        message="We couldn't find a payment reference for this page. If you completed a payment, your subscription is still active."
        onContinue={() => router.push("/dashboard")}
      />
    );
  }

  if (isError) {
    return (
      <Fallback
        message="We couldn't load this payment. It may belong to a different account, or the reference is invalid."
        onContinue={() => router.push("/dashboard")}
      />
    );
  }

  const statusLabel =
    data && (data.status === "paid" || data.status === "active")
      ? "CONFIRMED"
      : (data?.status ?? "").toUpperCase() || "PROCESSING";

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "8px 28px 70px" }}>
      {/* hero */}
      <div style={{ textAlign: "center", padding: "18px 0 8px" }}>
        <div
          style={{
            width: 96,
            height: 96,
            margin: "0 auto 22px",
            borderRadius: "50%",
            background: GREEN,
            display: "grid",
            placeItems: "center",
            boxShadow: "0 14px 34px rgba(60,160,110,0.4)",
          }}
        >
          {CheckBig}
        </div>
        <h1 style={{ fontSize: 34, fontWeight: 800, letterSpacing: "-0.03em", color: NAVY }}>Payment successful</h1>
        <p style={{ fontSize: 15.5, color: INK_MUTED, marginTop: 8 }}>
          Your subscription is active and your access has been provisioned.
        </p>
      </div>

      {/* detail grid */}
      <div className="ps-grid">
        {/* transaction summary */}
        <div style={{ background: "rgba(255,255,255,0.95)", border: `1.5px solid ${LINE_SOFT}`, borderRadius: 20, boxShadow: "0 8px 28px rgba(80,110,180,0.1)", overflow: "hidden" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 9, padding: "16px 20px", fontSize: 13.5, fontWeight: 800, color: NAVY }}>
            {Receipt} Transaction summary
          </div>
          <TRow k="Payment ID" v={data?.provider_payment_id ?? (isLoading ? PLACEHOLDER : "Processing…")} mono />
          <TRow k="Order ID" v={data?.provider_order_id ?? PLACEHOLDER} mono />
          <TRow k="Amount" v={data ? formatAmount(data.amount, data.currency) : PLACEHOLDER} />
          <TRow k="Payment Method" v={data ? formatMethod(data.method) : PLACEHOLDER} />
          <TRow k="Date" v={data ? formatDateTime(data.paid_at) : PLACEHOLDER} />
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 20px", fontSize: 13.5, borderTop: `1px solid ${LINE_SOFT}` }}>
            <span style={{ color: INK_MUTED, fontWeight: 600 }}>Status</span>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "4px 11px", borderRadius: 999, background: GREEN_SOFT, color: GREEN_DEEP, fontSize: 12, fontWeight: 800 }}>
              <span style={{ width: 7, height: 7, borderRadius: "50%", background: GREEN }} />
              {statusLabel}
            </span>
          </div>
        </div>

        {/* subscription panel */}
        <div style={{ background: `linear-gradient(150deg, ${NAVY}, ${NAVY_SOFT})`, color: "white", borderRadius: 20, overflow: "hidden", boxShadow: "0 8px 28px rgba(80,110,180,0.1)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 9, padding: "16px 20px", fontSize: 13.5, fontWeight: 800, borderBottom: "1px solid rgba(255,255,255,0.14)" }}>
            {Star} Subscription
          </div>
          <SubRow k="Plan" v={data?.plan_name ?? data?.plan_id ?? PLACEHOLDER} />
          <SubRow k="Status" v={data ? titleCase(data.subscription_status) : PLACEHOLDER} />
          <SubRow k="Billing" v="One-time" />
          <SubRow k="Access until" v={data ? formatDate(data.current_period_end) : PLACEHOLDER} />
        </div>
      </div>

      {/* cta */}
      <div style={{ display: "flex", justifyContent: "center", marginTop: 26 }}>
        <button
          onClick={() => router.push("/dashboard")}
          style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 9,
            width: "100%",
            maxWidth: 400,
            padding: "15px 24px",
            borderRadius: 14,
            fontSize: 15,
            fontWeight: 800,
            border: "none",
            cursor: "pointer",
            background: PRIMARY,
            color: "white",
            boxShadow: "0 8px 20px rgba(0,112,196,0.32)",
          }}
        >
          Start learning {Arrow}
        </button>
      </div>

      <style>{`
        .ps-grid { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 20px; margin-top: 30px; align-items: start; }
        @media (max-width: 760px) { .ps-grid { grid-template-columns: 1fr; } }
      `}</style>
    </div>
  );
}

export default function PaymentSuccessPage() {
  return (
    <main
      style={{
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        minHeight: "100svh",
        paddingTop: 100,
        background: "radial-gradient(1100px 620px at 78% -8%, rgba(0,112,196,0.10), transparent 60%), oklch(96% 0.02 245)",
      }}
    >
      <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" />
      <LandingNavbar showCTA={false} />
      <Suspense fallback={null}>
        <PaymentSuccessInner />
      </Suspense>
    </main>
  );
}
