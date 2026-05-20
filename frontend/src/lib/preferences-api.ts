import { api } from "./api";

export type CourseLengthLiteral = "24w" | "48w";

export interface UserCoursePreferenceRead {
  course_length: CourseLengthLiteral;
  tasks_per_day: number;
  allow_read: boolean;
  allow_write: boolean;
  allow_listen: boolean;
  allow_speak: boolean;
  current_week: number;
  current_day_in_week: number;
  current_day_started_at: string;
  last_completed_on: string | null;
}

export interface UserCoursePreferenceUpdate {
  course_length?: CourseLengthLiteral;
  tasks_per_day?: number;
  allow_read?: boolean;
  allow_write?: boolean;
  allow_listen?: boolean;
  allow_speak?: boolean;
}

export const preferencesApi = {
  get: () =>
    api
      .get<UserCoursePreferenceRead>("/api/preferences")
      .then((r) => r.data),

  update: (payload: UserCoursePreferenceUpdate) =>
    api
      .patch<UserCoursePreferenceRead>("/api/preferences", payload)
      .then((r) => r.data),
};
