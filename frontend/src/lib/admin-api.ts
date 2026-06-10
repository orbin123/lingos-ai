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
  pending_feedback_reviews: number;
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

export interface FeedbackReviewItem {
  feedback_type: "specific" | "rag";
  feedback_id: number;
  user: AdminLogUser | null;
  context_label: string;
  // Specific-feedback fields.
  score: number | null;
  summary: string | null;
  did_well: string[];
  mistakes: Record<string, unknown>[];
  next_tip: string | null;
  // RAG-feedback fields.
  mentor_note: string | null;
  rating: "like" | "dislike" | null;
  // Review annotation.
  review_status: "pending" | "approved" | "flagged" | "fixed";
  reviewed_by: AdminLogUser | null;
  reviewed_at: string | null;
  admin_note: string | null;
  created_at: string;
}

export interface FeedbackReviewUpdate {
  review_status: FeedbackReviewItem["review_status"];
  admin_note?: string | null;
}

export interface AdminPayment {
  id: number;
  user_id: number;
  user: AdminLogUser | null;
  provider: string;
  provider_payment_id: string | null;
  amount: number;
  currency: string;
  status: string;
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
  plan_name: string;
  status: string;
  trial_ends_at: string | null;
  current_period_start: string | null;
  current_period_end: string | null;
  created_at: string;
  updated_at: string;
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
  status: string;
  signed_up_at: string;
  trial_ends_at: string;
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
  status: string;
  created_at: string;
}

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

  appReviews: () =>
    api.get<AppReviewItem[]>("/admin/app-reviews").then((r) => r.data),

  auditLogs: () =>
    api.get<AdminAuditLog[]>("/admin/audit-logs").then((r) => r.data),

  aiLogs: () => api.get<AIRequestLog[]>("/admin/ai-logs").then((r) => r.data),

  aiLog: (logId: number) =>
    api.get<AIRequestLog>(`/admin/ai-logs/${logId}`).then((r) => r.data),

  aiQuality: (days = 7) =>
    api.get<AIQualityReport>(`/admin/ai-quality?days=${days}`).then((r) => r.data),

  feedbackReview: () =>
    api.get<FeedbackReviewItem[]>("/admin/feedback-review").then((r) => r.data),

  updateFeedbackReview: (
    feedbackType: "specific" | "rag",
    feedbackId: number,
    data: FeedbackReviewUpdate,
  ) =>
    api
      .patch<FeedbackReviewItem>(
        `/admin/feedback-review/${feedbackType}/${feedbackId}`,
        data,
      )
      .then((r) => r.data),

  payments: () => api.get<AdminPayment[]>("/admin/payments").then((r) => r.data),

  subscribers: () =>
    api.get<SubscribersOverview>("/admin/subscribers").then((r) => r.data),

  userBilling: (userId: number) =>
    api.get<AdminUserBilling>(`/admin/users/${userId}/billing`).then((r) => r.data),

  updateSubscriberAccess: (userId: number, accessExpiresAt: string) =>
    api
      .patch<SubscriberItem>(`/admin/subscribers/${userId}/access`, {
        access_expires_at: accessExpiresAt,
      })
      .then((r) => r.data),
};
