"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/auth-api";
import { clearPendingVerification } from "@/lib/pending-verification";
import { useAuthStore } from "@/store/authStore";

export function useVerifyEmail() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const setToken = useAuthStore((s) => s.setToken);

  return useMutation({
    mutationFn: (data: { email: string; code: string }) =>
      authApi.verifyEmail(data),
    onSuccess: (res) => {
      setToken(res.access_token);
      clearPendingVerification();
      // Drop any previous user's cached queries (the QueryClient lives for the
      // whole browser session). Otherwise the intro page reads a stale ["me"]
      // and bounces dashboard → diagnosis. Clearing before navigating means the
      // intro page mounts with an empty cache and fetches a fresh ["me"].
      queryClient.clear();
      // Welcome the freshly verified learner before the placement test
      router.push("/diagnosis/intro");
    },
  });
}
