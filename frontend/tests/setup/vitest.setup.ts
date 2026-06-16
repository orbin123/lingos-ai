import "@testing-library/jest-dom/vitest";

import { afterAll, afterEach, beforeAll, vi } from "vitest";
import { cleanup } from "@testing-library/react";

import { server } from "./msw/server";
import { resetAllStores } from "../utils/resetStores";

// next/navigation is mocked in a dedicated module (see ./router-mock); tests
// that need to assert navigation `import { routerMock } from "./router-mock"`.
import "./router-mock";

// ---------------------------------------------------------------------------
// jsdom polyfills — globals jsdom doesn't implement that app components touch.
// Inert when unused, so we install them once globally rather than per-test.
// ---------------------------------------------------------------------------
class MockIntersectionObserver {
  readonly root = null;
  readonly rootMargin = "";
  readonly thresholds: ReadonlyArray<number> = [];
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
  takeRecords = vi.fn(() => []);
}
vi.stubGlobal("IntersectionObserver", MockIntersectionObserver);

Object.defineProperty(HTMLMediaElement.prototype, "play", {
  configurable: true,
  value: vi.fn(() => Promise.resolve()),
});
Object.defineProperty(HTMLMediaElement.prototype, "pause", {
  configurable: true,
  value: vi.fn(),
});
Object.defineProperty(HTMLMediaElement.prototype, "load", {
  configurable: true,
  value: vi.fn(),
});

Element.prototype.scrollIntoView = vi.fn();

// jsdom (v25 under Vitest) exposes a `localStorage` object whose methods are
// missing, so `localStorage.setItem` throws "is not a function". authStore and
// the api.ts interceptor both depend on a working Storage, so install a real
// in-memory one. Inert if jsdom ever ships a functional Storage.
if (typeof localStorage === "undefined" || typeof localStorage.setItem !== "function") {
  class MemoryStorage implements Storage {
    private store = new Map<string, string>();
    get length() {
      return this.store.size;
    }
    clear() {
      this.store.clear();
    }
    getItem(key: string) {
      return this.store.has(key) ? this.store.get(key)! : null;
    }
    key(index: number) {
      return Array.from(this.store.keys())[index] ?? null;
    }
    removeItem(key: string) {
      this.store.delete(key);
    }
    setItem(key: string, value: string) {
      this.store.set(key, String(value));
    }
  }
  const storage = new MemoryStorage();
  Object.defineProperty(globalThis, "localStorage", { configurable: true, value: storage });
  Object.defineProperty(window, "localStorage", { configurable: true, value: storage });
}

if (!("createObjectURL" in URL)) {
  // @ts-expect-error jsdom lacks object-URL support
  URL.createObjectURL = vi.fn(() => "blob:mock");
  // @ts-expect-error jsdom lacks object-URL support
  URL.revokeObjectURL = vi.fn();
}

Object.defineProperty(navigator, "mediaDevices", {
  configurable: true,
  value: {
    getUserMedia: vi.fn(() =>
      Promise.resolve({ getTracks: () => [{ stop: vi.fn() }] }),
    ),
  },
});

// ---------------------------------------------------------------------------
// MSW — one server for the whole suite; unmocked requests fail loudly so no
// test can reach the real network (the project's first guiding principle).
// ---------------------------------------------------------------------------
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));

afterEach(() => {
  cleanup();
  server.resetHandlers();
  vi.clearAllMocks();
  // jsdom's localStorage persists across tests in a file; authStore.setToken
  // and the api.ts interceptor both read/write the "token" key, so a token from
  // one test would ride along on the next test's requests. Clear it explicitly.
  localStorage.clear();
  resetAllStores();
});

afterAll(() => server.close());
