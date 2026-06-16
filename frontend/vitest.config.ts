import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";

// Resolve `@/` the same way tsconfig does (`@/*` → `./src/*`) so tests import
// the REAL source — no transpile-in-vm, no hand-copied logic that silently
// drifts (the failure mode of the old `tests/*.test.mjs` suite).
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup/vitest.setup.ts"],
    include: ["tests/**/*.{test,spec}.{ts,tsx}"],
    // Pin the API base so the app's axios instance (src/lib/api.ts) and the MSW
    // handlers (tests/setup/msw/handlers.ts) read the SAME value — a stray shell
    // NEXT_PUBLIC_API_URL must not desync them and silently un-mock requests.
    env: { NEXT_PUBLIC_API_URL: "http://localhost:8000" },
    // Deterministic + offline: MSW errors on any unmocked request (see setup).
    coverage: {
      provider: "v8",
      reporter: ["text", "json-summary", "html"],
      reportsDirectory: "./coverage",
      include: ["src/**"],
      exclude: [
        "src/**/*.d.ts",
        "src/app/**/layout.tsx",
        "src/app/**/loading.tsx",
        "src/app/**/not-found.tsx",
        "src/**/*.stories.{ts,tsx}",
      ],
    },
  },
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
});
