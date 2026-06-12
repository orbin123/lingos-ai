"use client";

import type { CSSProperties } from "react";
import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ChevronLeft } from "lucide-react";
import { LandingNavbar } from "@/components/layout/LandingNavbar";
import { IeltsResultsPanel } from "@/components/challenges/IeltsResultsPanel";
import { challengesApi } from "@/lib/challenges-api";
import { useRequireAuth } from "@/hooks/useRequireAuth";

export default function ChallengeAttemptResultPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { isReady } = useRequireAuth();
  const attemptId = Number(params.id);

  const attemptQuery = useQuery({
    queryKey: ["challenge-attempt", attemptId],
    queryFn: () => challengesApi.getAttempt(attemptId),
    enabled: isReady && Number.isFinite(attemptId),
  });

  const attempt = attemptQuery.data ?? null;
  const isComplete =
    attempt?.status === "completed" || attempt?.status === "timed_out";

  // The results page only makes sense for a finished attempt. If the timer is
  // still running, send the user back to the exam to keep going.
  useEffect(() => {
    if (attempt && !isComplete) {
      router.replace(`/challenges/ielts/attempt/${attemptId}`);
    }
  }, [attempt, isComplete, attemptId, router]);

  if (!isReady) return null;

  return (
    <div style={pageWrapperStyle}>
      <div aria-hidden style={dotGridStyle} />
      <LandingNavbar variant="minimal" />
      <main style={mainStyle}>
        <button
          type="button"
          onClick={() => router.push("/challenges")}
          style={backLinkStyle}
        >
          <ChevronLeft size={18} aria-hidden />
          Challenges
        </button>

        {attemptQuery.isLoading && <div style={panelStyle}>Loading results…</div>}
        {attemptQuery.isError && (
          <div style={panelStyle}>Could not load these results.</div>
        )}
        {isComplete && attempt && <IeltsResultsPanel attempt={attempt} />}
      </main>
    </div>
  );
}

/* ─── Styles ─── */

const pageWrapperStyle: CSSProperties = {
  minHeight: "100vh",
  fontFamily: "'Plus Jakarta Sans', sans-serif",
  background: "oklch(91% 0.04 245)",
  position: "relative",
};

const dotGridStyle: CSSProperties = {
  position: "fixed",
  inset: 0,
  pointerEvents: "none",
  backgroundImage:
    "radial-gradient(circle, rgba(90,130,210,0.13) 1px, transparent 1px)",
  backgroundSize: "22px 22px",
  zIndex: 0,
};

const mainStyle: CSSProperties = {
  position: "relative",
  zIndex: 1,
  maxWidth: 1080,
  margin: "0 auto",
  padding: "96px 20px 76px",
};

const backLinkStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  background: "none",
  border: "none",
  color: "#0f172a",
  fontSize: 14,
  fontWeight: 600,
  cursor: "pointer",
  padding: 0,
  marginBottom: 24,
};

const panelStyle: CSSProperties = {
  background: "rgba(255,255,255,0.85)",
  backdropFilter: "blur(18px)",
  WebkitBackdropFilter: "blur(18px)",
  border: "1.5px solid rgba(255,255,255,0.92)",
  borderRadius: 22,
  padding: 28,
  boxShadow: "0 4px 24px rgba(80,110,180,0.1)",
  color: "#4a6880",
  fontWeight: 600,
};
