"use client";

/**
 * Terminal scorecard page.
 *
 * Reads the persisted scorecard for `sessionId`. Prefers the in-memory
 * snapshot from `sessionStore` (already populated by the complete mutation)
 * and falls back to `useSessionScorecard` for a clean fetch when the user
 * lands here directly (e.g. via URL).
 */

import { useParams, useRouter } from "next/navigation";

import { SessionScorecard } from "@/components/sessions/SessionScorecard";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useSessionScorecard } from "@/hooks/useSessionsFlow";
import { markScorecardViewed } from "@/lib/daily-session-entry";
import { useSessionStore } from "@/store/sessionStore";


export default function SessionScorecardPage() {
  const params = useParams<{ sessionId: string }>();
  const sessionId = params.sessionId;
  const router = useRouter();
  useRequireAuth();

  const cached = useSessionStore((s) => s.scorecard);
  const cachedMatches = cached?.session_id === sessionId;
  // Skip the fetch when we already have the right scorecard cached.
  const query = useSessionScorecard(cachedMatches ? null : sessionId);

  const scorecard = cachedMatches ? cached : query.data;

  return (
    <main
      style={{
        maxWidth: 1180,
        margin: "20px auto",
        padding: "0 clamp(18px, 3vw, 32px)",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
      }}
    >
      {!scorecard && query.isLoading && <p>Loading scorecard&hellip;</p>}
      {!scorecard && query.error && (
        <p style={{ color: "oklch(35% 0.18 25)" }}>
          {(query.error as Error).message}
        </p>
      )}
      {scorecard && (
        <SessionScorecard
          scorecard={scorecard}
          onDone={() => {
            markScorecardViewed(scorecard.session_id);
            useSessionStore.getState().clear();
            router.push("/dashboard");
          }}
        />
      )}
    </main>
  );
}
