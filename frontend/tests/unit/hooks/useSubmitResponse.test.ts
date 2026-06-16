import { describe, expect, it } from "vitest";
import { waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";

import { useSubmitResponse } from "@/hooks/useSubmitResponse";
import { useTaskStore } from "@/store/taskStore";
import { server } from "../../setup/msw/server";
import { routerMock } from "../../setup/router-mock";
import { renderHookWithProviders } from "../../utils/render";

const API = "http://localhost:8000";
const PAYLOAD = { user_task_id: 7, content: { Q1: "answer" } };

describe("useSubmitResponse", () => {
  it("stores the graded result and routes to /task/result on success", async () => {
    const graded = { id: 99, overall_score: 8.5, feedback: "Nice work" };
    server.use(
      http.post(`${API}/responses/submit`, () => HttpResponse.json(graded)),
    );

    const { result } = renderHookWithProviders(() => useSubmitResponse());
    result.current.mutate(PAYLOAD);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(useTaskStore.getState().result).toEqual(graded);
    expect(routerMock.push).toHaveBeenCalledWith("/task/result");
  });

  it("does not store or navigate when the submit fails", async () => {
    server.use(
      http.post(`${API}/responses/submit`, () =>
        HttpResponse.json({ detail: "bad payload" }, { status: 400 }),
      ),
    );

    const { result } = renderHookWithProviders(() => useSubmitResponse());
    result.current.mutate(PAYLOAD);

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(useTaskStore.getState().result).toBeNull();
    expect(routerMock.push).not.toHaveBeenCalled();
  });
});
