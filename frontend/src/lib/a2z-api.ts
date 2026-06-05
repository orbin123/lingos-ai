/**
 * API client for the A2Z Challenge endpoints.
 *
 * All calls use the shared axios `api` instance (JWT auth, base URL).
 */

import { api } from "./api";

// ── Types ─────────────────────────────────────────────────────────────

export interface A2ZLevelRead {
  level_number: number;
  name: string;
  target_words: number;
  round_time_seconds: number;
}

export interface A2ZProgressRead {
  challenge_slug: string;
  letters: string[];
  levels: A2ZLevelRead[];
  current_level_number: number;
  cleared_by_level: Record<string, string[]>;
  open_letters: string[];
  game_completed: boolean;
  can_restart: boolean;
}

export interface StartRoundResponse {
  round_id: number;
  letter: string;
  target_words: number;
  round_time_seconds: number;
  expires_at: string;
  level_number: number;
}

export interface AudioChunkResponse {
  new_words: string[];
  accepted_words: string[];
  valid_word_count: number;
  target_words: number;
  passed_so_far: boolean;
}

export interface FinishRoundResponse {
  passed: boolean;
  letter: string;
  valid_words: string[];
  valid_word_count: number;
  target_words: number;
  level_number: number;
  level_cleared: boolean;
  game_completed: boolean;
  progress: A2ZProgressRead;
}

// ── API calls ─────────────────────────────────────────────────────────

const PREFIX = "/api/v1/challenges/a2z";

export const a2zApi = {
  /** Get alphabet progress for the home screen. */
  getProgress: () =>
    api.get<A2ZProgressRead>(`${PREFIX}/progress`).then(r => r.data),

  /** Start a new round — spin for a random letter or pick one. */
  startRound: (mode: "spin" | "pick", letter?: string) =>
    api.post<StartRoundResponse>(`${PREFIX}/rounds`, { mode, letter }).then(r => r.data),

  /** Upload an audio chunk and receive new valid words. */
  sendAudioChunk: (roundId: number, audioBlob: Blob, chunkIndex: number) => {
    const formData = new FormData();
    formData.append("audio", audioBlob, `chunk_${chunkIndex}.webm`);
    formData.append("chunk_index", String(chunkIndex));
    return api.post<AudioChunkResponse>(
      `${PREFIX}/rounds/${roundId}/audio-chunks`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } },
    ).then(r => r.data);
  },

  /** Finish a round — get final grading and updated progress. */
  finishRound: (roundId: number) =>
    api.post<FinishRoundResponse>(`${PREFIX}/rounds/${roundId}/finish`).then(r => r.data),

  /** Restart the game (only after full completion). */
  restart: () =>
    api.post<A2ZProgressRead>(`${PREFIX}/restart`).then(r => r.data),
};
