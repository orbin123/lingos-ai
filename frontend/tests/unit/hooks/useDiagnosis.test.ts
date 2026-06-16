import { describe, expect, it } from "vitest";
import { waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";

import { useDiagnosis } from "@/hooks/useDiagnosis";
import { useDiagnosisStore } from "@/store/diagnosisStore";
import type { DiagnosisInput } from "@/lib/validators/diagnosis";
import { server } from "../../setup/msw/server";
import { routerMock } from "../../setup/router-mock";
import { renderHookWithProviders } from "../../utils/render";

const API = "http://localhost:8000";

// Minimal but structurally-complete input — diagnosisApi.submit reads each of
// these nested fields when assembling the request body.
const INPUT: DiagnosisInput = {
  self_assessment: "intermediate",
  fill_blank: { answers: { Q1: "is" } },
  writing: { response_text: "I went to the market yesterday." },
  read_aloud: {
    overall_score: 80,
    accuracy_score: 85,
    fluency_score: 78,
    completeness_score: 90,
    prosody_score: 75,
    words: [],
  },
} as unknown as DiagnosisInput;

describe("useDiagnosis", () => {
  it("stores the result and routes to /diagnosis/result on success", async () => {
    const dResult = { level: "B1", scores: { grammar: 6.2 } };
    server.use(
      http.post(`${API}/diagnosis/submit`, () => HttpResponse.json(dResult)),
    );

    const { result } = renderHookWithProviders(() => useDiagnosis());
    result.current.mutate(INPUT);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(useDiagnosisStore.getState().result).toEqual(dResult);
    expect(routerMock.push).toHaveBeenCalledWith("/diagnosis/result");
  });

  it("does not store or navigate when submit fails", async () => {
    server.use(
      http.post(`${API}/diagnosis/submit`, () =>
        HttpResponse.json({ detail: "server error" }, { status: 500 }),
      ),
    );

    const { result } = renderHookWithProviders(() => useDiagnosis());
    result.current.mutate(INPUT);

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(useDiagnosisStore.getState().result).toBeNull();
    expect(routerMock.push).not.toHaveBeenCalled();
  });
});
