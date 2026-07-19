# Milestones

## v4.0 v4.0 (Shipped: 2026-07-19)

**Phases completed:** 2 phases, 6 plans, 0 tasks

**Key accomplishments:**

- (none recorded)

---

## v3.0 secured the app (Shipped: 2026-07-19)

**Phases completed:** 3 phases (Phases 6-8), 6 plans

**Key accomplishments:**

- **Cookie-based Session Authentication (SEC-AUTH)**: Moved JWT access token storage from client LocalStorage to secure HttpOnly cookies, verified JWT from cookies, and implemented clean cookie removal on logout.
- **Double Submit Cookie CSRF Protection (SEC-CSRF)**: Implemented Double-Submit Cookie CSRF protection for all POST, PUT, and DELETE routes on the backend. Created Axios request interceptor on the frontend to automatically attach the CSRF token from cookie to the request header.
- **Secure Headers & API Rate Limiting**: Added global HTTP security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options) and registered rate limits via `slowapi` on authentication (5/min) and file processing (10/min) routes.
- **Input Hardening & Role Authorization**: Hardened file upload validation with strict MIME-type and 50MB file size checks using chunked streaming before reading into memory. Restricted audit logging and dashboard access to `admin` and `auditor` roles.

---

## v2.0 add documentation (Shipped: 2026-07-19)

**Phases completed:** 1 phase (Phase 5), 3 plans

**Key accomplishments:**

- Created comprehensive documentation suite in `/docs` (ARCHITECTURE.md, API-SPEC.md, DEPLOYMENT.md).
- Added detailed inline docstrings to the Python backend and TypeScript frontend components.

---

## v1.0 MVP (Shipped: 2026-07-19)

**Phases completed:** 4 phases (Phases 1-4), 10 plans

**Key accomplishments:**

- Built the foundation, in-memory preview parsing engine, and strategy-pattern based masking engine.
- Implemented user registration, login, and audit log tracking.
