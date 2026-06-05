import axios from "axios";

import { api } from "./api";

export interface ChallengesApiError {
  message: string;
  status?: number;
  attemptId?: number;
}

/** Parse FastAPI error bodies from challenge endpoints. */
export function getChallengesApiError(error: unknown): ChallengesApiError {
  if (!axios.isAxiosError(error)) {
    return {
      message: error instanceof Error ? error.message : "Request failed",
    };
  }

  const status = error.response?.status;
  const detail = error.response?.data?.detail;

  if (typeof detail === "object" && detail !== null) {
    const record = detail as { message?: string; attempt_id?: number };
    return {
      message: record.message ?? "Request failed",
      status,
      attemptId: record.attempt_id,
    };
  }

  if (typeof detail === "string" && detail.trim()) {
    return { message: detail, status };
  }

  if (status === 403) {
    return {
      message:
        "This level is locked. Pass the previous level with the required band to unlock it.",
      status,
    };
  }
  if (status === 409) {
    return {
      message: "You already have an attempt in progress for this level.",
      status,
    };
  }
  if (status === 429) {
    return {
      message: "Daily attempt limit reached. Try again tomorrow.",
      status,
    };
  }
  if (status === 500) {
    return {
      message:
        "Server error while starting the attempt. If this persists, run database migrations.",
      status,
    };
  }

  return {
    message: error.message || "Request failed",
    status,
  };
}

export type ChallengeAttemptStatus =
  | "in_progress"
  | "completed"
  | "abandoned"
  | "timed_out";

export interface ChallengeListItem {
  id: number;
  slug: string;
  name: string;
  short_description: string;
  icon: string | null;
  level_count: number;
}

export interface ChallengeLevelRead {
  id: number;
  level_number: number;
  name: string;
  time_limit_seconds: number;
  pass_threshold: number;
  config: Record<string, unknown>;
  unlocked: boolean;
  best_score: number | null;
  attempt_count: number;
  in_progress_attempt_id: number | null;
}

export interface ChallengeDetailRead {
  id: number;
  slug: string;
  name: string;
  short_description: string;
  rules_md: string;
  icon: string | null;
  levels: ChallengeLevelRead[];
}

export interface ChallengeAttemptRead {
  id: number;
  user_id: number;
  challenge_level_id: number;
  status: ChallengeAttemptStatus;
  started_at: string;
  timer_started_at: string | null;
  completed_at: string | null;
  expires_at: string | null;
  task_payload: Record<string, unknown>;
  response_payload: Record<string, unknown> | null;
  overall_score: number | null;
  section_scores: Record<string, number> | null;
  passed: boolean | null;
  evaluation_report: Record<string, unknown> | null;
  feedback_report: Record<string, unknown> | null;
  created_at: string;
  level_number: number | null;
  pass_threshold: number | null;
  time_limit_seconds: number | null;
}

export interface ChallengeSpeakingUploadRead {
  prompt_id: string;
  audio_url: string;
  audio_storage_key: string;
  content_type: string;
  size_bytes: number;
}

export interface ChallengeHistoryAttempt {
  id: number;
  challenge_level_id: number;
  level_number: number;
  level_name: string;
  status: ChallengeAttemptStatus;
  started_at: string;
  completed_at: string | null;
  expires_at: string | null;
  timer_started_at: string | null;
  overall_score: number | null;
  section_scores: Record<string, number> | null;
  passed: boolean | null;
  is_best_for_level: boolean;
  created_at: string;
}

export interface ChallengeHistoryRead {
  challenge_slug: string;
  challenge_name: string;
  attempts: ChallengeHistoryAttempt[];
}

export const challengesApi = {
  list: () => api.get<ChallengeListItem[]>("/api/v1/challenges").then((r) => r.data),

  detail: (slug: string) =>
    api.get<ChallengeDetailRead>(`/api/v1/challenges/${slug}`).then((r) => r.data),

  history: (slug: string) =>
    api.get<ChallengeHistoryRead>(`/api/v1/challenges/${slug}/history`).then((r) => r.data),

  getAttempt: (attemptId: number) =>
    api
      .get<ChallengeAttemptRead>(`/api/v1/challenge-attempts/${attemptId}`)
      .then((r) => r.data),

  startAttempt: (slug: string, levelNumber: number) =>
    api
      .post<ChallengeAttemptRead>(
        `/api/v1/challenges/${slug}/levels/${levelNumber}/attempts`,
      )
      .then((r) => r.data),

  beginAttempt: (attemptId: number) =>
    api
      .post<ChallengeAttemptRead>(`/api/v1/challenge-attempts/${attemptId}/begin`)
      .then((r) => r.data),

  saveResponses: (attemptId: number, responsePayload: Record<string, unknown>) =>
    api
      .patch<ChallengeAttemptRead>(`/api/v1/challenge-attempts/${attemptId}/responses`, {
        response_payload: responsePayload,
      })
      .then((r) => r.data),

  submitAttempt: (attemptId: number, responsePayload: Record<string, unknown>) =>
    api
      .post<ChallengeAttemptRead>(`/api/v1/challenge-attempts/${attemptId}/submit`, {
        response_payload: responsePayload,
      })
      .then((r) => r.data),

  uploadSpeakingTake: (
    attemptId: number,
    promptId: string,
    audioBlob: Blob,
    filename = "speaking.webm",
  ) => {
    const formData = new FormData();
    formData.append("audio", audioBlob, filename);
    return api
      .post<ChallengeSpeakingUploadRead>(
        `/api/v1/challenge-attempts/${attemptId}/speaking/${promptId}/upload`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } },
      )
      .then((r) => r.data);
  },

  getAttemptAudio: (audioUrl: string) =>
    api
      .get<Blob>(audioUrl, { responseType: "blob" })
      .then((r) => r.data),
};
