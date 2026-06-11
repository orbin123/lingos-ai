/**
 * Pending-email-verification state, shared by register → verify-email →
 * login flows. sessionStorage (not localStorage) on purpose: it should not
 * outlive the tab — the backend is the real source of truth and the page
 * falls back to asking for the email.
 */

const EMAIL_KEY = "pending_verify_email";
const SENT_AT_KEY = "pending_verify_sent_at";

export function setPendingVerification(email: string): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(EMAIL_KEY, email);
  sessionStorage.setItem(SENT_AT_KEY, String(Date.now()));
}

export function getPendingEmail(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(EMAIL_KEY);
}

/** Seconds remaining in the resend cooldown, based on the last send time. */
export function getResendCooldownLeft(cooldownSeconds = 60): number {
  if (typeof window === "undefined") return 0;
  const sentAt = Number(sessionStorage.getItem(SENT_AT_KEY) || 0);
  if (!sentAt) return 0;
  const elapsed = (Date.now() - sentAt) / 1000;
  return Math.max(0, Math.ceil(cooldownSeconds - elapsed));
}

export function markOtpSentNow(): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(SENT_AT_KEY, String(Date.now()));
}

export function clearPendingVerification(): void {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(EMAIL_KEY);
  sessionStorage.removeItem(SENT_AT_KEY);
}
