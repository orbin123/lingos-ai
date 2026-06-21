import { api } from "./api";
import type { EntitlementRead } from "./subscriptions-api";

export interface CreateOrderOut {
  order_id: string;
  amount: number; // paise, server-computed from the plan catalog
  currency: string;
  key_id: string;
  plan_id: string;
  plan_name: string;
}

export interface PaymentVerifyIn {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
}

export interface PaymentDetailRead {
  provider_payment_id: string | null;
  provider_order_id: string | null;
  amount: number; // rupees (catalog amount), not paise
  currency: string;
  status: string;
  method: string | null; // null until the webhook lands — render defensively
  paid_at: string | null;
  plan_id: string | null;
  plan_name: string | null;
  subscription_status: string | null;
  current_period_end: string | null;
}

export const paymentsApi = {
  createOrder: (planId: string) =>
    api
      .post<CreateOrderOut>("/api/payments/create-order", { plan_id: planId })
      .then((r) => r.data),

  verify: (payload: PaymentVerifyIn) =>
    api
      .post<EntitlementRead>("/api/payments/verify", payload)
      .then((r) => r.data),

  // Server-verified proof for the Payment Success page (user-scoped: a user
  // can only read their own order; another user's order → 404).
  byOrder: (orderId: string) =>
    api
      .get<PaymentDetailRead>(
        `/api/payments/by-order/${encodeURIComponent(orderId)}`,
      )
      .then((r) => r.data),

  // The current user's payments, newest first (user-scoped). Backs the
  // Settings → receipt entry point and the receipt list.
  mine: () =>
    api.get<PaymentDetailRead[]>("/api/payments/mine").then((r) => r.data),
};
