"use client";

import { useCallback } from "react";
import type { CreateOrderOut, PaymentVerifyIn } from "@/lib/payments-api";

interface RazorpaySuccessResponse {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
}

interface RazorpayInstance {
  open: () => void;
  on: (event: "payment.failed", handler: (resp: unknown) => void) => void;
}

interface RazorpayOptions {
  key: string;
  amount: number;
  currency: string;
  name: string;
  description: string;
  order_id: string;
  prefill: { name?: string; email?: string };
  handler: (response: RazorpaySuccessResponse) => void;
  modal: { ondismiss: () => void };
  theme: { color: string };
}

declare global {
  interface Window {
    Razorpay?: new (options: RazorpayOptions) => RazorpayInstance;
  }
}

const CHECKOUT_SRC = "https://checkout.razorpay.com/v1/checkout.js";

let scriptPromise: Promise<void> | null = null;

function loadCheckoutScript(): Promise<void> {
  if (window.Razorpay) return Promise.resolve();
  if (!scriptPromise) {
    scriptPromise = new Promise<void>((resolve, reject) => {
      const script = document.createElement("script");
      script.src = CHECKOUT_SRC;
      script.onload = () => resolve();
      script.onerror = () => {
        scriptPromise = null;
        reject(new Error("Could not load the payment widget."));
      };
      document.body.appendChild(script);
    });
  }
  return scriptPromise;
}

export interface OpenCheckoutArgs {
  order: CreateOrderOut;
  user: { name?: string; email?: string } | undefined;
  /** Checkout succeeded client-side; verify server-side next. */
  onSuccess: (payload: PaymentVerifyIn) => void;
  /** Payment failed or the modal was dismissed — nothing was charged. */
  onFailure: (message: string) => void;
}

/** Loads checkout.js once and opens the Razorpay modal for an order. */
export function useRazorpayCheckout() {
  const openCheckout = useCallback(
    async ({ order, user, onSuccess, onFailure }: OpenCheckoutArgs) => {
      try {
        await loadCheckoutScript();
      } catch (error) {
        onFailure(
          error instanceof Error
            ? error.message
            : "Could not load the payment widget.",
        );
        return;
      }
      if (!window.Razorpay) {
        onFailure("Could not load the payment widget.");
        return;
      }

      const instance = new window.Razorpay({
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: "LingosAI",
        description: order.plan_name,
        order_id: order.order_id,
        prefill: { name: user?.name, email: user?.email },
        handler: (response) =>
          onSuccess({
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          }),
        modal: {
          ondismiss: () =>
            onFailure("Payment was not completed — you have not been charged."),
        },
        theme: { color: "#0070C4" },
      });
      instance.on("payment.failed", () =>
        onFailure("Payment failed — you have not been charged. Please retry."),
      );
      instance.open();
    },
    [],
  );

  return { openCheckout };
}
