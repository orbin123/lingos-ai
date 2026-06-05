"use client";

import type { CSSProperties } from "react";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Save } from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import { BillingStatusBadge } from "@/components/admin/BillingPrimitives";
import {
  AdminButton,
  AdminPanel,
  formatAdminDate,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import { adminApi, type SubscriberItem, type TrialUserItem } from "@/lib/admin-api";
import { canManageSubscriptions } from "@/lib/admin-access";
import { authApi } from "@/lib/auth-api";

export default function AdminSubscribersPage() {
  const overviewQuery = useQuery({
    queryKey: ["admin", "subscribers"],
    queryFn: adminApi.subscribers,
  });
  const meQuery = useQuery({ queryKey: ["me"], queryFn: authApi.me });
  const canManage = canManageSubscriptions(meQuery.data);

  const subscribers = overviewQuery.data?.subscribers ?? [];
  const trials = overviewQuery.data?.trials ?? [];

  return (
    <AdminLayout title="Subscribers" eyebrow="Billing operations">
      <section style={sectionHeaderStyle}>
        <h2 style={sectionTitleStyle}>Paying subscribers</h2>
        <span style={countStyle}>{subscribers.length}</span>
      </section>
      <AdminPanel style={{ overflow: "hidden", marginBottom: 28 }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>User</th>
              <th style={thStyle}>Plan</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Purchased</th>
              <th style={thStyle}>Access until</th>
              {canManage && <th style={thStyle}>Manage access</th>}
            </tr>
          </thead>
          <tbody>
            {subscribers.map((sub) => (
              <SubscriberRow key={sub.user_id} sub={sub} canManage={canManage} />
            ))}
            {subscribers.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={canManage ? 6 : 5}>
                  {overviewQuery.isLoading ? "Loading…" : "No paying subscribers yet."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>

      <section style={sectionHeaderStyle}>
        <h2 style={sectionTitleStyle}>Trial users</h2>
        <span style={countStyle}>{trials.length}</span>
      </section>
      <AdminPanel style={{ overflow: "hidden" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>User</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Signed up</th>
              <th style={thStyle}>Trial ends</th>
            </tr>
          </thead>
          <tbody>
            {trials.map((trial) => (
              <TrialRow key={trial.user_id} trial={trial} />
            ))}
            {trials.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={4}>
                  {overviewQuery.isLoading ? "Loading…" : "No trial users."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>
    </AdminLayout>
  );
}

function SubscriberRow({
  sub,
  canManage,
}: {
  sub: SubscriberItem;
  canManage: boolean;
}) {
  const queryClient = useQueryClient();
  const [date, setDate] = useState(toDateInput(sub.access_expires_at));

  const mutation = useMutation({
    mutationFn: (isoDate: string) =>
      adminApi.updateSubscriberAccess(sub.user_id, isoDate),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin", "subscribers"] });
    },
  });

  const changed = date !== toDateInput(sub.access_expires_at);

  return (
    <tr>
      <td style={tdStyle}>
        <div style={strongTextStyle}>{sub.name}</div>
        <div style={mutedTextStyle}>{sub.email}</div>
      </td>
      <td style={tdStyle}>{sub.plan_name ?? sub.plan_id ?? "—"}</td>
      <td style={tdStyle}>
        <BillingStatusBadge status={sub.status} />
      </td>
      <td style={tdStyle}>{formatAdminDate(sub.purchased_at)}</td>
      <td style={tdStyle}>{formatAdminDate(sub.access_expires_at)}</td>
      {canManage && (
        <td style={tdStyle}>
          <div style={manageStyle}>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              style={dateInputStyle}
            />
            <AdminButton
              tone="secondary"
              disabled={!changed || !date || mutation.isPending}
              onClick={() => mutation.mutate(`${date}T00:00:00Z`)}
            >
              <Save size={15} />
              Save
            </AdminButton>
          </div>
        </td>
      )}
    </tr>
  );
}

function TrialRow({ trial }: { trial: TrialUserItem }) {
  return (
    <tr>
      <td style={tdStyle}>
        <div style={strongTextStyle}>{trial.name}</div>
        <div style={mutedTextStyle}>{trial.email}</div>
      </td>
      <td style={tdStyle}>
        <BillingStatusBadge status={trial.status === "trial" ? "trialing" : trial.status} />
      </td>
      <td style={tdStyle}>{formatAdminDate(trial.signed_up_at)}</td>
      <td style={tdStyle}>{formatAdminDate(trial.trial_ends_at)}</td>
    </tr>
  );
}

function toDateInput(value: string | null): string {
  if (!value) return "";
  return new Date(value).toISOString().slice(0, 10);
}

const sectionHeaderStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 10,
  marginBottom: 12,
};

const sectionTitleStyle: CSSProperties = {
  margin: 0,
  fontSize: 16,
  fontWeight: 800,
  color: "oklch(22% 0.05 245)",
};

const countStyle: CSSProperties = {
  minWidth: 24,
  textAlign: "center",
  padding: "1px 8px",
  borderRadius: 999,
  background: "oklch(93% 0.03 245)",
  color: "oklch(40% 0.08 245)",
  fontSize: 12,
  fontWeight: 800,
};

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

const manageStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
};

const dateInputStyle: CSSProperties = {
  minHeight: 38,
  borderRadius: 8,
  border: "1px solid oklch(86% 0.018 245)",
  padding: "0 10px",
  background: "white",
  color: "oklch(20% 0.055 245)",
  fontFamily: "inherit",
  fontSize: 13,
  fontWeight: 700,
};
