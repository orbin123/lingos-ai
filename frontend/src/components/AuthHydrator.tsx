"use client";

import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "@/store/authStore";

/**
 * Runs once on app load. Reads token from localStorage into Zustand store.
 * Without this, the store starts empty on every page refresh.
 *
 * Also clears the React Query cache on logout. The QueryClient lives for the
 * whole browser session, so without this a logged-out user would leave their
 * cached ["me"] (etc.) behind for the next account signing in/up in the same
 * tab — which caused post-OTP pages to read a stale diagnosis_completed and
 * bounce dashboard → diagnosis. (The login/verify "in" direction clears the
 * cache in useLogin / useVerifyEmail.)
 */
export function AuthHydrator() {
  const hydrate = useAuthStore((s) => s.hydrate);
  const token = useAuthStore((s) => s.token);
  const queryClient = useQueryClient();
  const prevToken = useRef(token);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    // token went from a value → null = logout: drop all stale user data.
    if (prevToken.current && !token) queryClient.clear();
    prevToken.current = token;
  }, [token, queryClient]);

  return null;  // renders nothing — pure side-effect component
}
