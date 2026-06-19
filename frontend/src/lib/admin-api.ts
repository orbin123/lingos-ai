import { api } from "./api";

export interface AdminUserListItem {
  id: number;
  name: string;
  email: string;
  role: string;
  roles: string[];
  is_active: boolean;
  created_at: string;
}

export interface AdminSummary {
  total_users: number;
  active_users: number;
  tasks_completed: number;
  feedback_generated: number;
  ai_requests_24h: number;
  ai_errors_24h: number;
  ai_cost_24h: number;
  ai_avg_latency_ms_24h: number | null;
  disliked_feedback: number;
  recent_users: AdminUserListItem[];
}

export interface AdminUserProfile {
  display_name: string | null;
  phone_number: string | null;
  country: string | null;
  native_language: string | null;
  self_assessed_level: string | null;
  goal: string | null;
  interests: string[];
  diagnosis_completed: boolean;
}

export interface AdminSkillScore {
  skill_id: number;
  skill_name: string;
  score: number;
  source: string;
}

export interface AdminRecentTask {
  id: number;
  task_id: number;
  title: string;
  task_type: string;
  status: string;
  completed_at: string | null;
  created_at: string;
}

export interface AdminRecentFeedback {
  id: number;
  task_title: string;
  task_type: string;
  score: number;
  body: Record<string, unknown>;
  created_at: string;
}

export interface AdminUserDetail extends AdminUserListItem {
  profile: AdminUserProfile | null;
  skill_scores: AdminSkillScore[];
  recent_tasks: AdminRecentTask[];
  recent_feedback: AdminRecentFeedback[];
}

export interface UserProgressItem {
  user_id: number;
  name: string;
  email: string;
  plan_id: string | null;
  plan_name: string | null;
  purchase_complete: boolean;
  access_expires_at: string | null;
  activities_completed: number;
  dashboard_score: number | null;
  subskill_scores: AdminSkillScore[];
}

export interface AdminPermission {
  id: number;
  key: string;
  description: string;
  created_at: string;
}

export interface AdminRole {
  id: number;
  name: string;
  permissions: string[];
  user_count: number;
  created_at: string;
}

export interface UserRolesUpdate {
  roles: string[];
}

export interface RolePermissionsUpdate {
  permission_keys: string[];
}

export interface AdminLogUser {
  id: number;
  name: string;
  email: string;
}

export interface AdminAuditLog {
  id: number;
  admin_user_id: number | null;
  admin: AdminLogUser | null;
  action: string;
  resource_type: string;
  resource_id: string;
  old_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface AIRequestLog {
  id: number;
  user_id: number | null;
  user: AdminLogUser | null;
  trace_id: string | null;
  agent_name: string;
  model: string;
  input_tokens: number | null;
  output_tokens: number | null;
  cost_usd: number | null;
  latency_ms: number | null;
  status: string;
  error_message: string | null;
  prompt_version: string | null;
  created_at: string;
}

export interface AIQualityRow {
  target_type: string;
  judged_count: number;
  mean_accuracy: number | null;
  mean_relevance: number | null;
  mean_helpfulness: number | null;
  mean_correctness: number | null;
  mean_faithfulness: number | null;
}

export interface AIQualityWorst {
  id: number;
  trace_id: string | null;
  target_type: string;
  target_id: string | null;
  judge_model: string;
  accuracy: number | null;
  relevance: number | null;
  helpfulness: number | null;
  correctness: number | null;
  faithfulness: number | null;
  rationale: string | null;
  created_at: string;
}

export interface AIQualityTimeSeriesPoint {
  date: string;
  target_type: string;
  judged_count: number;
  mean_accuracy: number | null;
  mean_relevance: number | null;
  mean_helpfulness: number | null;
  mean_correctness: number | null;
  mean_faithfulness: number | null;
}

export interface AIQualityReport {
  days: number;
  judged_count: number;
  means: AIQualityRow[];
  worst: AIQualityWorst[];
  series: AIQualityTimeSeriesPoint[];
}

export interface AICostByModel {
  model: string;
  requests: number;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number | null;
}

export interface AICostByCapability {
  agent_name: string;
  requests: number;
  errors: number;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
}

export interface AICostDailyPoint {
  date: string;
  cost_usd: number;
  requests: number;
}

export interface AICostReport {
  days: number;
  total_cost_usd: number;
  total_requests: number;
  total_input_tokens: number;
  total_output_tokens: number;
  unpriced_requests: number;
  by_model: AICostByModel[];
  by_capability: AICostByCapability[];
  daily: AICostDailyPoint[];
}

export type FeedbackReactionType = "ACTIVITY_FEEDBACK" | "COACH_NOTE";
export type FeedbackReactionValue = "LIKE" | "DISLIKE";

export interface FeedbackAnalyticsItem {
  feedback_type: FeedbackReactionType;
  feedback_id: number;
  user: AdminLogUser | null;
  context_label: string;
  // Activity-feedback fields.
  score: number | null;
  summary: string | null;
  did_well: string[];
  mistakes: Record<string, unknown>[];
  next_tip: string | null;
  // Coach's-Note field.
  mentor_note: string | null;
  // The learner's reaction to this feedback.
  user_reaction: FeedbackReactionValue | null;
  created_at: string;
}

export interface FeedbackReactionStats {
  total_items: number;
  liked: number;
  disliked: number;
  no_reaction: number;
  positive_rate: number | null;
}

export type FeedbackReactionFilter = "LIKE" | "DISLIKE" | "NONE";

export interface AdminPayment {
  id: number;
  user_id: number;
  user: AdminLogUser | null;
  provider: string;
  provider_payment_id: string | null;
  provider_order_id: string | null;
  amount: number;
  currency: string;
  status: string;
  method: string | null;
  failure_reason: string | null;
  paid_at: string | null;
  created_at: string;
}

export interface AdminSubscription {
  id: number;
  user_id: number;
  user: AdminLogUser | null;
  provider: string;
  provider_customer_id: string | null;
  provider_subscription_id: string | null;
  plan_id: string | null;
  plan_name: string;
  status: string;
  trial_started_at: string | null;
  trial_ends_at: string | null;
  cancelled_at: string | null;
  current_period_start: string | null;
  current_period_end: string | null;
  created_at: string;
  updated_at: string;
}

export interface SubscriptionAdminUpdate {
  status?: string;
  plan_id?: string;
  trial_started_at?: string;
  trial_ends_at?: string;
  current_period_end?: string;
}

export interface AdminUserBilling {
  user: AdminLogUser;
  subscription: AdminSubscription | null;
  payments: AdminPayment[];
}

export interface SubscriberItem {
  user_id: number;
  name: string;
  email: string;
  plan_id: string | null;
  plan_name: string | null;
  amount_paid: number | null;
  currency: string | null;
  status: string;
  purchased_at: string | null;
  access_expires_at: string | null;
}

export interface TrialUserItem {
  user_id: number;
  name: string;
  email: string;
  // "unverified" | "not_started" | "trial" | "expired"
  status: string;
  email_verified: boolean;
  signed_up_at: string;
  trial_started_at: string | null;
  trial_ends_at: string | null;
}

export interface SubscribersOverview {
  subscribers: SubscriberItem[];
  trials: TrialUserItem[];
}

export interface AppReviewItem {
  id: number;
  user: AdminLogUser | null;
  rating: number;
  title: string | null;
  body: string | null;
  positive_feedback: string | null;
  improvement_feedback: string | null;
  bug_report: string | null;
  status: string;
  created_at: string;
}

export interface ReviewThemeCount {
  text: string;
  count: number;
}

export interface ReviewTrendPoint {
  date: string;
  count: number;
  average_rating: number;
}

export interface ReviewStats {
  total_reviews: number;
  average_rating: number | null;
  rating_distribution: Record<string, number>;
  submission_rate: number | null;
  prompts_shown: number;
  prompts_submitted: number;
  top_improvements: ReviewThemeCount[];
  top_bugs: ReviewThemeCount[];
  trend: ReviewTrendPoint[];
}

export type BlogStatus = "draft" | "published";

export interface BlogPostAdmin {
  id: number;
  title: string;
  slug: string;
  excerpt: string | null;
  content: string;
  cover_image_url: string | null;
  category: string | null;
  status: BlogStatus;
  published_at: string | null;
  author_id: number | null;
  author_name: string;
  created_at: string;
  updated_at: string;
}

export interface BlogPostCreateInput {
  title: string;
  slug?: string | null;
  excerpt?: string | null;
  content: string;
  cover_image_url?: string | null;
  category?: string | null;
  status?: BlogStatus;
}

export type BlogPostUpdateInput = Partial<BlogPostCreateInput>;

export const adminApi = {
  summary: () => api.get<AdminSummary>("/admin/summary").then((r) => r.data),

  users: () => api.get<AdminUserListItem[]>("/admin/users").then((r) => r.data),

  user: (userId: number) =>
    api.get<AdminUserDetail>(`/admin/users/${userId}`).then((r) => r.data),

  userProgress: () =>
    api.get<UserProgressItem[]>("/admin/user-progress").then((r) => r.data),

  updateUserStatus: (userId: number, isActive: boolean) =>
    api
      .patch<AdminUserListItem>(`/admin/users/${userId}/status`, {
        is_active: isActive,
      })
      .then((r) => r.data),

  roles: () => api.get<AdminRole[]>("/admin/roles").then((r) => r.data),

  permissions: () =>
    api.get<AdminPermission[]>("/admin/permissions").then((r) => r.data),

  updateUserRoles: (userId: number, data: UserRolesUpdate) =>
    api.patch<AdminUserListItem>(`/admin/users/${userId}/roles`, data).then((r) => r.data),

  updateRolePermissions: (roleId: number, data: RolePermissionsUpdate) =>
    api
      .patch<AdminRole>(`/admin/roles/${roleId}/permissions`, data)
      .then((r) => r.data),

  appReviews: (rating?: number) =>
    api
      .get<AppReviewItem[]>("/admin/app-reviews", {
        params: rating ? { rating } : undefined,
      })
      .then((r) => r.data),

  reviewStats: () =>
    api.get<ReviewStats>("/admin/reviews/stats").then((r) => r.data),

  auditLogs: () =>
    api.get<AdminAuditLog[]>("/admin/audit-logs").then((r) => r.data),

  aiLogs: () => api.get<AIRequestLog[]>("/admin/ai-logs").then((r) => r.data),

  aiLog: (logId: number) =>
    api.get<AIRequestLog>(`/admin/ai-logs/${logId}`).then((r) => r.data),

  aiQuality: (days = 7) =>
    api.get<AIQualityReport>(`/admin/ai-quality?days=${days}`).then((r) => r.data),

  aiCosts: (days = 30) =>
    api.get<AICostReport>(`/admin/ai-costs?days=${days}`).then((r) => r.data),

  feedbackAnalytics: (filters?: {
    feedbackType?: FeedbackReactionType;
    reaction?: FeedbackReactionFilter;
  }) => {
    const params = new URLSearchParams();
    if (filters?.feedbackType) params.set("feedback_type", filters.feedbackType);
    if (filters?.reaction) params.set("reaction", filters.reaction);
    const query = params.toString();
    return api
      .get<FeedbackAnalyticsItem[]>(
        `/admin/feedback-analytics${query ? `?${query}` : ""}`,
      )
      .then((r) => r.data);
  },

  feedbackAnalyticsStats: () =>
    api
      .get<FeedbackReactionStats>("/admin/feedback-analytics/stats")
      .then((r) => r.data),

  payments: () => api.get<AdminPayment[]>("/admin/payments").then((r) => r.data),

  subscribers: (status?: string) =>
    api
      .get<SubscribersOverview>("/admin/subscribers", {
        params: status ? { status } : undefined,
      })
      .then((r) => r.data),

  userBilling: (userId: number) =>
    api.get<AdminUserBilling>(`/admin/users/${userId}/billing`).then((r) => r.data),

  updateSubscriberAccess: (userId: number, accessExpiresAt: string) =>
    api
      .patch<SubscriberItem>(`/admin/subscribers/${userId}/access`, {
        access_expires_at: accessExpiresAt,
      })
      .then((r) => r.data),

  updateSubscriberSubscription: (
    userId: number,
    update: SubscriptionAdminUpdate,
  ) =>
    api
      .patch<AdminSubscription>(
        `/admin/subscribers/${userId}/subscription`,
        update,
      )
      .then((r) => r.data),

  expireDueTrials: () =>
    api
      .post<{ expired: number }>("/admin/subscriptions/expire-due-trials")
      .then((r) => r.data),

  // ── Blog management ──────────────────────────────────────────────────
  blogList: () =>
    api.get<BlogPostAdmin[]>("/admin/blog").then((r) => r.data),

  blogGet: (postId: number) =>
    api.get<BlogPostAdmin>(`/admin/blog/${postId}`).then((r) => r.data),

  blogCreate: (data: BlogPostCreateInput) =>
    api.post<BlogPostAdmin>("/admin/blog", data).then((r) => r.data),

  blogUpdate: (postId: number, data: BlogPostUpdateInput) =>
    api.patch<BlogPostAdmin>(`/admin/blog/${postId}`, data).then((r) => r.data),

  blogDelete: (postId: number) =>
    api.delete<void>(`/admin/blog/${postId}`).then((r) => r.data),

  blogPublish: (postId: number) =>
    api.post<BlogPostAdmin>(`/admin/blog/${postId}/publish`).then((r) => r.data),

  blogUnpublish: (postId: number) =>
    api
      .post<BlogPostAdmin>(`/admin/blog/${postId}/unpublish`)
      .then((r) => r.data),

  blogUploadCover: (postId: number, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api
      .post<BlogPostAdmin>(`/admin/blog/${postId}/cover`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },
};
