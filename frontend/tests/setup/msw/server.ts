import { setupServer } from "msw/node";

import { handlers } from "./handlers";

// Node-side MSW server shared by every test (started in vitest.setup.ts).
// Per-test overrides go through `server.use(...)`; they are reset after each
// test by the `afterEach` hook.
export const server = setupServer(...handlers);
