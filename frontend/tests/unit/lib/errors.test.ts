import { describe, expect, it } from "vitest";
import { AxiosError, AxiosHeaders } from "axios";

import { getApiErrorCode, getApiErrorMessage } from "@/lib/errors";

/** Build an AxiosError carrying a FastAPI-style `{ detail }` body. */
function axiosErrorWith(detail: unknown, status = 403): AxiosError {
  const err = new AxiosError("Request failed with status code " + status);
  err.response = {
    data: { detail },
    status,
    statusText: "",
    headers: {},
    config: { headers: new AxiosHeaders() },
  };
  return err;
}

describe("getApiErrorMessage / getApiErrorCode", () => {
  it("reads the message from a structured oauth_account error", () => {
    const err = axiosErrorWith({
      code: "oauth_account",
      message: "This account uses Google sign-in. Continue with Google.",
    });
    expect(getApiErrorMessage(err)).toBe(
      "This account uses Google sign-in. Continue with Google.",
    );
    expect(getApiErrorCode(err)).toBe("oauth_account");
  });

  it("reads a plain-string detail (e.g. invalid credentials)", () => {
    const err = axiosErrorWith("Invalid email or password", 401);
    expect(getApiErrorMessage(err)).toBe("Invalid email or password");
    expect(getApiErrorCode(err)).toBeNull();
  });

  it("falls back gracefully for non-axios errors", () => {
    expect(getApiErrorMessage(new Error("boom"))).toBe(
      "Something went wrong. Please try again.",
    );
    expect(getApiErrorCode(new Error("boom"))).toBeNull();
  });
});
