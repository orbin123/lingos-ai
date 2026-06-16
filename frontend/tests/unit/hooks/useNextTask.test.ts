import { describe, expect, it } from "vitest";
import { waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";

import { useNextTask } from "@/hooks/useNextTask";
import { server } from "../../setup/msw/server";
import { renderHookWithProviders } from "../../utils/render";

const API = "http://localhost:8000";

describe("useNextTask", () => {
  it("fetches the day bundle from POST /tasks/next", async () => {
    const bundle = [{ user_task_id: 1, task_type: "fill_in_the_blanks" }];
    server.use(http.post(`${API}/tasks/next`, () => HttpResponse.json(bundle)));

    const { result } = renderHookWithProviders(() => useNextTask());

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(bundle);
  });

  it("does not fetch while disabled", async () => {
    let hits = 0;
    server.use(
      http.post(`${API}/tasks/next`, () => {
        hits += 1;
        return HttpResponse.json([]);
      }),
    );

    const { result } = renderHookWithProviders(() => useNextTask(false));

    // `enabled: false` keeps the query idle — nothing is requested.
    expect(result.current.fetchStatus).toBe("idle");
    expect(hits).toBe(0);
  });

  it("surfaces an error without retrying (404/409/503 are real states)", async () => {
    server.use(
      http.post(`${API}/tasks/next`, () =>
        HttpResponse.json({ detail: "no session" }, { status: 409 }),
      ),
    );

    const { result } = renderHookWithProviders(() => useNextTask());

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.data).toBeUndefined();
  });
});
