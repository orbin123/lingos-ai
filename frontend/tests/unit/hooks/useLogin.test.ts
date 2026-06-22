import { describe, expect, it } from "vitest";
import { waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";

import { useLogin } from "@/hooks/useLogin";
import { useAuthStore } from "@/store/authStore";
import { server } from "../../setup/msw/server";
import { routerMock } from "../../setup/router-mock";
import { renderHookWithProviders } from "../../utils/render";

const API = "http://localhost:8000";

// A JWT-shaped token with a valid base64 payload so authStore.setToken can
// decode it (payload = {"sub":"new-user"}).
const TOKEN = "h.eyJzdWIiOiJuZXctdXNlciJ9.s";

// useLogin's mutation hits POST /auth/login (for the token) then GET /auth/me;
// the `me` payload is what the onSuccess routing branch reads.
function mockLogin(me: Record<string, unknown>) {
  server.use(
    http.post(`${API}/auth/login`, () =>
      HttpResponse.json({ access_token: TOKEN, token_type: "bearer" }),
    ),
    http.get(`${API}/auth/me`, () => HttpResponse.json(me)),
  );
}

describe("useLogin", () => {
  it("routes to /diagnosis when the placement test isn't done yet", async () => {
    mockLogin({ diagnosis_completed: false, access_state: "verified" });

    const { result } = renderHookWithProviders(() => useLogin());
    result.current.mutate({ email: "a@example.com", password: "pw" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(routerMock.push).toHaveBeenCalledWith("/diagnosis");
  });

  it("sends a diagnosis-done, plan-less (verified) user to the dashboard, not pricing", async () => {
    // Regression guard: this branch used to push("/pricing"), which bypassed the
    // locked dashboard plan-picker the user is supposed to land on.
    mockLogin({ diagnosis_completed: true, access_state: "verified" });

    const { result } = renderHookWithProviders(() => useLogin());
    result.current.mutate({ email: "a@example.com", password: "pw" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(routerMock.push).toHaveBeenCalledWith("/dashboard");
    expect(routerMock.push).not.toHaveBeenCalledWith("/pricing");
  });

  it("sends an enrolled (trial) user to the dashboard", async () => {
    mockLogin({ diagnosis_completed: true, access_state: "trial" });

    const { result } = renderHookWithProviders(() => useLogin());
    result.current.mutate({ email: "a@example.com", password: "pw" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(routerMock.push).toHaveBeenCalledWith("/dashboard");
  });

  it("stores the access token on success", async () => {
    mockLogin({ diagnosis_completed: true, access_state: "trial" });

    const { result } = renderHookWithProviders(() => useLogin());
    result.current.mutate({ email: "a@example.com", password: "pw" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(useAuthStore.getState().token).toBe(TOKEN);
  });
});
