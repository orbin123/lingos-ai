import { type RequestHandler } from "msw";

/**
 * Base URL the app's axios instance targets (see `src/lib/api.ts`, which reads
 * `NEXT_PUBLIC_API_URL`, defaulting to http://localhost:8000). Build handler
 * URLs from this so a base-URL change doesn't silently un-mock every request.
 */
export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Default (success-path) handlers shared across integration tests. Kept empty
 * by default — each integration test composes the handlers it needs via
 * `server.use(...)`, so unit tests of pure logic stay request-free and any
 * unmocked request fails loudly (`onUnhandledRequest: "error"`).
 */
export const handlers: RequestHandler[] = [];
