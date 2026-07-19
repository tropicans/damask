# SecureData Web

## What This Is

SecureData Web is a local/internal web application that allows users to upload CSV, XLS, and XLSX files containing sensitive personal identifiable information (PII) or financial data, configure custom masking rules per column, and download a safely anonymized version of the file. The tool is designed to prevent data leakage to external LLMs and cloud systems by processing uploads strictly in-memory and logging only job execution metadata.

## Core Value

Ensure sensitive data is masked safely and efficiently before it leaves the organization's secure perimeter.

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

### Active

- [ ] DOC-01: Initialize a dedicated `/docs` directory in the repository workspace.
- [ ] DOC-02: Create root `README.md` containing installation, local development, and startup instructions.
- [ ] DOC-03: Create `/docs/ARCHITECTURE.md` detailing patterns, layers, data flow, and abstractions.
- [ ] DOC-04: Create `/docs/API-SPEC.md` documenting HTTP methods, request headers, parameters, and response models.
- [ ] DOC-05: Create `/docs/DEPLOYMENT.md` providing Docker Compose production configs, volumes, and ports.
- [ ] DOC-06: Write detailed inline docstrings for Python backend models, endpoint routers, and services.
- [ ] DOC-07: Write TypeScript docstrings for React page components and API clients.

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
*Last updated: 2026-07-19 after initialization*
