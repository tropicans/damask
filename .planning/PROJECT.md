# SecureData Web

## What This Is

SecureData Web is a local/internal web application that allows users to upload CSV, XLS, and XLSX files containing sensitive personal identifiable information (PII) or financial data, configure custom masking rules per column, and download a safely anonymized version of the file. The tool is designed to prevent data leakage to external LLMs and cloud systems by processing uploads strictly in-memory and logging only job execution metadata.

## Core Value

Ensure sensitive data is masked safely and efficiently before it leaves the organization's secure perimeter.

## Current State

- **v5.0 Production Readiness**: Completed on 2026-07-20. Hardened authentication policy, invite-based registration, account lockout, admin user management UI, login audits, PostgreSQL migration, and Nginx reverse proxy configurations.
- **Total Tests**: 54 tests (all passing).

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
- ✓ PROD-01: Admin User List UI — view all registered users in admin UI — Phase 12
- ✓ PROD-02: Admin User Role Change — update role (promote/demote) in admin UI — Phase 12
- ✓ PROD-03: Admin Deactivate User — deactivate accounts and block login — Phase 12
- ✓ PROD-04: Invite-only Registration — user registration requires valid invite token — Phase 11
- ✓ PROD-05: Admin Generate Invite Link — create one-time use invite tokens valid for 48 hours — Phase 11
- ✓ PROD-06: Password Strength Policy — enforce password complexity rules (uppercase/digit/min 8 chars) — Phase 11
- ✓ PROD-07: Registration Strength Indicator — real-time strength meter in UI — Phase 11
- ✓ PROD-08: PostgreSQL Support — database support for PostgreSQL concurrent writes — Phase 13
- ✓ PROD-09: Postgres docker-compose — production profile with persistent volume and healthcheck — Phase 13
- ✓ PROD-10: Production Deployment Guide — bilingual docs for SSL/VPS setup and automated backups — Phase 14
- ✓ PROD-11: Nginx Configuration template — reverse proxy upstream configuration template — Phase 14
- ✓ PROD-12: Log login success/failure — record security events with IP and user agent in DB — Phase 12
- ✓ PROD-13: Audit Dashboard Login Sub-tabs — admin views login history and failed attempts in dashboard — Phase 12
- ✓ PROD-14: Temporary Account Lockout — automatically lock accounts for 15 minutes after 5 consecutive failed logins — Phase 11

### Active

*(None — planning next milestone)*

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
| Database connection wait and retry | Implemented a 5-retry loop with 2s delay to wait for PostgreSQL to boot in containerized environments | — Approved & Implemented (Phase 13) |
| Switchable test database engine | Centralized session fixtures in `conftest.py` supporting `TEST_DATABASE_URL` for CI pipelines | — Approved & Implemented (Phase 13) |
| Port hardening | Bind proxy port to localhost (127.0.0.1:80:80) to restrict host-level exposure and block direct frontend/backend external ingress | — Approved & Implemented (Phase 14) |
| Zero DB Port Exposure Backups | Perform pg_dump inside the docker container using docker exec redirection | — Approved & Implemented (Phase 14) |

## Current Milestone: Planning

**Goal:** Plan next milestone goals and requirements.

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-07-20 after v5.0 milestone complete*
