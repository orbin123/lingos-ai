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
  type DashboardStartResponse,
  type DashboardTodayPlanResponse,
  type SessionScorecardRead,
  type SessionStartRequest,
  type SessionStartResponse,
  type SubmitActivityRequest,
  type SubmitActivityResponse,
  type NextActivityResponse,
} from "@/lib/sessions-api";
import { authoringStartPath, isAuthoringChatEnabled } from "@/lib/authoring-chat";
import { useSessionStore } from "@/store/sessionStore";


// ── Query keys ─────────────────────────────────────────────────────

export const sessionsKeys = {
  all: ["sessions"] as const,
  todayPlan: () => [...sessionsKeys.all, "today-plan"] as const,
  byId: (sessionId: string) => [...sessionsKeys.all, sessionId] as const,
  nextActivity: (sessionId: string) =>
    [...sessionsKeys.byId(sessionId), "next-activity"] as const,
  scorecard: (sessionId: string) =>
    [...sessionsKeys.byId(sessionId), "scorecard"] as const,
};


// ── Dashboard daily plan ───────────────────────────────────────────

export function useTodaySessionPlan() {
  return useQuery<DashboardTodayPlanResponse>({
    queryKey: sessionsKeys.todayPlan(),
    queryFn: sessionsApi.todayPlan,
    refetchOnWindowFocus: false,
    retry: false,
  });
}

export function useStartOrContinueTodaySession() {
  const queryClient = useQueryClient();
  const setSession = useSessionStore((s) => s.setSession);

  return useMutation<DashboardStartResponse, Error, void>({
    mutationFn: sessionsApi.startOrContinueToday,
    onSuccess: (session) => {
      if (session.session_id) {
        setSession({
          session_id: session.session_id,
          day_id: session.day_id,
          course_length: session.day_id.startsWith("day_48_") ? "48w" : "24w",
          status: session.status ?? "in_progress",
          is_first_attempt: session.mode === "start",
          started_at: new Date().toISOString(),
          attempts: session.activities.map((activity) => ({
            sequence: activity.sequence,
            archetype_id: activity.archetype_id,
            archetype_name: activity.archetype_name,
            is_mandatory: activity.is_mandatory,
            status: activity.status,
          })),
        });
      }
      queryClient.setQueryData(sessionsKeys.todayPlan(), session);
    },
  });
}


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


// ── Learning (chat) session start ─────────────────────────────────

/**
 * Open a chat-driven learning session layered on the user's V2
 * DailySession for today. The backend either resumes an existing chat
 * envelope or creates a fresh one (and the V2 DailySession behind it).
 *
 * Used by the dashboard "Start session" button — the response gives the
 * UUID the chat page opens its WebSocket against.
 */
export interface StartLearningSessionResponse {
  session_id: string;
  daily_session_id: number;
  topic: string;
  skill_name: string;
  task_type: string;
  message: string;
}

export interface StartLearningSessionInput {
  week?: number;
  day?: number;
}

export function useStartLearningSession() {
  return useMutation<StartLearningSessionResponse, Error, StartLearningSessionInput | void>({
    mutationFn: async (input) => {
      const { api } = await import("@/lib/api");
      if (isAuthoringChatEnabled()) {
        const response = await api.post<StartLearningSessionResponse>(
          authoringStartPath(input || undefined),
          {},
        );
        return response.data;
      }
      const response = await api.post<StartLearningSessionResponse>(
        "/api/learning/sessions/start",
        {},
      );
      return response.data;
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
