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

const STATUS_FILTERS = [
  "all",
  "active",
  "cancelled",
  "trial",
  "expired",
  "not_started",
  "unverified",
] as const;

export default function AdminSubscribersPage() {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const overviewQuery = useQuery({
    queryKey: ["admin", "subscribers", statusFilter],
    queryFn: () =>
      adminApi.subscribers(statusFilter === "all" ? undefined : statusFilter),
  });
  const meQuery = useQuery({ queryKey: ["me"], queryFn: authApi.me });
  const canManage = canManageSubscriptions(meQuery.data);

  const subscribers = overviewQuery.data?.subscribers ?? [];
  const trials = overviewQuery.data?.trials ?? [];

  return (
    <AdminLayout title="Subscribers" eyebrow="Billing operations">
      <div style={filterRowStyle}>
        {STATUS_FILTERS.map((value) => (
          <button
            key={value}
            type="button"
            onClick={() => setStatusFilter(value)}
            style={{
              ...filterChipStyle,
              ...(statusFilter === value ? filterChipActiveStyle : {}),
            }}
          >
            {value.replace("_", " ")}
          </button>
        ))}
      </div>

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
              <th style={thStyle}>Trial started</th>
              <th style={thStyle}>Trial ends</th>
              {canManage && <th style={thStyle}>Manage trial</th>}
            </tr>
          </thead>
          <tbody>
            {trials.map((trial) => (
              <TrialRow key={trial.user_id} trial={trial} canManage={canManage} />
            ))}
            {trials.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={canManage ? 6 : 5}>
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

function TrialRow({
  trial,
  canManage,
}: {
  trial: TrialUserItem;
  canManage: boolean;
}) {
  const queryClient = useQueryClient();
  const [date, setDate] = useState(toDateInput(trial.trial_ends_at));
  const mutation = useMutation({
    mutationFn: (endsAt: string) =>
      adminApi.updateSubscriberSubscription(trial.user_id, {
        status: "trial",
        trial_ends_at: endsAt,
        // Granting a trial to someone who never started one stamps the
        // start too, so "one trial per user" accounting stays coherent.
        ...(trial.trial_started_at
          ? {}
          : { trial_started_at: new Date().toISOString() }),
      }),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["admin", "subscribers"] }),
  });
  const changed = date !== toDateInput(trial.trial_ends_at);

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
      <td style={tdStyle}>{formatAdminDate(trial.trial_started_at)}</td>
      <td style={tdStyle}>{formatAdminDate(trial.trial_ends_at)}</td>
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
              disabled={!date || !changed || mutation.isPending}
              onClick={() => mutation.mutate(`${date}T00:00:00Z`)}
            >
              <Save size={15} />
              {trial.trial_started_at ? "Save" : "Grant"}
            </AdminButton>
          </div>
        </td>
      )}
    </tr>
  );
}

function toDateInput(value: string | null): string {
  if (!value) return "";
  return new Date(value).toISOString().slice(0, 10);
}

const filterRowStyle: CSSProperties = {
  display: "flex",
  gap: 8,
  flexWrap: "wrap",
  marginBottom: 18,
};

const filterChipStyle: CSSProperties = {
  border: "1.5px solid oklch(86% 0.025 240)",
  borderRadius: 999,
  background: "white",
  padding: "6px 14px",
  fontSize: 13,
  fontWeight: 700,
  color: "oklch(40% 0.06 240)",
  cursor: "pointer",
  textTransform: "capitalize",
};

const filterChipActiveStyle: CSSProperties = {
  background: "oklch(35% 0.1 245)",
  borderColor: "oklch(35% 0.1 245)",
  color: "white",
};

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
