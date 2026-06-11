"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/auth-api";
import { clearPendingVerification } from "@/lib/pending-verification";
import { useAuthStore } from "@/store/authStore";

export function useVerifyEmail() {
  const router = useRouter();
  const setToken = useAuthStore((s) => s.setToken);

  return useMutation({
    mutationFn: (data: { email: string; code: string }) =>
      authApi.verifyEmail(data),
    onSuccess: (res) => {
      setToken(res.access_token);
      clearPendingVerification();
      // Fresh accounts always start with diagnosis
      router.push("/diagnosis");
    },
  });
}
