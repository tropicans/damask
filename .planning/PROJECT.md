# SecureData Web

## What This Is

SecureData Web is a local/internal web application that allows users to upload CSV, XLS, and XLSX files containing sensitive personal identifiable information (PII) or financial data, configure custom masking rules per column, and download a safely anonymized version of the file. The tool is designed to prevent data leakage to external LLMs and cloud systems by processing uploads strictly in-memory and logging only job execution metadata.

## Core Value

Ensure sensitive data is masked safely and efficiently before it leaves the organization's secure perimeter.

## Current State

- **Milestone v3.0 (secured the app)**: Completed on 2026-07-19. Fully secured the application with cookie-based session auth, CSRF protection, secure headers, rate limiting, upload hardening, and role authorization.
- **Total Tests**: 26 tests (all passing in Docker backend container).

## Requirements

### Validated

- ✓ Technology stack mapped and Git repository initialized — 2026-07-19
- ✓ FR-1: Manage CSV/XLSX file uploads up to 50MB and process them strictly in-memory (no persistent server disk storage) — Phase 1 & 2
- ✓ FR-2: Read file headers and retrieve the first 3 rows of data to display as an interactive UI preview — Phase 1
- ✓ FR-3: Apply regex pattern matching on column headers to recommend default masking rules — Phase 1
- ✓ FR-4: Allow users to configure masking rules per column (No Masking, Fake Name, Fake Email, Fake Phone, Anonymize ID/Number, Perturb Numeric) — Phase 2
- ✓ FR-5: Execute masking transformations using Faker/pandas and trigger automatic file download of the anonymized file — Phase 2
- ✓ FR-6: Implement user login and register flow to track job history — Phase 3
- ✓ FR-7: Log job execution metadata (file name, file size, row count, masked columns) for security audits (without storing file contents) — Phase 4
- ✓ DOC-01: Initialize a dedicated `/docs` directory in the repository workspace — Phase 5
- ✓ DOC-02: Create root `README.md` containing installation, local development, and startup instructions — Phase 5
- ✓ DOC-03: Create `/docs/ARCHITECTURE.md` detailing patterns, layers, data flow, and abstractions — Phase 5
- ✓ DOC-04: Create `/docs/API-SPEC.md` documenting HTTP methods, request headers, parameters, and response models — Phase 5
- ✓ DOC-05: Create `/docs/DEPLOYMENT.md` providing Docker Compose production configs, volumes, and ports — Phase 5
- ✓ DOC-06: Write detailed inline docstrings for Python backend models, endpoint routers, and services — Phase 5
- ✓ DOC-07: Write TypeScript docstrings for React page components and API clients — Phase 5
- ✓ SEC-01: Move JWT token storage from frontend LocalStorage to secure HttpOnly, SameSite=Lax cookies — v3.0
- ✓ SEC-02: Configure secure HTTP response headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options) and CORS hardening — v3.0
- ✓ SEC-03: Implement API rate limiting on backend endpoints (FastAPI-Limiter or slowapi) — v3.0
- ✓ SEC-04: Harden input validation and tabular file parsing against malicious injection payloads — v3.0
- ✓ SEC-05: Implement CSRF protection (Double Submit Cookie pattern) for state-changing requests — v3.0
- ✓ SEC-06: Restrict dashboard access to authorized roles and secure audit log records — v3.0

### Active

- [ ] REV-01: Bijective 1-to-1 mapping generation during masking
- [ ] REV-02: Downloadable reversion mapping file (JSON) alongside masked data
- [ ] REV-03: Revert data UI page for uploading masked file + JSON mapping file
- [ ] REV-04: Revert file parsing & reconstruction in-memory
- [ ] REV-05: Revert audit log tracking (metadata only, no PII)
- [ ] REV-06: Robust error handling for invalid/corrupted files or mismatched mappings

### Out of Scope

- **Persistent file storage on server** — Excluded to guarantee compliance with privacy regulations (GDPR/UU PDP) by never storing raw data.
- **Direct cloud LLM API integration** — Out of scope to keep the initial tool focused purely on the local data sanitization step.

## Context

The application is built to run locally or as an internal web tool using a React.js frontend and a Python FastAPI backend. The backend utilizes `pandas` for tabular manipulation, `openpyxl` for Excel stream processing, and `faker` for generating realistic synthetic replacement data. Development is orchestrated via Docker Compose.

## Constraints

- **Security**: Must process files in temporary RAM buffers only. Output streams must be deleted/collected immediately after transmission.
- **Tech Stack**: Backend in Python (FastAPI/Pandas/Faker), Frontend in React.js, Database SQLite (dev) / PostgreSQL (prod).
- **Performance**: Must handle up to 50MB files without memory leaks or excessive event-loop blocking on the single-threaded Python backend.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| In-memory streaming | Prevents sensitive raw files from touching server disks, satisfying compliance policies | — Approved & Implemented |
| Strategy pattern for masking rules | Allows new masking strategies (e.g. custom date shift, salt hashing) to be plugged in easily | — Approved & Implemented |
| SQLite/PostgreSQL DB | Lightweight audit logging and user management | — Approved & Implemented |
| HttpOnly Session Cookies | Storing JWTs in HttpOnly SameSite=Lax cookies protects against XSS-based token theft | — Approved & Implemented (v3.0) |
| Double Submit CSRF Cookie | Validating custom headers matching CSRF cookies blocks Cross-Site Request Forgery | — Approved & Implemented (v3.0) |
| Chunked Upload Hardening | Inspecting file uploads in 8KB chunks ensures payloads >50MB are rejected before loading fully | — Approved & Implemented (v3.0) |
| Role-based RBAC Dashboard | Restricting audit metrics to admin/auditor roles enforces least-privilege security policy | — Approved & Implemented (v3.0) |

## Current Milestone: v4.0 (Data Reversion)

**Goal:** Create a facility to revert masked data back to its original/real values in a secure, zero-knowledge, and stateless manner.

**Target features:**
- Reversion mapping generation during data masking (bijective 1-to-1 mapping per column)
- Downloadable reversion mapping key file (JSON format) alongside the masked file
- Reversion upload interface (upload masked file + JSON mapping file to download restored file in-memory)
- Revert job audit logging (file size, row count, metadata only)

---
*Last updated: 2026-07-19 after v4.0 start*
