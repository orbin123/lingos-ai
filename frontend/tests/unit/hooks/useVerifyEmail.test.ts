import { describe, expect, it } from "vitest";
import { waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";

import { useVerifyEmail } from "@/hooks/useVerifyEmail";
import { useAuthStore } from "@/store/authStore";
import { server } from "../../setup/msw/server";
import { routerMock } from "../../setup/router-mock";
import { renderHookWithProviders } from "../../utils/render";

const API = "http://localhost:8000";

// A JWT-shaped token with a valid base64 payload so authStore.setToken can
// decode it (payload = {"sub":"new-user"}).
const TOKEN = "h.eyJzdWIiOiJuZXctdXNlciJ9.s";

describe("useVerifyEmail", () => {
  it("clears stale cached queries and routes to /diagnosis/intro on success", async () => {
    server.use(
      http.post(`${API}/auth/verify-email`, () =>
        HttpResponse.json({ access_token: TOKEN, token_type: "bearer" }),
      ),
    );

    const { result, queryClient } = renderHookWithProviders(() =>
      useVerifyEmail(),
    );

    // Simulate a previous user's stale cache lingering in the session-long
    // QueryClient — this is what used to bounce the new user dashboard→diagnosis.
    queryClient.setQueryData(["me"], { diagnosis_completed: true });

    result.current.mutate({ email: "new@example.com", code: "123456" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // The new token is stored, the stale ["me"] is gone, and we land on the
    // intro page (which will now fetch a fresh ["me"] and stay put).
    expect(useAuthStore.getState().token).toBe(TOKEN);
    expect(queryClient.getQueryData(["me"])).toBeUndefined();
    expect(routerMock.push).toHaveBeenCalledWith("/diagnosis/intro");
  });

  it("does not navigate when verification fails", async () => {
    server.use(
      http.post(`${API}/auth/verify-email`, () =>
        HttpResponse.json({ detail: "invalid code" }, { status: 400 }),
      ),
    );

    const { result } = renderHookWithProviders(() => useVerifyEmail());
    result.current.mutate({ email: "new@example.com", code: "000000" });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(routerMock.push).not.toHaveBeenCalled();
  });
});
