# 3. Frontend architecture

The frontend uses Next.js 16 App Router, React 19, TypeScript strict mode, Tailwind v4, Axios, TanStack Query, Zustand, React Hook Form, Zod, Vitest, and Sentry.

## `src/app/`

This is the route tree. Parentheses such as `(auth)` are route groups and do not appear in URLs. Square brackets are dynamic segments, for example `sessions/[sessionId]`. Pages cover public marketing, authentication, learner dashboard/course/session flows, diagnosis, challenges, payment, blog, and admin screens.

## Data and state

`src/lib/api.ts` is the shared Axios client. It attaches the JWT and handles an expired non-auth session. Domain wrappers such as `sessions-api.ts`, `diagnosis-api.ts`, and `admin-api.ts` keep endpoint knowledge out of components. TanStack Query owns server cache and refetching. Zustand owns small client workflows such as auth, session, task, diagnosis, and feedback state.

## Chat and widgets

The chat UI is assembled from teaching, task, evaluation, and feedback components. A backend widget key is normalized by the backend mapping and then adapted by `contractTaskAdapter.ts`/runtime mappings to a React renderer. Adding a new activity therefore crosses a contract boundary: scoring archetype, backend session contract, backend widget mapping, task schema, and frontend widget.

## Browser flow to remember

The learner opens a route, a hook calls a domain API wrapper, the API returns typed JSON or a WebSocket event, a store/query cache updates, and a widget renders the normalized payload. Audio recorders send speech to transcription; returned transcript/audio URLs are then used by the evaluation and feedback UI.
