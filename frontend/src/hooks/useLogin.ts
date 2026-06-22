"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/auth-api";
import { getApiErrorCode } from "@/lib/errors";
import { setPendingVerification } from "@/lib/pending-verification";
import { useAuthStore } from "@/store/authStore";
import type { LoginInput } from "@/lib/validators/auth";

export function useLogin() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const setToken = useAuthStore((s) => s.setToken);

  return useMutation({
    mutationFn: async (data: LoginInput) => {
      const token = await authApi.login(data);
      // Save token first, then fetch /me with it
      setToken(token.access_token);
      const me = await authApi.me();
      return me;
    },
    onSuccess: (me) => {
      // Wipe any previous user's cached queries, then seed the current user's
      // ["me"] so destination pages render fresh data instead of bouncing on a
      // stale diagnosis_completed value.
      queryClient.clear();
      queryClient.setQueryData(["me"], me);
      if (!me.diagnosis_completed) {
        router.push("/diagnosis");
      } else {
        // Diagnosis done — always land on the dashboard. Verified (no-plan)
        // users see the NoEnrollmentView plan cards there and choose from the
        // locked dashboard, matching the post-diagnosis result-page flow (#126).
        // Never jump straight to /pricing.
        router.push("/dashboard");
      }
    },
    onError: (error, variables) => {
      // Correct password but unverified email → route to the verify screen.
      if (getApiErrorCode(error) === "email_unverified") {
        setPendingVerification(variables.email);
        router.push(`/verify-email?email=${encodeURIComponent(variables.email)}`);
      }
    },
  });
}
