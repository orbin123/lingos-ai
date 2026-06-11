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

export const paymentsApi = {
  createOrder: (planId: string) =>
    api
      .post<CreateOrderOut>("/api/payments/create-order", { plan_id: planId })
      .then((r) => r.data),

  verify: (payload: PaymentVerifyIn) =>
    api
      .post<EntitlementRead>("/api/payments/verify", payload)
      .then((r) => r.data),
};
