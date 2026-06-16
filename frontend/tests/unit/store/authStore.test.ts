import { describe, expect, it } from "vitest";
import { http, HttpResponse } from "msw";

import { useAuthStore } from "@/store/authStore";
import { server } from "../../setup/msw/server";
import { API_BASE } from "../../setup/msw/handlers";

// A minimal JWT whose payload round-trips through the store's atob/JSON.parse.
function jwt(payload: Record<string, unknown>): string {
  return `header.${btoa(JSON.stringify(payload))}.sig`;
}

describe("authStore.setToken", () => {
  it("derives a plain learner (no admin, no superuser) and persists the token", () => {
    useAuthStore.getState().setToken(jwt({ roles: ["learner"] }));
    const s = useAuthStore.getState();
    expect(s.isAuthenticated).toBe(true);
    expect(s.roles).toEqual(["learner"]);
    expect(s.isAdmin).toBe(false);
    expect(s.isSuperUser).toBe(false);
    expect(localStorage.getItem("token")).toBe(jwt({ roles: ["learner"] }));
  });

  it("treats an explicit admin role as admin but not superuser", () => {
    useAuthStore.getState().setToken(jwt({ roles: ["admin"] }));
    const s = useAuthStore.getState();
    expect(s.isAdmin).toBe(true);
    expect(s.isSuperUser).toBe(false);
  });

  it("treats super_admin as both admin and superuser", () => {
    useAuthStore.getState().setToken(jwt({ roles: ["super_admin"] }));
    const s = useAuthStore.getState();
    expect(s.isAdmin).toBe(true);
    expect(s.isSuperUser).toBe(true);
  });

  it("falls back to super_admin when is_superuser is set without roles", () => {
    useAuthStore.getState().setToken(jwt({ is_superuser: true }));
    const s = useAuthStore.getState();
    expect(s.roles).toEqual(["super_admin"]);
    expect(s.isSuperUser).toBe(true);
    expect(s.isAdmin).toBe(true);
  });

  it("survives a malformed token — authenticated but no roles", () => {
    useAuthStore.getState().setToken("not-a-jwt");
    const s = useAuthStore.getState();
    expect(s.isAuthenticated).toBe(true);
    expect(s.roles).toEqual([]);
    expect(s.isAdmin).toBe(false);
    expect(s.isSuperUser).toBe(false);
  });
});

describe("authStore.hydrate", () => {
  it("marks hydrated and stays logged out with no stored token", () => {
    useAuthStore.getState().hydrate();
    const s = useAuthStore.getState();
    expect(s._hydrated).toBe(true);
    expect(s.isAuthenticated).toBe(false);
    expect(s.token).toBeNull();
  });

  it("rehydrates roles from a stored token", () => {
    localStorage.setItem("token", jwt({ roles: ["admin"] }));
    useAuthStore.getState().hydrate();
    const s = useAuthStore.getState();
    expect(s._hydrated).toBe(true);
    expect(s.isAuthenticated).toBe(true);
    expect(s.isAdmin).toBe(true);
  });
});

describe("authStore.logout", () => {
  it("clears state + localStorage (best-effort server revoke is fire-and-forget)", () => {
    // logout() does a raw fetch to /auth/logout; register a handler so MSW's
    // onUnhandledRequest:"error" doesn't trip on the fire-and-forget call.
    server.use(http.post(`${API_BASE}/auth/logout`, () => new HttpResponse(null, { status: 204 })));

    useAuthStore.getState().setToken(jwt({ roles: ["admin"] }));
    useAuthStore.getState().logout();

    const s = useAuthStore.getState();
    expect(s.token).toBeNull();
    expect(s.isAuthenticated).toBe(false);
    expect(s.roles).toEqual([]);
    expect(s.isAdmin).toBe(false);
    expect(localStorage.getItem("token")).toBeNull();
  });
});
