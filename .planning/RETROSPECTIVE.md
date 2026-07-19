# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v3.0 — secured the app

**Shipped:** 2026-07-19
**Phases:** 3 | **Plans:** 6 | **Sessions:** 6

### What Was Built
- **Cookie-based Session Authentication (SEC-AUTH)**: Moved JWT access token storage from client LocalStorage to secure HttpOnly cookies, verified JWT from cookies, and implemented clean cookie removal on logout.
- **Double Submit Cookie CSRF Protection (SEC-CSRF)**: Implemented Double-Submit Cookie CSRF protection for all POST, PUT, and DELETE routes on the backend. Created Axios request interceptor on the frontend to automatically attach the CSRF token from cookie to the request header.
- **Secure Headers & API Rate Limiting**: Added global HTTP security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, etc.) and registered rate limits via `slowapi` on authentication (5/min) and file processing (10/min) routes.
- **Input Hardening & Role Authorization**: Hardened file upload validation with strict MIME-type and 50MB file size checks using chunked streaming before reading into memory. Restricted audit logging and dashboard access to `admin` and `auditor` roles.

### What Worked
- Rebuilding containers and running Pytest inside the backend Docker container ensured that all tests were clean and reproducible in a production-like environment.
- Using Python's chunked file streaming allowed checking the content length and MIME-types early, preventing large payloads from consuming server resources.

### What Was Inefficient
- The `pytest` execution path on Windows sometimes had import path issues due to the Docker root path, which required configuring `pythonpath = ["."]` in `pyproject.toml` to resolve module import issues.

### Patterns Established
- Secure cookies and CSRF headers in Axios client configuration for all API interactions.
- Global middleware configuration for unified HTTP security headers.

### Key Lessons
1. Always secure JWTs using HttpOnly cookies to prevent XSS-based token theft.
2. In-memory pandas operations should be preceded by strict input file stream checks (size and MIME-type validation) to prevent Denial of Service (DoS) attacks on single-threaded FastAPI workers.

### Cost Observations
- Model mix: 100% Gemini 3.5 Flash (Medium)
- Sessions: 6
- Notable: Fast local verification execution inside Docker.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | 4 | 4 | Initial MVP and local storage authentication |
| v2.0 | 1 | 1 | Added complete documentation suite |
| v3.0 | 6 | 3 | Full application security hardening and rate limiting |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v3.0 | 26 | 100% | 0 |

### Top Lessons (Verified Across Milestones)

1. Keep pandas uploads strictly in-memory using BytesIO to prevent temporary raw data leakage.
2. Store auth tokens in HttpOnly SameSite cookies to protect the application from client-side token leakage.
