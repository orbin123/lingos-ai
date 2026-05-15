"use client";

import type { CSSProperties } from "react";
import { useQuery } from "@tanstack/react-query";

import { AdminLayout } from "@/components/admin/AdminLayout";
import { BillingStatusBadge, maskProviderId } from "@/components/admin/BillingPrimitives";
import {
  AdminPanel,
  formatAdminDateTime,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import { adminApi, type AdminPayment } from "@/lib/admin-api";

export default function AdminPaymentsPage() {
  const paymentsQuery = useQuery({
    queryKey: ["admin", "payments"],
    queryFn: adminApi.payments,
  });
  const payments = paymentsQuery.data ?? [];

  return (
    <AdminLayout title="Payments" eyebrow="Billing operations">
      <AdminPanel style={{ overflow: "hidden" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>User</th>
              <th style={thStyle}>Amount</th>
              <th style={thStyle}>Currency</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Provider</th>
              <th style={thStyle}>Provider ID</th>
              <th style={thStyle}>Paid</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((payment) => (
              <tr key={payment.id}>
                <td style={tdStyle}>
                  <UserCell payment={payment} />
                </td>
                <td style={tdStyle}>{formatAmount(payment.amount, payment.currency)}</td>
                <td style={tdStyle}>{payment.currency}</td>
                <td style={tdStyle}>
                  <BillingStatusBadge status={payment.status} />
                </td>
                <td style={tdStyle}>{payment.provider}</td>
                <td style={tdStyle}>{maskProviderId(payment.provider_payment_id)}</td>
                <td style={tdStyle}>{formatAdminDateTime(payment.paid_at)}</td>
              </tr>
            ))}
            {payments.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={7}>
                  No payments found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>
    </AdminLayout>
  );
}

function UserCell({ payment }: { payment: AdminPayment }) {
  if (!payment.user) return <span style={mutedTextStyle}>Deleted user</span>;
  return (
    <div>
      <div style={strongTextStyle}>{payment.user.name}</div>
      <div style={mutedTextStyle}>{payment.user.email}</div>
    </div>
  );
}

function formatAmount(amount: number, currency: string) {
  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      maximumFractionDigits: 2,
    }).format(amount);
  } catch {
    return `${amount.toFixed(2)} ${currency}`;
  }
}

const strongTextStyle: CSSProperties = {
  color: "oklch(18% 0.055 245)",
  fontWeight: 800,
};

const mutedTextStyle: CSSProperties = {
  marginTop: 3,
  color: "oklch(48% 0.045 245)",
  fontSize: 12,
  fontWeight: 650,
};
