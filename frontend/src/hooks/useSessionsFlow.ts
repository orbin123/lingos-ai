/**
 * React Query hooks for the new daily-sessions REST flow (Phase 6).
 *
 * One file because the hooks share a tightly-coupled lifecycle:
 *   useStartSession → useNextActivity → useSubmitActivity (loop)
 *                                     → useCompleteSession → useSessionScorecard
 *
 * Components import only what they need. The query cache is keyed by
 * `session_id` so navigation back/forward keeps state consistent.
 */

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  sessionsApi,
  type SessionScorecardRead,
  type SessionStartRequest,
  type SessionStartResponse,
  type SubmitActivityRequest,
  type SubmitActivityResponse,
  type NextActivityResponse,
} from "@/lib/sessions-api";
import { useSessionStore } from "@/store/sessionStore";


// ── Query keys ─────────────────────────────────────────────────────

export const sessionsKeys = {
  all: ["sessions"] as const,
  byId: (sessionId: string) => [...sessionsKeys.all, sessionId] as const,
  nextActivity: (sessionId: string) =>
    [...sessionsKeys.byId(sessionId), "next-activity"] as const,
  scorecard: (sessionId: string) =>
    [...sessionsKeys.byId(sessionId), "scorecard"] as const,
};


// ── Start ──────────────────────────────────────────────────────────

export function useStartSession() {
  const setSession = useSessionStore((s) => s.setSession);
  return useMutation<SessionStartResponse, Error, SessionStartRequest>({
    mutationFn: (payload) => sessionsApi.start(payload),
    onSuccess: (session) => setSession(session),
  });
}


// ── Start today (find-or-create) ───────────────────────────────────

/**
 * Resolves today's session from the user's stored preferences — no
 * day_id or course_length required from the caller. Returns the
 * existing session if one is in progress / completed for today,
 * otherwise creates a fresh one.
 *
 * The dashboard's primary entry point. Direct callers needing finer
 * control (admin tooling, tests) keep using `useStartSession`.
 */
export function useStartTodaySession() {
  const setSession = useSessionStore((s) => s.setSession);
  return useMutation<SessionStartResponse, Error, void>({
    mutationFn: () => sessionsApi.startToday(),
    onSuccess: (session) => setSession(session),
  });
}


// ── Next activity ──────────────────────────────────────────────────

export function useNextActivity(sessionId: string | null, options?: {
  enabled?: boolean;
}) {
  return useQuery<NextActivityResponse>({
    queryKey: sessionId ? sessionsKeys.nextActivity(sessionId) : ["sessions", "noop"],
    queryFn: () => sessionsApi.nextActivity(sessionId!),
    enabled: !!sessionId && (options?.enabled ?? true),
    // Refetch when invalidated by submit; don't poll on focus.
    refetchOnWindowFocus: false,
    retry: false,
  });
}


// ── Submit ─────────────────────────────────────────────────────────

export function useSubmitActivity(sessionId: string | null) {
  const queryClient = useQueryClient();
  const setLastFeedback = useSessionStore((s) => s.setLastFeedback);

  return useMutation<
    SubmitActivityResponse,
    Error,
    { sequence: number; archetype_id: string; payload: SubmitActivityRequest }
  >({
    mutationFn: ({ sequence, payload }) =>
      sessionsApi.submit(sessionId!, sequence, payload),
    onSuccess: (data, variables) => {
      // Snapshot the feedback for the inline card; next-activity is
      // intentionally NOT auto-refetched here — the page advances on user
      // action (after they've read the feedback).
      setLastFeedback({
        sequence: variables.sequence,
        archetype_id: variables.archetype_id,
        feedback: data.feedback,
      });
    },
    onSettled: () => {
      // Invalidate so the next call to useNextActivity returns the new
      // pending attempt (or 409 → caller flips to "complete" mode).
      if (sessionId) {
        queryClient.invalidateQueries({
          queryKey: sessionsKeys.nextActivity(sessionId),
        });
      }
    },
  });
}


// ── Complete ───────────────────────────────────────────────────────

export function useCompleteSession(sessionId: string | null) {
  const setScorecard = useSessionStore((s) => s.setScorecard);
  const queryClient = useQueryClient();

  return useMutation<SessionScorecardRead, Error, void>({
    mutationFn: () => sessionsApi.complete(sessionId!),
    onSuccess: (scorecard) => {
      setScorecard(scorecard);
      if (sessionId) {
        queryClient.setQueryData(sessionsKeys.scorecard(sessionId), scorecard);
      }
    },
  });
}


// ── Scorecard (read) ──────────────────────────────────────────────

export function useSessionScorecard(sessionId: string | null) {
  return useQuery<SessionScorecardRead>({
    queryKey: sessionId ? sessionsKeys.scorecard(sessionId) : ["sessions", "noop"],
    queryFn: () => sessionsApi.getScorecard(sessionId!),
    enabled: !!sessionId,
    refetchOnWindowFocus: false,
    retry: false,
  });
}
