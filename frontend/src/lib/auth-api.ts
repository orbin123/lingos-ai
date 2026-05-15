import { api } from "./api";
import type { EnrollmentRead } from "./courses-api";
import type { NotificationSettings } from "./subscriptions-api";
import type { LoginInput, RegisterInput } from "./validators/auth";

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
  enrollment: EnrollmentRead | null;
  phone_number: string | null;
  country: string | null;
  native_language: string | null;
  primary_goals: string[];
  personalisation_context: string;
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
  signup: (data: RegisterInput) =>
    api.post<UserOut>("/auth/signup", data).then((r) => r.data),

  login: (data: LoginInput) =>
    api.post<TokenOut>("/auth/login", data).then((r) => r.data),

  me: () => api.get<UserOut>("/auth/me").then((r) => r.data),

  updateMe: (data: UserUpdateInput) =>
    api.patch<UserOut>("/auth/me", data).then((r) => r.data),

  googleRelinkUrl: () =>
    api.post<{ auth_url: string }>("/auth/google/relink-url").then((r) => r.data),
};
