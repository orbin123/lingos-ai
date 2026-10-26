# LingosAI review guide

This folder is a local study mirror of the repository. It contains no application code. Its purpose is to help me recover the mental model of LingosAI before a test, code review, or interview.

## How to use this guide

1. Read `01-system-overview.md` to understand the product and the request path.
2. Read `02-backend-architecture.md` and `03-frontend-architecture.md` for the two halves of the application.
3. Read the focused AI notes in `04-ai-and-rag.md` and the session walkthrough in `05-session-lifecycle.md`.
4. Use the mirrored folders as a map. Each directory has a `README.md`; the file catalog explains the responsibility of individual source files without copying their implementation.
5. Finish with `06-data-and-infrastructure.md`, `07-testing-and-review-questions.md`, and `08-glossary.md`.

The real source remains one directory above this folder. Paths in this guide are relative to the repository root and are deliberately written as study notes, not as executable code.

## Important boundary

`review/` is ignored by Git and should remain local. Do not put secrets, database dumps, generated media, or production credentials here.

## Mirror key

The `backend/`, `frontend/`, `docs/`, `infra/`, and `tests/` directories mirror the main conceptual areas of the project. The mirror is intentionally human-friendly rather than byte-for-byte: source code is not duplicated; explanations are placed in `README.md` files and the source catalog.
