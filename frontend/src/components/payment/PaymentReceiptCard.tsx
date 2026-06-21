"use client";

import { useState } from "react";
import type { PaymentDetailRead } from "@/lib/payments-api";

/**
 * Shared receipt surface used by BOTH the completion page
 * (`/payment/success`) and the receipt page (`/payment/receipt`) so the two
 * can never visually drift. Renders the success hero, the transaction-summary
 * + subscription panel, and a client-side PDF download — all fed by the
 * server-verified `by-order` payload.
 */

// ── palette (exported so the host pages share the same accents) ───────────────
export const PRIMARY = "#0070C4";
export const GREEN = "oklch(56% 0.15 155)";
export const GREEN_DEEP = "oklch(46% 0.15 155)";
export const GREEN_SOFT = "oklch(95% 0.05 155)";
export const NAVY = "oklch(20% 0.09 245)";
export const NAVY_SOFT = "oklch(28% 0.08 245)";
export const INK_MUTED = "oklch(45% 0.07 240)";
const LINE_SOFT = "oklch(90% 0.02 240)";

const PLACEHOLDER = "—";
const MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, monospace";

export const Arrow = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
    <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);
const CheckBig = (
  <svg width="46" height="46" viewBox="0 0 24 24" fill="none">
    <path d="M5 13l4 4L19 7" stroke="white" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
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
const Download = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
    <path d="M12 3v12M7 11l5 5 5-5M5 21h14" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

// ── value formatters (defensive — fields may be null pre-webhook) ──────────────
const METHOD_LABELS: Record<string, string> = {
  card: "Card",
  upi: "UPI",
  netbanking: "Net Banking",
  wallet: "Wallet",
  emi: "EMI",
};

function formatMethod(method: string | null): string {
  if (!method) return "Processing…"; // filled by the webhook; render defensively
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

function statusLabelOf(data: PaymentDetailRead | undefined): string {
  if (data && (data.status === "paid" || data.status === "active")) return "CONFIRMED";
  return (data?.status ?? "").toUpperCase() || "PROCESSING";
}

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

export function PaymentReceiptCard({
  data,
  isLoading = false,
  heading = "Payment successful",
  subheading = "Your subscription is active and your access has been provisioned.",
}: {
  data: PaymentDetailRead | undefined;
  isLoading?: boolean;
  heading?: string;
  subheading?: string;
}) {
  return (
    <>
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
        <h1 style={{ fontSize: 34, fontWeight: 800, letterSpacing: "-0.03em", color: NAVY }}>{heading}</h1>
        <p style={{ fontSize: 15.5, color: INK_MUTED, marginTop: 8 }}>{subheading}</p>
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
              {statusLabelOf(data)}
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

      <style>{`
        .ps-grid { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 20px; margin-top: 30px; align-items: start; }
        @media (max-width: 760px) { .ps-grid { grid-template-columns: 1fr; } }
      `}</style>
    </>
  );
}

/**
 * Client-side PDF receipt. `jspdf` is lazy-imported inside the click handler so
 * it never lands in the initial bundle. Renders the same server-verified fields
 * as the page (with the same defensive `method` → "Processing…" fallback).
 */
export function DownloadReceiptButton({
  data,
  variant = "solid",
}: {
  data: PaymentDetailRead | undefined;
  variant?: "solid" | "outline";
}) {
  const [busy, setBusy] = useState(false);
  const disabled = !data || busy;

  const handleDownload = async () => {
    if (!data) return;
    setBusy(true);
    try {
      const { jsPDF } = await import("jspdf");
      const doc = new jsPDF({ unit: "pt", format: "a4" });
      const left = 56;
      let y = 72;

      doc.setFont("helvetica", "bold");
      doc.setFontSize(22);
      doc.setTextColor(17, 34, 64);
      doc.text("LingosAI", left, y);

      doc.setFont("helvetica", "normal");
      doc.setFontSize(11);
      doc.setTextColor(110, 120, 140);
      y += 20;
      doc.text("Payment receipt — Test Mode", left, y);

      y += 26;
      doc.setDrawColor(225, 230, 238);
      doc.line(left, y, 539, y);

      const rows: Array<[string, string]> = [
        ["Payment ID", data.provider_payment_id ?? "Processing…"],
        ["Order ID", data.provider_order_id ?? "—"],
        ["Amount", formatAmount(data.amount, data.currency)],
        ["Payment Method", formatMethod(data.method)],
        ["Date", formatDateTime(data.paid_at)],
        ["Status", statusLabelOf(data)],
        ["Plan", data.plan_name ?? data.plan_id ?? "—"],
        ["Subscription", titleCase(data.subscription_status)],
        ["Access until", formatDate(data.current_period_end)],
      ];

      y += 30;
      doc.setFontSize(12);
      for (const [label, value] of rows) {
        doc.setFont("helvetica", "normal");
        doc.setTextColor(110, 120, 140);
        doc.text(label, left, y);
        doc.setFont("helvetica", "bold");
        doc.setTextColor(17, 34, 64);
        doc.text(String(value), 539, y, { align: "right" });
        y += 28;
      }

      y += 8;
      doc.setDrawColor(225, 230, 238);
      doc.line(left, y, 539, y);
      y += 24;
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(140, 150, 168);
      doc.text("This is a Test-Mode receipt generated by LingosAI. No real funds were charged.", left, y);

      const ref = data.provider_order_id ?? "receipt";
      doc.save(`lingosai-receipt-${ref}.pdf`);
    } finally {
      setBusy(false);
    }
  };

  const base: React.CSSProperties = {
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
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.6 : 1,
  };
  const skin: React.CSSProperties =
    variant === "solid"
      ? { border: "none", background: PRIMARY, color: "white", boxShadow: "0 8px 20px rgba(0,112,196,0.32)" }
      : { border: `1.5px solid ${PRIMARY}`, background: "white", color: PRIMARY };

  return (
    <button onClick={handleDownload} disabled={disabled} style={{ ...base, ...skin }}>
      {Download} {busy ? "Preparing…" : "Download receipt (PDF)"}
    </button>
  );
}
