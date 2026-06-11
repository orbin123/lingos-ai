"use client";

import { useRouter } from "next/navigation";
import { useAccessState } from "@/hooks/useAccessState";

/**
 * UX gate for premium widgets: renders children normally while the user has
 * access (trial/active/legacy), and disabled with an "Upgrade to continue"
 * overlay once expired/cancelled. The backend 402 on premium endpoints is
 * the real enforcement — this only keeps the UI honest.
 */
export function AccessGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { accessState } = useAccessState();

  const blocked = accessState === "expired" || accessState === "cancelled";
  if (!blocked) return <>{children}</>;

  return (
    <div style={{ position: "relative" }}>
      <div
        aria-hidden
        style={{ pointerEvents: "none", opacity: 0.45, filter: "saturate(0.6)" }}
      >
        {children}
      </div>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: 12,
          background: "rgba(255,255,255,0.35)",
        }}
      >
        <button
          onClick={() => router.push("/pricing")}
          style={{
            border: "none",
            borderRadius: 10,
            padding: "12px 20px",
            fontSize: 14,
            fontWeight: 700,
            cursor: "pointer",
            color: "white",
            background: "oklch(48% 0.17 240)",
            boxShadow: "0 6px 18px rgba(50,100,220,0.3)",
          }}
        >
          Upgrade to continue
        </button>
      </div>
    </div>
  );
}
