import { describe, expect, it } from "vitest";

import { getChallengesApiError } from "@/lib/challenges-api";

// getChallengesApiError only inspects `isAxiosError === true` + `response`, so a
// plain object with that flag is a faithful stand-in for a real AxiosError.
function axiosError(status?: number, detail?: unknown, message = "Network Error"): unknown {
  return {
    isAxiosError: true,
    message,
    response: status === undefined ? undefined : { status, data: { detail } },
  };
}

describe("getChallengesApiError", () => {
  it("uses Error.message for a non-axios Error", () => {
    expect(getChallengesApiError(new Error("boom"))).toEqual({ message: "boom" });
  });

  it("falls back to 'Request failed' for a non-Error throwable", () => {
    expect(getChallengesApiError("nope")).toEqual({ message: "Request failed" });
  });

  it("unpacks an object detail with message + attempt_id", () => {
    expect(
      getChallengesApiError(axiosError(409, { message: "In progress", attempt_id: 7 })),
    ).toEqual({ message: "In progress", status: 409, attemptId: 7 });
  });

  it("uses a string detail verbatim", () => {
    expect(getChallengesApiError(axiosError(400, "Bad payload"))).toEqual({
      message: "Bad payload",
      status: 400,
    });
  });

  it("maps known statuses to friendly messages when there is no detail", () => {
    expect(getChallengesApiError(axiosError(403)).message).toMatch(/locked/i);
    expect(getChallengesApiError(axiosError(409)).message).toMatch(/in progress/i);
    expect(getChallengesApiError(axiosError(429)).message).toMatch(/limit reached/i);
    expect(getChallengesApiError(axiosError(500)).message).toMatch(/server error/i);
  });

  it("falls back to the axios message for an unmapped status", () => {
    expect(getChallengesApiError(axiosError(418, undefined, "I am a teapot"))).toEqual({
      message: "I am a teapot",
      status: 418,
    });
  });
});
