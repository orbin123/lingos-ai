import { describe, expect, it } from "vitest";
import { waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";

import {
  useStartTodaySession,
  useSubmitActivity,
} from "@/hooks/useSessionsFlow";
import { useSessionStore } from "@/store/sessionStore";
import { server } from "../../setup/msw/server";
import { renderHookWithProviders } from "../../utils/render";

const API = "http://localhost:8000";

describe("useSessionsFlow", () => {
  describe("useStartTodaySession", () => {
    it("stores the resolved session in the session store", async () => {
      const session = {
        session_id: "sess-1",
        day_id: "day_24_05_03",
        status: "in_progress",
        activities: [],
      };
      server.use(
        http.post(`${API}/api/sessions/start-today`, () =>
          HttpResponse.json(session),
        ),
      );

      const { result } = renderHookWithProviders(() => useStartTodaySession());
      result.current.mutate();

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(useSessionStore.getState().session).toEqual(session);
    });
  });

  describe("useSubmitActivity", () => {
    it("snapshots the returned feedback/evaluation for the submitted activity", async () => {
      const submitResponse = {
        feedback: { summary: "Good attempt" },
        evaluation: { score: 7 },
      };
      server.use(
        http.post(
          `${API}/api/sessions/sess-1/activities/2/submit`,
          () => HttpResponse.json(submitResponse),
        ),
      );

      const { result } = renderHookWithProviders(() =>
        useSubmitActivity("sess-1"),
      );
      result.current.mutate({
        sequence: 2,
        archetype_id: "READ_CLOZE",
        payload: { content: {} } as never,
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(useSessionStore.getState().lastFeedback).toEqual({
        sequence: 2,
        archetype_id: "READ_CLOZE",
        feedback: submitResponse.feedback,
        evaluation: submitResponse.evaluation,
      });
    });
  });
});
