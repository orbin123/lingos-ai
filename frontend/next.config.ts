import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig: NextConfig = {
  // Security headers (G7). HSTS uses a short 1-day max-age to start, per the
  // production plan's "start with a short max-age"; no `preload` (hard to
  // reverse). Applied to every route. Vercel terminates TLS, so HSTS is safe.
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "Strict-Transport-Security",
            value: "max-age=86400; includeSubDomains",
          },
          { key: "X-Content-Type-Options", value: "nosniff" },
        ],
      },
    ];
  },
};

export default withSentryConfig(nextConfig, {
  // Source-map upload identity — set in Vercel/CI. Without SENTRY_AUTH_TOKEN
  // the build still succeeds; source-map upload is simply skipped.
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,
  authToken: process.env.SENTRY_AUTH_TOKEN,
  sourcemaps: { disable: !process.env.SENTRY_AUTH_TOKEN },
  silent: !process.env.CI,
  telemetry: false,
});
