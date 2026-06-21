"use client";

import { Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { LandingNavbar } from "@/components/layout/LandingNavbar";
import { paymentsApi, type PaymentDetailRead } from "@/lib/payments-api";
import {
  Arrow,
  DownloadReceiptButton,
  INK_MUTED,
  NAVY,
  PaymentReceiptCard,
  PRIMARY,
} from "@/components/payment/PaymentReceiptCard";

/**
 * Payment Success — the reviewer-grade proof page (mock:
 * docs/PAYMENT_INTEGRATION/payment_successful.png).
 *
 * The transaction-summary + subscription panel are rendered by the shared
 * `PaymentReceiptCard` (also used by `/payment/receipt`). Data comes from
 * `GET /api/payments/by-order/{order_id}` (paymentsApi.byOrder), keyed off the
 * `order_id` query param set by the Pay-Now flow after `verify`.
 */

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

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "8px 28px 70px" }}>
      <PaymentReceiptCard data={data} isLoading={isLoading} />

      {/* ctas — the dashboard is reached ONLY by pressing "Start your journey" */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, marginTop: 26 }}>
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
          Start your journey {Arrow}
        </button>
        <DownloadReceiptButton data={data} variant="outline" />
      </div>
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
