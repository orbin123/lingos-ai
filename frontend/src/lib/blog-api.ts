// Public blog API — server-safe helpers.
//
// These use the native `fetch` (NOT the shared axios `api` in src/lib/api.ts,
// which is bound to localStorage/window) so they work inside React Server
// Components. Published-post reads are unauthenticated.

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Revalidate published content every 60s (ISR) — good enough for a blog and
// keeps the pages SEO-friendly without going fully dynamic.
const REVALIDATE_SECONDS = 60;

export interface BlogPostListItem {
  id: number;
  title: string;
  slug: string;
  excerpt: string | null;
  cover_image_url: string | null;
  category: string | null;
  published_at: string | null;
}

export interface BlogPostDetail extends BlogPostListItem {
  content: string;
  author_name: string;
}

/** Prefix backend-relative media paths (e.g. `/blog-media/…`) with the API
 *  origin so <img> tags resolve cross-origin in dev. Absolute URLs pass through. */
export function absolutizeMediaUrl(
  url: string | null | undefined,
): string | null {
  if (!url) return null;
  if (/^https?:\/\//i.test(url)) return url;
  return `${API_BASE}${url.startsWith("/") ? "" : "/"}${url}`;
}

export function formatBlogDate(value: string | null | undefined): string {
  if (!value) return "";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

export async function fetchPublishedPosts(
  limit?: number,
): Promise<BlogPostListItem[]> {
  const qs = limit ? `?limit=${limit}` : "";
  try {
    const res = await fetch(`${API_BASE}/blog${qs}`, {
      next: { revalidate: REVALIDATE_SECONDS },
    });
    if (!res.ok) return [];
    return (await res.json()) as BlogPostListItem[];
  } catch {
    return [];
  }
}

export async function fetchPostBySlug(
  slug: string,
): Promise<BlogPostDetail | null> {
  try {
    const res = await fetch(`${API_BASE}/blog/${encodeURIComponent(slug)}`, {
      next: { revalidate: REVALIDATE_SECONDS },
    });
    if (!res.ok) return null;
    return (await res.json()) as BlogPostDetail;
  } catch {
    return null;
  }
}

export async function fetchRelatedPosts(
  slug: string,
  limit = 3,
): Promise<BlogPostListItem[]> {
  try {
    const res = await fetch(
      `${API_BASE}/blog/${encodeURIComponent(slug)}/related?limit=${limit}`,
      { next: { revalidate: REVALIDATE_SECONDS } },
    );
    if (!res.ok) return [];
    return (await res.json()) as BlogPostListItem[];
  } catch {
    return [];
  }
}
