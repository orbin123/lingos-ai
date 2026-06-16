import { vi } from "vitest";

// ---------------------------------------------------------------------------
// next/navigation — App Router hooks throw "expected app router to be mounted"
// in jsdom. A global default mock keeps every component/hook renderable; tests
// that need specific search params re-declare `vi.mock("next/navigation", ...)`
// at their own top (a per-file mock overrides this one). The spies are created
// via `vi.hoisted` so the `vi.mock` factory below — hoisted above imports — can
// reference them. We export a *plain* const derived from the hoisted object
// (not the `vi.hoisted` call directly) so this module can be imported by tests
// to assert navigation without tripping Vitest's "cannot export hoisted
// variable" rule.
// ---------------------------------------------------------------------------
const navMocks = vi.hoisted(() => ({
  router: {
    push: vi.fn(),
    replace: vi.fn(),
    refresh: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    prefetch: vi.fn(() => Promise.resolve()),
  },
}));

vi.mock("next/navigation", () => ({
  useRouter: () => navMocks.router,
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
  redirect: vi.fn(),
  notFound: vi.fn(),
}));

export const routerMock = navMocks.router;
