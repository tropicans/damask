# Architecture & Design Patterns

**Mapped Date:** 2026-07-20

## System Overview

SecureData Web is an in-memory tabular data sanitization platform designed to mask sensitive Personal Identifiable Information (PII) and financial records before transmission to external cloud services or LLMs.

```
+-------------------------------------------------------------------+
|                        Client Browser                             |
|  - React 18 + Vite SPA                                            |
|  - Axios API Client (with CSRF header interceptor)                |
+---------------------------------+---------------------------------+
                                  | HTTP + Cookies
                                  v
+---------------------------------+---------------------------------+
|                       FastAPI Backend                             |
|  - Security Middleware (CSRF, Security Headers, SlowAPI Limiter)  |
|  - REST Endpoints (/api/auth, /api/jobs, /api/admin)              |
+------------------+------------------------------+-----------------+
                   |                              |
                   v                              v
+------------------+--------------+  +------------+-----------------+
|      In-Memory Data Engine      |  |      SQLModel Database       |
|  - Parser (Pandas/openpyxl)     |  |  - SQLite (dev / datamask.db)  |
|  - Masker (Strategy Pattern)    |  |  - Postgres (prod / DB container)|
|  - Reversion Engine (Fernet)    |  |  - Users, Invites, Audit Logs  |
+---------------------------------+  +------------------------------+
```

## Architectural Patterns

### 1. In-Memory Streaming Pipeline (Stateless Buffer Processing)
Uploaded CSV and XLSX files are read directly into memory buffers (`io.BytesIO`) using Pandas and `openpyxl`. Processed outputs (masked CSV/XLSX or ZIP archives) are generated in-memory and streamed directly back to the client response. Raw uploaded file contents are never written to server disk storage.

### 2. Strategy Pattern for Masking Rules
Masking algorithms implement a modular strategy pattern in `backend/app/services/masker.py`:
- `FakeNameStrategy` - Synthesizes realistic replacement names via Faker.
- `RedactStrategy` - Replaces internal characters with masking characters (e.g. `317101******0001`).
- `PerturbStrategy` - Introduces controlled numeric variance to salary/financial amounts while preserving statistical distributions.
- `HashStrategy` - Computes deterministic SHA-256 or anonymized hashes.
- `PseudonymStrategy` - Generates reversible tokenized identifiers.

### 3. Symmetric Data Reversion (Fernet Encrypted Mapping)
When reversion key generation is requested (`backend/app/services/reversion.py`):
- A symmetric Fernet encryption key is generated.
- The original unmasked values for targeted columns are encrypted and bundled into a JSON key structure (`reversion_key_XXXX.json`).
- The masked data file and the JSON key are packaged into an in-memory ZIP archive for the user to download.
- Reversion takes place 100% locally by uploading both files to `/api/jobs/revert`.

### 4. Layered Security & Defense-in-Depth
- **Authentication:** HttpOnly, SameSite=Lax JWT session cookies.
- **CSRF Protection:** Double-submit cookie validation for mutating HTTP requests.
- **Rate Limiting:** SlowAPI IP lockout protection after 5 consecutive failed login attempts (15-minute cooldown).
- **Security Headers:** Strict CSP, HSTS, X-Frame-Options DENY, X-Content-Type-Options nosniff.
- **Role-Based Access Control (RBAC):** Admin-only endpoints for user management, invites, and system-wide audit logging.

## Core Application Layers

### Frontend (`frontend/src/`)
- `App.tsx` - Root orchestration component managing active session, preview state, and routing.
- `components/AuthForm.tsx` - Tabbed login and invite-only registration UI with local strength calculation.
- `components/Dropzone.tsx` - Drag-and-drop file upload interface.
- `components/PreviewTable.tsx` - Interactive column-by-column masking configuration and preview grid.
- `components/AuditDashboard.tsx` - Compliance statistics, job audit logs, and failed login tracking.
- `components/UserManagement.tsx` - Admin user status toggle (Active/Inactive) and role management.
- `utils/formatError.ts` - Robust error response extractor preventing React rendering crashes.

### Backend (`backend/app/`)
- `main.py` - FastAPI app initialization, middleware stack, and global exception handlers.
- `api/endpoints/` - REST API controllers (`auth.py`, `jobs.py`, `admin.py`).
- `services/` - Business logic wrappers (`parser.py`, `detector.py`, `masker.py`, `reversion.py`, `auth.py`).
- `models/` - SQLModel database tables and Pydantic schemas (`user.py`, `job.py`).
- `db.py` - Database session management, foreign key pragmas, and auto-seeding logic.
