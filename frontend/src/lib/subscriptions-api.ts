import { api } from "./api";

export interface NotificationSettings {
  daily_practice_reminder: boolean;
  streak_reminder: boolean;
  weekly_progress_email: boolean;
  feature_announcements: boolean;
}

export type AccessState =
  | "unverified"
  | "verified"
  | "trial"
  | "active"
  | "expired"
  | "cancelled";

export interface EntitlementRead {
  access_state: AccessState;
  subscription_status: string | null;
  plan_id: string | null;
  plan_name: string | null;
  amount: number | null;
  currency: string | null;
  trial_started_at: string | null;
  trial_ends_at: string | null;
  days_remaining: number | null;
  current_period_end: string | null;
}

export const subscriptionsApi = {
  me: () =>
    api.get<EntitlementRead>("/api/subscriptions/me").then((r) => r.data),

  selectPlan: (planId: string) =>
    api
      .post<EntitlementRead>("/api/subscriptions/select-plan", {
        plan_id: planId,
      })
      .then((r) => r.data),

  startTrial: () =>
    api
      .post<EntitlementRead>("/api/subscriptions/start-trial")
      .then((r) => r.data),

  cancel: () =>
    api.post<EntitlementRead>("/api/subscriptions/cancel").then((r) => r.data),

  // Legacy Purchase-row pause (schedule-only; does not affect access).
  pause: () => api.patch("/api/subscriptions/me/pause").then((r) => r.data),

  updateNotifications: (data: Partial<NotificationSettings>) =>
    api
      .patch<NotificationSettings>("/api/users/me/notifications", data)
      .then((r) => r.data),

  deleteAccount: () => api.delete<void>("/api/users/me"),
};
