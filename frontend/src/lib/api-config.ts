/**
 * Single source of truth for the backend API base URL (audit F1).
 *
 * Before this, `process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"` was
 * duplicated across ~10 files (with `||`/`??` variants and ad-hoc ws:// and
 * trailing-slash handling). Centralizing it here means a prod misconfig fails
 * uniformly, and there's exactly one place to change the fallback.
 */

/** HTTP(S) base URL for the backend API, e.g. `https://api.lingosai.com`. */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * WebSocket base URL derived from {@link API_BASE_URL}.
 * `http` -> `ws`, `https` -> `wss` (the leading-`http` swap covers both).
 */
export const WS_BASE_URL = API_BASE_URL.replace(/^http/, "ws");

/**
 * Resolve a backend-relative media path (e.g. `/audio/x.mp3`) to an absolute
 * URL. Absolute inputs are returned unchanged. Joins without a double slash.
 */
export function resolveMediaUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path;
  const base = API_BASE_URL.replace(/\/$/, "");
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${base}${suffix}`;
}
