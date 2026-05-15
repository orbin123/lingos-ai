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

export interface TaskTemplate {
  id: number;
  title: string;
  task_type: string;
  difficulty: number;
  status: "draft" | "active" | "archived";
  content: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface TaskTemplateInput {
  title: string;
  task_type: string;
  difficulty: number;
  status: "draft" | "active" | "archived";
  content: Record<string, unknown>;
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
  latency_ms: number | null;
  status: string;
  error_message: string | null;
  prompt_version: string | null;
  created_at: string;
}

export interface FeedbackReviewItem {
  id: number;
  user: AdminLogUser | null;
  task_title: string;
  user_response: Record<string, unknown>;
  user_response_raw_text: string | null;
  ai_feedback: Record<string, unknown>;
  score: number;
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

export interface SubscriptionUpdate {
  plan_name?: string;
  status?: string;
  trial_ends_at?: string | null;
  current_period_start?: string | null;
  current_period_end?: string | null;
}

export const adminApi = {
  summary: () => api.get<AdminSummary>("/admin/summary").then((r) => r.data),

  users: () => api.get<AdminUserListItem[]>("/admin/users").then((r) => r.data),

  user: (userId: number) =>
    api.get<AdminUserDetail>(`/admin/users/${userId}`).then((r) => r.data),

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

  taskTemplates: () =>
    api.get<TaskTemplate[]>("/admin/task-templates").then((r) => r.data),

  createTaskTemplate: (data: TaskTemplateInput) =>
    api.post<TaskTemplate>("/admin/task-templates", data).then((r) => r.data),

  updateTaskTemplate: (templateId: number, data: Partial<TaskTemplateInput>) =>
    api
      .patch<TaskTemplate>(`/admin/task-templates/${templateId}`, data)
      .then((r) => r.data),

  archiveTaskTemplate: (templateId: number) =>
    api.delete<TaskTemplate>(`/admin/task-templates/${templateId}`).then((r) => r.data),

  auditLogs: () =>
    api.get<AdminAuditLog[]>("/admin/audit-logs").then((r) => r.data),

  aiLogs: () => api.get<AIRequestLog[]>("/admin/ai-logs").then((r) => r.data),

  aiLog: (logId: number) =>
    api.get<AIRequestLog>(`/admin/ai-logs/${logId}`).then((r) => r.data),

  feedbackReview: () =>
    api.get<FeedbackReviewItem[]>("/admin/feedback-review").then((r) => r.data),

  updateFeedbackReview: (feedbackId: number, data: FeedbackReviewUpdate) =>
    api
      .patch<FeedbackReviewItem>(`/admin/feedback-review/${feedbackId}`, data)
      .then((r) => r.data),

  payments: () => api.get<AdminPayment[]>("/admin/payments").then((r) => r.data),

  subscriptions: () =>
    api.get<AdminSubscription[]>("/admin/subscriptions").then((r) => r.data),

  userBilling: (userId: number) =>
    api.get<AdminUserBilling>(`/admin/users/${userId}/billing`).then((r) => r.data),

  updateSubscription: (subscriptionId: number, data: SubscriptionUpdate) =>
    api
      .patch<AdminSubscription>(`/admin/subscriptions/${subscriptionId}`, data)
      .then((r) => r.data),
};
