"use client";

/**
 * /auth/callback
 *
 * After Google OAuth the backend redirects here with:
 *   ?next=dashboard|diagnosis|profile   (and ?error=... on failure)
 *
 * The access token is NEVER passed in the URL (audit D2). The backend sets an
 * httpOnly refresh cookie on the OAuth redirect; this page mints a short-lived
 * access token from it via /auth/refresh, then redirects to the right page.
 */

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { api } from "@/lib/api";

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<CallbackLoading />}>
      <AuthCallbackInner />
    </Suspense>
  );
}

function AuthCallbackInner() {
  const router = useRouter();
  const params = useSearchParams();
  const setToken = useAuthStore((s) => s.setToken);

  useEffect(() => {
    const next = params.get("next") ?? "dashboard";
    const error = params.get("error");

    if (error) {
      if (next === "profile") {
        router.replace(`/profile?error=${encodeURIComponent(error)}`);
      } else {
        router.replace("/login?error=google_failed");
      }
      return;
    }

    let cancelled = false;

    // Mint an access token from the httpOnly refresh cookie the backend set on
    // the OAuth redirect (no token rides in the URL). withCredentials sends the
    // cookie; the response carries the short-lived access token.
    (async () => {
      try {
        const res = await api.post<{ access_token: string }>(
          "/auth/refresh",
          {},
          { withCredentials: true },
        );
        if (cancelled) return;
        setToken(res.data.access_token);
        router.replace(`/${next}`);
      } catch {
        if (cancelled) return;
        router.replace("/login?error=google_failed");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [params, router, setToken]);

  return (
    <CallbackLoading />
  );
}

function CallbackLoading() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <p className="text-sm text-slate-500">Signing you in...</p>
    </div>
  );
}
