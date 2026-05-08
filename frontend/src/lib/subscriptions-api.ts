import { api } from "./api";

export interface NotificationSettings {
  daily_practice_reminder: boolean;
  streak_reminder: boolean;
  weekly_progress_email: boolean;
  feature_announcements: boolean;
}

export interface PurchaseRead {
  id: number;
  user_id: number;
  plan_id: string;
  plan_name: string;
  amount_paid: number;
  currency: "INR" | string;
  status: "paid" | "paused" | string;
  created_at: string;
}

export const subscriptionsApi = {
  me: () =>
    api.get<PurchaseRead | null>("/api/subscriptions/me").then((r) => r.data),

  purchase: (planId: string) =>
    api
      .post<PurchaseRead>("/api/subscriptions/purchase", { plan_id: planId })
      .then((r) => r.data),

  pause: () =>
    api.patch<PurchaseRead>("/api/subscriptions/me/pause").then((r) => r.data),

  updateNotifications: (data: Partial<NotificationSettings>) =>
    api
      .patch<NotificationSettings>("/api/users/me/notifications", data)
      .then((r) => r.data),

  deleteAccount: () => api.delete<void>("/api/users/me"),
};
