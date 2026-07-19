# Roadmap: SecureData Web

## Overview

This roadmap defines the transition of SecureData Web from inception to a fully functional local data-masking web application. Slicing features vertically, the roadmap prioritizes the core in-memory file parsing and preview engine, followed by masking execution and download functionality, user authentication, and finally security audit logging.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (e.g. 2.1): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Foundation & Preview Engine** - In-memory parsing, header extraction, and auto-recommendation regex. (completed 2026-07-19)
- [x] **Phase 2: Masking Engine & Download** - Faker strategies, user column configuration, and stream downloads. (completed 2026-07-19)
- [ ] **Phase 3: User Authentication** - JWT login/register security boundaries.
- [ ] **Phase 4: Audit Logging & Dashboard** - Job execution metadata logging and audit history view.

## Phase Details

### Phase 1: Foundation & Preview Engine

**Goal**: Implement file upload management (CSV/XLSX), memory-only processing buffer, column header reading, first 3 rows preview display, and regex-based automatic masking recommendations.
**Mode**: mvp
**Depends on**: Nothing
**Requirements**: FILE-01, FILE-02, FILE-03, PREV-01, PREV-02, PREV-03
**Success Criteria** (what must be TRUE):

  1. User can upload a CSV/XLSX file up to 50MB and see it parsed in memory.
  2. User can view the column headers and first 3 rows as an interactive data preview table.
  3. UI displays recommended masking rules automatically based on regex matching of column headers.

**Plans**: 3 plans

Plans:

- [x] 01-01: Backend Uvicorn/FastAPI setup with file upload API.
- [x] 01-02: Preview and auto-detection engine logic (Pandas/openpyxl/regex).
- [x] 01-03: Frontend React drag-and-drop file upload and preview page.

### Phase 2: Masking Engine & Download

**Goal**: Implement masking execution backend using Faker, user customization controls, and download generator.
**Mode**: mvp
**Depends on**: Phase 1
**Requirements**: FILE-04, MASK-01, MASK-02, MASK-03, MASK-04, MASK-05, MASK-06, MASK-07
**Success Criteria** (what must be TRUE):

  1. User can select customized masking options for each column via dropdown.
  2. Masking operations (Fake Name, Fake Email, Fake Phone, Anonymize ID/Number, Perturb Numeric) successfully transform data without saving raw data on server.
  3. User triggers download and receives the fully masked CSV/XLSX file.

**Plans**: 3 plans

Plans:

- [x] 02-01: Backend masking strategies (Faker, scrambling, numeric perturbation).
- [x] 02-02: UI dropdown selectors and masking execution trigger.
- [x] 02-03: File generation, streaming download, and cleanup verification.

### Phase 3: User Authentication

**Goal**: Implement user registration, login, and secure session management.
**Mode**: mvp
**Depends on**: Phase 2
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04
**Success Criteria** (what must be TRUE):

  1. User can register an account with validation.
  2. User can login and log out, with active sessions maintained by JWT.
  3. Session persists across browser refreshes.

**Plans**: 2 plans

Plans:

- [ ] 03-01: Backend user model, password hashing, and JWT token authentication endpoints.
- [ ] 03-02: Frontend login/register views and session context integration.

### Phase 4: Audit Logging & Dashboard

**Goal**: Implement database logging of job execution metadata and history dashboard.
**Mode**: mvp
**Depends on**: Phase 3
**Requirements**: AUDT-01, AUDT-02, AUDT-03, AUDT-04
**Success Criteria** (what must be TRUE):

  1. Every masking execution writes job metadata (original filename, size, row count, strategies) to database.
  2. No sensitive file content is written to the audit log.
  3. User can view a dashboard of their historical masking runs.

**Plans**: 2 plans

Plans:

- [ ] 04-01: Backend audit database schema and logger integration.
- [ ] 04-02: Frontend audit history log dashboard.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Preview Engine | 3/3 | Complete    | 2026-07-19 |
| 2. Masking Engine & Download | 3/3 | Complete    | 2026-07-19 |
| 3. User Authentication | 0/2 | Not started | - |
| 4. Audit Logging & Dashboard | 0/2 | Not started | - |
