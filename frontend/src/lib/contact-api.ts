// Public contact API — unauthenticated.
//
// Uses the native `fetch` (NOT the shared axios `api` in src/lib/api.ts, which
// attaches a JWT and redirects to /login on 401) since the marketing contact
// form is for logged-out visitors. Same rationale as `lib/blog-api.ts`.

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ContactRequest {
  full_name: string;
  email: string;
  subject: string;
  message: string;
}

export interface ContactResponse {
  ok: boolean;
  message: string;
}

/** POST a contact message. Throws an Error with a human-readable message on
 *  failure (reads FastAPI's `detail`, including the 422 validation shape). */
export async function sendContactMessage(
  payload: ContactRequest,
): Promise<ContactResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/contact`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error("Network error. Please check your connection and try again.");
  }

  if (!res.ok) {
    throw new Error(await extractErrorMessage(res));
  }
  return (await res.json()) as ContactResponse;
}

async function extractErrorMessage(res: Response): Promise<string> {
  const fallback =
    res.status === 429
      ? "Too many messages. Please wait a moment and try again."
      : "Something went wrong. Please try again later.";
  try {
    const data = await res.json();
    const detail = (data as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
    // FastAPI 422 returns detail as an array of validation errors.
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string };
      if (first?.msg) return first.msg;
    }
  } catch {
    /* non-JSON body — fall through */
  }
  return fallback;
}
