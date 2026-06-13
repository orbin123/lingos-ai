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

// ── Feedback reactions (learner 👍/👎 on AI feedback) ───────────────

export type ReactionValue = "LIKE" | "DISLIKE";
export type FeedbackReactionType = "ACTIVITY_FEEDBACK" | "COACH_NOTE";

export interface ReactionResponse {
  user_reaction: ReactionValue | null;
}

export const feedbackApi = {
  shouldShow: () =>
    api.get<ShouldShowResponse>("/feedback/should-show").then((r) => r.data),
  submit: (data: FeedbackSubmit) =>
    api.post<FeedbackSubmitResponse>("/feedback/submit", data).then((r) => r.data),
  dismiss: () =>
    api.post<{ dismissed: boolean }>("/feedback/dismiss", {}).then((r) => r.data),

  // Set / switch / clear (toggle-off) the learner's reaction to one feedback
  // item. The server returns the resulting reaction (null = cleared).
  react: (params: {
    feedbackId: number;
    feedbackType: FeedbackReactionType;
    reaction: ReactionValue;
  }) =>
    api
      .post<ReactionResponse>("/feedback/reaction", {
        feedback_id: params.feedbackId,
        feedback_type: params.feedbackType,
        reaction: params.reaction,
      })
      .then((r) => r.data),
};
