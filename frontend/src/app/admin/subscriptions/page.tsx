"use client";

import type { CSSProperties } from "react";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Save } from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import { BillingStatusBadge, maskProviderId } from "@/components/admin/BillingPrimitives";
import {
  AdminButton,
  AdminPanel,
  formatAdminDate,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import { adminApi, type AdminSubscription } from "@/lib/admin-api";
import { canManageSubscriptions } from "@/lib/admin-access";
import { authApi } from "@/lib/auth-api";

const SUBSCRIPTION_STATUSES = [
  "trialing",
  "active",
  "past_due",
  "paused",
  "canceled",
  "expired",
];

export default function AdminSubscriptionsPage() {
  const queryClient = useQueryClient();
  const subscriptionsQuery = useQuery({
    queryKey: ["admin", "subscriptions"],
    queryFn: adminApi.subscriptions,
  });
  const meQuery = useQuery({ queryKey: ["me"], queryFn: authApi.me });
  const canManage = canManageSubscriptions(meQuery.data);
  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      adminApi.updateSubscription(id, { status }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin", "subscriptions"] });
      await queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
    },
  });

  const subscriptions = subscriptionsQuery.data ?? [];

  return (
    <AdminLayout title="Subscriptions" eyebrow="Billing operations">
      <AdminPanel style={{ overflow: "hidden" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>User</th>
              <th style={thStyle}>Plan</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Trial End</th>
              <th style={thStyle}>Period End</th>
              <th style={thStyle}>Provider</th>
              <th style={thStyle}>Provider ID</th>
              {canManage && <th style={thStyle}>Manage</th>}
            </tr>
          </thead>
          <tbody>
            {subscriptions.map((subscription) => (
              <SubscriptionRow
                key={`${subscription.id}-${subscription.status}-${subscription.updated_at}`}
                subscription={subscription}
                canManage={canManage}
                isSaving={updateMutation.isPending}
                onSave={(status) =>
                  updateMutation.mutate({ id: subscription.id, status })
                }
              />
            ))}
            {subscriptions.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={canManage ? 8 : 7}>
                  No subscriptions found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>
    </AdminLayout>
  );
}

function SubscriptionRow({
  subscription,
  canManage,
  isSaving,
  onSave,
}: {
  subscription: AdminSubscription;
  canManage: boolean;
  isSaving: boolean;
  onSave: (status: string) => void;
}) {
  const [status, setStatus] = useState(subscription.status);
  const changed = status !== subscription.status;

  return (
    <tr>
      <td style={tdStyle}>
        <UserCell subscription={subscription} />
      </td>
      <td style={tdStyle}>{subscription.plan_name}</td>
      <td style={tdStyle}>
        <BillingStatusBadge status={subscription.status} />
      </td>
      <td style={tdStyle}>{formatAdminDate(subscription.trial_ends_at)}</td>
      <td style={tdStyle}>{formatAdminDate(subscription.current_period_end)}</td>
      <td style={tdStyle}>{subscription.provider}</td>
      <td style={tdStyle}>{maskProviderId(subscription.provider_subscription_id)}</td>
      {canManage && (
        <td style={tdStyle}>
          <div style={manageStyle}>
            <select
              value={status}
              onChange={(event) => setStatus(event.target.value)}
              style={selectStyle}
            >
              {SUBSCRIPTION_STATUSES.map((item) => (
                <option key={item} value={item}>
                  {item.replace("_", " ")}
                </option>
              ))}
            </select>
            <AdminButton
              tone="secondary"
              disabled={!changed || isSaving}
              onClick={() => onSave(status)}
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

function UserCell({ subscription }: { subscription: AdminSubscription }) {
  if (!subscription.user) return <span style={mutedTextStyle}>Deleted user</span>;
  return (
    <div>
      <div style={strongTextStyle}>{subscription.user.name}</div>
      <div style={mutedTextStyle}>{subscription.user.email}</div>
    </div>
  );
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

const manageStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
};

const selectStyle: CSSProperties = {
  minHeight: 38,
  borderRadius: 8,
  border: "1px solid oklch(86% 0.018 245)",
  padding: "0 10px",
  background: "white",
  color: "oklch(20% 0.055 245)",
  fontFamily: "inherit",
  fontSize: 13,
  fontWeight: 750,
  textTransform: "capitalize",
};
