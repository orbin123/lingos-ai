"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { api } from "@/lib/api";

interface StartSessionResponse {
  session_id: string;
  topic: string;
  skill_name: string;
  task_type: string;
  user_task_id?: number | null;
  message: string;
}

export default function ChatEntryPage() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleStart() {
    setBusy(true);
    setError(null);
    try {
      const taskIdParam =
        typeof window !== "undefined"
          ? new URLSearchParams(window.location.search).get("id")
          : null;
      const taskId = taskIdParam ? Number(taskIdParam) : null;
      const res = await api.post<StartSessionResponse>(
        "/api/learning/sessions/start",
        taskId !== null && Number.isFinite(taskId) && taskId > 0
          ? { user_task_id: taskId }
          : {},
      );
      router.push(`/task/chat/${res.data.session_id}`);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } }; message?: string })
          ?.response?.data?.detail ||
        (err as { message?: string })?.message ||
        "Could not start a session.";
      setError(detail);
      setBusy(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        background: "oklch(91% 0.04 245)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
        color: "oklch(18% 0.06 240)",
      }}
    >
      <div
        aria-hidden
        style={{
          position: "fixed",
          inset: 0,
          pointerEvents: "none",
          backgroundImage:
            "radial-gradient(circle, rgba(90,130,210,0.13) 1px, transparent 1px)",
          backgroundSize: "22px 22px",
          zIndex: 0,
        }}
      />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          maxWidth: 460,
          width: "100%",
          background: "white",
          borderRadius: 22,
          padding: "32px 28px",
          border: "1.5px solid rgba(255,255,255,0.92)",
          boxShadow: "0 12px 40px rgba(80,110,180,0.18)",
          textAlign: "center",
        }}
      >
        <div
          style={{
            width: 56,
            height: 56,
            borderRadius: 14,
            margin: "0 auto 18px",
            background: "oklch(52% 0.18 240)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            fontWeight: 800,
            fontSize: 22,
            letterSpacing: "-0.02em",
            boxShadow: "0 6px 20px rgba(60,100,200,0.32)",
          }}
        >
          L
        </div>
        <div
          style={{
            fontSize: 22,
            fontWeight: 800,
            letterSpacing: "-0.02em",
            color: "oklch(20% 0.09 245)",
            marginBottom: 8,
          }}
        >
          Ready for today&apos;s activities?
        </div>
        <div
          style={{
            fontSize: 14,
            color: "oklch(45% 0.07 240)",
            lineHeight: 1.6,
            marginBottom: 22,
          }}
        >
          We&apos;ll teach today&apos;s topic once, then complete your daily
          activities in this chat.
        </div>

        {error && (
          <div
            style={{
              fontSize: 13,
              color: "oklch(35% 0.18 25)",
              background: "oklch(96% 0.05 25)",
              border: "1px solid oklch(85% 0.1 25)",
              borderRadius: 12,
              padding: "10px 12px",
              marginBottom: 14,
              textAlign: "left",
            }}
          >
            {error}
          </div>
        )}

        <button
          onClick={handleStart}
          disabled={busy}
          style={{
            width: "100%",
            padding: "14px 0",
            borderRadius: 14,
            border: "none",
            background: "oklch(20% 0.09 245)",
            color: "white",
            fontSize: 14.5,
            fontWeight: 700,
            cursor: busy ? "not-allowed" : "pointer",
            opacity: busy ? 0.6 : 1,
            boxShadow: "0 6px 20px rgba(20,40,90,0.25)",
            fontFamily: "inherit",
          }}
        >
          {busy ? "Preparing your session…" : "Start Session"}
        </button>

        <button
          onClick={() => router.push("/dashboard")}
          style={{
            marginTop: 10,
            width: "100%",
            padding: "10px 0",
            borderRadius: 12,
            border: "none",
            background: "transparent",
            color: "oklch(45% 0.07 240)",
            fontSize: 13,
            fontWeight: 600,
            cursor: "pointer",
            fontFamily: "inherit",
          }}
        >
          Back to dashboard
        </button>
      </div>
    </div>
  );
}
