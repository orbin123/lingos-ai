"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/auth-api";
import { setPendingVerification } from "@/lib/pending-verification";
import type { RegisterInput } from "@/lib/validators/auth";

export function useRegister() {
  const router = useRouter();

  return useMutation({
    // No auto-login: the account starts unverified, so signup hands the
    // user to the verify-email screen where the OTP completes login.
    mutationFn: (data: RegisterInput) => authApi.signup(data),
    onSuccess: (res) => {
      setPendingVerification(res.email);
      router.push(`/verify-email?email=${encodeURIComponent(res.email)}`);
    },
  });
}
