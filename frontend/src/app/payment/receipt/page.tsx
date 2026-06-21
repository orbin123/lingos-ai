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
 * Purchase receipt — reuses the shared `PaymentReceiptCard` (so it never drifts
 * from `/payment/success`). Reached from Settings → "Purchase details".
 *
 * - `?order_id=…` → render that single receipt (via `by-order`).
 * - no param → list the user's payments (via `mine`); deep-link a single one,
 *   or show a chooser when there is more than one.
 */

const Back = (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
    <path d="M19 12H5M11 18l-6-6 6-6" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const ghostBtn: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 7,
  fontSize: 14,
  fontWeight: 700,
  color: INK_MUTED,
  background: "none",
  border: "none",
  cursor: "pointer",
};

function fmtAmount(p: PaymentDetailRead): string {
  const symbol = p.currency?.toUpperCase() === "INR" ? "₹" : `${p.currency ?? ""} `;
  return symbol + p.amount.toLocaleString("en-IN");
}

function fmtDate(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

function Empty({ title, message, onBack }: { title: string; message: string; onBack: () => void }) {
  return (
    <div style={{ maxWidth: 520, margin: "40px auto 0", padding: "0 28px", textAlign: "center" }}>
      <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", color: NAVY }}>{title}</h1>
      <p style={{ fontSize: 15, color: INK_MUTED, marginTop: 10, lineHeight: 1.5 }}>{message}</p>
      <button onClick={onBack} style={{ ...ghostBtn, marginTop: 22 }}>
        {Back} Back to settings
      </button>
    </div>
  );
}

/** Single receipt, driven by `?order_id=`. */
function SingleReceipt({ orderId }: { orderId: string }) {
  const router = useRouter();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["payment-by-order", orderId],
    queryFn: () => paymentsApi.byOrder(orderId),
  });

  if (isError) {
    return (
      <Empty
        title="Receipt not found"
        message="We couldn't load this payment. It may belong to a different account, or the reference is invalid."
        onBack={() => router.push("/settings")}
      />
    );
  }

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "8px 28px 70px" }}>
      <PaymentReceiptCard
        data={data}
        isLoading={isLoading}
        heading="Payment receipt"
        subheading="A record of your purchase. Download a PDF copy for your files."
      />
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, marginTop: 26 }}>
        <DownloadReceiptButton data={data} variant="solid" />
        <button onClick={() => router.push("/settings")} style={ghostBtn}>
          {Back} Back to settings
        </button>
      </div>
    </div>
  );
}

/** Chooser shown when the user has more than one payment. */
function ReceiptList() {
  const router = useRouter();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["payments-mine"],
    queryFn: paymentsApi.mine,
  });

  if (isLoading) return null;

  if (isError) {
    return (
      <Empty
        title="Couldn't load purchases"
        message="Something went wrong loading your payments. Please try again."
        onBack={() => router.push("/settings")}
      />
    );
  }

  const payments = data ?? [];

  if (payments.length === 0) {
    return (
      <Empty
        title="No payments yet"
        message="You haven't made a purchase yet. Receipts will appear here once you do."
        onBack={() => router.push("/settings")}
      />
    );
  }

  // Exactly one → render it directly (no need to choose).
  if (payments.length === 1 && payments[0].provider_order_id) {
    return <SingleReceipt orderId={payments[0].provider_order_id} />;
  }

  return (
    <div style={{ maxWidth: 640, margin: "0 auto", padding: "12px 28px 70px" }}>
      <button onClick={() => router.push("/settings")} style={{ ...ghostBtn, marginBottom: 14 }}>
        {Back} Back to settings
      </button>
      <h1 style={{ fontSize: 28, fontWeight: 800, letterSpacing: "-0.02em", color: NAVY }}>Your purchases</h1>
      <p style={{ fontSize: 15, color: INK_MUTED, marginTop: 8 }}>Select a purchase to view its receipt.</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 22 }}>
        {payments.map((p, i) => (
          <button
            key={p.provider_order_id ?? p.provider_payment_id ?? i}
            onClick={() =>
              p.provider_order_id &&
              router.push(`/payment/receipt?order_id=${encodeURIComponent(p.provider_order_id)}`)
            }
            disabled={!p.provider_order_id}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 16,
              padding: "16px 20px",
              borderRadius: 16,
              border: "1.5px solid oklch(90% 0.02 240)",
              background: "rgba(255,255,255,0.95)",
              boxShadow: "0 6px 20px rgba(80,110,180,0.08)",
              cursor: p.provider_order_id ? "pointer" : "not-allowed",
              textAlign: "left",
            }}
          >
            <div>
              <div style={{ fontSize: 15.5, fontWeight: 800, color: NAVY }}>
                {p.plan_name ?? p.plan_id ?? "Purchase"}
              </div>
              <div style={{ fontSize: 13, color: INK_MUTED, marginTop: 4 }}>
                {fmtAmount(p)} · {fmtDate(p.paid_at)}
              </div>
            </div>
            <span style={{ color: PRIMARY }}>{Arrow}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function ReceiptInner() {
  const searchParams = useSearchParams();
  const orderId = searchParams.get("order_id");
  return orderId ? <SingleReceipt orderId={orderId} /> : <ReceiptList />;
}

export default function PaymentReceiptPage() {
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
        <ReceiptInner />
      </Suspense>
    </main>
  );
}
