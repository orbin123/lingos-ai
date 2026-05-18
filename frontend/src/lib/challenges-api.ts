import { api } from "./api";

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
  completed_at: string | null;
  expires_at: string;
  task_payload: Record<string, unknown>;
  response_payload: Record<string, unknown> | null;
  overall_score: number | null;
  section_scores: Record<string, number> | null;
  passed: boolean | null;
  evaluation_report: Record<string, unknown> | null;
  feedback_report: Record<string, unknown> | null;
  created_at: string;
}

export interface ChallengeSpeakingUploadRead {
  prompt_id: string;
  audio_url: string;
  audio_storage_key: string;
  content_type: string;
  size_bytes: number;
}

export const challengesApi = {
  list: () => api.get<ChallengeListItem[]>("/api/v1/challenges").then((r) => r.data),

  detail: (slug: string) =>
    api.get<ChallengeDetailRead>(`/api/v1/challenges/${slug}`).then((r) => r.data),

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
