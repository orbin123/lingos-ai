"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import type { CSSProperties, ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import { BillingStatusBadge, maskProviderId } from "@/components/admin/BillingPrimitives";
import {
  AdminPanel,
  RolePill,
  StatusPill,
  formatAdminDate,
  formatAdminDateTime,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import { adminApi, type AdminUserBilling } from "@/lib/admin-api";

export default function AdminUserDetailPage() {
  const params = useParams<{ id: string }>();
  const userId = Number(params.id);
  const userQuery = useQuery({
    queryKey: ["admin", "users", userId],
    queryFn: () => adminApi.user(userId),
    enabled: Number.isFinite(userId),
  });
  const billingQuery = useQuery({
    queryKey: ["admin", "users", userId, "billing"],
    queryFn: () => adminApi.userBilling(userId),
    enabled: Number.isFinite(userId),
    retry: false,
  });

  const user = userQuery.data;
  const billing = billingQuery.data;

  return (
    <AdminLayout
      title={user?.name ?? "User detail"}
      eyebrow="User management"
      actions={
        <Link href="/admin/users" style={backLinkStyle}>
          <ArrowLeft size={16} />
          Users
        </Link>
      }
    >
      {!user ? (
        <AdminPanel style={{ padding: 22 }}>Loading user...</AdminPanel>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "360px minmax(0, 1fr)", gap: 18 }}>
          <div style={{ display: "grid", gap: 18 }}>
            <AdminPanel style={{ padding: 22 }}>
              <div style={profileHeaderStyle}>
                <div style={avatarStyle}>{initials(user.name)}</div>
                <div>
                  <h2 style={cardTitleStyle}>{user.name}</h2>
                  <p style={mutedStyle}>{user.email}</p>
                </div>
              </div>
              <div style={profileGridStyle}>
                <Field label="Role" value={<RolePill role={user.role} />} />
                <Field label="Status" value={<StatusPill active={user.is_active} />} />
                <Field label="Created" value={formatAdminDate(user.created_at)} />
                <Field
                  label="Diagnosis"
                  value={user.profile?.diagnosis_completed ? "Complete" : "Not complete"}
                />
                <Field label="Country" value={user.profile?.country ?? "Not recorded"} />
                <Field label="Native language" value={user.profile?.native_language ?? "Not recorded"} />
                <Field label="Goal" value={user.profile?.goal ?? "Not recorded"} />
                <Field
                  label="Level"
                  value={user.profile?.self_assessed_level ?? "Not recorded"}
                />
              </div>
            </AdminPanel>

            <AdminPanel style={{ padding: 22 }}>
              <h2 style={cardTitleStyle}>Skill scores</h2>
              <div style={{ display: "grid", gap: 12, marginTop: 16 }}>
                {user.skill_scores.length === 0 && <p style={mutedStyle}>No skill scores yet.</p>}
                {user.skill_scores.map((score) => (
                  <div key={`${score.source}-${score.skill_id}`}>
                    <div style={scoreHeadStyle}>
                      <span>{score.skill_name.replace("_", " ")}</span>
                      <strong>{score.score.toFixed(1)}</strong>
                    </div>
                    <div style={barTrackStyle}>
                      <div style={{ ...barFillStyle, width: `${Math.min(100, score.score * 10)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </AdminPanel>
          </div>

          <div style={{ display: "grid", gap: 18 }}>
            <BillingSection billing={billing} isLoading={billingQuery.isLoading} />

            <AdminPanel style={{ overflow: "hidden" }}>
              <div style={panelHeadStyle}>
                <h2 style={cardTitleStyle}>Recent tasks</h2>
              </div>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>Task</th>
                    <th style={thStyle}>Type</th>
                    <th style={thStyle}>Status</th>
                    <th style={thStyle}>Completed</th>
                  </tr>
                </thead>
                <tbody>
                  {user.recent_tasks.map((task) => (
                    <tr key={task.id}>
                      <td style={tdStyle}>{task.title}</td>
                      <td style={tdStyle}>{task.task_type}</td>
                      <td style={tdStyle}>{task.status}</td>
                      <td style={tdStyle}>{formatAdminDateTime(task.completed_at)}</td>
                    </tr>
                  ))}
                  {user.recent_tasks.length === 0 && (
                    <tr>
                      <td style={tdStyle} colSpan={4}>
                        No recent tasks.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </AdminPanel>

            <AdminPanel style={{ overflow: "hidden" }}>
              <div style={panelHeadStyle}>
                <h2 style={cardTitleStyle}>Recent feedback</h2>
              </div>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>Task</th>
                    <th style={thStyle}>Score</th>
                    <th style={thStyle}>Feedback</th>
                    <th style={thStyle}>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {user.recent_feedback.map((feedback) => (
                    <tr key={feedback.id}>
                      <td style={tdStyle}>{feedback.task_title}</td>
                      <td style={tdStyle}>{feedback.score.toFixed(1)}</td>
                      <td style={{ ...tdStyle, maxWidth: 360 }}>
                        {feedbackSummary(feedback.body)}
                      </td>
                      <td style={tdStyle}>{formatAdminDateTime(feedback.created_at)}</td>
                    </tr>
                  ))}
                  {user.recent_feedback.length === 0 && (
                    <tr>
                      <td style={tdStyle} colSpan={4}>
                        No feedback generated yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </AdminPanel>
          </div>
        </div>
      )}
    </AdminLayout>
  );
}

function BillingSection({
  billing,
  isLoading,
}: {
  billing: AdminUserBilling | undefined;
  isLoading: boolean;
}) {
  const subscription = billing?.subscription ?? null;

  return (
    <AdminPanel style={{ overflow: "hidden" }}>
      <div style={panelHeadStyle}>
        <h2 style={cardTitleStyle}>Billing</h2>
      </div>
      <div style={billingSummaryStyle}>
        <Field label="Plan" value={subscription?.plan_name ?? "No plan"} />
        <Field
          label="Subscription"
          value={
            subscription ? (
              <BillingStatusBadge status={subscription.status} />
            ) : isLoading ? (
              "Loading"
            ) : (
              "Not subscribed"
            )
          }
        />
        <Field label="Trial" value={trialStatus(subscription?.trial_ends_at)} />
        <Field
          label="Provider ID"
          value={maskProviderId(subscription?.provider_subscription_id)}
        />
      </div>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th style={thStyle}>Amount</th>
            <th style={thStyle}>Status</th>
            <th style={thStyle}>Provider</th>
            <th style={thStyle}>Paid</th>
          </tr>
        </thead>
        <tbody>
          {(billing?.payments ?? []).map((payment) => (
            <tr key={payment.id}>
              <td style={tdStyle}>{formatPayment(payment.amount, payment.currency)}</td>
              <td style={tdStyle}>
                <BillingStatusBadge status={payment.status} />
              </td>
              <td style={tdStyle}>
                {payment.provider} / {maskProviderId(payment.provider_payment_id)}
              </td>
              <td style={tdStyle}>{formatAdminDateTime(payment.paid_at)}</td>
            </tr>
          ))}
          {!isLoading && (billing?.payments ?? []).length === 0 && (
            <tr>
              <td style={tdStyle} colSpan={4}>
                No payment history.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </AdminPanel>
  );
}

function Field({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div>
      <div style={fieldLabelStyle}>{label}</div>
      <div style={fieldValueStyle}>{value}</div>
    </div>
  );
}

function initials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

function feedbackSummary(body: Record<string, unknown>) {
  const value = body.overall_message ?? body.practice_suggestion;
  return typeof value === "string" && value.trim() ? value : "Feedback body recorded.";
}

function trialStatus(value: string | null | undefined) {
  if (!value) return "No trial";
  return new Date(value).getTime() > Date.now()
    ? `Ends ${formatAdminDate(value)}`
    : `Ended ${formatAdminDate(value)}`;
}

function formatPayment(amount: number, currency: string) {
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

const backLinkStyle: CSSProperties = {
  minHeight: 38,
  display: "inline-flex",
  alignItems: "center",
  gap: 8,
  borderRadius: 8,
  padding: "0 12px",
  background: "white",
  color: "oklch(28% 0.06 245)",
  border: "1px solid oklch(86% 0.018 245)",
  textDecoration: "none",
  fontSize: 13,
  fontWeight: 800,
};

const profileHeaderStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 14,
  marginBottom: 22,
};

const avatarStyle: CSSProperties = {
  width: 52,
  height: 52,
  borderRadius: 8,
  display: "grid",
  placeItems: "center",
  background: "#0070C4",
  color: "white",
  fontWeight: 850,
};

const cardTitleStyle: CSSProperties = {
  margin: 0,
  color: "oklch(18% 0.055 245)",
  fontSize: 17,
  fontWeight: 850,
};

const mutedStyle: CSSProperties = {
  margin: "4px 0 0",
  color: "oklch(48% 0.045 245)",
  fontSize: 13,
  fontWeight: 600,
};

const profileGridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
  gap: 14,
};

const billingSummaryStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
  gap: 14,
  padding: "0 18px 16px",
};

const fieldLabelStyle: CSSProperties = {
  color: "oklch(48% 0.045 245)",
  fontSize: 11,
  fontWeight: 850,
  letterSpacing: "0.05em",
  textTransform: "uppercase",
  marginBottom: 6,
};

const fieldValueStyle: CSSProperties = {
  color: "oklch(20% 0.055 245)",
  fontSize: 14,
  fontWeight: 700,
  textTransform: "capitalize",
};

const scoreHeadStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 12,
  color: "oklch(25% 0.055 245)",
  fontSize: 13,
  fontWeight: 800,
  textTransform: "capitalize",
  marginBottom: 7,
};

const barTrackStyle: CSSProperties = {
  height: 8,
  borderRadius: 999,
  background: "oklch(93% 0.012 245)",
  overflow: "hidden",
};

const barFillStyle: CSSProperties = {
  height: "100%",
  borderRadius: 999,
  background: "#0070C4",
};

const panelHeadStyle: CSSProperties = {
  padding: "18px 18px 8px",
};
