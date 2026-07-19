# Walking Skeleton — SecureData Web

**Phase:** 1
**Generated:** 2026-07-19

## Capability Proven End-to-End

A user can drag and drop a CSV/XLSX file on the React frontend, see the first 3 rows of data rendered in a preview table, and view recommended masking rules automatically pre-selected based on column header regex matching, with all data processed strictly in-memory by the FastAPI backend.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Framework | FastAPI (Backend) & React with Vite + TS (Frontend) | FastAPI provides high-performance asynchronous endpoint capability with automatic OpenAPI docs; React offers a highly interactive SPA experience. |
| Data layer | In-memory processing buffer (BytesIO) | Crucial for security and regulatory compliance: files are never written to disk, and RAM buffers are immediately collected. |
| Auth | JWT Session boundary (Deferred) | Security isolation is planned for Phase 3; Phase 1 remains unauthenticated for simplicity of the foundation. |
| Deployment target | Local Docker Compose dev environment | Ensures consistency across developer systems and matches local execution constraints. |
| Directory layout | Decoupled roots (`backend/` and `frontend/`) | Clear separation of concerns; simplifies testing, independent dependency lists, and independent containerization. |

## Stack Touched in Phase 1

- [x] Project scaffold (FastAPI boilerplate, Vite/React/TS scaffold, TailwindCSS v3)
- [x] Routing — `/api/preview` POST endpoint in FastAPI
- [ ] Database — (No database in Phase 1; SQLite/SQLModel setup is deferred to Phase 3 & 4)
- [x] UI — Drag-and-drop file Zone (Dropzone) and tabular data renderer (PreviewTable)
- [x] Deployment — docker-compose.yml for local development execution

## Out of Scope (Deferred to Later Slices)

- Masking execution engine (Faker/pandas transformations) — Deferred to Phase 2
- Processed file stream downloads — Deferred to Phase 2
- User sign-up/login JWT auth barrier — Deferred to Phase 3
- Audit log DB write execution — Deferred to Phase 4

## Subsequent Slice Plan

Each later phase adds one vertical slice on top of this skeleton without altering its architectural decisions:

- Phase 2: Masking Engine & Download (Faker strategies, user configurations, and downloads)
- Phase 3: User Authentication (SQLite storage for users, JWT login/register middleware)
- Phase 4: Audit Logging & Dashboard (SQLite job logging and history UI)
