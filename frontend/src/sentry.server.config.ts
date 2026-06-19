// Server-side (Node runtime) Sentry init. Accepts SENTRY_DSN or the public DSN
// so a single value can be configured. No DSN → no-op.
import * as Sentry from "@sentry/nextjs";

const dsn = process.env.SENTRY_DSN ?? process.env.NEXT_PUBLIC_SENTRY_DSN;

Sentry.init({
  dsn,
  enabled: Boolean(dsn),
  tracesSampleRate: 0.1,
});
