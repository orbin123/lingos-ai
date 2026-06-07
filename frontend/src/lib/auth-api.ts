import { api } from "./api";
import type { UserCoursePreferenceRead } from "./preferences-api";
import type { NotificationSettings } from "./subscriptions-api";
import type { LoginInput, RegisterInput } from "./validators/auth";

/**
 * Structured personalisation — server-derived JSON that the planner /
 * teacher / task generator / feedback agents consume directly. Populated
 * by the backend Personalization Engine from the free-text
 * `personalisation_context` plus the rest of the profile. Not user-editable
 * directly; refresh happens on profile save and diagnosis completion.
 */
export interface StructuredPersonalisation {
  domain: string;
  communication_contexts: string[];
  priority_skills: string[];
  pain_points: string[];
  tone_preference: "casual" | "neutral" | "professional" | "academic";
  extraction_source: "llm" | "fallback" | "empty";
  extracted_at: string;
}

// Backend response shapes
export interface UserOut {
  id: number;
  email: string;
  name: string;
  display_name: string;
  created_at: string;
  auth_provider: "password" | "google";
  diagnosis_completed: boolean;
  is_superuser: boolean;
  is_active: boolean;
  roles: string[];
  role: string;
  preference: UserCoursePreferenceRead | null;
  phone_number: string | null;
  country: string | null;
  native_language: string | null;
  primary_goals: string[];
  personalisation_context: string;
  structured_personalisation: StructuredPersonalisation | null;
  self_assessed_level: string | null;
  goal: string | null;
  interests: string[];
  notifications: NotificationSettings;
}

export interface TokenOut {
  access_token: string;
  token_type: string;
}

export interface UserUpdateInput {
  name?: string;
  display_name?: string;
  email?: string;
  password?: string;
  phone_number?: string | null;
  country?: string | null;
  native_language?: string | null;
  primary_goals?: string[];
  personalisation_context?: string;
}

export const authApi = {
  signup: (data: RegisterInput) => {
    const payload = {
      name: data.name,
      email: data.email,
      password: data.password,
    };
    return api.post<UserOut>("/auth/signup", payload).then((r) => r.data);
  },

  login: (data: LoginInput) =>
    api.post<TokenOut>("/auth/login", data).then((r) => r.data),

  me: () => api.get<UserOut>("/auth/me").then((r) => r.data),

  updateMe: (data: UserUpdateInput) =>
    api.patch<UserOut>("/auth/me", data).then((r) => r.data),

  googleRelinkUrl: () =>
    api.post<{ auth_url: string }>("/auth/google/relink-url").then((r) => r.data),
};
