// Browser-side Sentry init (Next.js App Router instrumentation hook).
// No DSN (local/dev) → the SDK no-ops, mirroring the backend's behaviour.
import * as Sentry from "@sentry/nextjs";

const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;

Sentry.init({
  dsn,
  enabled: Boolean(dsn),
  // Match the backend's sample rate (config.py sentry_traces_sample_rate=0.1).
  tracesSampleRate: 0.1,
  // Keep the client bundle lean; enable Session Replay later if needed.
});

// Instruments App Router client-side navigations for tracing.
export const onRouterTransitionStart = Sentry.captureRouterTransitionStart;
