# PROJECT_INTERNAL_MAP.md

This document describes how the application works today based on the current codebase. It is intentionally honest about overlap, older systems, and phase-labeled code that is still mounted.

## 1. Application Overview

This project has grown into a full-stack AI English learning platform with a polished learner-facing frontend, a FastAPI backend, PostgreSQL data models, AI task generation/evaluation/feedback agents, progress tracking, streaks, challenges, payments, and admin surfaces.

The original product idea is still visible: diagnose user weaknesses, generate personalized English tasks, evaluate responses, provide corrective feedback, and track progress. The current implementation, however, is not one clean pipeline. It has two parallel learning systems:

1. A legacy daily task/chat system.
   - Frontend: `frontend/src/components/dashboard/DailyTaskPanel.tsx`, `frontend/src/app/task/chat/*`.
   - Backend: `backend/app/modules/tasks`, `backend/app/modules/responses`, `backend/app/modules/learning_session`.
   - Data: `tasks`, `user_tasks`, `user_responses`, `evaluations`, `feedbacks`, `learning_sessions`, `daily_plans`.
   - This is still what the main dashboard uses for today's plan.

2. A newer sessions system.
   - Frontend: `frontend/src/app/sessions/*`, `frontend/src/components/sessions/*`.
   - Backend: `backend/app/modules/sessions`, `backend/app/scoring`, `backend/app/modules/curriculum/v2_models.py`.
   - Data: `curriculum_weeks`, `curriculum_days`, `task_archetypes`, `daily_sessions`, `activity_attempts`, `activity_evaluations`, `activity_feedback`, `session_scorecards`.
   - This is feature-flagged with `settings.use_new_session_flow` on the backend and `NEXT_PUBLIC_USE_NEW_SESSION_FLOW` on the frontend. The backend flag currently defaults to on in `backend/app/core/config.py`, but the frontend dashboard still uses the legacy task panel.

Main purpose:
- Help learners improve English through daily personalized practice.
- Use diagnosis and profile data to seed progress and personalize content.
- Use AI for generation, evaluation, feedback, teaching turns, personalization extraction, and IELTS challenge content.

Main user flow today:
- A user signs up or logs in.
- If diagnosis is incomplete, the dashboard redirects to `/diagnosis`.
- The user completes a multi-step diagnosis.
- The diagnosis writes skill scores and points, marks the profile as diagnosed, and shows a result page from an in-memory store.
- The user purchases/selects a plan on `/pricing`, which creates or updates a legacy `UserEnrollment`.
- The dashboard shows today's plan through the legacy `/tasks/next` bundle.
- The learner opens `/task/chat`, starts a legacy learning session, receives teaching over WebSocket, completes widgets inside chat, gets evaluation and feedback, and returns to the dashboard.

Core learning loop today:
1. Diagnose: rule/stub/speech evaluators produce initial skill scores.
2. Enroll: mock purchase attaches the learner to a 24-week or 48-week course.
3. Plan/generate: legacy task bundle is created from enrollment, rotation, topic data, and task generator.
4. Teach: legacy chat session streams a teaching turn before practice.
5. Practice: widgets collect answers or speech transcripts.
6. Evaluate: rule-based or LLM evaluators score answers.
7. Feedback: feedback agent produces structured corrective feedback.
8. Persist: legacy tables store response/evaluation/feedback; WMA score and points are updated.
9. Progress: dashboard/stats read from skill points, progress logs, and legacy completed tasks.
10. Advance: `/tasks/complete-day` advances the legacy enrollment day when all current tasks are completed.

Major implemented features:
- Email/password auth, Google OAuth, JWT auth, roles, permissions, and admin-only routes.
- Multi-step diagnosis with fill-in-blanks, writing, read-aloud recording, Whisper transcription, speech scoring, and AI diagnosis feedback.
- Mock pricing/purchase flow that enrolls users into a course.
- Legacy daily tasks, chat-based teaching sessions, WebSocket streaming, task widgets, evaluation, feedback, retries, and day advancement.
- New sessions API with deterministic planning, LLM task generation, LLM evaluation, LLM feedback, scorecards, and streak recording.
- Skill score, point, progress, and stats endpoints.
- Streak read/write API and activity grid.
- IELTS-style challenge framework with generation, timed attempts, reading/listening deterministic scoring, writing/speaking AI scoring, TTS/STT integration, and challenge feedback.
- Admin console for users, roles, permissions, task templates, AI logs, feedback review, audit logs, subscriptions, and payments.
- AI media/debug endpoints for LLM ping, TTS, image generation, pronunciation scoring, and STT.

What seems incomplete or experimental:
- The new sessions frontend is still a Phase-style shell. `frontend/src/components/sessions/widgets/registry.tsx` maps every new-session widget to `GenericResponseWidget`.
- The main dashboard still calls legacy `/tasks/next`, not the new `/api/sessions/start` flow.
- Diagnosis writing evaluation is still a word-count stub in `backend/app/modules/diagnosis/evaluators.py`.
- The README mentions Celery/Redis background jobs, but no Celery worker/job system appears to be active in the code inspected.
- New session feedback intentionally passes `task_content={}` into the feedback prompt in `backend/app/ai/sessions/llm_feedback.py`, so the feedback agent may not see the exact prompt/task the learner answered.
- Progress pages mix new and legacy scoring data. They read current display scores from `SkillPoints`, but recent activities and weekly task counts mostly come from legacy `UserTask`/`Evaluation` rows.
- Streaks are written by new session completion, while the main dashboard's legacy daily chat path does not appear to call `StreakService`.

## 2. Current Folder Structure

Readable high-level tree:

```text
.
|-- MD_FILES/
|-- backend/
|   |-- alembic/
|   |   `-- versions/
|   |-- app/
|   |   |-- ai/
|   |   |   |-- agents/
|   |   |   |   `-- prompts/ielts/
|   |   |   |-- embeddings/
|   |   |   |-- graphs/
|   |   |   |-- imagegen/
|   |   |   |-- llm/
|   |   |   |-- pronunciation/
|   |   |   |-- sessions/
|   |   |   |-- storage/
|   |   |   |-- stt/
|   |   |   `-- tts/
|   |   |-- core/
|   |   |-- data/
|   |   |   |-- courses/
|   |   |   |   `-- curriculum_v2/
|   |   |   `-- task_templates/
|   |   |-- modules/
|   |   |   |-- admin/
|   |   |   |-- auth/
|   |   |   |-- challenges/
|   |   |   |-- curriculum/
|   |   |   |-- diagnosis/
|   |   |   |-- learning_session/
|   |   |   |-- personalization/
|   |   |   |-- progress/
|   |   |   |-- responses/
|   |   |   |-- sessions/
|   |   |   |-- skills/
|   |   |   |-- streaks/
|   |   |   |-- subscriptions/
|   |   |   `-- tasks/
|   |   |-- scoring/
|   |   `-- tasks/
|   |       `-- schemas/
|   |-- docs/
|   |-- scripts/
|   `-- tests/
|-- frontend/
|   |-- public/
|   |-- src/
|   |   |-- app/
|   |   |-- components/
|   |   |-- hooks/
|   |   |-- lib/
|   |   |-- providers/
|   |   `-- store/
|   `-- tests/
|-- README.md
|-- docker-compose.yml
|-- backup.sql
`-- backup_pre_phase8.sql
```

Folder responsibilities:

`backend/`
- Responsibility: FastAPI backend, database models, AI orchestration, business logic, migrations, and tests.
- Depends on: PostgreSQL, OpenAI/LangChain, optional Azure Speech, optional Pinecone/HF embeddings.
- Status: core.

`backend/app/main.py`
- Responsibility: creates the FastAPI app, mounts static AI assets, adds CORS/rate-limit middleware, and mounts all routers.
- Core because it defines the public backend surface.

`backend/app/core/`
- Responsibility: config, database session/base, security, shared mixins, rate limiting.
- Files: `config.py`, `database.py`, `security.py`, `base.py`, `mixins.py`, `rate_limit.py`.
- Depends on: environment variables and SQLAlchemy.
- Status: core.

`backend/app/modules/`
- Responsibility: domain modules using a route -> service -> repository/model pattern.
- Depends on: `backend/app/core`, `backend/app/ai`, `backend/app/scoring`, and other modules.
- Status: core, but several modules are legacy/overlapping.

`backend/app/modules/auth/`
- Responsibility: users, profiles, OAuth accounts, roles, permissions, JWT dependency helpers.
- Depends on: `core/security`, `core/database`, `curriculum` for `/auth/me` enrollment data, `personalization` for profile refresh.
- Status: core.

`backend/app/modules/diagnosis/`
- Responsibility: diagnosis start/transcribe/submit flow, rule-based fill blank scoring, stub writing scoring, read-aloud scoring, initial skill/point seeding.
- Depends on: `ai/stt`, `ai/agents/diagnosis_feedback.py`, `personalization`, `skills`, `progress`.
- Status: core.

`backend/app/modules/curriculum/`
- Responsibility: legacy courses/enrollments/rotation and new v2 curriculum models.
- Important files:
  - `models.py`: legacy `Course`, `UserEnrollment`, `EnrollmentSkillHistory`, `DailyPlan`.
  - `rotation.py`: deprecated legacy rotation engine.
  - `topics.py`: legacy topic lookup.
  - `v2_models.py`, `v2_repository.py`: new curriculum weeks/days/archetypes.
- Depends on: `tasks.models` for legacy task activity enums.
- Status: mixed. Legacy curriculum is active through dashboard; v2 curriculum is used by new sessions.

`backend/app/modules/tasks/`
- Responsibility: legacy task templates and assigned `UserTask`s.
- Important files:
  - `models.py`: `Task`, `TaskSkill`, `UserTask`.
  - `service.py`: deprecated but still live `/tasks/next` bundle generation.
  - `routes.py`: `/tasks/next`, `/tasks/superuser-jump`, retry, complete-day.
- Depends on: legacy curriculum, AI task generator, TTS for listen tasks, skills.
- Status: core for current dashboard, but marked deprecated.

`backend/app/modules/responses/`
- Responsibility: legacy submission, evaluation, feedback, WMA score update, points update, embeddings.
- Important files:
  - `models.py`: `UserResponse`, `Evaluation`, `Feedback`.
  - `service.py`: deprecated but still live submission loop.
  - `feedback_service.py`: legacy feedback persistence around the feedback agent.
- Depends on: `ai/agents/evaluator.py`, `ai/agents/feedback.py`, `progress`, `embeddings`.
- Status: core for legacy chat/results, but marked deprecated.

`backend/app/modules/learning_session/`
- Responsibility: legacy chat-driven learning session REST and WebSocket flow.
- Important files:
  - `router.py`: `/api/learning/sessions/start`, restart, by-task, and `/ws/learning/{session_id}`.
  - `service.py`: deprecated but still active orchestration.
  - `models.py`: `learning_sessions`.
- Depends on: `ai/graphs/nodes.py`, teacher/task/evaluator/feedback agents, legacy tasks/curriculum.
- Status: active legacy core, planned for removal per comments.

`backend/app/modules/sessions/`
- Responsibility: new daily session lifecycle: start, next activity, submit, complete, scorecard.
- Important files:
  - `service.py`: orchestrates `daily_sessions`.
  - `planner.py`: deterministic planner.
  - `scoring_writer.py`: writes new scorecards into points tables.
  - `models.py`: new session tables.
  - `routes.py`: `/api/sessions/*`.
- Depends on: `curriculum/v2_models.py`, `app/scoring`, `app/ai/sessions`.
- Status: new core, but not fully integrated into the main dashboard UI.

`backend/app/modules/progress/`
- Responsibility: current skill display scores, WMA history, points history, stats dashboard, recent activities.
- Important files:
  - `models.py`: `ProgressLog`, `SkillPoints`, `SkillPointsLog`.
  - `service.py`: legacy WMA and points updater.
  - `routes.py`: `/progress/scores`, `/progress/history`, `/progress/stats`, `/progress/activities`, `/progress/skill-points`, `/progress/points-history`.
- Depends on: legacy `Evaluation`/`UserTask`, `SkillPoints`, `ProgressLog`.
- Status: core, but it blends legacy and new scoring concepts.

`backend/app/modules/streaks/`
- Responsibility: daily streak state, local-date activity rows, activity grid, animation state.
- Important files:
  - `service.py`: streak state machine.
  - `models.py`: `DailyActivity`, `StreakFreezeUsage`.
  - `dates.py`: timezone/local date helpers.
- Depends on: `UserProfile`, new `daily_sessions` via `last_session_id`.
- Status: core for new session completion; incompletely wired to legacy dashboard completion.

`backend/app/modules/challenges/`
- Responsibility: generic challenge framework and IELTS challenge flow.
- Important files:
  - `models.py`: `Challenge`, `ChallengeLevel`, `ChallengeAttempt`.
  - `service.py`: generation, attempt lifecycle, evaluation, feedback, audio.
  - `routes.py`: `/api/v1/challenges/*`.
- Depends on: IELTS AI agents, TTS, STT, storage.
- Status: supporting but substantial product surface.

`backend/app/modules/admin/`
- Responsibility: admin dashboard APIs, audit logs, AI request logs, feedback review, task template management, billing views.
- Depends on: auth roles/permissions, tasks, feedback, billing models.
- Status: supporting/admin core.

`backend/app/modules/subscriptions/`
- Responsibility: mock purchases, course enrollment attachment, pause access, notification settings, delete account.
- Depends on: legacy curriculum/course enrollment and admin audit.
- Status: supporting product/business surface.

`backend/app/modules/personalization/`
- Responsibility: service wrapper for extracting structured personalization and caching it on `user_profiles`.
- Depends on: `backend/app/ai/agents/personalization.py`.
- Status: supporting core for personalization.

`backend/app/modules/skills/`
- Responsibility: master skill rows and per-user WMA scores.
- Depends on: none beyond core DB.
- Status: core.

`backend/app/ai/`
- Responsibility: all AI-facing service clients and agents.
- Depends on: OpenAI, LangChain, optional Azure, Pinecone/HF.
- Status: core.

`backend/app/ai/agents/`
- Responsibility: legacy/chat/challenge agents:
  - task generator
  - evaluator
  - feedback
  - diagnosis feedback
  - personalization
  - planner
  - teacher
  - IELTS generator/evaluators/feedback
- Status: core, but older and newer prompt systems coexist.

`backend/app/ai/sessions/`
- Responsibility: new sessions-specific LLM task generator, evaluator, feedback generator, and prompt builders.
- Depends on: `ai/llm`, `app/scoring`.
- Status: new core, experimental/generic task content.

`backend/app/ai/graphs/`
- Responsibility: LangGraph state/nodes for legacy learning session.
- Important caveat: `learning_session/service.py` manually calls nodes by phase instead of simply running one compiled graph.
- Status: legacy core, somewhat confusing.

`backend/app/scoring/`
- Responsibility: deterministic new scoring engine and task archetype registry.
- Important files:
  - `constants.py`: rewards, caps, sub-skill aliases.
  - `engine.py`: pure score math.
  - `archetypes.py`: source-of-truth archetype definitions for new sessions.
- Depends on: no DB.
- Status: new scoring core.

`backend/app/tasks/schemas/`
- Responsibility: legacy task template registry and Pydantic output schemas for generated task content.
- Depends on: AI task generator and legacy task service.
- Status: active for legacy task/chat; separate from new `task_archetypes`.

`backend/app/data/`
- Responsibility: seed/static data for courses, topics, task templates, and v2 curriculum source.
- Depends on: seed scripts and services that read course topics.
- Status: supporting core.

`backend/alembic/`
- Responsibility: database migrations.
- `backend/alembic/versions/17e15923f549_squashed_initial_schema.py` is the squashed base.
- Later migrations add admin roles/monitoring, challenges, streaks, curriculum v2, sessions, skill labels, and billing/admin permission phases.
- Status: core.

`backend/scripts/`
- Responsibility: operational seed/reset helpers.
- Important files:
  - `seed_curriculum_v2.py`
  - `seed_ielts_challenge.py`
  - `reset_user_cache.py`
- Status: supporting.

`frontend/`
- Responsibility: Next.js app, UI components, client API wrappers, state stores, and frontend tests.
- Depends on: backend API base URL, React Query, Zustand, axios, react-hook-form, zod, lucide-react.
- Status: core.

`frontend/src/app/`
- Responsibility: Next App Router pages.
- Contains marketing pages, auth pages, dashboard, diagnosis, profile/settings, stats, legacy chat/task pages, new session pages, challenge pages, and admin pages.
- Depends on: `components`, `lib`, `hooks`, `store`.
- Status: core.

`frontend/src/components/`
- Responsibility: shared UI and feature components.
- Important subfolders:
  - `dashboard`: current daily task panel and skill preview.
  - `task/task-widgets`: polished legacy chat widgets.
  - `sessions`: new sessions scorecard/feedback/generic widgets.
  - `streak`: activity grid and celebration.
  - `admin`: admin UI primitives/layout.
  - `layout`: shared nav/layout.
- Status: core/supporting; `sessions/widgets` is experimental/generic.

`frontend/src/lib/`
- Responsibility: API clients, shared client helpers, validators, voice recorder hook, skill label mapping.
- Important files:
  - `api.ts`: axios instance and JWT interceptors.
  - `tasks-api.ts`: legacy task/response API types.
  - `sessions-api.ts`: new sessions API types and feature flag.
  - `diagnosis-api.ts`, `auth-api.ts`, `progress-api.ts`, `streak-api.ts`, `courses-api.ts`, `subscriptions-api.ts`, `challenges-api.ts`, `admin-api.ts`.
  - `skill-labels.ts`: client-side alias/label normalization.
- Status: core.

`frontend/src/hooks/`
- Responsibility: React Query and auth guard hooks.
- Important files:
  - `useRequireAuth.ts`
  - `useDiagnosis.ts`
  - `useNextTask.ts`
  - `useSessionsFlow.ts`
  - `useSubmitResponse.ts`
- Status: core.

`frontend/src/store/`
- Responsibility: Zustand local UI/auth state.
- Important files:
  - `authStore.ts`: localStorage JWT and role flags.
  - `diagnosisStore.ts`: in-memory diagnosis result.
  - `sessionStore.ts`: in-memory new sessions UI state.
  - `taskStore.ts`: legacy task state.
- Status: core/supporting.

`MD_FILES/`
- Responsibility: currently empty in this checkout.
- Status: supporting or staging area; not used by runtime code.

Root SQL backups:
- `backup.sql`, `backup_pre_phase8.sql`.
- Status: local backup artifacts, not runtime code.

## 3. Frontend Architecture

Frontend stack:
- Next.js App Router under `frontend/src/app`.
- React 19.
- Zustand for local client state.
- TanStack Query for server data/cache/mutations.
- Axios API client in `frontend/src/lib/api.ts`.
- Tailwind/global CSS plus a lot of inline styles.

Main routes/pages:

Marketing and auth:
- `/`: landing page at `frontend/src/app/page.tsx`.
- `/about`, `/features`, `/how-it-works`, `/pricing`.
- `/login`: route group file `frontend/src/app/(auth)/login/page.tsx`.
- `/register`: `frontend/src/app/(auth)/register/page.tsx`.
- `/callback`: OAuth callback page.

Main learner app:
- `/dashboard`: `frontend/src/app/dashboard/page.tsx`.
- `/diagnosis`: multi-step diagnosis form.
- `/diagnosis/result`: diagnosis result display.
- `/pricing`: plan purchase.
- `/profile`: user profile/personalization.
- `/settings`: purchase/settings/course preferences.
- `/stats`: progress dashboard.
- `/stats/activities`: activity history.

Legacy task/chat:
- `/task/chat`: entry page that starts/resumes a legacy chat session.
- `/task/chat/[sessionId]`: WebSocket chat shell and task widgets.
- `/task/result`: legacy result page.
- `/task/history/[userTaskId]`: stored result/history view.

New sessions:
- `/sessions/start`: manual new-session starter.
- `/sessions/[sessionId]`: new daily session shell.
- `/sessions/[sessionId]/scorecard`: new session scorecard.

Challenges:
- `/challenges`
- `/challenges/ielts`
- `/challenges/ielts/attempt/[id]`

Admin:
- `/admin`
- `/admin/users`
- `/admin/users/[id]`
- `/admin/roles-permissions`
- `/admin/task-templates`
- `/admin/feedback-review`
- `/admin/ai-logs`
- `/admin/ai-logs/[id]`
- `/admin/audit-logs`
- `/admin/payments`
- `/admin/subscriptions`

Dashboard flow:
- `frontend/src/app/dashboard/page.tsx` uses `useRequireAuth()` and `authApi.me`.
- If `/auth/me` says `diagnosis_completed` is false, it redirects to `/diagnosis`.
- If the user has an enrollment, it renders `EnrolledView`.
- `EnrolledView` shows:
  - greeting and week/day from `user.enrollment`;
  - `DailyTaskPanel`;
  - `SkillScorePreview`;
  - streak activity grid via `ActivityGridCard`;
  - some mock right-column widgets like weekly goal/yesterday wins.
- If there is no enrollment, the page renders a no-enrollment view that pushes toward `/pricing`.

Important dashboard coupling:
- The dashboard uses `DailyTaskPanel`.
- `DailyTaskPanel` uses `useNextTask`.
- `useNextTask` calls `tasksApi.getNext`.
- `tasksApi.getNext` calls `POST /tasks/next`.
- That means the main dashboard still uses the legacy task bundle system, not the new `/api/sessions` flow.

Diagnosis/onboarding flow:
- `frontend/src/app/diagnosis/page.tsx` is a four-step form:
  1. About you.
  2. Fill the blanks.
  3. Short writing.
  4. Read aloud.
- It uses `react-hook-form`, `zod`, `frontend/src/lib/validators/diagnosis.ts`, and `useDiagnosis`.
- Read-aloud uses the browser recorder and then `diagnosisApi.transcribe`, which posts audio to `/diagnosis/transcribe`.
- Submit uses `diagnosisApi.submit`, which posts JSON to `/diagnosis/submit`.
- `useDiagnosis` stores the result in `diagnosisStore` and pushes `/diagnosis/result`.
- The result page reads only from in-memory Zustand. Refreshing `/diagnosis/result` loses the result and redirects back to `/diagnosis`.
- The result page multiplies diagnosis scores by 2.5 for display because diagnosis scores are capped at 4.0 but dashboard uses a 0-10 display.

Plan/enrollment flow:
- `/pricing` uses `subscriptionsApi.purchase`, which calls `POST /api/subscriptions/purchase`.
- The backend purchase endpoint records a mock `Purchase`, records a mock `Payment`, and creates/updates legacy `UserEnrollment`.
- `/courses` is no longer used. `frontend/src/app/courses/page.tsx` redirects to `/pricing`.
- `/settings` can update enrollment settings through `coursesApi.updateEnrollmentSettings`.

Legacy chat/task session flow:
- `frontend/src/components/dashboard/DailyTaskPanel.tsx` renders today's task bundle from `/tasks/next`.
- It shows the active task and locks later tasks until prior tasks are completed.
- Clicking the active task pushes to `/task/chat?id=<user_task_id>`.
- `/task/chat`:
  - checks `sessionStorage` via `daily-session-entry.ts` to resume today's session;
  - otherwise calls `POST /api/learning/sessions/start`;
  - passes `user_task_id` if the URL had an `id` query param;
  - routes to `/task/chat/[sessionId]`.
- `/task/chat/[sessionId]`:
  - opens WebSocket `${NEXT_PUBLIC_API_URL}/ws/learning/{sessionId}?token=<JWT>`;
  - renders streamed teaching messages;
  - renders task widgets from `frontend/src/components/task/task-widgets/*`;
  - sends messages of type `user_message`, `task_submission`, and `follow_up_action`;
  - receives `chat_message`, `chat_stream_*`, `ui_event`, and `error`;
  - recognizes `ui_event.widget` values like `mcq`, `fill_in_blanks`, `open_text`, `timed_text`, `structured_essay`, `speak_and_record`, `listen_and_respond`, `storyboard`, `scorecard`, and `feedback_card`.
- Voice input in chat uses `frontend/src/lib/hooks/useVoiceRecorder.ts` and `tasksApi.transcribeAudio`, which posts to `/responses/transcribe-audio`.
- The chat page invalidates `["task", "next"]` and `["me"]` when returning to dashboard so completed tasks and enrollment day changes can refresh.

New sessions flow:
- `frontend/src/lib/sessions-api.ts` is a typed client for `/api/sessions`.
- It is gated by `NEXT_PUBLIC_USE_NEW_SESSION_FLOW === "true"`.
- `/sessions/start` is a manual form with hard-coded default `day_24_01_01`. Comments say Phase 7+ should wire it to dashboard defaults, but that does not appear done.
- `useSessionsFlow.ts` wraps session start, next activity, submit, complete, and scorecard through React Query.
- `/sessions/[sessionId]`:
  - fetches next pending activity;
  - uses `getSessionWidget(ui_widget)`;
  - shows inline feedback after submit;
  - on 409 from next-activity, shows "Complete session";
  - posts `/complete` and routes to scorecard.
- `frontend/src/components/sessions/widgets/registry.tsx` currently maps every backend `ui_widget` to `GenericResponseWidget`.
- `GenericResponseWidget` renders instructions and a single textarea. It can display a "Stub task content" warning if task content has `phase: "stub"`.

Result/feedback pages:
- Diagnosis result: `/diagnosis/result`, in-memory `diagnosisStore`.
- Legacy task history: `/task/history/[userTaskId]`, using stored legacy response/evaluation/feedback.
- Legacy chat result: chat page itself renders scorecard and feedback `ui_event`s.
- New sessions scorecard: `/sessions/[sessionId]/scorecard`, using `SessionScorecard` and either `sessionStore.scorecard` or `GET /api/sessions/{id}/scorecard`.

Shared components:
- Layout/nav:
  - `frontend/src/components/layout/DashboardLayout.tsx`
  - `LandingNavbar.tsx`, `LandingFooter.tsx`, `Logo.tsx`, `Navbar.tsx`
- Auth:
  - `AuthCard`, `FormField`, `ServerErrorBanner`, `SocialDivider`, `SubmitButton`
- Dashboard:
  - `DailyTaskPanel`
  - `SkillScorePreview`
- Legacy task widgets:
  - `FillBlanksWidget`
  - `ListenAndRespondWidget`
  - `MCQWidget`
  - `OpenTextWidget`
  - `SpeakRecordWidget`
  - `StoryboardWidget`
  - `StructuredEssayWidget`
  - `TimedTextWidget`
- New sessions:
  - `ActivityFeedbackCard`
  - `SessionActivityNav`
  - `SessionScorecard`
  - `GenericResponseWidget`
- Streak:
  - `ActivityGridCard`
  - `StreakCelebration`
- Admin:
  - `AdminLayout`
  - `AdminPrimitives`
  - `BillingPrimitives`

State management approach:
- Auth:
  - `frontend/src/store/authStore.ts`
  - stores token in `localStorage`;
  - decodes JWT role/superuser flags client-side;
  - exposes `_hydrated` to prevent refresh redirects before localStorage is read.
- Server data:
  - React Query is used for `/auth/me`, tasks, progress, streaks, sessions, purchase, admin lists, etc.
- Diagnosis result:
  - `diagnosisStore` keeps the diagnosis result in memory only.
- New sessions:
  - `sessionStore` keeps `session`, last inline feedback, and scorecard in memory only.
  - React Query remains the source for backend session data.
- Legacy chat:
  - mostly local component state, WebSocket state, and `sessionStorage` for "resume today's chat".

API/WebSocket communication:
- `frontend/src/lib/api.ts` creates one axios instance.
- Base URL is `NEXT_PUBLIC_API_URL || "http://localhost:8000"`.
- Request interceptor reads `localStorage.token` and adds `Authorization: Bearer <token>`.
- Response interceptor catches 401, clears local token/store, and redirects to `/login`, except login/signup endpoints.
- WebSocket URL is derived from `NEXT_PUBLIC_API_URL` by replacing `http` with `ws`.
- Legacy chat authenticates the WebSocket by passing the JWT as a `token` query param.

Loading/skeleton behavior:
- Dashboard has a simple full-page "Loading your dashboard..." state.
- Legacy chat has specialized `TaskChatLoadingSkeleton` types:
  - `teacher_loading`
  - `activity_loading`
  - `evaluation_loading`
  - `feedback_loading`
  - `next_activity_loading`
- New sessions use simple text loading messages.
- Diagnosis has transcribing and submission spinners.
- Streak activity grid renders placeholder cells before data loads.

UI areas tightly coupled to backend data:
- `DailyTaskPanel` expects legacy `UserTask.task.content` to contain `sub_skill`, `activity`, `widget`, or old task content shapes.
- Legacy chat widgets expect exact `ui_event.widget` names and payload shapes.
- New sessions expect `task_archetypes.ui_widget` strings to match `components/sessions/widgets/registry.tsx`.
- Skill charts use `frontend/src/lib/skill-labels.ts` to normalize aliases like `thought_org`, `thought_organization`, `expression`, `listening`, `comprehension`, `tone_social`, and `tone`.
- Dashboard and stats expect `/auth/me` to include `enrollment`, and `/progress/stats` to include point/skill/recent-activity data.
- Diagnosis frontend hard-codes versioned IDs expected by backend:
  - `diag_fillblank_v1`
  - `diag_writing_v1`
  - `diag_passage_v1`

## 4. Backend Architecture

Backend stack:
- FastAPI.
- SQLAlchemy ORM.
- Alembic migrations.
- PostgreSQL-oriented JSONB, with SQLite compatibility in places.
- LangChain/OpenAI for LLM calls.
- Optional Azure Speech, OpenAI STT/TTS/image generation, Pinecone/HF embeddings.

Main API structure:
- `backend/app/main.py` mounts:
  - `/health`
  - `/auth`
  - `/admin`
  - `/diagnosis`
  - `/courses`
  - `/tasks`
  - `/responses`
  - `/progress`
  - `/debug/ai`
  - `/api/subscriptions`
  - `/api/users`
  - `/api/v1/challenges`
  - `/api/learning`
  - `/ws/learning/{session_id}`
  - `/api/sessions`
  - `/api/streak`

Common route -> service -> repository/database flow:
- Routes validate auth and HTTP payloads.
- Services own business logic and often commit at logical boundaries.
- Repositories wrap DB reads/writes for some modules.
- Models live beside modules.
- `backend/app/models.py` imports model classes so Alembic sees them.

Examples:
- Auth:
  - route: `backend/app/modules/auth/routes.py`
  - service: `backend/app/modules/auth/service.py`
  - repository: `backend/app/modules/auth/repository.py`
  - models: `backend/app/modules/auth/models.py`
- Legacy tasks:
  - route: `backend/app/modules/tasks/routes.py`
  - service: `backend/app/modules/tasks/service.py`
  - repository: `backend/app/modules/tasks/repository.py`
  - models: `backend/app/modules/tasks/models.py`
- New sessions:
  - route: `backend/app/modules/sessions/routes.py`
  - service: `backend/app/modules/sessions/service.py`
  - repositories: `backend/app/modules/sessions/repository.py`, `backend/app/modules/curriculum/v2_repository.py`, `backend/app/modules/progress/repository.py`
  - models: `backend/app/modules/sessions/models.py`

Authentication flow:
- Signup:
  - `POST /auth/signup`.
  - `AuthService.signup` checks duplicate email, hashes password, creates `User`, creates default `UserProfile`, assigns learner role, commits.
  - Signup returns user data but not an access token.
- Login:
  - `POST /auth/login`.
  - `AuthService.authenticate` verifies email/password and active status.
  - Route returns JWT with `sub`, `roles`, and `is_superuser`.
- Current user:
  - `GET /auth/me`.
  - Resolves JWT through `get_current_user`.
  - Returns user, profile fields, role flags, notification settings, structured personalization, and legacy enrollment.
- Profile update:
  - `PATCH /auth/me`.
  - Updates editable fields.
  - If personalization-relevant fields changed, calls `PersonalizationService.refresh_for_user`.
- Google OAuth:
  - `/auth/google/login` redirects to Google.
  - `/auth/google/callback` exchanges code, fetches profile, links or creates user, issues JWT, redirects frontend to diagnosis for new users or dashboard for existing users.
  - `/auth/google/relink-url` supports relinking Google for an authenticated user.
- Authorization:
  - `require_role`, `require_permission`, `require_super_admin` are in `backend/app/modules/auth/dependencies.py`.
  - Admin routes use permission dependencies.

User/profile flow:
- `User` stores account fields: email, password hash, name, active/superuser flags.
- `UserProfile` stores learning/profile fields:
  - self-assessed level, goal, exposure, interests, daily time;
  - display/contact/profile info;
  - free-text personalization and structured personalization;
  - diagnosis completed flag;
  - notification settings;
  - timezone and streak counters.
- `/auth/me` composes user, profile, and legacy enrollment into one frontend-friendly object.

Diagnosis flow:
- Routes: `backend/app/modules/diagnosis/routes.py`.
- Service: `backend/app/modules/diagnosis/service.py`.
- Start:
  - `POST /diagnosis/start`.
  - Marks profile `diagnosis_completed=False` to allow retake.
  - Does not appear to wipe previous score/progress rows.
- Transcribe:
  - `POST /diagnosis/transcribe`.
  - Accepts audio upload.
  - Uses OpenAI Whisper service.
  - Returns transcript, duration, and word timings.
- Submit:
  - `POST /diagnosis/submit`.
  - Guards against already-completed diagnosis.
  - Evaluates fill blanks with an answer key.
  - Evaluates writing with a word-count stub.
  - Evaluates read-aloud against Whisper transcript/timing.
  - Computes seven skill scores using `compute_skill_scores`.
  - Upserts `user_skill_scores`.
  - Seeds `skill_points` with `round(score * 1000)`.
  - Updates profile self-assessment fields and `diagnosis_completed=True`.
  - Best-effort refreshes structured personalization.
  - Calls `generate_diagnosis_feedback` to produce result text.

Task generation flow, legacy:
- Main route: `POST /tasks/next`.
- Service: `TaskService.get_or_create_day_bundle`.
- Inputs:
  - active `UserEnrollment`;
  - current week/day;
  - user skill scores;
  - profile personalization;
  - legacy course topics;
  - rotation engine;
  - task templates.
- Output:
  - list of `UserTaskRead` assigned for the current day.
- Process:
  - existing current-day bundle is reused if present;
  - otherwise rotation/planning chooses skill/activity;
  - LLM `TaskGeneratorAgent` tries to generate content from templates;
  - listen tasks may get TTS audio;
  - generated content is persisted as `Task`;
  - `TaskSkill` rows connect generated task to target skills;
  - `UserTask` assigns the task to the learner.
- Fallback:
  - if generation fails or no template exists, service falls back to active seeded task pool.

Task generation flow, new sessions:
- Main route: `POST /api/sessions/start`.
- Service: `SessionService.start_session`.
- Inputs:
  - `day_id`;
  - `course_length`;
  - `tasks_per_day`;
  - activity preferences.
- Process:
  - loads `CurriculumDay`;
  - refuses another in-progress session for same user/day;
  - `plan_session` deterministically selects activity archetypes;
  - creates `DailySession`;
  - marks `is_first_attempt` false if user already completed same day;
  - calls `LLMTaskGenerator` for each archetype;
  - stores generated task content in `ActivityAttempt.task_content`.
- The LLM generator returns generic fields:
  - `topic`
  - `instructions`
  - `primary_text`
  - `target_words`
  - plus metadata.

Feedback/evaluation flow, legacy response endpoint:
- Main route: `POST /responses/submit`.
- Service: `ResponseService.submit_and_grade`.
- Process:
  1. Persist `UserResponse`.
  2. Run `EvaluationService` against the task content.
  3. Save `Evaluation`.
  4. Run `FeedbackService` / feedback agent.
  5. Save `Feedback`.
  6. Apply WMA skill scores via `ScoreUpdaterService`.
  7. Best-effort apply points via `PointsUpdaterService`.
  8. Mark `UserTask` completed.
  9. Best-effort embed text response in Pinecone.
  10. Mark `UserTask` completed again. This duplicate completion block is suspicious.

Feedback/evaluation flow, legacy chat:
- Main route: WebSocket `/ws/learning/{session_id}`.
- `LearningSessionService` receives task submissions.
- `evaluation_node` scores the submission.
- `feedback_node` creates feedback.
- `_mark_bound_task_complete` writes legacy `UserResponse`, `Evaluation`, `Feedback`, updates scores/points, and marks the bound `UserTask` completed.

Feedback/evaluation flow, new sessions:
- Main route: `POST /api/sessions/{session_id}/activities/{sequence}/submit`.
- Service: `SessionService.submit_activity`.
- Process:
  1. Persist `ActivityAttempt.user_response` and mark submitted.
  2. Call `LLMEvaluator`.
  3. Compute base reward from raw score and course length.
  4. Distribute reward through archetype weight map.
  5. Save `ActivityEvaluation`.
  6. Call `LLMFeedbackGenerator`.
  7. Save `ActivityFeedback`.
  8. Mark attempt evaluated.

Progress/scoring flow:
- Legacy WMA:
  - `ScoreUpdaterService` updates `user_skill_scores`.
  - Writes append-only `progress_logs`.
- Legacy points:
  - `PointsUpdaterService` updates `skill_points`.
  - Writes `skill_points_logs`.
- New sessions scoring:
  - `backend/app/scoring/engine.py` calculates deterministic rewards and aggregations.
  - `SessionService.complete_session` creates `SessionScorecard`.
  - `apply_session_scorecard` writes `SkillPoints` and `SkillPointsLog`.
- Progress read APIs:
  - `/progress/scores` reads `SkillPoints`, not `UserSkillScore`.
  - `/progress/stats` reads `SkillPoints`, `SkillPointsLog`, legacy `Evaluation`, legacy `UserTask`, and `ProgressLog`.

Streak/activity tracking flow:
- Streak routes are in `backend/app/modules/streaks/routes.py`.
- `StreakService.record_in_same_tx` is called from `SessionService.complete_session`.
- Streak state is stored partly in:
  - `daily_activities`;
  - `streak_freeze_usages`;
  - `user_profiles.current_streak`;
  - `user_profiles.longest_streak`;
  - `user_profiles.last_activity_date`;
  - animation fields on `UserProfile`.
- Default timezone is `Asia/Kolkata`.
- Freeze code exists, but constants set `DEFAULT_FREEZES_ON_SIGNUP = 0` and `MAX_AUTO_FREEZE_DAYS = 0`.
- Legacy `/tasks/complete-day` does not appear to call `StreakService`.

Background jobs:
- No active Celery worker or background job system was found.
- Embedding after legacy response submission is best-effort inline.
- AI media caches write to local filesystem and are served through FastAPI static mounts.

## 5. AI / Agentic System Map

This project has several AI systems, not one.

LLM client foundation:
- `backend/app/ai/llm/openai_client.py`
- Uses `langchain_openai.ChatOpenAI`.
- Default model is `gpt-4o-mini`.
- Supports:
  - plain text generation;
  - streaming text;
  - structured output through LangChain `with_structured_output`.
- Retries and provider exception translation are centralized here.
- Structured-output calls log a marker, but token usage metadata may be unavailable.

AI request logging:
- `backend/app/ai/request_logging.py`.
- Records rows in `ai_request_logs`.
- It does not store prompts/raw user content.
- Not every AI call is clearly wrapped by this logger. Some AI calls only log to Python logs/LangSmith.

AI agents/chains/tools:

### New sessions agents

`LLMTaskGenerator`
- File: `backend/app/ai/sessions/llm_task_generator.py`.
- Used by: `SessionService.start_session`.
- Responsibility: generate generic task content for one planned archetype.
- Prompt location: `backend/app/ai/sessions/prompts.py`.
- Structured output: `TaskGenOutput`.
- Expected fields:
  - `topic`
  - `instructions`
  - `primary_text`
  - `target_words`
- Failure behavior: falls back to `StubTaskGenerator`.
- Fragility:
  - output is generic, while frontend new-session widgets are generic too;
  - bespoke archetype-specific content is not implemented yet.

`LLMEvaluator`
- File: `backend/app/ai/sessions/llm_evaluator.py`.
- Used by: `SessionService.submit_activity`.
- Responsibility: objectively score one new-session activity.
- Prompt location: `backend/app/ai/sessions/prompts.py`.
- Structured output: `EvaluationOutput`.
- Expected fields:
  - `raw_score` 0-10;
  - `rubric_scores`;
  - `evaluator_notes`.
- Deterministic vs flexible:
  - LLM scoring is flexible;
  - reward calculation after raw score is deterministic.
- Failure behavior: returns raw score 5.0 and notes evaluator unavailable.
- Fragility:
  - a provider failure can still award mid-range points.

`LLMFeedbackGenerator`
- File: `backend/app/ai/sessions/llm_feedback.py`.
- Used by: `SessionService.submit_activity`.
- Responsibility: produce structured learner-facing feedback.
- Prompt location: `backend/app/ai/sessions/prompts.py`.
- Structured output: `FeedbackOutput`.
- Expected fields:
  - `score`
  - `summary`
  - `did_well`
  - `mistakes`
  - `next_tip`
  - `sub_skill_breakdown`
- Failure behavior: minimal fallback feedback.
- Fragility:
  - code passes `task_content={}` into the prompt, so feedback does not see the full task that the evaluator saw.

### Legacy task/chat agents

`TaskGeneratorAgent`
- File: `backend/app/ai/agents/task_generator.py`.
- Used by:
  - legacy `TaskService`;
  - legacy `learning_session` task delivery;
  - potentially admin/dev task template flow.
- Responsibility: fill a `TaskTemplate` prompt and return validated Pydantic task content.
- Prompt organization:
  - system prompt in `task_generator.py`;
  - detailed task prompts live in `backend/app/tasks/schemas/*`.
- Structured output:
  - uses Pydantic models registered in `ALL_OUTPUT_MODELS`.
- Personalization:
  - receives user profile dict with topic, weak areas, interests, goals, personalization context, structured personalization, lesson context, and template modifiers.
- Fragility:
  - many content shapes and task_type strings;
  - frontend and evaluator infer behavior from JSON fingerprints;
  - template placeholder mismatches raise configuration errors.

`EvaluationService`
- File: `backend/app/ai/agents/evaluator.py`.
- Used by:
  - legacy `ResponseService`;
  - legacy chat `evaluation_node`.
- Responsibility: score user answers.
- Mostly deterministic/rule-based for:
  - fill in blanks;
  - error spotting;
  - sentence transformation;
  - voice conversion;
  - sentence engineering;
  - paraphrasing;
  - error correction;
  - speak with tense;
  - grammar listen MCQ.
- LLM-backed for:
  - open text writing;
  - grammar speaking.
- Structured output:
  - internal Pydantic schemas for LLM writing/speaking evaluation.
- Fragility:
  - activity type detection can depend on top-level JSON keys;
  - task content shape drift can break evaluation.

`generate_feedback`
- File: `backend/app/ai/agents/feedback.py`.
- Used by:
  - `FeedbackService`;
  - legacy chat `feedback_node`.
- Responsibility: turn task, answers, and evaluation report into structured feedback.
- Prompt location: inline `FEEDBACK_SYSTEM_PROMPT`.
- Structured output: `FeedbackOutput`.
- Personalization:
  - optional structured personalization and lesson context are included in prompt.
- Fragility:
  - assumes evaluation report shapes for many task types;
  - frontend expects `errors`, `overall_message`, `practice_suggestion`, etc.

`PlannerAgent`
- File: `backend/app/ai/agents/planner.py`.
- Used by:
  - legacy chat plan loader node.
- Responsibility: create one `DailyPlan` per user/course/week/day.
- Output:
  - `teacher_instructions`;
  - four `evaluation_focuses`;
  - deterministic activity blocks assembled from template registry.
- Data:
  - stored in legacy `daily_plans`.
- Personalization:
  - heavily uses `structured_personalisation`.
- Fragility:
  - new `/api/sessions` flow does not use this planner; it uses `modules/sessions/planner.py` instead.

`TeachingAgent`
- File: `backend/app/ai/agents/teacher.py`.
- Used by:
  - legacy chat `teach_node`;
  - streaming teaching in `LearningSessionService`.
- Responsibility: generate short teaching chat messages before practice.
- Prompt:
  - inline system prompt and user prompt builder.
- Personalization:
  - receives planner instructions and structured personalization.
- Fragility:
  - readiness/understanding logic is split between agent prompt and regex logic in `learning_session/service.py`.

`DiagnosisFeedbackAgent`
- File: `backend/app/ai/agents/diagnosis_feedback.py`.
- Used by: diagnosis submit.
- Responsibility: explain starting profile, weak skills, motivation, first-week focus.
- Structured output expected.
- Fragility:
  - called after DB commit; if it fails, user data may be written but HTTP response may fail unless fallback exists inside agent.

`PersonalizationAgent`
- File: `backend/app/ai/agents/personalization.py`.
- Used by:
  - diagnosis completion;
  - profile updates.
- Responsibility: convert raw learner profile into structured personalization.
- Structured output:
  - `StructuredPersonalisation`.
- Safety:
  - strips emails/phone-like text.
  - returns empty/fallback personalization if input is empty or LLM fails.

### Challenge/IELTS agents

`IELTSChallengeGenerator`
- File: `backend/app/ai/agents/ielts_challenge_generator.py`.
- Prompt file: `backend/app/ai/agents/prompts/ielts/generator.md`.
- Used by challenge attempt start.
- Generates reading/listening/writing/speaking payloads.
- Service retries generation and falls back to starter payload.

`IELTSChallengeWritingEvaluator`
- File: `backend/app/ai/agents/ielts_challenge_evaluator.py`.
- Prompt file: `backend/app/ai/agents/prompts/ielts/evaluator.md`.
- Used during challenge submit for writing.

`IELTSChallengeSpeakingEvaluator`
- File: `backend/app/ai/agents/ielts_challenge_speaking_evaluator.py`.
- Prompt file: `backend/app/ai/agents/prompts/ielts/speaking_evaluator.md`.
- Used during challenge submit after STT transcription.
- Pronunciation is marked unavailable in this phase.

`IELTSChallengeFeedbackAgent`
- File: `backend/app/ai/agents/ielts_challenge_feedback.py`.
- Prompt file: `backend/app/ai/agents/prompts/ielts/feedback.md`.
- Used after challenge evaluation.

### AI media/service tools

STT:
- Files: `backend/app/ai/stt/*`.
- Backend routes:
  - `/diagnosis/transcribe`
  - `/responses/transcribe-audio`
  - `/debug/ai/stt/transcribe`
  - challenge speaking upload flow.
- Uses OpenAI Whisper.
- Supports timestamps where requested.

TTS:
- Files: `backend/app/ai/tts/*`.
- Used for generated listening tasks/challenges.
- Cached locally and served under `/audio`.

Pronunciation:
- Files: `backend/app/ai/pronunciation/*`.
- Uses Azure Speech.
- Exposed through `/debug/ai/pronunciation/score`.

Image generation:
- Files: `backend/app/ai/imagegen/*`.
- Exposed through `/debug/ai/image/generate`.
- Cached locally and served under `/images`.

Embeddings:
- Files: `backend/app/ai/embeddings/*`.
- Used best-effort after legacy response submission.
- Stores vector metadata in Pinecone and updates `UserResponse.embedding_status`.

How prompts are organized:
- New sessions prompts: centralized in `backend/app/ai/sessions/prompts.py`.
- Legacy feedback/task/teacher/planner prompts: mostly inline in agent files plus templates in `backend/app/tasks/schemas/*`.
- IELTS prompts: markdown files under `backend/app/ai/agents/prompts/ielts/`.
- Task templates: Pydantic/template definitions under `backend/app/tasks/schemas/*`.

How LLM responses are parsed/validated:
- Most modern code uses `OpenAILLMClient.generate_structured` and Pydantic models.
- Legacy code sometimes uses the raw LangChain chat model with structured output.
- Challenge agents use Pydantic schemas and fallback behavior.
- For deterministic task evaluation, no LLM parsing is involved.

Where structured output is expected:
- Diagnosis feedback.
- Personalization extraction.
- New session task generation, evaluation, feedback.
- Legacy task generation.
- Legacy open writing/speaking evaluation.
- Legacy feedback.
- Planner output.
- Teacher output for non-streaming mode.
- IELTS generation/evaluation/feedback.

How personalization context is passed:
- `UserProfile.personalisation_context`, interests, goals, country, native language, and self-assessed level are raw inputs.
- `PersonalizationAgent` writes `UserProfile.structured_personalisation`.
- Legacy `TaskService._build_user_profile` includes raw and structured personalization in the task-generation profile.
- Legacy `PlannerAgent` uses structured personalization to choose scenario, vocabulary domain, and conversation style.
- Legacy `TeacherAgent` receives planner instructions and structured personalization.
- Legacy `FeedbackAgent` can receive structured personalization and lesson context.
- New sessions task generator receives only `user_interests` from `SessionService.start_session`. It does not appear to receive full structured personalization in the route call.

How user history/progress affects AI behavior:
- Diagnosis seeds skill scores and points.
- Legacy `TaskService` reads `UserSkillScore` and weakest skills to build user profile and sub-level.
- Legacy rotation tracks recent activity per skill via `EnrollmentSkillHistory`.
- Legacy planner caches daily plans per user/course/week/day.
- New sessions scoring reads current `SkillPoints` totals at completion to compute dashboard-after scores.
- New sessions planning is deterministic from curriculum day and preferences, not from weak skills/history.

Deterministic vs flexible:
- Deterministic:
  - diagnosis fill blank answer key;
  - diagnosis score formula;
  - read-aloud WPM/pause/similarity math;
  - new session planner;
  - new session points calculation;
  - legacy rotation engine;
  - most legacy discrete evaluators;
  - streak state machine.
- Flexible/LLM:
  - task content generation;
  - open writing/speaking evaluation;
  - feedback text;
  - teaching turns;
  - daily planner;
  - personalization extraction;
  - IELTS generation/writing/speaking/feedback.

Fragile/hard-to-understand AI areas:
- Two planners exist:
  - legacy LLM `PlannerAgent` writing `daily_plans`;
  - new deterministic `plan_session` using `curriculum_days`.
- Two task generation systems exist:
  - legacy template-based generator;
  - new generic archetype generator.
- Two feedback schemas exist:
  - legacy `Feedback.body`;
  - new `ActivityFeedback`.
- Several systems silently fall back on failure, sometimes producing generic/stub content or score 5.0.
- Prompt text is spread across Python files, markdown files, and template modules.
- Structured output usage is strong, but downstream frontend still depends on exact ad hoc JSON shapes.

## 6. Data Model and Database Flow

Main table groups:

Auth/profile:
- `users`
  - Account identity: email, password hash, name, active/superuser flags.
- `user_profiles`
  - Learning profile, diagnosis fields, personalization fields, notification fields, timezone, streak counters.
- `oauth_accounts`
  - OAuth provider links.
- `roles`, `user_roles`, `permissions`, `role_permissions`
  - Role/permission system for admin access.

Skills/progress:
- `skills`
  - Seven master sub-skills.
  - Internal names: `grammar`, `vocabulary`, `pronunciation`, `fluency`, `expression`, `comprehension`, `tone`.
  - `display_label` gives friendly labels.
- `user_skill_scores`
  - WMA/current skill score.
  - One row per user/skill.
  - Used by legacy generation and legacy score history.
- `progress_logs`
  - Append-only WMA score history.
  - Linked to `user_task_id`.
- `skill_points`
  - Points-based gamified score.
  - 1000 points = 1.0 dashboard score.
  - Used by `/progress/scores` and `/progress/stats` current scores.
- `skill_points_logs`
  - Append-only points gains.
  - Can link either to legacy `user_task_id` or new `session_id`.

Legacy curriculum/task/session:
- `courses`
  - Course catalog rows for 24-week/48-week beginner plans.
- `user_enrollments`
  - One active path per user through a course.
  - Stores current week/day, task count, allowed activities, started/current-day timestamps.
- `enrollment_skill_history`
  - Legacy rotation memory by enrollment and skill.
- `daily_plans`
  - Legacy LLM planner cache by user/course/week/day.
- `tasks`
  - Task template or generated task content.
  - Content shape varies by `task_type`.
- `task_skills`
  - Task-to-skill weights.
- `user_tasks`
  - Task assignment for a user/enrollment, status, completed time.
- `user_responses`
  - Submitted answer content for one `UserTask`.
  - Also stores embedding status/vector id.
- `evaluations`
  - Legacy structured evaluation result, percentage, overall score.
- `feedbacks`
  - Legacy structured feedback body and admin review status.
- `learning_sessions`
  - Legacy chat session state: UUID, phase, topic, messages, generated tasks, queue, submission/evaluation/feedback.

New curriculum/sessions:
- `curriculum_weeks`
  - V2 weekly curriculum entries by course length and week number.
- `curriculum_days`
  - Day topic, explanation brief, default/mandatory activities, suggested archetypes.
- `task_archetypes`
  - Static archetypes mirrored from `app.scoring.ARCHETYPE_REGISTRY`.
  - Includes core activity, UI widget, supported themes, CEFR range, weight map, rubric.
- `daily_sessions`
  - New daily session instance for one user/day.
  - External UUID `session_id`; internal integer ID.
  - `is_first_attempt` controls whether points are awarded.
- `activity_attempts`
  - One planned activity/archetype inside a daily session.
  - Stores generated `task_content`, user response, status.
- `activity_evaluations`
  - New activity score, rubric scores, base reward, weighted points.
- `activity_feedback`
  - New activity feedback shape: summary, did_well, mistakes, next_tip, sub_skill_breakdown.
- `session_scorecards`
  - One scorecard per completed new session.
  - Stores points earned, totals after, dashboard after, and whether points were applied.

Streaks:
- `daily_activities`
  - One row per user/local date with activity count and last session link.
- `streak_freeze_usages`
  - Protected missed dates. Code exists but freeze constants are currently zero.
- Streak counters also live on `user_profiles`.

Challenges:
- `challenges`
  - Challenge catalog, e.g. IELTS Sprint.
- `challenge_levels`
  - Sequential levels with time limit, pass threshold, and config.
- `challenge_attempts`
  - User attempt lifecycle, task payload, response payload, scores, pass flag, evaluation report, feedback report.

Billing/admin:
- `purchases`
  - One current mock purchase per user.
- `subscriptions`
  - Provider-backed subscription metadata.
- `payments`
  - Provider/mock payment metadata.
- `admin_audit_logs`
  - Admin action audit trail.
- `ai_request_logs`
  - AI request operational logs.

Relationships between important models:
- `User` has one `UserProfile`.
- `User` has many `OAuthAccount`, `UserRole`, enrollments/activities through FKs.
- `UserEnrollment` belongs to `Course`.
- `UserTask` belongs to `User`, `Task`, and optionally `UserEnrollment`.
- `Task` has many `TaskSkill`.
- `UserResponse` belongs to `UserTask` and has one `Evaluation`.
- `Evaluation` has one `Feedback`.
- `LearningSession` links to `User`, `UserEnrollment`, and optionally `UserTask`.
- `DailySession` belongs to `User` and `CurriculumDay`.
- `DailySession` has many `ActivityAttempt` and one `SessionScorecard`.
- `ActivityAttempt` has one `ActivityEvaluation` and one `ActivityFeedback`.
- `SkillPointsLog` can refer to either legacy `user_task_id` or new `daily_sessions.id`.
- `DailyActivity.last_session_id` links to new `daily_sessions.id`.

How user progress is updated:
- Diagnosis:
  - Upserts `user_skill_scores`.
  - Upserts `skill_points` using `score * 1000`.
- Legacy response:
  - `ScoreUpdaterService` updates `user_skill_scores` with WMA.
  - Writes `progress_logs`.
  - `PointsUpdaterService` updates `skill_points`.
  - Writes `skill_points_logs`.
- Legacy chat:
  - Stores session evaluation in `learning_sessions.evaluation`.
  - At completion, bridges into legacy `user_responses`, `evaluations`, `feedbacks`, WMA, points.
- New sessions:
  - Per-attempt evaluation stores raw score and weighted points.
  - Completion aggregates points, writes `session_scorecards`, writes `skill_points` and `skill_points_logs` only for first attempts.
  - Does not update `user_skill_scores` or `progress_logs`.

How task/session/response/feedback data is stored:
- Legacy:
  - Task content: `tasks.content`.
  - Assigned status: `user_tasks`.
  - Chat state: `learning_sessions`.
  - Submission: `user_responses`.
  - Evaluation: `evaluations`.
  - Feedback: `feedbacks`.
- New:
  - Session: `daily_sessions`.
  - Activity task content and response: `activity_attempts`.
  - Evaluation: `activity_evaluations`.
  - Feedback: `activity_feedback`.
  - Final scorecard: `session_scorecards`.
- Challenges:
  - Task and response payloads plus evaluation/feedback reports are all stored on `challenge_attempts`.

Migrations:
- Alembic versions live in `backend/alembic/versions`.
- Important phases:
  - squashed initial schema;
  - admin roles;
  - admin monitoring;
  - personalisation and plan wipe;
  - challenges foundation;
  - streak tables;
  - curriculum v2 tables;
  - sessions tables;
  - skill display labels;
  - admin permissions/billing.

Suspicious, duplicate, unused, or confusing database models:
- `user_skill_scores` and `skill_points` both store "current skill score" concepts.
- `progress_logs` and `skill_points_logs` both store progress history, but for different scoring systems.
- `learning_sessions` and `daily_sessions` both represent a learning session.
- `feedbacks` and `activity_feedback` both store feedback.
- `evaluations` and `activity_evaluations` both store evaluation.
- `daily_plans` and `curriculum_days`/`task_archetypes` both represent planning.
- `Task`/`TaskSkill` templates and `TaskArchetype` definitions both represent task types/content generation inputs.
- `DailyActivity` streak writes refer to new sessions, while the main UI still completes legacy tasks.

## 7. Core Business Logic

Diagnosis scoring:
- File: `backend/app/modules/diagnosis/scoring.py`.
- Inputs:
  - self-assessed level;
  - content exposure;
  - fill blank correct count;
  - writing expression/vocabulary/tone stub scores;
  - speech fluency/clarity.
- Constants:
  - beginner base: 1.0
  - intermediate base: 1.5
  - advanced base: 2.0
  - exposure bonus: none 0.0, low 0.25, medium 0.50, high 0.75
  - fill blank grammar: +0.25 each
  - fill blank vocabulary: +0.10 each
  - hard cap: 4.0
- Outputs:
  - seven scores in 1.0-4.0-ish range, capped at 4.0.
- Diagnosis result UI displays these as 0-10 by multiplying by 2.5.
- Diagnosis seeds points as score * 1000, so a capped diagnosis skill becomes 4.0 display, not 10.0.

Curriculum/day/week logic, legacy:
- Legacy enrollment state lives on `UserEnrollment.current_week` and `current_day_in_week`.
- `TaskService.mark_day_complete` checks all current day tasks are completed, then advances:
  - day 1 through 7;
  - after day 7, increments week and resets day to 1.
- Current day started timestamp is used to locate tasks for the day.
- Legacy `RotationEngine` chooses skill/activity from day/week and history.
- `EnrollmentSkillHistory` remembers last activity per skill.
- Course topics come from `backend/app/data/courses/topics_24w.json`, `topics_48w.json`, and `curriculum/topics.py`.

Curriculum/day/week logic, new:
- New curriculum is seeded into `curriculum_weeks` and `curriculum_days`.
- `SessionService.start_session` requires a `day_id` directly.
- `plan_session` chooses activities from `CurriculumDay.mandatory_activities` and `suggested_archetypes`.
- The service does not appear to derive `day_id` from `UserEnrollment` by itself.
- This makes the source of truth for "today's current day" unclear between legacy enrollment and v2 `day_id`.

Task selection/generation, legacy:
- `TaskService.get_or_create_day_bundle` is idempotent for the current legacy day.
- It uses:
  - active enrollment settings;
  - rotation;
  - user scores/profile;
  - task template registries;
  - TTS for listening tasks;
  - fallback seeded task pool.
- It persists each generated task and assignment.

Task selection/generation, new:
- `plan_session` is deterministic.
- Activity order is fixed: read, write, listen, speak.
- Mandatory activities are included first if allowed.
- Optional activities fill remaining slots up to `tasks_per_day`.
- First suggested archetype per activity is chosen.
- LLM fills the task content but cannot change the skeleton.

Session completion:
- Legacy:
  - each `UserTask` completion unlocks the next task in dashboard bundle.
  - `/tasks/complete-day` advances enrollment only after all current day tasks are completed.
- New:
  - all `ActivityAttempt`s must be evaluated.
  - `/api/sessions/{id}/complete` aggregates and writes scorecard/points/streak.

Evaluation and feedback:
- Legacy:
  - discrete tasks use rule-based evaluators;
  - some open writing/speaking use LLM evaluators;
  - feedback is LLM-generated from task, answer, evaluation report.
- New:
  - every activity uses LLM evaluator unless no response;
  - feedback uses LLM feedback generator;
  - scoring math after raw score is deterministic.

Weighted scoring:
- Legacy WMA:
  - `ALPHA = 0.2`.
  - Effective alpha is `ALPHA * task_skill.weight`.
  - New score = weighted blend of old score and task score.
  - Writes `user_skill_scores` and `progress_logs`.
- Legacy points:
  - performance tiers map to point rewards for 24-week and 48-week courses.
  - advanced slowdown halves points if current display score is 8.0+.
- New scoring:
  - raw score maps to tier:
    - 8.0+ excellent
    - 6.0+ good
    - 4.0+ average
    - 2.0+ poor
    - below 2.0 very poor
  - 24-week rewards: 55, 40, 24, 10, 0.
  - 48-week rewards: 28, 20, 12, 5, 0.
  - reward is split by archetype `weight_map`.
  - points are rounded once per sub-skill at session end.
  - totals cap at 10000.
  - dashboard display is `points / 1000`, rounded half-up to one decimal.

Streak calculation:
- File: `backend/app/modules/streaks/service.py`.
- One completion per local date increments or starts streak.
- Same local date increments `activity_count` but does not increment streak again.
- Gap of one day continues streak.
- Gap greater than one day resets streak because auto-freeze constants are zero.
- Animation type is stored on `UserProfile.last_animation_type`.
- Frontend marks animation seen through `/api/streak/animation-seen`.

Activity history:
- Legacy stats activity history comes from completed `UserTask`s and their legacy response/evaluation/feedback.
- New session activity attempts do not appear in `/progress/activities`.
- Streak activity grid comes from `daily_activities`, which new sessions write.

Dashboard score display:
- Dashboard receives `skill_scores` from `/auth/me` only if that schema includes it; otherwise `DashboardPage` falls back to zeros.
- Stats and `/progress/scores` clearly use `SkillPoints.display_score`.
- Skill label normalization is duplicated between backend display labels and frontend `skill-labels.ts`.

Rules spread across many files:
- Skill naming/alias rules:
  - `backend/app/scoring/constants.py`
  - `frontend/src/lib/skill-labels.ts`
  - `backend/app/modules/tasks/service.py`
  - `backend/app/ai/agents/planner.py`
- Task/widget naming:
  - legacy frontend widgets;
  - legacy task content schemas;
  - new `TaskArchetype.ui_widget`;
  - new sessions widget registry.
- Course length reward logic:
  - `backend/app/scoring/constants.py`
  - legacy `PointsUpdaterService` in `backend/app/modules/progress/service.py`
- Completion semantics:
  - legacy `UserTask.status`;
  - legacy `LearningSession.phase`;
  - new `ActivityAttempt.status`;
  - new `DailySession.status`;
  - streak `DailyActivity`.

## 8. End-to-End User Flows

### 8.1 New User Flow

Signup/login -> diagnosis -> profile creation -> first dashboard -> first task:

1. User registers through `/register`.
2. Frontend calls `POST /auth/signup`.
3. Backend creates:
   - `users`;
   - default `user_profiles`;
   - learner role.
4. User logs in through `/login`.
5. Frontend stores JWT in `authStore` and `localStorage`.
6. Dashboard calls `GET /auth/me`.
7. If `diagnosis_completed` is false, dashboard redirects to `/diagnosis`.
8. User completes diagnosis form.
9. Read-aloud step sends audio to `/diagnosis/transcribe`.
10. Submit sends full payload to `/diagnosis/submit`.
11. Backend:
    - scores fill blank/writing/speech;
    - computes seven skill scores;
    - writes `user_skill_scores`;
    - seeds `skill_points`;
    - updates profile;
    - refreshes structured personalization best-effort;
    - returns AI diagnosis feedback.
12. Frontend stores result in `diagnosisStore` and routes to `/diagnosis/result`.
13. User clicks continue to dashboard.
14. If no enrollment exists, dashboard shows no-enrollment state and points to `/pricing`.
15. User purchases a plan on `/pricing`.
16. Frontend calls `POST /api/subscriptions/purchase`.
17. Backend records purchase/payment and creates or updates `UserEnrollment`.
18. Dashboard now renders enrolled view.
19. `DailyTaskPanel` calls `POST /tasks/next`.
20. Backend creates or returns the legacy current-day task bundle.
21. User clicks the active task and enters `/task/chat`.

### 8.2 Daily Learning Flow

Dashboard -> daily task/session -> chat/activity -> evaluation -> score update -> streak update -> result/dashboard:

Current main dashboard/legacy path:

1. Dashboard loads `/auth/me` and renders `DailyTaskPanel`.
2. `DailyTaskPanel` calls `/tasks/next`.
3. Backend returns the current legacy day bundle.
4. User clicks active task.
5. Frontend routes to `/task/chat?id=<user_task_id>`.
6. `/task/chat` calls `POST /api/learning/sessions/start`.
7. Backend `LearningSessionService.create_session` creates or resumes a `learning_sessions` row and links it to a `UserTask`.
8. Frontend opens WebSocket `/ws/learning/{session_id}?token=<JWT>`.
9. Backend streams teaching messages.
10. Backend sends a task widget as a `ui_event`.
11. Frontend renders the legacy widget.
12. User submits answers through WebSocket.
13. Backend evaluates and sends scorecard/feedback events.
14. Backend marks the bound `UserTask` complete and writes legacy response/evaluation/feedback plus WMA/points.
15. User chooses "Next activity" or "Go to dashboard".
16. Dashboard invalidates tasks/me and refreshes.
17. When all tasks are complete, `DailyTaskPanel` shows advance action.
18. User clicks advance, which calls `/tasks/complete-day`.
19. Backend advances legacy enrollment week/day.
20. Streak update is unclear for this path; no call to `StreakService` was found in legacy completion.

New sessions path if manually used:

1. User navigates to `/sessions/start`.
2. User supplies a v2 `day_id`, course length, and task count.
3. Frontend calls `/api/sessions/start`.
4. Backend creates `daily_sessions` and `activity_attempts`.
5. `/sessions/[sessionId]` calls next-activity.
6. User submits generic widget response.
7. Backend evaluates, writes `activity_evaluations`, generates feedback, writes `activity_feedback`.
8. Frontend shows inline feedback.
9. After no pending activities remain, frontend calls `/complete`.
10. Backend writes scorecard, applies points if first attempt, and records streak.
11. Frontend routes to `/sessions/[sessionId]/scorecard`.

### 8.3 AI Feedback Flow

User response -> backend receives it -> AI/evaluator runs -> feedback generated -> scores saved -> frontend displays result:

Legacy response endpoint:

1. Frontend submits a response through `tasksApi.submitResponse` or legacy chat bridge.
2. Backend persists `UserResponse`.
3. `EvaluationService` scores the response:
   - rule-based for discrete tasks;
   - LLM for open writing/speaking cases.
4. Backend persists `Evaluation`.
5. `FeedbackService` calls `generate_feedback`.
6. Feedback agent receives:
   - original task content;
   - user answers;
   - evaluation report;
   - score;
   - optional structured personalization and lesson context.
7. Feedback agent returns structured `FeedbackOutput`.
8. Backend saves `Feedback.body`.
9. Backend updates WMA scores and points.
10. Frontend renders scorecard/feedback from response or WebSocket `ui_event`.

New sessions:

1. Frontend posts `user_response` to `/api/sessions/{id}/activities/{sequence}/submit`.
2. Backend persists response on `ActivityAttempt`.
3. `LLMEvaluator` receives:
   - archetype metadata;
   - task content;
   - user response.
4. Backend saves `ActivityEvaluation`.
5. `LLMFeedbackGenerator` receives:
   - archetype metadata;
   - raw score;
   - rubric scores;
   - evaluator notes;
   - user response;
   - empty task content.
6. Backend saves `ActivityFeedback`.
7. Frontend renders `ActivityFeedbackCard`.
8. Points are not applied until `/complete`.

### 8.4 Streak Flow

Activity completion -> date check -> streak update -> animation/dashboard state:

New sessions path:

1. User completes all activities in a new daily session.
2. Frontend calls `POST /api/sessions/{session_id}/complete`.
3. `SessionService.complete_session` creates scorecard and applies points.
4. In the same transaction, it calls `StreakService.record_in_same_tx`.
5. Streak service resolves user's local date from `UserProfile.timezone`.
6. If `daily_activities` already has a row for today:
   - increments `activity_count`;
   - does not increment streak.
7. If no row exists:
   - inserts `DailyActivity`;
   - compares `today` to `profile.last_activity_date`;
   - starts, continues, resets, or theoretically freezes streak.
8. `UserProfile` streak fields and animation type are updated.
9. Dashboard `ActivityGridCard` calls `GET /api/streak/me`.
10. Frontend receives:
    - current streak;
    - longest streak;
    - today complete;
    - 91-day activity grid;
    - animation state.
11. Frontend can call `PATCH /api/streak/animation-seen` to suppress repeat animation.

Legacy daily task path:
- The current legacy dashboard/chat flow completes `UserTask`s and advances enrollment, but no clear streak write was found.
- Therefore streak display may lag or remain empty for users only using the dashboard's current legacy path.

## 9. Redundancy and Complexity Audit

Duplicate or parallel systems:

- Legacy task/chat system and new sessions system both implement "daily learning".
  - Legacy: `/tasks`, `/responses`, `/api/learning`, `/ws/learning`.
  - New: `/api/sessions`.
  - The dashboard still uses legacy.

- Legacy `LearningSession` and new `DailySession`.
  - `learning_sessions` stores chat phase/messages/tasks.
  - `daily_sessions` stores new REST activity attempts.

- Legacy `Task`/`TaskSkill` and new `TaskArchetype`.
  - Legacy generated tasks become rows in `tasks`.
  - New sessions use archetype registry and activity attempts.

- Legacy `Evaluation`/`Feedback` and new `ActivityEvaluation`/`ActivityFeedback`.
  - Shapes differ.
  - Frontend components differ.

- Legacy `DailyPlan` and new `CurriculumDay`/`TaskArchetype` planner.
  - Legacy planner is LLM-generated and cached.
  - New planner is deterministic from v2 curriculum.

- WMA score system and points score system.
  - `user_skill_scores` plus `progress_logs`.
  - `skill_points` plus `skill_points_logs`.
  - Progress endpoints read a mixture.

- Legacy and new points reward constants.
  - `backend/app/scoring/constants.py`.
  - `PointsUpdaterService` in `backend/app/modules/progress/service.py`.
  - They currently match but are duplicated.

Old logic that seems replaced by newer logic:
- `backend/app/modules/tasks/service.py` is explicitly marked deprecated.
- `backend/app/modules/responses/service.py` is explicitly marked deprecated.
- `backend/app/modules/learning_session/service.py` is explicitly marked deprecated.
- `backend/app/modules/curriculum/rotation.py` is described as legacy/rotation logic.
- The new sessions module appears intended to replace them, but it is not the main dashboard path yet.

Dead or unused-looking modules:
- `/courses` frontend page redirects to `/pricing`, but backend `/courses` still supports list/enroll/settings.
- `backend/app/ai/graphs/learning_session_graph.py` exists, but chat orchestration appears to call nodes manually.
- README mentions Celery/Redis background jobs; code does not show an active Celery worker.
- `MD_FILES/` exists but is empty and not used by runtime code.

Over-engineered or split areas:
- AI prompt organization is spread across:
  - new session prompt builders;
  - legacy agent inline prompts;
  - task schema prompt templates;
  - IELTS markdown prompt files.
- Skill naming normalization is spread across backend scoring constants, planner aliases, task service labels, and frontend label mapping.
- Legacy chat has a lot of regex readiness logic plus LLM teaching behavior, making conversational state hard to reason about.
- `Progress` tries to support WMA scores, points scores, weekly stats, difficulty, feedback insights, and recent activities in one route file.

Frontend/backend duplicated logic:
- Skill labels and aliases:
  - backend has `skills.display_label` and scoring aliases;
  - frontend has `frontend/src/lib/skill-labels.ts`.
- Widget names:
  - backend task content/archetypes ship widget strings;
  - frontend registries must mirror them.
- Course plan concepts:
  - frontend pricing plan IDs map to backend `PLAN_CATALOG`.
- Diagnosis prompt IDs:
  - frontend hard-codes IDs that backend expects.

Confusing naming:
- `expression` means "Thought Organization".
- `comprehension` means "Listening".
- `tone` means "Tone & Social".
- New docs/code aliases mention `thought_org`, `listening`, and `tone_social`.
- "Session" can mean legacy `learning_sessions`, new `daily_sessions`, or a chat UI page.
- "Activity" can mean new `activity_attempts`, legacy task activity types, or streak daily activity.

Files that should probably be merged, deleted, or clarified later:
- Do not delete now, but these deserve explicit ownership decisions:
  - `backend/app/modules/tasks/service.py`
  - `backend/app/modules/responses/service.py`
  - `backend/app/modules/learning_session/service.py`
  - `backend/app/modules/curriculum/rotation.py`
  - `backend/app/ai/graphs/learning_session_graph.py`
  - `frontend/src/app/sessions/*` vs `frontend/src/app/task/chat/*`
  - `frontend/src/components/sessions/widgets/*` vs `frontend/src/components/task/task-widgets/*`
  - `backend/app/scoring/constants.py` vs legacy points constants in `progress/service.py`

Suspicious specific findings:
- `ResponseService.submit_and_grade` marks a `UserTask` completed twice.
- New session feedback prompt discards task content.
- `/progress/stats` uses legacy evaluation/task rows for weekly score changes, task counts, difficulty, and recent activity, but current scores from `SkillPoints`.
- New sessions write streaks; legacy dashboard path appears not to.
- New sessions `/start` relies on caller-provided `day_id`; it does not derive it from `UserEnrollment`.
- The file `RESTRUCTURE_DECISIONS.md` is referenced by scoring comments but is deleted in the current worktree status.

## 10. Risk Areas / Fragile Areas

Risk: changing daily learning flow.
- Why risky: there are two active systems.
- Files involved:
  - `frontend/src/components/dashboard/DailyTaskPanel.tsx`
  - `frontend/src/app/task/chat/*`
  - `frontend/src/app/sessions/*`
  - `backend/app/modules/tasks/*`
  - `backend/app/modules/learning_session/*`
  - `backend/app/modules/sessions/*`
- Check before changing:
  - which frontend path the user actually enters;
  - whether `NEXT_PUBLIC_USE_NEW_SESSION_FLOW` is enabled;
  - whether backend `use_new_session_flow` is on;
  - whether progress/streak/day advancement still updates.

Risk: changing scoring.
- Why risky: WMA, legacy points, and new scoring coexist.
- Files involved:
  - `backend/app/modules/progress/service.py`
  - `backend/app/scoring/*`
  - `backend/app/modules/sessions/scoring_writer.py`
  - `backend/app/modules/diagnosis/scoring.py`
  - `frontend/src/components/dashboard/SkillScorePreview.tsx`
  - `frontend/src/app/stats/page.tsx`
- Check before changing:
  - whether the change should affect WMA, points, or both;
  - whether diagnosis seeding should change;
  - whether stats/dashboard read the same source being updated.

Risk: changing skill names.
- Why risky: internal names and display names differ, and aliases are spread across code.
- Files involved:
  - `backend/app/scoring/constants.py`
  - `backend/app/modules/skills/models.py`
  - `frontend/src/lib/skill-labels.ts`
  - `backend/app/ai/agents/planner.py`
  - `backend/app/modules/tasks/service.py`
- Check before changing:
  - seeded `skills` table;
  - archetype weight maps;
  - frontend normalization;
  - progress APIs;
  - task templates and planner aliases.

Risk: changing task content schemas.
- Why risky: frontend widgets, evaluator dispatch, feedback prompts, and admin task templates all assume particular JSON shapes.
- Files involved:
  - `backend/app/tasks/schemas/*`
  - `backend/app/ai/agents/task_generator.py`
  - `backend/app/ai/agents/evaluator.py`
  - `backend/app/modules/responses/service.py`
  - `frontend/src/lib/tasks-api.ts`
  - `frontend/src/components/task/task-widgets/*`
- Check before changing:
  - evaluator activity detection;
  - frontend widget props;
  - feedback agent expectations;
  - persisted old task rows.

Risk: changing WebSocket chat behavior.
- Why risky: legacy chat stores state in DB, streams messages, uses regex readiness logic, and persists legacy scores only at certain transitions.
- Files involved:
  - `backend/app/modules/learning_session/router.py`
  - `backend/app/modules/learning_session/service.py`
  - `backend/app/ai/graphs/nodes.py`
  - `frontend/src/app/task/chat/[sessionId]/page.tsx`
- Check before changing:
  - reconnect behavior;
  - outgoing event schema;
  - task_queue/current_task_index;
  - `_mark_bound_task_complete`;
  - dashboard query invalidation.

Risk: changing progress dashboard.
- Why risky: stats combine current points, WMA history, legacy evaluations, feedback bodies, and completed tasks.
- Files involved:
  - `backend/app/modules/progress/routes.py`
  - `frontend/src/app/stats/page.tsx`
  - `frontend/src/lib/progress-api.ts`
- Check before changing:
  - whether data comes from legacy or new sessions;
  - whether empty/fallback values are intentionally shown;
  - whether new session attempts need to appear in recent activities.

Risk: changing streaks.
- Why risky: write path is currently tied to new sessions completion, but main dashboard uses legacy tasks.
- Files involved:
  - `backend/app/modules/streaks/service.py`
  - `backend/app/modules/sessions/service.py`
  - `backend/app/modules/tasks/service.py`
  - `frontend/src/components/streak/*`
- Check before changing:
  - timezone behavior;
  - idempotency by local date;
  - whether legacy completion should call streak service;
  - animation seen behavior.

Risk: changing diagnosis.
- Why risky: diagnosis seeds both old and new scoring sources and gates dashboard access.
- Files involved:
  - `backend/app/modules/diagnosis/*`
  - `backend/app/ai/agents/diagnosis_feedback.py`
  - `backend/app/modules/personalization/service.py`
  - `frontend/src/app/diagnosis/*`
  - `frontend/src/lib/diagnosis-api.ts`
- Check before changing:
  - hard-coded frontend diagnosis IDs;
  - score scale 1-4 vs 0-10 display;
  - `diagnosis_completed` redirects;
  - retake behavior.

Risk: changing personalization.
- Why risky: profile updates can trigger LLM extraction; old and new learning paths use different subsets of personalization.
- Files involved:
  - `backend/app/modules/auth/routes.py`
  - `backend/app/modules/personalization/service.py`
  - `backend/app/ai/agents/personalization.py`
  - `backend/app/modules/tasks/service.py`
  - `backend/app/ai/agents/planner.py`
  - `backend/app/ai/agents/teacher.py`
- Check before changing:
  - which profile fields trigger refresh;
  - PII stripping;
  - fallback structures;
  - whether new sessions should receive structured personalization.

Risk: changing AI provider/client behavior.
- Why risky: all structured agents depend on `generate_structured`, and fallbacks can hide failures.
- Files involved:
  - `backend/app/ai/llm/openai_client.py`
  - `backend/app/ai/sessions/*`
  - `backend/app/ai/agents/*`
  - `backend/app/ai/request_logging.py`
- Check before changing:
  - structured output validation;
  - timeout/retry behavior;
  - usage logging;
  - fallback paths that may persist stub scores/content.

Risk: changing challenges.
- Why risky: challenge service spans generation, TTS, STT, deterministic scoring, AI scoring, feedback, protected audio, attempt limits, and pass/unlock logic.
- Files involved:
  - `backend/app/modules/challenges/*`
  - `backend/app/ai/agents/ielts_challenge_*`
  - `frontend/src/app/challenges/*`
  - `frontend/src/lib/challenges-api.ts`
- Check before changing:
  - attempt lifecycle and expiry;
  - daily limit;
  - level unlock;
  - generated payload schemas;
  - audio storage/protected URLs.

## 11. Missing Clarifications / Incomplete Decisions

- Is legacy enrollment still the source of truth for today's learning day, or should v2 `curriculum_days.day_id` take over?
- Should the main dashboard move from `/tasks/next` to `/api/sessions/start`?
- Where exactly should scoring happen long-term: WMA, points, or both?
- Should new sessions also update `user_skill_scores` and `progress_logs`, or should old WMA be retired?
- Should legacy task/chat completion record streaks, or should streaks wait until all users are on new sessions?
- Which object is the completion unit: `UserTask`, `LearningSession`, `ActivityAttempt`, `DailySession`, or `DailyActivity`?
- Are `daily_plans` still required once new curriculum v2 is active?
- Should the LLM `PlannerAgent` feed new sessions, or should new sessions stay deterministic?
- Should `TaskArchetype` replace `Task` templates, or are both intended to remain?
- Are old sub-skill names (`expression`, `comprehension`, `tone`) permanent DB identifiers?
- Should frontend skill label aliases remain, or should backend `display_label` fully own display naming?
- Should new-session widgets become bespoke components, or is generic free-text intended for MVP?
- Should new session feedback receive full task content?
- Should diagnosis writing remain a stub, or move to an LLM evaluator?
- Should `/diagnosis/result` be fetchable from backend instead of in-memory only?
- Should `RESTRUCTURE_DECISIONS.md` be restored, replaced, or references removed?
- Should AI request logging wrap every LLM call, including structured outputs?
- Should embedding be moved to a background worker instead of inline best-effort?
- Should challenge completion affect learner progress/streaks, or remain separate?
- Are admin task templates meant to manage legacy `tasks` only, or future archetypes too?

## 13. Developer Mental Model

If you want to change diagnosis logic, go to:
- Backend scoring/evaluators: `backend/app/modules/diagnosis/scoring.py`, `backend/app/modules/diagnosis/evaluators.py`, `backend/app/modules/diagnosis/service.py`.
- Diagnosis feedback: `backend/app/ai/agents/diagnosis_feedback.py`.
- Frontend form/result: `frontend/src/app/diagnosis/page.tsx`, `frontend/src/app/diagnosis/result/page.tsx`, `frontend/src/lib/diagnosis-api.ts`.

If you want to change signup/login/auth, go to:
- Backend: `backend/app/modules/auth/routes.py`, `service.py`, `repository.py`, `dependencies.py`, `models.py`.
- Frontend: `frontend/src/app/(auth)/*`, `frontend/src/store/authStore.ts`, `frontend/src/lib/auth-api.ts`, `frontend/src/lib/api.ts`.

If you want to change profile personalization, go to:
- Backend profile route: `backend/app/modules/auth/routes.py`.
- Personalization service/agent: `backend/app/modules/personalization/service.py`, `backend/app/ai/agents/personalization.py`.
- Frontend profile: `frontend/src/app/profile/page.tsx`.

If you want to change today's dashboard plan, first decide legacy vs new:
- Current dashboard legacy path: `frontend/src/components/dashboard/DailyTaskPanel.tsx`, `frontend/src/hooks/useNextTask.ts`, `frontend/src/lib/tasks-api.ts`, `backend/app/modules/tasks/service.py`.
- New sessions path: `frontend/src/app/sessions/*`, `frontend/src/hooks/useSessionsFlow.ts`, `backend/app/modules/sessions/*`.

If you want to change legacy task generation, go to:
- `backend/app/modules/tasks/service.py`
- `backend/app/ai/agents/task_generator.py`
- `backend/app/tasks/schemas/*`
- `backend/app/modules/curriculum/rotation.py`
- `backend/app/modules/curriculum/topics.py`

If you want to change new session generation, go to:
- `backend/app/modules/sessions/planner.py`
- `backend/app/modules/sessions/service.py`
- `backend/app/ai/sessions/llm_task_generator.py`
- `backend/app/ai/sessions/prompts.py`
- `backend/app/scoring/archetypes.py`
- `frontend/src/components/sessions/widgets/registry.tsx`

If you want to change feedback style, go to:
- Legacy feedback: `backend/app/ai/agents/feedback.py`, `backend/app/modules/responses/feedback_service.py`, `backend/app/ai/graphs/nodes.py`.
- New sessions feedback: `backend/app/ai/sessions/llm_feedback.py`, `backend/app/ai/sessions/prompts.py`.
- Frontend legacy feedback: `frontend/src/app/task/chat/[sessionId]/page.tsx`.
- Frontend new feedback: `frontend/src/components/sessions/ActivityFeedbackCard.tsx`.

If you want to change evaluation rules, go to:
- Legacy evaluator: `backend/app/ai/agents/evaluator.py`.
- Legacy detection/persistence: `backend/app/modules/responses/service.py`.
- New evaluator: `backend/app/ai/sessions/llm_evaluator.py`.
- New scoring persistence: `backend/app/modules/sessions/service.py`.

If you want to change scoring/points, go to:
- New deterministic scoring: `backend/app/scoring/constants.py`, `backend/app/scoring/engine.py`.
- New points write: `backend/app/modules/sessions/scoring_writer.py`.
- Legacy WMA/points: `backend/app/modules/progress/service.py`.
- Progress reads: `backend/app/modules/progress/routes.py`.

If you want to change streak behavior, go to:
- Backend state machine: `backend/app/modules/streaks/service.py`.
- Streak routes/schemas: `backend/app/modules/streaks/routes.py`, `schemas.py`.
- New session completion hook: `backend/app/modules/sessions/service.py`.
- Frontend activity/animation: `frontend/src/components/streak/*`, `frontend/src/lib/streak-api.ts`.

If you want to change dashboard display, go to:
- Page: `frontend/src/app/dashboard/page.tsx`.
- Daily plan card: `frontend/src/components/dashboard/DailyTaskPanel.tsx`.
- Skill bars: `frontend/src/components/dashboard/SkillScorePreview.tsx`.
- Streak grid: `frontend/src/components/streak/ActivityGridCard.tsx`.
- Backend user payload: `backend/app/modules/auth/routes.py`.
- Backend scores: `backend/app/modules/progress/routes.py`.

If you want to change chat UI, go to:
- Entry: `frontend/src/app/task/chat/page.tsx`.
- Chat shell: `frontend/src/app/task/chat/[sessionId]/page.tsx`.
- Widgets: `frontend/src/components/task/task-widgets/*`.
- Loading states: `frontend/src/components/task/TaskChatSkeletons.tsx`.
- Backend WebSocket: `backend/app/modules/learning_session/router.py`, `backend/app/modules/learning_session/service.py`.

If you want to change new session UI, go to:
- Pages: `frontend/src/app/sessions/start/page.tsx`, `frontend/src/app/sessions/[sessionId]/page.tsx`, `frontend/src/app/sessions/[sessionId]/scorecard/page.tsx`.
- Hooks/API: `frontend/src/hooks/useSessionsFlow.ts`, `frontend/src/lib/sessions-api.ts`.
- Components: `frontend/src/components/sessions/*`.

If you want to change stats/progress pages, go to:
- Frontend: `frontend/src/app/stats/page.tsx`, `frontend/src/app/stats/activities/page.tsx`, `frontend/src/lib/progress-api.ts`.
- Backend: `backend/app/modules/progress/routes.py`, `backend/app/modules/progress/service.py`, `backend/app/modules/progress/models.py`.

If you want to change course purchase/enrollment, go to:
- Backend purchase/enrollment: `backend/app/modules/subscriptions/routes.py`, `backend/app/modules/curriculum/service.py`, `backend/app/modules/curriculum/repository.py`.
- Frontend pricing/settings: `frontend/src/app/pricing/page.tsx`, `frontend/src/app/settings/page.tsx`, `frontend/src/lib/subscriptions-api.ts`, `frontend/src/lib/courses-api.ts`.

If you want to change challenges, go to:
- Backend: `backend/app/modules/challenges/*`.
- IELTS agents/prompts: `backend/app/ai/agents/ielts_challenge_*`, `backend/app/ai/agents/prompts/ielts/*`.
- Frontend: `frontend/src/app/challenges/*`, `frontend/src/lib/challenges-api.ts`.

If you want to change admin behavior, go to:
- Backend: `backend/app/modules/admin/*`, auth permission models/dependencies.
- Frontend: `frontend/src/app/admin/*`, `frontend/src/components/admin/*`, `frontend/src/lib/admin-api.ts`.

If you are overwhelmed, start with this rule:
- Current production-feeling learner dashboard path is legacy: `dashboard -> /tasks/next -> /task/chat -> /ws/learning -> legacy response/evaluation/feedback`.
- New architecture path is present but not fully wired into dashboard: `/api/sessions -> daily_sessions/activity_attempts -> session_scorecards -> streaks`.
