"use client";

/**
 * Legacy scorecard URL — redirects to the chat session where the
 * day-level scorecard is shown as a continuation of the conversation.
 */

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";

import { useRequireAuth } from "@/hooks/useRequireAuth";


export default function SessionScorecardRedirectPage() {
  const params = useParams<{ sessionId: string }>();
  const sessionId = params.sessionId;
  const router = useRouter();
  useRequireAuth();

  useEffect(() => {
    if (sessionId) {
      router.replace(`/task/chat/${sessionId}`);
    }
  }, [sessionId, router]);

  return (
    <main
      style={{
        maxWidth: 1180,
        margin: "20px auto",
        padding: "0 clamp(18px, 3vw, 32px)",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
      }}
    >
      <p>Opening your session&hellip;</p>
    </main>
  );
}
