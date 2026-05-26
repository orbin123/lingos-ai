/**
 * Session state — current session id, last per-activity feedback, terminal
 * scorecard. In-memory only (cleared on page refresh) following the pattern
 * of the legacy `taskStore`.
 *
 * The session page reads from React Query for source-of-truth server state;
 * this store holds short-lived UI state that doesn't belong in the URL or
 * in the cache (e.g. "we just submitted activity 2 — show its feedback").
 */

import { create } from "zustand";
import type {
  FeedbackRead,
  EvaluationRead,
  SessionScorecardRead,
  SessionStartResponse,
} from "@/lib/sessions-api";

interface ActivityFeedbackSnapshot {
  sequence: number;
  archetype_id: string;
  feedback: FeedbackRead;
  evaluation: EvaluationRead;
}

interface SessionState {
  session: SessionStartResponse | null;
  lastFeedback: ActivityFeedbackSnapshot | null;
  scorecard: SessionScorecardRead | null;

  setSession: (session: SessionStartResponse) => void;
  setLastFeedback: (snapshot: ActivityFeedbackSnapshot) => void;
  setScorecard: (scorecard: SessionScorecardRead) => void;
  clear: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  session: null,
  lastFeedback: null,
  scorecard: null,

  setSession: (session) => set({ session, lastFeedback: null, scorecard: null }),
  setLastFeedback: (lastFeedback) => set({ lastFeedback }),
  setScorecard: (scorecard) => set({ scorecard }),
  clear: () => set({ session: null, lastFeedback: null, scorecard: null }),
}));
