import { create } from "zustand";

import { API_BASE_URL } from "@/lib/api-config";

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  isSuperUser: boolean;
  isAdmin: boolean;
  roles: string[];

  /**
   * True once hydrate() has run at least once.
   * Pages should wait for this before deciding to redirect.
   * Without this flag, a logged-in user gets kicked to /login
   * on every refresh because the store starts empty before
   * localStorage is read.
   */
  _hydrated: boolean;

  setToken: (token: string) => void;
  logout: () => void;
  hydrate: () => void;
}

function decodePayload(token: string): { roles: string[]; isSuperUser: boolean } {
  try {
    const payloadB64 = token.split(".")[1];
    const decoded = JSON.parse(atob(payloadB64));
    const roles = Array.isArray(decoded.roles)
      ? decoded.roles.filter((role: unknown): role is string => typeof role === "string")
      : decoded.is_superuser === true
        ? ["super_admin"]
        : [];
    return {
      roles,
      isSuperUser: decoded.is_superuser === true || roles.includes("super_admin"),
    };
  } catch {
    return { roles: [], isSuperUser: false };
  }
}

function isAdminRole(roles: string[], isSuperUser: boolean): boolean {
  return isSuperUser || roles.includes("admin") || roles.includes("super_admin");
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  isAuthenticated: false,
  isSuperUser: false,
  isAdmin: false,
  roles: [],
  _hydrated: false,

  setToken: (token) => {
    localStorage.setItem("token", token);
    const payload = decodePayload(token);
    set({
      token,
      isAuthenticated: true,
      isSuperUser: payload.isSuperUser,
      isAdmin: isAdminRole(payload.roles, payload.isSuperUser),
      roles: payload.roles,
    });
  },

  logout: () => {
    // Best-effort server-side revocation of the refresh session. Raw fetch
    // (not the shared axios instance) to avoid an import cycle with api.ts;
    // the httpOnly cookie rides along via credentials: "include".
    if (typeof window !== "undefined") {
      fetch(`${API_BASE_URL}/auth/logout`, {
        method: "POST",
        credentials: "include",
      }).catch(() => {});
    }
    localStorage.removeItem("token");
    set({
      token: null,
      isAuthenticated: false,
      isSuperUser: false,
      isAdmin: false,
      roles: [],
    });
  },

  hydrate: () => {
    const token = localStorage.getItem("token");
    const payload = token ? decodePayload(token) : { roles: [], isSuperUser: false };
    set({
      token: token ?? null,
      isAuthenticated: !!token,
      isSuperUser: payload.isSuperUser,
      isAdmin: isAdminRole(payload.roles, payload.isSuperUser),
      roles: payload.roles,
      _hydrated: true,       // ← mark hydration as done
    });
  },
}));
