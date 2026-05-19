/**
 * Typed client for the new daily-sessions REST API (Phase 3+).
 *
 * Backend mounts the routes under `/api/sessions`. Gated by both the
 * backend `use_new_session_flow` flag and the frontend
 * `NEXT_PUBLIC_USE_NEW_SESSION_FLOW`. When either is off, the endpoints
 * return 404 — callers should check `isSessionsFlowEnabled()` before
 * navigating to any /sessions/* route.
 */

import { api } from "./api";

// ── Feature flag ───────────────────────────────────────────────────

export function isSessionsFlowEnabled(): boolean {
  return process.env.NEXT_PUBLIC_USE_NEW_SESSION_FLOW === "true";
}

// ── Status enums (must match backend exactly) ──────────────────────

export type SessionStatus = "in_progress" | "completed" | "abandoned";
export type AttemptStatus = "pending" | "submitted" | "evaluated";
export type CourseLength = "24w" | "48w";

// ── Schemas ────────────────────────────────────────────────────────

export interface ActivityPreferences {
  allow_read?: boolean;
  allow_write?: boolean;
  allow_listen?: boolean;
  allow_speak?: boolean;
}

export interface SessionStartRequest {
  day_id: string;
  course_length: CourseLength;
  tasks_per_day: 2 | 3 | 4;
  preferences?: ActivityPreferences;
}

export interface AttemptSkeleton {
  sequence: number;
  archetype_id: string;
  is_mandatory: boolean;
  status: AttemptStatus;
}

export interface SessionStartResponse {
  session_id: string;
  day_id: string;
  course_length: CourseLength;
  status: SessionStatus;
  is_first_attempt: boolean;
  started_at: string;
  attempts: AttemptSkeleton[];
}

export interface NextActivityResponse {
  sequence: number;
  archetype_id: string;
  is_mandatory: boolean;
  status: AttemptStatus;
  ui_widget: string;
  task_content: Record<string, unknown>;
}

export interface SubmitActivityRequest {
  user_response: Record<string, unknown>;
}

export interface MistakeRead {
  user_wrote?: string | null;
  issue: string;
  correction?: string | null;
  rule?: string | null;
  sub_skills_affected: string[];
}

export interface FeedbackRead {
  score: number;
  summary: string;
  did_well: string[];
  mistakes: MistakeRead[];
  next_tip: string | null;
  sub_skill_breakdown: Record<string, number>;
}

export interface EvaluationRead {
  raw_score: number;
  rubric_scores: Record<string, number>;
  base_reward: number;
  weighted_points: Record<string, number>;
  evaluator_notes: string | null;
}

export interface SubmitActivityResponse {
  sequence: number;
  status: AttemptStatus;
  evaluation: EvaluationRead;
  feedback: FeedbackRead;
}

export interface SessionScorecardRead {
  session_id: string;
  points_earned: Record<string, number>;
  subskill_totals_after: Record<string, number>;
  dashboard_after: Record<string, number>;
  skill_labels: Record<string, string>;
  completed_at: string;
  points_applied: boolean;
}

// ── Endpoints ──────────────────────────────────────────────────────

export const sessionsApi = {
  start: (payload: SessionStartRequest) =>
    api
      .post<SessionStartResponse>("/api/sessions/start", payload)
      .then((r) => r.data),

  startToday: () =>
    api
      .post<SessionStartResponse>("/api/sessions/start-today")
      .then((r) => r.data),

  nextActivity: (sessionId: string) =>
    api
      .get<NextActivityResponse>(`/api/sessions/${sessionId}/next-activity`)
      .then((r) => r.data),

  submit: (sessionId: string, sequence: number, payload: SubmitActivityRequest) =>
    api
      .post<SubmitActivityResponse>(
        `/api/sessions/${sessionId}/activities/${sequence}/submit`,
        payload,
      )
      .then((r) => r.data),

  complete: (sessionId: string) =>
    api
      .post<SessionScorecardRead>(`/api/sessions/${sessionId}/complete`)
      .then((r) => r.data),

  getScorecard: (sessionId: string) =>
    api
      .get<SessionScorecardRead>(`/api/sessions/${sessionId}/scorecard`)
      .then((r) => r.data),
};
