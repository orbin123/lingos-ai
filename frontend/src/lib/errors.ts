import { AxiosError } from "axios";

export function getApiErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    // FastAPI returns errors as { detail: "..." } or, for structured auth
    // errors, { detail: { code, message, ... } }
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (detail && typeof detail.message === "string") return detail.message;
    if (error.message) return error.message;
  }
  return "Something went wrong. Please try again.";
}

/** Machine-readable error code from structured auth errors
 * (e.g. "email_unverified", "otp_expired"), or null. */
export function getApiErrorCode(error: unknown): string | null {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail;
    if (detail && typeof detail.code === "string") return detail.code;
  }
  return null;
}
