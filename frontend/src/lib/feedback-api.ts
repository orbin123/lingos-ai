import { api } from "./api";

export interface ShouldShowResponse {
  show: boolean;
  trigger_type: string | null;
}

export interface FeedbackSubmit {
  rating: number;
  positive_feedback?: string | null;
  improvement_feedback?: string | null;
  bug_report?: string | null;
  app_version?: string | null;
}

export interface FeedbackSubmitResponse {
  review_id: number;
  created_at: string;
}

export const feedbackApi = {
  shouldShow: () =>
    api.get<ShouldShowResponse>("/feedback/should-show").then((r) => r.data),
  submit: (data: FeedbackSubmit) =>
    api.post<FeedbackSubmitResponse>("/feedback/submit", data).then((r) => r.data),
  dismiss: () =>
    api.post<{ dismissed: boolean }>("/feedback/dismiss", {}).then((r) => r.data),
};
